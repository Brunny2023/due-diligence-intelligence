"""Retrieval backends: deterministic local search for offline demo and Pinecone for live mode."""
import math
import os
from typing import Any

from app.embeddings.providers import EmbeddingProvider
from app.models import DocumentChunk, RetrievedEvidence


def _cosine(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right)) / ((math.sqrt(sum(a*a for a in left)) or 1) * (math.sqrt(sum(b*b for b in right)) or 1))


class LocalVectorIndex:
    def __init__(self, chunks: list[DocumentChunk], embedder: EmbeddingProvider) -> None:
        self.chunks = chunks
        self.embedder = embedder
        self.vectors = embedder.embed([chunk.text for chunk in chunks])

    def query(self, question: str, top_k: int = 5, metadata_filter: dict[str, Any] | None = None) -> list[RetrievedEvidence]:
        query_vector = self.embedder.embed([question])[0]
        candidates = []
        for chunk, vector in zip(self.chunks, self.vectors):
            metadata = chunk.pinecone_metadata()
            if metadata_filter and any(metadata.get(key) != value for key, value in metadata_filter.items()):
                continue
            candidates.append((chunk, _cosine(query_vector, vector)))
        ranked = sorted(candidates, key=lambda item: item[1], reverse=True)[:top_k]
        return [RetrievedEvidence(chunk=chunk, score=score, rank=index + 1) for index, (chunk, score) in enumerate(ranked)]


class PineconeVectorIndex:
    """Thin adapter over the official Pinecone client; no local fake is used."""
    def __init__(self, embedder: EmbeddingProvider, index_name: str | None = None, host: str | None = None, namespace: str = "demo") -> None:
        from pinecone import Pinecone
        self.embedder = embedder
        self.namespace = namespace
        client = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
        self.index = client.Index(host=host) if host else client.Index(index_name or os.environ["PINECONE_INDEX"])

    def upsert(self, chunks: list[DocumentChunk], batch_size: int = 64) -> int:
        total = 0
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start:start + batch_size]
            vectors = self.embedder.embed([chunk.text for chunk in batch])
            self.index.upsert(vectors=[{"id": chunk.chunk_id, "values": vector, "metadata": chunk.pinecone_metadata()} for chunk, vector in zip(batch, vectors)], namespace=self.namespace)
            total += len(batch)
        return total

    def query(self, question: str, top_k: int = 5, metadata_filter: dict[str, Any] | None = None) -> list[RetrievedEvidence]:
        vector = self.embedder.embed([question])[0]
        response = self.index.query(vector=vector, top_k=top_k, include_metadata=True, namespace=self.namespace, filter=metadata_filter)
        results: list[RetrievedEvidence] = []
        matches = response.get("matches", []) if isinstance(response, dict) else getattr(response, "matches", [])
        for rank, match in enumerate(matches, 1):
            metadata = dict(match.get("metadata", {})) if isinstance(match, dict) else dict(getattr(match, "metadata", {}) or {})
            match_id = match.get("id") if isinstance(match, dict) else getattr(match, "id", "unknown")
            score = match.get("score", 0.0) if isinstance(match, dict) else getattr(match, "score", 0.0)
            chunk = DocumentChunk(chunk_id=str(match_id), text=str(metadata.pop("text", "")), document_id=str(metadata.pop("document_id", "unknown")), document_name=str(metadata.pop("document_name", "unknown")), document_type=str(metadata.pop("document_type", "evidence")), page_number=metadata.pop("page_number", None), section=metadata.pop("section", None), source=metadata.pop("source", None), date=metadata.pop("date", None), metadata=metadata)
            results.append(RetrievedEvidence(chunk=chunk, score=float(score), rank=rank))
        return results
