# Interpret native scorecard reads

Read the live schemas first; availability depends on backend deployment. The
reduced interface wraps existing app reads and has no scorecard write tools.

- `list_scorecards`: optional `filters.enabled_only`.
- `get_scorecard`: an Airspeed `scorecard_id`, returning the current definition.
- `list_scorecard_results`: choose `filters.call_ids={any_of: [one_call_id]}` for per-call results,
  or `filters.users={mode: "self"}` / `{mode: "ids", ids: [one_id]}` for one-user
  history. History alone accepts `filters.scored_on={gte: "YYYY-MM-DD", lt:
  "YYYY-MM-DD"}`: inclusive start, exclusive end, based on native UTC day buckets.
- `get_scorecard_report`: native team overview, optional `filters.users` and
  `filters.view` (`everyone` or `my_team`), inside the app's overview entitlement.
  It has no date, scorecard-ID, revenue, include-section or pagination options.

History returns at most 100 results per scorecard, with no cursor. Do not invent
continuations or present the sample as an exhaustive period. Numeric history or
team aggregates may include scores whose call details are inaccessible; never
reconstruct those identities. Use returned call context and `get_call_info` only
when accessible, and cite returned links or explicit result IDs.

| Native value | Interpretation |
| --- | --- |
| `total_score_percentage`, history `score_card_user_average` / `score_card_company_average`, team `average_overall_score` | Ratios from 0 to 1. History's user/company averages are all-time, even when its result list has a date filter. |
| Skill `average_score_pct` | Already 0–100; do not multiply again. History skill metrics use its latest-100 filtered sample. |
| Team `score_percentage_change` | Percentage-point change, not relative percent change. |
| Team `past_overall_scores` | Native downsampled values, at most 32 points; not individually dated evaluations. |
| Team `skill_average_scores` | Native bounded skill output, at most 100 skills; there is no skill cursor or completeness flag. |

Native `max_score` is the **current rubric maximum**, not a saved historical
scale. The interface has no historical-scale/version field. Do not divide an old
stored score by today's maximum to infer its historical percentage. Removed or
renamed skills can be absent from native results; absence does not mean zero.
Persisted overall percentages remain separate values and must not be recalculated
from today's rubric. Current-rubric report calculations do not prove that older
results used comparable scales.

Native metrics may contain a zero placeholder when no scored observations exist.
Distinguish that from an observed score of zero using the returned evidence and
counts; if the denominator is unavailable, label it unknown. Preserve missing,
pending, unavailable and N/A states. Show sample size, time basis and native scale
beside visuals, and separate incompatible rubrics rather than normalize them.
Revenue analysis and score corrections are outside these tools and this skill.
