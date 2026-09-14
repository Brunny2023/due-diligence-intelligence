# Fictional V2 sample data

`northstar_acquisition.json` is a wholly fictional acquisition-target case. It deliberately includes an unresolved employee-count conflict across company-affiliated materials, unverified market-position and expansion claims, customer concentration, debt, a supplier-dependency signal, a regulatory remediation signal, incomplete IP assignment evidence, financial information with stated limits, opportunity hypotheses, and conditional scenarios. It does not refer to a real company, person, customer, supplier, regulator, or transaction.

The sample demonstrates V2 source-family treatment: the company website and pitch deck are one company-affiliated family and do not become independent corroboration merely by repeating a claim. It also demonstrates primary-support versus independent-corroboration distinctions, reconciliation-aware discrepancy handling, risk-linked evidence requests and management questions, decision-impact reasoning, conclusion-change conditions, external-research non-fabrication, and analytical scenarios that remain separate from facts.

From the package root, regenerate the sample with:

```bash
python3 scripts/validate_input.py sample/input/northstar_acquisition.json
python3 scripts/evidence_tracker.py sample/input/northstar_acquisition.json --output sample/output/evidence_analysis.json
python3 scripts/build_report.py sample/input/northstar_acquisition.json --output-dir sample/output --format all
python3 scripts/quality_check.py sample/output/business_due_diligence_report.md --output sample/output/quality_check.json
```
