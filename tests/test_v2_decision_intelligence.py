import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from evidence_tracker import analyse_case
from build_report import build_markdown
from quality_check import check_report


def case_with(sources, **extra):
    case = {"company": {"name": "V2 Test Co."}, "objective": "Acquisition Target", "investigation_period": "FY2025", "sources": sources}
    case.update(extra)
    return case


class V2DecisionIntelligenceTests(unittest.TestCase):
    def test_same_source_family_is_not_independent_corroboration(self):
        sources = [{"id": name, "source_type": source_type, "evidence_tier": 3, "source_family": "company-marketing", "assertions": [{"claim_id": "customers", "claim": "Customer count", "value": "500"}]} for name, source_type in [("site", "company_website"), ("deck", "company_presentation"), ("profile", "company_linkedin")]]
        claim = analyse_case(case_with(sources))["claims"][0]
        self.assertEqual(claim["status"], "UNVERIFIED")
        self.assertIn("0 independent", claim["corroboration"])

    def test_date_discrepancy_is_not_false_contradiction(self):
        sources = [{"id": "old", "source_type": "company_website", "evidence_tier": 3, "assertions": [{"claim_id": "employees", "claim": "Employees", "value": "500", "period": "2024"}]}, {"id": "new", "source_type": "company_website", "evidence_tier": 3, "assertions": [{"claim_id": "employees", "claim": "Employees", "value": "650", "period": "2025"}]}]
        result = analyse_case(case_with(sources))
        self.assertEqual(result["contradictions"], [])
        self.assertEqual(result["discrepancies"][0]["status"], "RECONCILED DIFFERENCE")

    def test_definition_discrepancy_requires_reconciliation(self):
        sources = [{"id": "a", "source_type": "company_website", "evidence_tier": 3, "assertions": [{"claim_id": "headcount", "claim": "Headcount", "value": "500", "definition": "employees"}]}, {"id": "b", "source_type": "company_presentation", "evidence_tier": 3, "assertions": [{"claim_id": "headcount", "claim": "Headcount", "value": "620", "definition": "employees plus contractors"}]}]
        result = analyse_case(case_with(sources))
        self.assertEqual(result["contradictions"], [])
        self.assertEqual(result["claims"][0]["status"], "APPARENT DISCREPANCY — REQUIRES RECONCILIATION")

    def test_subsidiary_scope_difference_is_not_false_contradiction(self):
        sources = [{"id": "parent", "source_type": "company_website", "evidence_tier": 3, "assertions": [{"claim_id": "revenue", "claim": "Revenue", "value": "100", "scope": "parent"}]}, {"id": "subsidiary", "source_type": "company_presentation", "evidence_tier": 3, "assertions": [{"claim_id": "revenue", "claim": "Revenue", "value": "60", "scope": "subsidiary"}]}]
        result = analyse_case(case_with(sources))
        self.assertEqual(result["contradictions"], [])
        self.assertEqual(result["discrepancies"][0]["status"], "RECONCILED DIFFERENCE")

    def test_customer_concentration_gap_generates_specific_request(self):
        result = analyse_case(case_with([]))
        request = next(item for item in result["evidence_requests"] if item["required_evidence"] == "customer concentration data")
        self.assertEqual(request["priority"], "Critical")
        self.assertIn("revenue dependency", request["purpose"])

    def test_management_question_is_linked_to_risk(self):
        result = analyse_case(case_with([], risks=[{"category": "Commercial", "issue": "Concentration", "severity": "High", "evidence": "NOT PROVIDED", "follow_up_question": "Provide customer schedule."}]))
        self.assertTrue(any(item["risk_addressed"] for item in result["management_questions"]))
        self.assertTrue(any("customer concentration" in item["question"].lower() for item in result["management_questions"]))

    def test_decision_map_contains_required_fields(self):
        sources = [{"id": "record", "source_type": "corporate_registry", "evidence_tier": 1, "assertions": [{"claim_id": "incorporation", "claim": "Incorporated", "value": "2016", "classification": "FACT"}]}]
        row = analyse_case(case_with(sources))["decision_map"][0]
        self.assertEqual(set(row), {"finding", "evidence", "verification", "confidence", "risk_opportunity", "decision_impact", "evidence_needed", "management_question"})

    def test_unverified_claim_has_conclusion_change_conditions(self):
        sources = [{"id": "site", "source_type": "company_website", "evidence_tier": 3, "assertions": [{"claim_id": "market", "claim": "Market leader", "value": "leader"}]}]
        claim = analyse_case(case_with(sources))["claims"][0]
        self.assertEqual(claim["status"], "UNVERIFIED")
        self.assertIn("could change", claim["what_would_change"])

    def test_opportunity_register_is_generated(self):
        result = analyse_case(case_with([], opportunities=[{"opportunity": "New market", "evidence": "customer demand", "confidence": "Low"}]))
        self.assertEqual(result["opportunity_register"][0]["opportunity"], "New market")

    def test_external_research_unavailable_is_never_fabricated(self):
        status = analyse_case(case_with([]))["external_research_status"]
        self.assertEqual(status["performed"], "No")
        self.assertIn("not performed", status["status"])

    def test_scenario_and_financial_boundaries_render_in_report(self):
        report = build_markdown(case_with([], scenarios=[{"case": "Base Case", "supported_by": "None", "assumptions": "ANALYTICAL SCENARIO: test", "implication": "Test", "uncertainty": "Unknown assumption"}]))
        self.assertIn("ANALYTICAL SCENARIO control", report)
        self.assertIn("Calculation not possible from available evidence.", report)
        self.assertTrue(check_report(report)["passed"])


if __name__ == "__main__":
    unittest.main()

