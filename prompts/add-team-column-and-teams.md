# Add team column and teams.csv for contests with team information

**Goal:** When a contest results table (e.g. `results.csv`) does **not** have a `team` column but the source data includes team information (e.g. student name followed by team in parentheses like `Alexander Wang (LV Fire)`), add the team column to the results table and create/update the corresponding `teams.csv` with full team metadata.

**Input:** You will be given:
1. The path to an existing results table (e.g. `database/contests/hmmt-feb/year=2026/results.csv`)
2. The source result data as text (e.g. copied from a webpage or PDF) that includes team names, typically in the format: `Student Name (Team Name)`

---

## 1. Check if the table already has a team column

- Read the results file at `database/contests/<contest_folder>/year=<year>/results.csv`.
- If it already has a `team` or `team_name` column, **skip** this prompt.
- If it does **not** have a team column, proceed.

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

- Add a new column `team` (or `team_name`) to the results CSV.
- **Column order:** Place `team` **immediately after** `student_name` (before `year`, `rank`, scores, and any other columns).
- Fill each row with the team name extracted from the source data for that student.
- Preserve all existing columns and data; only insert the new column in that position and its values.

**Example:** For `database/contests/hmmt-feb/year=2026/results.csv`:

| student_id | student_name      | team          | year | rank | total_score | ... |
|------------|-------------------|---------------|------|------|-------------|-----|
| 1          | Alexander Wang    | LV Fire       | 2026 | 1    | 112.14      | ... |
| 2          | Bryan Sicheng Guo | San Diego A1  | 2026 | 2    | 109.92      | ... |

---

## 4. Create or update teams.csv

- Path: `database/contests/<contest_folder>-teams/year=<year>/teams.csv`
  - Example: `database/contests/hmmt-feb-teams/year=2026/teams.csv`
- Schema: `team_id`, `team_name`, `student_ids`, `state`

### 4.1 team_id

- Integer identifier unique within this contest/year.
- If `teams.csv` already exists, reuse existing `team_id` for matching `team_name`; otherwise assign the next available integer (1, 2, 3, …).

### 4.2 team_name

- The team name as it appears in the source data (e.g. `LV Fire`, `San Diego A1`, `PEA Chestnuts`).

### 4.3 student_ids

- Pipe-separated list of `student_id` values for all students on that team in this contest/year.
- Use the `student_id` from the corresponding `results.csv` for each student in that team.

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
3. Add `team` to `results.csv` **right after** `student_name`, with the extracted team name per student.
4. Create/update `database/contests/<contest>-teams/year=<year>/teams.csv` with columns: `team_id`, `team_name`, `student_ids`, `state`.
5. Rebuild search data.
