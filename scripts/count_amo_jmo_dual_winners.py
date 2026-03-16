#!/usr/bin/env python3
"""Count students who have won both AMO and JMO in 2022-2025."""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "database" / "contests"

def get_student_ids(contest: str, years: list[int]) -> set[int]:
    ids = set()
    for year in years:
        path = DB / contest / f"year={year}" / "results.csv"
        if not path.exists():
            continue
        with open(path, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                ids.add(int(row["student_id"]))
    return ids


def get_student_ids_from_csv(path: Path) -> set[int] | None:
    """Read a contest CSV; return set of student_ids if it has student_id column else None."""
    try:
        with open(path, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            rows = list(r)
            if not rows or "student_id" not in rows[0]:
                return None
            return {int(row["student_id"]) for row in rows if row.get("student_id")}
    except Exception:
        return None


def all_contest_student_ids_except_amo_jmo() -> set[int]:
    """All student_ids that appear in any contest result/competitor file other than amo or jmo."""
    ids = set()
    for item in DB.iterdir():
        if not item.is_dir() or item.name in ("amo", "jmo"):
            continue
        for sub in item.rglob("*.csv"):
            s = get_student_ids_from_csv(sub)
            if s is not None:
                ids |= s
    return ids


def load_student_lookup() -> dict[int, tuple[str, str | None]]:
    """Map student_id -> (name, state)."""
    students_csv = ROOT / "database" / "students" / "students.csv"
    mapping: dict[int, tuple[str, str | None]] = {}
    if not students_csv.exists():
        return mapping
    with open(students_csv, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            sid = row.get("student_id")
            if not sid:
                continue
            try:
                sid_int = int(sid)
            except ValueError:
                continue
            name = row.get("student_name") or ""
            state = row.get("state")
            mapping[sid_int] = (name, state)
    return mapping


def main():
    years = [2022, 2023, 2024, 2025]
    amo_ids = get_student_ids("amo", years)
    jmo_ids = get_student_ids("jmo", years)
    both = amo_ids & jmo_ids
    print(f"AMO winners (any award) 2022-2025: {len(amo_ids)}")
    print(f"JMO winners (any award) 2022-2025: {len(jmo_ids)}")
    print(f"Students who won BOTH AMO and JMO (2022-2025): {len(both)}")

    other_ids = all_contest_student_ids_except_amo_jmo()
    only_amo_jmo = sorted(both - other_ids)
    with_other = sorted(both & other_ids)

    print(f"\nOf those, with NO other contest records: {len(only_amo_jmo)}")
    print("Student IDs (only AMO+JMO):", only_amo_jmo)
    print(f"\nWith other contest records: {len(with_other)}")
    print("Student IDs (have other records):", with_other)

    lookup = load_student_lookup()
    if lookup:
        print("\nDetails for students with only AMO+JMO records:")
        for sid in only_amo_jmo:
            name, state = lookup.get(sid, ("<unknown>", None))
            state_str = state or ""
            print(f"{sid}: {name} ({state_str})")

if __name__ == "__main__":
    main()
