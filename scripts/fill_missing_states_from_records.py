#!/usr/bin/env python3
"""
Fill missing state for students in students.csv per prompts/fill-missing-state.md.
Look up state by student_id only (never by name). Priority: (1) Mathcounts, AMO, JMO,
(2) other contest CSVs with state column, (3) team name when it clearly indicates state.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Dict, Set

ROOT = Path(__file__).resolve().parent.parent
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
CONTESTS_DIR = ROOT / "database" / "contests"

# US state names (and DC) for team-name inference; check longer phrases first.
STATE_NAMES = [
    "Rhode Island",
    "New York",
    "New Jersey",
    "New Hampshire",
    "New Mexico",
    "North Carolina",
    "North Dakota",
    "South Carolina",
    "South Dakota",
    "West Virginia",
    "District of Columbia",
    "Washington",  # state; DC is "District of Columbia"
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
    "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Tennessee", "Texas", "Utah", "Vermont",
    "Virginia", "Wisconsin", "Wyoming",
]


def _read_state_from_csv(csv_path: Path, state_by_sid: Dict[int, str]) -> None:
    """Read CSV with student_id and state; fill state_by_sid only for new keys."""
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = [fn.strip() for fn in (reader.fieldnames or [])]
        if "student_id" not in fieldnames or "state" not in fieldnames:
            return
        for row in reader:
            sid_raw = (row.get("student_id") or "").strip()
            if not sid_raw:
                continue
            try:
                sid = int(sid_raw)
            except ValueError:
                continue
            state = (row.get("state") or "").strip()
            if not state:
                continue
            if sid not in state_by_sid:
                state_by_sid[sid] = state


def build_state_map() -> Dict[int, str]:
    """Build student_id -> state from contest CSVs in priority order (prompt 2.1, 2.2):
    1) mathcounts-national, 2) mathcounts-national-rank, 3) amo, 4) jmo, 5) other contests.
    """
    state_by_sid: Dict[int, str] = {}

    # 2.1 Mathcounts, AMO, JMO (all have state)
    for folder in ("mathcounts-national", "mathcounts-national-rank", "amo", "jmo"):
        path = CONTESTS_DIR / folder
        if path.exists():
            for csv_path in sorted(path.rglob("*.csv")):
                _read_state_from_csv(csv_path, state_by_sid)

    # 2.2 Other contest CSVs that have student_id and state
    for csv_path in sorted(CONTESTS_DIR.rglob("*.csv")):
        if any(x in str(csv_path) for x in ("mathcounts-national", "/amo/", "/jmo/")):
            continue
        _read_state_from_csv(csv_path, state_by_sid)

    return state_by_sid


def _state_from_team_name(team_name: str) -> str | None:
    """If team_name clearly indicates a US state, return it; else None."""
    if not (team_name or "").strip():
        return None
    t = " " + (team_name.strip()) + " "
    for state in STATE_NAMES:
        # Word boundary or start/end so "New York" matches but "New Yorker" is ambiguous
        if re.search(r"(^|\s)" + re.escape(state) + r"(\s|$|[,\"])", t, re.IGNORECASE):
            return state
    return None


def build_team_state_map() -> Dict[int, str]:
    """Build team_id -> state from contest team CSVs when team_name clearly indicates state."""
    team_state: Dict[int, str] = {}
    for csv_path in CONTESTS_DIR.rglob("teams.csv"):
        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fn = [x.strip() for x in (reader.fieldnames or [])]
            if "team_id" not in fn or "team_name" not in fn:
                continue
            for row in reader:
                tid_raw = (row.get("team_id") or "").strip()
                tname = (row.get("team_name") or "").strip()
                if not tid_raw or not tname:
                    continue
                try:
                    tid = int(tid_raw)
                except ValueError:
                    continue
                if tid in team_state:
                    continue
                state = _state_from_team_name(tname)
                if state:
                    team_state[tid] = state
    return team_state


def main() -> None:
    state_by_sid = build_state_map()
    team_state = build_team_state_map()

    # Read all student rows
    with STUDENTS_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    missing_before: Set[int] = set()
    updates: Dict[int, str] = {}
    from_contest = 0
    from_team = 0

    for row in rows:
        sid_raw = (row.get("student_id") or "").strip()
        try:
            sid = int(sid_raw)
        except ValueError:
            continue
        existing_state = (row.get("state") or "").strip()
        if not existing_state:
            missing_before.add(sid)
            if sid in state_by_sid:
                updates[sid] = state_by_sid[sid]
                from_contest += 1
            else:
                # 2.3 State from team name (only when student has team_ids and we have a state for that team)
                team_ids_raw = (row.get("team_ids") or "").strip()
                if team_ids_raw:
                    for part in team_ids_raw.split("|"):
                        part = part.strip()
                        if not part:
                            continue
                        try:
                            tid = int(part)
                            if tid in team_state:
                                updates[sid] = team_state[tid]
                                from_team += 1
                                break
                        except ValueError:
                            continue

    for row in rows:
        sid_raw = (row.get("student_id") or "").strip()
        try:
            sid = int(sid_raw)
        except ValueError:
            continue
        if sid in updates:
            row["state"] = updates[sid]

    safe_fieldnames = [f for f in fieldnames if f is not None]
    tmp_path = STUDENTS_CSV.with_suffix(".csv.tmp")
    with tmp_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=safe_fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    tmp_path.replace(STUDENTS_CSV)

    still_missing = missing_before - set(updates.keys())
    print(f"Students that had no state: {len(missing_before)}")
    print(f"State found (contest records): {from_contest}")
    print(f"State found (team name): {from_team}")
    print(f"Cannot find state (left blank): {len(still_missing)}")


if __name__ == "__main__":
    main()
