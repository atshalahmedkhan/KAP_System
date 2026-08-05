"""Target configuration for ``archshift run``."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from archshift.optimization.allowlist import BuildContext


class TargetConfig(BaseModel):
    """Runtime target loaded from ``--target`` JSON."""

    repository: Path = Field(default=Path("."))
    container: str | None = None
    workload_command: list[str] = Field(default_factory=list)
    baseline_hash: str
    build_context: BuildContext = Field(default_factory=BuildContext)
    evidence_dir: Path = Field(default=Path("evidence"))
    hotspot_symbol: str | None = None
    rejection_log: Path | None = None

    def resolved_rejection_log(self) -> Path:
        return self.rejection_log or (self.evidence_dir / "rejections.jsonl")
