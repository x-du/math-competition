# Sync contest `teams.csv` and `team_id` in results

**Goal:** Use **`scripts/sync_contest_teams.py`** to create or refresh `database/contests/<contest>-teams/year=<year>/teams.csv`, align **`team_id`** on each row of `database/contests/<contest>/year=<year>/results.csv`, and (for BMT) rebuild **`bmt-teams`** from all five division result files—without hand-editing IDs when the data already lists team names or official team ids.

**Script:** `scripts/sync_contest_teams.py` (run from repository root).

---

## When to use this prompt

- After adding or editing **`results.csv`** for a contest year that has **team** information.
- When **`teams.csv`** is missing but **`results.csv`** has a **`team_name`** or **`team`** column (the script creates **`database/contests/<slug>-teams/year=<year>/teams.csv`**).
- When **`teams.csv`** already exists and you need **`team_id`** filled or kept stable by **team name** matching.

**Skip the script** for contests whose **`results.csv`** has **no** **`team_name`** or **`team`** column; the script exits early for those folders (see stderr).

---

## Commands

From the repo root:

| Task | Command |
|------|---------|
| **BMT only** — rebuild `bmt-teams` from General + Algebra + Calculus + Discrete + Geometry | `python scripts/sync_contest_teams.py bmt <year>` |
| Same, legacy shorthand | `python scripts/sync_contest_teams.py <year>` *(single argument: digits only)* |
| **One contest folder** (e.g. `cmimc`, `hmmt-feb`, `mmaths`) | `python scripts/sync_contest_teams.py sync <contest> <year>` |
| **Whole year** — BMT aggregate if `bmt/year=<year>/results.csv` exists, then sync every other contest under `database/contests/` that has that year’s `results.csv` | `python scripts/sync_contest_teams.py sync-all <year>` |

Examples:

```bash
python scripts/sync_contest_teams.py bmt 2024
python scripts/sync_contest_teams.py sync cmimc 2022
python scripts/sync_contest_teams.py sync-all 2025
```

---

## Behavior (summary)

1. **Generic contests** (`sync`): The team column in **`results.csv`** may be named **`team`** or **`team_name`**—either is accepted. If **both** columns exist on the same file, **`team_name`** is used. Builds **normalized team name → `team_id`**: reuse ids from an existing **`<contest>-teams/.../teams.csv`** when the **team name** matches; otherwise assign new numeric ids (padding matches existing ids when present). Writes **`student_ids`** as pipe-separated, sorted numerically. Inserts or updates a **`team_id`** column in **`results.csv`** immediately **after** that team column.

2. **BMT** (`bmt` or legacy year-only): Aggregates rosters from **`bmt`**, **`bmt-algebra`**, **`bmt-calculus`**, **`bmt-discrete`**, **`bmt-geometry`** into **`bmt-teams`** with **`bmt_student_ids`**, **`school`**, etc. Full manual workflow and standings rules remain in **`prompts/add-bmt-teams.md`**.

3. **`sync-all`**: Runs the BMT aggregate when appropriate, then runs generic sync on other contest directories. It **does not** treat **`bmt-algebra`** (and the other BMT divisions) as separate generic contests—those rows are included only via the BMT aggregate.

---

## After updating

Run:

```bash
python scripts/build_search_data.py
```

so **`docs/data.json`** stays in sync.

**Roster validation:** `scripts/check_student_ids.py` treats **`pumac-b-teams`** like **BMT**: a student counts as “in results” if they appear on **`pumac-b`** composite **`results.csv`** or on any Division B subject test (**`pumac-b-algebra`**, **`pumac-b-combinator`**, **`pumac-b-geometry`**, **`pumac-b-number-theory`**) for that year—because composite Division B lists fewer students than the subject rounds.

---

## Related prompts

- **`prompts/add-bmt-teams.md`** — BMT-specific team IDs from **`bmt_student_id`**, merging standings, and **`bmt-teams`** columns.
- **`prompts/add-team-column-and-teams.md`** — Adding a **`team`** column from raw source text when **`results.csv`** did not have one yet.
