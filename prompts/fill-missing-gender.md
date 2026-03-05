# Fill missing gender for students in students.csv

**Goal:** Find every student in `database/students/students.csv` who has a blank or missing `gender` field. Use an **LLM** to infer gender from the student’s name **only when you can do so with >80% accuracy**. Update `students.csv` for those students; for all others, list their names so they can be handled manually.

**Rule:** Infer gender **only from `student_name`** (and optionally `alias` if it clarifies the name). Do **not** infer from contest participation, school, or other fields. Only assign `male` or `female` when the LLM is **>80% confident**; otherwise do **not** update and add the name to the “cannot infer” list.

---

## 1. Identify students with missing gender

- Read `database/students/students.csv` (columns include: `student_id`, `student_name`, `state`, `team_ids`, `alias`, `gender`, `grade_in_2026`).
- List all rows where `gender` is empty, blank, or missing. These are the only rows you may update or report.

---

## 2. Use LLM to infer gender from name

For each student with missing gender:

1. **Input to the LLM:** Provide the student’s full name (and alias if it helps disambiguate, e.g. “Weiping (Jessica) Li” or alias “Jessica Li”). Ask the LLM to infer whether the name is typically male or female in a US/English context, and to respond with:
   - **Inferred gender:** `male` or `female`
   - **Confidence:** a percentage (0–100%) that the inference is correct

2. **Decision:**
   - If the LLM’s confidence is **>80%** and the inferred value is `male` or `female`, **update** that student’s `gender` in `students.csv` to that value.
   - If the LLM’s confidence is **≤80%**, or the LLM says it cannot infer, or the name is ambiguous (e.g. unisex, non-Latin script only, single initial), **do not update**. Add that student’s **student_name** (and `student_id` for reference) to the “cannot infer” list.

3. **LLM instructions to use:**  
   - Consider first name(s) and any parenthetical or nickname (e.g. “Jiayu Ellie Su” → Ellie suggests female).  
   - Prefer US/English naming conventions when the name allows (e.g. “Alexander” → male, “Charlotte” → female).  
   - For names that are clearly unisex or ambiguous, or that the model does not recognize well, return low confidence and do not guess.  
   - Output only `male` or `female`; do not use other values (e.g. “other”, “unknown”).

---

## 3. Update students.csv

- For each student with missing gender for whom the LLM inferred gender with **>80% confidence**, update **only** the `gender` column for that `student_id` in `database/students/students.csv` to `male` or `female`.
- Do not add or remove rows; do not change `student_id` or `student_name`.
- Leave `gender` blank for any student whose gender was not inferred with >80% confidence.

---

## 4. Report students whose gender cannot be inferred

- Produce a list of all students for whom gender was **not** updated because:
  - LLM confidence was ≤80%, or
  - LLM could not infer, or
  - Name was ambiguous/unisex or otherwise not inferable with sufficient confidence.
- For each such student, list at least: **student_id**, **student_name** (and alias if present). This list can be used for manual lookup or other data sources later.

---

## Summary

1. List all rows in `students.csv` with empty/missing `gender`.
2. For each, use an LLM to infer gender from `student_name` (and alias if helpful); require **>80% confidence** for the inference.
3. Update `gender` in `students.csv` only when the LLM returns `male` or `female` with **>80%** confidence.
4. Report every student whose gender was **not** inferred (with `student_id` and `student_name`) so they can be handled separately.
