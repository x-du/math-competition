#!/usr/bin/env python3
"""
One-off: Add team_id to PUMaC 2024 Geometry B results.

- Ensures every Geometry B team exists in database/students/teams.csv.
- Adds the corresponding team_id to each student's team_ids in database/students/students.csv.
- Adds a team_id column to database/contests/pumac-b-geometry/year=2024/results_B.csv.
"""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
TEAMS_CSV = ROOT / "database" / "students" / "teams.csv"
RESULTS_CSV = ROOT / "database" / "contests" / "pumac-b-geometry" / "year=2024" / "results_B.csv"


# Name -> team name for PUMaC 2024 Geometry B, from the official table.
NAME_TEAM_ROWS: list[tuple[str, str]] = [
    ("Jason Lian", "Individuals Team 161"),
    ("Jiawen Huang", "Arcadia High School"),
    ("YEOJUN JAY JUNG", "Individuals Team 162"),
    ("Eden He", "Not Great Valley"),
    ("Terry Huang", "PRISMS Baby Falcons"),
    ("Shirley Xiong", "Ward Melville Math Team"),
    ("Minhe Liu", "MHSProfessionalJobbers"),
    ("Katherine Li", "Theta Math Club"),
    ("Alexander Mitev", "MathSchool 2"),
    ("Participant 123 - 1 (Liran Zhou)", "Jericho A"),
    ("James Browning", "Sierra Canyon School"),
    ("Joel Pulikkan", "MHSProfessionalJobbers"),
    ("Franklin Lee", "Theta Math Club"),
    ("Krivi Partani", "Knights B"),
    ("Karson Jiang", "Millburn Mathematical Madpeople"),
    ("Alethea Liu", "Millburn Mathematical Madpeople"),
    ("Daniel Wu", "Not Great Valley"),
    ("Harry Gao", "Ward Melville Math Team"),
    ("Dian Yang", "Jericho B"),
    ("William Liu", "PHS Apricot"),
    ("Zihan Yu", "PHS Apricot"),
    ("Ryan Zhang", "Theta Math Club"),
    ("Shannon Xu", "Knights B"),
    ("Michael Wang", "Sierra Canyon School"),
    ("Alex Zhao", "CRH Math Team"),
    ("Kevin Zhao", "MHSProfessionalJobbers"),
    ("Benjamin Song", "Theta Math Club"),
    ("Derek Peng", "Pingry Blue"),
    ("Eric Dai", "Individuals Team 161"),
    ("Terence Wu", "Individuals Team 162"),
    ("Kaiqi Xu", "Individuals Team 160"),
    ("Xinqi Jessie Wang", "PRISMS Young Falcons"),
    ("Vincent Yang", "Jericho A"),
    ("Zachary Ji", "PHS Blueberry"),
    ("Atticus Masuzawa", "Sierra Canyon School"),
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
    """Load Geometry B results, returning list of rows."""
    with open(RESULTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


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
    name_to_team = {name: team for name, team in NAME_TEAM_ROWS}

    # 1) Load results and determine which teams we need.
    result_rows = load_results()
    needed_teams = set()
    for row in result_rows:
        name = (row.get("student_name") or "").strip()
        team_name = name_to_team.get(name)
        if team_name:
            needed_teams.add(team_name)

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
        name = (row.get("student_name") or "").strip()
        if not sid_s or not name:
            continue
        try:
            sid = int(sid_s)
        except ValueError:
            continue
        team_name = name_to_team.get(name)
        if not team_name:
            continue
        tid = name_to_id.get(team_name)
        if tid is None:
            continue
        sid_to_team_id[sid] = tid

    # 4) Update students.csv: add team_ids reference by student_id.
    student_rows, student_fields = load_students()
    student_id_idx = {
        int((r.get("student_id") or "0").strip() or 0): i
        for i, r in enumerate(student_rows)
        if (r.get("student_id") or "").strip().isdigit()
    }

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

    # 5) Rewrite Geometry B results with team_id column.
    new_fieldnames = [
        "student_id",
        "team_id",
        "student_name",
        "year",
        "division",
        "rank",
        "score",
        "p1",
        "p2",
        "p3",
        "p4",
        "p5",
        "p6",
        "p7",
        "p8",
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
                "team_id": str(tid) if tid is not None else "",
                "student_name": row.get("student_name", ""),
                "year": row.get("year", ""),
                "division": row.get("division", ""),
                "rank": row.get("rank", ""),
                "score": row.get("score", ""),
                "p1": row.get("p1", ""),
                "p2": row.get("p2", ""),
                "p3": row.get("p3", ""),
                "p4": row.get("p4", ""),
                "p5": row.get("p5", ""),
                "p6": row.get("p6", ""),
                "p7": row.get("p7", ""),
                "p8": row.get("p8", ""),
            }
            writer.writerow(out)

    print("Updated teams.csv, students.csv, and Geometry B 2024 results_B.csv for PUMaC.")


if __name__ == "__main__":
    main()

