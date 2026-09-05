---
name: fill-missing-state
description: >-
  Fills blank state values in students.csv from contest records (by
  student_id), Math Kangaroo scripts, or school-name lookup, then fills team
  state when every roster member shares the same state. Use when the user asks
  to fill missing state, find student states, or complete blank state fields.
---

# Fill missing state

Update **only** rows in `database/students/students.csv` whose `state` is blank. Key by **student_id**. Never infer state from name alone.

Do **not** write a helper script to bulk-update state. Look up each student; use an LLM/web search only for school (or clearly locatable team/site) names.

## 1. Target list

Rows in `students.csv` with empty `state`. Those are the only student rows you may change.

## 2. Lookup order

Use the first non-empty state found for that `student_id`. Stop once you have one.

### 2.1 Mathcounts, AMO, JMO

These always have state. Check all years for that `student_id`:

- `database/contests/mathcounts-national/year=*/results.csv`
- `database/contests/mathcounts-national-rank/year=*/results.csv`
- `database/contests/amo/year=*/results.csv`
- `database/contests/jmo/year=*/results.csv`

### 2.2 Math Kangaroo

```bash
python scripts/fill_state_from_mk_national_csv.py [--dry-run]
python scripts/fill_state_from_math_kangaroo.py [--dry-run]
```

Local mk-national CSVs first; the second script fetches Math Kangaroo winner PDFs.

### 2.3 Other contests

Search other `database/contests/**/results.csv` files that have `state`, `school`, `team`, or `site`. Match by `student_id` only.

- Non-empty **state** column → use it.
- Non-empty **school** and no state → look up the school’s US state (web search). Assign only when the answer is clear. Skip if school is blank.
- **team** / **site** → use only if the string clearly names a state, or if it is a school/location you can look up confidently.

### 2.4 Team name

Only if the student appears in `database/contests/<contest>-teams/year=<year>/teams.csv` with a non-empty team name that clearly indicates a state. Otherwise skip.

## 3. Update students.csv

Change only `state` for those `student_id`s. Do not add/remove rows. Leave blank if no source applied.

## 4. Team state

After `students.csv` is updated, for each `database/contests/*-teams/**/teams.csv` row with blank `state`:

- Split `student_ids` on `|` and look up each student’s `state`.
- Set team `state` only when **every** student has the **same non-empty** state.
- If any student is blank or states differ, leave team `state` blank (no majority).
