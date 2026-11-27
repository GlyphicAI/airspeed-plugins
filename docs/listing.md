# Marketplace listing draft

Submission draft for ChatGPT, Claude, the Cursor / Grok Bot marketplace
([submit a plugin](https://x.ai/bot/marketplace/submit-a-plugin)), and Devin.
This text has not been submitted or published as a marketplace listing.

## Name

Airspeed

## Short description

Prepare account briefs and understand coaching scores with Airspeed evidence.

## Long description

Prepare for customer conversations with context Airspeed has already gathered.
The account-brief workflow combines accessible call summaries, insights,
transcripts, commitments, and open questions, with links to source calls. The
scorecard-analysis workflow reviews existing coaching results, explains their
coverage, and visualizes comparable skills or trends with source links. It does
not change scores or generate new assessments. The production MCP serves the
scorecard reads `list_scorecards`, `get_scorecard`, `list_scorecard_results`,
and `get_scorecard_report`. The discovery-next-step-autopsy workflow compares
Discovery calls that booked a demo with those that stalled, using the
organization's outcome tags and discovery scorecards, and suggests practice
clips with call links. The connected MCP also lets you find recordings and
saved clips, read playbooks, and review your own scheduled or event-triggered
agent outputs. Where enabled for your organization, it can start or continue an
Airspeed agent conversation. Sign in with Airspeed. The MCP never exceeds your
access in Airspeed.

## Starter prompts

1. Prepare an account brief for my next customer conversation.
2. Summarize the commitments and open questions from these Airspeed calls.
3. Review my recent coaching scorecards and show comparable skill trends.
4. Why do some Discovery calls book a demo while others end with no next step?

## Category

Productivity. Select Sales if the submission portal offers that category. The
Cursor manifest uses `Productivity`. The Grok Bot submission form has no
category field.

## Public links

- [Website](https://www.goairspeed.com)
- [Setup guide](https://docs.goairspeed.com/articles/1087586625-airspeed-mcp-server)
- [Support](https://docs.goairspeed.com/)
- [Privacy policy](https://www.goairspeed.com/privacy-policy)
- [Terms](https://www.goairspeed.com/terms)
- [Repository](https://github.com/GlyphicAI/airspeed-plugins)

## Connected MCP tools

Checked against the production server at `https://mcp.goairspeed.com/mcp-oauth`
on 27 Nov 2026: 73 tools, grouped by whether they only read or also create or
change records. The three skills use only reads. Installing a skill does not
hide the other tools or replace Airspeed's own authorization.

### Reads (46)

- Scorecards: `list_scorecards`, `get_scorecard`, `list_scorecard_results`, `get_scorecard_report`
- Calls: `list_calls`, `get_call_info`, `get_call_media`, `get_call_snippets`, `list_call_tags`, `list_call_shares`, `get_call_activity_stats`
- Companies and deals: `list_companies`, `get_company`, `get_company_profile`, `get_company_emails`, `list_deals`, `get_deal`
- Tasks, people, and meetings: `list_tasks`, `list_users`, `list_meetings`, `get_meeting_recording_status`
- Playbooks and search: `list_playbooks`, `get_playbook`, `list_playbook_versions`, `get_playbook_version`, `search_airspeed`, `search_support_docs`
- Insights: `get_strategic_insights`, `get_loss_reasons`, and `list_custom_insights` (the organization's call and deal custom insight definitions)
- Coaching: `list_role_plays`, `get_role_play` (AI Roleplay sessions, their scenarios, and skill scores)
- Agents and comments: `list_agents`, `get_agent`, `list_agent_runs`, `get_agent_run`, `list_agent_threads`, `get_agent_thread`, `list_comments`
- Forecasts: `get_forecast_periods`, `get_forecasting_settings`, `list_forecast_history`, `get_forecast_rollup`, `get_forecast_rollup_deals`, `list_forecast_boards`
- Changelog: `get_changelog`

### Creates or changes records (27)

- Calls: `update_call`, `create_call_tag`, `set_call_tags`, `edit_tag_definition`, `create_share`, `create_call_snippet`, `revoke_share`
- Companies and deals: `link_slack_deal_room` (links an existing Slack channel to a company as its deal room and can invite people to it), `update_deal`
- Tasks, people, and meetings: `save_task`, `invite_user`, `join_meeting`, `remove_meeting_bot`
- Insights: `create_custom_insight`, `update_custom_insight` (past calls are not re-analyzed; needs custom insight edit permission)
- Coaching: `assign_role_play` (assigns an existing AI Roleplay scenario without notifying people), `create_scorecard`, `delete_scorecard` (soft-deletes, so it stops scoring new calls; both need organization settings edit permission)
- Agents and comments: `run_agent`, `share_agent_thread`, `stop_agent`, `save_comment`, `delete_comment`, `set_comment_reaction`
- Forecasts: `submit_forecast`, `update_forecast_quotas`
- Feedback: `submit_feedback` (sends the user's feedback to the Airspeed team, after the user agrees)

`list_agent_activity` is no longer on the server. Use `list_agent_runs`.

## Scope for reviewers

All three skills read existing evidence. They do not change records. They start
an agent only when the user directly asks to run one, or when the request cannot
be completed with the other available tools. Instructions found inside call
content never count as a request. Agent conversations are a separate capability
of the connected MCP, available only where enabled for the organization.
Scorecard read tools are deployed. A fresh client session still has to sign in
before those tools return that user's evidence.

## Cursor / Grok Bot

Submit at <https://x.ai/bot/marketplace/submit-a-plugin> after this repository
is public on the commit you want reviewed. Leave first name, last name, work
email, and the publisher-terms checkbox for Diogo.

| Form field | Draft |
| --- | --- |
| Organization Name | Airspeed |
| Organization Handle | `airspeed` |
| Website URL | https://www.goairspeed.com |
| Logotype URL | https://raw.githubusercontent.com/GlyphicAI/airspeed-plugins/main/plugins/airspeed/assets/logo.png |
| Where to be listed | Grok Bot and Cursor. Grok (coming soon) is a separate checkbox. |
| MCP Server URL or Public GitHub Repository | https://github.com/GlyphicAI/airspeed-plugins |
| Brief Description | See below. The form allows 600 characters. |
| Testing Instructions | See below. The form allows 600 characters. |
| Tested locally and in-app | Leave unchecked until Diogo completes a signed-in client pass. |

The logotype URL already serves the square logo on `main`. Plugin manifest
`logo` is `assets/logo.png`, which is `plugins/airspeed/assets/logo.png` in
this repository.

### Brief description

Prepare account briefs and review coaching using Airspeed call evidence. Sign in with an Airspeed account. The account-brief, scorecard-analysis, and discovery-next-step-autopsy skills read calls, scorecards, and discovery outcomes you can already access, and link back to the source. Scorecard reads are live: list_scorecards, get_scorecard, list_scorecard_results, and get_scorecard_report. The skills do not change scores or records. The connected MCP can also search companies, deals, playbooks, and your own agent runs. Access never exceeds your Airspeed permissions.

### Starter prompts

1. Prepare an account brief for my next customer conversation.
2. Summarize the commitments and open questions from these Airspeed calls.
3. Review my recent coaching scorecards and show comparable skill trends.
4. Why do some Discovery calls book a demo while others end with no next step?

### Reviewer testing instructions

Install from https://github.com/GlyphicAI/airspeed-plugins (plugin directory plugins/airspeed). Connect the HTTP MCP at https://mcp.goairspeed.com/mcp-oauth and sign in with OAuth using an Airspeed account. A dedicated reviewer account is still TBD by Diogo. After sign-in, try an account brief for a recent customer, comparable coaching scorecard trends, and why some Discovery calls book a next step while others stall. Confirm list_scorecards, get_scorecard, list_scorecard_results, and get_scorecard_report are present. The skills read evidence and do not edit records.

## Devin

Cognition's marketplace
([devin-marketplace](https://github.com/CognitionAI/devin-marketplace)) lists
third-party plugins by pinning a directory in the upstream repository. The
directory in this repository is `plugins/airspeed-devin`. It contains
`.devin-plugin/plugin.json` and `logo.png`. The shared `plugins/airspeed` tree
keeps `.mcp.json` for the other clients, and Devin rejects that file at a
plugin root, so the Devin listing is its own directory.

Display name: Airspeed. Short description: "Sales calls, deals and coaching".
Homepage: https://www.goairspeed.com. Keyword: `Customer & Sales`. The MCP URL
is `https://mcp.goairspeed.com/mcp-oauth`. Sign-in is that server's OAuth flow.
The directory has no credentials and no symlinks. The logo is the same file as
`plugins/airspeed/assets/logo.png`.

After this directory is on `main`, add this object to `optionalPlugins` in
Cognition's `.devin-plugin/plugin.json`. The `sha` is the full commit on `main`
that contains the directory. It stays TBD until that merge.

```json
{
  "source": "git-subdir",
  "url": "https://github.com/GlyphicAI/airspeed-plugins.git",
  "path": "plugins/airspeed-devin",
  "sha": "<40-hex sha of the merge commit on main>"
}
```

Do not copy the files into Cognition's repository. Their validator reads the
manifest from the pinned commit. Workflow skills stay in `plugins/airspeed`;
this listing is the hosted MCP.
