---
name: add-contest-results
description: >-
  Adds contest results from pasted text (webpage, PDF, or spreadsheet) into
  database/contests, resolves student_id from students.csv, and creates new
  student rows when needed. Use when the user asks to add contest results,
  import a contest year, or load rankings/awards into results.csv.
argument-hint: "<contest> <year>"
---

# Add contest results

**Input:** Contest results as text. Treat that text as the source of truth for names, awards, ranks, and scores.

## Layout

- Contest folders live under `database/contests/<folder>/year=<year>/results.csv`.
- Match **folder name** and **column schema** to an existing contest of the same type.
- If the contest is new, add a row to `database/contests/contests.csv` using that file’s existing columns (`folder_name`, `contest_name`, `contest_name_long`, `description`, `website`, `mcp_tier`, `mcp_weight`, `mcp_mode`, `rank_col`). Copy MCP fields from the closest similar contest.

Typical schemas (always include `student_id` and `student_name`):

| Style | Extra columns | Example |
| --- | --- | --- |
| Awards | `state`, `school`, `award`, `mcp_rank` | `jmo/year=2025/results.csv` |
| Place / site / team | `place`, `site`, `team`, … | `arml/year=2025/results.csv` |
| Rank / score | `team`, `team_id`, `year`, `rank`, `score` | `cmimc-algebra/year=2025/results.csv` |
| Rankings with grade | `state`, `year`, `rank`, `grade` | `mathcounts-national-rank/year=2025/results.csv` |

## Student lookup

Registry: `database/students/students.csv`  
Columns, in order: `student_id`, `student_name`, `state`, `alias`, `gender`, `grade_in_2026`

- Match by **(student_name, state)**. Same name + different state = different students.
- Match names case-insensitively, but write the canonical `student_name` from `students.csv` into results.
- `alias` is pipe-separated. If the source name matches an alias, use that row’s `student_id` and `student_name`.
- If state is missing in the source, use team/site/school when it clearly implies a state; otherwise leave state blank and still match on (name, state).

## New students

If no (name, state) match:

1. Assign `student_id` = max existing id + 1.
2. **Append** a 6-field row (5 commas, no trailing comma). Example: `7080,Ashita Thakkar,California,,,`
3. Leave `alias`, `gender`, and `grade_in_2026` blank unless known.

Then use that `student_id` and `student_name` in `results.csv`.

## Teams

If the source includes teams:

- Prefer the **add-team-column-and-teams** skill when `results.csv` has no `team` column yet.
- Prefer the **sync-contest-teams** skill when `results.csv` already has `team` / `team_name`.
- Write rosters only at the **composite** path `database/contests/<event>-teams/year=<year>/teams.csv` (e.g. `cmimc-teams`, not `cmimc-algebra-teams`).
- Schema is usually `team_id`, `team`, `student_ids`, `state`. `student_ids` is pipe-separated.

There is no global `database/students/teams.csv`.

## IMO, RMM, and EGMO

These international olympiads use **two** files per year. Copy schema from the latest existing year of that contest. Do not add `scripts/fetch_imo_official_scores.py`, `scripts/fetch_rmm_official_scores.py`, or `scripts/import_imo_results.py`. Temporary code is fine; delete it after.

| File | Role |
| --- | --- |
| `official-scores.csv` | Full official scoreboard (the website prefers this when present) |
| `results.csv` | Only students **already** in `students.csv` |

Do **not** create a new `students.csv` row for every official contestant. Match the official name against `student_name` and `alias` (not US state). Country is not a US state. If a tracked student’s `state` is blank, you may set it to the official country name.

**`us_rank` and `mcp_rank`:** fill only for Country Code `USA`, ranked by total among matched US students (ties: official rank). Leave both blank for everyone else.

- **IMO** results: `student_id`, `student_name`, `country`, `award`, `rank`, `us_rank`, `P1`–`P6`, `total`, `mcp_rank`. Awards like `Gold medal`. Source: `https://www.imo-official.org/year_individual_r.aspx` (western name order). Official CSV includes `Contestant Code`.
- **RMM** results: `student_id`, `student_name`, `country`, `year`, `us_rank`, `international_rank`, `total_score`, `award`, `mcp_rank`. Awards in results are `Gold` / `Silver` / `Bronze` (no “medal”). Official names are often family-name-first (`Reddy Liam`); match reversed given/family or aliases. Onsite individual table only — skip online contestants. Source: `https://rmms.lbi.ro/rmm{year}/index.php?id=results_math` (TLS on that host may be expired; still fetch public results).
- **EGMO** results match the IMO column set. Combine given + family name when matching.

## After updating

From repo root:

```bash
python scripts/build_search_data.py
python scripts/check_all.py
```

Fix any `check_csv_integrity.py` field-count errors before finishing.
