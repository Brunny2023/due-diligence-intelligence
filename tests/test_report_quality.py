import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_report import write_report
from quality_check import check_report


class ReportQualityTests(unittest.TestCase):
    def test_acquisition_screening_full_report(self):
        case_path = ROOT / "sample" / "input" / "northstar_acquisition.json"
        case = json.loads(case_path.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            written = write_report(case, Path(directory), "all")
            report = next(path for path in written if path.suffix == ".md")
            result = check_report(report.read_text(encoding="utf-8"))
        self.assertTrue(result["passed"], result)


if __name__ == "__main__":
    unittest.main()

