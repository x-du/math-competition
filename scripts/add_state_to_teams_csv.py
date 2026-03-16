#!/usr/bin/env python3
"""
Add state column to all teams.csv files in database/contests.

State is inferred from team members (student_ids): use the most common state
among students who have a state. If no students have state, leave empty.
"""

from collections import Counter
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
CONTESTS_DIR = ROOT / "database" / "contests"


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


def process_teams_csv(path: Path, states: dict[int, str]) -> bool:
    """Add state column to a teams.csv. Returns True if modified."""
    rows: list[dict[str, str]] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        if "state" in fieldnames:
            return False  # Already has state
        fieldnames.append("state")
        for row in reader:
            student_ids_raw = (row.get("student_ids") or "").strip()
            sids = []
            for part in student_ids_raw.split("|"):
                part = part.strip()
                if not part:
                    continue
                try:
                    sids.append(int(part))
                except ValueError:
                    pass
            state = infer_team_state(sids, states)
            new_row = dict(row)
            new_row["state"] = state
            rows.append(new_row)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return True


def main() -> None:
    states = load_student_states()
    print(f"Loaded {len(states)} student states")

    teams_files = sorted(CONTESTS_DIR.rglob("teams.csv"))
    print(f"Found {len(teams_files)} teams.csv files")

    for path in teams_files:
        rel = path.relative_to(ROOT)
        if process_teams_csv(path, states):
            print(f"  Updated {rel}")
        else:
            print(f"  Skipped (already has state): {rel}")


if __name__ == "__main__":
    main()
