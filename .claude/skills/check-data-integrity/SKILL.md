---
name: check-data-integrity
description: >-
  Runs python scripts/check_all.py and explains the data-quality results.
  Use when the user asks to check database integrity, validate CSVs, or run
  check_all.
---

# Check data integrity

From the repo root, run:

```bash
python scripts/check_all.py
```

Then explain the output. Do not add a new helper script.

## What it runs

Each block is one check. Exit status 1 from `check_all.py` means at least one **failing** script listed in `FAILED:`.

| Script | Meaning | Fails the run? |
| --- | --- | --- |
| `check_mathcounts_national_students.py` | MATHCOUNTS National rankings: a student should appear ≤3 times with distinct grades | Yes (if any violations) |
| `find_incomplete_students.py` | Missing `state`, `gender`, or `grade_in_2026`; also writes `incomplete_students.json` | No (summary only) |
| `check_csv_integrity.py` | Every data row has the same column count as the header | Yes |
| `check_student_ids.py` | Registry IDs vs contest IDs; team roster IDs missing from that year's results | Yes (missing/orphan IDs or team roster errors) |
| `check_student_name.py` | Contest `student_name` must match primary name, alias, or a known `student_id` | Yes (unresolved names) |
| `check_hmmt_students.py` | Same student in HMMT Nov Y and HMMT Feb Y+1 | No (prints overlaps) |
| `check_pumac_students.py` | Same student in PUMaC A and B in the same year | No (prints overlaps) |
| `check_amo_jmo_same_year.py` | Same student must not win both JMO and AMO in the same year | Yes |
| `check_results_duplicates.py` | Duplicate `student_id` or identical rows in a results.csv | Yes |

Unused students (in the registry but no contest row) are printed by `check_student_ids.py` and do **not** fail the run.

## How to report

1. Say whether `check_all.py` succeeded or failed (exit code / `FAILED:` line).
2. For each failing check, quote the errors and what they mean.
3. For informational checks, summarize counts and notable overlaps; do not treat them as a failed integrity run unless the user asked to clean those up.
4. If the run succeeded and informational output is long, lead with "all failing checks passed" and a short note on incomplete students / HMMT / PUMaC / MATHCOUNTS findings.
