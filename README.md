# Due Diligence Intelligence

**Evidence-grounded Python due diligence analysis using retrieval-augmented generation.** This repository preserves the original standard-library due-diligence skill—claim verification, source independence, contradiction handling, evidence gaps, risk registers, and decision maps—and adds a transparent RAG engineering showcase around that logic.

## What this demonstrates

- **Document ingestion:** existing case JSON sources are parsed into traceable evidence chunks.
- **Chunking and metadata:** 900-character chunks with 120-character overlap retain document, source type, page, section, date, evidence tier, and topic metadata.
- **Embeddings:** live mode uses the configured OpenAI embedding model; offline mode uses a deterministic hash vector only as a clearly labeled test/demo fallback.
- **Vector retrieval:** live mode queries a real Pinecone index; offline mode performs deterministic cosine retrieval over the synthetic corpus.
- **Grounded reasoning:** retrieved chunks are assembled into a labeled context before optional LLM analysis. Findings expose evidence, inference, uncertainty, and missing evidence.
- **Existing domain analysis:** `scripts/evidence_tracker.py` remains the source of truth for evidence-calibrated due-diligence records and does not invent scores or conclusions.

## Demo

Run `python3 -m app.api.server` and open `http://localhost:8000/demo`. The UI is explicitly labeled offline when credentials are absent. Configure the variables in `.env.example` to enable live Pinecone retrieval and LLM reasoning; credentials remain server-side.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) and [RAG.md](RAG.md). The core path is **documents → ingestion → chunking → embeddings → Pinecone/local index → semantic retrieval → evidence context → reasoning → grounded finding**.

## Existing analysis workflow

The original implementation accepts structured JSON with a company, objective, source register, assertions, risks, opportunities, and evidence gaps. It produces Markdown/HTML due-diligence reports and deterministic validation. See [SKILL.md](SKILL.md), `scripts/`, and `sample/input/northstar_acquisition.json` (fictional).

## Local setup and tests

```bash
python3 -m venv .venv && . .venv/bin/activate
python3 -m unittest discover -s tests -v
python3 scripts/validate_input.py sample/input/northstar_acquisition.json
python3 scripts/evidence_tracker.py sample/input/northstar_acquisition.json --output /tmp/evidence.json
python3 -m app.api.server
```

Optional live providers are listed in `requirements-rag.txt`. Copy `.env.example` to `.env` and provide only your own server-side credentials. No credentials or proprietary customer data belong in this repository.

## Validation status

The offline pipeline is validated by the local test suite and the public demo smoke test. The live Pinecone path is implemented, including synthetic-corpus upsert and query, but is **NOT TESTED** in the current environment because Pinecone credentials and the SDK were unavailable. Do not interpret the implementation as proof of a live external-service run.

## Limitations and honesty boundary

The checked-in demo dataset is synthetic. Offline mode is not semantic model inference and is not presented as Pinecone. Live Pinecone/LLM execution requires credentials and an index configured by the operator. Retrieval quality is not benchmarked here; reranking, hybrid search, and a larger labeled evaluation set remain future improvements. This is an analytical aid, not legal, financial, investment, tax, accounting, or regulatory advice.

## Origin

The repository originated as a Capafy-native due-diligence skill. The showcase preserves that provenance and makes the engineering boundary independently understandable; it does not claim that the original implementation contained the added RAG adapters.
