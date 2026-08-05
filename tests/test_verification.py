from __future__ import annotations

import json
import subprocess
from collections.abc import Callable
from pathlib import Path

from archshift.optimization.allowlist import (
    ExpectedImpact,
    OptimizationProposal,
    PatchEntry,
)
from archshift.verification.engine import BenchmarkMeasurement, VerificationEngine


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
        hypothesis="dot-product instructions reduce Q4 matrix multiplication time",
        patch=[PatchEntry(flag="+dotprod", action="add", rationale="hotspot is Q4 matmul")],
        expected_impact=ExpectedImpact(
            metric="wall_time_s", direction="faster", magnitude_pct=10.0
        ),
        confidence=0.8,
    )


def _repository(tmp_path: Path) -> Path:
    repository = tmp_path / "repo"
    repository.mkdir()
    _git(repository, "init")
    (repository / "CMakeLists.txt").write_text("set(FLAGS \"\")\n", encoding="utf-8")
    _git(repository, "add", ".")
    _git(
        repository,
        "-c",
        "user.name=verification-test",
        "-c",
        "user.email=verification-test@example.invalid",
        "commit",
        "-m",
        "initial",
    )
    return repository


def _git(repository: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repository,
        check=True,
        text=True,
        capture_output=True,
    ).stdout


def _engine(
    repository: Path,
    tmp_path: Path,
    *,
    apply_patch: Callable[[Path, OptimizationProposal], None],
    correctness: Callable[[Path], str],
    measurements: list[BenchmarkMeasurement],
) -> VerificationEngine:
    sequence = iter(measurements)
    return VerificationEngine(
        repository,
        apply_patch=apply_patch,
        build=lambda _: None,
        correctness=correctness,
        benchmark=lambda _: next(sequence),
        rejection_log=tmp_path / "rejections.jsonl",
    )


def test_accepts_good_patch_that_clears_noise_threshold(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    def apply_patch(path: Path, _: OptimizationProposal) -> None:
        with (path / "CMakeLists.txt").open("a", encoding="utf-8") as handle:
            handle.write("set(FLAGS \"+dotprod\")\n")

    engine = _engine(
        repository,
        tmp_path,
        apply_patch=apply_patch,
        correctness=lambda _: "baseline-hash",
        measurements=[_measurement(1.0), _measurement(0.90)],
    )

    [result] = engine.verify([_proposal()], baseline_hash="baseline-hash")

    assert result.accepted
    assert result.accepted_measurements is not None
    assert result.accepted_measurements["observed_improvement_seconds"] > result.accepted_measurements[
        "required_improvement_seconds"
    ]
    assert _git(repository, "status", "--porcelain") == ""


def test_rejects_correctness_divergence_and_rolls_back_cleanly(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    def apply_patch(path: Path, _: OptimizationProposal) -> None:
        with (path / "CMakeLists.txt").open("a", encoding="utf-8") as handle:
            handle.write("set(FLAGS \"+dotprod\")\n")

    engine = _engine(
        repository,
        tmp_path,
        apply_patch=apply_patch,
        correctness=lambda _: "different-hash",
        measurements=[_measurement(1.0)],
    )

    [result] = engine.verify([_proposal()], baseline_hash="baseline-hash")

    assert not result.accepted
    assert result.rejection is not None
    assert result.rejection.failed_gate == "correctness"
    assert _git(repository, "status", "--porcelain") == ""
    assert _git(repository, "branch", "--list", result.branch_ref).strip() == result.branch_ref
    logged = json.loads((tmp_path / "rejections.jsonl").read_text(encoding="utf-8"))
    assert set(logged) == {
        "attempt_number",
        "patch",
        "hypothesis",
        "failed_gate",
        "measured_numbers",
        "timestamp",
        "branch_ref",
    }


def test_rejects_slower_correct_patch(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    def apply_patch(path: Path, _: OptimizationProposal) -> None:
        with (path / "CMakeLists.txt").open("a", encoding="utf-8") as handle:
            handle.write("set(FLAGS \"+dotprod\")\n")

    engine = _engine(
        repository,
        tmp_path,
        apply_patch=apply_patch,
        correctness=lambda _: "baseline-hash",
        measurements=[_measurement(0.9), _measurement(1.0)],
    )

    [result] = engine.verify([_proposal()], baseline_hash="baseline-hash")

    assert not result.accepted
    assert result.rejection is not None
    assert result.rejection.failed_gate == "benchmark"
    assert result.rejection.measured_numbers["observed_improvement_seconds"] < 0
    assert _git(repository, "status", "--porcelain") == ""


def test_rejects_patch_that_modifies_test_or_benchmark_files(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    def apply_patch(path: Path, _: OptimizationProposal) -> None:
        (path / "tests").mkdir()
        (path / "tests" / "hacked.py").write_text("pass\n", encoding="utf-8")

    engine = _engine(
        repository,
        tmp_path,
        apply_patch=apply_patch,
        correctness=lambda _: "baseline-hash",
        measurements=[_measurement(1.0)],
    )

    [result] = engine.verify([_proposal()], baseline_hash="baseline-hash")

    assert not result.accepted
    assert result.rejection is not None
    assert result.rejection.failed_gate == "apply"
    assert _git(repository, "status", "--porcelain") == ""
