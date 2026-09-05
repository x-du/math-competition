---
name: sync-contest-teams
description: >-
  Creates or refreshes contest teams.csv files and aligns team_id in
  results.csv from team or team_name columns. Use after adding or editing
  results that include teams, when teams.csv is missing, or when the user
  asks to sync contest teams.
argument-hint: "<contest> <year>"
---

# Sync contest teams

Create or refresh `database/contests/<contest>-teams/year=<year>/teams.csv` and align **`team_id`** on each `results.csv` row.

Do not add or commit `scripts/sync_contest_teams.py`. Create temporary code for this task, run it, then delete it. Do not leave helper scripts in the repo.

If `results.csv` has no `team` or `team_name` column, stop. To add a team column from raw source text first, use **add-team-column-and-teams**.

## Generic contest

1. Read `database/contests/<contest>/year=<year>/results.csv`.
2. Team column is `team_name` if present, else `team`.
3. Reuse `team_id` from an existing `<contest>-teams/.../teams.csv` when the team name matches. Otherwise assign new numeric ids (keep existing id padding).
4. Write `student_ids` as pipe-separated, sorted numerically.
5. Insert or update `team_id` in `results.csv` immediately after the team column.
6. Composite path only (e.g. `cmimc-teams`, not `cmimc-algebra-teams`). Schema is usually `team_id`, `team`, `student_ids`, `state`.

## BMT

When the user asks to sync BMT teams, rebuild `bmt-teams` from **all five** result files for that year: `bmt`, `bmt-algebra`, `bmt-calculus`, `bmt-discrete`, `bmt-geometry`. Do not treat those subject folders as separate generic contests.

`team_id` is the leading digit prefix of `bmt_student_id` (e.g. `220A` → `220`). Schema: `team_id`, `team_name`, `student_ids`, `bmt_student_ids`, `school`, `state`.

## After updating

Preserve existing CSV line endings (many contest files are CRLF).

```bash
python scripts/build_search_data.py
```

`scripts/check_student_ids.py` treats **`pumac-b-teams`** like BMT: a student counts as “in results” if they appear on `pumac-b` or any Division B subject test (`pumac-b-algebra`, `pumac-b-combinator`, `pumac-b-geometry`, `pumac-b-number-theory`) for that year.
