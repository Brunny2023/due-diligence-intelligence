"""Build evidence, verification, decision-intelligence, and diligence follow-up records."""
import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from validate_input import load_input

TIER_NAMES = {
    1: "Primary evidence",
    2: "Strong independent secondary evidence",
    3: "Supporting evidence",
    4: "Weak/unverified signal",
}
COMPANY_AFFILIATED_TYPES = {
    "company_website", "company_presentation", "company_linkedin", "management_information",
    "company_press_release", "company_marketing", "investor_presentation",
}
GAP_LIBRARY = {
    "audited financial statements": {
        "source_types": {"audited_financial_statement", "financial_statement"},
        "priority": "Critical", "purpose": "Assess revenue quality, profitability, cash generation, working capital, and financial position.",
        "preferred_source": "Audited financial statements and supporting schedules.",
        "resolution": "Whether reported financial performance and liabilities are reliable and decision-useful.",
        "topic": "Financial quality", "risk": "Financial quality / valuation sensitivity",
    },
    "ownership and corporate records": {
        "source_types": {"government_record", "corporate_registry", "company_filing"},
        "priority": "Critical", "purpose": "Confirm legal entity, ownership, authority, and corporate structure.",
        "preferred_source": "Current corporate registry extracts, cap table, and constitutional records.",
        "resolution": "Whether ownership, control, and transaction authority are understood.",
        "topic": "Ownership and structure", "risk": "Corporate transparency / control risk",
    },
    "customer concentration data": {
        "source_types": {"customer_concentration", "financial_statement"},
        "priority": "Critical", "purpose": "Measure revenue dependency, customer concentration, and concentration trend.",
        "preferred_source": "Management accounting schedule tied to audited financial records.",
        "resolution": "Whether concentration risk is temporary, structural, or mitigated by durable contracts.",
        "topic": "Customer concentration", "risk": "Commercial concentration / revenue durability",
    },
    "major customer and supplier contracts": {
        "source_types": {"signed_contract", "contract"},
        "priority": "Critical", "purpose": "Assess renewal, termination, pricing, volume, exclusivity, and assignment exposure.",
        "preferred_source": "Executed contracts and amendment schedules.",
        "resolution": "Whether material commercial dependencies are contractually durable.",
        "topic": "Commercial contracts", "risk": "Revenue durability / supplier continuity",
    },
    "regulatory licenses or authorizations": {
        "source_types": {"regulatory_filing", "license"},
        "priority": "Critical", "purpose": "Confirm required approvals, regulatory standing, and renewal obligations.",
        "preferred_source": "Regulator-issued license records and compliance correspondence.",
        "resolution": "Whether operations depend on missing, restricted, or contingent authorizations.",
        "topic": "Regulatory status", "risk": "Regulatory exposure",
    },
    "debt schedule": {
        "source_types": {"debt_schedule", "financial_statement"},
        "priority": "Critical", "purpose": "Identify debt, maturities, covenants, security, and financing dependency.",
        "preferred_source": "Current debt schedule, facility agreements, and covenant compliance certificates.",
        "resolution": "Whether leverage, liquidity, or change-of-control exposure could affect the decision.",
        "topic": "Debt and liquidity", "risk": "Financial resilience / refinancing risk",
    },
    "intellectual-property ownership evidence": {
        "source_types": {"ip_record", "signed_contract"},
        "priority": "Important", "purpose": "Confirm ownership, licensing, encumbrances, and assignment of material intellectual property.",
        "preferred_source": "IP register, assignments, and material license agreements.",
        "resolution": "Whether material technology and brand assets are owned or usable as represented.",
        "topic": "Intellectual property", "risk": "Technology / IP ownership",
    },
    "employee and key-person obligations": {
        "source_types": {"employment_record", "management_information"},
        "priority": "Important", "purpose": "Assess leadership dependency, retention, incentives, and employment obligations.",
        "preferred_source": "Employment agreements, retention data, and organisation chart.",
        "resolution": "Whether people dependencies or obligations could disrupt continuity.",
        "topic": "People and key-person dependency", "risk": "Operational resilience / key-person risk",
    },
    "tax exposure evidence": {
        "source_types": {"tax_return", "tax_advice", "tax_assessment"},
        "priority": "Important", "purpose": "Identify tax positions, audits, liabilities, and unresolved exposures.",
        "preferred_source": "Tax returns, assessments, and tax diligence schedules.",
        "resolution": "Whether tax liabilities or compliance matters could affect value or transaction timing.",
        "topic": "Tax exposure", "risk": "Financial / regulatory exposure",
    },
    "insurance evidence": {
        "source_types": {"insurance_policy", "insurance_schedule"},
        "priority": "Important", "purpose": "Confirm coverage limits, exclusions, claims history, and continuity.",
        "preferred_source": "Current insurance certificates, policy schedules, and claims register.",
        "resolution": "Whether material operational, product, cyber, or liability risks are appropriately covered.",
        "topic": "Insurance", "risk": "Operational / liability exposure",
    },
}
OBJECTIVE_FOCUS = {
    "Acquisition Target": ["valuation assumptions", "transaction structure", "conditions precedent", "representations, warranties or transaction protections", "integration risk", "key-person dependency", "customer concentration", "debt and working capital", "regulatory approvals", "IP ownership"],
    "Investment Target": ["business model", "growth quality", "unit economics", "market position", "capital requirements", "governance", "downside risks"],
    "Vendor/Supplier": ["financial resilience", "operational capacity", "service continuity", "supplier concentration", "cybersecurity", "business continuity"],
    "Partnership": ["strategic fit", "capability fit", "reputation", "execution capacity", "commercial incentives", "conflicting interests"],
    "Customer/Client": ["financial capacity", "payment risk", "reputation", "concentration", "contractual issues", "regulatory considerations"],
    "Competitor": ["positioning", "products", "pricing", "market", "customers", "growth signals", "strategic opportunities"],
    "General Company Investigation": ["balanced commercial, financial, operational, governance, and regulatory coverage"],
}
ASSESSMENT_DIMENSIONS = (
    ("Corporate transparency", {"source_types": {"corporate_registry", "government_record", "company_filing"}, "terms": ("incorporat", "ownership", "corporate", "beneficial"), "gap": "ownership and corporate records", "missing": "No current corporate registry, ownership, or authority evidence was supplied."}),
    ("Financial quality", {"source_types": {"audited_financial_statement", "financial_statement", "debt_schedule"}, "terms": ("revenue", "margin", "cash", "debt", "financial", "profit"), "gap": "audited financial statements", "missing": "No audited financial statements or complete supporting schedules were supplied; financial condition cannot yet be adequately assessed."}),
    ("Commercial strength", {"source_types": {"customer_concentration", "signed_contract", "contract"}, "terms": ("customer", "commercial", "contract", "supplier", "revenue"), "gap": "customer concentration data", "missing": "No sufficiently complete customer, contract, or concentration evidence was supplied."}),
    ("Operational resilience", {"source_types": {"operational_report", "business_continuity_plan", "supplier_contract", "employment_record"}, "terms": ("supplier", "operational", "employee", "continuity", "capacity"), "gap": "employee and key-person obligations", "missing": "No sufficiently complete operational-continuity, supplier, or workforce evidence was supplied."}),
    ("Market position", {"source_types": {"independent_market_report", "industry_report"}, "terms": ("market", "leader", "competitor", "position"), "gap": "independent market-position evidence", "missing": "Market-position claims are not independently corroborated by the supplied evidence."}),
    ("Management/key-person risk", {"source_types": {"employment_record", "management_information"}, "terms": ("management", "leadership", "key-person", "employee"), "gap": "employee and key-person obligations", "missing": "No sufficiently complete leadership, retention, or key-person evidence was supplied."}),
    ("Technology", {"source_types": {"ip_record", "technical_assessment", "security_assessment"}, "terms": ("technology", "ip", "patent", "security", "platform"), "gap": "intellectual-property ownership evidence", "missing": "No sufficient architecture, security, technical-debt, or IP-control evidence was supplied."}),
    ("Regulatory exposure", {"source_types": {"regulatory_filing", "license"}, "terms": ("regulatory", "license", "compliance", "authori"), "gap": "regulatory licenses or authorizations", "missing": "No sufficient regulator-issued authorization or compliance evidence was supplied."}),
    ("Reputation", {"source_types": {"independent_media", "reputation_report"}, "terms": ("reputation", "adverse", "complaint"), "gap": "independent reputation evidence", "missing": "No independent reputation evidence or external-research record was supplied."}),
)


