# Interpret Airspeed scorecard reports

Read the live tool schema first: older deployments may not have these fields.
This reference describes the selected MCP report interface; it does not imply
that an unavailable tool has been deployed.

`get_scorecard_report` accepts a saved `scorecard_id`, a `view` (`user`, `team` or
`my_team`), typed `filters`, optional `include` sections, and page options.
`filters.users` uses `{mode: "self"}` or `{mode: "ids", ids: [...]}`.
`filters.score_date` uses strict `YYYY-MM-DD` boundaries, inclusive `gte` and
exclusive `lt`, based on the call's UTC date. Name sorting uses
`sort={field: "name", direction: "asc"|"desc"}`. Follow the returned cursor with
the same query to retrieve more users or skills.

| Returned value | Interpretation for a visual |
| --- | --- |
| User `user_average_all_time`, `organization_average_all_time` | Ratios from 0 to 1, explicitly all-time even when a date filter is supplied. Multiply by 100 only when labeling percentages. |
| User skill `average_score_pct` | Already a percentage from 0 to 100. Do not multiply it again. Skill metrics use a latest-100 filtered history sample; show `filtered_history_sample_count` and `history_sample_limit`. |
| `include=["skill_benchmark"]` | Each skill's all-time organization benchmark. Label its different time basis before comparing it to filtered metrics. |
| Team `average_overall_score` | A 0–1 ratio. `score_percentage_change` is a percentage-point change, not another score or a relative percent change. |
| Team `past_overall_scores` | Already downsampled by the app to at most 32 points. Preserve `trend_sampling` and `trend_sample_limit`; do not portray these points as individual dated evaluations. |
| Team `skill_average_scores` | At most 100 skills. If `skills_truncated` is true, use the user's report and follow its skill pages for the rest. |

Use `list_scorecard_results` for dated evaluations. Its typed filters support
result IDs, scorecard IDs, call IDs, users and score dates; the live schema gives
the exact field names. Sort by `score_date` and follow page cursors. Optional
`feedback` and `last_edit` sections provide explanation and correction context.
Do not reconstruct hidden call identities: authorized numeric cohort metrics
can include evaluations whose call details the current user cannot read.

Use `include=["examples"]` for scoped call examples. A missing example does not
make its aggregate zero. Return links only when provided and still accessible.

`include=["revenue"]` applies to team and my-team views. It uses current CRM
Opportunity access and the report date range on close dates. An absent amount
can mean no owner mapping; a failed or unavailable CRM section is not zero.
Amounts retain the app's currency convention without conversion, so do not
combine unlike currencies. `cache_refresh="scheduled"` means a refresh was
queued, not completed; disclose stale or incomplete data before correlating
revenue with coaching scores. This section can schedule the same cache refresh
as the app, even though it does not edit CRM records.

Prefer a dated-result trend for changes over time, skill bars for comparable
skill metrics, or a table for mixed time bases and units. Show cohort, date
window, sampling, denominator and units beside the visual. These reads do not
authorize rubric changes, result corrections, or coaching messages.
