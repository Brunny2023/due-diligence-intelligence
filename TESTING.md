# Testing

The original suite covers evidence claims, discrepancy reconciliation, decision maps, report quality, and security boundaries. Added RAG tests cover chunk overlap, metadata preservation, deterministic retrieval relevance, evidence-context propagation, missing-evidence behavior, and provider separation.

Tests are offline and do not require paid APIs or Pinecone credentials:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q app scripts tests
python3 scripts/security_scan.py --output /tmp/security_scan.json
python3 scripts/quality_check.py sample/output/business_due_diligence_report.md --output /tmp/quality.json
```

Live integration is intentionally separate: provide `PINECONE_API_KEY`, `PINECONE_INDEX` or `PINECONE_HOST`, and the embedding provider configuration, then run the demo and inspect `/health`. No live result or evaluation score is committed.