def clean(value: Any) -> str:
    return str(value if value is not None else "NOT PROVIDED").strip() or "NOT PROVIDED"


def confidence_for_tier(tier: int, independent_families: int = 0, contrary: bool = False) -> str:
    if contrary:
        return "Low"
    if tier == 1:
        return "High"
    if tier == 2 and independent_families >= 1:
        return "Medium"
    return "Low"


def source_family(source: dict[str, Any]) -> str:
    declared = clean(source.get("source_family", ""))
    if declared != "NOT PROVIDED":
        return declared
    source_type = clean(source.get("source_type", "not_provided"))
    if source_type in COMPANY_AFFILIATED_TYPES or int(source.get("evidence_tier", 3)) >= 3:
        return "company-affiliated-source-family"
    return clean(source.get("id", "unknown-source"))


def source_independence(source: dict[str, Any]) -> str:
    declared = clean(source.get("source_independence", ""))
    if declared != "NOT PROVIDED":
        return declared
    if source_family(source) == "company-affiliated-source-family":
        return "Company-affiliated / not independent"
    if int(source.get("evidence_tier", 3)) <= 2:
        return "Independent or primary source family"
    return "Independence not established"


def is_independent_source(independence: str) -> bool:
    """Return True only when the source label explicitly establishes independence."""
    label = independence.lower()
    return "independent" in label and "not independent" not in label and "independence not established" not in label


