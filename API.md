# API

The optional dependency-free demo server is `python3 -m app.api.server`.

| Method | Route | Input | Output | Auth | Errors |
|---|---|---|---|---|---|
| GET | `/demo` | none | HTML demo UI | none | 404 for unknown route |
| GET | `/health` | none | `{ok, retrieval_mode}` | none | 404 for unknown route |
| POST | `/api/query` | JSON `{question: string, top_k?: integer}` | Grounded answer, evidence, scores, provider, and `live_retrieval` | none for demo; provider credentials remain server-side | 400 for invalid/missing question; 500 for provider failure |

`top_k` is clamped to 1–10. Returned evidence contains actual chunk text and source metadata. The endpoint does not claim Pinecone was queried when offline mode is active.

When called from the production frontend, the Python service permits the exact origin `https://ddi.maindev20.workers.dev` and handles `OPTIONS` preflight. Other browser origins are not granted CORS access. The response never contains provider credentials.
