"""Provider-neutral LLM adapter seam for Cairn.

Adapters are deliberately tiny: Cairn prepares a prompt/context and providers
return text. A provider can be a local llama.cpp wrapper, an Ollama script, a
Hoglah queue submitter, or any CLI that reads stdin and writes stdout.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import shlex
import subprocess
from typing import Protocol


@dataclass
class LLMRequest:
    task: str
    prompt: str
    context: dict


@dataclass
class LLMResponse:
    text: str
    provider: str
    raw: str | None = None


class LLMProvider(Protocol):
    name: str

    def complete(self, request: LLMRequest) -> LLMResponse:
        ...


class CommandLLMProvider:
    """Run an external command as an LLM provider.

    The command receives a JSON payload on stdin:
    ``{"task": ..., "prompt": ..., "context": ...}``

    If stdout is JSON with a ``text`` field, that field is used. Otherwise stdout
    is treated as the response text. This makes it easy to wrap llama.cpp,
    Ollama, Hoglah submission scripts, or hosted-model CLIs.
    """

    name = "command"

    def __init__(self, command: str | list[str], *, timeout: int = 120):
        self.command = shlex.split(command) if isinstance(command, str) else command
        self.timeout = timeout

    def complete(self, request: LLMRequest) -> LLMResponse:
        payload = json.dumps(
            {"task": request.task, "prompt": request.prompt, "context": request.context},
            ensure_ascii=False,
        )
        proc = subprocess.run(
            self.command,
            input=payload,
            text=True,
            capture_output=True,
            timeout=self.timeout,
            check=False,
        )
        if proc.returncode != 0:
            detail = proc.stderr.strip() or proc.stdout.strip()
            raise RuntimeError(f"LLM command failed with exit code {proc.returncode}: {detail}")
        raw = proc.stdout.strip()
        text = raw
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict) and isinstance(parsed.get("text"), str):
            text = parsed["text"]
        return LLMResponse(text=text, provider=self.name, raw=raw)
