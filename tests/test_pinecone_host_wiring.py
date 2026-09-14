import os
import unittest
from pathlib import Path
from unittest.mock import patch

from app.rag import RAGService


class PineconeHostWiringTests(unittest.TestCase):
    def test_configured_host_is_passed_and_index_fallback_is_not_used(self):
        captured = {}

        class FakeEmbedder:
            model = "test"
            dimension = 1536

        class FakeIndex:
            def __init__(self, embedder, index_name=None, host=None, namespace="demo"):
                captured.update(index_name=index_name, host=host, namespace=namespace)

            def upsert(self, chunks):
                return len(chunks)

        env = {
            "PINECONE_API_KEY": "test-key",
            "PINECONE_HOST": "https://example.pinecone.io",
            "PINECONE_NAMESPACE": "northstar-validation",
        }
        with patch.dict(os.environ, env, clear=True):
            with patch("app.rag.configured_provider", return_value=FakeEmbedder()):
                with patch("app.rag.PineconeVectorIndex", FakeIndex):
                    RAGService(Path("sample/input/northstar_acquisition.json"))

        self.assertEqual(captured["host"], "https://example.pinecone.io")
        self.assertIsNone(captured["index_name"])
        self.assertEqual(captured["namespace"], "northstar-validation")


if __name__ == "__main__":
    unittest.main()
