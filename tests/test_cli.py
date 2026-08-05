from __future__ import annotations

import json
import subprocess
from itertools import cycle
from pathlib import Path

import pytest

from archshift.cli import main
from archshift.optimization.allowlist import (
    ExpectedImpact,
    OptimizationProposal,
    PatchEntry,
)
from archshift.runner import RuntimeCallbacks, run_loop
from archshift.target import TargetConfig
from archshift.verification.engine import BenchmarkMeasurement


def _measurement(seconds: float) -> BenchmarkMeasurement:
    return BenchmarkMeasurement(
        warmup_seconds=(seconds, seconds),
        measured_seconds=(
            seconds * 0.99,
            seconds,
            seconds * 1.01,
            seconds,
            seconds,
            seconds,
            seconds,
        ),
    )


def _proposal() -> OptimizationProposal:
    return OptimizationProposal(
        hypothesis="dotprod should help Q4 matmul",
        patch=[PatchEntry(flag="+dotprod", action="add", rationale="hotspot")],
        expected_impact=ExpectedImpact(
            metric="wall_time_s", direction="faster", magnitude_pct=8.0
        ),
        confidence=0.7,
    )


def _repository(tmp_path: Path) -> Path:
    repository = tmp_path / "repo"
    repository.mkdir()
    subprocess.run(["git", "init"], cwd=repository, check=True, capture_output=True)
    (repository / "CMakeLists.txt").write_text("set(FLAGS \"\")\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repository, check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-m",
            "init",
        ],
        cwd=repository,
        check=True,
        capture_output=True,
    )
    return repository


def _target(repository: Path, evidence_dir: Path) -> TargetConfig:
    return TargetConfig(
        repository=repository,
        container="llama",
        workload_command=["./llama-cli", "--temp", "0"],
        baseline_hash="baseline-hash",
        evidence_dir=evidence_dir,
        build_context={
            "cmake_flags": ["-DCMAKE_BUILD_TYPE=Release"],
            "cpu_features": ["neon"],
            "compiler_version": "gcc 13.2.0",
        },
    )


def test_run_loop_wires_profile_propose_and_verify(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    evidence_dir = tmp_path / "evidence"
    target = _target(repository, evidence_dir)
    profile_payload = {
        "status": "ok",
        "errors": [],
        "metadata": {"build_flags": [], "cpu_model": "", "cpu_features": [], "thread_count": 0, "perf_command": "", "timestamp": ""},
        "summary": {"ipc": 1.2, "cache_miss_rate": 0.1, "branch_miss_rate": 0.02, "wall_time_s": 1.0},
        "hotspots": [{"symbol": "ggml_vec_dot_q4_0_q8_0", "percent": 42.0, "event_counts": {}}],
    }
    measurements = iter([_measurement(1.0), _measurement(0.90)])

    def apply_patch(path: Path, _: OptimizationProposal) -> None:
        with (path / "CMakeLists.txt").open("a", encoding="utf-8") as handle:
            handle.write("set(FLAGS \"+dotprod\")\n")

    callbacks = RuntimeCallbacks(
        apply_patch=apply_patch,
        build=lambda _: None,
        correctness=lambda _: "baseline-hash",
        benchmark=lambda _: next(measurements),
    )

    outcome = run_loop(
        target,
        callbacks,
        profile_fn=lambda *args, **kwargs: profile_payload,
        propose=lambda *args, **kwargs: _proposal(),
    )

    assert outcome.accepted
    assert outcome.run_attempts == 1
    evidence_lines = (evidence_dir / "run.jsonl").read_text(encoding="utf-8").splitlines()
    stages = [json.loads(line)["stage"] for line in evidence_lines]
    assert stages == ["profile", "proposal", "verification"]


def test_reject_outcome_counts_as_successful_run(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    evidence_dir = tmp_path / "evidence"
    target = _target(repository, evidence_dir)
    measurements = cycle([_measurement(1.0)])

    def apply_patch(path: Path, _: OptimizationProposal) -> None:
        with (path / "CMakeLists.txt").open("a", encoding="utf-8") as handle:
            handle.write("set(FLAGS \"+dotprod\")\n")

    callbacks = RuntimeCallbacks(
        apply_patch=apply_patch,
        build=lambda _: None,
        correctness=lambda _: "different-hash",
        benchmark=lambda _: next(measurements),
    )

    outcome = run_loop(
        target,
        callbacks,
        profile_fn=lambda *args, **kwargs: {
            "status": "ok",
            "errors": [],
            "metadata": {},
            "summary": {},
            "hotspots": [],
        },
        propose=lambda *args, **kwargs: _proposal(),
    )

    assert not outcome.accepted
    exit_code = 0 if outcome.accepted or outcome.run_attempts > 0 else 1
    assert exit_code == 0


def test_cli_run_exits_nonzero_without_phase_c_runtime(tmp_path: Path) -> None:
    target_path = tmp_path / "target.json"
    target_path.write_text(
        json.dumps(
            {
                "repository": ".",
                "baseline_hash": "hash",
                "evidence_dir": str(tmp_path / "evidence"),
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(SystemExit) as exc:
        main(["run", "--target", str(target_path)])
    assert exc.value.code != 0
