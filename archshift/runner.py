"""Orchestrate profile → propose → verify for ``archshift run``."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from archshift.logging import configure_logging
from archshift.optimization import PriorAttempt, propose_optimization
from archshift.profiling import profile
from archshift.target import TargetConfig
from archshift.verification import (
    RejectionRecord,
    VerificationEngine,
    VerificationResult,
)
from archshift.verification.engine import (
    BenchmarkRunner,
    BuildRunner,
    CorrectnessRunner,
    MAX_ATTEMPTS,
    PatchApplier,
)

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class RuntimeCallbacks:
    """Injected host/runtime operations for build, benchmark, and patch apply."""

    apply_patch: PatchApplier
    build: BuildRunner
    correctness: CorrectnessRunner
    benchmark: BenchmarkRunner


@dataclass(frozen=True)
class RunOutcome:
    """Summary of one ``archshift run`` invocation."""

    accepted: bool
    run_attempts: int
    results: list[VerificationResult]
    evidence_path: Path


def run_loop(
    target: TargetConfig,
    callbacks: RuntimeCallbacks,
    *,
    propose: Any = propose_optimization,
    profile_fn: Any = profile,
) -> RunOutcome:
    """Execute the locked B1 → B2 → B3 loop up to three attempts."""

    configure_logging()
    target.evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = target.evidence_dir / "run.jsonl"

    profile_result = profile_fn(
        target.workload_command,
        container=target.container,
        build_flags=target.build_context.cmake_flags,
        cpu_features=target.build_context.cpu_features,
    )
    _write_evidence(evidence_path, {"stage": "profile", "profile": profile_result})

    hotspot_context = _hotspot_context(profile_result, target.hotspot_symbol)
    prior_attempts: list[PriorAttempt] = []
    results: list[VerificationResult] = []

    engine = VerificationEngine(
        target.repository.resolve(),
        apply_patch=callbacks.apply_patch,
        build=callbacks.build,
        correctness=callbacks.correctness,
        benchmark=callbacks.benchmark,
        rejection_log=target.resolved_rejection_log(),
    )

    for run_attempt in range(1, MAX_ATTEMPTS + 1):
        LOGGER.info("optimization attempt %s/%s", run_attempt, MAX_ATTEMPTS)
        proposal = propose(
            profile_result,
            hotspot_context=hotspot_context,
            build_context=target.build_context,
            prior_attempts=prior_attempts,
        )
        _write_evidence(
            evidence_path,
            {
                "stage": "proposal",
                "run_attempt": run_attempt,
                "proposal": proposal.model_dump(),
            },
        )
        attempt_results = engine.verify([proposal], baseline_hash=target.baseline_hash)
        result = attempt_results[0]
        results.append(result)
        _write_evidence(
            evidence_path,
            {
                "stage": "verification",
                "run_attempt": run_attempt,
                "accepted": result.accepted,
                "branch_ref": result.branch_ref,
                "rejection": _rejection_dict(result.rejection),
                "accepted_measurements": result.accepted_measurements,
            },
        )
        if result.accepted:
            return RunOutcome(True, run_attempt, results, evidence_path)
        rejection = result.rejection
        if rejection is None:
            break
        prior_attempts.append(
            PriorAttempt(
                patch=rejection.patch,
                hypothesis=rejection.hypothesis,
                rejection_reason=rejection.failed_gate,
            )
        )

    return RunOutcome(False, len(results), results, evidence_path)


def _hotspot_context(profile_result: dict[str, Any], override: str | None) -> str:
    if override:
        return override
    hotspots = profile_result.get("hotspots") or []
    if hotspots:
        top = hotspots[0]
        symbol = top.get("symbol", "unknown")
        percent = top.get("percent", 0.0)
        return f"{symbol} ({percent}% sample time)"
    return "no hotspot data available"


def _rejection_dict(rejection: RejectionRecord | None) -> dict[str, Any] | None:
    return asdict(rejection) if rejection is not None else None


def _write_evidence(path: Path, payload: dict[str, Any]) -> None:
    record = {"timestamp": datetime.now(UTC).isoformat(), **payload}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True))
        handle.write("\n")
