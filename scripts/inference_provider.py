"""Secure, optional inference boundary for V2.2.

This module is intentionally separate from V2.1 deterministic helpers. It makes no
network request until a caller explicitly invokes ``complete`` with permission for
external inference. Credentials are read only from the configured runtime environment
variable, retained in memory for one request, and never returned, logged, or serialized.
"""

from __future__ import annotations

import json
import os
import re
import socket
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "inference_runtime.json"
_SECRET_PATTERNS = (
    re.compile(r"(?i)(?:bearer\s+|api[_-]?key\s*[:=]\s*)[a-z0-9_\-]{8,}"),
    re.compile(r"(?i)sk-[a-z0-9_\-]{8,}"),
)


class InferenceError(RuntimeError):
    """A safe error intended for agent-facing handling, never raw provider output."""

    def __init__(self, code: str, message: str, retryable: bool = False) -> None:
        self.code = code
        self.retryable = retryable
        super().__init__(message)


def _redact(value: str) -> str:
    """Remove recognizable credential fragments from defensive error text."""
    redacted = value
    for pattern in _SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


@dataclass(frozen=True)
class InferenceSettings:
    provider: str
    mode: str
    base_url: str
    allowed_hosts: tuple[str, ...]
    api_key_env: str
    model_env: str
    model_id: str | None
    temperature: float
    max_output_tokens: int
    timeout_seconds: float
    max_retries: int
    retry_backoff_seconds: float
    mock_response: str


@dataclass(frozen=True)
class InferenceResult:
    provider: str
    model: str
    content: str
    purpose: str
    usage: Mapping[str, int]

    def as_dict(self) -> dict[str, Any]:
        """Return only report-safe result fields; no headers, credentials, or raw payload."""
        return {
            "provider": self.provider,
            "model": self.model,
            "content": self.content,
            "purpose": self.purpose,
            "usage": dict(self.usage),
        }


Transport = Callable[[str, bytes, Mapping[str, str], float], tuple[int, bytes]]
Sleeper = Callable[[float], None]


def _config_error(message: str) -> InferenceError:
    return InferenceError("INVALID_INFERENCE_CONFIGURATION", message)


