# Fill missing state for students in students.csv

**Goal:** Find the state for every student in `database/students/students.csv` who has a blank or missing `state` field. Update only those rows with a state value you can **derive from existing records**, using **student_id** as the key. Do not guess based on student name.

**Rule:** Always use **student_id** to find a student’s records. Do not match or infer state from name alone; same names in different states are different students.

**Workflow:** Do **not** use a script to update state. Use an LLM (or manual search) to look up state by **school name** when contest records have school but no state (see 2.2). Update `students.csv` only after you have a clear, student_id-based source.

---

## 1. Identify students with missing state

- Read `database/students/students.csv` (columns include: `student_id`, `student_name`, `state`, `team_ids`, `alias`, etc.).
- List all rows where `state` is empty or missing. These are the only rows you may update.

---

## 2. Look up state in this order

For each student with missing state, try sources in the following order. Use the **first** state you find for that **student_id**; stop once you have one.

### 2.1 State from Mathcounts, AMO, and JMO

These sources always have state information. Check all available years for the student’s `student_id`.

- **`database/contests/mathcounts-national/`**  
  - Per year: `year=<year>/results.csv` has columns `student_id`, `state`, `student_name`, `grade`, `city`, `school`.  
  - If the student’s `student_id` appears here, use the `state` value from that row.
- **`database/contests/mathcounts-national-rank/`**  
  - Per year: `year=<year>/results.csv` has columns `student_id`, `student_name`, `state`, `year`, `rank`, `grade`.  
  - If the student’s `student_id` appears here, use the `state` value from that row.
- **`database/contests/amo/`**  
  - Per year: `year=<year>/results.csv` has `student_id`, `student_name`, `state`, `award`. AMO always has state; use it when the student appears here.
- **`database/contests/jmo/`**  
  - Per year: `year=<year>/results.csv` has `student_id`, `student_name`, `state`, `award`. JMO always has state; use it when the student appears here.

Use the first non-empty state you find for that `student_id`.

### 2.2 State from Math Kangaroo USA winners

- **`scripts/fill_state_from_mk_national_csv.py`** uses local `database/contests/mk-national/` CSV files. Matches by student_id (if present in mk-national) or by name when the name appears with exactly one state. Run: `python scripts/fill_state_from_mk_national_csv.py [--dry-run]`.
- **`scripts/fill_state_from_math_kangaroo.py`** fetches [Math Kangaroo National and State Winners](https://mathkangaroo.org/mks/national-and-state-winners/) PDFs (grades 2–12), parses (name, grade, state), and matches missing-state students by name. Run: `python scripts/fill_state_from_math_kangaroo.py [--dry-run]`.

### 2.3 State from other contests: explicit state column or LLM lookup by school name

- Search other contest result files under `database/contests/` that contain **state**, **school**, **team**, or **site** columns.
- For each such file, look up rows where `student_id` matches the student.  
  - If the row has a **state** column with a non-empty value, use that state.  
  - If the row has **school** (or similar) but no state: only when that row has a **non-empty school name**, use an **LLM to search for the state** by school name (e.g. “What US state is [school name] located in?” or a web/search lookup). Assign state only when the LLM (or search) returns a clear, confident answer for that school. **If there is no school name in the record, skip that source**; do not infer state from empty or missing school.
  - For **team** or **site** without state: only if the value clearly indicates state (e.g. “California” in the name), you may use it; otherwise use LLM search by that name if it looks like a school or location.
- Examples of contests that may have state or school: `mpfg`, `mpfg-olympiad`, `bamo-8`, `bamo-12`, `arml` (site), `dmm` (team_name), etc. Inspect each file’s header and use only columns that exist.

Match only by **student_id**; do not use name alone to assign state.

### 2.4 State from team name

- **Only if** the student has **team_ids** in `students.csv` or appears in contest-specific team files (e.g. `database/contests/<contest>-teams/year=<year>/teams.csv` with `team_id`, `team_name`, `student_ids`), and **only when a non-empty team name exists** for that student: look up the **team_name** and, if it clearly indicates a state (e.g. “Texas A&M”, “California Math Club”), you may set state from that. Prefer unambiguous state references in the team name; if ambiguous, leave state blank.
- **If there is no team name** (e.g. student has no team_ids, or team record has no team_name), **skip this step**; do not guess state from team.

---

## 3. Update students.csv

- For each student with missing state for whom you found a state in steps 2.1–2.4, update **only** the `state` column for that `student_id` in `database/students/students.csv`.
- Do not add or remove rows; do not change `student_id` or infer state from name-only matches.
- Leave `state` blank for any student for whom no state could be found using the rules above.

---

## Summary

1. List students in `students.csv` with empty `state`.
2. For each, use **student_id** only to look up state in: (1) mathcounts-national, mathcounts-national-rank, AMO, and JMO (use state from those CSVs when present), (2) Math Kangaroo: run `scripts/fill_state_from_mk_national_csv.py` (local mk-national CSVs) or `scripts/fill_state_from_math_kangaroo.py` (fetches PDFs), (3) other contest CSVs—use explicit **state** column when present; when only **school name** is present and non-empty, use an **LLM to search** for the state by school name and assign only when the result is clear, (4) team name only when non-empty and it clearly indicates state.
3. Update `state` in `students.csv` manually (or via LLM-assisted edits) only when you have a clear, student_id-based source. Never guess based on student name alone.
