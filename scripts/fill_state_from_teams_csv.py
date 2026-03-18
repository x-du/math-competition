#!/usr/bin/env python3
"""
Fill missing state for students using ONLY teams.csv files in database/contests.

Per prompts/fill-missing-state.md section 2.4: when a student appears in
database/contests/<contest>-teams/year=<year>/teams.csv with team_id, team_name,
student_ids, and a non-empty state column, use that state.

Reads missing_state from incomplete_students.json. Updates students.csv.
"""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
CONTESTS_DIR = ROOT / "database" / "contests"
INCOMPLETE_JSON = ROOT / "incomplete_students.json"


def build_state_from_teams() -> dict[int, str]:
    """Build student_id -> state from all teams.csv in database/contests."""
    state_by_sid: dict[int, str] = {}
    for teams_path in sorted(CONTESTS_DIR.rglob("teams.csv")):
        with open(teams_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                state = (row.get("state") or "").strip()
                if not state:
                    continue
                student_ids_raw = (row.get("student_ids") or "").strip()
                for part in student_ids_raw.split("|"):
                    part = part.strip()
                    if not part:
                        continue
                    # Handle malformed ids like "2Big L Club326" - skip non-numeric
                    try:
                        sid = int(part)
                    except ValueError:
                        continue
                    if sid not in state_by_sid:
                        state_by_sid[sid] = state
    return state_by_sid


def main() -> None:
    state_by_sid = build_state_from_teams()
    print(f"Loaded state for {len(state_by_sid)} students from teams.csv")

    with open(INCOMPLETE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    missing_state = data.get("missing_state", [])
    missing_sids = {int(s["student_id"]) for s in missing_state}

    to_update = {sid: state for sid, state in state_by_sid.items() if sid in missing_sids}
    print(f"Can fill state for {len(to_update)} students with missing state")

    if not to_update:
        return

    rows = []
    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            sid_s = (row.get("student_id") or "").strip()
            if not sid_s:
                rows.append(row)
                continue
            try:
                sid = int(sid_s)
            except ValueError:
                rows.append(row)
                continue
            if sid in to_update:
                row["state"] = to_update[sid]
                print(f"  {sid} {row.get('student_name', '')} -> {to_update[sid]}")
            rows.append(row)

    with open(STUDENTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Updated {len(to_update)} rows in {STUDENTS_CSV}")


if __name__ == "__main__":
    main()
