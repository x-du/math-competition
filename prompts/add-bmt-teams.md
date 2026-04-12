# Add and maintain `teams.csv` for BMT (Berkeley Math Tournament)

**Goal:** Populate or update `database/contests/bmt-teams/year=<year>/teams.csv` so every team that appears in that year’s BMT results (or in official team standings you provide) has a row with consistent IDs, names, school, roster links, and state.

**Scope:** Teams are **specific to the competition year**. Do not mix rosters across years.

**Result tables for roster building:** Team membership is **not** only in the General exam. For each year, read **all** of these when building or refreshing `student_ids` / `bmt_student_ids`:

| Contest folder | Typical `subject` in CSV |
|----------------|---------------------------|
| `database/contests/bmt/year=<year>/results.csv` | General |
| `database/contests/bmt-algebra/year=<year>/results.csv` | Algebra |
| `database/contests/bmt-calculus/year=<year>/results.csv` | Calculus |
| `database/contests/bmt-discrete/year=<year>/results.csv` | Discrete |
| `database/contests/bmt-geometry/year=<year>/results.csv` | Geometry |

Each file should include `bmt_student_id` and a **`team_id`** column (see §1). If `team_id` is missing, add it immediately after `bmt_student_id`, filled from the leading digit prefix of `bmt_student_id`.

**Input:** You will typically have:

1. The BMT result CSVs above for the target year.
2. Optional: Official team standings or summary text (e.g. `Rank. Team <id>, <team name>, <school or org>, <score>`). You may receive **several pasted blocks** (e.g. different rounds); see §4 for how to merge them.

Related prompt for other contests: `prompts/add-team-column-and-teams.md` (different schema and rules; BMT uses the workflow below).

---

## 1. Team ID from `bmt_student_id` (BMT-specific)

BMT encodes the **team identifier** inside `bmt_student_id` on each student row.

- **Rule:** The `team_id` is the **numeric prefix** of `bmt_student_id` before the first letter (A–Z).  
  - Example: `bmt_student_id` = `220A` → `team_id` = `220`  
  - Example: `041C` → `team_id` = `041`  
  - Example: `166D` → `team_id` = `166`
- **Implementation note:** Parse with a rule such as: take all leading digits; that string is `team_id`. Preserve leading zeros if present (e.g. `093` stays `093`, not `93`), so IDs match official “Team 093” style listings unless the data consistently use unpadded numbers—**match whatever appears in each result file after extraction.**
- If `bmt_student_id` is empty or cannot be parsed to a team prefix, that row does not define a team roster line by itself (skip for team grouping, or handle as individual per project conventions).

---

## 2. Discover students per team from all BMT `results.csv` files

- Read **every** result file listed in **Scope** (General + Algebra + Calculus + Discrete + Geometry) for `year=<year>`.
- For each row with a non-empty `bmt_student_id`:
  - Take **`team_id`** from the column if present; otherwise compute it as in §1.
  - **Consistency check:** The leading-digit prefix of `bmt_student_id` must equal `team_id` for this row to count toward that team’s roster. If they disagree, fix the row or skip until clarified.
- **Same student, different teams:** A competitor may appear on **different** `team_id`s in different exams (e.g. `074D` on one subject and `242D` on another). Assign a student to team **T** only from rows whose **`team_id` is `T`**—never infer team membership from a row that belongs to another team.
- **Group** all qualifying rows by `team_id`, across all five files. Each group is the team roster for that year.
- Collect for each team:
  - **`student_ids`:** pipe-separated `student_id` values, **one entry per person** (dedupe across subjects and duplicate award lines).
  - **`bmt_student_ids`:** pipe-separated codes aligned with `student_ids` (same index order). If the same `student_id` appears multiple times for the **same** team with different codes (unusual), pick a single canonical code (e.g. one consistent rule such as lexicographic order).
- Sort `student_ids` numerically unless the project already uses another fixed order.
- **`team_name` / `school` in `teams.csv`:** Prefer values already set from **standings** (§4) or an existing `teams.csv`. Otherwise derive from results: use the most common non-empty `team_name` and `school` among rows for that `team_id`, preferring General when helpful. Avoid inventing names.

---

## 3. Schema: `database/contests/bmt-teams/year=<year>/teams.csv`

**Path:** `database/contests/bmt-teams/year=<year>/teams.csv`

**Columns (in order):**

