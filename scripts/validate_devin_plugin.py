#!/usr/bin/env python3
"""Validate plugins/airspeed-devin against Devin's marketplace plugin rules.

Rules are taken from CognitionAI/devin-marketplace scripts/validate.py at
70dedee48316f24bb2cb7083b961fc9570840c8e (check_local_plugin, check_logo,
check_server, and the shadow-manifest list). Devin checks those rules for
plugins authored in its own repository. An upstream git-subdir entry is only
checked for shape and commit pin, so this script applies the same directory
rules here before Cognition pins the path.

The manifest name stays "airspeed". The directory is plugins/airspeed-devin
because the shared plugins/airspeed tree contains .mcp.json, which Devin
rejects at a plugin root. Devin compares name to the directory only for
plugins that live under its own plugins/ folder.
"""

import hashlib
import json
import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_DIR = ROOT / "plugins" / "airspeed-devin"
SHARED_LOGO = ROOT / "plugins" / "airspeed" / "assets" / "logo.png"
MANIFEST_PATH = PLUGIN_DIR / ".devin-plugin" / "plugin.json"
MCP_URL = "https://mcp.goairspeed.com/mcp-oauth"
PLUGIN_KEYS = {
    "name",
    "displayName",
    "description",
    "shortDescription",
    "setup",
    "homepage",
    "repository",
    "logo",
    "keywords",
    "mcpServers",
}
HTTP_KEYS = {"url", "headers", "transport", "oauthClientId", "oauthScopes"}
SHADOW_FILES = ("plugin.json", ".mcp.json", "mcp.json")
OTHER_MARKETPLACE_DIRS = (".claude-plugin", ".codex-plugin", ".cursor-plugin")
ALLOWED_FILES = {
    ".devin-plugin/plugin.json",
    "logo.png",
}
LOGO_RE = re.compile(r"^[A-Za-z0-9_-]+(/[A-Za-z0-9_-]+)*\.(svg|png|jpg|jpeg|webp)$")
NAME_RE = re.compile(r"^[a-z0-9]+([.-][a-z0-9]+)*$")
PLACEHOLDER_RE = re.compile(r"\$\{([^}]*)\}")


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_tree(errors: list[str]) -> None:
    if not PLUGIN_DIR.is_dir():
        errors.append("plugins/airspeed-devin is missing")
        return
    found: set[str] = set()
    for parent, dirs, files in os.walk(PLUGIN_DIR):
        for name in dirs + files:
            path = Path(parent) / name
            relative = path.relative_to(PLUGIN_DIR).as_posix()
            if path.is_symlink():
                errors.append(f"symlink {relative} is not allowed")
                continue
            if name in SHADOW_FILES and path.parent == PLUGIN_DIR:
                errors.append(
                    f"{relative} is not allowed; declare everything in "
                    ".devin-plugin/plugin.json"
                )
            if path.is_dir() and name in OTHER_MARKETPLACE_DIRS:
                errors.append(
                    f"{relative} is another marketplace manifest; keep this "
                    "directory limited to the Devin plugin"
                )
        for name in files:
            path = Path(parent) / name
            if path.is_symlink() or not path.is_file():
                continue
            found.add(path.relative_to(PLUGIN_DIR).as_posix())
    extra = found - ALLOWED_FILES
    missing = ALLOWED_FILES - found
    if extra:
        errors.append(
            "unexpected files in plugins/airspeed-devin: " + ", ".join(sorted(extra))
        )
    if missing:
        errors.append(
            "plugins/airspeed-devin is missing: " + ", ".join(sorted(missing))
        )


def check_placeholders(where: str, value: str, errors: list[str]) -> None:
    for reference in PLACEHOLDER_RE.findall(value):
        errors.append(
            f"{where}: placeholder ${{{reference}}} is not allowed; "
            "the hosted MCP uses OAuth and this directory has no credentials"
        )


