"""Mechanical accept/reject gate for build-flag optimization attempts."""

from __future__ import annotations

import json
import shutil
import statistics
import subprocess
import tempfile
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any
from uuid import uuid4

from archshift.optimization.allowlist import OptimizationProposal, validate_patch

WARMUP_ITERATIONS = 2
MEASURED_ITERATIONS = 7
MAX_COEFFICIENT_OF_VARIATION = 0.10
MAX_ATTEMPTS = 3

BuildRunner = Callable[[Path], None]
CorrectnessRunner = Callable[[Path], str]
BenchmarkRunner = Callable[[Path], "BenchmarkMeasurement"]
PatchApplier = Callable[[Path, OptimizationProposal], None]


class VerificationError(RuntimeError):
    """Base error for a verification run that cannot safely continue."""


class RollbackError(VerificationError):
    """Raised when a rejected attempt cannot be restored to its base state."""


@dataclass(frozen=True)
class BenchmarkMeasurement:
    """Timed benchmark samples with mandated warm-up and measured counts."""

    warmup_seconds: tuple[float, ...]
    measured_seconds: tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.warmup_seconds) != WARMUP_ITERATIONS:
            raise ValueError(f"expected {WARMUP_ITERATIONS} warm-up samples")
        if len(self.measured_seconds) != MEASURED_ITERATIONS:
            raise ValueError(f"expected {MEASURED_ITERATIONS} measured samples")
        if any(value <= 0 for value in (*self.warmup_seconds, *self.measured_seconds)):
            raise ValueError("benchmark durations must be positive")

    @property
    def mean_seconds(self) -> float:
        return statistics.fmean(self.measured_seconds)

    @property
    def stdev_seconds(self) -> float:
        return statistics.stdev(self.measured_seconds)

    @property
    def coefficient_of_variation(self) -> float:
        return self.stdev_seconds / self.mean_seconds

    def as_dict(self) -> dict[str, Any]:
        return {
            "warmup_seconds": list(self.warmup_seconds),
            "measured_seconds": list(self.measured_seconds),
            "mean_seconds": self.mean_seconds,
            "stdev_seconds": self.stdev_seconds,
            "coefficient_of_variation": self.coefficient_of_variation,
        }


@dataclass(frozen=True)
class RejectionRecord:
    """Submission-evidence record defined by wayfinder issue #6."""

    attempt_number: int
    patch: list[dict[str, str]]
    hypothesis: str
    failed_gate: str
    measured_numbers: dict[str, Any]
    timestamp: str
    branch_ref: str


@dataclass(frozen=True)
class VerificationResult:
    """Result of one attempted optimization."""

    accepted: bool
    attempt_number: int
    branch_ref: str
    rejection: RejectionRecord | None = None
    accepted_measurements: dict[str, Any] | None = None