def load_settings(
    config_path: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> InferenceSettings:
    """Load and validate non-secret runtime settings without reading any credential."""
    path = config_path or DEFAULT_CONFIG_PATH
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise _config_error("Inference configuration is unavailable. Contact the publisher.") from exc
    except json.JSONDecodeError as exc:
        raise _config_error("Inference configuration is invalid. Contact the publisher.") from exc

    runtime = raw.get("runtime", {})
    provider = str(runtime.get("provider", "")).strip().lower()
    mode_env = str(runtime.get("mode_env", "DDI_INFERENCE_MODE"))
    active_environment = environ or os.environ
    mode = str(active_environment.get(mode_env, runtime.get("default_mode", "production"))).strip().lower()
    base_url = str(runtime.get("base_url", "")).rstrip("/")
    parsed = urlparse(base_url)
    allowed_hosts = tuple(str(item).lower() for item in runtime.get("allowed_hosts", []))
    if provider != "openrouter":
        raise _config_error("The configured inference provider is not supported by this release.")
    if mode not in {"production", "mock"}:
        raise _config_error("Inference mode must be production or mock.")
    if parsed.scheme != "https" or not parsed.hostname:
        raise _config_error("Inference endpoint must be an HTTPS URL.")
    if not allowed_hosts or parsed.hostname.lower() not in allowed_hosts:
        raise _config_error("Inference endpoint is not approved for this package configuration.")

    api_key_env = str(runtime.get("api_key_env", "")).strip()
    model_env = str(runtime.get("model_env", "")).strip()
    if not api_key_env or not model_env:
        raise _config_error("Inference runtime variable names are missing from configuration.")
    raw_configured_model = runtime.get("model_id")
    configured_model = str(raw_configured_model).strip() if isinstance(raw_configured_model, str) else None
    model_id = str(active_environment.get(model_env, configured_model or "")).strip() or None
    if mode == "production" and not model_id:
        raise _config_error("No production model is configured. The publisher must set the configured model variable.")
    if model_id and not re.fullmatch(r"[a-zA-Z0-9_.~:-]+/[a-zA-Z0-9_.~:-]+(?::[a-zA-Z0-9_.-]+)?", model_id):
        raise _config_error("The configured model identifier is invalid.")

    generation = runtime.get("generation", {})
    timeout = runtime.get("timeout", {})
    retry = runtime.get("retry", {})
    try:
        temperature = float(generation.get("temperature", 0.1))
        max_output_tokens = int(generation.get("max_output_tokens", 3000))
        timeout_seconds = float(timeout.get("seconds", 45))
        max_retries = int(retry.get("max_retries", 1))
        retry_backoff_seconds = float(retry.get("backoff_seconds", 0.25))
    except (TypeError, ValueError) as exc:
        raise _config_error("Inference generation or timeout settings are invalid.") from exc
    if not 0 <= temperature <= 2 or not 1 <= max_output_tokens <= 32000:
        raise _config_error("Inference generation settings are outside allowed bounds.")
    if not 1 <= timeout_seconds <= 180 or not 0 <= max_retries <= 3 or not 0 <= retry_backoff_seconds <= 5:
        raise _config_error("Inference timeout or retry settings are outside allowed bounds.")

    return InferenceSettings(
        provider=provider,
        mode=mode,
        base_url=base_url,
        allowed_hosts=allowed_hosts,
        api_key_env=api_key_env,
        model_env=model_env,
        model_id=model_id,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
        mock_response=str(runtime.get("mock_response", "Mock contextual interpretation for deterministic local testing.")),
    )


def _validate_messages(messages: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    if not messages:
        raise InferenceError("INVALID_INFERENCE_INPUT", "No inference messages were supplied.")
    normalized: list[dict[str, str]] = []
    for message in messages:
        role = str(message.get("role", "")).strip()
        content = message.get("content")
        if role not in {"system", "user", "assistant"} or not isinstance(content, str) or not content.strip():
            raise InferenceError("INVALID_INFERENCE_INPUT", "Inference messages must contain a supported role and non-empty text.")
        normalized.append({"role": role, "content": content})
    return normalized


def _safe_usage(value: Any) -> dict[str, int]:
    if not isinstance(value, Mapping):
        return {}
    result: dict[str, int] = {}
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        item = value.get(key)
        if isinstance(item, int) and item >= 0:
            result[key] = item
    return result


def _safe_provider_error(status: int, payload: Any) -> InferenceError:
    code = ""
    if isinstance(payload, Mapping):
        error = payload.get("error")
        if isinstance(error, Mapping):
            code = str(error.get("code", "")).lower()
        elif isinstance(error, str):
            code = error.lower()
    if status in {401, 403}:
        return InferenceError("AUTHENTICATION_FAILED", "Inference authentication failed. The publisher must verify the hosted credential.")
    if status == 429:
        return InferenceError("RATE_LIMITED", "The inference provider is temporarily rate-limited. Please retry later.", retryable=True)
    if status in {408, 504}:
        return InferenceError("PROVIDER_TIMEOUT", "The inference provider timed out. Please retry later.", retryable=True)
    if status >= 500:
        return InferenceError("PROVIDER_UNAVAILABLE", "The inference provider is temporarily unavailable. Please retry later.", retryable=True)
    if "context" in code and ("length" in code or "limit" in code):
        return InferenceError("CONTEXT_LENGTH_EXCEEDED", "The supplied material exceeds the configured model context. Reduce or stage the material and retry.")
    return InferenceError("PROVIDER_REQUEST_FAILED", "The inference provider could not process this request. Please retry or contact the publisher.")


def _decode_response(status: int, body: bytes, purpose: str) -> InferenceResult:
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InferenceError("MALFORMED_PROVIDER_RESPONSE", "The inference provider returned an unreadable response. Please retry later.") from exc
    if status < 200 or status >= 300:
        raise _safe_provider_error(status, payload)
    if not isinstance(payload, Mapping):
        raise InferenceError("MALFORMED_PROVIDER_RESPONSE", "The inference provider returned an invalid response. Please retry later.")
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], Mapping):
        raise InferenceError("MALFORMED_PROVIDER_RESPONSE", "The inference provider returned an incomplete response. Please retry later.")
    choice = choices[0]
    message = choice.get("message")
    if not isinstance(message, Mapping):
        raise InferenceError("MALFORMED_PROVIDER_RESPONSE", "The inference provider returned an incomplete response. Please retry later.")
    if message.get("refusal") or choice.get("finish_reason") in {"content_filter", "refusal"}:
        raise InferenceError("MODEL_REFUSAL", "The configured model declined this inference task. Refine the permitted request or use the documented fallback process.")
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise InferenceError("MALFORMED_PROVIDER_RESPONSE", "The inference provider returned no usable content. Please retry later.")
    model = str(payload.get("model", "")).strip()
    if not model:
        raise InferenceError("MALFORMED_PROVIDER_RESPONSE", "The inference provider did not identify the model used. Please retry later.")
    return InferenceResult(provider="openrouter", model=model, content=content, purpose=purpose, usage=_safe_usage(payload.get("usage")))


