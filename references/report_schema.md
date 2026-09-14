# V2.1 Report and Portable JSON Schema

## Required report sections

Use this order: Executive Decision Snapshot; Investigation Objective; Company Overview; Ownership & Corporate Structure; Management & Leadership; Business Model; Products & Services; Market & Competitive Position; Commercial Analysis; Financial Analysis; Operational Analysis; Technology Analysis; Regulatory & Compliance Signals; Reputation & External Signals; Diligence Decision Map; Claim Verification; Contradiction Register; Risk Register; Evidence Request Register; Evidence Gaps; Management Questions; Opportunity Register; Scenario Analysis; What Would Change This Conclusion?; Transaction-Impact Analysis; Risk Assessment; Decision Considerations; What Must Happen Next; Sources & Evidence Register.

Every report must open with the AI-generated professional disclaimer, untrusted-content control, and external-research status. Use Markdown as the primary portable output. HTML is supplementary.

## Minimal V2.1 JSON input

```json
{
  "company": {"name": "Example Co.", "website": "https://example.invalid", "description": "Optional"},
  "objective": "Acquisition Target",
  "report_mode": "Deep Due Diligence",
  "investigation_period": "FY2024–FY2025",
  "sources": [],
  "risks": [],
  "opportunities": [],
  "external_research": {"performed": false}
}
```

## Source and assertion format

```json
{
  "id": "source-1",
  "origin": "User-supplied evidence",
  "source_type": "audited_financial_statement",
  "evidence_tier": 1,
  "source_family": "audited-financial-records",
  "source_independence": "Primary company record; not independent",
  "date": "2025-03-31",
  "accessed_date": "2025-03-31",
  "summary": "Fictional source summary.",
  "assertions": [{
    "claim_id": "fy2024_revenue",
    "claim": "Revenue for FY2024 was US$26m.",
    "value": "26000000 USD",
    "classification": "FACT",
    "period": "FY2024",
    "definition": "Recognized revenue",
    "scope": "Target entity",
    "geography": "Global",
    "accounting_treatment": "Audited financial statements",
    "specificity": "High"
  }]
}
```

`source_family` is essential where the same underlying claim appears on a website, pitch deck, executive profile, or copied press coverage. These may be a single company-affiliated family, not independent corroboration. Set `origin` to `User-supplied evidence` or `Independently researched evidence`. If the latter is used, provide date/access detail and never overstate research scope.

## Structured finding and executive summary

Material claims are normalized into a structured finding before the report is rendered. Detailed Claim Verification, the Diligence Decision Map, and the Executive Decision Snapshot must preserve the same `status`, `confidence`, evidence limitations, decision impact, evidence gap, and management question.

```json
{
  "finding_id": "employee_count",
  "claim": "Employee count reported in company materials.",
  "status": "CONTRADICTED",
  "confidence": "Low",
  "evidence": ["company-website", "company-presentation"],
  "risk": "Risk",
  "decision_impact": "Moderate",
  "evidence_gap": "Dated payroll or HR records reconciled to legal-entity scope.",
  "management_question": "Please reconcile the employee-count reports using current payroll records.",
  "snapshot_text": "Employee count is conflicting and NOT VERIFIED."
}
```

A snapshot must never convert `UNVERIFIED`, `CONTRADICTED`, `PARTIALLY SUPPORTED`, or `APPARENT DISCREPANCY — REQUIRES RECONCILIATION` into an unqualified fact. The renderer includes a machine-readable marker to allow deterministic consistency checks.

## Evidence-calibrated risk assessment

The Risk Assessment section includes `Dimension`, `Assessment`, `Confidence`, `Evidence Quality`, `Evidence Basis`, and `Numerical Analysis (only if reproducible)`. Permitted qualitative assessments are **Strong**, **Adequate**, **Mixed**, **Weak**, **Insufficient Evidence**, and **Not Assessed**. Evidence quality is **High**, **Medium**, **Low**, or **Insufficient**.

Numerical analysis is optional. When supplied, every dimension must document a score, scale, inputs, methodology, confidence, and limitations. When this method package is not complete, the renderer must state that no reproducible score was supplied rather than manufacture a default number.

## Risk format

```json
{
  "risk_id": "R-01",
  "category": "Commercial",
  "finding": "Top customer represents 38% of revenue.",
  "evidence": "audited-financials-2024",
  "evidence_basis": "Audited financial schedule for FY2024; current renewal evidence is incomplete.",
  "severity": "High",
  "severity_rationale": "The concentration could materially affect revenue durability.",
  "confidence": "High",
  "confidence_rationale": "The percentage is supported by Tier 1 financial evidence.",
  "potential_impact": "Revenue volatility and valuation sensitivity.",
  "time_horizon": "Near-term",
  "reversibility": "Difficult to reverse",
  "evidence_gap": "Customer contract, renewal history, and 24-month trend.",
  "management_question": "Provide top-customer revenue, contract, renewal, and retention schedules.",
  "decision_impact": "Material",
  "decision_impact_reason": "The concentration may affect revenue durability and valuation assumptions."
}
```

## Opportunity and scenario formats

```json
{
  "opportunity": "Recurring maintenance software cross-sell may expand customer value.",
  "evidence": "product-roadmap-2025; customer-demand-notes",
  "confidence": "Medium",
  "potential_upside": "Higher recurring revenue and retention.",
  "required_conditions": "Customer adoption and product integration.",
  "dependencies": "Product execution and sales capacity.",
  "what_could_invalidate": "Low adoption or unsupported demand claim.",
  "evidence_required": "Cohort retention, bookings, and contract data.",
  "decision_relevance": "Moderate"
}
```

```json
{
  "case": "Base Case",
  "supported_by": "Provided FY2024 audited revenue and concentration data.",
  "assumptions": "ANALYTICAL SCENARIO: largest-customer revenue remains stable through the next renewal cycle.",
  "implication": "Commercial concentration remains a material diligence focus.",
  "uncertainty": "Unknown assumption: renewal and pipeline evidence are incomplete."
}
```

Never present scenarios as facts or fabricate forecasts.
