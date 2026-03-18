#!/usr/bin/env python3
"""
Infer student state from school_team_for_state_inference.json using a web-researched
mapping of school/team names to (state, accuracy). Update students.csv only when
accuracy > 80%.

Usage: python scripts/fill_state_from_school_team_web.py [--dry-run]
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
SCHOOL_TEAM_JSON = ROOT / "school_team_for_state_inference.json"
ACCURACY_THRESHOLD = 80

# School/team name (lowercase) or pattern -> (state, accuracy 0-100).
# Built from web search: verified school locations and state-in-name patterns.
SCHOOL_TEAM_TO_STATE: list[tuple[str | re.Pattern, str, int]] = [
    # State explicitly in name (accuracy 95)
    (re.compile(r"^texas\s+a\d*$", re.I), "Texas", 95),
    (re.compile(r"^colorado\s+b\d*$", re.I), "Colorado", 95),
    (re.compile(r"^minnesota\s+b\d*$", re.I), "Minnesota", 95),
    (re.compile(r"^washington\s+a\d*$", re.I), "Washington", 95),
    (re.compile(r"^florida\s+a\d*$", re.I), "Florida", 95),
    (re.compile(r"^ohio\s+b\d*$", re.I), "Ohio", 95),
    (re.compile(r"^montgomery\s+b\d*$", re.I), "Maryland", 95),
    (re.compile(r"^nc\s+a\d*$", re.I), "North Carolina", 95),
    (re.compile(r"^ncssm\b", re.I), "North Carolina", 95),
    (re.compile(r"sfba|norcal", re.I), "California", 95),
    (re.compile(r"^dallas\s+individuals", re.I), "Texas", 95),
    (re.compile(r"^ontario\s+math\s+circles", re.I), "Ontario, Canada", 95),
    (re.compile(r"^mass\s+arml", re.I), "Massachusetts", 95),
    (re.compile(r"^co\s+mathletes", re.I), "Colorado", 95),
    # Verified schools (accuracy 88–92)
    ("pingry", "New Jersey", 92),
    ("prisms", "New Jersey", 90),
    ("young falcons", "New Jersey", 90),
    ("baby falcons", "New Jersey", 90),
    ("future falcons", "New Jersey", 90),
    ("falcons", "New Jersey", 88),  # PRISMS Falcons; after more specific
    ("jericho high school", "New York", 92),
    ("jericho mathletes", "New York", 92),
    ("jericho a", "New York", 90),
    ("jericho b", "New York", 90),
    ("hotchkiss", "Connecticut", 92),
    ("edison academy magnet school", "New Jersey", 92),
    ("central regional", "New Jersey", 90),
    ("crh math team", "New Jersey", 90),
    ("crh ", "New Jersey", 88),
    ("crh", "New Jersey", 85),
    ("sierra canyon school", "California", 92),
    ("sierra canyon", "California", 90),
    ("ward melville", "New York", 92),
    ("millburn", "New Jersey", 92),
    ("bergen county academies", "New Jersey", 90),
    ("bca 2", "New Jersey", 90),
    ("bca ", "New Jersey", 88),
    ("gunn math", "California", 92),
    ("gunn", "California", 90),
    ("lexington alpha", "Massachusetts", 90),
    ("lexington gamma", "Massachusetts", 90),
    ("lexington muztaba", "Massachusetts", 88),
    ("thomas jefferson", "Virginia", 90),
    ("tjhsst", "Virginia", 92),
    ("ardrey kell", "North Carolina", 92),
    ("garnet valley", "Pennsylvania", 92),
    ("gvhs math club", "Pennsylvania", 90),
    ("conestoga", "Pennsylvania", 90),
    ("stoga", "Pennsylvania", 92),
    ("phillips academy andover", "Massachusetts", 92),
    ("wellesley", "Massachusetts", 92),
    ("wellesley raiders", "Massachusetts", 90),
    ("cambridge rindge", "Massachusetts", 90),
    ("crls omega", "Massachusetts", 90),
    ("crls", "Massachusetts", 88),
    ("novi unicorns", "Michigan", 90),
    ("novi", "Michigan", 88),
    ("cranbrook", "Michigan", 92),
    ("stanford online hs", "California", 90),
    ("stanford ohs", "California", 90),
    ("davidson academy", "Nevada", 90),
    ("davidson academy online", "Nevada", 90),
    ("bayside academy", "California", 92),
    ("westchester area math circle", "New York", 88),
    ("ridge mu alpha theta", "New Jersey", 90),
    ("ridge high school", "New Jersey", 88),
    ("princeton high school", "New Jersey", 88),
    ("phs avocado", "New Jersey", 88),
    ("phs blueberry", "New Jersey", 88),
    ("phs apricot", "New Jersey", 88),
    ("phs math team", "New Jersey", 88),
    ("phs ", "New Jersey", 82),
    ("tenafly high school", "New Jersey", 90),
    ("tenafly", "New Jersey", 88),
    ("arcadia high school", "California", 90),
    ("arcadia", "California", 88),
    ("river hill", "Maryland", 90),
    ("le club mathematique de river hill", "Maryland", 90),
    ("doral academy", "Florida", 90),
    ("plano west", "Texas", 90),
    ("pesh math club", "Texas", 88),
    ("academies math team", "New Jersey", 82),
    ("dmv math circle", "Maryland", 85),
    ("dmv math circle sigma", "Maryland", 85),
    ("dmv math circle alpha", "Maryland", 85),
    ("newark red team", "New Jersey", 88),
    ("greater boston", "Massachusetts", 88),
    ("cheshire cats", "Connecticut", 85),
    ("moco rockets", "Maryland", 88),
    ("not great valley", "Pennsylvania", 88),
    ("theta math club", "New York", 85),
    ("knights b", "New York", 85),
    ("knights beta", "New York", 85),
    ("knights y", "New York", 85),
    ("oss orcas", "Washington", 82),
    ("oss orcas team 1", "Washington", 82),
    ("evergreen ms", "Washington", 85),
    ("usc individuals", "California", 88),
    ("ndhs", "New York", 85),
    ("green hamsters", "New Jersey", 85),
    # From lookup_student_state_web research
    ("enloe eagles", "North Carolina", 92),
    ("mclean hs", "Virginia", 92),
    ("mclean high school", "Virginia", 92),
    ("mocoswagga", "Maryland", 88),
    ("moco rockets", "Maryland", 88),
    ("montgomery county team 1", "Maryland", 90),
    ("texas ampere", "Texas", 95),
    ("mg varna", "Bulgaria", 95),
    ("mix bg", "Bulgaria", 95),
    ("burgas a", "Bulgaria", 92),
    ("burgas b", "Bulgaria", 92),
    ("bulgaria mixed", "Bulgaria", 95),
    # From web research for incomplete_students (prompts/fill-missing-state.md)
    ("vamc", "Virginia", 90),  # Virginia math circles
    ("vamc2025", "Virginia", 90),
    ("wwp charizard", "New Jersey", 90),  # West Windsor-Plainsboro NJ
    ("wwp ", "New Jersey", 88),
    ("stearns middle school", "Maine", 88),  # Stearns Jr-Sr, Millinocket ME
    ("stearns jr-sr", "Maine", 90),
    ("mca underdogs", "New Jersey", 88),  # MCA Math League, Middlesex County Academy NJ
    ("mca math league", "New Jersey", 90),
    ("bulgaria 1", "Bulgaria", 95),
]

# Non-US or ambiguous: do not assign US state (skip or use as Canada)
NON_US_PATTERNS = [
    re.compile(r"shanghai", re.I),
    re.compile(r"starriver", re.I),
]


def normalize(s: str) -> str:
    return (s or "").strip().lower()


def infer_state_and_accuracy(schools_and_teams: list[str]) -> tuple[str | None, int]:
    """Return (state, best_accuracy) for the list of school/team names. Uses highest accuracy match."""
    if not schools_and_teams:
        return None, 0
    best_state: str | None = None
    best_acc = 0
    for name in schools_and_teams:
        n = normalize(name)
        if not n:
            continue
        skip_name = False
        for pat in NON_US_PATTERNS:
            if pat.search(n):
                skip_name = True
                break
        if skip_name:
            continue
        for key, state, acc in SCHOOL_TEAM_TO_STATE:
            if isinstance(key, re.Pattern):
                if key.search(n):
                    if acc > best_acc:
                        best_state = state
                        best_acc = acc
                    break
            else:
                if key in n:
                    if acc > best_acc:
                        best_state = state
                        best_acc = acc
                    break
    return best_state, best_acc


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    if not SCHOOL_TEAM_JSON.exists():
        print(f"Missing {SCHOOL_TEAM_JSON}", file=sys.stderr)
        sys.exit(1)
    with SCHOOL_TEAM_JSON.open(encoding="utf-8") as f:
        entries = json.load(f)
    updates: dict[int, str] = {}
    skipped_low = 0
    skipped_unknown = 0
    for rec in entries:
        sid = rec.get("student_id")
        if sid is None:
            continue
        try:
            sid = int(sid)
        except (TypeError, ValueError):
            continue
        schools = rec.get("schools_and_teams") or []
        state, acc = infer_state_and_accuracy(schools)
        if state and acc > ACCURACY_THRESHOLD:
            updates[sid] = state
        elif state:
            skipped_low += 1
        else:
            skipped_unknown += 1
    print(f"Inferred state with accuracy > {ACCURACY_THRESHOLD}: {len(updates)}")
    print(f"Skipped (low accuracy): {skipped_low}, unknown: {skipped_unknown}")
    if dry_run:
        print("\n[DRY RUN] Would update students.csv with:")
        for sid in sorted(updates.keys()):
            print(f"  student_id={sid} -> state={updates[sid]}")
        return
    if not updates:
        return
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
    print(f"Updated {len(updates)} rows in {STUDENTS_CSV}")


if __name__ == "__main__":
    main()
