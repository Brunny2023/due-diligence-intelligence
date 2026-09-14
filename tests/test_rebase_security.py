import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from security_scan import scan_package


class RebaseSecurityTests(unittest.TestCase):
    def test_package_has_no_hard_coded_credential_or_network_capable_helper(self):
        result = scan_package(ROOT)
        self.assertTrue(result["passed"], result)
        self.assertIn("scripts/evidence_tracker.py", result["scanned_files"])
        self.assertIn("scripts/quality_check.py", result["scanned_files"])


if __name__ == "__main__":
    unittest.main()
