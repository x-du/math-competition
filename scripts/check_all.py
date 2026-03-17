#!/usr/bin/env python3
"""
Run all data-quality and validation checks:

  1. check_mathcounts_national_students.py — MATHCOUNTS National rankings
  2. find_incomplete_students.py — students missing state, gender, or grade
  3. check_csv_integrity.py — CSV row/column consistency
  4. check_student_ids.py — registry vs contest student_id consistency
  5. check_hmmt_students.py — HMMT Nov Y vs Feb Y+1 overlapping students
  6. check_pumac_students.py — PUMaC A vs B division overlaps by year
  7. check_amo_jmo_same_year.py — no student wins both JMO and AMO in same year

Exits with status 1 if any script fails. Run from the repo root:

    python scripts/check_all.py
"""

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

CHECKS = [
    ("check_mathcounts_national_students.py", "MATHCOUNTS National rankings"),
    ("find_incomplete_students.py", "Incomplete students (state/gender/grade)"),
    ("check_csv_integrity.py", "CSV integrity (row lengths)"),
    ("check_student_ids.py", "Student ID consistency (registry vs contests)"),
    ("check_hmmt_students.py", "HMMT Nov Y vs Feb Y+1 overlapping students"),
    ("check_pumac_students.py", "PUMaC A vs B division overlaps by year"),
    ("check_amo_jmo_same_year.py", "No student wins both JMO and AMO in same year"),
]


def main() -> None:
    script_dir = REPO_ROOT / "scripts"
    failed = []

    for script_name, description in CHECKS:
        script_path = script_dir / script_name
        if not script_path.exists():
            print(f"SKIP {script_name} (not found)")
            failed.append(script_name)
            continue

        print("=" * 60)
        print(f"Running: {script_name}")
        print(f"  {description}")
        print("=" * 60)

        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(REPO_ROOT),
        )
        print()

        if result.returncode != 0:
            failed.append(script_name)

    if failed:
        print("FAILED:", ", ".join(failed))
        sys.exit(1)
    print("All checks completed successfully.")


if __name__ == "__main__":
    main()
