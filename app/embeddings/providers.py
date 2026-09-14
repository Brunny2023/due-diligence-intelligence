"""Embedding interfaces: real OpenAI embeddings in live mode, deterministic vectors offline."""
import hashlib
import math
import os
from typing import Protocol


class EmbeddingProvider(Protocol):
    model: str
    dimension: int
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class HashEmbeddingProvider:
    """Deterministic local fallback; it is explicitly not a semantic model."""
    model = "sha256-feature-hash-offline"
    dimension = 256

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        for text in texts:
            vector = [0.0] * self.dimension
            tokens = text.lower().split()
            for token in tokens:
                digest = hashlib.sha256(token.encode()).digest()
                index = int.from_bytes(digest[:4], "big") % self.dimension
                vector[index] += 1.0
            norm = math.sqrt(sum(value * value for value in vector)) or 1.0
            vectors.append([value / norm for value in vector])
        return vectors


class OpenAIEmbeddingProvider:
    model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    dimension = int(os.getenv("EMBEDDING_DIMENSION", "1536"))

    def __init__(self, api_key: str | None = None) -> None:
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key or os.environ["LLM_API_KEY"])

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]


def configured_provider() -> EmbeddingProvider:
    if os.getenv("LLM_API_KEY"):
        return OpenAIEmbeddingProvider()
    return HashEmbeddingProvider()
