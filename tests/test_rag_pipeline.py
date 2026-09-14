import json
import tempfile
import unittest
from pathlib import Path

from app.analysis.grounded import build_context, reason_over_evidence
from app.embeddings.providers import HashEmbeddingProvider
from app.ingestion.pipeline import ingest_case, ingest_text
from app.retrieval.index import LocalVectorIndex


class RagPipelineTests(unittest.TestCase):
    def setUp(self):
        self.case = Path('sample/input/northstar_acquisition.json')

    def test_ingestion_preserves_source_metadata(self):
        chunks = ingest_case(self.case)
        self.assertTrue(chunks)
        concentration = [c for c in chunks if '38%' in c.text]
        self.assertTrue(concentration)
        self.assertIn('evidence_tier', concentration[0].pinecone_metadata())
        self.assertEqual(concentration[0].document_type, 'audited_financial_statement')

    def test_chunking_uses_overlap(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'doc.txt'
            path.write_text('word ' * 500, encoding='utf-8')
            chunks = ingest_text(path)
            self.assertGreater(len(chunks), 1)
            self.assertTrue(set(chunks[0].text.split()[-10:]) & set(chunks[1].text.split()[:20]))

    def test_retrieval_returns_customer_evidence(self):
        chunks = ingest_case(self.case)
        results = LocalVectorIndex(chunks, HashEmbeddingProvider()).query('customer concentration revenue largest customer', top_k=5)
        self.assertTrue(any('38%' in item.chunk.text for item in results))
        self.assertEqual([item.rank for item in results], list(range(1, len(results) + 1)))

    def test_context_contains_retrieved_text_and_citation_labels(self):
        chunks = ingest_case(self.case)
        results = LocalVectorIndex(chunks, HashEmbeddingProvider()).query('customer concentration', top_k=2)
        context = build_context(results)
        self.assertIn('[E1]', context)
        self.assertIn(results[0].chunk.text, context)

    def test_missing_evidence_does_not_claim_certainty(self):
        answer = reason_over_evidence('What is the retention rate?', [])
        self.assertEqual(answer.confidence, 'Low')
        self.assertIn('Insufficient', answer.finding)
        self.assertFalse(answer.live_retrieval)


if __name__ == '__main__':
    unittest.main()
