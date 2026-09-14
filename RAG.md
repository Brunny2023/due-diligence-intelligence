# Retrieval-Augmented Generation

## Problem

Ordinary prompting cannot reliably fit a growing diligence data room into context, preserve source provenance, or distinguish company claims from independently supported evidence. The existing analytical engine is deliberately evidence-calibrated; RAG makes the relevant source material available to reasoning without replacing those controls.

## Pipeline

**Document → chunk → embed → index → retrieve → context → reason → grounded finding.** `app/ingestion/pipeline.py` converts the existing JSON source register into chunks. Chunk size is 900 characters with 120-character overlap: large enough to keep an assertion and its summary together, while overlap reduces boundary loss. Metadata includes document ID/name, type, page, section, source, date, evidence tier, and topic.

Live embeddings use `OPENROUTER_EMBEDDING_MODEL` (default `openai/text-embedding-3-small`) through OpenRouter's OpenAI-compatible `/embeddings` endpoint when `OPENROUTER_API_KEY` is configured. The expected dimension is explicit in `OPENROUTER_EMBEDDING_DIMENSION` and is validated against every observed response; vectors are never padded, truncated, or reshaped. Direct OpenAI-compatible embeddings remain available through `LLM_API_KEY`, `EMBEDDING_MODEL`, and `EMBEDDING_DIMENSION` for backward compatibility. Pinecone upsert stores each chunk ID, vector, and metadata in the configured namespace (`demo` by default). Query embeds the question and calls Pinecone with configurable `top_k` and optional metadata filters. Results retain similarity scores. The offline provider is a deterministic hash vector for reproducible tests and is explicitly labeled as non-semantic fallback behavior.

## Grounding and reasoning

`build_context()` formats each result as `[E#] document | page | score` followed by the exact chunk. When configured, the reasoning layer sends that context through OpenRouter's OpenAI-compatible API using `OPENROUTER_BASE_URL` and `OPENROUTER_MODEL` (default `anthropic/claude-opus-5`) with `OPENROUTER_API_KEY` held server-side. The prompt requires JSON, evidence labels, and a distinction between evidence, inference, uncertainty, and missing information. Without an OpenRouter key, the demo returns a bounded deterministic synthesis rather than pretending a model was called; it does not silently fall back to direct OpenAI reasoning.

## Failure modes

Irrelevant retrieval, insufficient evidence, conflicting evidence, missing or stale documents, provider failure, and hallucination risk remain possible. The UI shows the retrieved chunks and missing-evidence list so a reviewer can inspect the boundary. There is no reranker or hybrid search yet; those are future improvements alongside a larger labeled Recall@K benchmark.

## Validation status

**Implemented:** ingestion, chunking, metadata enrichment, configurable embeddings, Pinecone upsert/query, metadata filtering, evidence context construction, optional LLM reasoning, source mapping, and deterministic offline fallback. **Offline validated:** the synthetic corpus, retrieval path, context construction, grounding behavior, and insufficient-evidence behavior pass the local test suite. **Live Pinecone validated:** **NOT TESTED** in the current environment because Pinecone credentials and the SDK were unavailable. The repository therefore makes no claim that a real Pinecone index was queried in this validation pass.
