#!/usr/bin/env python3
"""
Build teams.csv for BMT from database/contests/bmt/year=<year>/results.csv.

BMT results already have team_name and school columns. This script:
1. Aggregates students by team_name (non-empty)
2. Creates database/contests/bmt-teams/year=<year>/teams.csv
   Schema: team_id, team_name, student_ids, state
3. Infers state from students.csv (most common state among team members)
"""

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BMT_RESULTS = ROOT / "database" / "contests" / "bmt"
BMT_TEAMS = ROOT / "database" / "contests" / "bmt-teams"
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"


def load_student_states() -> dict[int, str]:
    """Load student_id -> state from students.csv."""
    result: dict[int, str] = {}
    if not STUDENTS_CSV.exists():
        return result
    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid_s = (row.get("student_id") or "").strip()
            state = (row.get("state") or "").strip()
            if not sid_s:
                continue
            try:
                sid = int(sid_s)
                if state:
                    result[sid] = state
            except ValueError:
                pass
    return result


def infer_team_state(student_ids: list[int], states: dict[int, str]) -> str:
    """Infer team state from member states. Use most common; empty if none."""
    member_states = [states[sid] for sid in student_ids if sid in states and states[sid]]
    if not member_states:
        return ""
    counts = Counter(member_states)
    return counts.most_common(1)[0][0]


def build_teams_for_year(year: str, states: dict[int, str]) -> list[dict]:
    """Build teams from BMT results for a given year."""
    results_path = BMT_RESULTS / f"year={year}" / "results.csv"
    if not results_path.exists():
        return []

    team_to_student_ids: dict[str, set[int]] = {}
    with open(results_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            team_name = (row.get("team_name") or "").strip()
            if not team_name:
                continue
            sid_s = (row.get("student_id") or "").strip()
            if not sid_s:
                continue
            try:
                sid = int(sid_s)
            except ValueError:
                continue
            if team_name not in team_to_student_ids:
                team_to_student_ids[team_name] = set()
            team_to_student_ids[team_name].add(sid)

    teams: list[dict] = []
    for i, (team_name, sids) in enumerate(sorted(team_to_student_ids.items()), start=1):
        sids_list = sorted(sids)
        state = infer_team_state(sids_list, states)
        teams.append({
            "team_id": str(i),
            "team_name": team_name,
            "student_ids": "|".join(str(s) for s in sids_list),
            "state": state,
        })
    return teams


def main() -> None:
    states = load_student_states()
    print(f"Loaded {len(states)} student states")

    for year in ("2023", "2025"):
        teams = build_teams_for_year(year, states)
        if not teams:
            print(f"No teams for year {year} (results not found or no team names)")
            continue

        out_dir = BMT_TEAMS / f"year={year}"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "teams.csv"

        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["team_id", "team_name", "student_ids", "state"])
            writer.writeheader()
            writer.writerows(teams)

        print(f"Wrote {len(teams)} teams to {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
