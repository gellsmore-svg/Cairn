"""Interactionless hosted LLM wrappers for Cairn.

These wrappers keep provider-specific HTTP details outside the core analysis
modules. They implement the same small provider contract as CommandLLMProvider:
accept a prepared Cairn LLMRequest and return text.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from cairn.llm_adapters import LLMProvider, LLMRequest, LLMResponse


@dataclass
class HostedLLMConfig:
    provider: str
    model: str
    api_key_env: str
    endpoint: str
    temperature: float = 0.2
    top_p: float | None = None
    max_tokens: int | None = None
    structured: bool = False
    timeout: int = 120
    system: str | None = None


class HostedLLMProvider:
    """HTTP JSON LLM provider with non-interactive stdin-free execution."""

    def __init__(self, config: HostedLLMConfig, *, api_key: str | None = None):
        self.config = config
        self.api_key = api_key or os.environ.get(config.api_key_env)
        self.name = config.provider
        if not self.api_key:
            raise RuntimeError(f"{config.provider} API key missing; set {config.api_key_env}")

    def complete(self, request: LLMRequest) -> LLMResponse:
        payload = _payload(self.config, request)
        headers = {"Content-Type": "application/json"}
        if self.config.provider != "gemini":
            headers["Authorization"] = f"Bearer {self.api_key}"
        if self.config.provider == "anthropic":
            headers["x-api-key"] = self.api_key
            headers["anthropic-version"] = "2023-06-01"
            headers.pop("Authorization", None)
        req = Request(
            self.config.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urlopen(req, timeout=self.config.timeout) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"{self.config.provider} request failed: HTTP {exc.code}: {detail}") from exc
        text = _extract_text(self.config.provider, json.loads(raw))
        return LLMResponse(text=text, provider=self.config.provider, raw=raw)


def grok_provider(
    *,
    model: str = "grok-3-mini",
    api_key_env: str = "XAI_API_KEY",
    **kwargs: Any,
) -> HostedLLMProvider:
    return HostedLLMProvider(
        HostedLLMConfig(
            provider="grok",
            model=model,
            api_key_env=api_key_env,
            endpoint="https://api.x.ai/v1/chat/completions",
            **kwargs,
        )
    )


def openai_provider(
    *,
    model: str = "gpt-4.1-mini",
    api_key_env: str = "OPENAI_API_KEY",
    endpoint: str = "https://api.openai.com/v1/chat/completions",
    **kwargs: Any,
) -> HostedLLMProvider:
    return HostedLLMProvider(
        HostedLLMConfig(
            provider="openai",
            model=model,
            api_key_env=api_key_env,
            endpoint=endpoint,
            **kwargs,
        )
    )


def claude_provider(
    *,
    model: str = "claude-3-5-sonnet-latest",
    api_key_env: str = "ANTHROPIC_API_KEY",
    **kwargs: Any,
) -> HostedLLMProvider:
    return HostedLLMProvider(
        HostedLLMConfig(
            provider="anthropic",
            model=model,
            api_key_env=api_key_env,
            endpoint="https://api.anthropic.com/v1/messages",
            **kwargs,
        )
    )


def gemini_provider(
    *,
    model: str = "gemini-1.5-pro",
    api_key_env: str = "GEMINI_API_KEY",
    **kwargs: Any,
) -> HostedLLMProvider:
    key = os.environ.get(api_key_env)
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    if key:
        endpoint += f"?key={key}"
    return HostedLLMProvider(
        HostedLLMConfig(
            provider="gemini",
            model=model,
            api_key_env=api_key_env,
            endpoint=endpoint,
            **kwargs,
        ),
        api_key=key,
    )


def _payload(config: HostedLLMConfig, request: LLMRequest) -> dict[str, Any]:
    system = config.system or "You are a precise Cairn analysis assistant. Return concise, structured output."
    prompt = request.prompt
    if request.context:
        prompt += "\n\nContext JSON:\n" + json.dumps(request.context, ensure_ascii=False)

    if config.provider == "anthropic":
        payload: dict[str, Any] = {
            "model": config.model,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": config.temperature,
        }
        if config.max_tokens:
            payload["max_tokens"] = config.max_tokens
        return payload
    if config.provider == "gemini":
        payload = {
            "contents": [{"role": "user", "parts": [{"text": f"{system}\n\n{prompt}"}]}],
            "generationConfig": {"temperature": config.temperature},
        }
        if config.max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = config.max_tokens
        if config.top_p is not None:
            payload["generationConfig"]["topP"] = config.top_p
        if config.structured:
            payload["generationConfig"]["responseMimeType"] = "application/json"
        return payload

    payload = {
        "model": config.model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        "temperature": config.temperature,
    }
    if config.top_p is not None:
        payload["top_p"] = config.top_p
    if config.max_tokens:
        payload["max_tokens"] = config.max_tokens
    if config.structured:
        payload["response_format"] = {"type": "json_object"}
    return payload


def _extract_text(provider: str, payload: dict[str, Any]) -> str:
    if provider in {"openai", "grok"}:
        return str(payload["choices"][0]["message"]["content"])
    if provider == "anthropic":
        return "".join(part.get("text", "") for part in payload.get("content", []) if isinstance(part, dict))
    if provider == "gemini":
        candidates = payload.get("candidates", [])
        parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
        return "".join(part.get("text", "") for part in parts if isinstance(part, dict))
    return json.dumps(payload)


__all__ = [
    "HostedLLMConfig",
    "HostedLLMProvider",
    "claude_provider",
    "gemini_provider",
    "grok_provider",
    "openai_provider",
]
