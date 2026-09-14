"""Embedding interfaces for OpenRouter, direct OpenAI-compatible APIs, and offline tests."""
import hashlib
import math
import os
from typing import Protocol


OPENROUTER_DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_DEFAULT_MODEL = "openai/text-embedding-3-small"


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
    """Backward-compatible direct OpenAI-compatible embedding provider."""

    model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    dimension = int(os.getenv("EMBEDDING_DIMENSION", "1536"))

    def __init__(self, api_key: str | None = None) -> None:
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key or os.environ["LLM_API_KEY"])

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.model, input=texts)
        vectors = [item.embedding for item in response.data]
        _validate_dimensions(vectors, self.dimension, self.model)
        return vectors


class OpenRouterEmbeddingProvider:
    """OpenRouter embeddings via its OpenAI-compatible /embeddings endpoint."""

    def __init__(self, api_key: str | None = None) -> None:
        from openai import OpenAI

        self.model = os.getenv("OPENROUTER_EMBEDDING_MODEL", OPENROUTER_DEFAULT_MODEL)
        self.dimension = int(os.getenv("OPENROUTER_EMBEDDING_DIMENSION", "1536"))
        self.base_url = os.getenv("OPENROUTER_BASE_URL", OPENROUTER_DEFAULT_BASE_URL)
        key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        if not key:
            raise RuntimeError("OPENROUTER_API_KEY is required for OpenRouter embeddings")
        self.client = OpenAI(api_key=key, base_url=self.base_url)

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.model, input=texts)
        vectors = [item.embedding for item in response.data]
        _validate_dimensions(vectors, self.dimension, self.model)
        return vectors


def _validate_dimensions(vectors: list[list[float]], expected: int, model: str) -> None:
    observed = {len(vector) for vector in vectors}
    if observed != {expected}:
        raise ValueError(
            f"Embedding dimension mismatch for {model}: observed {sorted(observed)}, expected {expected}; refusing to alter vectors"
        )


def configured_provider() -> EmbeddingProvider:
    if os.getenv("OPENROUTER_API_KEY"):
        return OpenRouterEmbeddingProvider()
    if os.getenv("LLM_API_KEY"):
        return OpenAIEmbeddingProvider()
    return HashEmbeddingProvider()
