"""Optimization agent: profile JSON in, validated flag patch out."""

from __future__ import annotations

import json
import logging
from typing import Any

import anthropic
from anthropic.types import Message

from archshift.config import get_settings
from archshift.optimization.allowlist import (
    AllowlistViolationError,
    BuildContext,
    EmptyPatchError,
    OptimizationAgentError,
    OptimizationProposal,
    PatchEntry,
    PriorAttempt,
    validate_patch,
)

LOGGER = logging.getLogger(__name__)

MODEL_ID = "claude-opus-5"
OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "hypothesis": {"type": "string"},
        "patch": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "flag": {"type": "string"},
                    "action": {"type": "string", "enum": ["add", "remove"]},
                    "rationale": {"type": "string"},
                },
                "required": ["flag", "action", "rationale"],
                "additionalProperties": False,
            },
        },
        "expected_impact": {
            "type": "object",
            "properties": {
                "metric": {"type": "string"},
                "direction": {"type": "string", "enum": ["faster", "slower"]},
                "magnitude_pct": {"type": "number"},
            },
            "required": ["metric", "direction", "magnitude_pct"],
            "additionalProperties": False,
        },
        "confidence": {"type": "number"},
    },
    "required": ["hypothesis", "patch", "expected_impact", "confidence"],
    "additionalProperties": False,
}


def propose_optimization(
    profile: dict[str, Any],
    *,
    hotspot_context: str,
    build_context: BuildContext,
    prior_attempts: list[PriorAttempt] | None = None,
    client: anthropic.Anthropic | None = None,
) -> OptimizationProposal:
    """Call Claude and return an allowlist-validated optimization proposal."""

    prompt = _build_prompt(
        profile=profile,
        hotspot_context=hotspot_context,
        build_context=build_context,
        prior_attempts=prior_attempts or [],
    )
    api_client = client or _default_client()
    response = api_client.messages.create(
        model=MODEL_ID,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        output_config={
            "format": {
                "type": "json_schema",
                "schema": OUTPUT_SCHEMA,
            },
            "effort": "high",
        },
        messages=[{"role": "user", "content": prompt}],
    )
    proposal = _parse_response(response)
    try:
        validate_patch(proposal.patch)
    except (AllowlistViolationError, EmptyPatchError) as exc:
        LOGGER.error("optimization proposal rejected by allowlist", exc_info=exc)
        raise
    return proposal


def _default_client() -> anthropic.Anthropic:
    settings = get_settings()
    if settings.anthropic_api_key is None:
        raise OptimizationAgentError("ANTHROPIC_API_KEY is required for live optimization calls")
    return anthropic.Anthropic(api_key=settings.anthropic_api_key.get_secret_value())


def _build_prompt(
    *,
    profile: dict[str, Any],
    hotspot_context: str,
    build_context: BuildContext,
    prior_attempts: list[PriorAttempt],
) -> str:
    prior_block = "None."
    if prior_attempts:
        prior_block = json.dumps(
            [attempt.model_dump() for attempt in prior_attempts],
            indent=2,
            sort_keys=True,
        )
    return (
        "You are the ArchShift optimization agent. change_scope is build flags / CMake "
        "configuration only. Do not propose source edits, test changes, benchmark harness "
        "changes, or correctness-checker changes.\n\n"
        "Allowed flags only:\n"
        "- -mcpu=native\n"
        "- +dotprod\n"
        "- +i8mm\n"
        "- CMake cache variables that clearly toggle Q4_0 / GGML pack or repack only\n"
        "- CMAKE_C_FLAGS / CMAKE_CXX_FLAGS entries that add only the flags above\n\n"
        "Return one hypothesis grounded in a specific profile figure, a non-empty patch, "
        "expected impact, and a self-rated confidence between 0 and 1. Confidence is "
        "display-only and does not gate acceptance.\n\n"
        f"Profile JSON:\n{json.dumps(profile, indent=2, sort_keys=True)}\n\n"
        f"Hotspot function context:\n{hotspot_context}\n\n"
        f"Build context:\n{build_context.model_dump_json(indent=2)}\n\n"
        f"Prior rejected attempts:\n{prior_block}"
    )


def _parse_response(response: Message) -> OptimizationProposal:
    for block in response.content:
        if block.type != "text":
            continue
        payload = json.loads(block.text)
        proposal = OptimizationProposal.model_validate(payload)
        proposal.patch = [PatchEntry.model_validate(entry) for entry in proposal.patch]
        return proposal
    raise OptimizationAgentError("model response did not include structured JSON text")
