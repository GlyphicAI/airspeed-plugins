# Discovery overlay notes

Read the live tool schemas first; availability depends on the server release. These
notes describe the read shapes this workflow relies on and the limits that follow.

## Tags and calls

- `list_call_tags` takes no arguments and returns `id`, `name`, `description` and
  `group` for each tag. Outcome tags usually sit in their own group, apart from
  call-type tags. Descriptions are the organisation's definitions and may contain
  typos or point at other tags; treat them as definitions to quote, not rules to
  repair.
- `list_calls` `tag_ids` is an any-of match. Query one outcome tag at a time. Filters
  combine with `start_time_from`, `start_time_to` and `participant_email`. The
  `filters` object cannot be mixed with the flat arguments and has no dates.
- Each returned call lists its `tags`, so the Discovery tag and the outcome tag can
  be verified on the result. Stored CRM IDs are references, not live CRM data.

## Scorecard result shapes

| Read | One request returns | Notes |
| --- | --- | --- |
| `list_scorecard_results` with `filters.call_ids` (one ID) | One row per scorecard and evaluated person for that call | Has `call_id`, per-skill `timestamp_in_seconds`, `max_score`, feedback and `skill_example` |
| `list_scorecard_results` with `filters.scorecard_ids` and `started_at` | Rows for one scorecard across readable people, newest first, paged by cursor | Joins by `call_context.call_id`; no per-skill timestamps and no `skill_example`; hidden calls have no `call_context` or feedback |
| `list_scorecard_results` with `filters.users` | One person's grouped history, at most 100 results per scorecard, no cursor | Not used for outcome joins; averages in it are all-time |
| `get_scorecard_report` | Team overview aggregates | No tag, call or date filter; different population from the sample |

## Interpreting values

- `total_score_percentage` is a 0 to 1 ratio persisted at scoring time. Do not
  recompute it from today's rubric.
- A skill `score` of `null` is unscored or not applicable, whether or not feedback
  text is present. A genuine score of 0 is a different state. Keep a separate count.
- `max_score` differs between skills (for example 5 for most and 2 for a next-step
  skill) and reflects the current rubric. There is no historical scale or version
  field. Compare a skill only against the same skill on the same scorecard and
  maximum. Do not add raw scores across skills, convert scales or call a difference
  an improvement across rubric changes.
- Removed or renamed skills can be absent from older results. Absence is not zero.
- A call can be scored for several people and several scorecards. Deduplicate by
  result ID, count unique calls separately from results, and treat the outcome as
  one call-level fact.

## Small samples

- With fewer than about five scored results in a group, show the individual scores
  or a distribution and avoid means, percentages and "wins by" language.
- Give every figure its denominator: calls in the group, results scored, results
  unscored. A difference in a skill with few scored results is a lead to check in
  the transcripts, not a finding.
- A pattern in this sample is an association. Outcome tags, scores and summaries are
  assessments; neither the tags nor the scores establish why a buyer agreed to or
  declined a next step.

## Tolerated failures

- If `list_scorecards` or `get_scorecard` errors, continue from names, IDs and
  `max_score` inside the result rows and say rubric meaning is unavailable.
- If a result read fails for one call, report that call as unread. Do not fill the
  gap or drop it silently.
- If `get_scorecard_report` is unavailable, omit the team context. It is optional.
- "Call not found" can mean missing, redacted or hidden. Do not guess which.
