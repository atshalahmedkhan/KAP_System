"""Optimization agent package."""

from archshift.optimization.agent import propose_optimization
from archshift.optimization.allowlist import (
    AllowlistViolationError,
    BuildContext,
    EmptyPatchError,
    OptimizationAgentError,
    OptimizationProposal,
    PriorAttempt,
    is_allowed_flag,
    validate_patch,
)

__all__ = [
    "AllowlistViolationError",
    "BuildContext",
    "EmptyPatchError",
    "OptimizationAgentError",
    "OptimizationProposal",
    "PriorAttempt",
    "is_allowed_flag",
    "propose_optimization",
    "validate_patch",
]
