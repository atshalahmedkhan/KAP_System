from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from archshift.optimization import (
    AllowlistViolationError,
    BuildContext,
    EmptyPatchError,
    PriorAttempt,
    is_allowed_flag,
    propose_optimization,
    validate_patch,
)
from archshift.optimization.allowlist import PatchEntry

FIXTURE_PROFILE = json.loads(
    (Path(__file__).parent / "fixtures" / "profile-degraded.json").read_text(encoding="utf-8")
)


def test_allowlist_accepts_locked_flags() -> None:
    assert is_allowed_flag("-mcpu=native")
    assert is_allowed_flag("+dotprod")
    assert is_allowed_flag("+i8mm")
    assert is_allowed_flag("GGML_Q4_0_REPACK=ON")
    assert is_allowed_flag("-DCMAKE_CXX_FLAGS=+dotprod")


def test_allowlist_rejects_unknown_flags() -> None:
    assert not is_allowed_flag("-O3")
    assert not is_allowed_flag("src/ggml.c")
    assert not is_allowed_flag("-DCMAKE_CXX_FLAGS=-O3")


def test_validate_patch_rejects_empty_and_disallowed() -> None:
    with pytest.raises(EmptyPatchError):
        validate_patch([])
    with pytest.raises(AllowlistViolationError):
        validate_patch(
            [PatchEntry(flag="-O3", action="add", rationale="unsafe")]
        )


def test_propose_optimization_returns_validated_proposal(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "hypothesis": "Adding +dotprod should accelerate Q4 matmul kernels.",
        "patch": [
            {
                "flag": "+dotprod",
                "action": "add",
                "rationale": "Profile shows matmul symbols dominate runtime.",
            }
        ],
        "expected_impact": {
            "metric": "wall_time_s",
            "direction": "faster",
            "magnitude_pct": 4.5,
        },
        "confidence": 0.62,
    }

    class FakeMessages:
        def create(self, **_: object) -> SimpleNamespace:
            return SimpleNamespace(
                content=[SimpleNamespace(type="text", text=json.dumps(payload))]
            )

    fake_client = SimpleNamespace(messages=FakeMessages())
    proposal = propose_optimization(
        FIXTURE_PROFILE,
        hotspot_context="ggml_vec_dot_q4_0_q8_0",
        build_context=BuildContext(
            cmake_flags=["-DCMAKE_BUILD_TYPE=Release"],
            cpu_features=["neon"],
            compiler_version="gcc 13.2.0",
        ),
        prior_attempts=[
            PriorAttempt(
                patch=[{"flag": "+i8mm", "action": "add", "rationale": "retry"}],
                hypothesis="Prior i8mm attempt",
                rejection_reason="benchmark noise threshold not cleared",
            )
        ],
        client=fake_client,
    )

    assert proposal.patch[0].flag == "+dotprod"
    assert proposal.expected_impact.direction == "faster"


def test_propose_optimization_rejects_disallowed_model_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = {
        "hypothesis": "Edit source for speed.",
        "patch": [
            {
                "flag": "src/ggml.c",
                "action": "add",
                "rationale": "forbidden",
            }
        ],
        "expected_impact": {
            "metric": "wall_time_s",
            "direction": "faster",
            "magnitude_pct": 1.0,
        },
        "confidence": 0.1,
    }

    class FakeMessages:
        def create(self, **_: object) -> SimpleNamespace:
            return SimpleNamespace(
                content=[SimpleNamespace(type="text", text=json.dumps(payload))]
            )

    fake_client = SimpleNamespace(messages=FakeMessages())
    with pytest.raises(AllowlistViolationError):
        propose_optimization(
            FIXTURE_PROFILE,
            hotspot_context="ggml_vec_dot_q4_0_q8_0",
            build_context=BuildContext(),
            client=fake_client,
        )
