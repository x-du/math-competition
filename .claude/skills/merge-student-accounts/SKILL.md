---
name: merge-student-accounts
description: >-
  Merges duplicate student accounts in the math-competition database. Keeps the
  earlier student_id, adds the later student's name as an alias, merges profile
  fields, and remaps student_id / student_ids in contest results and team
  rosters. Use when the user says two students are the same person, asks to
  merge student IDs, or to combine duplicate accounts.
argument-hint: "<student-id-a> <student-id-b>"
---

# Merge student accounts

Use this when two `student_id` values in `database/students/students.csv` are the same person.

Do not add or commit `scripts/merge_student_accounts.py`. Perform the merge with editor/search tools (or a one-off command that is not saved into the repo).

## Workflow

1. Load both rows from `database/students/students.csv`.
2. Show both profiles and the planned keeper/drop, unless the user already named the IDs and asked to merge them.
3. Apply the rules below.
4. Rebuild frontend data: `python scripts/build_search_data.py`
5. Run `python scripts/check_student_ids.py` and `python scripts/check_student_name.py`

Default keeper is the **earlier** account (lower numeric `student_id`). Either ID order is fine: `1152` and `2187` would keep `1152`. If the user names a specific ID to keep, use that one.

## Rules

1. Keep the keeper's `student_id` and `student_name`.
2. Add the later `student_name` as an alias (pipe-separated, de-duplicated). Also absorb the later row's existing aliases.
3. Merge other profile fields (`state`, `gender`, `grade_in_2026`, plus any extra columns):
   - If the keeper is blank and the later row has a value, copy it.
   - If both have different non-empty values, keep the keeper's value and report the conflict.
4. Remap every contest `student_id` cell and every teams `student_ids` pipe list from the later ID to the keeper. Deduplicate a roster if both IDs were already listed.
5. Delete the later `students.csv` row.
6. Leave official contest grade, score, rank, and historical `student_name` values as they were. Remap `student_id` / `student_ids` only. The new alias covers `scripts/check_student_name.py`.
7. If both IDs already have a row in the same results CSV, stop and tell the user. Do not guess which score to keep.
8. Edit only changed rows. Preserve existing CSV line endings (many contest files are CRLF).

Do not remap `smt_student_ids`, `bmt_student_ids`, or other contest-native ID columns.

## After a merge

Report: keeper ID, dropped ID, alias/profile notes (including conflicts), files updated, and any checker warnings.

## Example

User: `1152` and `2187` are the same person.

Keeps `1152`, adds `2187`'s `student_name` as an alias if it is not already the primary name or an alias, remaps results/teams that referenced `2187`, deletes `2187`. Do not run that example unless the user asks.
