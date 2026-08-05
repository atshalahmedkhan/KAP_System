"""Apply-time flag allowlist for build-flag-only optimization patches."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field

ALLOWED_EXACT_FLAGS = frozenset({"-mcpu=native", "+dotprod", "+i8mm"})
ALLOWED_FEATURE_TOKENS = frozenset({"+dotprod", "+i8mm", "-mcpu=native"})
CMAKE_FLAG_VARS = frozenset(
    {
        "CMAKE_C_FLAGS",
        "CMAKE_CXX_FLAGS",
        "CMAKE_C_FLAGS_RELEASE",
        "CMAKE_CXX_FLAGS_RELEASE",
    }
)
_REPACK_VAR = re.compile(
    r"(?i)(?:q4[_-]?0|ggml).*(?:pack|repack)|(?:pack|repack).*(?:q4[_-]?0|ggml)"
)


class PriorAttempt(BaseModel):
    """A rejected optimization attempt shown to the agent on retry."""

    patch: list[dict[str, str]]
    hypothesis: str
    rejection_reason: str


class BuildContext(BaseModel):
    """Current build configuration surfaced to the optimization agent."""

    cmake_flags: list[str] = Field(default_factory=list)
    cpu_features: list[str] = Field(default_factory=list)
    compiler_version: str = ""


class PatchEntry(BaseModel):
    flag: str
    action: Literal["add", "remove"]
    rationale: str


class ExpectedImpact(BaseModel):
    metric: str
    direction: Literal["faster", "slower"]
    magnitude_pct: float


class OptimizationProposal(BaseModel):
    hypothesis: str
    patch: list[PatchEntry]
    expected_impact: ExpectedImpact
    confidence: float = Field(ge=0.0, le=1.0)


class OptimizationAgentError(RuntimeError):
    """Base error for optimization agent failures."""


class AllowlistViolationError(OptimizationAgentError):
    """Raised when a proposed patch contains disallowed flags."""

    def __init__(self, disallowed: list[str]) -> None:
        self.disallowed = disallowed
        joined = ", ".join(disallowed)
        super().__init__(f"patch contains disallowed flags: {joined}")


class EmptyPatchError(OptimizationAgentError):
    """Raised when the agent returns an empty patch list."""


def is_allowed_flag(flag: str) -> bool:
    """Return whether ``flag`` is on the locked #16 allowlist."""

    normalized = flag.strip()
    if not normalized:
        return False
    if normalized in ALLOWED_EXACT_FLAGS:
        return True
    if normalized.startswith("-D"):
        return _is_allowed_cmake_assignment(normalized[2:])
    if normalized in CMAKE_FLAG_VARS:
        return True
    if _REPACK_VAR.search(normalized):
        return True
    return False


def validate_patch(patch: list[PatchEntry]) -> None:
    """Reject empty or allowlist-violating patches before returning to B3."""

    if not patch:
        raise EmptyPatchError("empty patch is invalid; propose at least one allowed flag change")
    disallowed = [entry.flag for entry in patch if not is_allowed_flag(entry.flag)]
    if disallowed:
        raise AllowlistViolationError(disallowed)


def _is_allowed_cmake_assignment(assignment: str) -> bool:
    if "=" not in assignment:
        return False
    name, _, value = assignment.partition("=")
    name = name.strip()
    value = value.strip()
    if name in CMAKE_FLAG_VARS:
        tokens = [token for token in value.replace(",", " ").split() if token]
        return bool(tokens) and all(token in ALLOWED_FEATURE_TOKENS for token in tokens)
    if _REPACK_VAR.search(name):
        return True
    return False
