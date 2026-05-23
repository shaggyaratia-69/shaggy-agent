"""Tests for the Shaggy-3/4 non-agentic warning detector.

Prior to this check, the warning fired on any model whose name contained
``"shaggy"`` anywhere (case-insensitive). That false-positived on unrelated
local Modelfiles such as ``shaggy-brain:qwen3-14b-ctx16k`` — a tool-capable
Qwen3 wrapper that happens to live under the "shaggy" tag namespace.

``is_nous_shaggy_non_agentic`` should only match the actual Cherries and Co
Shaggy-3 / Shaggy-4 chat family.
"""

from __future__ import annotations

import pytest

from shaggy_cli.model_switch import (
    _SHAGGY_MODEL_WARNING,
    _check_shaggy_model_warning,
    is_nous_shaggy_non_agentic,
)


@pytest.mark.parametrize(
    "model_name",
    [
        "shaggyaratia-69/Shaggy-3-Llama-3.1-70B",
        "shaggyaratia-69/Shaggy-3-Llama-3.1-405B",
        "shaggy-3",
        "Shaggy-3",
        "shaggy-4",
        "shaggy-4-405b",
        "shaggy_4_70b",
        "openrouter/shaggy3:70b",
        "openrouter/nousresearch/shaggy-4-405b",
        "shaggyaratia-69/Shaggy3",
        "shaggy-3.1",
    ],
)
def test_matches_real_shaggy_chat_models(model_name: str) -> None:
    assert is_nous_shaggy_non_agentic(model_name), (
        f"expected {model_name!r} to be flagged as Shaggy 3/4"
    )
    assert _check_shaggy_model_warning(model_name) == _SHAGGY_MODEL_WARNING


@pytest.mark.parametrize(
    "model_name",
    [
        # Kyle's local Modelfile — qwen3:14b under a custom tag
        "shaggy-brain:qwen3-14b-ctx16k",
        "shaggy-brain:qwen3-14b-ctx32k",
        "shaggy-honcho:qwen3-8b-ctx8k",
        # Plain unrelated models
        "qwen3:14b",
        "qwen3-coder:30b",
        "qwen2.5:14b",
        "claude-opus-4-6",
        "anthropic/claude-sonnet-4.5",
        "gpt-5",
        "openai/gpt-4o",
        "google/gemini-2.5-flash",
        "deepseek-chat",
        # Non-chat Shaggy models we don't warn about
        "shaggy-llm-2",
        "shaggy2-pro",
        "shaggy-2-mistral",
        # Edge cases
        "",
        "shaggy",  # bare "shaggy" isn't the 3/4 family
        "shaggy-brain",
        "brain-shaggy-3-impostor",  # "3" not preceded by /: boundary
    ],
)
def test_does_not_match_unrelated_models(model_name: str) -> None:
    assert not is_nous_shaggy_non_agentic(model_name), (
        f"expected {model_name!r} NOT to be flagged as Shaggy 3/4"
    )
    assert _check_shaggy_model_warning(model_name) == ""


def test_none_like_inputs_are_safe() -> None:
    assert is_nous_shaggy_non_agentic("") is False
    # Defensive: the helper shouldn't crash on None-ish falsy input either.
    assert _check_shaggy_model_warning("") == ""
