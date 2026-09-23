# Airspeed plugins

One maintained workflow library for ChatGPT and Claude, using Airspeed's existing
OAuth MCP. The first workflow prepares an account brief from accessible calls,
summaries, insights, and transcripts, with links to source calls.

## Contents

```text
plugins/airspeed/
  .codex-plugin/plugin.json   ChatGPT compatibility manifest
  .claude-plugin/plugin.json  Claude manifest
  .mcp.json                  Shared remote MCP connection
  skills/account-brief/      Shared workflow instructions
.claude-plugin/marketplace.json  Claude repository installation catalog
scripts/package.py           Validate metadata and build the release ZIP
tests/cases.json              Five positive and three negative workflow cases
tests/test_package.py         Offline upload-format regression tests
docs/release.md               Installation, submission, and update process
```

The server remains at `https://mcp.goairspeed.com/mcp-oauth`. Users authenticate
with their own Airspeed account. MCP access never exceeds their Airspeed access.
This package contains no credentials, customer data, server implementation, or
local installation hooks.

The account-brief skill reads data. The remote server can expose other tools,
including tools that start work. Installing this skill does not restrict the
server's tool list or replace its authorization and confirmation controls.

## Try a workflow

After installing and connecting Airspeed in your client:

- "Prepare an account brief for Northstar using my calls from this month. My
  meeting email is rep@example.org."
- "Summarize the commitments from these Airspeed call links."
- "What questions should I ask this customer next, based on their recent calls?"

The plugin may ask for a contact email or call link to identify the right account.
Call title search does not search transcripts, and the MCP currently has no
account-name filter. A returned CRM ID is a stored reference, not live CRM data.

## Maintain and extend

Add a workflow at `plugins/airspeed/skills/<workflow-name>/SKILL.md`. Keep its
instructions provider-neutral and use real MCP tool names and parameters. Add a
realistic case to `tests/cases.json`, then run it in both clients. Keep
platform-specific changes in the two small manifests.

```sh
python3 scripts/package.py --dry-run
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/package.py
claude plugin validate plugins/airspeed --strict
```

The default build writes `dist/airspeed-<version>.zip` with both supported
manifests and the shared remote MCP configuration. Release archives exclude
documentation, tests, scripts, and development files.

For **ChatGPT's New Plugin uploader**, first register and connect Airspeed's MCP,
then build a package using that app's ID:

```sh
python3 scripts/package.py --chatgpt-app-id asdk_app_YOUR_REGISTERED_APP_ID
```

Upload **`dist/airspeed-chatgpt-<version>.zip`**. It contains the full plugin and
references the existing connection through `.app.json`. It omits the remote MCP
configuration so it does not register a second connection. Use the ID beginning
with `asdk_app_`, not the `plugin_` prefix shown in some ChatGPT URLs. The ID is
specific to the registered app; the build does not change the shared source.

For the OpenAI submission portal's **Skills section** only:

```sh
python3 scripts/package.py --skill account-brief
```

This writes **`dist/airspeed-account-brief-<version>-skill.zip`**. A skill-only ZIP
does not work in the New Plugin uploader.

Update both manifest versions together. The packaging check rejects divergent
metadata. Follow [the release process](docs/release.md) for client checks,
submission, and version rollout.

## Release scope

This release contains only account-brief guidance for existing MCP reads.
Future skills must pass the [MCP compatibility gate](docs/release.md#mcp-compatibility-gate)
before joining a release. Package validation, authenticated client testing,
connector listing, and plugin publication are separate checks.

The source is published without an open-source license. Copyright 2026 Airspeed.
All rights reserved. Airspeed retains its branding and trademark rights.

The packaged logo is the official Airspeed dark mark on a gradient background,
also used for the ChatGPT listing. Using it here does not grant trademark or
redistribution rights to others. Support and setup help:
[Airspeed documentation](https://docs.goairspeed.com/).
