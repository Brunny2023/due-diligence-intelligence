"""Run deterministic V2.1 due-diligence report quality gates without network access."""
import argparse
import html
import json
import re
from pathlib import Path

REQUIRED_SECTIONS = [
    "Executive Decision Snapshot", "Investigation Objective", "Company Overview", "Ownership & Corporate Structure",
    "Management & Leadership", "Business Model", "Products & Services", "Market & Competitive Position",
    "Commercial Analysis", "Financial Analysis", "Operational Analysis", "Technology Analysis",
    "Regulatory & Compliance Signals", "Reputation & External Signals", "Diligence Decision Map", "Claim Verification",
    "Contradiction Register", "Risk Register", "Evidence Request Register", "Evidence Gaps", "Management Questions",
    "Opportunity Register", "Scenario Analysis", "What Would Change This Conclusion?", "Transaction-Impact Analysis",
    "Risk Assessment", "Decision Considerations", "What Must Happen Next", "Sources & Evidence Register",
]
PROHIBITED_CERTAINTY = [r"\byou should acquire\b", r"\bdefinitely a good investment\b", r"\bguaranteed(?:ly)?\b", r"\brisk[- ]free\b", r"\bdemand this warranty\b"]
SECRET_PATTERNS = [r"(?i)sk-[a-z0-9]{16,}", r"(?i)api[_-]?key\s*[:=]\s*['\"]?[a-z0-9_\-]{12,}", r"(?i)aws_secret_access_key\s*[:=]"]
UNRESOLVED_STATUSES = {"UNVERIFIED", "CONTRADICTED", "PARTIALLY SUPPORTED", "APPARENT DISCREPANCY — REQUIRES RECONCILIATION"}


def executive_block(text: str) -> str:
    start = text.find("## 1. Executive Decision Snapshot")
    end = text.find("## 2. Investigation Objective")
    return text[start:end] if start >= 0 and end > start else ""


def structured_executive_findings(text: str) -> list[dict]:
    marker = re.search(r"<!-- STRUCTURED_EXECUTIVE_FINDINGS: (.*?) -->", text, flags=re.DOTALL)
    if not marker:
        raise ValueError("Structured executive findings marker is missing.")
    payload = html.unescape(marker.group(1))
    findings = json.loads(payload)
    if not isinstance(findings, list):
        raise ValueError("Structured executive findings must be a list.")
    return findings


def check_executive_consistency(text: str, failures: list[str]) -> None:
    snapshot = executive_block(text)
    try:
        findings = structured_executive_findings(text)
    except (ValueError, json.JSONDecodeError) as exc:
        failures.append(f"Executive-summary consistency control unavailable: {exc}")
        return
    for finding in findings:
        status = str(finding.get("status", ""))
        summary = str(finding.get("snapshot_text", ""))
        claim = str(finding.get("claim", "material finding"))
        if not summary or summary not in snapshot:
            failures.append(f"Executive snapshot is not generated from the structured finding for: {claim}")
        if status in UNRESOLVED_STATUSES:
            required = "PARTIALLY SUPPORTED" if status == "PARTIALLY SUPPORTED" else "NOT VERIFIED"
            if required not in summary and status not in summary:
                failures.append(f"Executive snapshot upgrades uncertainty for: {claim}")


def check_risk_assessment(text: str, failures: list[str]) -> None:
    start = text.find("## 26. Risk Assessment")
    end = text.find("## 27. Decision Considerations")
    section = text[start:end] if start >= 0 and end > start else ""
    for label in ("Assessment", "Confidence", "Evidence Quality", "Evidence Basis", "Numerical Analysis (only if reproducible)"):
        if label not in section:
            failures.append(f"Risk assessment is missing V2.1 evidence-calibrated field: {label}")
    for line in section.splitlines():
        if re.search(r"\|\s*[^|]+\s*\|\s*\d+/(?:10|100)\s*\|", line) and "methodology:" not in line.lower():
            failures.append("Arbitrary numerical score detected without a reproducible methodology.")
    if "Evidence uncertainty must not be converted into artificial risk certainty" not in section:
        failures.append("Risk assessment does not preserve the uncertainty-versus-severity boundary.")


def check_report(text: str) -> dict:
    failures, warnings = [], []
    for section in REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"Missing required section: {section}")
    for label in ("NOT VERIFIED", "NOT PROVIDED", "ANALYST INFERENCE", "COMPANY CLAIM", "UNVERIFIED"):
        if label not in text:
            failures.append(f"Missing required evidence-status label: {label}")
    if "AI-generated" not in text or "not legal" not in text.lower() or "not financial" not in text.lower():
        failures.append("Missing required professional disclaimer.")
    check_risk_assessment(text, failures)
    check_executive_consistency(text, failures)
    if "Contradiction check completed" not in text and "CONFLICTING EVIDENCE" not in text and "REQUIRES RECONCILIATION" not in text:
        failures.append("Contradictions were not visibly checked.")
    if "Sources & Evidence Register" not in text or "Evidence Tier" not in text:
        failures.append("Traceable evidence register is missing.")
    if "Source Quality" not in text or "Independence" not in text or "Corroboration" not in text:
        failures.append("Material evidence attributes or source independence are missing.")
    if "Decision Impact" not in text or "Decision-Impact Reasoning" not in text:
        failures.append("Decision impacts lack visible reasoning.")
    if "Priority" not in text or "Preferred Source" not in text or "What It Could Resolve" not in text:
        failures.append("Evidence request priority or resolution logic is missing.")
    if "Reason for Asking" not in text or "Risk Addressed" not in text:
        failures.append("Management questions are not visibly linked to risks and evidence needs.")
    if "ANALYTICAL SCENARIO control" not in text or "Unknown assumption" not in text:
        failures.append("Scenario assumptions are not visibly separated from facts.")
    if "External research status" not in text:
        failures.append("External research status is not disclosed.")
    if "Untrusted-content control" not in text or "not allowed to modify this investigation" not in text:
        failures.append("Prompt-injection control is not visibly preserved.")
    for pattern in PROHIBITED_CERTAINTY:
        if re.search(pattern, text, flags=re.IGNORECASE):
            failures.append(f"Unsupported certainty detected: {pattern}")
    for pattern in SECRET_PATTERNS:
        if re.search(pattern, text):
            failures.append("Potential secret material detected.")
    if len(text) < 3500:
        warnings.append("Report is unusually short for V2.1; confirm the selected mode and evidence scope are appropriate.")
    return {"passed": not failures, "failures": failures, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description="Check a V2.1 Markdown due-diligence report.")
    parser.add_argument("report_path", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = {"passed": False, "failures": [f"Report does not exist: {args.report_path}"], "warnings": []} if not args.report_path.exists() else check_report(args.report_path.read_text(encoding="utf-8"))
    payload = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