def source_recency(source: dict[str, Any], case: dict[str, Any]) -> str:
    raw = clean(source.get("date", ""))
    if raw == "NOT PROVIDED":
        return "Unknown recency"
    try:
        year = int(raw[:4])
        end = str(case.get("investigation_period", ""))[-4:]
        reference_year = int(end) if end.isdigit() else date.today().year
        delta = reference_year - year
        if delta <= 1:
            return "Current or recent"
        if delta <= 3:
            return "Aging; confirm continuing relevance"
        return "Historical; refresh before reliance"
    except (ValueError, TypeError):
        return "Date supplied; recency not deterministically assessed"


def assertion_context(assertion: dict[str, Any], source: dict[str, Any], key: str) -> str:
    return clean(assertion.get(key, source.get(key, "")))


def discrepancy_review(items: list[dict[str, Any]]) -> dict[str, str] | None:
    values = {item["value"].lower() for item in items if item["value"] != "NOT PROVIDED"}
    if len(values) <= 1:
        return None
    dimensions = {
        "period": {item["period"] for item in items if item["period"] != "NOT PROVIDED"},
        "definition": {item["definition"] for item in items if item["definition"] != "NOT PROVIDED"},
        "scope": {item["scope"] for item in items if item["scope"] != "NOT PROVIDED"},
        "geography": {item["geography"] for item in items if item["geography"] != "NOT PROVIDED"},
        "accounting_treatment": {item["accounting_treatment"] for item in items if item["accounting_treatment"] != "NOT PROVIDED"},
    }
    source = " vs ".join(item["source"] for item in items[:2])
    if len(dimensions["period"]) > 1:
        return {"status": "RECONCILED DIFFERENCE", "source": source, "reason": "Values refer to different stated periods; they are not treated as a direct contradiction.", "importance": "Moderate", "resolution": "Confirm the period-end dates and confirm whether the trend is comparable."}
    if len(dimensions["scope"]) > 1:
        return {"status": "RECONCILED DIFFERENCE", "source": source, "reason": "Values relate to explicitly different stated entity or business scopes; they are not treated as a direct contradiction.", "importance": "Moderate", "resolution": "Confirm the legal-entity and business-unit perimeter for each statement."}
    for label in ("definition", "geography", "accounting_treatment"):
        if len(dimensions[label]) > 1:
            pretty = label.replace("_", " ")
            return {"status": "APPARENT DISCREPANCY — REQUIRES RECONCILIATION", "source": source, "reason": f"Values may use different {pretty}; the available evidence does not establish a direct contradiction.", "importance": "High", "resolution": f"Reconcile the reported {pretty} using dated primary evidence."}
    return {"status": "CONTRADICTED", "source": source, "reason": "Values differ for the same stated claim, period, scope, and definition in the available evidence.", "importance": "High", "resolution": "Reconcile the conflicting statements with dated primary evidence, definitions, and scope."}


