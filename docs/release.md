# Release and maintain Airspeed plugins

## Shared source

Maintain one source tree and one version for the ChatGPT and Claude packages.
Skills and `.mcp.json` are shared. The two compatibility manifests contain only
identity, discovery, and component metadata. `scripts/package.py` checks that
their shared fields agree and produces ZIPs containing only runtime files.
The ChatGPT test package derives `.app.json` from a registered app ID supplied at
build time. It does not change the shared source or the portable Claude package.

OpenAI supports `.codex-plugin/plugin.json`; Claude uses
`.claude-plugin/plugin.json`. OpenAI also supports a newer portable root manifest.
We retain the small supported compatibility files for this release rather than
maintain a third copy. Revisit that choice if a platform changes its requirements.

## Local checks

1. Run `python3 scripts/package.py --dry-run`.
   Run `python3 -m unittest discover -s tests -p 'test_*.py'` for the upload formats.
2. Run `claude plugin validate plugins/airspeed --strict` with a recent Claude
   CLI. This validates the package; it does not test authentication or behavior.
3. When available, also run the plugin-creator `validate_plugin.py` on
   `plugins/airspeed` and skill-creator `quick_validate.py` on each skill folder.
4. Run the cases in `tests/cases.json` in fresh ChatGPT and Claude sessions using
   dedicated synthetic records. Do not publish production transcripts or tokens.
5. Run `python3 scripts/package.py`; record its filename and SHA-256.

Record client version/surface, plugin version, test date, test user role, cases
passed, and any issue for each client. Keep reviewer credentials outside this
repository. Any case not run remains unverified.

## MCP compatibility gate

Skills ship against deployed capabilities, not just merged backend code. For
each new workflow:

1. Link its backend dependencies in the skill PR. Keep it out of release branches
   until those changes are merged and deployed.
2. Refresh the intended client's connection and inspect the live tool names and
   input/output schemas. Use only supported arguments; a missing tool is a failed
   prerequisite, not an empty result.
3. Run the synthetic workflow cases in the intended clients, first against the
   deployed staging connector and then production. Keep any staging endpoint
   override local. Record the backend release, discovered schema, plugin commit,
   and results together in the release evidence.
4. Merge the skill only after those checks pass, then include it in the next
   version. Package and backend version numbers do not need to match.

