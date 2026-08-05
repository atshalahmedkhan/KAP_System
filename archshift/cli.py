"""Command-line entrypoint for ArchShift."""

from __future__ import annotations

import argparse
from pathlib import Path

from archshift.runner import RuntimeCallbacks, run_loop
from archshift.target import TargetConfig


def main(argv: list[str] | None = None) -> int:
    """Run the ArchShift CLI."""

    parser = argparse.ArgumentParser(prog="archshift")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="profile → propose → verify loop")
    run_parser.add_argument(
        "--target",
        required=True,
        help="path to target JSON config (see issue #20 orchestration contract)",
    )
    args = parser.parse_args(argv)

    if args.command == "run":
        return _run_command(Path(args.target))
    parser.error(f"unknown command: {args.command}")
    return 2


def _run_command(target_path: Path) -> int:
    _ = load_target(target_path)
    # TODO(phase-c): replace with real Arm64 runtime adapters once C1/C2 land.
    raise SystemExit(
        "archshift run wiring is implemented, but production runtime callbacks are not "
        "configured yet. Use injected callbacks in tests or complete Phase C host setup."
    )


def load_target(path: Path) -> TargetConfig:
    """Load a target config from disk."""

    return TargetConfig.model_validate_json(path.read_text(encoding="utf-8"))


def run_with_callbacks(target_path: Path, callbacks: RuntimeCallbacks) -> int:
    """Run the loop with explicit runtime callbacks (used by tests and Phase C)."""

    outcome = run_loop(load_target(target_path), callbacks)
    return 0 if outcome.accepted or outcome.run_attempts > 0 else 1
