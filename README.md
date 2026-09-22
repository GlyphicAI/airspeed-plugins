# Airspeed plugins

One maintained workflow library for ChatGPT and Claude, using Airspeed's existing
OAuth MCP. The workflows prepare account briefs from accessible call evidence
and analyze existing coaching scorecards with comparable, source-linked visuals.

## Contents

```text
plugins/airspeed/
  .codex-plugin/plugin.json   ChatGPT compatibility manifest
  .claude-plugin/plugin.json  Claude manifest
  .mcp.json                  Shared remote MCP connection
  skills/account-brief/      Shared workflow instructions
  skills/scorecard-analysis/ Shared coaching-analysis instructions
.claude-plugin/marketplace.json  Claude repository installation catalog
scripts/package.py           Validate metadata and build the release ZIP
tests/cases.json              Behavior cases for both workflows
docs/release.md               Installation, submission, and update process
```

The server remains at `https://mcp.goairspeed.com/mcp-oauth`. Users authenticate
with their own Airspeed account. MCP access never exceeds their Airspeed access.
This package contains no credentials, customer data, server implementation, or
local installation hooks.

Both skills read data. The remote server can expose other tools,
including tools that start work. Installing this skill does not restrict the
server's tool list or replace its authorization and confirmation controls.

## Try a workflow

After installing and connecting Airspeed in your client:

- "Prepare an account brief for Northstar using my calls from this month. My
  meeting email is rep@example.org."
- "Summarize the commitments from these Airspeed call links."
- "What questions should I ask this customer next, based on their recent calls?"
- "Review my coaching scorecards this month and show comparable skill trends."

The plugin may ask for a contact email or call link to identify the right account.
Call title search does not search transcripts. Each workflow uses the connected
tool schemas, preferring typed filters where available and retaining legacy call
arguments for older servers. A returned CRM ID is a stored reference, not live
CRM data.

Scorecard analysis needs the server's scorecard read tools. If they are absent,
the skill explains the missing capability and can analyze supplied evidence;
it does not generate new results or start an agent as a substitute. This workflow
awaits backend deployment and authenticated client validation before release.

## Maintain and extend

Add a workflow at `plugins/airspeed/skills/<workflow-name>/SKILL.md`. Keep its
instructions provider-neutral and use real MCP tool names and parameters. Add a
realistic case to `tests/cases.json`, then run it in both clients. Keep
platform-specific changes in the two small manifests.

```sh
python3 scripts/package.py --dry-run
python3 scripts/package.py
claude plugin validate plugins/airspeed --strict
```

The first command validates without creating an archive. The second writes
`dist/airspeed-<version>.zip`. The same archive carries both supported manifests
and the same skill files. It excludes this repository's release documentation,
tests, scripts, and development files.

Update both manifest versions together. The packaging check rejects divergent
metadata. Follow [the release process](docs/release.md) for client checks,
submission, and version rollout.

## Release status

This is an unpublished release candidate. Local package validation is separate
from authenticated client testing and marketplace approval. Listing review, a
dedicated reviewer account, and submission access are still required.
The scorecard behavior cases and canonical call-filter path remain pending until
their backend tools are deployed; metadata validation does not exercise them.

The source is published without an open-source license. Copyright 2026 Airspeed.
All rights reserved. Airspeed retains its branding and trademark rights.

The packaged logo is Airspeed's
[public webclip icon](https://www.goairspeed.com/images/webclip.png). Using it here does
not grant trademark or redistribution rights to others. Support and setup help:
[Airspeed documentation](https://docs.goairspeed.com/).
