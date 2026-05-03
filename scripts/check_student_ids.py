#!/usr/bin/env python3
"""
Check student ID consistency between database/students/students.csv and
database/contests:

1. Student IDs in students.csv that are not referenced by any contest CSV
   (unused in contests).
2. Student IDs referenced in contest CSVs that are not in students.csv
   (missing from registry / orphan references).
3. Student IDs listed in database/contests/<slug>-teams/year=<y>/teams.csv
   that never appear in that contest's results for the same year — for BMT,
   `bmt/.../year=<y>/results.csv` (all five divisions) are unioned; for **pumac-b**,
   composite `pumac-b` plus **pumac-b-algebra**, **pumac-b-combinator**,
   **pumac-b-geometry**, and **pumac-b-number-theory** are unioned (subject-only
   competitors are not listed on division-wide `pumac-b/results.csv`).

Run from the repo root:

    python scripts/check_student_ids.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent
STUDENTS_CSV = REPO_ROOT / "database" / "students" / "students.csv"
CONTESTS_DIR = REPO_ROOT / "database" / "contests"

BMT_DIVISIONS = ("bmt", "bmt-algebra", "bmt-calculus", "bmt-discrete", "bmt-geometry")

PUMAC_B_DIVISIONS = (
    "pumac-b",
    "pumac-b-algebra",
    "pumac-b-combinator",
    "pumac-b-geometry",
    "pumac-b-number-theory",
)


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
                continue

            fieldnames = reader.fieldnames or []
            if "student_id" not in fieldnames:
                continue

            for row in reader:
                sid_raw = (row.get("student_id") or "").strip()
                if not sid_raw:
                    continue
                used.add(sid_raw)

    return used


def parse_results_student_ids(results_csv: Path) -> Set[str]:
    out: Set[str] = set()
    with open(results_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "student_id" not in (reader.fieldnames or []):
            return out
        for row in reader:
            sid = (row.get("student_id") or "").strip()
            if sid:
                out.add(sid)
    return out


def results_student_ids_for_contest_year(contest_slug: str, year: str) -> Tuple[Set[str], bool]:
    """Union of student_id from results.csv; bool is True if at least one results file existed."""
    ids: Set[str] = set()
    found_file = False
    if contest_slug == "bmt":
        paths = [CONTESTS_DIR / d / f"year={year}" / "results.csv" for d in BMT_DIVISIONS]
    elif contest_slug == "pumac-b":
        paths = [CONTESTS_DIR / d / f"year={year}" / "results.csv" for d in PUMAC_B_DIVISIONS]
    else:
        paths = [CONTESTS_DIR / contest_slug / f"year={year}" / "results.csv"]
    for p in paths:
        if p.is_file():
            found_file = True
            ids |= parse_results_student_ids(p)
    return ids, found_file


def iter_teams_csv_paths():
    if not CONTESTS_DIR.is_dir():
        return
    for teams_root in sorted(CONTESTS_DIR.iterdir()):
        if not teams_root.is_dir() or not teams_root.name.endswith("-teams"):
            continue
        for year_dir in sorted(teams_root.glob("year=*")):
            tc = year_dir / "teams.csv"
            if tc.is_file():
                yield tc


def contest_slug_from_teams_root(teams_root_name: str) -> str:
    return teams_root_name.removesuffix("-teams")


def collect_teams_results_mismatches() -> List[str]:
    """student_id on teams.csv roster but not in that contest year's results."""
    issues: List[str] = []
    for teams_csv in iter_teams_csv_paths():
        teams_root_name = teams_csv.parent.parent.name
        slug = contest_slug_from_teams_root(teams_root_name)
        year = teams_csv.parent.name.removeprefix("year=")

        in_results, found_results = results_student_ids_for_contest_year(slug, year)
        rel = teams_csv.relative_to(REPO_ROOT)
        if not found_results:
            issues.append(
                f"WARNING [{rel}]: no results.csv for contest {slug!r} year={year}; "
                "skipped teams-vs-results student_id check"
            )
            continue

        with open(teams_csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if "student_ids" not in (reader.fieldnames or []):
                continue
            for row in reader:
                team_id = (row.get("team_id") or "").strip()
                raw = (row.get("student_ids") or "").strip()
                if not raw:
                    continue
                for sid in (p.strip() for p in raw.split("|") if p.strip()):
                    if sid not in in_results:
                        issues.append(
                            f"ERROR [{rel} team_id={team_id}]: student_id {sid} appears in teams.csv "
                            f"but not in results for {slug!r} year={year}"
                        )
    return issues


def main() -> int:
    students_by_id, all_student_ids = load_students()
    used_ids = collect_used_student_ids()

    unused_ids = sorted(
        (sid for sid in all_student_ids if sid not in used_ids),
        key=lambda x: int(x) if x.isdigit() else x,
    )
    missing_from_registry = sorted(
        (sid for sid in used_ids if sid not in all_student_ids),
        key=lambda x: int(x) if x.isdigit() else x,
    )

    teams_issues = collect_teams_results_mismatches()
    teams_errors = [m for m in teams_issues if m.startswith("ERROR")]
    teams_warnings = [m for m in teams_issues if m.startswith("WARNING")]

    print(f"Total students in students.csv: {len(all_student_ids)}")
    print(f"Distinct student_ids used in contests: {len(used_ids)}")
    print(f"Student_ids not used in any contest CSV: {len(unused_ids)}")
    print(f"Student_ids in contests but NOT in students.csv: {len(missing_from_registry)}")
    print(f"Teams.csv vs results.csv roster issues: {len(teams_issues)} "
          f"({len(teams_errors)} errors, {len(teams_warnings)} warnings)")
    print()

    if missing_from_registry:
        print("Student_ids referenced in contests but missing from registry:")
        for sid in missing_from_registry:
            print(f"  {sid}")
        print()

    for line in teams_warnings:
        print(line)
    if teams_warnings:
        print()

    for line in teams_errors:
        print(line)
    if teams_errors:
        print()

    if not unused_ids:
        print("All students are referenced in at least one contest CSV.")
    else:
        print("Unused students (student_id, student_name, state):")
        for sid in unused_ids:
            row = students_by_id.get(sid, {})
            name = row.get("student_name", "")
            state = row.get("state", "")
            print(f"{sid},{name},{state}")

    if missing_from_registry or teams_errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
