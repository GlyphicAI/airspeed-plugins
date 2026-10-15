#!/usr/bin/env python3
"""Validate the Cursor plugin manifests against the official Cursor schemas.

Schemas are copied from cursor/plugins main at 1e5c90a4b6f249917bd21fe361b3a2a7deb741b8
(schemas/plugin.schema.json and schemas/marketplace.schema.json). The Cursor CLI
was not available here, so this script is the local stand-in for that check.
"""

import json
import struct
import sys
import zlib
from pathlib import Path

from jsonschema import Draft7Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas" / "cursor"
PLUGIN_DIR = ROOT / "plugins" / "airspeed"
EXPECTED_MCP = {
    "mcpServers": {
        "airspeed": {
            "type": "http",
            "url": "https://mcp.goairspeed.com/mcp-oauth",
        }
    }
}
ENTRY_FIELDS = {"name", "source", "description", "minClientVersions"}
REQUIRED_SKILLS = {
    "account-brief",
    "scorecard-analysis",
    "discovery-next-step-autopsy",
}
# Same shared identity fields scripts/package.py compares between Cursor and Codex.
SHARED_WITH_CODEX = (
    "name",
    "version",
    "description",
    "homepage",
    "keywords",
    "repository",
)


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")


def schema_errors(schema: dict, instance: dict) -> list[str]:
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    messages = []
    for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.path)):
        location = "/" + "/".join(str(part) for part in error.path)
        messages.append(f"{location or '/'}: {error.message}")
    return messages


