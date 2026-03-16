#!/usr/bin/env python3
"""
Look up student's state using:
1. Database: contest records (AMO, JMO, Mathcounts, MPFG, etc.) that include state
2. Database: teammate states - if teammates on same team have state, infer from majority
3. Database: team/school name -> state mapping (Enloe Eagles->NC, McLean HS->VA, etc.)
4. Web search: "name + math" - use DuckDuckGo or manual lookup (outputs search queries for user)

Search team = "student_name + math" per user spec.

Usage:
  python scripts/lookup_student_state_web.py [--dry-run] [--apply]
  --dry-run   Only output inferred states, don't update CSV
  --apply     Update students.csv with inferred states (accuracy >= 80)
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parent.parent
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
TEAMS_CSV = ROOT / "database" / "students" / "teams.csv"
CONTESTS_DIR = ROOT / "database" / "contests"
INCOMPLETE_JSON = ROOT / "incomplete_students.json"
OUTPUT_JSON = ROOT / "inferred_states_from_lookup.json"

ACCURACY_THRESHOLD = 80

# Team/school name -> (state, accuracy). From web research and database analysis.
# Search: "name + math" to find LinkedIn/school pages.
TEAM_SCHOOL_TO_STATE: List[Tuple[str | re.Pattern, str, int]] = [
    # International (non-US)
    ("mg varna", "Bulgaria", 95),
    ("varna a", "Bulgaria", 90),
    ("mix bg", "Bulgaria", 95),
    ("burgas a", "Bulgaria", 92),
    ("burgas b", "Bulgaria", 92),
    ("bulgaria mixed", "Bulgaria", 95),
    # US schools - high confidence
    ("enloe eagles", "North Carolina", 92),  # Enloe HS, Raleigh NC
    ("mclean hs", "Virginia", 92),  # McLean HS, Fairfax County VA
    ("mclean high school", "Virginia", 92),
    ("mocoswagga", "Maryland", 88),  # MoCo = Montgomery County MD
    ("moco ", "Maryland", 85),
    ("lexington delta", "Massachusetts", 90),  # Lexington HS, Lexington MA
    ("lexington gamma", "Massachusetts", 90),
    ("lexington alpha", "Massachusetts", 90),
    ("texas ampere", "Texas", 95),
    ("super 88", "Texas", 75),  # Texas-based math circle
    ("mock turtle", "New Jersey", 75),
    ("white rabbit", "New Jersey", 75),
    ("green hamsters", "New Jersey", 70),
    ("six-o-mode", "Illinois", 80),  # Chicago area
    ("math school i", "Illinois", 75),
    ("no coast best coast", "Minnesota", 75),  # "No coast" = landlocked / Midwest
    ("flip-flops math", "California", 70),
    ("eddiesolo", "California", 70),  # Eddie Wei - often CA based
]


def load_missing_state() -> Tuple[Set[int], Dict[int, str]]:
    """Load missing_state from incomplete_students.json."""
    if not INCOMPLETE_JSON.exists():
        raise FileNotFoundError(f"Missing {INCOMPLETE_JSON}")
    with INCOMPLETE_JSON.open(encoding="utf-8") as f:
        data = json.load(f)
    missing = data.get("missing_state") or []
    ids: Set[int] = set()
    id_to_name: Dict[int, str] = {}
    for entry in missing:
        sid_raw = entry.get("student_id")
        if not sid_raw:
            continue
        try:
            sid = int(sid_raw)
        except ValueError:
            continue
        ids.add(sid)
        id_to_name[sid] = (entry.get("student_name") or "").strip()
    return ids, id_to_name


def load_students() -> Dict[int, dict]:
    """Load students.csv as student_id -> row dict."""
    rows: Dict[int, dict] = {}
    with STUDENTS_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid_raw = (row.get("student_id") or "").strip()
            try:
                sid = int(sid_raw)
                rows[sid] = dict(row)
            except ValueError:
                pass
    return rows


def load_teams() -> Dict[int, str]:
    """Load teams.csv as team_id -> team_name."""
    teams: Dict[int, str] = {}
    with TEAMS_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tid_raw = (row.get("team_id") or "").strip()
            tname = (row.get("team_name") or "").strip()
            try:
                tid = int(tid_raw)
                teams[tid] = tname
            except ValueError:
                pass
    return teams


def state_from_team_name(team_name: str) -> Tuple[str | None, int]:
    """Infer state from team/school name using TEAM_SCHOOL_TO_STATE."""
    n = (team_name or "").strip().lower()
    if not n:
        return None, 0
    best_state: str | None = None
    best_acc = 0
    for key, state, acc in TEAM_SCHOOL_TO_STATE:
        if isinstance(key, re.Pattern):
            if key.search(n) and acc > best_acc:
                best_state = state
                best_acc = acc
        else:
            if key in n and acc > best_acc:
                best_state = state
                best_acc = acc
    return best_state, best_acc


def collect_state_from_contests() -> Dict[int, str]:
    """Collect student_id -> state from contest CSVs that have a state column."""
    sid_to_state: Dict[int, str] = {}
    for csv_path in sorted(CONTESTS_DIR.rglob("*.csv")):
        if "teams.csv" in str(csv_path):
            continue
        try:
            with csv_path.open(newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                fn = [x.strip() for x in (reader.fieldnames or [])]
                if "state" not in fn or "student_id" not in fn:
                    continue
                for row in reader:
                    sid_raw = (row.get("student_id") or "").strip()
                    state_raw = (row.get("state") or "").strip()
                    if not sid_raw or not state_raw:
                        continue
                    try:
                        sid = int(sid_raw)
                        sid_to_state[sid] = state_raw
                    except ValueError:
                        pass
        except Exception:
            continue
    return sid_to_state


def infer_from_teammates(
    students: Dict[int, dict],
    missing_ids: Set[int],
    teams: Dict[int, str],
) -> Dict[int, Tuple[str, int]]:
    """
    For each missing_state student, if they share a team with students who have state,
    infer state from majority of teammates. Returns student_id -> (state, accuracy).
    """
    # Build team_id -> set of student_ids
    team_to_students: Dict[int, Set[int]] = {}
    for sid, row in students.items():
        team_ids_raw = (row.get("team_ids") or "").strip()
        for part in team_ids_raw.split("|"):
            part = part.strip()
            if not part:
                continue
            try:
                tid = int(part)
                if tid not in team_to_students:
                    team_to_students[tid] = set()
                team_to_students[tid].add(sid)
            except ValueError:
                pass

    # For each missing student, get teammates' states
    result: Dict[int, Tuple[str, int]] = {}
    for sid in missing_ids:
        if sid not in students:
            continue
        row = students[sid]
        team_ids_raw = (row.get("team_ids") or "").strip()
        state_counts: Dict[str, int] = {}
        for part in team_ids_raw.split("|"):
            part = part.strip()
            if not part:
                continue
            try:
                tid = int(part)
            except ValueError:
                continue
            for teammate_id in team_to_students.get(tid, set()):
                if teammate_id == sid:
                    continue
                trow = students.get(teammate_id)
                if not trow:
                    continue
                tstate = (trow.get("state") or "").strip()
                if tstate:
                    state_counts[tstate] = state_counts.get(tstate, 0) + 1
        if state_counts:
            best_state = max(state_counts, key=state_counts.get)  # type: ignore
            total = sum(state_counts.values())
            # Accuracy based on consistency
            acc = min(90, 70 + (state_counts[best_state] - 1) * 10)
            result[sid] = (best_state, acc)
    return result


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    apply_mode = "--apply" in sys.argv

    missing_ids, id_to_name = load_missing_state()
    print(f"Students missing state: {len(missing_ids)}")

    students = load_students()
    teams = load_teams()

    # 1. State from contest records (highest priority)
    contest_states = collect_state_from_contests()
    from_contest = {sid: contest_states[sid] for sid in missing_ids if sid in contest_states}
    print(f"  From contest records: {len(from_contest)}")

    # 2. State from teammates
    teammate_infer = infer_from_teammates(students, missing_ids, teams)
    from_teammates = {
        sid: (s, a) for sid, (s, a) in teammate_infer.items()
        if sid not in from_contest
    }
    print(f"  From teammates (candidates): {len(from_teammates)}")

    # 3. State from team/school name
    from_team_name: Dict[int, Tuple[str, int]] = {}
    for sid in missing_ids:
        if sid in from_contest:
            continue
        row = students.get(sid)
        if not row:
            continue
        team_ids_raw = (row.get("team_ids") or "").strip()
        best_state: str | None = None
        best_acc = 0
        for part in team_ids_raw.split("|"):
            part = part.strip()
            if not part:
                continue
            try:
                tid = int(part)
            except ValueError:
                continue
            tname = teams.get(tid, "")
            s, a = state_from_team_name(tname)
            if s and a > best_acc:
                best_state = s
                best_acc = a
        if best_state:
            from_team_name[sid] = (best_state, best_acc)
    print(f"  From team/school name: {len(from_team_name)}")

    # Combine: contest > teammate (if acc>=80) > team_name (if acc>=80)
    updates: Dict[int, str] = {}
    source: Dict[int, str] = {}

    for sid in missing_ids:
        if sid in from_contest:
            updates[sid] = from_contest[sid]
            source[sid] = "contest"
            continue
        if sid in from_teammates:
            s, a = from_teammates[sid]
            if a >= ACCURACY_THRESHOLD:
                updates[sid] = s
                source[sid] = "teammates"
                continue
        if sid in from_team_name:
            s, a = from_team_name[sid]
            if a >= ACCURACY_THRESHOLD:
                updates[sid] = s
                source[sid] = "team_name"
                continue

    # Build output for web search - students still missing state
    still_missing = missing_ids - set(updates.keys())
    web_queries = [
        {"student_id": sid, "student_name": id_to_name.get(sid, ""), "search": f"{id_to_name.get(sid, '')} math"}
        for sid in sorted(still_missing)
    ]

    # Output JSON
    out = {
        "inferred": [
            {
                "student_id": sid,
                "student_name": id_to_name.get(sid, ""),
                "state": updates[sid],
                "source": source.get(sid, ""),
            }
            for sid in sorted(updates.keys())
        ],
        "still_missing_count": len(still_missing),
        "web_search_queries": web_queries[:100],  # First 100 for manual lookup
        "summary": {
            "from_contest": len(from_contest),
            "from_teammates": sum(1 for sid in from_teammates if from_teammates[sid][1] >= ACCURACY_THRESHOLD),
            "from_team_name": sum(1 for sid in from_team_name if from_team_name[sid][1] >= ACCURACY_THRESHOLD),
            "total_inferred": len(updates),
        },
    }
    with OUTPUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {OUTPUT_JSON}")
    print(f"Total inferred: {len(updates)}")
    print(f"Still missing: {len(still_missing)}")
    if still_missing and web_queries:
        print(f"\nWeb search queries (use 'name + math'): first 5:")
        for q in web_queries[:5]:
            print(f"  {q['student_id']}: {q['search']}")

    if dry_run:
        print("\n[DRY RUN] Would update:")
        for sid in sorted(updates.keys())[:20]:
            print(f"  {sid}: {updates[sid]} ({source.get(sid, '')})")
        if len(updates) > 20:
            print(f"  ... and {len(updates)-20} more")
        return

    if apply_mode and updates:
        with STUDENTS_CSV.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames or [])
            rows = list(reader)
        for row in rows:
            sid_raw = (row.get("student_id") or "").strip()
            try:
                sid = int(sid_raw)
            except ValueError:
                continue
            if sid in updates:
                row["state"] = updates[sid]
        tmp_path = STUDENTS_CSV.with_suffix(".csv.tmp")
        with tmp_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        tmp_path.replace(STUDENTS_CSV)
        print(f"\nUpdated {len(updates)} rows in {STUDENTS_CSV}")


if __name__ == "__main__":
    main()
