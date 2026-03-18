#!/usr/bin/env python3
"""
Populate a `state` column in database/students/students.csv by inferring
states from contest results that already include a `state` field.

Sources scanned (any CSV under database/contests with both `student_id`
and `state` columns), e.g.:
- amo/year=20xx/results.csv
- jmo/year=20xx/results.csv
- mathcounts-national-rank/year=20xx/results.csv

For each student_id, we prefer the first non-empty state encountered.
If conflicting states are found for the same student_id, we keep the
first and record the conflict, but do not fail.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Tuple, Set


ROOT = Path(__file__).resolve().parent.parent
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
CONTESTS_DIR = ROOT / "database" / "contests"


def build_state_map() -> Tuple[Dict[int, str], Dict[int, Set[str]]]:
    """Return (state_by_sid, conflicts) from all contest result CSVs."""
    state_by_sid: Dict[int, str] = {}
    conflicts: Dict[int, Set[str]] = {}

    for csv_path in sorted(CONTESTS_DIR.rglob("*.csv")):
        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = [fn.strip() for fn in (reader.fieldnames or [])]
            if "student_id" not in fieldnames or "state" not in fieldnames:
                continue

            for row in reader:
                sid_raw = (row.get("student_id") or row.get("student_id ") or "").strip()
                if not sid_raw:
                    continue
                try:
                    sid = int(sid_raw)
                except ValueError:
                    continue

                state = (row.get("state") or "").strip()
                if not state:
                    continue

                prev = state_by_sid.get(sid)
                if prev is None:
                    state_by_sid[sid] = state
                elif prev != state:
                    # Track conflicting states but keep the first one.
                    s = conflicts.setdefault(sid, set())
                    s.add(prev)
                    s.add(state)

    return state_by_sid, conflicts


def rewrite_students(state_by_sid: Dict[int, str]) -> None:
    """Rewrite students.csv with a `state` column filled when available."""
    with STUDENTS_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        orig_fieldnames = [fn.strip() for fn in (reader.fieldnames or [])]

        # Insert `state` after `student_name` if not already present.
        if "state" in orig_fieldnames:
            new_fieldnames = orig_fieldnames
        else:
            new_fieldnames = []
            inserted = False
            for fn in orig_fieldnames:
                new_fieldnames.append(fn)
                if fn == "student_name":
                    new_fieldnames.append("state")
                    inserted = True
            if not inserted:
                # Fallback: append at the end.
                new_fieldnames.append("state")

        rows_out = []
        for row in reader:
            sid_raw = (row.get("student_id") or "").strip()
            try:
                sid = int(sid_raw)
            except ValueError:
                sid = None

            existing_state = (row.get("state") or "").strip()

            # Do NOT overwrite an existing state; only fill when blank.
            if existing_state:
                state_value = existing_state
            else:
                inferred_state = ""
                if sid is not None:
                    inferred_state = state_by_sid.get(sid, "").strip()
                state_value = inferred_state

            new_row = {}
            for fn in new_fieldnames:
                if fn == "state":
                    new_row[fn] = state_value
                else:
                    new_row[fn] = row.get(fn, "")
            rows_out.append(new_row)

    with STUDENTS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)


def main() -> None:
    state_by_sid, conflicts = build_state_map()
    print(f"Found states for {len(state_by_sid)} students.")
    if conflicts:
        print(f"Detected conflicting states for {len(conflicts)} student_ids.")
    rewrite_students(state_by_sid)
    print(f"Updated {STUDENTS_CSV} with `state` column.")


if __name__ == "__main__":
    main()

