from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from archshift.profiling import profile
from archshift.profiling.parser import PERF_EVENTS, parse_profile

FIXTURE = (
    Path(__file__).parent / "fixtures" / "perf-stat-docker-desktop-2026-08-05.txt"
)


def test_real_perf_fixture_degrades_without_changing_profile_shape() -> None:
    raw = FIXTURE.read_text(encoding="utf-8")

    result = parse_profile(raw, metadata={"perf_command": "perf stat -x, ..."})

    assert result["status"] == "degraded"
    assert set(result) == {"status", "errors", "metadata", "summary", "hotspots"}
    assert result["metadata"]["perf_command"] == "perf stat -x, ..."
    assert result["hotspots"] is None
    assert all(any(event in error for error in result["errors"]) for event in PERF_EVENTS)
    assert result["summary"] == {
        "ipc": None,
        "cache_miss_rate": None,
        "branch_miss_rate": None,
        "wall_time_s": None,
    }


def test_profile_uses_perf_stat_and_record_for_container(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw = FIXTURE.read_text(encoding="utf-8")
    calls: list[list[str]] = []

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        if "stat" in command:
            return subprocess.CompletedProcess(command, 0, "", raw)
        return subprocess.CompletedProcess(command, 1, "", "perf_event_open: Operation not permitted")

    monkeypatch.setattr("archshift.profiling.perf_runner.subprocess.run", fake_run)

    result = profile(["./llama-cli", "--temp", "0"], container="llama")

    assert result["status"] == "degraded"
    assert result["metadata"]["perf_command"].startswith("docker exec llama perf stat")
    assert any("perf record exited 1" in error for error in result["errors"])
    assert calls[0][:5] == ["docker", "exec", "llama", "perf", "stat"]
    assert calls[1][:5] == ["docker", "exec", "llama", "perf", "record"]


def test_profile_rejects_ambiguous_target() -> None:
    with pytest.raises(ValueError, match="exactly one"):
        profile(["true"])
