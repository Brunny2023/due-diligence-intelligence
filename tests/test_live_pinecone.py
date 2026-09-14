import os
import unittest
from pathlib import Path

from app.embeddings.providers import configured_provider
from app.ingestion.pipeline import ingest_case
from app.retrieval.index import PineconeVectorIndex


LIVE = bool(os.getenv("PINECONE_API_KEY") and (os.getenv("PINECONE_INDEX") or os.getenv("PINECONE_HOST")) and os.getenv("LLM_API_KEY"))


@unittest.skipUnless(LIVE, "requires PINECONE_API_KEY, PINECONE_INDEX or PINECONE_HOST, and LLM_API_KEY")
class LivePineconeTests(unittest.TestCase):
    """Uses only the checked-in synthetic case and the configured test namespace."""

    @classmethod
    def setUpClass(cls):
        cls.embedder = configured_provider()
        cls.chunks = ingest_case(Path("sample/input/northstar_acquisition.json"))
        cls.index = PineconeVectorIndex(cls.embedder, namespace=os.getenv("PINECONE_NAMESPACE", "validation"))
        cls.index.upsert(cls.chunks)

    def test_real_query_returns_score_and_source_metadata(self):
        results = self.index.query("Does the target have a material customer concentration risk?", top_k=3)
        self.assertTrue(results)
        self.assertTrue(all(result.score >= 0 for result in results))
        self.assertTrue(any("customer" in result.chunk.text.lower() for result in results))
        self.assertTrue(all(result.chunk.document_id for result in results))

    def test_metadata_filter_changes_query_scope(self):
        results = self.index.query("financial risk", top_k=5, metadata_filter={"document_type": "audited_financial_statement"})
        self.assertTrue(results)
        self.assertTrue(all(result.chunk.document_type == "audited_financial_statement" for result in results))


if __name__ == "__main__":
    unittest.main()