class VerificationEngine:
    """Apply proposals in isolated Git worktrees and enforce #6's hard gates."""

    def __init__(
        self,
        repository: Path,
        *,
        apply_patch: PatchApplier,
        build: BuildRunner,
        correctness: CorrectnessRunner,
        benchmark: BenchmarkRunner,
        rejection_log: Path,
        max_measurement_retries: int = 3,
    ) -> None:
        self.repository = repository.resolve()
        self.apply_patch = apply_patch
        self.build = build
        self.correctness = correctness
        self.benchmark = benchmark
        self.rejection_log = rejection_log
        self.max_measurement_retries = max_measurement_retries

    def verify(
        self,
        proposals: Sequence[OptimizationProposal],
        *,
        baseline_hash: str,
    ) -> list[VerificationResult]:
        """Run at most three proposals; stop immediately after an acceptance."""

        if not proposals:
            return []
        self._require_clean_repository()
        baseline = self._measure_reliably(self.repository, state="baseline")
        results: list[VerificationResult] = []
        for attempt_number, proposal in enumerate(proposals[:MAX_ATTEMPTS], start=1):
            result = self._verify_attempt(
                attempt_number=attempt_number,
                proposal=proposal,
                baseline_hash=baseline_hash,
                baseline=baseline,
            )
            results.append(result)
            if result.accepted:
                break
        return results

    def _verify_attempt(
        self,
        *,
        attempt_number: int,
        proposal: OptimizationProposal,
        baseline_hash: str,
        baseline: BenchmarkMeasurement,
    ) -> VerificationResult:
        workspace = _AttemptWorkspace.create(self.repository, attempt_number)
        measured_numbers: dict[str, Any] = {"baseline": baseline.as_dict()}
        try:
            validate_patch(proposal.patch)
            self.apply_patch(workspace.path, proposal)
            self._reject_protected_changes(workspace.path)
        except _ProtectedPathError as exc:
            return self._reject(workspace, attempt_number, proposal, "apply", measured_numbers, exc)
        except ValueError as exc:
            return self._reject(workspace, attempt_number, proposal, "apply", measured_numbers, exc)

        try:
            self.build(workspace.path)
        except Exception as exc:  # Build callback errors are a build rejection.
            return self._reject(workspace, attempt_number, proposal, "build", measured_numbers, exc)

        try:
            candidate_hash = self.correctness(workspace.path)
        except Exception as exc:
            return self._reject(
                workspace, attempt_number, proposal, "correctness", measured_numbers, exc
            )
        measured_numbers["baseline_output_hash"] = baseline_hash
        measured_numbers["candidate_output_hash"] = candidate_hash
        if candidate_hash != baseline_hash:
            return self._reject(
                workspace, attempt_number, proposal, "correctness", measured_numbers
            )

        try:
            candidate = self._measure_reliably(workspace.path, state="candidate")
        except Exception as exc:
            return self._reject(workspace, attempt_number, proposal, "benchmark", measured_numbers, exc)
        measured_numbers["candidate"] = candidate.as_dict()
        threshold = max(3 * baseline.stdev_seconds, 0.05 * baseline.mean_seconds)
        improvement = baseline.mean_seconds - candidate.mean_seconds
        measured_numbers["required_improvement_seconds"] = threshold
        measured_numbers["observed_improvement_seconds"] = improvement
        if improvement > threshold:
            workspace.keep()
            return VerificationResult(
                accepted=True,
                attempt_number=attempt_number,
                branch_ref=workspace.branch_ref,
                accepted_measurements=measured_numbers,
            )
        return self._reject(workspace, attempt_number, proposal, "benchmark", measured_numbers)

    def _reject(
        self,
        workspace: "_AttemptWorkspace",
        attempt_number: int,
        proposal: OptimizationProposal,
        failed_gate: str,
        measured_numbers: dict[str, Any],
        error: Exception | None = None,
    ) -> VerificationResult:
        if error is not None:
            measured_numbers["error"] = str(error)
        workspace.rollback()
        rejection = self._record_rejection(
            attempt_number=attempt_number,
            proposal=proposal,
            failed_gate=failed_gate,
            measured_numbers=measured_numbers,
            branch_ref=workspace.branch_ref,
        )
        return VerificationResult(
            accepted=False,
            attempt_number=attempt_number,
            branch_ref=workspace.branch_ref,
            rejection=rejection,
        )

    def _measure_reliably(self, path: Path, *, state: str) -> BenchmarkMeasurement:
        for _ in range(self.max_measurement_retries):
            measurement = self.benchmark(path)
            if measurement.coefficient_of_variation <= MAX_COEFFICIENT_OF_VARIATION:
                return measurement
        raise VerificationError(
            f"{state} benchmark CV remained above {MAX_COEFFICIENT_OF_VARIATION:.0%} "
            f"after {self.max_measurement_retries} complete re-runs"
        )

    def _record_rejection(
        self,
        *,
        attempt_number: int,
        proposal: OptimizationProposal,
        failed_gate: str,
        measured_numbers: dict[str, Any],
        branch_ref: str,
    ) -> RejectionRecord:
        record = RejectionRecord(
            attempt_number=attempt_number,
            patch=[entry.model_dump() for entry in proposal.patch],
            hypothesis=proposal.hypothesis,
            failed_gate=failed_gate,
            measured_numbers=measured_numbers,
            timestamp=datetime.now(timezone.utc).isoformat(),
            branch_ref=branch_ref,
        )
        self.rejection_log.parent.mkdir(parents=True, exist_ok=True)
        with self.rejection_log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(record), sort_keys=True))
            handle.write("\n")
        return record

    def _require_clean_repository(self) -> None:
        if self._git_output(self.repository, "status", "--porcelain"):
            raise VerificationError("verification requires a clean repository")

    def _reject_protected_changes(self, workspace: Path) -> None:
        changed_paths = self._git_output(workspace, "diff", "--name-only", "HEAD").splitlines()
        changed_paths.extend(
            line[3:]
            for line in self._git_output(workspace, "status", "--porcelain").splitlines()
            if line.startswith("?? ")
        )
        protected = [path for path in changed_paths if _is_protected_path(path)]
        if protected:
            raise _ProtectedPathError(protected)

    @staticmethod
    def _git_output(path: Path, *args: str) -> str:
        return subprocess.run(
            ["git", *args],
            cwd=path,
            check=True,
            text=True,
            capture_output=True,
        ).stdout


class _ProtectedPathError(ValueError):
    def __init__(self, paths: list[str]) -> None:
        super().__init__(f"patch modified protected paths: {', '.join(paths)}")


def _is_protected_path(path: str) -> bool:
    parts = {part.lower() for part in PurePosixPath(path).parts}
    return bool(parts & {"test", "tests", "benchmark", "benchmarks"}) or (
        "archshift" in parts and "verification" in parts
    )


class _AttemptWorkspace:
    """A disposable worktree whose branch survives rejected attempts."""

    def __init__(self, repository: Path, path: Path, branch_ref: str) -> None:
        self.repository = repository
        self.path = path
        self.branch_ref = branch_ref
        self._keep = False

    @classmethod
    def create(cls, repository: Path, attempt_number: int) -> "_AttemptWorkspace":
        branch_ref = f"archshift/verification/{uuid4().hex[:12]}-{attempt_number}"
        path = Path(tempfile.mkdtemp(prefix="archshift-verification-"))
        shutil.rmtree(path)
        subprocess.run(
            ["git", "worktree", "add", "-b", branch_ref, str(path), "HEAD"],
            cwd=repository,
            check=True,
            text=True,
            capture_output=True,
        )
        return cls(repository, path, branch_ref)

    def keep(self) -> None:
        """Retain accepted worktree for review and later integration."""

        self._keep = True

    def rollback(self) -> None:
        """Restore rejected worktree, assert clean, remove it, retain branch ref."""

        try:
            subprocess.run(
                ["git", "reset", "--hard", "HEAD"],
                cwd=self.path,
                check=True,
                text=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "clean", "-fd"],
                cwd=self.path,
                check=True,
                text=True,
                capture_output=True,
            )
            status = VerificationEngine._git_output(self.path, "status", "--porcelain")
            if status:
                raise RollbackError("rejected worktree remains dirty after rollback")
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(self.path)],
                cwd=self.repository,
                check=True,
                text=True,
                capture_output=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            raise RollbackError("mandatory rollback failed") from exc
