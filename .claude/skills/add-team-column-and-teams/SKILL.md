---
name: add-team-column-and-teams
description: >-
  Adds a team column to an existing results.csv from source text such as
  "Student Name (Team Name)", then creates or updates the composite teams.csv
  and team_id values. Use when results lack a team column but the source lists
  teams, or when the user asks to add team names to a contest year.
argument-hint: "<contest> <year>"
---

# Add team column and teams.csv

**Input:** Path to an existing `results.csv`, plus source text that includes team names (often `Student Name (Team Name)`).

## 1. Check the results file

- If it already has **`team`**, do not add another column. Use **sync-contest-teams** if `team_id` still needs aligning.
- If it has only legacy **`team_name`**, rename that column to **`team`**.
- If it has no team column, continue.

## 2. Extract teams from the source

Parse `Student Name (Team Name)` (e.g. `Alexander Wang (LV Fire)`). Match each name to a `results.csv` row by `student_name` or `student_id`. Leave `team` blank (or `Individuals`) when the source has no team.

If a source student is missing from `results.csv`, add them first with **add-contest-results**, then include them on the team.

## 3. Add columns

Insert **`team`** then **`team_id`** immediately after `student_name`. Preserve every other column.

Example order: `student_id`, `student_name`, `team`, `team_id`, then `year`, `rank`, scores, …

## 4. Composite teams.csv only

Write **one** `teams.csv` per event/year — never a subject-only `-teams` folder.

| Results under … | `teams.csv` at … |
| --- | --- |
| `cmimc`, `cmimc-algebra`, `cmimc-geometry`, `cmimc-comb` | `database/contests/cmimc-teams/year=<year>/teams.csv` |
| `hmmt-feb` or any `hmmt-feb-*` subject | `database/contests/hmmt-feb-teams/year=<year>/teams.csv` |
| Other single-folder contest `<slug>` | `database/contests/<slug>-teams/year=<year>/teams.csv` |

Merge the same team labels across all rounds for that event/year so `team_id` is consistent.

**Schema:** `team_id`, `team`, `student_ids`, `state`

- **`team_id`:** unique within this contest/year. Reuse the existing id when `team` matches; otherwise next integer.
- **`team`:** name as in the source.
- **`student_ids`:** pipe-separated ids from all relevant result files for that event/year.
- **`state`:** from team name, school, or `students.csv`. Leave blank if unknown.

## After updating

```bash
python scripts/build_search_data.py
```
