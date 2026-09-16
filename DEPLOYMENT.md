# Deployment

The active deployment is a split architecture:

- **Frontend:** Cloudflare Worker `ddi` serves the static browser shell.
- **API:** Lizard service `due-diligence-intelligence` in `us-east-1` runs the Python service.
- **Runtime:** Python standard-library `ThreadingHTTPServer`.
- **Port:** `8000`, bound to `0.0.0.0`.
- **Startup command:** `python3 -m app.api.server`.
- **Public API:** `https://crew-trumpet-thv1.us-east-1.onlizard.com`.

The Python service must run separately from the static Cloudflare frontend. The frontend may point to the API with the browser-safe `window.DD_API_BASE` value. Provider credentials remain in Lizard server-side secrets.

## Live configuration names

The current code recognizes these names:

```text
PINECONE_API_KEY
PINECONE_INDEX
PINECONE_HOST
PINECONE_NAMESPACE
LLM_API_KEY
EMBEDDING_MODEL
EMBEDDING_DIMENSION
OPENROUTER_API_KEY
OPENROUTER_BASE_URL
OPENROUTER_MODEL
OPENROUTER_EMBEDDING_MODEL
OPENROUTER_EMBEDDING_DIMENSION
```

`PINECONE_INDEX` or `PINECONE_HOST` is required for live Pinecone selection, together with `PINECONE_API_KEY`. In the validated deployment, Pinecone used index `northstar-ddi` and namespace `northstar-validation`. OpenRouter embedding configuration used `openai/text-embedding-3-small` with dimension `1536`; reasoning used `anthropic/claude-opus-5`. The direct OpenAI-compatible embedding variables remain supported for backward compatibility.

Do not put values for these variables in Git, Dockerfiles, frontend JavaScript, issue reports, or documentation. Configure secrets through the hosting platform's secret manager.

## Validation record

The deployed process reached stable health, startup indexing completed with five synthetic chunks, live OpenRouter embeddings returned 1536-dimensional vectors, and live Pinecone retrieval returned traceable matches in `northstar-validation`. The reasoning route reached OpenRouter during validation, but final generation was blocked by an upstream HTTP 402 caused by the available token/credit budget. No additional reasoning request is part of this documentation update.

## Cloudflare boundary

See [CLOUDFLARE.md](CLOUDFLARE.md) for the static frontend configuration. Cloudflare does not replace the Python API runtime and must not contain Pinecone or OpenRouter credentials.

## Data boundary

The checked-in Northstar case is synthetic. Do not upload confidential data to the public demonstration deployment or commit private diligence materials.

## Historical files

`Dockerfile`, `fly.toml`, and older reports may describe earlier packaging or validation phases. Fly.io and Render are not the active hosting targets documented here.
