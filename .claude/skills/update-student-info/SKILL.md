---
name: update-student-info
description: >-
  Updates a student's profile in students.csv (state, grade, alias, gender,
  name). Does not change official results grade or score except student_name
  typos. Use when the user asks to set or fix a student's state, grade, alias,
  or other students.csv fields.
argument-hint: "<student-id> --state ... --grade ... --add-alias ..."
---

# Update student info

Update the students.csv.

Don't update official record's grade, score. Except typo in names.

Do not add or commit `scripts/update_student_info.py`. Create temporary code for this task, run it, then delete it. Do not leave helper scripts in the repo.

## Fields

- `state`, `grade_in_2026`, `alias` (`|`-separated; skip the primary name), `gender`, `student_name` — `students.csv` only
- results.csv `student_name` — only when the user asks to fix a typo
- Never edit results `grade`, `score`, `rank`, or other official fields. Do not change `teams.csv` team `state`. Do not rewrite contest grades from `grade_in_2026`.

## Workflow

1. Load the `students.csv` row. Show before/after unless the user already gave a specific update.
2. Change only the named fields. Preserve CSV line endings (many contest files are CRLF).
3. Rebuild: `python scripts/build_search_data.py`
4. Check: `python scripts/check_student_name.py` and `python scripts/check_student_state.py`

Report the student_id, field changes, any name-typo results edits, and checker warnings.