def impact_for(claim_id: str, status: str) -> tuple[str, str]:
    lower = claim_id.lower()
    if any(token in lower for token in ("concentration", "debt", "license", "regulatory", "litigation", "ownership", "ip")):
        return "Material", "The finding concerns a category that can affect transaction assumptions, continuity, or contingent exposure."
    if status == "CONTRADICTED":
        return "Material", "Unreconciled conflicting information could distort decision assumptions."
    if any(token in lower for token in ("revenue", "cash", "margin", "customer", "supplier", "employee")):
        return "Moderate", "The finding may affect commercial, financial, or operating assumptions if confirmed."
    return "Low", "The current evidence does not show a direct decision-critical effect, but traceability remains necessary."


def request_for_gap(name: str) -> dict[str, str]:
    details = GAP_LIBRARY.get(name, {
        "priority": "Important", "purpose": "Resolve a material information gap before relying on the related conclusion.",
        "preferred_source": "Current primary records or independent corroboration.", "resolution": "Whether the unresolved issue changes the decision context.",
        "topic": "Diligence gap", "risk": "Evidence completeness",
    })
    return {
        "required_evidence": name,
        "purpose": details["purpose"],
        "priority": details["priority"],
        "preferred_source": details["preferred_source"],
        "what_it_could_resolve": details["resolution"],
        "topic": details["topic"],
        "risk_addressed": details["risk"],
    }


def question_for_request(request: dict[str, str]) -> dict[str, str]:
    return {
        "priority": request["priority"], "topic": request["topic"],
        "question": f"Please provide current, complete {request['required_evidence']} and explain any material changes during the investigation period.",
        "reason_for_asking": request["purpose"], "evidence_requested": request["preferred_source"], "risk_addressed": request["risk_addressed"],
    }


def calculate_gaps(case: dict[str, Any], source_types: set[str]) -> list[str]:
    gaps = [name for name, data in GAP_LIBRARY.items() if not (data.get("source_types", set()) & source_types)]
    for stated_gap in case.get("evidence_gaps", []):
        name = clean(stated_gap)
        if name not in gaps and name != "NOT PROVIDED":
            gaps.append(name)
    return gaps


def external_research_status(case: dict[str, Any]) -> dict[str, str]:
    external = case.get("external_research", {})
    if not isinstance(external, dict) or not external.get("performed"):
        return {"status": "External research was not performed in this execution.", "performed": "No", "scope": "Document-only / supplied evidence mode."}
    return {
        "status": "Independently researched evidence is limited to sources explicitly marked as independently researched in the Sources & Evidence Register.",
        "performed": "Yes", "scope": clean(external.get("scope", "NOT PROVIDED")),
    }


