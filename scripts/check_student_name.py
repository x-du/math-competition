#!/usr/bin/env python3
"""
Validate that every student_name value in contest CSVs exists in the
students table (either as student_name or alias).

Run from the repo root:

    python scripts/check_student_name.py
"""

import csv
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent
STUDENTS_CSV = REPO_ROOT / "database" / "students" / "students.csv"
CONTESTS_DIR = REPO_ROOT / "database" / "contests"


def load_allowed_names() -> Tuple[Set[str], Dict[str, str]]:
    """
    Load all valid student names from students.csv.

    Includes:
    - the primary student_name column
    - any alias values (pipe-separated list is allowed)

    Also returns a mapping from student_id -> canonical student_name.
    """
    allowed: Set[str] = set()
    id_to_name: Dict[str, str] = {}

    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        if "student_name" not in fieldnames or "student_id" not in fieldnames:
            raise SystemExit(
                f"'student_name' and 'student_id' columns are required in {STUDENTS_CSV}"
            )

        for row in reader:
            primary = (row.get("student_name") or "").strip()
            sid = (row.get("student_id") or "").strip()
            if primary:
                allowed.add(primary)
                if sid:
                    id_to_name[sid] = primary

            alias_field = (row.get("alias") or "").strip()
            if alias_field:
                # Allow multiple aliases separated by "|"
                for alias in alias_field.split("|"):
                    alias = alias.strip()
                    if alias:
                        allowed.add(alias)

    return allowed, id_to_name


def iter_contest_csv_files() -> Iterable[Path]:
    """Yield all CSV files under the contests directory."""
    if not CONTESTS_DIR.exists():
        return []
    return sorted(CONTESTS_DIR.rglob("*.csv"))


def find_unmatched_student_names(
    allowed_names: Set[str],
    id_to_name: Dict[str, str],
) -> Tuple[List[Dict[str, object]], int, int]:
    """
    Scan contest CSVs for student_name values not present in allowed_names.

    Returns:
        (violations, files_with_student_name_col, total_checked_rows)

    Each violation is a dict with keys:
        - student_id: str (may be empty if not present in the row)
        - students_name: str (canonical name from students.csv, if student_id found)
        - contest_name: str (student_name as written in the contest CSV)
        - csv_path: Path
        - row_number: int
    """
    violations: List[Dict[str, object]] = []
    files_with_student_name = 0
    total_rows_checked = 0

    for csv_path in iter_contest_csv_files():
        with open(csv_path, newline="", encoding="utf-8") as f:
            try:
                reader = csv.DictReader(f)
            except csv.Error:
                # Skip malformed files; integrity can be checked separately.
                continue

            fieldnames = reader.fieldnames or []
            if "student_name" not in fieldnames:
                continue

            files_with_student_name += 1
            row_number = 1  # header
            for row in reader:
                row_number += 1
                name = (row.get("student_name") or "").strip()
                if not name:
                    continue

                total_rows_checked += 1
                if name not in allowed_names:
                    sid = (row.get("student_id") or "").strip()
                    canonical = id_to_name.get(sid, "")
                    violations.append(
                        {
                            "student_id": sid,
                            "students_name": canonical,
                            "contest_name": name,
                            "csv_path": csv_path,
                            "row_number": row_number,
                        }
                    )

    return violations, files_with_student_name, total_rows_checked


def main() -> int:
    allowed_names, id_to_name = load_allowed_names()
    violations, files_with_student_name, total_rows_checked = find_unmatched_student_names(
        allowed_names, id_to_name
    )

    print("=== Contest student_name validation against students.csv ===\n")
    print(f"Total unique allowed names (student_name + alias): {len(allowed_names)}")
    print(f"Contest CSV files with a student_name column: {files_with_student_name}")
    print(f"Contest rows with non-empty student_name checked: {total_rows_checked}\n")

    if not violations:
        print(
            "All contest student_name values are present in students.csv "
            "(either student_name or alias)."
        )
        return 0

    print(
        f"Found {len(violations)} unmatched student_name row(s) across contest CSVs.\n"
    )
    print(
        "Each line below is:\n"
        "  student_id | students.csv name | contest student_name | file:row\n"
    )

    def sort_key(v: Dict[str, object]) -> Tuple[str, str, str, int]:
        sid = str(v.get("student_id") or "")
        cname = str(v.get("contest_name") or "")
        path = str(v.get("csv_path") or "")
        row = int(v.get("row_number") or 0)
        return (sid, cname, path, row)

    for v in sorted(violations, key=sort_key):
        sid = str(v.get("student_id") or "").strip() or "N/A"
        canonical = str(v.get("students_name") or "").strip() or "N/A"
        contest_name = str(v.get("contest_name") or "").strip()
        csv_path = v.get("csv_path")
        row_number = int(v.get("row_number") or 0)
        rel_path = (
            csv_path.relative_to(REPO_ROOT)
            if isinstance(csv_path, Path)
            else str(csv_path)
        )
        print(
            f"  {sid} | {canonical} | {contest_name} | {rel_path}: row {row_number}"
        )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

