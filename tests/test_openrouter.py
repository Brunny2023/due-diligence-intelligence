import json
import os
import sys
import types
import unittest
from unittest.mock import patch

from app.analysis.grounded import (
    OPENROUTER_DEFAULT_BASE_URL,
    OPENROUTER_DEFAULT_MODEL,
    _openrouter_settings,
    reason_over_evidence,
)


class OpenRouterConfigurationTests(unittest.TestCase):
    def test_defaults_are_explicit(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}, clear=False):
            with patch.dict(os.environ, {"OPENROUTER_BASE_URL": "", "OPENROUTER_MODEL": ""}, clear=False):
                # Empty values are intentionally not treated as defaults by os.getenv.
                self.assertEqual(_openrouter_settings()[0], "test-key")
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}, clear=False):
            os.environ.pop("OPENROUTER_BASE_URL", None)
            os.environ.pop("OPENROUTER_MODEL", None)
            _, base_url, model = _openrouter_settings()
            self.assertEqual(base_url, OPENROUTER_DEFAULT_BASE_URL)
            self.assertEqual(model, OPENROUTER_DEFAULT_MODEL)

    def test_missing_key_fails_without_exposing_secret(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "OPENROUTER_API_KEY") as ctx:
                _openrouter_settings()
            self.assertNotIn("sk-", str(ctx.exception))

    def test_offline_mode_does_not_require_openrouter(self):
        with patch.dict(os.environ, {}, clear=True):
            answer = reason_over_evidence("What is the retention rate?", [])
            self.assertEqual(answer.provider, "offline-deterministic")
            self.assertEqual(answer.confidence, "Low")

    def test_openrouter_client_uses_base_url_model_and_safe_provider_label(self):
        calls = []

        class FakeCompletions:
            def create(self, **kwargs):
                calls.append(kwargs)
                return types.SimpleNamespace(
                    model="anthropic/claude-opus-5",
                    choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=json.dumps({
                        "finding": "Supported by E1.",
                        "confidence": "High",
                        "inference": "None.",
                        "missing_evidence": [],
                    })))]
                )

        class FakeClient:
            def __init__(self, **kwargs):
                self.kwargs = kwargs
                self.chat = types.SimpleNamespace(completions=FakeCompletions())

        fake_openai = types.SimpleNamespace(OpenAI=FakeClient)
        evidence = []
        with patch.dict(os.environ, {
            "OPENROUTER_API_KEY": "test-key",
            "OPENROUTER_BASE_URL": "https://openrouter.example/api/v1",
            "OPENROUTER_MODEL": "anthropic/claude-opus-5",
        }, clear=False):
            with patch.dict(sys.modules, {"openai": fake_openai}):
                answer = reason_over_evidence("Does the target have concentration risk?", evidence)

        self.assertEqual(answer.provider, "OpenRouter/anthropic/claude-opus-5")
        self.assertEqual(calls[0]["model"], "anthropic/claude-opus-5")
        self.assertEqual(calls[0]["response_format"], {"type": "json_object"})


if __name__ == "__main__":
    unittest.main()
