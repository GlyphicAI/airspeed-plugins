"""Validate the Devin plugin directory without Devin or a signed-in client."""

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DevinPluginTests(unittest.TestCase):
    def test_directory_matches_devin_marketplace_rules(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_devin_plugin.py")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("plugins/airspeed-devin", result.stdout)
        self.assertIn("mcp.goairspeed.com/mcp-oauth", result.stdout)
        self.assertIn("No shadow manifest", result.stdout)


if __name__ == "__main__":
    unittest.main()
