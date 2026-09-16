# Testing and Validation

The repository combines deterministic unit tests with separately recorded live integration validation. The checked-in tests do not require paid APIs or Pinecone credentials.

## Local checks

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q app scripts tests
python3 scripts/security_scan.py --output /tmp/security_scan.json
python3 scripts/quality_check.py sample/output/business_due_diligence_report.md --output /tmp/quality.json
git diff --check
```

The suite covers evidence claims, source independence, discrepancy handling, decision maps, report quality, chunk overlap, metadata preservation, deterministic retrieval, provider selection, OpenRouter embedding routing, dimension enforcement, Pinecone host wiring, evidence-context propagation, missing-evidence behavior, route validation, and security boundaries.

## Live validation record

The deployed service was validated without adding another corpus write or replacing the architecture:

| Check | Result |
|---|---|
| Lizard process and `/health` | HTTP 200 |
| OpenRouter embedding route | Live request succeeded |
| Returned embedding dimension | 1536 |
| Pinecone index | `northstar-ddi` |
| Pinecone namespace | `northstar-validation` |
| Startup upsert | 5 synthetic chunks |
| Semantic retrieval | Live query returned 5 matches |
| Metadata mapping | Source, page, section, evidence tier, topic, and score traceable |
| Invalid public query | Structured HTTP 400 |
| Reasoning provider reachability | OpenRouter request reached the configured Claude Opus 5 route |
| Final reasoning generation | Not captured; OpenRouter returned HTTP 402 due to available token/credit budget |

Live OpenRouter embeddings and Pinecone retrieval have been validated in the deployed application. No final Claude-generated diligence answer is claimed from the last reasoning validation.

## Security checks

Before committing, search for secret-like material without printing values:

```bash
rg -n -i 'api[_-]?key|token|authorization|bearer|secret|password|sk-' --glob '!*.pyc' --glob '!.git/**' .
```

Review any match in context. The public repository must contain synthetic Northstar data only, and `.env.example` must contain variable names and placeholders rather than credential values.

## Offline boundary

When live credentials are absent, the application uses a deterministic hash embedding provider and local cosine retrieval. The UI and `/health` response label this `offline-demo`; it is a reproducible testing fallback, not semantic model inference or proof of Pinecone connectivity.
