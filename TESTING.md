# Testing

The original suite covers evidence claims, discrepancy reconciliation, decision maps, report quality, and security boundaries. Added RAG tests cover chunk overlap, metadata preservation, deterministic retrieval relevance, evidence-context propagation, missing-evidence behavior, and provider separation.

Tests are offline and do not require paid APIs or Pinecone credentials:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q app scripts tests
python3 scripts/security_scan.py --output /tmp/security_scan.json
python3 scripts/quality_check.py sample/output/business_due_diligence_report.md --output /tmp/quality.json
```

Live integration is intentionally separate: `tests/test_live_pinecone.py` uses only the synthetic case and skips unless `PINECONE_API_KEY`, `PINECONE_INDEX` or `PINECONE_HOST`, and `LLM_API_KEY` are available. In this validation environment those variables and the Pinecone SDK were absent, so the live test status is **NOT TESTED**. No live result or evaluation score is committed.

**Offline validated:** 25 tests pass, including chunking, metadata, deterministic retrieval, context construction, source mapping, grounding, and insufficient-evidence behavior. **Live validated:** none in this environment.
