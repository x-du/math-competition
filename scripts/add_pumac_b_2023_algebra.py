#!/usr/bin/env python3
"""
Add PUMaC 2023 Algebra B results. Resolves students by name (state from team/context when possible),
resolves teams by name; adds new students and teams as needed.
Schema matches year=2024: student_id, team_id, student_name, year, division, rank, score, p1..p8.
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
TEAMS_CSV = ROOT / "database" / "students" / "teams.csv"
OUT_DIR = ROOT / "database" / "contests" / "pumac-b-algebra" / "year=2023"

# (rank, name, team_name, score, p1..p8)
ROWS = [
    (1, "Michael Lu", "Ward Melville Math Team", 16.153, 1, 1, 1, 1, 1, 1, 0, 0),
    (1, "Jason Lu", "MHSProfessionalJobbers", 16.153, 1, 1, 1, 1, 1, 1, 0, 0),
    (3, "Elbert Ho", "Pingry Blue", 12.578, 1, 1, 1, 1, 1, 0, 0, 0),
    (3, "Jason Lian", "CCC", 12.578, 1, 1, 1, 1, 1, 0, 0, 0),
    (3, "James Li", "Cougz", 12.578, 1, 1, 1, 1, 1, 0, 0, 0),
    (6, "Sounak Bagchi", "MCA Underdogs", 12.445, 1, 1, 1, 0, 1, 1, 0, 0),
    (7, "Evan Xie", "Pingry Blue", 8.870, 1, 1, 1, 1, 0, 0, 0, 0),
    (8, "Wenqing Eric Mao", "PRISMS Young Falcons", 8.737, 1, 1, 1, 0, 0, 1, 0, 0),
    (8, "Andy Chin", "CRH Math Team", 8.737, 1, 1, 1, 0, 0, 1, 0, 0),
    (10, "Maddie Zhu", "Pingry Blue", 6.694, 1, 0, 1, 0, 0, 1, 0, 0),
    (10, "Michael Retakh", "Ward Melville Math Team", 6.694, 1, 0, 1, 0, 0, 1, 0, 0),
    (12, "Charles Wang", "Millburn Mathematical Madpeople", 5.751, 0, 1, 0, 1, 0, 0, 0, 0),
    (13, "Jennifer Ni", "Ridge Mu Alpha Theta", 5.618, 0, 1, 0, 0, 0, 1, 0, 0),
    (14, "Shreyan Lingampalli", "Cougz", 5.162, 1, 1, 1, 0, 0, 0, 0, 0),
    (14, "Albert Wu", "Pingry Blue", 5.162, 1, 1, 1, 0, 0, 0, 0, 0),
    (14, "Isabella Hu", "CCC", 5.162, 1, 1, 1, 0, 0, 0, 0, 0),
    (14, "Derek Peng", "Pingry Blue", 5.162, 1, 1, 1, 0, 0, 0, 0, 0),
    (14, "Howard Ziyuan Tang", "Individuals Team 162", 5.162, 1, 1, 1, 0, 0, 0, 0, 0),
    (14, "Sujay Konda", "Knights B", 5.162, 1, 1, 1, 0, 0, 0, 0, 0),
    (14, "Ishan Guthikonda", "Knights B", 5.162, 1, 1, 1, 0, 0, 0, 0, 0),
    (14, "Dylan Ochoa", "Sierra Canyon School", 5.162, 1, 1, 1, 0, 0, 0, 0, 0),
    (14, "Luca Huang", "Charter", 5.162, 1, 1, 1, 0, 0, 0, 0, 0),
    (14, "Eric Zhong", "Ward Melville Math Team", 5.162, 1, 1, 1, 0, 0, 0, 0, 0),
    (14, "Vishrut Goyal", "Jericho Mathletes", 5.162, 1, 1, 1, 0, 0, 0, 0, 0),
    (14, "Srilekha Mamidala", "GVHS Math Club", 5.162, 1, 1, 1, 0, 0, 0, 0, 0),
    (14, "Maiya Qiu", "PHS Math Team", 5.162, 1, 1, 1, 0, 0, 0, 0, 0),
    (14, "Amy Lin", "PHS Math Team", 5.162, 1, 1, 1, 0, 0, 0, 0, 0),
    (28, "Alethea Liu", "Millburn Mathematical Madpeople", 5.045, 0, 0, 1, 0, 1, 0, 0, 0),
    (29, "Hongjian Gary Zheng", "PRISMS Young Falcons", 3.826, 1, 1, 0, 0, 0, 0, 0, 0),
    (30, "Eric Cheng", "Pingry Blue", 3.380, 0, 1, 1, 0, 0, 0, 0, 0),
    (30, "Fiona Chen", "Fat L Club", 3.380, 0, 1, 1, 0, 0, 0, 0, 0),
    (30, "Shining Sun", "BCA 2", 3.380, 0, 1, 1, 0, 0, 0, 0, 0),
    (30, "Frank Yuan", "Sierra Canyon School", 3.380, 0, 1, 1, 0, 0, 0, 0, 0),
    (30, "Michael Pylypovych", "BCA 2", 3.380, 0, 1, 1, 0, 0, 0, 0, 0),
    (30, "Lindsay Miao", "Hotchkiss", 3.380, 0, 1, 1, 0, 0, 0, 0, 0),
    (30, "Srijith Chinthalapudi", "MCA Underdogs", 3.380, 0, 1, 1, 0, 0, 0, 0, 0),
]


def load_students():
    key_to_row = {}
    next_id = 1
    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            sid_s = (row.get("student_id") or "").strip()
            if not sid_s:
                continue
            try:
                sid = int(sid_s)
            except ValueError:
                continue
            next_id = max(next_id, sid + 1)
            name = (row.get("student_name") or "").strip()
            state = (row.get("state") or "").strip()
            r = {"student_id": sid, "student_name": name, "state": state}
            if name:
                key = (name.lower(), state)
                if key not in key_to_row:
                    key_to_row[key] = r
            for a in (row.get("alias") or "").split("|"):
                a = a.strip()
                if a:
                    key = (a.lower(), state)
                    if key not in key_to_row:
                        key_to_row[key] = r
    return key_to_row, next_id, fieldnames


def load_teams():
    name_to_id = {}
    next_id = 1
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
            if name and name not in name_to_id:
                name_to_id[name] = tid
    return name_to_id, next_id


def main():
    key_to_row, next_student_id, student_fieldnames = load_students()
    name_to_team_id, next_team_id = load_teams()

    # Maddie Zhu -> Madeline Zhu
    for k, v in list(key_to_row.items()):
        if k[0] == "madeline zhu":
            key_to_row[("maddie zhu", k[1])] = v
            break

    new_students = []
    new_teams = []
    out_rows = []

    for rank, name, team_name, score, p1, p2, p3, p4, p5, p6, p7, p8 in ROWS:
        name = name.strip()
        team_name = team_name.strip()

        # Resolve team_id
        team_id = name_to_team_id.get(team_name)
        if team_id is None:
            team_id = next_team_id
            next_team_id += 1
            name_to_team_id[team_name] = team_id
            new_teams.append({"team_id": team_id, "team_name": team_name})

        # Resolve student
        state = ""
        key = (name.lower(), state)
        row = key_to_row.get(key)
        if not row:
            for k, v in key_to_row.items():
                if k[0] == name.lower():
                    row = v
                    break
        if row:
            out_rows.append(
                (
                    row["student_id"],
                    team_id,
                    row["student_name"],
                    2023,
                    "B",
                    rank,
                    score,
                    p1,
                    p2,
                    p3,
                    p4,
                    p5,
                    p6,
                    p7,
                    p8,
                )
            )
            continue

        sid = next_student_id
        next_student_id += 1
        key_to_row[(name.lower(), state)] = {"student_id": sid, "student_name": name, "state": state}
        new_students.append(
            {
                "student_id": sid,
                "student_name": name,
                "state": state,
                "team_ids": "",
                "alias": "",
            }
        )
        out_rows.append(
            (sid, team_id, name, 2023, "B", rank, score, p1, p2, p3, p4, p5, p6, p7, p8)
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "results_B.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
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
        )
        for r in out_rows:
            w.writerow(r)
    print(f"Wrote {out_path} ({len(out_rows)} rows)")

    if new_students:
        # students.csv has: student_id, student_name, state, team_ids, alias, gender, grade_in_2026
        with open(STUDENTS_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            for r in new_students:
                row = [
                    r["student_id"],
                    r["student_name"],
                    r["state"],
                    r.get("team_ids", ""),
                    r.get("alias", ""),
                    "",
                    "",
                ]
                w.writerow(row)
        print(f"Appended {len(new_students)} new students: {[s['student_name'] for s in new_students]}")
    else:
        print("No new students to add.")

    if new_teams:
        with open(TEAMS_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            for t in new_teams:
                w.writerow([t["team_id"], t["team_name"], ""])
        print(f"Appended {len(new_teams)} new teams: {[t['team_name'] for t in new_teams]}")
    else:
        print("No new teams to add.")

    print("Run: python scripts/build_search_data.py")


if __name__ == "__main__":
    main()
