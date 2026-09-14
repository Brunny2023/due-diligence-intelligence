# Business Due Diligence & Acquisition Intelligence — Rebased Final

V2.1 is the authoritative analytical foundation. This Skill turns imperfect company evidence into reproducible decision intelligence: claim verification, source independence, reconciliation-aware discrepancies, calibrated confidence, risk and opportunity registers, evidence requests, management questions, Diligence Decision Maps, scenarios, transaction impacts, qualitative assessments, and deterministic quality gates.

The host environment may supply an LLM for contextual interpretation and synthesis. This package is **LLM-agnostic** and does not implement provider selection, API authentication, credential storage, endpoints, model routing, billing, subscription management, entitlement counting, background execution, polling, scheduling, or a persistent backend.

## Components

| Component | Purpose |
| --- | --- |
| `SKILL.md` | Evidence methodology, untrusted-content controls, host-LLM boundary, and Run-on-Demand rules. |
| `scripts/validate_input.py` | Offline input and untrusted-content validation. |
| `scripts/evidence_tracker.py` | Claims, evidence, reconciliation, decision outputs, and qualitative assessments. |
| `scripts/build_report.py` | Markdown and standalone HTML report assembly. |
| `scripts/quality_check.py` | Evidence, disclosure, status-consistency, and report-quality checks. |
| `scripts/security_scan.py` | Static credential and deterministic-helper network-boundary scan. |
| `config/config.json` | Non-secret package metadata and host-native runtime boundary. |
| `V2.1_V2.2_FINAL_CHANGE_AUDIT.md` | Disposition of every significant V2.2 change. |

## Local validation

```bash
python3 -m compileall -q scripts tests
python3 -m unittest discover -s tests -v
python3 scripts/validate_input.py sample/input/northstar_acquisition.json
python3 scripts/evidence_tracker.py sample/input/northstar_acquisition.json --output sample/output/evidence_analysis.json
python3 scripts/build_report.py sample/input/northstar_acquisition.json --output-dir sample/output --format all
python3 scripts/quality_check.py sample/output/business_due_diligence_report.md --output sample/output/quality_check.json
python3 scripts/security_scan.py --output sample/output/security_scan.json
```

The sample is fictional. The Skill is an AI-generated analytical aid, not legal, financial, investment, tax, accounting, or regulatory advice. It is designed for Run on Demand; one substantive investigation is one user request, and internal reasoning and deterministic processing are not separately counted by the Skill.

Live model, provider, credential, data-processing, pricing, and platform request-limit settings are host-managed. Complete the platform’s live support, category, delivery, commercial, disclosure, test-case, and review fields before publication. No platform approval is claimed.