def normalise_opportunities(case: dict[str, Any]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for raw in case.get("opportunities", []):
        if isinstance(raw, dict):
            result.append({
                "opportunity": clean(raw.get("opportunity", raw.get("finding", "NOT PROVIDED"))),
                "evidence": clean(raw.get("evidence", "NOT PROVIDED")), "confidence": clean(raw.get("confidence", "Low")),
                "potential_upside": clean(raw.get("potential_upside", "NOT PROVIDED")), "required_conditions": clean(raw.get("required_conditions", "NOT PROVIDED")),
                "dependencies": clean(raw.get("dependencies", "NOT PROVIDED")), "what_could_invalidate": clean(raw.get("what_could_invalidate", "NOT PROVIDED")),
                "evidence_required": clean(raw.get("evidence_required", "NOT PROVIDED")), "decision_relevance": clean(raw.get("decision_relevance", "Low")),
            })
        else:
            result.append({"opportunity": clean(raw), "evidence": "NOT PROVIDED", "confidence": "Low", "potential_upside": "NOT PROVIDED", "required_conditions": "Independent corroboration and commercial evidence.", "dependencies": "NOT PROVIDED", "what_could_invalidate": "Evidence may not support the stated opportunity.", "evidence_required": "Supporting financial, customer, or contract evidence.", "decision_relevance": "Low"})
    return result


def build_transaction_impacts(case: dict[str, Any], risks: list[dict[str, str]]) -> list[dict[str, str]]:
    focus = OBJECTIVE_FOCUS.get(clean(case.get("objective")), OBJECTIVE_FOCUS["General Company Investigation"])
    rows = []
    for risk in risks[:8]:
        rows.append({
            "finding": risk["finding"], "decision_area": "; ".join(focus[:3]), "impact": risk["decision_impact"],
            "analysis": f"This finding may affect {clean(case.get('objective'))} assumptions and warrants further analysis before reliance.",
            "cautious_action": "Obtain the identified evidence and consider appropriate qualified legal, financial, or technical review where applicable.",
        })
    return rows


def executive_finding(claim: dict[str, Any]) -> dict[str, str]:
    """Render an executive-safe finding from the same structured claim record."""
    status = claim["status"]
    if status == "SUPPORTED":
        snapshot_text = claim["claim"]
    elif status == "CONTRADICTED":
        snapshot_text = f"{claim['claim']} — CONFLICTING EVIDENCE / NOT VERIFIED. {claim['assessment']}"
    elif status == "APPARENT DISCREPANCY — REQUIRES RECONCILIATION":
        snapshot_text = f"{claim['claim']} — APPARENT DISCREPANCY / NOT VERIFIED. {claim['assessment']}"
    elif status == "PARTIALLY SUPPORTED":
        snapshot_text = f"{claim['claim']} — PARTIALLY SUPPORTED. {claim['assessment']}"
    else:
        snapshot_text = f"{claim['claim']} — NOT VERIFIED. {claim['assessment']}"
    return {"finding_id": claim["claim_id"], "claim": claim["claim"], "status": status, "confidence": claim["confidence"], "evidence": claim["evidence"], "risk": "Risk" if status != "SUPPORTED" else "Evidence-supported finding", "decision_impact": claim["decision_impact"], "evidence_gap": claim["evidence_needed"], "management_question": claim["management_question"], "snapshot_text": snapshot_text}


def validated_numerical_score(case: dict[str, Any], dimension: str) -> str:
    """Display a user-supplied score only if its calculation is reproducibly documented."""
    supplied = case.get("scores", {})
    item = supplied.get(dimension, {}) if isinstance(supplied, dict) else {}
    required = ("score", "scale", "inputs", "methodology", "confidence", "limitations")
    if not isinstance(item, dict) or any(clean(item.get(field, "")) == "NOT PROVIDED" for field in required):
        return "Not calculated; no reproducible scoring method was supplied."
    return f"{clean(item['score'])}/{clean(item['scale'])}; inputs: {clean(item['inputs'])}; methodology: {clean(item['methodology'])}; confidence: {clean(item['confidence'])}; limitations: {clean(item['limitations'])}."


def dimension_assessments(case: dict[str, Any], claims: list[dict[str, Any]], source_types: set[str], contradictions: list[dict[str, Any]]) -> tuple[list[dict[str, str]], dict[str, str]]:
    """Assess dimensions qualitatively; absence of evidence is never converted to a numerical risk score."""
    rows: list[dict[str, str]] = []
    for dimension, rule in ASSESSMENT_DIMENSIONS:
        terms = rule["terms"]
        related = [claim for claim in claims if any(term in f"{claim['claim_id']} {claim['claim']}".lower() for term in terms)]
        matching_sources = source_types & rule["source_types"]
        statuses = {claim["status"] for claim in related}
        contradiction = any(status in {"CONTRADICTED", "APPARENT DISCREPANCY — REQUIRES RECONCILIATION"} for status in statuses)
        supported = any(status in {"SUPPORTED", "PARTIALLY SUPPORTED"} for status in statuses)
        unresolved = any(status in {"UNVERIFIED", "CONTRADICTED", "APPARENT DISCREPANCY — REQUIRES RECONCILIATION"} for status in statuses)
        if not matching_sources and not related:
            assessment = "NOT ASSESSED" if dimension == "Reputation" else "INSUFFICIENT EVIDENCE"
            confidence, quality, basis = "High", "INSUFFICIENT", rule["missing"]
        elif contradiction:
            assessment, confidence, quality = "MIXED", "Low", "LOW"
            basis = "Relevant supplied evidence includes an unresolved contradiction or apparent discrepancy; the underlying condition should not be concluded from the available record."
        elif supported and unresolved:
            assessment, confidence, quality = "MIXED", "Medium", "MEDIUM"
            basis = "Some relevant evidence is supplied, but material verification or completeness limitations remain."
        elif supported or matching_sources:
            assessment, confidence, quality = "ADEQUATE", "Medium", "MEDIUM"
            basis = "Relevant supplied evidence is available, subject to stated source scope, recency, independence, and completeness limitations."
        else:
            assessment, confidence, quality, basis = "INSUFFICIENT EVIDENCE", "High", "INSUFFICIENT", rule["missing"]
        rows.append({"dimension": dimension, "assessment": assessment, "confidence": confidence, "evidence_quality": quality, "evidence_basis": basis, "numerical_analysis": validated_numerical_score(case, dimension), "evidence_request": rule["gap"]})
    insufficient = [row["dimension"] for row in rows if row["assessment"] in {"INSUFFICIENT EVIDENCE", "NOT ASSESSED"}]
    mixed = [row["dimension"] for row in rows if row["assessment"] == "MIXED"]
    if contradictions:
        overall = {"assessment": "MIXED", "confidence": "Medium", "evidence_quality": "LOW", "basis": "The evidence set contains unresolved contradictory material; no overall risk score is calculated."}
    elif insufficient:
        overall = {"assessment": "MIXED", "confidence": "Medium", "evidence_quality": "INSUFFICIENT", "basis": f"Evidence is insufficient or not assessed for: {', '.join(insufficient)}. No overall risk score is calculated."}
    elif mixed:
        overall = {"assessment": "MIXED", "confidence": "Medium", "evidence_quality": "MEDIUM", "basis": f"Relevant evidence is available but mixed for: {', '.join(mixed)}. No overall risk score is calculated."}
    else:
        overall = {"assessment": "ADEQUATE", "confidence": "Medium", "evidence_quality": "MEDIUM", "basis": "The supplied evidence supports a bounded qualitative assessment; no overall risk score is calculated."}
    return rows, overall


def analyse_case(case: dict[str, Any]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    source_types: set[str] = set()
    for source in case.get("sources", []):
        tier = int(source.get("evidence_tier", 3))
        source_id = clean(source.get("id", "unknown-source"))
        source_types.add(clean(source.get("source_type", "not_provided")))
        for assertion in source.get("assertions", []):
            claim_id = clean(assertion.get("claim_id", assertion.get("claim", source_id)))
            item = {
                "claim_id": claim_id, "claim": clean(assertion.get("claim", "NOT PROVIDED")), "value": clean(assertion.get("value", "NOT PROVIDED")),
                "classification": clean(assertion.get("classification", "COMPANY CLAIM")), "source": source_id,
                "source_type": clean(source.get("source_type", "not_provided")), "evidence_tier": tier,
                "evidence_tier_name": TIER_NAMES.get(tier, "Unknown"), "source_quality": TIER_NAMES.get(tier, "Unknown"),
                "source_family": source_family(source), "source_independence": source_independence(source), "recency": source_recency(source, case),
                "specificity": clean(assertion.get("specificity", "Specific" if assertion.get("value") not in (None, "") else "Limited")),
                "period": assertion_context(assertion, source, "period"), "definition": assertion_context(assertion, source, "definition"),
                "scope": assertion_context(assertion, source, "scope"), "geography": assertion_context(assertion, source, "geography"),
                "accounting_treatment": assertion_context(assertion, source, "accounting_treatment"),
                "origin": clean(source.get("origin", "User-supplied evidence")), "accessed_date": clean(source.get("accessed_date", source.get("date", "NOT PROVIDED"))),
                "notes": clean(source.get("summary", "No source limitation supplied.")),
            }
            grouped[claim_id].append(item)
    claims: list[dict[str, Any]] = []
    contradictions: list[dict[str, Any]] = []
    discrepancies: list[dict[str, Any]] = []
    for claim_id, items in grouped.items():
        best_tier = min(item["evidence_tier"] for item in items)
        families = {item["source_family"] for item in items}
        independent_families = {item["source_family"] for item in items if is_independent_source(item["source_independence"])}
        review = discrepancy_review(items)
        contrary = review is not None and review["status"] in {"CONTRADICTED", "APPARENT DISCREPANCY — REQUIRES RECONCILIATION"}
        if review:
            discrepancies.append({"claim_id": claim_id, "claim_a": items[0]["value"], "claim_b": items[1]["value"], **review})
        if review and review["status"] == "CONTRADICTED":
            status = "CONTRADICTED"
            assessment = "CONFLICTING EVIDENCE: available values conflict without a stated timing, definition, scope, geography, or accounting explanation."
            contradictions.append({"claim_id": claim_id, "claim_a": items[0]["value"], "claim_b": items[1]["value"], "source": review["source"], "conflict": review["reason"], "importance": review["importance"], "resolution": review["resolution"]})
        elif review and review["status"] == "APPARENT DISCREPANCY — REQUIRES RECONCILIATION":
            status = review["status"]
            assessment = review["reason"]
        elif review and review["status"] == "RECONCILED DIFFERENCE":
            status = "PARTIALLY SUPPORTED" if best_tier <= 2 else "UNVERIFIED"
            assessment = review["reason"]
        elif all(item["value"] == "NOT PROVIDED" for item in items):
            status, assessment = "UNVERIFIED", "NOT VERIFIED: no usable value was supplied."
        elif best_tier == 1:
            status, assessment = "SUPPORTED", "Supported by supplied Tier 1 primary evidence, subject to the stated period, scope, and source limitations."
        elif best_tier == 2 and independent_families:
            status, assessment = "PARTIALLY SUPPORTED", "Partially supported by independent secondary material; primary corroboration remains warranted for a material decision."
        else:
            status, assessment = "UNVERIFIED", "NOT VERIFIED: repeated company-affiliated or supporting material is not independent corroboration."
        confidence = confidence_for_tier(best_tier, len(independent_families), contrary)
        confidence_explanation = f"{confidence} confidence because the best available source is Tier {best_tier}; independent corroborating source families: {len(independent_families)}; contrary or unresolved evidence: {'yes' if contrary else 'no'}."
        impact, impact_reason = impact_for(claim_id, status)
        evidence_needed = "Dated primary evidence with explicit period, definition, scope, and source provenance."
        management_question = f"Please provide dated primary evidence supporting '{items[0]['claim']}' and explain the period, definition, scope, and any contrary statement."
        record = {
            "claim_id": claim_id, "claim": items[0]["claim"], "classification": items[0]["classification"], "status": status,
            "confidence": confidence, "confidence_explanation": confidence_explanation, "assessment": assessment,
            "why_it_matters": "Material company information should be traceable, independently assessed where possible, and bounded before it informs a decision.",
            "source_quality": TIER_NAMES.get(best_tier, "Unknown"), "source_independence": "Independent corroboration present" if independent_families else "No independent corroboration established; primary support may still be available",
            "recency": "; ".join(sorted({item["recency"] for item in items})), "specificity": "; ".join(sorted({item["specificity"] for item in items})),
            "corroboration": f"{len(families)} source family/families; {len(independent_families)} independent corroborating family/families.",
            "contrary_evidence": review["reason"] if contrary and review else "None identified in the available structured evidence.",
            "completeness": "Incomplete" if best_tier > 1 or not independent_families else "Partially complete",
            "decision_impact": impact, "decision_impact_reason": impact_reason, "evidence_needed": evidence_needed,
            "management_question": management_question, "what_would_change": f"The conclusion could change with {evidence_needed.lower()} that confirms, narrows, or refutes the current finding.",
            "evidence": items,
        }
        claims.append(record)
        for item in items:
            item["status"] = status
            records.append(item)
    gaps = calculate_gaps(case, source_types)
    evidence_requests = [request_for_gap(gap) for gap in gaps]
    management_questions = [question_for_request(item) for item in evidence_requests]
    for contradiction in contradictions:
        management_questions.insert(0, {"priority": "Critical", "topic": "Contradiction reconciliation", "question": f"Why do the sources report different values for {contradiction['claim_id']}? {contradiction['resolution']}", "reason_for_asking": "An unreconciled contradiction may materially distort decision assumptions.", "evidence_requested": "Dated primary records and a written reconciliation.", "risk_addressed": "Evidence reliability / decision quality"})
    for claim in claims:
        if claim["status"] in {"UNVERIFIED", "CONTRADICTED", "APPARENT DISCREPANCY — REQUIRES RECONCILIATION"}:
            management_questions.append({"priority": "Critical" if claim["decision_impact"] in {"Material", "Potentially Critical"} else "Important", "topic": "Claim verification", "question": claim["management_question"], "reason_for_asking": claim["why_it_matters"], "evidence_requested": claim["evidence_needed"], "risk_addressed": "Evidence reliability / decision impact"})
    risks: list[dict[str, str]] = []
    for item in contradictions:
        risks.append({"risk_id": f"R-{len(risks)+1:02d}", "category": "Evidence reliability", "finding": f"Unresolved contradiction: {item['claim_id']}.", "evidence": item["source"], "severity": "High", "confidence": "High", "potential_impact": "Decision-making may rely on an inaccurate or scope-inconsistent statement.", "time_horizon": "Immediate", "reversibility": "Moderately reversible", "evidence_gap": item["resolution"], "management_question": f"Reconcile {item['claim_id']} with dated primary evidence.", "decision_impact": "Material", "decision_impact_reason": "The disputed information could alter core operating or valuation assumptions."})
    # Evidence requests remain evidence gaps, not automatically asserted business risks. This preserves the distinction between uncertainty and risk severity.
    for raw in case.get("risks", []):
        if isinstance(raw, dict):
            risks.append({"risk_id": clean(raw.get("risk_id", f"R-{len(risks)+1:02d}")), "category": clean(raw.get("category", "NOT PROVIDED")), "finding": clean(raw.get("finding", raw.get("issue", "NOT PROVIDED"))), "evidence": clean(raw.get("evidence", "NOT PROVIDED")), "severity": clean(raw.get("severity", "NOT PROVIDED")), "confidence": clean(raw.get("confidence", "NOT PROVIDED")), "potential_impact": clean(raw.get("potential_impact", "NOT PROVIDED")), "time_horizon": clean(raw.get("time_horizon", "Near-term")), "reversibility": clean(raw.get("reversibility", "Moderately reversible")), "evidence_gap": clean(raw.get("evidence_gap", "NOT PROVIDED")), "management_question": clean(raw.get("management_question", raw.get("follow_up_question", "NOT PROVIDED"))), "decision_impact": clean(raw.get("decision_impact", "Moderate")), "decision_impact_reason": clean(raw.get("decision_impact_reason", "The stated risk may affect decision assumptions if confirmed."))})
    opportunities = normalise_opportunities(case)
    scenarios = []
    for raw in case.get("scenarios", []):
        if isinstance(raw, dict):
            scenarios.append({"case": clean(raw.get("case", "Analytical scenario")), "supported_by": clean(raw.get("supported_by", "NOT PROVIDED")), "assumptions": clean(raw.get("assumptions", "Unknown assumption")), "implication": clean(raw.get("implication", "NOT PROVIDED")), "uncertainty": clean(raw.get("uncertainty", "Unknown assumption"))})
    decision_map = [{"finding": claim["claim"], "evidence": "; ".join(f"{entry['source']} (Tier {entry['evidence_tier']}, {entry['source_independence']})" for entry in claim["evidence"]), "verification": claim["status"], "confidence": f"{claim['confidence']}: {claim['confidence_explanation']}", "risk_opportunity": "Risk" if claim["status"] in {"UNVERIFIED", "CONTRADICTED", "APPARENT DISCREPANCY — REQUIRES RECONCILIATION"} else "Evidence-supported finding", "decision_impact": f"{claim['decision_impact']}: {claim['decision_impact_reason']}", "evidence_needed": claim["evidence_needed"], "management_question": claim["management_question"]} for claim in claims]
    assessments, overall_evidence = dimension_assessments(case, claims, source_types, contradictions)
    executive_findings = [executive_finding(claim) for claim in claims]
    return {"evidence_records": records, "claims": claims, "executive_findings": executive_findings, "dimension_assessments": assessments, "overall_evidence": overall_evidence, "contradictions": contradictions, "discrepancies": discrepancies, "evidence_gaps": gaps, "evidence_requests": evidence_requests, "management_questions": management_questions, "risks": risks, "opportunity_register": opportunities, "scenarios": scenarios, "decision_map": decision_map, "transaction_impacts": build_transaction_impacts(case, risks), "external_research_status": external_research_status(case)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build V2 diligence evidence and decision-intelligence records.")
    parser.add_argument("input_path", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        case = load_input(args.input_path)
        if case.get("kind"):
            raise ValueError("Evidence tracking requires structured JSON input.")
        payload = json.dumps(analyse_case(case), indent=2, ensure_ascii=False)
        if args.output:
            args.output.write_text(payload + "\n", encoding="utf-8")
        print(payload)
        return 0
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

