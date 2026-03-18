#!/usr/bin/env python3
"""Check that no student_id wins both JMO and AMO in the same year.

JMO (Junior Mathematical Olympiad) and AMO (American Mathematical Olympiad)
are for different grade levels, so a student cannot win both in the same year.
"""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "database" / "contests"


def get_winner_ids_by_year(contest: str) -> dict[int, set[int]]:
    """Return {year: set(student_ids)} for a contest."""
    result: dict[int, set[int]] = {}
    contest_dir = DB / contest
    if not contest_dir.exists():
        return result
    for year_dir in contest_dir.iterdir():
        if not year_dir.is_dir() or not year_dir.name.startswith("year="):
            continue
        try:
            year = int(year_dir.name.split("=")[1])
        except (IndexError, ValueError):
            continue
        path = year_dir / "results.csv"
        if not path.exists():
            continue
        ids = set()
        with open(path, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                sid = row.get("student_id")
                if sid:
                    try:
                        ids.add(int(sid))
                    except ValueError:
                        pass
        result[year] = ids
    return result


def main() -> int:
    amo_by_year = get_winner_ids_by_year("amo")
    jmo_by_year = get_winner_ids_by_year("jmo")
    years = sorted(set(amo_by_year) | set(jmo_by_year))

    violations: list[tuple[int, int]] = []  # (year, student_id)
    for year in years:
        amo_ids = amo_by_year.get(year, set())
        jmo_ids = jmo_by_year.get(year, set())
        both = amo_ids & jmo_ids
        for sid in both:
            violations.append((year, sid))

    if violations:
        print("ERROR: The following students won BOTH JMO and AMO in the same year:")
        for year, sid in sorted(violations):
            print(f"  Year {year}, student_id {sid}")
        print(f"\nTotal violations: {len(violations)}")
        return 1

    print("OK: No student won both JMO and AMO in the same year.")
    for year in years:
        amo_count = len(amo_by_year.get(year, set()))
        jmo_count = len(jmo_by_year.get(year, set()))
        print(f"  {year}: AMO={amo_count}, JMO={jmo_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
