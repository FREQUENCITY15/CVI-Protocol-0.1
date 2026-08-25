"""
Participant-facing LLM client.

EXPERIMENTAL FIREWALL (enforced in code, not merely by instruction):

1. This module contains NO knowledge of tasks, generators, graders, seeds,
   or answer keys.  It imports none of them.  It can only send text it is
   given and return text it receives.
2. Every call is a CLEAN context: the client keeps no conversational state
   between calls.  The arm layer passes exactly the messages it wants the
   participant to see; across a context boundary the arm layer passes a
   fresh single-turn message list (verified by tests).
3. No tools / function calling / RAG / file access is ever enabled for a
   participant call.  A participant response is only ever parsed as text
   (program sections).  A participant can *ask* for hidden material in its
   response text, but nothing in the harness will retrieve it.
4. Runaway protection: a usage tracker with hard call/token budgets raises
   RunawayGuardError, which stops the participant phase safely.
"""

from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol

from .config import ModelConfig


class RunawayGuardError(RuntimeError):
    pass


@dataclass
class UsageTracker:
    max_calls: int
    max_input_tokens: int
    max_output_tokens: int
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0
    retries: int = 0
    api_errors: List[Dict[str, Any]] = field(default_factory=list)
    call_log: List[Dict[str, Any]] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def check(self) -> None:
        if self.calls >= self.max_calls:
            raise RunawayGuardError(
                f"runaway guard: API call budget exceeded "
                f"({self.calls} >= {self.max_calls})")
        if self.input_tokens >= self.max_input_tokens:
            raise RunawayGuardError(
                f"runaway guard: input token budget exceeded "
                f"({self.input_tokens} >= {self.max_input_tokens})")
        if self.output_tokens >= self.max_output_tokens:
            raise RunawayGuardError(
                f"runaway guard: output token budget exceeded "
                f"({self.output_tokens} >= {self.max_output_tokens})")

    def record(self, label: str, model: str, input_tokens: int,
               output_tokens: int, cache_read: int, cache_creation: int,
               latency_s: float, error: Optional[str] = None) -> None:
        with self._lock:
            self.calls += 1
            self.input_tokens += input_tokens
            self.output_tokens += output_tokens
            self.cache_read_tokens += cache_read
            self.cache_creation_tokens += cache_creation
            self.call_log.append({
                "index": self.calls,
                "label": label,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cache_read_tokens": cache_read,
                "cache_creation_tokens": cache_creation,
                "latency_s": round(latency_s, 3),
                "error": error,
            })

    def to_dict(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "calls": self.calls,
                "input_tokens": self.input_tokens,
                "output_tokens": self.output_tokens,
                "cache_read_tokens": self.cache_read_tokens,
                "cache_creation_tokens": self.cache_creation_tokens,
                "retries": self.retries,
                "api_errors": list(self.api_errors),
                "call_log": list(self.call_log),
            }


@dataclass
class LLMResponse:
    text: str
    model: str
    stop_reason: str
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_creation_tokens: int
    latency_s: float
    raw: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "model": self.model,
            "stop_reason": self.stop_reason,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cache_read_tokens": self.cache_read_tokens,
            "cache_creation_tokens": self.cache_creation_tokens,
            "latency_s": self.latency_s,
        }


class ParticipantClient(Protocol):
    """Minimal participant-call interface.  Implementations must be
    stateless between calls and must never consult anything outside the
    arguments they are given."""

    def complete(self, system: str, messages: List[Dict[str, str]],
                 max_tokens: int, label: str) -> LLMResponse:
        ...


class DeepSeekAnthropicClient:
    """Talks to the DeepSeek API's Anthropic-compatible endpoint.

    One call == one clean POST with exactly the provided messages.  No
    session state, no caching, no tools.
    """

    def __init__(self, config: ModelConfig, tracker: UsageTracker,
                 api_key: str):
        self.config = config
        self.tracker = tracker
        # The API key is held ONLY in memory (injected from the
        # environment at run time) and is never serialized anywhere.
        self.api_key = api_key

    def complete(self, system: str, messages: List[Dict[str, str]],
                 max_tokens: int, label: str) -> LLMResponse:
        body: Dict[str, Any] = {
            "model": self.config.model,
            "max_tokens": max_tokens,
            "temperature": self.config.temperature,
            "system": system,
            "messages": messages,
        }
        if self.config.thinking_disabled:
            body["thinking"] = {"type": "disabled"}
        payload = json.dumps(body).encode("utf-8")
        last_error: Optional[str] = None
        for attempt in range(self.config.max_retries):
            self.tracker.check()
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            req = urllib.request.Request(
                f"{self.config.endpoint}/messages", data=payload,
                headers=headers, method="POST")
            started = time.monotonic()
            try:
                with urllib.request.urlopen(req,
                                            timeout=self.config.timeout_s) as resp:
                    raw = json.loads(resp.read().decode("utf-8"))
                latency = time.monotonic() - started
                text = "\n".join(
                    b.get("text", "")
                    for b in raw.get("content", [])
                    if b.get("type") == "text")
                usage = raw.get("usage", {})
                self.tracker.record(
                    label=label, model=raw.get("model", self.config.model),
                    input_tokens=usage.get("input_tokens", 0),
                    output_tokens=usage.get("output_tokens", 0),
                    cache_read=usage.get("cache_read_input_tokens", 0),
                    cache_creation=usage.get("cache_creation_input_tokens", 0),
                    latency_s=latency)
                return LLMResponse(
                    text=text, model=raw.get("model", self.config.model),
                    stop_reason=raw.get("stop_reason", ""),
                    input_tokens=usage.get("input_tokens", 0),
                    output_tokens=usage.get("output_tokens", 0),
                    cache_read_tokens=usage.get("cache_read_input_tokens", 0),
                    cache_creation_tokens=usage.get(
                        "cache_creation_input_tokens", 0),
                    latency_s=latency, raw=raw)
            except urllib.error.HTTPError as exc:
                last_error = f"HTTP {exc.code}: {exc.read(400).decode('utf-8', 'replace')}"
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_error = f"network: {exc}"
            if attempt < self.config.max_retries - 1:
                self.tracker.retries += 1
                time.sleep(2 ** attempt)
        self.tracker.record(label=label, model=self.config.model,
                            input_tokens=0, output_tokens=0, cache_read=0,
                            cache_creation=0, latency_s=0.0, error=last_error)
        self.tracker.api_errors.append({"label": label, "error": last_error})
        raise RuntimeError(f"participant API call failed after "
                           f"{self.config.max_retries} attempts: {last_error}")