The first release includes only account-brief. The separate
[scorecard skill PR](https://github.com/GlyphicAI/airspeed-plugins/pull/2) depends on
[scorecard reads](https://github.com/GlyphicAI/maverick-backend/pull/8137) and
[calls adapters](https://github.com/GlyphicAI/maverick-backend/pull/8160). Its gate
must discover `list_scorecards`, `get_scorecard`, `list_scorecard_results`, and
`get_scorecard_report`, and validate the call arguments used by account-brief.
Keep that PR and its backend links together until its gate passes.

## Install for testing

### Claude

The repository includes a Claude marketplace catalog. Once the repository is
available to the installer:

```sh
claude plugin marketplace add GlyphicAI/airspeed-plugins
claude plugin install airspeed@airspeed-plugins
```

For a local Claude Code package check:

```sh
claude --plugin-dir ./plugins/airspeed
```

Authenticate the Airspeed server through the client's MCP connection flow and
invoke `/airspeed:account-brief`. Also test in the intended Claude desktop or web
plugin surface; a CLI pass does not establish compatibility there. Use the
current Claude plugin upload/install flow and confirm both the skill and remote
MCP are available. Account and workspace policy can restrict installations.

### ChatGPT

Enable Developer mode where available, register the remote MCP in the Plugins
Directory, and authenticate it using the dedicated demo account. Build the full
plugin with the registered app ID:

```sh
python3 scripts/package.py --chatgpt-app-id asdk_app_YOUR_REGISTERED_APP_ID
```

Upload `dist/airspeed-chatgpt-<version>.zip` in **New Plugin**, then start a fresh
chat. Use the underlying `asdk_app_...` ID, not a URL's `plugin_asdk_app_...` route
identifier. The package references the registered connection through `.app.json`
and omits `.mcp.json` and the Claude manifest to avoid duplicate registration.
Keep the app mapping out of shared source. Other workspaces may need a different
registered app ID and a newly built test package.

For the submission portal's **Skills section**, run
`python3 scripts/package.py --skill account-brief` and upload
`dist/airspeed-account-brief-<version>-skill.zip`. This archive is only a skill;
it cannot be installed through ChatGPT's New Plugin uploader.

For the public submission, choose **With MCP**, enter the production endpoint,
and include the skills in the same draft. Do not submit as skills-only or assume
an existing registered MCP ID can stand in for the remote server submission.

## Before submission

- Source: https://github.com/GlyphicAI/airspeed-plugins. The package is proprietary
  and has no open-source license. Use the Airspeed company publishing accounts
  and designated maintainer for submissions.
- Review the [listing draft](listing.md), which includes public links and starter
  prompts. Supply the approved logo and final listing copy to each portal.
- Provide a dedicated reviewer account with representative synthetic calls and
  usable sign-in instructions. Verify OAuth from a clean browser session.
- Check the entire server tool list and schemas, including tools this skill does
  not use. Confirm read/write annotations and write confirmations describe the
  actual behavior. A read-only skill does not make a server read-only.
- For OpenAI, complete publisher identity verification and Apps Management
  permissions. Serve its domain-verification challenge as instructed by the
  portal. Verify OAuth discovery, scopes, and any required UserInfo claims.
- Complete every submission scan and attach repeatable prompts with expected
  outcomes. Record the exact ZIP hash and server release tested.

## Submit and release

1. After local and client checks pass, commit the release sources and merge the
   release PR. Check out that exact commit, rebuild, and record each archive's
   SHA-256. Create an annotated `v<version>` tag on that commit and attach the
   portable ZIP, skill ZIP, and checksums to its GitHub release. A workspace-bound
   ChatGPT test ZIP is not the shared public release artifact. Do not tag a
   package whose client tests are still pending.
2. Create the OpenAI **With MCP** draft, attach this release's skills, and complete
   its authentication, listing, test, and review fields.
3. Create the Claude plugin submission with the public source/package and its
   requested listing and review information. A connector directory listing is a
   separate submission; it does not publish the bundled workflow.
4. Record both submission URLs, owner, version, and status in the team's
   release tracker. Keep submitted, approved, published, and installed distinct.
5. After approval, publish the accepted releases and capture their installation
   links. Update Airspeed Settings and the customer guide with those verified
   links. Do not promise a marketplace installation link before publication.
6. Test installation from each published listing with a fresh user account.

## Updates and recovery

Edit shared skills once. Add or adjust behavior cases, bump both manifest
versions, rerun checks and both client flows, and submit the new version where
required. A remote MCP tool change can require a separate catalog refresh or
review; do not assume existing installations discover it immediately.

Retain the previous source tag and release ZIP. For a faulty skill release,
disable or withdraw the listing if the platform supports it, correct or revert
the source, then submit a higher version. Do not overwrite a published artifact.
Document any server change separately so package rollback is not confused with
server rollback.

## Sources

Recheck platform requirements before each public submission.

- [OpenAI package format](https://developers.openai.com/plugins/build/plugins)
- [OpenAI remote MCP and Claude conversion](https://developers.openai.com/plugins/guides/submit-claude-plugin)
- [OpenAI submission](https://developers.openai.com/plugins/deploy/submission)
- [OpenAI testing](https://developers.openai.com/plugins/deploy/connect-chatgpt)
- [Claude plugin schema](https://code.claude.com/docs/en/plugins-reference)
- [Claude plugin submission](https://claude.com/docs/plugins/submit)
- [Airspeed customer guide](https://docs.goairspeed.com/articles/1087586625-airspeed-mcp-server)