def png_size_and_alpha(path: Path) -> tuple[int, int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        fail(f"{path.relative_to(ROOT)} is not a PNG")
    offset = 8
    width = height = color = bit = None
    idat = b""
    while offset + 8 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8]
        chunk = data[offset + 8 : offset + 8 + length]
        if kind == b"IHDR":
            width, height, bit, color, *_rest = struct.unpack(">IIBBBBB", chunk)
        elif kind == b"IDAT":
            idat += chunk
        elif kind == b"IEND":
            break
        offset += 12 + length
    if width is None or not idat:
        fail(f"{path.relative_to(ROOT)} is missing IHDR or image data")
    if bit != 8 or color not in {2, 6}:
        fail(
            f"{path.relative_to(ROOT)} must be 8-bit RGB or RGBA "
            f"(bit={bit}, color={color})"
        )
    channels = 3 if color == 2 else 4
    raw = zlib.decompress(idat)
    stride = width * channels
    if len(raw) != (stride + 1) * height:
        fail(f"{path.relative_to(ROOT)} has an unexpected image size")

    def paeth(left: int, up: int, upper_left: int) -> int:
        estimate = left + up - upper_left
        if abs(estimate - left) <= abs(estimate - up) and abs(estimate - left) <= abs(
            estimate - upper_left
        ):
            return left
        if abs(estimate - up) <= abs(estimate - upper_left):
            return up
        return upper_left

    cursor = 0
    previous = bytearray(stride)
    minimum_alpha = 255
    for _y in range(height):
        filter_type = raw[cursor]
        cursor += 1
        row = bytearray(raw[cursor : cursor + stride])
        cursor += stride
        for x in range(stride):
            left = row[x - channels] if x >= channels else 0
            up = previous[x]
            upper_left = previous[x - channels] if x >= channels else 0
            if filter_type == 0:
                continue
            if filter_type == 1:
                row[x] = (row[x] + left) & 255
            elif filter_type == 2:
                row[x] = (row[x] + up) & 255
            elif filter_type == 3:
                row[x] = (row[x] + ((left + up) // 2)) & 255
            elif filter_type == 4:
                row[x] = (row[x] + paeth(left, up, upper_left)) & 255
            else:
                fail(f"{path.relative_to(ROOT)} uses unknown PNG filter {filter_type}")
        if channels == 4:
            for x in range(3, stride, 4):
                minimum_alpha = min(minimum_alpha, row[x])
        previous = row
    return width, height, minimum_alpha


def require_codex_parity(plugin: dict) -> None:
    codex = load_json(PLUGIN_DIR / ".codex-plugin" / "plugin.json")
    for field in SHARED_WITH_CODEX:
        if plugin.get(field) != codex.get(field):
            fail(f"Cursor manifest diverges from shared metadata: {field}")
    cursor_author = plugin.get("author")
    codex_author = codex.get("author")
    if (
        not isinstance(cursor_author, dict)
        or not isinstance(codex_author, dict)
        or cursor_author.get("name") != codex_author.get("name")
    ):
        fail("Cursor author name diverges from the shared manifests")


def discover_skills(plugin: dict) -> list[str]:
    skills_field = plugin.get("skills")
    if skills_field != "./skills/":
        fail('Cursor plugin skills must be "./skills/" so discovery stays shared')
    skills_dir = (PLUGIN_DIR / "skills").resolve()
    found = []
    for skill in sorted(skills_dir.glob("*/SKILL.md")):
        frontmatter = skill.read_text().split("---", 2)
        if len(frontmatter) < 3 or not skill.read_text().startswith("---\n"):
            fail(f"Skill is missing frontmatter: {skill.parent.name}")
        header = frontmatter[1]
        if f"\nname: {skill.parent.name}\n" not in f"\n{header}":
            fail(f"Skill name does not match its directory: {skill.parent.name}")
        if "\ndescription:" not in f"\n{header}":
            fail(f"Skill is missing a description: {skill.parent.name}")
        found.append(skill.parent.name)
    missing = REQUIRED_SKILLS - set(found)
    if missing:
        fail(f"Missing skills: {', '.join(sorted(missing))}")
    return found


def main() -> None:
    plugin_schema = load_json(SCHEMA_DIR / "plugin.schema.json")
    marketplace_schema = load_json(SCHEMA_DIR / "marketplace.schema.json")
    plugin_path = PLUGIN_DIR / ".cursor-plugin" / "plugin.json"
    marketplace_path = ROOT / ".cursor-plugin" / "marketplace.json"
    plugin = load_json(plugin_path)
    marketplace = load_json(marketplace_path)

    for label, schema, instance in (
        ("plugin.json", plugin_schema, plugin),
        ("marketplace.json", marketplace_schema, marketplace),
    ):
        errors = schema_errors(schema, instance)
        if errors:
            fail(label + " schema validation failed:\n  " + "\n  ".join(errors))

    require_codex_parity(plugin)
    if plugin.get("displayName") != "Airspeed" or not plugin.get("category"):
        fail("Cursor plugin needs displayName Airspeed and a category")
    logo = plugin.get("logo")
    if not isinstance(logo, str) or logo.startswith(("/", "http")) or ".." in Path(logo).parts:
        fail("Cursor logo must be a relative path inside the plugin")
    logo_path = PLUGIN_DIR / logo
    if logo_path.resolve() != (PLUGIN_DIR / "assets" / "logo.png").resolve():
        fail("Cursor logo must point at plugins/airspeed/assets/logo.png")
    width, height, minimum_alpha = png_size_and_alpha(logo_path)
    if width != height:
        fail(f"Cursor logo must be square (got {width}x{height})")
    if minimum_alpha < 250:
        fail(f"Cursor logo background is transparent (minimum alpha {minimum_alpha})")

    mcp_field = plugin.get("mcpServers")
    if mcp_field != "./.mcp.json":
        fail('Cursor mcpServers must reference "./.mcp.json"')
    connection = load_json(PLUGIN_DIR / ".mcp.json")
    if connection != EXPECTED_MCP:
        fail("Shared MCP config must stay the production HTTP OAuth endpoint")

    entries = marketplace.get("plugins") or []
    if len(entries) != 1:
        fail("Cursor marketplace must list exactly the airspeed plugin")
    entry = entries[0]
    extra = set(entry) - ENTRY_FIELDS
    if extra:
        fail(
            "Marketplace plugin entries may only contain "
            f"name, source, description, and minClientVersions (extra: {sorted(extra)})"
        )
    if entry.get("name") != plugin["name"]:
        fail("Marketplace entry name does not match plugin.json")
    if entry.get("source") != "plugins/airspeed":
        fail('Marketplace source must be "plugins/airspeed"')
    if entry.get("description") != plugin.get("description"):
        fail("Marketplace description does not match plugin.json")
    source_dir = (ROOT / entry["source"]).resolve()
    if source_dir != PLUGIN_DIR.resolve() or not plugin_path.is_file():
        fail("Marketplace source does not resolve to the Cursor plugin manifest")

    skills = discover_skills(plugin)
    print(
        f"Validated Cursor plugin {plugin['name']} {plugin['version']} "
        f"({plugin['displayName']}, {plugin['category']})"
    )
    print(f"Logo: {width}x{height} PNG, opaque background (minimum alpha {minimum_alpha})")
    print("MCP: https://mcp.goairspeed.com/mcp-oauth (http) via ./.mcp.json")
    print("Skills discovered: " + ", ".join(skills))


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(0)
