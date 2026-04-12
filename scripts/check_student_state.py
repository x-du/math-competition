#!/usr/bin/env python3
"""
Check that BMT-style team rosters match geography: when `teams.csv` lists a
non-empty `state` for a team, every student on that team should have the
same `state` in `database/students/students.csv`.

Teams layout:
  database/contests/<slug>-teams/year=<year>/teams.csv

The contest slug is the main competition folder name (e.g. `bmt` → `bmt-teams`).

Run from repo root:

    python scripts/check_student_state.py bmt
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DATABASE = REPO_ROOT / "database"
CONTESTS_DIR = DATABASE / "contests"
STUDENTS_CSV = DATABASE / "students" / "students.csv"


def teams_root_for_slug(slug: str) -> Path:
    s = slug.strip()
    if not s:
        raise ValueError("contest slug must be non-empty")
    if s.endswith("-teams"):
        return CONTESTS_DIR / s
    return CONTESTS_DIR / f"{s}-teams"


def load_student_states() -> dict[str, str]:
    """student_id str -> state str (may be empty)."""
    out: dict[str, str] = {}
    if not STUDENTS_CSV.is_file():
        return out
    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sid = str(row.get("student_id") or "").strip()
            if not sid:
                continue
            out[sid] = (row.get("state") or "").strip()
    return out


def iter_team_rows(teams_csv: Path):
    with open(teams_csv, newline="", encoding="utf-8") as f:
        yield from csv.DictReader(f)


def check_year(
    teams_root_name: str,
    teams_csv: Path,
    student_state: dict[str, str],
) -> list[str]:
    warnings: list[str] = []
    prefix = f"{teams_root_name}/{teams_csv.parent.name}"

    for row in iter_team_rows(teams_csv):
        team_id = (row.get("team_id") or "").strip()
        team_state = (row.get("state") or "").strip()
        raw_ids = (row.get("student_ids") or "").strip()
        if not team_state or not raw_ids:
            continue

        sids = [p.strip() for p in raw_ids.split("|") if p.strip()]
        if not sids:
            continue

        per_student: list[tuple[str, str]] = []
        for sid in sids:
            st = student_state.get(sid, "")
            per_student.append((sid, st))

        def sid_key(t: tuple[str, str]):
            s = t[0]
            return int(s) if s.isdigit() else s

        non_empty = {st for _, st in per_student if st}
        detail = ", ".join(
            f"{sid}={st or '(empty)'}" for sid, st in sorted(per_student, key=sid_key)
        )

        if len(non_empty) > 1:
            warnings.append(
                f"WARNING [{prefix} team_id={team_id}]: roster has multiple different student states: {detail}"
            )
            continue

        empty_sids = [sid for sid, st in per_student if not st]
        if len(non_empty) == 0:
            warnings.append(
                f"WARNING [{prefix} team_id={team_id}]: teams.csv state={team_state!r} but no student has state in students.csv: {detail}"
            )
            continue

        roster_state = next(iter(non_empty))
        if roster_state != team_state:
            warnings.append(
                f"WARNING [{prefix} team_id={team_id}]: teams.csv state={team_state!r} but student roster state is {roster_state!r}: {detail}"
            )
        elif empty_sids:
            warnings.append(
                f"WARNING [{prefix} team_id={team_id}]: teams.csv state={team_state!r} matches roster, but some students lack state in students.csv ({','.join(empty_sids)}): {detail}"
            )

    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Warn when team state in teams.csv does not match student states in students.csv."
    )
    parser.add_argument(
        "contest_slug",
        help="Contest folder name, e.g. bmt (uses database/contests/<slug>-teams/).",
    )
    args = parser.parse_args()

    try:
        teams_root = teams_root_for_slug(args.contest_slug)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2

    if not teams_root.is_dir():
        print(f"ERROR: teams directory not found: {teams_root}", file=sys.stderr)
        return 2

    student_state = load_student_states()
    if not student_state and STUDENTS_CSV.is_file():
        print(f"WARNING: no rows loaded from {STUDENTS_CSV}", file=sys.stderr)

    all_warnings: list[str] = []
    for year_dir in sorted(teams_root.iterdir()):
        if not year_dir.is_dir() or not year_dir.name.startswith("year="):
            continue
        teams_csv = year_dir / "teams.csv"
        if not teams_csv.is_file():
            continue
        all_warnings.extend(check_year(teams_root.name, teams_csv, student_state))

    if not all_warnings:
        print(f"OK: no state mismatches under {teams_root.relative_to(REPO_ROOT)}")
        return 0

    for line in all_warnings:
        print(line, file=sys.stderr)
    print(f"Total warnings: {len(all_warnings)}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
