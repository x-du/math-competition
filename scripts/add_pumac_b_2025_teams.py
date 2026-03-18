#!/usr/bin/env python3
"""
One-off: Add teams for PUMaC 2025 Division B.

- Ensures every PUMaC-B 2025 team exists in database/students/teams.csv.
- Adds the corresponding team_id to each student's team_ids in database/students/students.csv.
- Adds a team_id column to database/contests/pumac-b/year=2025/results_B.csv.
"""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
TEAMS_CSV = ROOT / "database" / "students" / "teams.csv"
RESULTS_CSV = ROOT / "database" / "contests" / "pumac-b" / "year=2025" / "results_B.csv"


# Rank -> team name for PUMaC 2025 Division B, from the official table.
RANK_TEAM_ROWS: list[tuple[int, str]] = [
    (1, "Millburn Mathematical Madpeople"),
    (2, "Jericho A"),
    (3, "Not Great Valley"),
    (4, "Greater Boston"),
    (5, "Ridge Mu Alpha Theta"),
    (6, "Big L Club"),
    (7, "Ward Melville Math Team"),
    (8, "Gunn Math"),
    (9, "Individuals Team 189"),
    (10, "Ridge Mu Alpha Theta"),
    (11, "PRISMS Young Falcons"),
    (12, "PHS Avocado"),
    (13, "Gunn Math"),
    (14, "Greater Boston"),
    (15, "Individuals Team 190"),
    (16, "Individuals Team 190"),
    (17, "PRISMS Young Falcons"),
    (18, "MH Math Knightmares"),
    (19, "PHS Avocado"),
    (20, "OSS ORCAS"),
    (21, "BCA 2"),
    (22, "BCA 2"),
    (23, "CRH"),
    (24, "Pirates B"),
    (25, "EightTimesEpsilon"),
    (26, "Jericho A"),
    (27, "Greater Boston"),
    (28, "PHS Avocado"),
    (29, "Individuals Team 191"),
    (30, "Sierra Canyon School"),
    (31, "Pingry"),
    (32, "Millburn Mathematical Madpeople 2"),
    (33, "Ward Melville Math Team"),
    (34, "Small L Club"),
    (35, "Big L Club"),
    (36, "THE Labubu"),
]


def load_teams():
    """Load teams.csv -> (rows, name->id, next_id)."""
    rows = []
    name_to_id: dict[str, int] = {}
    next_id = 1
    if TEAMS_CSV.exists():
        with open(TEAMS_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tid_s = (row.get("team_id") or "").strip()
                if not tid_s:
                    continue
                try:
                    tid = int(tid_s)
                except ValueError:
                    continue
                next_id = max(next_id, tid + 1)
                name = (row.get("team_name") or "").strip()
                rows.append(
                    {
                        "team_id": str(tid),
                        "team_name": name,
                        "associated_team_ids": (row.get("associated_team_ids") or "").strip(),
                    }
                )
                if name:
                    name_to_id[name] = tid
    return rows, name_to_id, next_id


def save_teams(rows):
    rows_sorted = sorted(rows, key=lambda r: int(r["team_id"]))
    with open(TEAMS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["team_id", "team_name", "associated_team_ids"])
        writer.writeheader()
        for r in rows_sorted:
            writer.writerow(r)


def load_results():
    """Load PUMaC-B 2025 results, returning (rows, sid->rank)."""
    with open(RESULTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    sid_to_rank: dict[int, int] = {}
    for r in rows:
        sid_s = (r.get("student_id") or "").strip()
        rank_s = (r.get("rank") or "").strip()
        if not sid_s or not rank_s:
            continue
        try:
            sid = int(sid_s)
            rank = int(rank_s)
        except ValueError:
            continue
        sid_to_rank[sid] = rank
    return rows, sid_to_rank


def load_students():
    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or [
            "student_id",
            "student_name",
            "state",
            "team_ids",
            "alias",
            "gender",
            "grade_in_2026",
        ]
    return rows, fieldnames


def main():
    rank_to_team = {rank: team for rank, team in RANK_TEAM_ROWS}

    # 1) Load results and determine which students/teams we need.
    result_rows, sid_to_rank = load_results()
    needed_teams = {rank_to_team[rank] for rank in sid_to_rank.values() if rank in rank_to_team}

    # 2) Ensure all teams exist in teams.csv.
    team_rows, name_to_id, next_tid = load_teams()
    for team_name in sorted(needed_teams):
        if team_name not in name_to_id:
            tid = next_tid
            next_tid += 1
            name_to_id[team_name] = tid
            team_rows.append(
                {"team_id": str(tid), "team_name": team_name, "associated_team_ids": ""}
            )
    save_teams(team_rows)

    # 3) Map each student in this contest to a team_id.
    sid_to_team_id: dict[int, int] = {}
    for row in result_rows:
        sid_s = (row.get("student_id") or "").strip()
        rank_s = (row.get("rank") or "").strip()
        if not sid_s or not rank_s:
            continue
        try:
            sid = int(sid_s)
            rank = int(rank_s)
        except ValueError:
            continue
        team_name = rank_to_team.get(rank)
        if not team_name:
            continue
        tid = name_to_id.get(team_name)
        if tid is None:
            continue
        sid_to_team_id[sid] = tid

    # 4) Update students.csv: add team_ids reference.
    student_rows, student_fields = load_students()
    student_id_idx = {int((r.get("student_id") or "0").strip() or 0): i for i, r in enumerate(student_rows) if (r.get("student_id") or "").strip().isdigit()}

    for sid, tid in sid_to_team_id.items():
        idx = student_id_idx.get(sid)
        if idx is None:
            continue
        row = student_rows[idx]
        team_ids_str = (row.get("team_ids") or "").strip()
        if not team_ids_str:
            new_ids = [str(tid)]
        else:
            parts = [p for p in team_ids_str.split("|") if p]
            if str(tid) not in parts:
                parts.append(str(tid))
            new_ids = parts
        row["team_ids"] = "|".join(new_ids)

    with open(STUDENTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=student_fields)
        writer.writeheader()
        for r in student_rows:
            writer.writerow(r)

    # 5) Rewrite results_B.csv with team_id column.
    # Put team_id as the second column.
    new_fieldnames = [
        "student_id",
        "team_id",
        "student_name",
        "year",
        "division",
        "rank",
        "total_score",
        "finals_score",
        "test1",
        "test2",
    ]

    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        for row in result_rows:
            sid_s = (row.get("student_id") or "").strip()
            sid = int(sid_s) if sid_s.isdigit() else None
            tid = sid_to_team_id.get(sid) if sid is not None else None
            out = {
                "student_id": row.get("student_id", ""),
                "student_name": row.get("student_name", ""),
                "year": row.get("year", ""),
                "division": row.get("division", ""),
                "rank": row.get("rank", ""),
                "total_score": row.get("total_score", ""),
                "finals_score": row.get("finals_score", ""),
                "team_id": str(tid) if tid is not None else "",
                "test1": row.get("test1", ""),
                "test2": row.get("test2", ""),
            }
            writer.writerow(out)

    print("Updated teams.csv, students.csv, and results_B.csv for PUMaC 2025 Division B.")


if __name__ == "__main__":
    main()

