# Deployment

The showcase is a small Python HTTP service and can run on any host that supports Python 3.10+. Start it with `python3 -m app.api.server`; it binds to `0.0.0.0:8000` and exposes `/health`, `/api/query`, and `/demo`. `Dockerfile` and `fly.toml` provide a Fly.io deployment definition using the existing application without changing its architecture. Fly deployment and live Pinecone/LLM validation remain **NOT TESTED** until Fly authentication and production provider configuration are available.

For live mode, inject environment variables from a secret manager. Do not place keys in HTML, JavaScript, Git history, or `.env.example`. Keep Pinecone and LLM calls server-side. The checked-in synthetic case is safe for demonstration; do not upload confidential diligence materials.

The public demo is currently **offline validated** and reports `offline-demo` from `/health`. Live Pinecone deployment is implemented but **NOT TESTED** in this environment because Pinecone credentials and the SDK were unavailable. Configure a dedicated validation namespace before enabling live mode; do not point it at an unrelated production index.

Lizard secrets must be configured server-side with the exact variables expected by the current code: `PINECONE_API_KEY`, `PINECONE_INDEX` or `PINECONE_HOST`, `PINECONE_NAMESPACE`, `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, `OPENROUTER_MODEL`, `OPENROUTER_EMBEDDING_MODEL`, and `OPENROUTER_EMBEDDING_DIMENSION`. OpenRouter is used for both embeddings and LLM reasoning through its OpenAI-compatible API; the intended reasoning model is `anthropic/claude-opus-5`. Direct OpenAI-compatible embedding variables remain supported for backward compatibility but are not required when OpenRouter embedding variables are configured. The embedding provider refuses to upsert vectors when their observed dimension differs from the configured dimension. No credential belongs in the repository or frontend.

For Cloudflare static hosting, see [CLOUDFLARE.md](CLOUDFLARE.md). The included `wrangler.jsonc` deploys the browser demo shell from `public/`; the Python RAG API must run separately on a Python-capable backend.
