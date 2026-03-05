#!/usr/bin/env python3
"""
Check for students who appear in both PUMaC division A and division B
in the same year.

A‑division contests are any contest whose slug starts with "pumac"
but not "pumac-b" (e.g. "pumac", "pumac-algebra", "pumac-geometry", ...).
B‑division contests are any contest whose slug starts with "pumac-b"
(e.g. "pumac-b", "pumac-b-geometry", ...).

Run from the repo root:

    python scripts/check_pumac_students.py

The script will print, for each year that has any PUMaC data, whether
there are overlapping students between divisions, and list any overlaps.
"""

import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DATABASE = REPO_ROOT / "database"
CONTESTS_DIR = DATABASE / "contests"
STUDENTS_CSV = DATABASE / "students" / "students.csv"


def load_student_names():
    """Return {student_id_int: student_name} from students.csv."""
    names = {}
    if not STUDENTS_CSV.exists():
        return names
    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = (row.get("student_id") or "").strip()
            if not sid:
                continue
            try:
                sid_int = int(sid)
            except ValueError:
                continue
            name = (row.get("student_name") or "").strip()
            names[sid_int] = name or f"Student {sid_int}"
    return names


def collect_pumac_result_files():
    """Yield (slug, year, csv_path) for all pumac* contest result CSVs."""
    if not CONTESTS_DIR.exists():
        return
    for contest_dir in sorted(CONTESTS_DIR.iterdir()):
        if not contest_dir.is_dir():
            continue
        slug = contest_dir.name
        if not slug.startswith("pumac"):
            continue
        for year_dir in sorted(contest_dir.iterdir()):
            if not year_dir.is_dir() or not year_dir.name.startswith("year="):
                continue
            year = year_dir.name.replace("year=", "")
            for csv_path in sorted(year_dir.glob("*.csv")):
                yield slug, year, csv_path


def add_ids_from_file(target_set, csv_path):
    """Add student IDs from a single results CSV into target_set."""
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row.get("student_id") or row.get("student_id ")
            if sid is not None:
                sid = str(sid).strip()
            if not sid:
                continue
            try:
                sid_int = int(sid)
            except ValueError:
                continue
            target_set.add(sid_int)


def build_division_maps():
    """Return (year_to_a_ids, year_to_b_ids).

    Each value is a dict: {year_str: set(student_id_int)}.
    """
    year_to_a_ids = {}
    year_to_b_ids = {}

    for slug, year, csv_path in collect_pumac_result_files():
        if slug.startswith("pumac-b"):
            ids_map = year_to_b_ids
        else:
            ids_map = year_to_a_ids
        ids = ids_map.setdefault(year, set())
        add_ids_from_file(ids, csv_path)

    return year_to_a_ids, year_to_b_ids


def main():
    student_names = load_student_names()
    year_to_a_ids, year_to_b_ids = build_division_maps()

    all_years = sorted(set(year_to_a_ids) | set(year_to_b_ids))
    if not all_years:
        print("No PUMaC contest data found.")
        return

    any_overlap = False
    for year in all_years:
        a_ids = year_to_a_ids.get(year, set())
        b_ids = year_to_b_ids.get(year, set())
        overlap = sorted(a_ids & b_ids)
        if not overlap:
            print(f"{year}: OK (no students appear in both PUMaC A and B).")
            continue

        any_overlap = True
        print(f"{year}: FOUND {len(overlap)} overlapping student(s) between PUMaC A and B:")
        for sid in overlap:
            name = student_names.get(sid, "")
            if name:
                print(f"  - {sid}: {name}")
            else:
                print(f"  - {sid}")

    if not any_overlap:
        print("All years: no overlaps between PUMaC division A and division B.")


if __name__ == "__main__":
    main()

