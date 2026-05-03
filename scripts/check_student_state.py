#!/usr/bin/env python3
"""
Check team rosters against `database/students/students.csv` state field.

Reports WARNING when (skipped entirely when **`team_name`** is **`Individuals`**
or starts with **`Individuals `**, e.g. **`Individuals 1`**, or contains **`Leading Aces Academy`**;
or **`bmt-teams`** rows whose **`school`** is **`Think Academy Online`**):

  1. On the same team, two or more students with non-empty states have
     different states (exceptions: Connecticut + New York; Connecticut + New Jersey;
     Maryland + Virginia; Arizona + California; California + Nevada;
     New Jersey + Pennsylvania + New York together;
     any roster that includes **`State Department`** (mixable with other states); or **`teams.csv` team `state`
     is **`China`** allowing mixed member geography). If **`teams.csv`
     has no team `state`**, this warning is shown whenever members disagree,
     **even if** some members lack state. If **`teams.csv` lists a team `state`**,
     that warning is suppressed when some members lack state (partly-unknown roster).
  2. `teams.csv` has a non-empty `state` for the team and it does not match
     the students' states — except when both fall in the same allowed region as
     in (1), or team `state` is **`China`**. Also warns when every listed student lacks state while the team row
     lists one, or when one roster state disagrees with the team row outside those
     exceptions. Team or student state **`State Department`** also pairs with any other state.

Teams layout:
  database/contests/<slug>-teams/year=<year>/teams.csv

Run from repo root:

    python scripts/check_student_state.py                      # all *-teams, all years
    python scripts/check_student_state.py --year 2024          # all *-teams, only year=2024
    python scripts/check_student_state.py bmt --year 2025      # only bmt-teams/year=2025
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

# Rosters where everyone’s state stays inside one of these sets do not trigger
# “different states”; team-row `state` vs a single known roster state also skips
# warnings when both values lie in the same set (e.g. team NJ vs student NY).
COMPATIBLE_STATE_GROUPS: tuple[frozenset[str], ...] = (
    frozenset({"Connecticut", "New York"}),
    frozenset({"Connecticut", "New Jersey"}),
    frozenset({"Maryland", "Virginia"}),
    frozenset({"Arizona", "California"}),
    frozenset({"California", "Nevada"}),
    frozenset({"New Jersey", "Pennsylvania", "New York"}),
)

STATE_DEPARTMENT = "State Department"


def roster_includes_state_department(non_empty: set[str]) -> bool:
    """Diplomatic / overseas schooling; roster may mix with any US state."""
    return STATE_DEPARTMENT in non_empty


def roster_states_within_exception(non_empty: set[str]) -> bool:
    """True if every listed state lies inside one allowed multi-state group."""
    if len(non_empty) <= 1:
        return True
    if roster_includes_state_department(non_empty):
        return True
    return any(non_empty <= grp for grp in COMPATIBLE_STATE_GROUPS)


def team_row_compatible_with_roster_state(team_state: str, roster_state: str) -> bool:
    """True if teams.csv `state` may differ from the single non-empty roster state."""
    if team_state == "China":
        return True
    if team_state == STATE_DEPARTMENT or roster_state == STATE_DEPARTMENT:
        return True
    if team_state == roster_state:
        return True
    pair = frozenset({team_state, roster_state})
    return any(pair <= grp for grp in COMPATIBLE_STATE_GROUPS)


def is_individuals_team(team_name: str) -> bool:
    """HMMT-style pseudo-team for competitors without a school team."""
    t = (team_name or "").strip()
    return t == "Individuals" or t.startswith("Individuals ")


def skip_state_checks_for_team_name(team_name: str) -> bool:
    """Organizations that explicitly pool students across regions."""
    return "Leading Aces Academy" in (team_name or "")


def skip_state_checks_for_bmt_row(teams_root_name: str, row: dict[str, str]) -> bool:
    """BMT lists school separately from team_name; online programs may span states."""
    if teams_root_name != "bmt-teams":
        return False
    return (row.get("school") or "").strip() == "Think Academy Online"


def teams_root_for_slug(slug: str) -> Path:
    s = slug.strip()
    if not s:
        raise ValueError("contest slug must be non-empty")
    if s.endswith("-teams"):
        return CONTESTS_DIR / s
    return CONTESTS_DIR / f"{s}-teams"


def iter_teams_roots() -> list[Path]:
    roots = []
    if not CONTESTS_DIR.is_dir():
        return roots
    for p in sorted(CONTESTS_DIR.iterdir()):
        if p.is_dir() and p.name.endswith("-teams"):
            roots.append(p)
    return roots


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


def sid_sort_key(sid: str) -> tuple[int, int | str]:
    if sid.isdigit():
        return (0, int(sid))
    return (1, sid)


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
        if not raw_ids:
            continue

        sids = [p.strip() for p in raw_ids.split("|") if p.strip()]
        if not sids:
            continue

        team_name = (row.get("team_name") or "").strip()
        if (
            is_individuals_team(team_name)
            or skip_state_checks_for_team_name(team_name)
            or skip_state_checks_for_bmt_row(teams_root_name, row)
        ):
            continue

        per_student: list[tuple[str, str]] = []
        for sid in sids:
            st = student_state.get(sid, "")
            per_student.append((sid, st))

        non_empty = {st for _, st in per_student if st}
        empty_sids = [sid for sid, st in per_student if not st]
        detail = ", ".join(
            f"{sid}={st or '(empty)'}" for sid, st in sorted(per_student, key=lambda t: sid_sort_key(t[0]))
        )

        # Roster: 2+ distinct member states. If team row has a state, allow unknown member
        # states to skip this; if team row has no state, still warn (conflict is visible).
        # Skip when all states fall in an allowed group (CT/NY, CT/NJ, MD/VA, NJ/PA/NY),
        # roster includes State Department (mixable with other states),
        # or team row is China (mixed provinces / registrants OK).
        multi_bad = (
            len(non_empty) > 1
            and (not empty_sids or not team_state)
            and not roster_states_within_exception(non_empty)
            and team_state != "China"
            and team_state != STATE_DEPARTMENT
        )
        if multi_bad:
            ts = f" teams.csv state={team_state!r}" if team_state else ""
            warnings.append(
                f"WARNING [{prefix} team_id={team_id}]: roster members have different states:{ts} {detail}"
            )

        if not team_state:
            continue

        if len(non_empty) == 0:
            warnings.append(
                f"WARNING [{prefix} team_id={team_id}]: teams.csv state={team_state!r} but no student has state in students.csv: {detail}"
            )
            continue

        if len(non_empty) == 1:
            roster_state = next(iter(non_empty))
            if not team_row_compatible_with_roster_state(team_state, roster_state):
                warnings.append(
                    f"WARNING [{prefix} team_id={team_id}]: teams.csv state={team_state!r} "
                    f"but student state is {roster_state!r}: {detail}"
                )
            elif empty_sids:
                warnings.append(
                    f"WARNING [{prefix} team_id={team_id}]: teams.csv state={team_state!r} matches roster, "
                    f"but some students lack state in students.csv ({','.join(empty_sids)}): {detail}"
                )

    return warnings


def collect_warnings(
    teams_root: Path,
    student_state: dict[str, str],
    years_filter: frozenset[str] | None,
) -> list[str]:
    all_w: list[str] = []
    for year_dir in sorted(teams_root.iterdir()):
        if not year_dir.is_dir() or not year_dir.name.startswith("year="):
            continue
        y = year_dir.name.removeprefix("year=")
        if years_filter is not None and y not in years_filter:
            continue
        teams_csv = year_dir / "teams.csv"
        if not teams_csv.is_file():
            continue
        all_w.extend(check_year(teams_root.name, teams_csv, student_state))
    return all_w


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Warn when team members have inconsistent states or when teams.csv state "
            "does not match student states in students.csv."
        )
    )
    parser.add_argument(
        "contest_slug",
        nargs="?",
        help=(
            "Optional. Contest folder name, e.g. bmt (uses database/contests/<slug>-teams/). "
            "If omitted, every database/contests/*-teams/ directory is checked."
        ),
    )
    parser.add_argument(
        "--year",
        "-y",
        action="append",
        dest="years",
        metavar="YEAR",
        help=(
            "Only check folders named year=YEAR (repeat for multiple years). "
            "Default: every year=* under each teams tree."
        ),
    )
    args = parser.parse_args()

    years_filter: frozenset[str] | None = None
    if args.years:
        years_filter = frozenset(str(y).strip() for y in args.years if str(y).strip())

    if args.contest_slug:
        try:
            roots = [teams_root_for_slug(args.contest_slug)]
        except ValueError as e:
            print(e, file=sys.stderr)
            return 2

        if not roots[0].is_dir():
            print(f"ERROR: teams directory not found: {roots[0]}", file=sys.stderr)
            return 2
    else:
        roots = iter_teams_roots()
        if not roots:
            print(f"ERROR: no *-teams directories under {CONTESTS_DIR}", file=sys.stderr)
            return 2

    student_state = load_student_states()
    if not student_state and STUDENTS_CSV.is_file():
        print(f"WARNING: no rows loaded from {STUDENTS_CSV}", file=sys.stderr)

    all_warnings: list[str] = []
    for tr in roots:
        all_warnings.extend(collect_warnings(tr, student_state, years_filter))

    year_suffix = (
        f" [only year={','.join(sorted(years_filter))}]" if years_filter else ""
    )

    if not all_warnings:
        if args.contest_slug:
            print(
                f"OK: no state issues under {roots[0].relative_to(REPO_ROOT)}{year_suffix}"
            )
        else:
            print(
                f"OK: no state issues in {len(roots)} *-teams trees under database/contests{year_suffix}"
            )
        return 0

    for line in all_warnings:
        print(line, file=sys.stderr)
    print(f"Total warnings: {len(all_warnings)}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
