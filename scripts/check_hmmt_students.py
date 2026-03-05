#!/usr/bin/env python3
"""
Check for students who appear in both HMMT November of year Y and
HMMT February of year Y+1.

Contest directory naming:
  * All November HMMT contests have "hmmt-nov" in the slug
    (e.g. "hmmt-nov", "hmmt-nov-general", "hmmt-nov-theme").
  * All February HMMT contests have "hmmt-feb" in the slug
    (e.g. "hmmt-feb", "hmmt-feb-geometry", "hmmt-feb-combo",
    "hmmt-feb-algebra-number-theory").

Run from the repo root:

    python scripts/check_hmmt_students.py

The script will print, for each relevant year pair (Y, Y+1), whether there
are overlapping students between HMMT November Y and HMMT February Y+1,
and list any overlaps.
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


def collect_hmmt_result_files():
    """Yield (slug, year, csv_path) for all hmmt-* contest result CSVs."""
    if not CONTESTS_DIR.exists():
        return
    for contest_dir in sorted(CONTESTS_DIR.iterdir()):
        if not contest_dir.is_dir():
            continue
        slug = contest_dir.name
        if "hmmt-nov" not in slug and "hmmt-feb" not in slug:
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


def build_nov_feb_maps():
    """Return (year_to_nov_ids, year_to_feb_ids).

    Each dict maps year_str -> set(student_id_int).
    """
    year_to_nov_ids = {}
    year_to_feb_ids = {}

    for slug, year, csv_path in collect_hmmt_result_files():
        if "hmmt-nov" in slug:
            ids_map = year_to_nov_ids
        elif "hmmt-feb" in slug:
            ids_map = year_to_feb_ids
        else:
            continue
        ids = ids_map.setdefault(year, set())
        add_ids_from_file(ids, csv_path)

    return year_to_nov_ids, year_to_feb_ids


def main():
    student_names = load_student_names()
    year_to_nov_ids, year_to_feb_ids = build_nov_feb_maps()

    if not year_to_nov_ids and not year_to_feb_ids:
        print("No HMMT contest data found.")
        return

    # We care about pairs (Y, Y+1) where Y has November data and Y+1 has February data.
    years_nov = sorted(int(y) for y in year_to_nov_ids.keys() if y.isdigit())
    years_feb = {int(y) for y in year_to_feb_ids.keys() if y.isdigit()}

    any_overlap = False
    if not years_nov:
        print("No HMMT November data found.")
    for y in years_nov:
        next_year = y + 1
        if next_year not in years_feb:
            print(f"{y} -> {next_year}: no HMMT February data; skipping.")
            continue
        nov_ids = year_to_nov_ids.get(str(y), set())
        feb_ids = year_to_feb_ids.get(str(next_year), set())
        overlap = sorted(nov_ids & feb_ids)

        if not overlap:
            print(f"{y} (Nov) and {next_year} (Feb): OK (no overlapping students).")
            continue

        any_overlap = True
        print(
            f"{y} (Nov) and {next_year} (Feb): "
            f"FOUND {len(overlap)} overlapping student(s):"
        )
        for sid in overlap:
            name = student_names.get(sid, "")
            if name:
                print(f"  - {sid}: {name}")
            else:
                print(f"  - {sid}")

    if not any_overlap:
        print("All checked year pairs: no overlaps between HMMT November and next-year February.")


if __name__ == "__main__":
    main()

