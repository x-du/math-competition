---
name: fill-missing-grade-amo-winners
description: >-
  Fills blank grade_in_2026 in students.csv for AMO winners using web search
  (LinkedIn, school posts, news). Use when the user asks to fill missing
  grades for AMO/USAMO winners or complete grade_in_2026 for olympiad winners.
---

# Fill missing grade for AMO winners

Update **only** `grade_in_2026` for AMO winners whose grade is still blank. Join by **student_id**. Do not search for or change anyone who already has a grade.

## 1. Target list

1. Collect unique `student_id`s from `database/contests/amo/year=*/results.csv` (all years present).
2. Keep a student only if their `students.csv` `grade_in_2026` is empty.
3. Note `student_id`, `student_name`, alias, and AMO year(s)/award(s) for search context.

## 2. Search

Search `"<name>" math` / `"<name>" math AMO` / olympiad. Prefer sources that identify the student by name plus school or state.

1. **LinkedIn** — education timeline plus listed AMO year → grade at contest.
2. **School / club posts** — explicit grade or class year (sophomore, etc.) with a date.
3. **News / official announcements** — grade at the award, clearly the same person.

Do not guess from weak or conflicting sources.

## 3. Compute `grade_in_2026`

`grade_in_2026` is US K–12 grade as of January 1, 2026.

If the student was in grade `G` during contest year `Y`:

```
grade_in_2026 = G + (2026 - Y)
```

Examples: grade 10 in AMO 2024 → 12; grade 9 in AMO 2023 → 12; grade 11 in AMO 2025 → 12.

When sources conflict, use the most recent contest year. Prefer grade info from the same year as the award.

## 4. Update

Set only `grade_in_2026` (integer) for target-list students with a clear source. Leave blank if nothing reliable was found.

## Report

For each target student not updated: `student_id`, `student_name`, alias, AMO year(s)/award(s), and why (no source, ambiguous, or identity uncertain).
