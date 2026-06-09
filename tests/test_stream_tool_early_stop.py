import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import models
from helpers import extract_tools


def _chunk(content: str) -> dict:
    return {"choices": [{"delta": {"content": content}, "message": {}}]}


class _AsyncChunkStream:
    def __init__(self, chunks: list[dict]):
        self._chunks = chunks
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self._chunks):
            raise StopAsyncIteration
        chunk = self._chunks[self.index]
        self.index += 1
        return chunk


def test_extract_json_root_string_returns_canonical_snapshot():
    text = (
        'prefix {"tool_name":"response","tool_args":{"text":"brace } inside"}} '
        "trailing noise"
    )

    root = extract_tools.extract_json_root_string(text)

    assert root == '{"tool_name":"response","tool_args":{"text":"brace } inside"}}'
    assert extract_tools.json_parse_dirty(root)["tool_args"]["text"] == "brace } inside"
    assert extract_tools.extract_json_root_string(
        '{"tool_name":"response","tool_args":{"text":"missing"'
    ) is None
    assert extract_tools.extract_json_root_string('[{"tool_name":"response"}]') is None


def test_litellm_global_kwargs_merge_defaults_and_config(monkeypatch):
    monkeypatch.setattr(
        models.settings,
        "get_settings",
        lambda: {"litellm_global_kwargs": {}},
    )

    assert models._merge_litellm_call_kwargs({})["drop_params"] is True
    assert models._merge_litellm_call_kwargs({"temperature": 0}) == {
        "drop_params": True,
        "temperature": 0,
    }

    monkeypatch.setattr(
        models.settings,
        "get_settings",
        lambda: {"litellm_global_kwargs": {"drop_params": "false", "timeout": "30"}},
    )

    assert models._merge_litellm_call_kwargs({}) == {
        "drop_params": False,
        "timeout": 30,
    }

    original_drop_params = getattr(models.litellm, "drop_params", None)
    had_timeout = hasattr(models.litellm, "timeout")
    original_timeout = getattr(models.litellm, "timeout", None)
    try:
        assert models.set_litellm_params() == {
            "drop_params": False,
            "timeout": 30,
        }
        assert models.litellm.drop_params is False
        assert models.litellm.timeout == 30
    finally:
        setattr(models.litellm, "drop_params", original_drop_params)
        if had_timeout:
            setattr(models.litellm, "timeout", original_timeout)
        elif hasattr(models.litellm, "timeout"):
            delattr(models.litellm, "timeout")


@pytest.mark.asyncio
async def test_unified_call_stops_after_canonical_root_snapshot(monkeypatch):
    stream = _AsyncChunkStream(
        [
            _chunk(
                '{"tool_name":"response","tool_args":{"text":"hello"}} trailing text'
            ),
            _chunk(" unreachable"),
        ]
    )

    async def fake_acompletion(*args, **kwargs):
        assert kwargs["stream"] is True
        assert kwargs["drop_params"] is True
        return stream

    async def fake_rate_limiter(*args, **kwargs):
        return None

    monkeypatch.setattr(models, "acompletion", fake_acompletion)
    monkeypatch.setattr(models, "apply_rate_limiter", fake_rate_limiter)
    monkeypatch.setattr(
        models.settings,
        "get_settings",
        lambda: {"litellm_global_kwargs": {}},
    )

    wrapper = models.LiteLLMChatWrapper(
        model="test-model",
        provider="openai",
        model_config=None,
    )

    seen: list[tuple[str, str]] = []

    async def response_callback(chunk: str, full: str):
        seen.append((chunk, full))
        snapshot = extract_tools.extract_json_root_string(full)
        if snapshot:
            return snapshot
        return None

    response, reasoning = await wrapper.unified_call(
        messages=[],
        response_callback=response_callback,
    )

    assert response == '{"tool_name":"response","tool_args":{"text":"hello"}}'
    assert reasoning == ""
    assert stream.index == 1
    assert len(seen) == 1
    assert seen[0][1] == '{"tool_name":"response","tool_args":{"text":"hello"}} trailing text'
