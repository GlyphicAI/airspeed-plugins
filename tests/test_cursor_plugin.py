"""Validate Cursor manifests without a Cursor CLI or a signed-in client."""

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CursorPluginTests(unittest.TestCase):
    def test_official_schema_logo_mcp_and_skills(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_cursor_plugin.py")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Skills discovered:", result.stdout)
        for skill in (
            "account-brief",
            "scorecard-analysis",
            "discovery-next-step-autopsy",
        ):
            self.assertIn(skill, result.stdout)
        self.assertIn("mcp.goairspeed.com/mcp-oauth", result.stdout)
        self.assertIn("opaque background", result.stdout)


if __name__ == "__main__":
    unittest.main()
