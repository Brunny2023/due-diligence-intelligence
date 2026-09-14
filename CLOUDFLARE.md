# Cloudflare deployment

This repository contains a Python HTTP/RAG backend and a browser demo page. Cloudflare Workers static assets can host the demo page, but they do not execute `app/api/server.py` or the Python Pinecone/LLM integrations.

The repository includes `wrangler.jsonc` and `public/index.html` so the frontend can be deployed with:

```bash
npx wrangler deploy
```

The Wrangler configuration points at `./public/`, which resolves the error `Could not detect a directory containing static files`. The static deployment serves the UI at `/`. The UI's `/api/query` requests require the Python backend to be deployed separately on a Python-capable service. For a complete live demo, configure the frontend API origin to that backend and set `PINECONE_API_KEY`, `PINECONE_INDEX` or `PINECONE_HOST`, and provider credentials only in the backend's server-side secrets.

Do not add Pinecone or LLM keys to Cloudflare static asset files, browser code, GitHub, or `.env.example`. The checked-in demo corpus is synthetic and safe for public asset hosting.

The Cloudflare static deployment should be described as a **frontend/demo shell deployment**, not as proof that the Python RAG backend or live Pinecone path runs inside Cloudflare Workers.
