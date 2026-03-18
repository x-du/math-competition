#!/usr/bin/env python3
"""
Add MMATHs team names from a year's results to teams.csv and update team_ids in students.csv.
Run from repo root: python scripts/add_mmaths_teams_to_registry.py [year]
Default year: 2024. Example for 2025: python scripts/add_mmaths_teams_to_registry.py 2025
"""
import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEAMS_CSV = REPO / "database/students/teams.csv"
STUDENTS_CSV = REPO / "database/students/students.csv"


def main():
    year = (sys.argv[1] if len(sys.argv) > 1 else "2024").strip()
    mmaths_results = REPO / f"database/contests/mmaths/year={year}/results.csv"
    if not mmaths_results.exists():
        print(f"Results file not found: {mmaths_results}")
        sys.exit(1)
    # Load existing teams: team_name -> team_id (strip for match)
    name_to_id = {}
    max_id = 0
    with TEAMS_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tid_raw = (row.get("team_id") or "").strip()
            if not tid_raw:
                continue
            try:
                tid = int(tid_raw)
            except ValueError:
                continue
            max_id = max(max_id, tid)
            name = (row.get("team_name") or "").strip()
            if name:
                name_to_id[name] = tid

    # Unique team names from MMATHs results
    results_teams = set()
    student_team: list[tuple[int, str]] = []  # (student_id, team_name)
    with mmaths_results.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            team = (row.get("team") or "").strip()
            if not team:
                continue
            sid_raw = (row.get("student_id") or "").strip()
            if not sid_raw:
                continue
            try:
                sid = int(sid_raw)
            except ValueError:
                continue
            results_teams.add(team)
            student_team.append((sid, team))

    # Assign new team_ids for teams not in registry
    new_teams = []
    for name in sorted(results_teams):
        if name not in name_to_id:
            max_id += 1
            name_to_id[name] = max_id
            new_teams.append((max_id, name))

    # Append new teams to teams.csv
    if new_teams:
        with TEAMS_CSV.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for tid, name in new_teams:
                writer.writerow([tid, name, ""])
        print(f"Added {len(new_teams)} new teams to {TEAMS_CSV}")

    # Build student_id -> set of team_ids (from this contest)
    sid_to_team_ids: dict[int, set[int]] = {}
    for sid, team_name in student_team:
        tid = name_to_id.get(team_name)
        if tid is not None:
            sid_to_team_ids.setdefault(sid, set()).add(tid)

    # Load students, update team_ids
    rows = []
    with STUDENTS_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = [c for c in (reader.fieldnames or []) if c is not None]
        for row in reader:
            sid_raw = (row.get("student_id") or "").strip()
            if not sid_raw:
                rows.append({k: row.get(k) for k in fieldnames})
                continue
            try:
                sid = int(sid_raw)
            except ValueError:
                rows.append({k: row.get(k) for k in fieldnames})
                continue
            existing = (row.get("team_ids") or "").strip()
            existing_ids = set()
            for x in existing.split("|"):
                x = x.strip()
                if x:
                    try:
                        existing_ids.add(int(x))
                    except ValueError:
                        pass
            new_ids = sid_to_team_ids.get(sid, set())
            existing_ids.update(new_ids)
            clean = {k: row.get(k) for k in fieldnames}
            if existing_ids:
                clean["team_ids"] = "|".join(str(i) for i in sorted(existing_ids))
            else:
                clean["team_ids"] = ""
            rows.append(clean)

    with STUDENTS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Updated team_ids in {STUDENTS_CSV} for {len(sid_to_team_ids)} MMATHs {year} participants")


if __name__ == "__main__":
    main()
