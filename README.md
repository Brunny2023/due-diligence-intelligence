# Business Due Diligence & Acquisition Intelligence — Rebased Final

This package is an evidence-calibrated business due-diligence Skill for imperfect company information. **V2.1 is the authoritative analytical foundation.** It preserves the full evidence-to-decision methodology: claim taxonomy, source independence, verification, contradiction/reconciliation treatment, confidence calibration, risk and opportunity registers, evidence requests, management questions, the Diligence Decision Map, scenario analysis, transaction impacts, qualitative evidence-calibrated assessments, structured executive findings, and deterministic quality gates.

The Skill is deliberately **LLM-agnostic**. The host environment may make an LLM available for contextual interpretation and synthesis, but the package does not implement a provider adapter, select a model, store or request a credential, hard-code an endpoint, make a network call, operate a backend, count requests, or manage billing or subscriptions.

## Architecture

```text
Host environment
  ↓
Business Due Diligence & Acquisition Intelligence Skill
  ↓
Host-provided LLM for contextual interpretation and synthesis, when available
  ↓
V2.1 evidence and decision-intelligence methodology
  ↓
Deterministic validation and quality gates
  ↓
Final diligence output
```

The package is designed for **Run on Demand**. It creates no polling, scheduled inference, background worker, persistent model process, idle resource use, persistent server, payment flow, subscription management, or separate request-entitlement mechanism. One substantive investigation is one user request; internal reasoning, document processing, evidence tracking, validation, and report assembly are not independently counted by the Skill.

## Package components

| Component | Purpose |
| --- | --- |
| `SKILL.md` | Operating instructions, evidence boundaries, Run-on-Demand limits, and host-provided LLM role. |
| `scripts/validate_input.py` | Offline input and untrusted-content validation. |
| `scripts/evidence_tracker.py` | Offline claim/evidence, discrepancy, decision-map, and assessment generation. |
| `scripts/build_report.py` | Offline Markdown/HTML report assembly. |
| `scripts/quality_check.py` | Evidence, quality, status-consistency, and output-boundary checks. |
| `scripts/security_scan.py` | Static scan for hard-coded credentials and network-capable deterministic helpers. |
| `config/config.json` | Non-secret metadata for the host-native, Run-on-Demand package. |
| `V2.1_V2.2_FINAL_CHANGE_AUDIT.md` | Full V2.1 → V2.2 → final disposition of significant V2.2 changes. |

## Local validation workflow

```bash
cd /home/ubuntu/skills/business-due-diligence-intelligence
python3 scripts/validate_input.py sample/input/northstar_acquisition.json
python3 scripts/evidence_tracker.py sample/input/northstar_acquisition.json --output sample/output/evidence_analysis.json
python3 scripts/build_report.py sample/input/northstar_acquisition.json --output-dir sample/output --format all
python3 scripts/quality_check.py sample/output/business_due_diligence_report.md --output sample/output/quality_check.json
python3 scripts/security_scan.py --output sample/output/security_scan.json
python3 -m unittest discover -s tests -v
```

The Northstar case is wholly fictional. The Skill is an analytical aid, not legal, financial, investment, tax, accounting, or regulatory advice. It must not be used as a final transaction, investment, contracting, or professional conclusion.

## Host-runtime and publication setup

The live platform controls any model, provider, credential, retention, training, data-processing, pricing, and native request-limit configuration. The package contains no API key, provider credential, endpoint, or model identifier and has no mechanism for such values. Before publication, complete the live listing’s required support, category/tag, delivery, commercial, data-handling, test-case, and review fields. See `CAPAFY_COMPLIANCE_CHECKLIST.md`, `DATA_SHARING_DECLARATION.md`, `LLM_PROVIDER_DISCLOSURE.md`, and `PUBLISHING_RECOMMENDATIONS.md`.