def check_server(config: object, errors: list[str]) -> None:
    where = "plugins/airspeed-devin mcpServers.airspeed"
    if not isinstance(config, dict):
        errors.append(f"{where} must be an object")
        return
    extra = set(config) - HTTP_KEYS - {"description"}
    if "command" in config:
        errors.append(f"{where} must be the hosted https MCP, with no local command")
        return
    if extra:
        errors.append(f"{where} has unexpected keys {sorted(extra)}")
    url = config.get("url")
    if url != MCP_URL:
        errors.append(f"{where} url must be {MCP_URL}")
    headers = config.get("headers", {})
    if headers:
        errors.append(f"{where} must not set headers")
    elif not isinstance(headers, dict):
        errors.append(f"{where} headers must be an object")
    strings = [value for value in config.values() if isinstance(value, str)]
    for value in strings:
        check_placeholders(where, value, errors)


def check_manifest(errors: list[str]) -> None:
    if not MANIFEST_PATH.is_file():
        errors.append("plugins/airspeed-devin/.devin-plugin/plugin.json is missing")
        return
    try:
        data = json.loads(MANIFEST_PATH.read_text())
    except json.JSONDecodeError as exc:
        errors.append(f".devin-plugin/plugin.json is not valid JSON: {exc}")
        return
    if not isinstance(data, dict):
        errors.append(".devin-plugin/plugin.json must be an object")
        return
    extra = set(data) - PLUGIN_KEYS
    if extra:
        errors.append(f"unexpected manifest keys {sorted(extra)}")
    name = data.get("name")
    if name != "airspeed" or not isinstance(name, str) or not NAME_RE.match(name):
        errors.append('name must be "airspeed"')
    display_name = data.get("displayName")
    if (
        not isinstance(display_name, str)
        or display_name != "Airspeed"
        or display_name != display_name.strip()
        or any(ch.isspace() and ch != " " for ch in display_name)
    ):
        errors.append('displayName must be "Airspeed"')
    description = data.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("description must be a non-empty string")
    elif description != description.strip() or description.endswith("."):
        errors.append("description must be one sentence without a trailing period")
    elif "glyphic" in description.lower():
        errors.append("description must use the Airspeed name")
    short_description = data.get("shortDescription")
    if not isinstance(short_description, str) or not short_description.strip():
        errors.append("shortDescription must be a non-empty string")
    elif len(short_description) > 40:
        errors.append("shortDescription must be 40 characters or fewer")
    elif short_description != "Sales calls, deals and coaching":
        errors.append(
            'shortDescription must stay "Sales calls, deals and coaching"'
        )
    if data.get("homepage") != "https://www.goairspeed.com":
        errors.append("homepage must be https://www.goairspeed.com")
    logo = data.get("logo")
    if not isinstance(logo, str) or (
        not logo.startswith("https://") and not LOGO_RE.match(logo)
    ):
        errors.append(
            "logo must be an https url or a plain repo-relative file path"
        )
    elif logo != "logo.png":
        errors.append('logo must be "logo.png" inside plugins/airspeed-devin')
    else:
        logo_path = PLUGIN_DIR / logo
        if not logo_path.is_file() or logo_path.is_symlink():
            errors.append("logo.png must be a file inside plugins/airspeed-devin")
        elif logo_path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            errors.append("logo.png must be a PNG")
        elif not SHARED_LOGO.is_file() or sha256(logo_path) != sha256(SHARED_LOGO):
            errors.append(
                "logo.png must match plugins/airspeed/assets/logo.png"
            )
    keywords = data.get("keywords")
    if keywords != ["Customer & Sales"]:
        errors.append('keywords must be ["Customer & Sales"]')
    servers = data.get("mcpServers")
    if not isinstance(servers, dict) or set(servers) != {"airspeed"}:
        errors.append('mcpServers must contain exactly the "airspeed" server')
        return
    check_server(servers["airspeed"], errors)
    text = MANIFEST_PATH.read_text()
    if "glyphic" in text.lower():
        errors.append("manifest must use the Airspeed name")


def main() -> None:
    errors: list[str] = []
    check_tree(errors)
    check_manifest(errors)
    if errors:
        fail("\n".join(errors))
    print("Validated Devin plugin plugins/airspeed-devin")
    print("Manifest name: airspeed (Airspeed)")
    print(f"MCP: {MCP_URL}")
    print("Logo: logo.png, same file as plugins/airspeed/assets/logo.png")
    print("No shadow manifest, symlink, or credential in the plugin directory")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(0)
