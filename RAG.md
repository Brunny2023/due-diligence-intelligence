# Retrieval-Augmented Generation

## Problem

Ordinary prompting cannot reliably fit a growing diligence data room into context, preserve source provenance, or distinguish company claims from independently supported evidence. The existing analytical engine is deliberately evidence-calibrated; RAG makes the relevant source material available to reasoning without replacing those controls.

## Pipeline

**Document → chunk → embed → index → retrieve → context → reason → grounded finding.** `app/ingestion/pipeline.py` converts the existing JSON source register into chunks. Chunk size is 900 characters with 120-character overlap: large enough to keep an assertion and its summary together, while overlap reduces boundary loss. Metadata includes document ID/name, type, page, section, source, date, evidence tier, and topic.

Live embeddings use `EMBEDDING_MODEL` (default `text-embedding-3-small`) through the OpenAI-compatible client. The configured dimension defaults to 1536. Pinecone upsert stores each chunk ID, vector, and metadata in the configured namespace (`demo` by default). Query embeds the question and calls Pinecone with configurable `top_k` and optional metadata filters. Results retain similarity scores. The offline provider is a deterministic hash vector for reproducible tests and is explicitly labeled as non-semantic fallback behavior.

## Grounding and reasoning

`build_context()` formats each result as `[E#] document | page | score` followed by the exact chunk. The optional LLM prompt requires JSON, evidence labels, and a distinction between evidence, inference, uncertainty, and missing information. Without an LLM key, the demo returns a bounded deterministic synthesis rather than pretending a model was called.

## Failure modes

Irrelevant retrieval, insufficient evidence, conflicting evidence, missing or stale documents, provider failure, and hallucination risk remain possible. The UI shows the retrieved chunks and missing-evidence list so a reviewer can inspect the boundary. There is no reranker or hybrid search yet; those are future improvements alongside a larger labeled Recall@K benchmark.
