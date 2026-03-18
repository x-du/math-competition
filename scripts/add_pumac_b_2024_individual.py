#!/usr/bin/env python3
"""
One-off: Add PUMaC 2024 Individual Rankings B from pasted table.
Resolves (name, state) via students.csv; adds new students as needed.
"""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "pumac-b" / "year=2024"


# Pasted table: rank, name, team, total, finals, test1, test2
ROWS: list[tuple[int, str, str, float, int, str, str]] = [
    (1, "Qiao Zhang", "Sierra Canyon School", 3.889, 21, "20.112 (ALG)", "17.527 (CMB)"),
    (2, "Elbert Ho", "Pingry Blue", 3.699, 21, "12.043 (ALG)", "15.581 (CMB)"),
    (3, "Harry Gao", "Ward Melville Math Team", 3.476, 19, "16.297 (NTY)", "7.450 (GEO)"),
    (4, "Katherine Li", "Theta Math Club", 3.444, 21, "8.837 (GEO)", "10.761 (NTY)"),
    (5, "Participant 123 - 1 (Liran Zhou)", "Jericho A", 3.435, 17, "8.816 (GEO)", "15.450 (NTY)"),
    (6, "Jiawen Huang", "Arcadia High School", 3.241, 17, "4.921 (NTY)", "14.554 (GEO)"),
    (7, "Benjamin Song", "Theta Math Club", 3.150, 17, "5.978 (GEO)", "11.336 (NTY)"),
    (8, "Advait Joshi", "Big L", 3.148, 14, "3.770 (ALG)", "15.191 (NTY)"),
    (9, "Derrick Chen", "Theta Math Club", 3.100, 14, "7.255 (ALG)", "10.486 (CMB)"),
    (10, "Jason Lu", "MHSProfessionalJobbers", 3.001, 10, "7.054 (ALG)", "13.533 (NTY)"),
    (11, "Hongjian Gary Zheng", "PRISMS Young Falcons", 2.877, 14, "10.539 (ALG)", "3.626 (NTY)"),
    (12, "Alex Zhao", "CRH Math Team", 2.865, 9, "6.906 (GEO)", "15.581 (CMB)"),
    (13, "Shirley Xiong", "Ward Melville Math Team", 2.826, 10, "7.782 (NTY)", "9.786 (GEO)"),
    (14, "Benjamin Sun", "Big L", 2.809, 10, "10.539 (ALG)", "6.921 (CMB)"),
    (15, "Jason Lian", "Individuals Team 161", 2.805, 8, "3.770 (ALG)", "14.960 (GEO)"),
    (16, "Eden He", "Not Great Valley", 2.692, 6, "10.539 (ALG)", "10.309 (GEO)"),
    (17, "Kevin Chen", "Individuals Team 162", 2.604, 10, "11.638 (ALG)", "2.717 (NTY)"),
    (18, "Jacob Chung", "Individuals Team 162", 2.595, 9, "4.921 (NTY)", "10.456 (CMB)"),
    (19, "Eric Zhong", "Ward Melville Math Team", 2.515, 6, "7.255 (ALG)", "9.213 (CMB)"),
    (20, "Charles Wang", "Millburn Mathematical Madpeople", 2.506, 8, "7.255 (ALG)", "5.512 (CMB)"),
    (21, "Thomas McCurley", "Sierra Canyon School", 2.461, 7, "6.102 (NTY)", "9.213 (CMB)"),
    (22, "YEOJUN JAY JUNG", "Individuals Team 162", 2.425, 3, "8.354 (ALG)", "13.082 (GEO)"),
    (23, "William Liu", "PHS Apricot", 2.408, 6, "7.782 (NTY)", "7.450 (GEO)"),
    (24, "Suhas Kondapalli", "Pirates B", 2.381, 9, "2.717 (NTY)", "8.825 (CMB)"),
    (25, "Terry Huang", "PRISMS Baby Falcons", 2.203, 7, "10.309 (GEO)", "1.295 (NTY)"),
    (26, "Krivi Partani", "Knights B", 2.143, 3, "7.255 (ALG)", "7.450 (GEO)"),
    (27, "Minhe Liu", "MHSProfessionalJobbers", 2.010, 3, "2.519 (ALG)", "9.135 (GEO)"),
    (28, "Guanjie Zhao", "Jericho B", 1.799, 3, "8.475 (NTY)", "2.574 (GEO)"),
    (29, "Andrew Zhou", "Big L", 1.774, 1, "6.360 (NTY)", "10.088 (CMB)"),
    (30, "Alexander Mitev", "MathSchool 2", 1.437, 0, "3.770 (ALG)", "8.816 (GEO)"),
    (31, "Peyton Li", "CRH Math Team", 1.422, 0, "15.581 (CMB)", "2.717 (NTY)"),
    (32, "Sophie Chen", "Hotchkiss", 1.302, 0, "4.994 (CMB)", "7.782 (NTY)"),
]


def load_students():
    key_to_row = {}
    next_id = 1
    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
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
    return key_to_row, next_id


def main():
    key_to_row, next_id = load_students()
    new_students = []
    out_rows = []

    for rank, name, team, total, finals, test1, test2 in ROWS:
        # State is unknown from this table; resolve primarily by name.
        state = ""
        key = (name.strip().lower(), state)
        row = key_to_row.get(key)
        if not row:
            # Fallback: same name, any state (as used in other one-off scripts).
            for (k, v) in key_to_row.items():
                if k[0] == name.strip().lower():
                    row = v
                    break
        if row:
            out_rows.append((row["student_id"], row["student_name"], 2024, "B", rank, total, finals, test1, test2))
            continue

        sid = next_id
        next_id += 1
        canon_name = name.strip()
        key_to_row[key] = {"student_id": sid, "student_name": canon_name, "state": state}
        new_students.append(
            {"student_id": sid, "student_name": canon_name, "state": state, "team_ids": "", "alias": ""}
        )
        out_rows.append((sid, canon_name, 2024, "B", rank, total, finals, test1, test2))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "results_B.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "student_id",
                "student_name",
                "year",
                "division",
                "rank",
                "total_score",
                "finals_score",
                "test1",
                "test2",
            ]
        )
        for r in out_rows:
            w.writerow(r)
    print(f"Wrote {out_path} ({len(out_rows)} rows)")

    if new_students:
        with open(STUDENTS_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            for r in new_students:
                w.writerow(
                    [r["student_id"], r["student_name"], r["state"], r.get("team_ids", ""), r.get("alias", "")]
                )
        print(f"Appended {len(new_students)} new students: {[s['student_name'] for s in new_students]}")
    else:
        print("No new students to add.")

    print("Run: python scripts/build_search_data.py")


if __name__ == "__main__":
    main()

