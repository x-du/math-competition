# Add team column and teams.csv for contests with team information

**Goal:** When a contest results table (e.g. `results.csv`) does **not** have a `team` column but the source data includes team information (e.g. student name followed by team in parentheses like `Alexander Wang (LV Fire)`), add the team column to the results table and create/update the corresponding `teams.csv` with full team metadata.

**Input:** You will be given:
1. The path to an existing results table (e.g. `database/contests/hmmt-feb/year=2026/results.csv`)
2. The source result data as text (e.g. copied from a webpage or PDF) that includes team names, typically in the format: `Student Name (Team Name)`

---

## 1. Check if the table already has a team column

- Read the results file at `database/contests/<contest_folder>/year=<year>/results.csv`.
- If it already has a **`team`** column, **skip** adding one (you may still need to sync **`team_id`** with section 4 if results were updated).
- If it has only legacy **`team_name`**, rename that column to **`team`** and continue; use **`team`** everywhere, not `team_name`.
- If it has **no** team column, proceed with §2–§4.

---

## 2. Extract team information from the source data

- The source data often lists results as: `Student Name (Team Name)` — e.g. `Alexander Wang (LV Fire)`, `Bryan Sicheng Guo (San Diego A1)`.
- Parse each line to extract:
  - **Student name** (before the parentheses)
  - **Team name** (inside the parentheses)
- Match each student name to the corresponding row in the existing `results.csv` (by `student_name` or `student_id`).
- If a student appears without a team in parentheses (e.g. individual competitor), you may leave `team` blank or use a placeholder like `Individuals`.

---

## 3. Add the team column to the results table

- Add a new column **`team`** to the results CSV (use **`team`**, not `team_name`).
- After `team`, include **`team_id`** when rosters are tracked in `teams.csv` (see section 4). **Column order:** `student_id`, `student_name`, `team`, `team_id`, then `year`, `rank`, scores, etc.
- Fill each row with the team name extracted from the source data for that student.
- Preserve all existing columns and data; only insert the new column(s) in that order and their values.

**Example:** For `database/contests/hmmt-feb/year=2026/results.csv`:

| student_id | student_name      | team          | team_id | year | rank | total_score | ... |
|------------|-------------------|---------------|---------|------|------|-------------|-----|
| 1          | Alexander Wang    | LV Fire       | 7       | 2026 | 1    | 112.14      | ... |
| 2          | Bryan Sicheng Guo | San Diego A1  | 12      | 2026 | 2    | 109.92      | ... |

---

## 4. Create or update teams.csv

- **One `teams.csv` per competition bundle per year** — at the **composite** `-teams` path for that event, **not** under subject-only folders.
- **Do not** create `database/contests/<subject>-teams/…` for subject rounds (e.g. no `cmimc-algebra-teams`, no `hmmt-feb-algebra-number-theory-teams`). Subject directories hold **`results.csv` only**; rosters live in the shared teams file below.

**Where to write `teams.csv`**

| If you are editing results under … | Create/update `teams.csv` at … |
|-----------------------------------|--------------------------------|
| `cmimc-algebra`, `cmimc-geometry`, `cmimc-comb`, or `cmimc` | `database/contests/cmimc-teams/year=<year>/teams.csv` |
| `hmmt-feb-algebra-number-theory`, `hmmt-feb-geometry`, `hmmt-feb-combo`, or `hmmt-feb` | `database/contests/hmmt-feb-teams/year=<year>/teams.csv` |
| Any other single-folder contest `<slug>` | `database/contests/<slug>-teams/year=<year>/teams.csv` |

- Merge team names and student lists across **all** rounds for that event/year that share the same team labels so **`team_id` is consistent** in every subject and overall `results.csv`.

**Schema:** `team_id`, `team`, `student_ids`, `state`

### 4.1 team_id

- Integer identifier unique within this contest/year (within that composite `teams.csv`).
- If `teams.csv` already exists, reuse existing `team_id` for matching **`team`** strings; otherwise assign the next available integer (1, 2, 3, …).

### 4.2 team

- The team name as it appears in the source data (e.g. `LV Fire`, `San Diego A1`, `PEA Chestnuts`).

### 4.3 student_ids

- Pipe-separated list of `student_id` values for all students on that team for this contest/year, across **all** relevant result files (overall + subject rounds) for that event.
- Use the `student_id` from the corresponding `results.csv` rows for each student on that team.

### 4.4 state

- US state (or region) for the team, if known.
- Infer from: team name (e.g. "Texas Momentum A" → TX, "Florida Alligators" → FL), school name, or student records in `database/students/students.csv`.
- Leave blank if unknown.

---

## 5. Student lookup and new students

- **Student registry:** `database/students/students.csv`  
  Columns: `student_id`, `student_name`, `state`, `team_ids`, `alias`, `gender`, `grade_in_2026`
- Match students by **(name, state)** when possible. Students with the same name but different states are different people.
- If a student from the source is not in `results.csv` yet, add them first (following the conventions in `prompts/add-contest-results.md`), then include them in the team.

---

## 6. After updating

- Run from repo root:  
  `python scripts/build_search_data.py`  
  so that `docs/data.json` reflects the changes.

---

## Summary

1. Check if `results.csv` has a `team` column; if yes, stop.
2. Parse source data for `Student Name (Team Name)` and match to existing results rows.
3. Add **`team`** (and **`team_id`** when using rosters) to `results.csv` immediately after `student_name`, consistent with the composite `teams.csv` for that event/year.
4. Create/update **only** the composite teams path — e.g. `cmimc-teams` or `hmmt-feb-teams`, **never** a subject-level folder like `cmimc-algebra-teams`. Columns: `team_id`, `team`, `student_ids`, `state`.
5. Rebuild search data (`python scripts/build_search_data.py`).
