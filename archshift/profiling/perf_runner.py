"""Safe subprocess wrapper for container and PID ``perf`` profiling."""

from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import PurePosixPath
from typing import Any, Sequence
from uuid import uuid4

from .parser import PERF_EVENTS, parse_profile


def profile(
    command: Sequence[str] | None = None,
    *,
    pid: int | None = None,
    container: str | None = None,
    duration_s: float = 10.0,
    build_flags: Sequence[str] = (),
    cpu_model: str = "",
    cpu_features: Sequence[str] = (),
    thread_count: int = 0,
) -> dict[str, Any]:
    """Run ``perf stat`` and ``perf record`` for a PID or container command.

    A container target profiles a command via ``docker exec``. A PID target
    samples for ``duration_s``. Both require a real target; no shell is used.
    """
    if bool(pid is not None) == bool(container is not None):
        raise ValueError("provide exactly one of pid or container")
    if container is not None and not command:
        raise ValueError("container profiling requires a workload command")
    if pid is not None and pid <= 0:
        raise ValueError("pid must be positive")

    event_list = ",".join(PERF_EVENTS)
    data_path = PurePosixPath("/tmp") / f"archshift-perf-{uuid4().hex}.data"
    stat = _execute(_perf_command("stat", event_list, command, pid, container, data_path, duration_s))
    record = _execute(
        _perf_command("record", event_list, command, pid, container, data_path, duration_s)
    )
    report = _execute(_report_command(container, data_path)) if record.returncode == 0 else None

    errors = [
        f"perf stat exited {stat.returncode}: {stat.stderr.strip()}"
        for stat in (stat,)
        if stat.returncode != 0 and stat.stderr.strip()
    ]
    if record.returncode != 0:
        errors.append(f"perf record exited {record.returncode}: {record.stderr.strip()}")
    if report is not None and report.returncode != 0:
        errors.append(f"perf report exited {report.returncode}: {report.stderr.strip()}")

    metadata = {
        "build_flags": list(build_flags),
        "cpu_model": cpu_model,
        "cpu_features": list(cpu_features),
        "thread_count": thread_count,
        "perf_command": " ".join(_perf_command("stat", event_list, command, pid, container, data_path, duration_s)),
        "timestamp": datetime.now(UTC).isoformat(),
    }
    result = parse_profile(stat.stderr, report.stdout if report and report.returncode == 0 else None, metadata=metadata)
    result["errors"] = errors + result["errors"]
    if errors and result["status"] == "ok":
        result["status"] = "degraded"
    return result


def _perf_command(
    mode: str,
    event_list: str,
    command: Sequence[str] | None,
    pid: int | None,
    container: str | None,
    data_path: PurePosixPath,
    duration_s: float,
) -> list[str]:
    perf = ["perf", mode, "-e", event_list]
    if mode == "stat":
        perf.extend(["-x,", "--log-fd", "2"])
    else:
        perf.extend(["-o", str(data_path)])
    if pid is not None:
        perf.extend(["-p", str(pid), "--", "sleep", str(duration_s)])
    else:
        perf.extend(["--", *(command or ())])
    return ["docker", "exec", container, *perf] if container else perf


def _report_command(container: str | None, data_path: PurePosixPath) -> list[str]:
    command = ["perf", "report", "--stdio", "--no-children", "-i", str(data_path)]
    return ["docker", "exec", container, *command] if container else command


def _execute(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, capture_output=True, text=True, check=False)
    except OSError as error:
        return subprocess.CompletedProcess(command, 127, "", str(error))
