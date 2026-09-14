import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_report import build_markdown
from evidence_tracker import analyse_case
from quality_check import check_report


class V21HardeningTests(unittest.TestCase):
    def _base_case(self, sources):
        return {
            "company": {"name": "Example Co.", "website": "https://example.invalid", "description": "Fictional test company."},
            "objective": "Acquisition Target",
            "report_mode": "Standard Due Diligence",
            "investigation_period": "FY2025",
            "sources": sources,
            "risks": [],
            "opportunities": [],
            "external_research": {"performed": False},
        }

    def test_executive_snapshot_cannot_upgrade_employee_count_uncertainty(self):
        case = self._base_case([
            {
                "id": "company-website", "source_type": "company_website", "evidence_tier": 3, "date": "2025-03-01",
                "summary": "Fictional company website.",
                "assertions": [{"claim_id": "employee_count", "claim": "Employee count", "value": "500", "classification": "COMPANY CLAIM", "period": "2025", "scope": "Target entity", "definition": "Employees"}],
            },
            {
                "id": "company-presentation", "source_type": "company_presentation", "evidence_tier": 3, "date": "2025-03-15",
                "summary": "Fictional company presentation.",
                "assertions": [{"claim_id": "employee_count", "claim": "Employee count", "value": "1200", "classification": "COMPANY CLAIM", "period": "2025", "scope": "Target entity", "definition": "Employees"}],
            },
        ])
        analysis = analyse_case(case)
        report = build_markdown(case)
        claim = next(item for item in analysis["claims"] if item["claim_id"] == "employee_count")
        self.assertEqual(claim["status"], "CONTRADICTED")
        self.assertIn("Employee count — CONFLICTING EVIDENCE / NOT VERIFIED", report)
        self.assertNotIn("| Major findings | Employee count;", report)
        self.assertIn("| Employee count |", report)
        self.assertIn("| CONTRADICTED |", report)
        self.assertTrue(check_report(report)["passed"], check_report(report))

    def test_insufficient_financial_evidence_does_not_create_high_financial_risk(self):
        case = self._base_case([
            {
                "id": "company-website", "source_type": "company_website", "evidence_tier": 3, "date": "2025-03-01",
                "summary": "Fictional company website.",
                "assertions": [{"claim_id": "annual_revenue", "claim": "Annual revenue", "value": "US$50 million", "classification": "COMPANY CLAIM", "period": "FY2025", "scope": "Target entity", "definition": "Annual revenue"}],
            },
        ])
        analysis = analyse_case(case)
        report = build_markdown(case)
        revenue_claim = next(item for item in analysis["claims"] if item["claim_id"] == "annual_revenue")
        financial = next(item for item in analysis["dimension_assessments"] if item["dimension"] == "Financial quality")
        self.assertEqual(revenue_claim["status"], "UNVERIFIED")
        self.assertEqual(financial["assessment"], "INSUFFICIENT EVIDENCE")
        self.assertIn("financial condition cannot yet be adequately assessed", financial["evidence_basis"].lower())
        self.assertIn("audited financial statements", " ".join(analysis["evidence_gaps"]).lower())
        self.assertNotIn("| Financial quality | High |", report)
        self.assertIn("| Financial quality | INSUFFICIENT EVIDENCE |", report)
        self.assertIn("Annual revenue — NOT VERIFIED", report)
        self.assertTrue(check_report(report)["passed"], check_report(report))


if __name__ == "__main__":
    unittest.main()