def _default_transport(url: str, body: bytes, headers: Mapping[str, str], timeout: float) -> tuple[int, bytes]:
    request = Request(url, data=body, headers=dict(headers), method="POST")
    try:
        with urlopen(request, timeout=timeout) as response:  # nosec B310: URL is validated against the configured HTTPS allowlist
            return int(response.getcode()), response.read()
    except HTTPError as exc:
        return int(exc.code), exc.read()
    except (URLError, socket.timeout, TimeoutError) as exc:
        raise InferenceError("NETWORK_FAILURE", "The inference provider could not be reached. Please retry later.", retryable=True) from exc


class OpenRouterProvider:
    """OpenRouter implementation of the narrow V2.2 inference-provider contract."""

    def __init__(
        self,
        settings: InferenceSettings,
        environ: Mapping[str, str] | None = None,
        transport: Transport | None = None,
        sleeper: Sleeper | None = None,
    ) -> None:
        self.settings = settings
        self._environ = environ if environ is not None else os.environ
        self._transport = transport or _default_transport
        self._sleeper = sleeper or time.sleep

    def complete(
        self,
        messages: Sequence[Mapping[str, Any]],
        purpose: str,
        *,
        external_data_permitted: bool = False,
    ) -> InferenceResult:
        """Request permitted contextual inference; never expose raw provider data or credential material."""
        if self.settings.mode == "mock":
            return MockProvider(self.settings).complete(messages, purpose, external_data_permitted=external_data_permitted)
        if not external_data_permitted:
            raise InferenceError("EXTERNAL_INFERENCE_NOT_PERMITTED", "External inference is not permitted for this execution. Use document-only mode or obtain the required permission.")
        normalized_messages = _validate_messages(messages)
        credential = str(self._environ.get(self.settings.api_key_env, "")).strip()
        if not credential:
            raise InferenceError("MISSING_CREDENTIAL", "The inference credential is not configured. The publisher must configure the hosted runtime credential.")
        if not self.settings.model_id:
            raise _config_error("No production model is configured. The publisher must set the configured model variable.")

        body = json.dumps(
            {
                "model": self.settings.model_id,
                "messages": normalized_messages,
                "temperature": self.settings.temperature,
                "max_tokens": self.settings.max_output_tokens,
                "stream": False,
            }, separators=(",", ":"), ensure_ascii=False,
        ).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {credential}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        endpoint = f"{self.settings.base_url}/chat/completions"
        last_error: InferenceError | None = None
        for attempt in range(self.settings.max_retries + 1):
            try:
                status, response_body = self._transport(endpoint, body, headers, self.settings.timeout_seconds)
                return _decode_response(status, response_body, purpose)
            except InferenceError as exc:
                last_error = exc
                if not exc.retryable or attempt >= self.settings.max_retries:
                    raise InferenceError(exc.code, _redact(str(exc)), retryable=exc.retryable) from None
                self._sleeper(self.settings.retry_backoff_seconds * (attempt + 1))
            except Exception:
                raise InferenceError("UNEXPECTED_PROVIDER_FAILURE", "The inference provider encountered an unexpected failure. Please retry later.") from None
        raise last_error or InferenceError("UNEXPECTED_PROVIDER_FAILURE", "The inference provider encountered an unexpected failure. Please retry later.")


class MockProvider:
    """Offline test provider; it never reads credentials or opens a network connection."""

    def __init__(self, settings: InferenceSettings) -> None:
        self.settings = settings

    def complete(
        self,
        messages: Sequence[Mapping[str, Any]],
        purpose: str,
        *,
        external_data_permitted: bool = False,
    ) -> InferenceResult:
        _validate_messages(messages)
        return InferenceResult(
            provider="mock",
            model="mock/deterministic-v2.2",
            content=self.settings.mock_response,
            purpose=purpose,
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        )


def build_provider(
    config_path: Path | None = None,
    environ: Mapping[str, str] | None = None,
    transport: Transport | None = None,
    sleeper: Sleeper | None = None,
) -> OpenRouterProvider | MockProvider:
    """Create the configured provider; callers can inject mock settings or transport in tests."""
    settings = load_settings(config_path=config_path, environ=environ)
    if settings.mode == "mock":
        return MockProvider(settings)
    return OpenRouterProvider(settings, environ=environ, transport=transport, sleeper=sleeper)


__all__ = [
    "DEFAULT_CONFIG_PATH",
    "InferenceError",
    "InferenceResult",
    "InferenceSettings",
    "MockProvider",
    "OpenRouterProvider",
    "build_provider",
    "load_settings",
]
