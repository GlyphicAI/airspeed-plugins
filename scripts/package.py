#!/usr/bin/env python3
"""Validate shared metadata and build a portable, ChatGPT, or skill archive."""

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path


def registered_app_id(value: str) -> str:
    if not re.fullmatch(
        r"(?:asdk_app_|connector_|templated_apps_)[A-Za-z0-9][A-Za-z0-9_-]*", value
    ):
        raise argparse.ArgumentTypeError(
            "Use the registered app ID beginning with asdk_app_, connector_, or "
            "templated_apps_. Do not include a URL or its plugin_ prefix."
        )
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate without writing"
    )
    target = parser.add_mutually_exclusive_group()
    target.add_argument(
        "--chatgpt-app-id",
        type=registered_app_id,
        help="Build a ChatGPT plugin using this existing registered MCP app",
    )
    target.add_argument(
        "--skill", help="Build one skill for the submission portal's Skills section"
    )
    parser.add_argument(
        "--output-dir", type=Path, help="Output directory (default: repository dist/)"
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    plugin = root / "plugins" / "airspeed"
    codex = json.loads((plugin / ".codex-plugin/plugin.json").read_text())
    claude = json.loads((plugin / ".claude-plugin/plugin.json").read_text())
    for field in ("name", "version", "description", "author", "homepage", "keywords"):
        if not codex.get(field) or codex[field] != claude.get(field):
            raise ValueError(f"Missing or divergent metadata: {field}")
    for field in ("license", "repository"):
        if codex.get(field) != claude.get(field):
            raise ValueError(f"Divergent optional metadata: {field}")
    if codex["name"] != plugin.name or not re.fullmatch(
        r"\d+\.\d+\.\d+", codex["version"]
    ):
        raise ValueError("Plugin name or release version is invalid")
    for manifest in (codex, claude):
        if manifest.get("skills") != "./skills/":
            raise ValueError("Both manifests must use the shared skills directory")
        if manifest.get("mcpServers") != "./.mcp.json":
            raise ValueError("Both manifests must use the shared MCP configuration")
    marketplace = json.loads((root / ".claude-plugin/marketplace.json").read_text())
    entries = marketplace.get("plugins", [])
    if not marketplace.get("description") or not any(
        entry.get("name") == plugin.name
        and entry.get("source") == f"./plugins/{plugin.name}"
        for entry in entries
    ):
        raise ValueError("Claude marketplace must point to the packaged plugin")
    connection = json.loads((plugin / ".mcp.json").read_text())
    expected_connection = {
        "mcpServers": {
            "airspeed": {
                "type": "http",
                "url": "https://mcp.goairspeed.com/mcp-oauth",
            }
        }
    }
    if connection != expected_connection:
        raise ValueError(
            "Review changed endpoint, transport, or extra MCP configuration"
        )
    skills = sorted((plugin / "skills").glob("*/SKILL.md"))
    if not skills:
        raise ValueError("At least one skill is required")
    for skill in skills:
        content = skill.read_text()
        if not content.startswith(f"---\nname: {skill.parent.name}\n"):
            raise ValueError(f"Skill name does not match its directory: {skill}")
        if "[TODO" in content or "\ndescription: " not in content.split("---", 2)[1]:
            raise ValueError(f"Incomplete skill frontmatter: {skill}")
    if args.skill and args.skill not in {skill.parent.name for skill in skills}:
        parser.error(f"Unknown skill: {args.skill}")
    cases = json.loads((root / "tests/cases.json").read_text())
    if (
        sum(case["kind"] == "positive" for case in cases) < 5
        or sum(case["kind"] == "negative" for case in cases) < 3
    ):
        raise ValueError(
            "Keep at least five positive and three negative behavior cases"
        )
    files = []
    for path in sorted(plugin.rglob("*")):
        relative = path.relative_to(plugin)
        if path.is_symlink():
            raise ValueError(f"Release files must not be symlinks: {relative}")
        if not path.is_file():
            continue
        component = relative.parts[0]
        if component not in {
            ".codex-plugin",
            ".claude-plugin",
            "skills",
            "assets",
        } and (relative.as_posix() != ".mcp.json"):
            raise ValueError(f"Unexpected runtime file: {relative}")
        if path.suffix not in {".json", ".md", ".yaml", ".png", ".svg"}:
            raise ValueError(f"Unexpected runtime file type: {relative}")
        files.append((relative.as_posix(), path.read_bytes()))
    print(f"Validated {len(skills)} skills and {len(files)} runtime files")
    if args.dry_run:
        print("No archive written; authenticated behavior cases were not run")
        return
    if args.chatgpt_app_id:
        # A registered app supplies OAuth and tools; do not also register .mcp.json.
        codex.pop("mcpServers")
        codex["apps"] = "./.app.json"
        files = [
            (name, data)
            for name, data in files
            if name.split("/", 1)[0] in {"skills", "assets"}
        ]
        files.extend(
            [
                (
                    ".codex-plugin/plugin.json",
                    (json.dumps(codex, indent=2) + "\n").encode(),
                ),
                (
                    ".app.json",
                    (
                        json.dumps(
                            {"apps": {"airspeed": {"id": args.chatgpt_app_id}}},
                            indent=2,
                        )
                        + "\n"
                    ).encode(),
                ),
            ]
        )
        filename = f"airspeed-chatgpt-{codex['version']}.zip"
    elif args.skill:
        files = [
            (name.removeprefix("skills/"), data)
            for name, data in files
            if name.startswith(f"skills/{args.skill}/")
        ]
        filename = f"airspeed-{args.skill}-{codex['version']}-skill.zip"
    else:
        files = [(f"airspeed/{name}", data) for name, data in files]
        filename = f"airspeed-{codex['version']}.zip"
    output = (args.output_dir or root / "dist") / filename
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files):
            entry = zipfile.ZipInfo(name)
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            archive.writestr(entry, data)
    print(output)
    print(f"SHA-256: {hashlib.sha256(output.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
