# Architecture

The original deterministic due-diligence analysis remains separate from the new retrieval and reasoning layers.

```mermaid
flowchart TD
  A[Demo UI / API] --> B[RAGService]
  B --> C[Case JSON ingestion]
  C --> D[Chunking + traceable metadata]
  D --> E[EmbeddingProvider]
  E --> F{Index backend}
  F -->|live credentials| G[Pinecone vector index]
  F -->|no credentials| H[Offline local cosine index]
  G --> I[RetrievedEvidence]
  H --> I
  I --> J[Evidence context builder]
  J --> K{Reasoning provider}
  K -->|LLM_API_KEY| L[LLM JSON analysis]
  K -->|offline| M[Deterministic bounded synthesis]
  L --> N[GroundedAnswer]
  M --> N
  N --> A
  C -. separate domain workflow .-> O[scripts/evidence_tracker.py]
```

Pinecone is queried only when `PINECONE_API_KEY` and `PINECONE_INDEX` or `PINECONE_HOST` are set. The browser never receives credentials. `GroundedAnswer.evidence` is populated from returned chunks, preserving source and page metadata.
