# Retrieval-Augmented Generation

## Problem

Ordinary prompting cannot reliably fit a growing diligence data room into context, preserve source provenance, or distinguish company claims from independently supported evidence. The existing analytical engine is evidence-calibrated; RAG makes relevant source material available to reasoning without replacing those controls.

## Pipeline

**Documents → ingestion → parsing/extraction → chunking → metadata → embeddings → Pinecone → semantic retrieval → evidence filtering → reasoning → structured diligence finding.**

`app/ingestion/pipeline.py` converts the synthetic Northstar JSON source register into 900-character chunks with 120-character overlap. Metadata includes document ID/name, type, page, section, source, date, evidence tier, and topic.

In the deployed configuration, `OpenRouterEmbeddingProvider` calls OpenRouter's OpenAI-compatible `/embeddings` endpoint using `OPENROUTER_EMBEDDING_MODEL` (validated as `openai/text-embedding-3-small`). `OPENROUTER_EMBEDDING_DIMENSION` is explicit and every observed response is validated at 1536 dimensions. Vectors are never padded, truncated, or reshaped. Direct OpenAI-compatible embeddings remain available through `LLM_API_KEY`, `EMBEDDING_MODEL`, and `EMBEDDING_DIMENSION` for backward compatibility.

Pinecone stores each chunk ID, vector, and metadata in the configured namespace. The validated deployment used index `northstar-ddi` and namespace `northstar-validation`. Query results retain similarity scores and source metadata. Without live credentials, the deterministic hash provider and local cosine index are used only as an explicitly labeled offline fallback.

## Grounding and reasoning

`build_context()` formats each result as `[E#] document | page | score` followed by the exact chunk text. When configured, the reasoning layer sends that context through OpenRouter using `OPENROUTER_BASE_URL`, `OPENROUTER_MODEL`, and `OPENROUTER_API_KEY`. The deployed reasoning model is `anthropic/claude-opus-5`. The prompt requires JSON, evidence labels, and a distinction between evidence, inference, uncertainty, and missing information.

The reasoning integration reached OpenRouter during final validation, but generation was blocked by an HTTP 402 caused by the available token/credit budget. No final Claude-generated diligence answer is claimed.

## Evidence quality

Semantic similarity helps discover candidate passages but does not equal evidentiary strength. In live validation for the Northstar revenue question, `website-2025` had the highest similarity while `audited-financials-2024` was the stronger direct source. The application retains evidence tiers and traceability so reviewers can evaluate source quality rather than accepting rank as truth.

## Failure modes

Relevant risks include irrelevant retrieval, insufficient evidence, conflicting evidence, missing or stale documents, provider failure, and hallucination. The UI exposes retrieved chunks and missing-evidence fields so a reviewer can inspect the boundary. There is no reranker or hybrid search yet.

## Validation status

Live OpenRouter embeddings and Pinecone retrieval have been validated in the deployed application. Startup upserted five synthetic chunks, and a live semantic query returned five traceable matches in `northstar-validation` with source metadata and similarity scores. Route validation confirmed public invalid requests return structured HTTP 400 responses. Final reasoning-provider reachability was observed, but the provider's HTTP 402 prevented capturing a final generated answer.
