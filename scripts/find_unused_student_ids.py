#!/usr/bin/env python3
"""
Find student IDs in database/students/students.csv that are not referenced
by any CSV file under database/contests.

Run from the repo root:

    python scripts/find_unused_student_ids.py
"""

import csv
from pathlib import Path
from typing import Dict, Set, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent
STUDENTS_CSV = REPO_ROOT / "database" / "students" / "students.csv"
CONTESTS_DIR = REPO_ROOT / "database" / "contests"


def load_students() -> Tuple[Dict[str, Dict[str, str]], Set[str]]:
    """Return mapping of student_id -> row dict, and set of all student_ids."""
    students: Dict[str, Dict[str, str]] = {}
    ids: Set[str] = set()

    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "student_id" not in (reader.fieldnames or []):
            raise SystemExit(f"'student_id' column not found in {STUDENTS_CSV}")

        for row in reader:
            sid_raw = (row.get("student_id") or "").strip()
            if not sid_raw:
                continue
            students[sid_raw] = row
            ids.add(sid_raw)

    return students, ids


def iter_contest_csv_files():
    """Yield all CSV files under the contests directory."""
    if not CONTESTS_DIR.exists():
        return
    for path in sorted(CONTESTS_DIR.rglob("*.csv")):
        if path.is_file():
            yield path


def collect_used_student_ids() -> Set[str]:
    """Scan all contest CSVs and collect every referenced student_id."""
    used: Set[str] = set()

    for csv_path in iter_contest_csv_files():
        with open(csv_path, newline="", encoding="utf-8") as f:
            try:
                reader = csv.DictReader(f)
            except csv.Error:
                # Skip malformed files; integrity can be checked separately.
                continue

            fieldnames = reader.fieldnames or []
            if "student_id" not in fieldnames:
                # This contest file doesn't have per-student rows.
                continue

            for row in reader:
                sid_raw = (row.get("student_id") or "").strip()
                if not sid_raw:
                    continue
                used.add(sid_raw)

    return used


def main() -> None:
    students_by_id, all_student_ids = load_students()
    used_ids = collect_used_student_ids()

    unused_ids = sorted(
        (sid for sid in all_student_ids if sid not in used_ids),
        key=lambda x: int(x) if x.isdigit() else x,
    )

    print(f"Total students in students.csv: {len(all_student_ids)}")
    print(f"Distinct student_ids used in contests: {len(used_ids)}")
    print(f"Student_ids not used in any contest CSV: {len(unused_ids)}")
    print()

    if not unused_ids:
        print("All students are referenced in at least one contest CSV.")
        return

    print("Unused students (student_id, student_name, state):")
    for sid in unused_ids:
        row = students_by_id.get(sid, {})
        name = row.get("student_name", "")
        state = row.get("state", "")
        print(f"{sid},{name},{state}")


if __name__ == "__main__":
    main()

