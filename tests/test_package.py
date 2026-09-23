"""Check the different upload contracts without a client account or network."""

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "airspeed"
APP_ID = "asdk_app_packaging_test"


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.output = Path(self.directory.name)

    def package(self, *args, success=True):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/package.py"),
                "--output-dir",
                str(self.output),
                *args,
            ],
            capture_output=True,
            text=True,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def test_chatgpt_archive_uses_existing_app_and_preserves_shared_source(self):
        before = {
            path.relative_to(PLUGIN).as_posix(): path.read_bytes()
            for path in PLUGIN.rglob("*")
            if path.is_file()
        }
        self.package("--chatgpt-app-id", APP_ID)
        output = next(self.output.glob("airspeed-chatgpt-*.zip"))
        with zipfile.ZipFile(output) as archive:
            expected_shared = {
                name for name in before if name.startswith(("skills/", "assets/"))
            }
            self.assertEqual(
                set(archive.namelist()),
                expected_shared | {".app.json", ".codex-plugin/plugin.json"},
            )
            manifest = json.loads(archive.read(".codex-plugin/plugin.json"))
            self.assertEqual(manifest["apps"], "./.app.json")
            self.assertNotIn("mcpServers", manifest)
            self.assertEqual(
                json.loads(archive.read(".app.json")),
                {"apps": {"airspeed": {"id": APP_ID}}},
            )
            for name in expected_shared:
                self.assertEqual(archive.read(name), before[name])
        for name, content in before.items():
            self.assertEqual((PLUGIN / name).read_bytes(), content)
        first_build = output.read_bytes()
        self.package("--chatgpt-app-id", APP_ID)
        self.assertEqual(output.read_bytes(), first_build)

    def test_url_plugin_prefix_and_invalid_ids_fail_before_writing(self):
        for invalid in (
            f"plugin_{APP_ID}",
            f"https://chatgpt.com/plugins/{APP_ID}",
            "asdk_app_",
            "asdk_app_demo space",
            "asdk_app_demo/other",
        ):
            with self.subTest(app_id=invalid):
                result = self.package("--chatgpt-app-id", invalid, success=False)
                self.assertIn("registered app ID", result.stderr)
                self.assertIn("plugin_ prefix", result.stderr)
                self.assertFalse(list(self.output.iterdir()))

    def test_portable_archive_keeps_both_manifests_and_remote_mcp(self):
        self.package()
        with zipfile.ZipFile(next(self.output.glob("*.zip"))) as archive:
            for name in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
                manifest = json.loads(archive.read(f"airspeed/{name}"))
                self.assertEqual(manifest["mcpServers"], "./.mcp.json")
                self.assertNotIn("apps", manifest)
            self.assertEqual(
                archive.read("airspeed/.mcp.json"), (PLUGIN / ".mcp.json").read_bytes()
            )
            self.assertNotIn("airspeed/.app.json", archive.namelist())

    def test_skill_upload_is_distinct_from_full_plugin_upload(self):
        self.package("--skill", "account-brief")
        output = next(self.output.glob("airspeed-account-brief-*-skill.zip"))
        with zipfile.ZipFile(output) as archive:
            self.assertIn("account-brief/SKILL.md", archive.namelist())
            self.assertIn("account-brief/agents/openai.yaml", archive.namelist())
            self.assertTrue(
                all(name.startswith("account-brief/") for name in archive.namelist())
            )
        self.package("--skill", "../account-brief", success=False)

    def test_dry_run_does_not_create_an_upload(self):
        self.package("--chatgpt-app-id", APP_ID, "--dry-run")
        self.assertFalse(list(self.output.iterdir()))


if __name__ == "__main__":
    unittest.main()
