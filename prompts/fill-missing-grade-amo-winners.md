# Fill missing grade for AMO winners in students.csv

**Goal:** Find every student who has won an AMO award and has a blank or missing `grade_in_2026` in `database/students/students.csv`. Use web search to infer the student's grade from information on the internet. Update **only** the `grade_in_2026` column for those students. Do **not** modify any other student information; do **not** change students who already have `grade_in_2026` labeled.

**Rule:** Always use **student_id** to identify students. Join AMO results with `students.csv` by `student_id`. Update only rows where `grade_in_2026` is empty or missing.

---

## 1. Identify AMO winners with missing grade

1. Read all AMO result files under `database/contests/amo/`:
   - `year=2022/results.csv`
   - `year=2023/results.csv`
   - `year=2024/results.csv`
   - `year=2025/results.csv`

   Each file has columns: `student_id`, `student_name`, `state`, `school`, `award`, `mcp_rank`. All rows are AMO winners (Gold, Silver, Bronze, or Honorable Mention).

2. Collect the set of unique `student_id` values from all AMO result files.

3. Read `database/students/students.csv` (columns: `student_id`, `student_name`, `state`, `team_ids`, `alias`, `gender`, `grade_in_2026`).

4. For each `student_id` that appears in AMO results, check the corresponding row in `students.csv`. If `grade_in_2026` is empty, blank, or missing, add that student to the **target list**. These are the only students you may update.

5. Output the target list: `student_id`, `student_name`, `alias` (if any), and the AMO year(s) and award(s) they won. This helps with search context.

---

## 2. Search for grade information on the internet

For each student in the target list, search using the student's name with the keyword **"math"** (e.g., `"[Student Name]" math AMO` or `"[Student Name]" math olympiad`). Use the following sources in order of preference.

### 2.1 LinkedIn

- Search for the student's LinkedIn profile (e.g., `"[Student Name]" LinkedIn` or `"[Student Name]" math AMO site:linkedin.com`).
- If the student lists AMO (American Mathematics Olympiad) or similar awards on their LinkedIn profile, check whether they mention their grade or year when they won.
- If they list "AMO 2024 Gold" and their education timeline shows they were in 10th grade in 2023–2024, derive `grade_at_contest` = 10 for contest year 2024.
- Use the formula below to compute `grade_in_2026`.

### 2.2 School or organization posts

- Search for posts from schools, math clubs, or educational organizations mentioning the student (e.g., `"[Student Name]" "[School Name]" AMO` or `"[Student Name]" grade math`).
- If a post states the student's grade and when it was posted (e.g., "10th grader [Name] won AMO Gold in 2024"), use that information.
- If the post date is known but grade is implied (e.g., "our sophomore [Name]..."), derive the grade from the post date and typical grade progression.
- Use the formula below to compute `grade_in_2026`.

### 2.3 Other reliable sources

- News articles, official AMO/MAA announcements, or school newsletters that explicitly state the student's grade at the time of the award may be used.
- Only use sources that clearly identify the student (name + school or state) and state or strongly imply their grade. Do not guess.

---

## 3. Compute grade_in_2026

**Definition:** `grade_in_2026` = the student's grade as of January 1, 2026 (US K–12 grade levels, typically 7–12 for AMO winners).

**Formula:** When you find that a student was in grade `G` during contest year `Y` (e.g., AMO 2024, so Y=2024):

```
grade_in_2026 = G + (2026 - Y)
```

Examples:
- Grade 10 in AMO 2024 → `grade_in_2026` = 10 + (2026 - 2024) = **12**
- Grade 9 in AMO 2023 → `grade_in_2026` = 9 + (2026 - 2023) = **12**
- Grade 11 in AMO 2025 → `grade_in_2026` = 11 + (2026 - 2025) = **12**

Use the **most recent** contest year when multiple sources conflict. Prefer grade information from the same year as the AMO award when possible.

---

## 4. Update students.csv

- For each student in the target list for whom you found a **clear, verifiable** grade from the internet:
  - Update **only** the `grade_in_2026` column for that `student_id` in `database/students/students.csv`.
  - Set the value to the computed integer (e.g., `9`, `10`, `11`, `12`).

- **Do not:**
  - Change `student_id`, `student_name`, `state`, `team_ids`, `alias`, or `gender`.
  - Update any student who already has a non-empty `grade_in_2026`.
  - Update any student who is not in the target list (AMO winners with missing grade).
  - Guess or infer grade from weak or ambiguous sources.

- Leave `grade_in_2026` blank for any student for whom no reliable grade could be found.

---

## 5. Report students whose grade could not be inferred

Produce a list of all target-list students for whom `grade_in_2026` was **not** updated because:
- No reliable source was found, or
- The source was ambiguous or conflicting, or
- The student could not be confidently identified.

For each such student, list: **student_id**, **student_name**, **alias** (if any), **AMO year(s) and award(s)**, and a brief note on what was searched and why no update was made.

---

## Summary

1. Join AMO results (`database/contests/amo/year=*/results.csv`) with `students.csv` by `student_id`.
2. Identify AMO winners with empty `grade_in_2026`.
3. Search the internet using student name + "math" keyword; prefer LinkedIn (AMO listed) and school/organization posts with grade information.
4. Compute `grade_in_2026` = grade_at_contest + (2026 - contest_year).
5. Update **only** `grade_in_2026` for those students in `students.csv`; do not modify any other column or any other student.
6. Report students whose grade could not be inferred for manual follow-up.
