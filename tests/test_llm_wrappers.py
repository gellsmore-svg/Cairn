from __future__ import annotations

import json

import cairn
from cairn.llm_adapters import LLMRequest
from cairn.llm_wrappers import HostedLLMConfig, HostedLLMProvider


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_hosted_llm_provider_posts_openai_style_payload(monkeypatch):
    calls = {}

    def fake_urlopen(req, timeout):
        calls["timeout"] = timeout
        calls["body"] = json.loads(req.data.decode("utf-8"))
        return FakeResponse({"choices": [{"message": {"content": "ok"}}]})

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr("cairn.llm_wrappers.urlopen", fake_urlopen)
    provider = HostedLLMProvider(
        HostedLLMConfig(
            provider="openai",
            model="gpt-test",
            api_key_env="OPENAI_API_KEY",
            endpoint="https://example.test",
            structured=True,
            timeout=7,
        )
    )

    response = provider.complete(LLMRequest(task="demo", prompt="hello", context={"x": 1}))

    assert response.text == "ok"
    assert calls["timeout"] == 7
    assert calls["body"]["response_format"] == {"type": "json_object"}
    assert calls["body"]["messages"][1]["content"].startswith("hello")
    assert cairn.HostedLLMProvider is HostedLLMProvider
