import os
import sys
import types
import unittest
from unittest.mock import patch

from app.embeddings.providers import (
    OPENROUTER_DEFAULT_BASE_URL,
    OPENROUTER_DEFAULT_MODEL,
    OpenRouterEmbeddingProvider,
    configured_provider,
)


class OpenRouterEmbeddingTests(unittest.TestCase):
    def test_missing_openrouter_key_fails_safely(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "OPENROUTER_API_KEY"):
                OpenRouterEmbeddingProvider()

    def test_explicit_base_url_model_and_observed_dimension(self):
        captured = {}

        class FakeEmbeddings:
            def create(self, **kwargs):
                captured.update(kwargs)
                return types.SimpleNamespace(data=[types.SimpleNamespace(embedding=[0.0] * 1536)])

        class FakeClient:
            def __init__(self, **kwargs):
                captured["client"] = kwargs
                self.embeddings = FakeEmbeddings()

        with patch.dict(os.environ, {
            "OPENROUTER_API_KEY": "test-key",
            "OPENROUTER_BASE_URL": OPENROUTER_DEFAULT_BASE_URL,
            "OPENROUTER_EMBEDDING_MODEL": OPENROUTER_DEFAULT_MODEL,
            "OPENROUTER_EMBEDDING_DIMENSION": "1536",
        }, clear=True):
            with patch.dict(sys.modules, {"openai": types.SimpleNamespace(OpenAI=FakeClient)}):
                provider = OpenRouterEmbeddingProvider()
                vectors = provider.embed(["synthetic Northstar evidence"])

        self.assertEqual(len(vectors[0]), 1536)
        self.assertEqual(captured["client"]["base_url"], OPENROUTER_DEFAULT_BASE_URL)
        self.assertEqual(captured["client"]["api_key"], "test-key")
        self.assertEqual(captured["model"], OPENROUTER_DEFAULT_MODEL)

    def test_dimension_mismatch_is_rejected_without_reshaping(self):
        class FakeEmbeddings:
            def create(self, **kwargs):
                return types.SimpleNamespace(data=[types.SimpleNamespace(embedding=[0.0] * 4)])

        class FakeClient:
            def __init__(self, **kwargs):
                self.embeddings = FakeEmbeddings()

        with patch.dict(os.environ, {
            "OPENROUTER_API_KEY": "test-key",
            "OPENROUTER_EMBEDDING_DIMENSION": "1536",
        }, clear=True):
            with patch.dict(sys.modules, {"openai": types.SimpleNamespace(OpenAI=FakeClient)}):
                provider = OpenRouterEmbeddingProvider()
                with self.assertRaisesRegex(ValueError, "dimension mismatch"):
                    provider.embed(["test"])

    def test_configured_provider_selects_openrouter_before_direct_provider(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}, clear=True):
            provider = configured_provider()
            self.assertIsInstance(provider, OpenRouterEmbeddingProvider)

    def test_offline_fallback_remains_available(self):
        with patch.dict(os.environ, {}, clear=True):
            provider = configured_provider()
            self.assertEqual(provider.model, "sha256-feature-hash-offline")


if __name__ == "__main__":
    unittest.main()