| Column | Description |
|--------|-------------|
| `team_id` | Extracted from `bmt_student_id` as in §1 (same identifier space as “Team \<id\>” in official listings). |
| `team_name` | Team name for that year (from results and/or official standings). |
| `student_ids` | Pipe-separated internal `student_id`s for members of this team in this year. |
| `bmt_student_ids` | Pipe-separated BMT codes (`041C`, `220A`, …) for those students. |
| `school` | School or organization string (from results and/or standings). |
| `state` | US state (or region), if known—infer from school name, `database/students/students.csv`, or external references; leave empty if unknown. |

**Row key:** `(year implicit from folder, team_id)` — one row per `team_id` per year file.

**Which `team_id`s to include:** Include every `team_id` that appears in **any** of the five result CSVs for that year, plus any **`team_id`** present only in **standings** (§4) (rosters empty until results exist). That yields a complete team list for the year.

---

## 4. Official team standings text (optional but recommended)

When you have a pasted list in a form like:

```text
9. Team 177, Harker Omicron, The Harker School, 91
9. Team 127, Saratoga 1, Saratoga High School, 91
8. Team 093, Proof Narwhals, Proof School, 92
...
1. Team 092, -1, -1, 115
```

- Parse each line into: leading **rank** (optional), **team_id** (digits after `Team `), **team_name**, **school**, trailing **numeric score** (optional).
- **Ignore team ranking and team score** when updating `teams.csv`: do not add columns for placement or team points; use only **team_id**, **team_name**, and **school** from these lines (plus rosters from §2).
- **Multiple blocks:** The same contest year may come with several standings excerpts (e.g. different rounds). Merge by **`team_id` only**. If the same `team_id` appears more than once, the name and school should match; if not, prefer the most complete non-placeholder text. Do not treat different ranks or scores as conflicting—those fields are discarded.
- Treat placeholders like `-1` for name or school as **unknown**; fill from the BMT result CSVs when students exist.
- **If a team appears in this list but has no row in `teams.csv` yet, add a row** with `team_id` from the list. Fill `team_name` / `school` from the list when not `-1`. Then **attach students** by re-running the grouping in §2 across **all five** result files so `student_ids` and `bmt_student_ids` reflect every subject where that `team_id` appears.
- **Standings-only teams:** If a team appears in standings but has no students in **any** of the five result files for that year, still add a row with empty `student_ids` and `bmt_student_ids` and the name/school from standings (when known), so published team lists stay complete.

---

## 5. Merge policy: results vs standings vs existing `teams.csv`

1. When **regenerating rosters** from results, preserve **`team_name`**, **`school`**, and **`state`** from the existing `teams.csv` for each `team_id` when those fields were set from standings or manual edits; then replace only **`student_ids`** and **`bmt_student_ids`** from §2.
2. **Augment** with teams discovered from **all five** result files (§2).
3. **Add missing teams** from official standings (§4) so the file reflects the published team list.
4. Ensure each `team_id` appears **exactly once** (default: one row per `team_id`).

---

## 6. Student registry

- **`database/students/students.csv`** — use for disambiguation and **state** when the results/school string alone is insufficient.
- Match students by **`student_id`** from the result tables; do not invent IDs.

---

## 7. After updating

- Run from repo root:  
  `python scripts/build_search_data.py`  
  so that `docs/data.json` reflects the changes.

---

## Summary

1. **Team ID:** Use the `team_id` column in each result CSV, or the leading digit sequence of `bmt_student_id` (e.g. `220A` → `220`). Ensure **General + Algebra + Calculus + Discrete + Geometry** files for that year have a `team_id` column.
2. **Rosters:** Union rows from **all five** `results.csv` paths; group by `team_id`; assign students only from rows whose `team_id` matches (§2). Fill `student_ids` and `bmt_student_ids`.
3. **File:** Write `database/contests/bmt-teams/year=<year>/teams.csv` with columns: `team_id`, `team_name`, `student_ids`, `bmt_student_ids`, `school`, `state`. Include every `team_id` seen in any result file or in standings.
4. **Standings:** Add teams from provided lists that are missing; merge duplicate `team_id` lines across multiple blocks; **do not store** team rank or team score. Prefer standings **team_name** / **school** when given (non-placeholder); otherwise derive from results or keep existing `teams.csv` metadata.
5. Rebuild search data.
