"""End-to-end ingestion → embedding → retrieval → grounded reasoning orchestration."""
import os
from pathlib import Path

from app.analysis.grounded import reason_over_evidence
from app.embeddings.providers import configured_provider
from app.ingestion.pipeline import ingest_case
from app.models import GroundedAnswer
from app.retrieval.index import LocalVectorIndex, PineconeVectorIndex


class RAGService:
    def __init__(self, case_path: Path) -> None:
        self.embedder = configured_provider()
        chunks = ingest_case(case_path)
        self.live = bool(os.getenv("PINECONE_API_KEY") and (os.getenv("PINECONE_INDEX") or os.getenv("PINECONE_HOST")))
        self.chunks = chunks
        if self.live:
            self.index = PineconeVectorIndex(self.embedder, namespace=os.getenv("PINECONE_NAMESPACE", "demo"))
            self.upserted_chunks = self.index.upsert(chunks)
        else:
            self.index = LocalVectorIndex(chunks, self.embedder)
            self.upserted_chunks = 0

    def query(self, question: str, top_k: int = 5) -> GroundedAnswer:
        evidence = self.index.query(question, top_k=top_k)
        answer = reason_over_evidence(question, evidence)
        return GroundedAnswer(answer.question, answer.finding, answer.confidence, answer.evidence, answer.missing_evidence, answer.inference, answer.provider, self.live)
