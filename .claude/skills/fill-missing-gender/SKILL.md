---
name: fill-missing-gender
description: >-
  Infers blank gender values in students.csv from student_name (and alias)
  only when confidence is above 80 percent. Use when the user asks to fill
  missing gender, infer gender from names, or complete blank gender fields.
---

# Fill missing gender

Update **only** rows in `database/students/students.csv` whose `gender` is blank. Infer from **`student_name`** (and `alias` if it clarifies the name). Do not use contest, school, or other fields.

Assign only `male` or `female`, and only when confidence is **>80%**. Otherwise leave blank and report the student.

## Workflow

1. List rows with empty `gender`.
2. For each name, infer typical gender in a US/English context:
   - Use first names and parenthetical nicknames (e.g. `Jiayu Ellie Su` → Ellie → female).
   - Unisex names, non-Latin-only names, or single initials → do not guess.
3. If confidence **>80%**, set `gender` to `male` or `female` for that `student_id`.
4. Do not add/remove rows or change `student_id` / `student_name`.

## Report

List every student not updated (`student_id`, `student_name`, alias if any) because confidence was ≤80%, the name was ambiguous, or gender could not be inferred.
