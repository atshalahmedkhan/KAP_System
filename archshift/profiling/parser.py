"""Parse ``perf stat`` and ``perf report --stdio`` output into B1 profiles."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

PERF_EVENTS = (
    "cycles",
    "instructions",
    "cache-references",
    "cache-misses",
    "branch-misses",
    "stalled-cycles-frontend",
    "stalled-cycles-backend",
)

_TIME_RE = re.compile(r"([\d,.]+)\s+seconds time elapsed")
_REPORT_ROW_RE = re.compile(
    r"^\s*(?P<percent>[\d.]+)%\s+(?:\S+\s+)?(?:\S+\s+)?"
    r"(?P<symbol>\S.*\S|\S)\s*$"
)


def parse_profile(
    stat_output: str,
    report_output: str | None = None,
    *,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the locked #4 profile shape from raw perf output.

    ``perf stat -x,`` is used by the runner, but common whitespace-delimited
    output is accepted too for operator-supplied captures.
    """
    counts, errors, wall_time = _parse_stat(stat_output)
    if not counts and not wall_time:
        errors.append("perf stat produced no parseable event counts")

    summary = _summary(counts, wall_time)
    hotspots = _parse_report(report_output or "")
    profile_metadata = {
        "build_flags": [],
        "cpu_model": "",
        "cpu_features": [],
        "thread_count": 0,
        "perf_command": "",
        "timestamp": datetime.now(UTC).isoformat(),
    }
    if metadata:
        profile_metadata.update(metadata)

    return {
        "status": "failed"
        if not stat_output.strip()
        else ("degraded" if errors else "ok"),
        "errors": errors,
        "metadata": profile_metadata,
        "summary": summary,
        "hotspots": hotspots if report_output is not None else None,
    }


def _parse_stat(output: str) -> tuple[dict[str, float], list[str], float | None]:
    counts: dict[str, float] = {}
    errors: list[str] = []
    wall_time: float | None = None
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        time_match = _TIME_RE.search(line)
        if time_match:
            wall_time = _number(time_match.group(1))
            continue
        event = _event_from_line(line)
        if event is None:
            continue
        if "<not supported>" in line or "<not counted>" in line:
            errors.append(f"{event}: unsupported or not counted")
            continue
        value = _stat_value(line)
        if value is None:
            errors.append(f"{event}: unable to parse count")
        else:
            counts[event] = value
    missing = set(PERF_EVENTS) - set(counts) - {
        error.split(":", 1)[0] for error in errors
    }
    errors.extend(f"{event}: missing from perf output" for event in sorted(missing))
    return counts, errors, wall_time


def _event_from_line(line: str) -> str | None:
    for event in PERF_EVENTS:
        if re.search(rf"(?<![\w-]){re.escape(event)}(?=$|[\s,:])", line):
            return event
    return None


def _stat_value(line: str) -> float | None:
    first_field = line.split(",", 1)[0].strip()
    if first_field and first_field not in {"<not supported>", "<not counted>"}:
        value = _number(first_field)
        if value is not None:
            return value
    match = re.match(r"([\d,]+(?:\.\d+)?)\s+", line)
    return _number(match.group(1)) if match else None


def _number(value: str) -> float | None:
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return None


def _summary(counts: dict[str, float], wall_time: float | None) -> dict[str, float | None]:
    def ratio(numerator: str, denominator: str) -> float | None:
        denominator_value = counts.get(denominator)
        if not denominator_value:
            return None
        numerator_value = counts.get(numerator)
        return None if numerator_value is None else numerator_value / denominator_value

    # #4 deliberately excludes `branches`; branch-misses alone cannot form a
    # branch miss *rate*. Keeping it null prevents falsely calling a proxy rate.
    return {
        "ipc": ratio("instructions", "cycles"),
        "cache_miss_rate": ratio("cache-misses", "cache-references"),
        "branch_miss_rate": None,
        "wall_time_s": wall_time,
    }


def _parse_report(output: str) -> list[dict[str, Any]]:
    hotspots: list[dict[str, Any]] = []
    for line in output.splitlines():
        match = _REPORT_ROW_RE.match(line)
        if not match:
            continue
        hotspots.append(
            {
                "symbol": match.group("symbol"),
                "percent": float(match.group("percent")),
                "event_counts": {},
            }
        )
        if len(hotspots) == 15:
            break
    return hotspots
