#!/usr/bin/env python3
"""Add/complete grade_in_2026 column in students.csv based **only** on student_id.

grade_in_2026 = grade at Jan 1st of 2026 = grade_at_contest + (2025 - contest_year)

Sources used (via student_id only):
- database/contests/mathcounts-national (competitors.csv by year)
- database/contests/mathcounts-national-rank (results.csv by year)
- database/contests/mpfg (results.csv by year); grade like "9th" -> 9

Rules:
- Never overwrite a non-empty existing grade_in_2026 value.
- Ignore alias/student_name when joining; rely strictly on student_id.
- When multiple contests have data for the same student_id, prefer the most
  recent contest year.
"""

import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
MATHCOUNTS_DIR = BASE / "database" / "contests" / "mathcounts-national"
MATHCOUNTS_RANK_DIR = BASE / "database" / "contests" / "mathcounts-national-rank"
MPFG_DIR = BASE / "database" / "contests" / "mpfg"
STUDENTS_CSV = BASE / "database" / "students" / "students.csv"


def parse_mpfg_grade(grade_str):
    """Parse mpfg grade like '9th', '11th' -> int 9, 11. Return None if invalid."""
    if not grade_str:
        return None
    s = (grade_str or "").strip()
    # Grades are like "9th", "10th", etc.
    digits = ""
    for ch in s:
        if ch.isdigit():
            digits += ch
        else:
            break
    if not digits:
        return None
    try:
        return int(digits)
    except ValueError:
        return None


def update_best(grade_year_dict, sid, grade, year):
    """Set (grade, year) for this student_id only if year is newer."""
    if sid is None:
        return
    if sid not in grade_year_dict or year > grade_year_dict[sid][1]:
        grade_year_dict[sid] = (grade, year)


def build_student_grade_year():
    """Return dict: student_id -> (grade_at_contest, contest_year)."""
    student_grade_year = {}

    # --- mathcounts-national (competitors) ---
    for year_dir in sorted(MATHCOUNTS_DIR.iterdir(), reverse=True):
        if not year_dir.is_dir():
            continue
        try:
            year = int(year_dir.name.replace("year=", ""))
        except ValueError:
            continue
        competitors_file = year_dir / "competitors.csv"
        if not competitors_file.exists():
            continue
        with competitors_file.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sid = (row.get("student_id") or "").strip()
                grade_str = (row.get("grade") or "").strip()
                if not sid or not grade_str:
                    continue
                if not sid.isdigit():
                    continue
                try:
                    grade = int(grade_str)
                except ValueError:
                    continue
                update_best(student_grade_year, int(sid), grade, year)

    # --- mathcounts-national-rank (results) ---
    for year_dir in sorted(MATHCOUNTS_RANK_DIR.iterdir(), reverse=True):
        if not year_dir.is_dir():
            continue
        try:
            year = int(year_dir.name.replace("year=", ""))
        except ValueError:
            continue
        results_file = year_dir / "results.csv"
        if not results_file.exists():
            continue
        with results_file.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sid = (row.get("student_id") or "").strip()
                grade_str = (row.get("grade") or "").strip()
                if not sid or not grade_str:
                    continue
                if not sid.isdigit():
                    continue
                try:
                    grade = int(grade_str)
                except ValueError:
                    continue
                update_best(student_grade_year, int(sid), grade, year)

    # --- mpfg (results; grade like "9th" -> 9) ---
    for year_dir in sorted(MPFG_DIR.iterdir(), reverse=True):
        if not year_dir.is_dir():
            continue
        try:
            year = int(year_dir.name.replace("year=", ""))
        except ValueError:
            continue
        results_file = year_dir / "results.csv"
        if not results_file.exists():
            continue
        with results_file.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sid = (row.get("student_id") or "").strip()
                if not sid or not sid.isdigit():
                    continue
                grade_val = parse_mpfg_grade(row.get("grade"))
                if grade_val is None:
                    continue
                update_best(student_grade_year, int(sid), grade_val, year)

    return student_grade_year


def main():
    student_grade_year = build_student_grade_year()
    print(f"Found grade data for {len(student_grade_year)} student_ids.")

    rows = []
    with STUDENTS_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        if "grade_in_2026" not in fieldnames:
            fieldnames.append("grade_in_2026")

        for row in reader:
            existing = (row.get("grade_in_2026") or "").strip()
            sid_str = (row.get("student_id") or "").strip()

            # Respect existing values: never overwrite non-empty grade_in_2026.
            if existing:
                row["grade_in_2026"] = existing
                rows.append(row)
                continue

            grade_2026 = ""
            if sid_str and sid_str.isdigit():
                sid = int(sid_str)
                if sid in student_grade_year:
                    grade, year = student_grade_year[sid]
                    grade_2026 = str(grade + (2025 - year))

            row["grade_in_2026"] = grade_2026
            rows.append(row)

    with STUDENTS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    filled = sum(1 for r in rows if (r.get("grade_in_2026") or "").strip())
    print(f"Updated {STUDENTS_CSV}")
    print(f"Filled grade_in_2026 for {filled} students")


if __name__ == "__main__":
    main()
