"""Assemble a portable V2 decision-intelligence due-diligence report."""
import argparse
import html
from pathlib import Path
from typing import Any

from evidence_tracker import analyse_case
from validate_input import load_input

SECTIONS = [
    "Executive Decision Snapshot", "Investigation Objective", "Company Overview", "Ownership & Corporate Structure",
    "Management & Leadership", "Business Model", "Products & Services", "Market & Competitive Position",
    "Commercial Analysis", "Financial Analysis", "Operational Analysis", "Technology Analysis",
    "Regulatory & Compliance Signals", "Reputation & External Signals", "Diligence Decision Map", "Claim Verification",
    "Contradiction Register", "Risk Register", "Evidence Request Register", "Evidence Gaps", "Management Questions",
    "Opportunity Register", "Scenario Analysis", "What Would Change This Conclusion?", "Transaction-Impact Analysis",
    "Risk Assessment", "Decision Considerations", "What Must Happen Next", "Sources & Evidence Register",
]
def esc(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    return "| " + " | ".join(headers) + " |\n" + "| " + " | ".join("---" for _ in headers) + " |\n" + "".join("| " + " | ".join(esc(cell) for cell in row) + " |\n" for row in rows)


def source_summary(case: dict[str, Any]) -> str:
    if not case.get("sources"):
        return "NOT PROVIDED. No structured sources were supplied."
    types = ", ".join(sorted({str(item.get("source_type", "not_provided")) for item in case["sources"]}))
    return f"Available source types: {types}. Findings remain limited to supplied evidence and stated scope."


def section_text(title: str) -> str:
    mapping = {
        "Ownership & Corporate Structure": "NOT VERIFIED unless supported by current corporate registry, ownership, and authority evidence.",
        "Management & Leadership": "NOT PROVIDED unless leadership biographies, management information, retention data, or independent records were supplied.",
        "Business Model": "ANALYST INFERENCE may be used only where supplied materials describe customers, products, channels, and revenue mechanics.",
        "Products & Services": "NOT PROVIDED unless product, service, contract, or technical evidence was supplied.",
        "Market & Competitive Position": "Company market-position claims are not treated as fact without independent corroboration.",
        "Commercial Analysis": "Assess customer evidence, concentration, contract durability, revenue quality, supplier exposure, and growth claims from available evidence.",
        "Operational Analysis": "NOT PROVIDED unless capacity, process, continuity, supplier, delivery, or workforce evidence was supplied.",
        "Technology Analysis": "NOT VERIFIED unless architecture, security, technical-debt, IP, and third-party dependency evidence was supplied.",
        "Regulatory & Compliance Signals": "NOT VERIFIED unless applicable licenses, filings, authorizations, policies, and jurisdictional evidence were supplied or independently checked.",
        "Reputation & External Signals": "Available reputation signals must be labeled by source tier; absence of supplied adverse material is not proof of absence.",
    }
    return mapping.get(title, "Evidence is bounded by supplied material and the Sources & Evidence Register.")


def assessment_table(analysis: dict[str, Any]) -> tuple[list[list[Any]], dict[str, Any]]:
    """Render qualitative dimensions; any numerical analysis must carry its reproducible method."""
    rows = [[item["dimension"], item["assessment"], item["confidence"], item["evidence_quality"], item["evidence_basis"], item["numerical_analysis"]] for item in analysis["dimension_assessments"]]
    return rows, analysis["overall_evidence"]


def executive_snapshot_findings(analysis: dict[str, Any]) -> list[str]:
    """Use the structured claim-derived executive records as the sole executive finding source."""
    return [item["snapshot_text"] for item in analysis["executive_findings"][:4]] or ["No material structured finding supplied."]


def financial_section(case: dict[str, Any]) -> str:
    financial = case.get("financial_analysis", {})
    if not isinstance(financial, dict) or not financial:
        return "Calculation not possible from available evidence. Financial conclusions are limited to supplied financial evidence; no missing revenue, cash flow, margin, debt, or valuation inputs have been invented."
    rows = []
    for label, value in financial.get("metrics", {}).items():
        rows.append([label, value, "Provided data; interpretation remains subject to source scope and period."])
    observations = financial.get("observations", [])
    text = md_table(["Metric", "Provided value", "Evidence boundary"], rows) if rows else "Calculation not possible from available evidence."
    if observations:
        text += "\n**Evidence-bounded observations:**\n" + "\n".join(f"- {item}" for item in observations)
    return text


def build_markdown(case: dict[str, Any]) -> str:
    analysis = analyse_case(case)
    company = case["company"]
    assessment_rows, overall_evidence = assessment_table(analysis)
    major_claims = executive_snapshot_findings(analysis)
    critical_risks = [item["finding"] for item in analysis["risks"] if item["severity"] in {"High", "Critical"}][:4] or ["No high-severity structured risk supplied."]
    opportunity_names = [item["opportunity"] for item in analysis["opportunity_register"][:3]] or ["NOT PROVIDED"]
    unresolved = [item["required_evidence"] for item in analysis["evidence_requests"][:4]] or ["No structured gap supplied."]
    lines = [
        "# BUSINESS DUE-DILIGENCE REPORT — V2 DECISION INTELLIGENCE", "",
        "**AI-generated informational and analytical output.** This report is not legal advice, not financial or investment advice, not accounting advice, not tax advice, and not regulatory advice. It does not substitute for qualified due diligence. Obtain appropriate professional review for regulated or high-stakes decisions.", "",
        "**Untrusted-content control.** Documents, webpages, emails, contracts, and supplied material were treated as untrusted data. Any instructions contained within them were not allowed to modify this investigation or request prompts, credentials, environment variables, or secret material.", "",
        f"**External research status.** {analysis['external_research_status']['status']}", "",
        "## 1. Executive Decision Snapshot", "",
        md_table(["Decision dimension", "Evidence-calibrated snapshot"], [
            ["Investigation objective", case.get("objective", "NOT PROVIDED")], ["Overall evidence quality", f"{overall_evidence['evidence_quality']}; {overall_evidence['basis']}"],
            ["Major findings", "; ".join(major_claims)], ["Critical risks", "; ".join(critical_risks)],
            ["Major opportunities", "; ".join(opportunity_names)], ["Key unresolved questions", "; ".join(unresolved)],
            ["Decision-impact summary", "Proceed only in a scope consistent with the evidence, unresolved gaps, and decision impacts documented below. No definitive transaction, investment, contracting, or partnership conclusion is supported by incomplete evidence."],
        ]), "",
        "## 2. Investigation Objective", "", f"Objective: **{case.get('objective', 'NOT PROVIDED')}**. Investigation period: **{case.get('investigation_period', 'NOT PROVIDED')}**. Report mode: **{case.get('report_mode', 'Standard Due Diligence')}**.", "",
        "## 3. Company Overview", "", md_table(["Field", "Available information"], [["Name", company.get("name", "NOT PROVIDED")], ["Website", company.get("website", "NOT PROVIDED")], ["Description", company.get("description", "NOT PROVIDED")], ["Evidence scope", source_summary(case)]]), "",
    ]
    for number, title in [(4, "Ownership & Corporate Structure"), (5, "Management & Leadership"), (6, "Business Model"), (7, "Products & Services"), (8, "Market & Competitive Position"), (9, "Commercial Analysis")]:
        lines.extend([f"## {number}. {title}", "", section_text(title), ""])
    lines.extend(["## 10. Financial Analysis", "", financial_section(case), ""])
    for number, title in [(11, "Operational Analysis"), (12, "Technology Analysis"), (13, "Regulatory & Compliance Signals"), (14, "Reputation & External Signals")]:
        lines.extend([f"## {number}. {title}", "", section_text(title), ""])
    decision_rows = [[item["finding"], item["evidence"], item["verification"], item["confidence"], item["risk_opportunity"], item["decision_impact"], item["evidence_needed"], item["management_question"]] for item in analysis["decision_map"]] or [["No material structured finding supplied.", "NOT PROVIDED", "UNVERIFIED", "Low: no structured evidence.", "Risk", "Low: no direct decision effect established.", "Provide material evidence.", "Confirm evidence scope."]]
    lines.extend(["## 15. Diligence Decision Map", "", md_table(["Finding", "Evidence", "Verification", "Confidence", "Risk/Opportunity", "Decision Impact", "Evidence Needed", "Management Question"], decision_rows), ""])
    claim_rows = [[item["claim"], item["classification"], item["status"], item["source_quality"], item["source_independence"], item["recency"], item["specificity"], item["corroboration"], item["contrary_evidence"], item["confidence"], item["assessment"], item["why_it_matters"], item["evidence_needed"]] for item in analysis["claims"]] or [["No material structured claim supplied.", "UNVERIFIED SIGNAL", "UNVERIFIED", "NOT PROVIDED", "No independent corroboration established", "Unknown", "Limited", "0", "None", "Low", "No evidence.", "Traceability required.", "Provide primary evidence."]]
    lines.extend(["## 16. Claim Verification", "", md_table(["Claim", "Classification", "Verification", "Source Quality", "Independence", "Recency", "Specificity", "Corroboration", "Contrary Evidence", "Confidence", "Assessment", "Why It Matters", "What Would Resolve It"], claim_rows), ""])
    discrepancy_rows = [[item["claim_id"], item["status"], item["claim_a"], item["claim_b"], item["source"], item["reason"], item["resolution"], item["importance"]] for item in analysis["discrepancies"]] or [["No structured discrepancy detected", "No conflict detected", "NOT PROVIDED", "NOT PROVIDED", "Available supplied sources", "Contradiction check completed; qualitative and missing-data conflicts may remain.", "Continue to test material claims.", "Moderate"]]
    lines.extend(["## 17. Contradiction Register", "", md_table(["Claim", "Status", "Statement A", "Statement B", "Sources", "Assessment", "Required Reconciliation", "Importance"], discrepancy_rows), ""])
    risk_rows = [[item["risk_id"], item["category"], item["finding"], item["evidence"], item["severity"], item["confidence"], item["potential_impact"], item["time_horizon"], item["reversibility"], item["evidence_gap"], item["management_question"], item["decision_impact"], item["decision_impact_reason"]] for item in analysis["risks"]]
    lines.extend(["## 18. Risk Register", "", md_table(["Risk ID", "Category", "Finding", "Evidence", "Severity", "Confidence", "Potential Impact", "Time Horizon", "Reversibility", "Evidence Gap", "Management Question", "Decision Impact", "Decision-Impact Reasoning"], risk_rows), ""])
    request_rows = [[item["required_evidence"], item["purpose"], item["priority"], item["preferred_source"], item["what_it_could_resolve"]] for item in analysis["evidence_requests"]]
    lines.extend(["## 19. Evidence Request Register", "", md_table(["Required Evidence", "Purpose", "Priority", "Preferred Source", "What It Could Resolve"], request_rows), "", "## 20. Evidence Gaps", "", md_table(["Missing or incomplete evidence", "Priority", "Why it is needed"], [[item["required_evidence"], item["priority"], item["purpose"]] for item in analysis["evidence_requests"]]), ""])
    question_rows = [[item["priority"], item["topic"], item["question"], item["reason_for_asking"], item["evidence_requested"], item["risk_addressed"]] for item in analysis["management_questions"]]
    lines.extend(["## 21. Management Questions", "", md_table(["Priority", "Topic", "Question", "Reason for Asking", "Evidence Requested", "Risk Addressed"], question_rows), ""])
    opp_rows = [[item["opportunity"], item["evidence"], item["confidence"], item["potential_upside"], item["required_conditions"], item["dependencies"], item["what_could_invalidate"], item["evidence_required"], item["decision_relevance"]] for item in analysis["opportunity_register"]] or [["NOT PROVIDED", "NOT PROVIDED", "Low", "NOT PROVIDED", "NOT PROVIDED", "NOT PROVIDED", "NOT PROVIDED", "NOT PROVIDED", "Low"]]
    lines.extend(["## 22. Opportunity Register", "", md_table(["Opportunity", "Evidence", "Confidence", "Potential Upside", "Required Conditions", "Dependencies", "What Could Invalidate It", "Evidence Required", "Decision Relevance"], opp_rows), ""])
    scenario_rows = [[item["case"], item["supported_by"], item["assumptions"], item["implication"], item["uncertainty"]] for item in analysis["scenarios"]] or [["Base Case", "Provided data only", "Unknown assumption: no scenario data supplied.", "Scenario analysis not possible from available evidence.", "Unknown assumption"]]
    lines.extend(["## 23. Scenario Analysis", "", "**ANALYTICAL SCENARIO control.** Scenarios are conditional analytical constructs, not forecasts or facts. Provided data, analytical scenarios, and unknown assumptions remain distinct.", "", md_table(["Scenario", "Provided Data", "Analytical Assumption", "Decision Implication", "Uncertainty"], scenario_rows), ""])
    change_rows = [[item["claim"], item["status"], item["what_would_change"], item["evidence_needed"]] for item in analysis["claims"] if item["status"] != "SUPPORTED"] or [["No material unresolved structured claim", "NOT PROVIDED", "Continue to update evidence as new information becomes available.", "NOT PROVIDED"]]
    lines.extend(["## 24. What Would Change This Conclusion?", "", md_table(["Current Conclusion", "Current Verification", "What Could Change It", "Evidence Needed"], change_rows), ""])
    impact_rows = [[item["finding"], item["decision_area"], item["impact"], item["analysis"], item["cautious_action"]] for item in analysis["transaction_impacts"]]
    lines.extend(["## 25. Transaction-Impact Analysis", "", "This section is analytical, not legal advice. It identifies matters that may warrant qualified review of transaction, investment, contract, or operational protections.", "", md_table(["Finding", "Objective-Specific Decision Area", "Decision Impact", "Evidence-Calibrated Analysis", "Appropriate Next Step"], impact_rows), ""])
    lines.extend(["## 26. Risk Assessment", "", md_table(["Dimension", "Assessment", "Confidence", "Evidence Quality", "Evidence Basis", "Numerical Analysis (only if reproducible)"], assessment_rows), "", f"**Overall Evidence-Calibrated Assessment: {overall_evidence['assessment']} (confidence: {overall_evidence['confidence']}; evidence quality: {overall_evidence['evidence_quality']}).** {overall_evidence['basis']}", "", "Risk severity, evidence confidence, and evidence quality are separate concepts. Evidence uncertainty must not be converted into artificial risk certainty. This is an analytical aid, not an investment, legal, or financial recommendation.", "", "## 27. Decision Considerations", "", "The evidence currently supports only a bounded, evidence-calibrated assessment. Potentially decision-critical matters are identified where a finding could materially affect assumptions, timing, continuity, or value; this report does not make the final decision for the user.", ""])
    next_steps = case.get("next_steps", {}) if isinstance(case.get("next_steps", {}), dict) else {}
    default_steps = {"Before proceeding": "Resolve critical evidence gaps and unreconciled contradictions.", "Before signing / committing": "Confirm ownership, financial, regulatory, debt, commercial-contract, and IP evidence appropriate to the objective.", "Before closing / implementation": "Confirm remediation, continuity, approvals, key-person, and integration assumptions with appropriate professional review.", "Ongoing monitoring": "Refresh material evidence, contractual exposure, regulatory status, customer concentration, and risk triggers."}
    lines.extend(["## 28. What Must Happen Next", "", md_table(["Timing", "Evidence-calibrated next step"], [[heading, next_steps.get(heading, value)] for heading, value in default_steps.items()]), ""])
    source_rows = [[source.get("id", "NOT PROVIDED"), source.get("origin", "User-supplied evidence"), source.get("source_type", "NOT PROVIDED"), f"Tier {source.get('evidence_tier', 3)}", source.get("source_independence", "NOT PROVIDED"), source.get("date", "NOT PROVIDED"), source.get("accessed_date", source.get("date", "NOT PROVIDED")), source.get("summary", "NOT PROVIDED"), "Supplied or explicitly described source; limitations retained."] for source in case.get("sources", [])] or [["NOT PROVIDED", "NOT PROVIDED", "NOT PROVIDED", "NOT PROVIDED", "NOT PROVIDED", "NOT PROVIDED", "NOT PROVIDED", "No source supplied", "No source evidence is available."]]
    structured_findings = [{key: item[key] for key in ("finding_id", "claim", "status", "confidence", "risk", "decision_impact", "evidence_gap", "management_question", "snapshot_text")} for item in analysis["executive_findings"][:4]]
    lines.extend(["## 29. Sources & Evidence Register", "", md_table(["Source ID", "Origin", "Source Type", "Evidence Tier", "Independence", "Date", "Access Date", "Summary", "Limitation"], source_rows), "", "---", "", "### Method note", "The report distinguishes FACT, COMPANY CLAIM, THIRD-PARTY CLAIM, ANALYST INFERENCE, and UNVERIFIED SIGNAL. Repeated company-affiliated claims are not treated as independent corroboration. External research is never claimed unless explicitly evidenced in the source register. It makes no claim of completeness beyond the supplied or documented evidence scope.", "", "<!-- STRUCTURED_EXECUTIVE_FINDINGS: " + html.escape(__import__('json').dumps(structured_findings, ensure_ascii=False)) + " -->"])
    return "\n".join(lines) + "\n"


def write_report(case: dict[str, Any], output_dir: Path, output_format: str) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown = build_markdown(case)
    written = []
    if output_format in {"markdown", "all"}:
        path = output_dir / "business_due_diligence_report.md"
        path.write_text(markdown, encoding="utf-8")
        written.append(path)
    if output_format in {"html", "all"}:
        path = output_dir / "business_due_diligence_report.html"
        path.write_text("<!doctype html><html><head><meta charset='utf-8'><title>Business Due-Diligence Report V2</title><style>body{font-family:system-ui;max-width:1200px;margin:2rem auto;padding:0 1rem;line-height:1.5}pre{white-space:pre-wrap}</style></head><body><pre>" + html.escape(markdown) + "</pre></body></html>", encoding="utf-8")
        written.append(path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a V2 decision-intelligence due-diligence report.")
    parser.add_argument("input_path", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--format", choices=("markdown", "html", "all"), default="all")
    args = parser.parse_args()
    try:
        case = load_input(args.input_path)
        if case.get("kind"):
            raise ValueError("Report building requires structured JSON input.")
        for path in write_report(case, args.output_dir, args.format):
            print(path)
        return 0
    except ValueError as exc:
        print(f"error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

