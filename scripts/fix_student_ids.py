#!/usr/bin/env python3
"""
Fix student_id values in a contest results CSV based on students.csv.

For each row in the results file:
- Look up the student by name, matching against students.student_name
  and students.alias (pipe-separated).
- If a unique student_id is found for that name and it differs from the
  current student_id in the results file, update the results row.
- If the name does not exist in students.student_name or alias, append
  a new row to students.csv with a fresh student_id and use that ID in
  the results row.

Ambiguous name matches (same name / alias mapping to multiple student_ids)
are left unchanged and reported.

Run from the repo root:

    python scripts/fix_mmaths_2024_student_ids.py <results_csv_path>

Example:

    python scripts/fix_mmaths_2024_student_ids.py database/contests/pumac-b-combinator/year=2022/results_B.csv
"""

import argparse
import csv
from pathlib import Path
from typing import Dict, List, Set, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent
STUDENTS_CSV = REPO_ROOT / "database" / "students" / "students.csv"


def load_students() -> Tuple[List[Dict[str, str]], Dict[str, Set[str]], int]:
    """
    Load students.csv.

    Returns:
        rows: list of student rows (as dicts)
        name_to_ids: mapping from name/alias -> set of student_id strings
        max_id: maximum numeric student_id found (for assigning new IDs)
    """
    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        required = {"student_id", "student_name", "alias"}
        if not required.issubset(fieldnames):
            missing = ", ".join(sorted(required - set(fieldnames)))
            raise SystemExit(f"{STUDENTS_CSV} is missing required column(s): {missing}")

        rows: List[Dict[str, str]] = list(reader)

    name_to_ids: Dict[str, Set[str]] = {}
    max_id = 0

    for row in rows:
        sid = (row.get("student_id") or "").strip()
        if sid:
            try:
                max_id = max(max_id, int(sid))
            except ValueError:
                # Non-numeric IDs are ignored for max-id computation.
                pass

        primary = (row.get("student_name") or "").strip()
        if primary:
            name_to_ids.setdefault(primary, set()).add(sid)

        alias_field = (row.get("alias") or "").strip()
        if alias_field:
            for alias in alias_field.split("|"):
                alias = alias.strip()
                if alias:
                    name_to_ids.setdefault(alias, set()).add(sid)

    return rows, name_to_ids, max_id


def load_results(results_path: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    """Load a contest results CSV (must have student_id and student_name columns)."""
    with open(results_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        required = {"student_id", "student_name"}
        if not required.issubset(fieldnames):
            missing = ", ".join(sorted(required - set(fieldnames)))
            raise SystemExit(f"{results_path} is missing required column(s): {missing}")
        rows = list(reader)
    return rows, fieldnames


def save_students(header: List[str], rows: List[Dict[str, str]]) -> None:
    """Write updated students.csv."""
    with open(STUDENTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def save_results(results_path: Path, header: List[str], rows: List[Dict[str, str]]) -> None:
    """Write updated results CSV."""
    with open(results_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fix student_id in a contest results CSV using students.csv."
    )
    parser.add_argument(
        "results_csv",
        type=Path,
        help="Path to the results CSV (relative to repo root or absolute)",
    )
    args = parser.parse_args()

    results_path = args.results_csv if args.results_csv.is_absolute() else REPO_ROOT / args.results_csv
    if not results_path.exists():
        raise SystemExit(f"Results file not found: {results_path}")

    students_rows, name_to_ids, max_id = load_students()
    results_rows, results_header = load_results(results_path)

    # Preserve the original students.csv header order.
    students_header = list(students_rows[0].keys()) if students_rows else [
        "student_id",
        "student_name",
        "state",
        "team_ids",
        "alias",
        "gender",
        "grade_in_2026",
    ]

    updated_results = 0
    created_students = 0
    ambiguous_names: Set[str] = set()

    for row in results_rows:
        name = (row.get("student_name") or "").strip()
        current_id = (row.get("student_id") or "").strip()

        if not name:
            continue

        candidate_ids = name_to_ids.get(name, set())

        if not candidate_ids:
            # Name not present in students.csv; create a new student.
            max_id += 1
            new_id = str(max_id)

            new_student: Dict[str, str] = {}
            for col in students_header:
                if col == "student_id":
                    new_student[col] = new_id
                elif col == "student_name":
                    new_student[col] = name
                else:
                    # Leave other fields empty by default.
                    new_student[col] = ""

            students_rows.append(new_student)
            name_to_ids.setdefault(name, set()).add(new_id)
            row["student_id"] = new_id

            created_students += 1
            updated_results += 1
            continue

        if len(candidate_ids) > 1:
            # Ambiguous: multiple possible IDs for this name; do not change.
            if current_id not in candidate_ids:
                ambiguous_names.add(name)
            continue

        # Unique match
        (expected_id,) = tuple(candidate_ids)
        if current_id != expected_id:
            row["student_id"] = expected_id
            updated_results += 1

    # Save changes
    save_students(students_header, students_rows)
    save_results(results_path, results_header, results_rows)

    print(f"=== student_id reconciliation: {results_path.name} ===\n")
    print(f"Results file: {results_path}")
    print(f"Results rows processed: {len(results_rows)}")
    print(f"Result rows with updated / filled student_id: {updated_results}")
    print(f"New students added to students.csv: {created_students}")
    print()

    if ambiguous_names:
        print("Ambiguous names (multiple student_ids in students.csv; results left unchanged):")
        for name in sorted(ambiguous_names):
            ids = sorted(name_to_ids.get(name, []))
            print(f"  {name}: possible IDs {ids}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

