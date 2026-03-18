#!/usr/bin/env python3
"""
Find students who won AMO gold or silver in 2024 or 2025, have no other contest
records, are in the US, and have grade 12 or no grade.

Run from repo root:
    python scripts/find_amo_gold_silver_only_us_12.py
"""

import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATABASE = REPO_ROOT / "database"
STUDENTS_CSV = DATABASE / "students" / "students.csv"
CONTESTS_DIR = DATABASE / "contests"

AMO_YEARS = {"2024", "2025"}
AMO_AWARDS = {"Gold", "Silver"}


def load_students_us_grade12_or_empty():
    """Return { student_id: {'name', 'state', 'grade_in_2026'} } for US students
    with grade_in_2026 in (12, None, "").
    """
    by_id = {}
    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            sid = (row.get("student_id") or "").strip()
            if not sid:
                continue
            try:
                sid_int = int(sid)
            except ValueError:
                continue
            state = (row.get("state") or "").strip()
            state_lc = state.lower()
            if "canada" in state_lc or "canda" in state_lc:
                continue
            grade = (row.get("grade_in_2026") or "").strip()
            if grade and grade != "12":
                continue
            name = (row.get("student_name") or "").strip() or f"Student {sid_int}"
            by_id[sid_int] = {"name": name, "state": state, "grade_in_2026": grade or None}
    return by_id


def collect_result_files():
    """Yield (contest_slug, year, csv_path) for every contest result CSV."""
    for contest_dir in sorted(CONTESTS_DIR.iterdir()):
        if not contest_dir.is_dir():
            continue
        slug = contest_dir.name
        for year_dir in sorted(contest_dir.iterdir()):
            if not year_dir.is_dir() or not year_dir.name.startswith("year="):
                continue
            year = year_dir.name.replace("year=", "")
            for csv_path in sorted(year_dir.glob("*.csv")):
                yield slug, year, csv_path


def build_student_contest_map():
    """Return { student_id: {'slugs': set, 'years': set, 'awards': {(slug, year): award}} }."""
    by_sid = {}
    for slug, year, csv_path in collect_result_files():
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
                entry = by_sid.setdefault(sid_int, {"slugs": set(), "years": set(), "awards": {}})
                entry["slugs"].add(slug)
                entry["years"].add(year)
                award = (row.get("award") or "").strip()
                entry["awards"][(slug, year)] = award
    return by_sid


def main():
    students = load_students_us_grade12_or_empty()
    contests_by_sid = build_student_contest_map()

    # Student IDs that have AMO gold or silver in 2024 or 2025
    amo_gold_silver_2024_2025 = set()
    for sid, info in contests_by_sid.items():
        awards = info.get("awards") or {}
        for (slug, year), award in awards.items():
            if slug == "amo" and year in AMO_YEARS and award in AMO_AWARDS:
                amo_gold_silver_2024_2025.add(sid)
                break

    # Among those, keep only: US, grade 12 or no grade, and no other contest records
    result = []
    for sid in amo_gold_silver_2024_2025:
        student_info = students.get(sid)
        if student_info is None:
            continue
        info = contests_by_sid.get(sid, {})
        slugs = info.get("slugs") or set()
        years = info.get("years") or set()
        awards = info.get("awards") or {}
        if slugs != {"amo"} or not (years <= AMO_YEARS):
            continue
        # All their records are AMO 2024/2025; ensure at least one is Gold/Silver (already in set)
        award_pairs = [
            f"{y}={awards.get(('amo', y), '')}" for y in sorted(years)
        ]
        result.append({
            "student_id": sid,
            "name": student_info["name"],
            "state": student_info["state"],
            "grade_in_2026": student_info["grade_in_2026"] or "",
            "amo_years": ";".join(sorted(years)),
            "awards": ";".join(award_pairs),
        })

    result.sort(key=lambda x: (x["name"].lower(), x["student_id"]))

    # Summary
    print("Summary: AMO Gold/Silver 2024 or 2025, no other records, US, grade 12 or no grade")
    print("=" * 70)
    print(f"Total students: {len(result)}")
    if result:
        by_grade = {}
        for r in result:
            g = r["grade_in_2026"] or "(no grade)"
            by_grade[g] = by_grade.get(g, 0) + 1
        print("By grade_in_2026:")
        for g in sorted(by_grade.keys(), key=lambda x: (x == "(no grade)", x)):
            print(f"  {g}: {by_grade[g]}")
        print("\nStudents:")
        for r in result:
            print(f"  {r['student_id']}: {r['name']} ({r['state']}) grade={r['grade_in_2026'] or '—'}  AMO: {r['awards']}")


if __name__ == "__main__":
    main()
