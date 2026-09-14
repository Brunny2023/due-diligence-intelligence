"""Typed contracts shared by ingestion, retrieval, and grounding layers."""
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    text: str
    document_id: str
    document_name: str
    document_type: str
    page_number: int | None = None
    section: str | None = None
    source: str | None = None
    date: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def pinecone_metadata(self) -> dict[str, Any]:
        data = {
            "document_id": self.document_id,
            "document_name": self.document_name,
            "document_type": self.document_type,
            "section": self.section or "",
            "source": self.source or self.document_name,
            "text": self.text,
        }
        if self.page_number is not None:
            data["page_number"] = self.page_number
        if self.date:
            data["date"] = self.date
        data.update(self.metadata)
        return data


@dataclass(frozen=True)
class RetrievedEvidence:
    chunk: DocumentChunk
    score: float
    rank: int


@dataclass(frozen=True)
class GroundedAnswer:
    question: str
    finding: str
    confidence: str
    evidence: list[RetrievedEvidence]
    missing_evidence: list[str]
    inference: str
    provider: str
    live_retrieval: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "finding": self.finding,
            "confidence": self.confidence,
            "evidence": [
                {"rank": e.rank, "score": e.score, **e.chunk.pinecone_metadata()}
                for e in self.evidence
            ],
            "missing_evidence": self.missing_evidence,
            "inference": self.inference,
            "provider": self.provider,
            "live_retrieval": self.live_retrieval,
        }
