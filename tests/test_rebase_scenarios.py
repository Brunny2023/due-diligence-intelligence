import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_report import build_markdown
from evidence_tracker import analyse_case
from quality_check import check_report


def case_with(sources, **extra):
    case = {
        "company": {"name": "Rebase Test Co."},
        "objective": "Acquisition Target",
        "investigation_period": "FY2025",
        "sources": sources,
    }
    case.update(extra)
    return case


class FinalRebaseScenarioTests(unittest.TestCase):
    def test_normal_diligence_investigation_generates_quality_checked_report(self):
        sources = [
            {
                "id": "registry",
                "source_type": "corporate_registry",
                "evidence_tier": 1,
                "source_family": "registry",
                "assertions": [
                    {"claim_id": "incorporation", "claim": "Incorporation year", "value": "2016", "classification": "FACT"}
                ],
            }
        ]
        report = build_markdown(case_with(sources))
        self.assertIn("Diligence Decision Map", report)
        self.assertTrue(check_report(report)["passed"])

    def test_multi_document_evidence_keeps_source_provenance_and_reconciliation(self):
        sources = [
            {
                "id": "annual-report",
                "source_type": "financial_statement",
                "evidence_tier": 1,
                "source_family": "audited-record",
                "assertions": [
                    {"claim_id": "headcount", "claim": "Employees", "value": "500", "period": "2024"}
                ],
            },
            {
                "id": "current-presentation",
                "source_type": "company_presentation",
                "evidence_tier": 3,
                "source_family": "company-marketing",
                "assertions": [
                    {"claim_id": "headcount", "claim": "Employees", "value": "620", "period": "2025"}
                ],
            },
        ]
        result = analyse_case(case_with(sources))
        self.assertEqual(len(result["claims"][0]["evidence"]), 2)
        self.assertEqual(result["contradictions"], [])
        self.assertEqual(result["discrepancies"][0]["status"], "RECONCILED DIFFERENCE")

    def test_large_evidence_set_remains_traceable_and_bounded(self):
        sources = [
            {
                "id": f"record-{index}",
                "source_type": "corporate_registry",
                "evidence_tier": 1,
                "source_family": "registry",
                "assertions": [
                    {
                        "claim_id": f"claim-{index}",
                        "claim": f"Registered fact {index}",
                        "value": str(index),
                        "classification": "FACT",
                    }
                ],
            }
            for index in range(80)
        ]
        result = analyse_case(case_with(sources))
        self.assertEqual(len(result["evidence_records"]), 80)
        self.assertEqual(len(result["claims"]), 80)
        self.assertEqual(result["contradictions"], [])
        self.assertTrue(all(item["evidence"] for item in result["claims"]))


if __name__ == "__main__":
    unittest.main()
