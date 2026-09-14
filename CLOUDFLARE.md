# Cloudflare deployment

This repository contains a Python HTTP/RAG backend and a browser demo page. Cloudflare Workers static assets can host the demo page, but they do not execute `app/api/server.py` or the Python Pinecone/LLM integrations.

The repository includes `wrangler.jsonc` and `public/index.html` so the frontend can be deployed with:

```bash
npx wrangler deploy
```

The Wrangler configuration points at `./public/`, which resolves the error `Could not detect a directory containing static files`. The static deployment serves the UI at `/`. The UI reads an optional browser-safe `window.DD_API_BASE` value; set it to the Python backend's public HTTPS origin in the deployed frontend. The UI then calls `<DD_API_BASE>/health` to show `LIVE RAG` only when the backend reports live Pinecone mode, and calls `<DD_API_BASE>/api/query` for analysis. The Python backend must be deployed separately on a Python-capable service. Set `PINECONE_API_KEY`, `PINECONE_INDEX` or `PINECONE_HOST`, and provider credentials only in the backend's server-side secrets.

Do not add Pinecone or LLM keys to Cloudflare static asset files, browser code, GitHub, or `.env.example`. The checked-in demo corpus is synthetic and safe for public asset hosting.

The Cloudflare static deployment should be described as a **frontend/demo shell deployment**, not as proof that the Python RAG backend or live Pinecone path runs inside Cloudflare Workers.
