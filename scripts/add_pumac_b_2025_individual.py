#!/usr/bin/env python3
"""
One-off: Add PUMaC 2025 Individual Rankings B from pasted table.
Resolves (name, state) via students.csv; adds new students as needed.
"""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "pumac-b" / "year=2025"

# Pasted table: rank, name, team, total, finals, test1, test2
ROWS: list[tuple[int, str, str, float, int, str, str]] = [
    (1, "Eric Dai", "Millburn Mathematical Madpeople", 3.672, 21, "14.294 (CMB)", "16.174 (NTY)"),
    (2, "Liran Zhou", "Jericho A", 3.641, 15, "15.983 (GEO)", "16.174 (NTY)"),
    (3, "Eden He", "Not Great Valley", 3.619, 15, "12.464 (ALG)", "11.833 (GEO)"),
    (4, "Brandon Ni", "Greater Boston", 3.451, 14, "19.179 (CMB)", "9.108 (NTY)"),
    (5, "Andrew Chai", "Ridge Mu Alpha Theta", 3.266, 18, "4.852 (CMB)", "16.174 (NTY)"),
    (6, "Advait Joshi", "Big L Club", 3.245, 19, "5.801 (ALG)", "16.239 (NTY)"),
    (7, "Harry Gao", "Ward Melville Math Team", 3.200, 17, "10.508 (CMB)", "5.832 (NTY)"),
    (8, "Max Li", "Gunn Math", 3.165, 10, "9.702 (ALG)", "11.577 (NTY)"),
    (9, "Derrick Chen", "Individuals Team 189", 3.117, 8, "10.475 (ALG)", "10.084 (CMB)"),
    (10, "Kevin Chen", "Ridge Mu Alpha Theta", 3.106, 6, "12.059 (ALG)", "8.531 (GEO)"),
    (11, "Angelica Feng", "PRISMS Young Falcons", 3.062, 11, "9.702 (ALG)", "6.730 (NTY)"),
    (12, "Alexander Sheng", "PHS Avocado", 3.030, 10, "12.107 (ALG)", "3.268 (GEO)"),
    (13, "Alex Bae", "Gunn Math", 3.011, 12, "9.702 (ALG)", "4.852 (CMB)"),
    (14, "Eric Huang", "Greater Boston", 2.987, 9, "7.469 (CMB)", "10.948 (NTY)"),
    (15, "Hayden Hughes", "Individuals Team 190", 2.949, 11, "10.508 (CMB)", "4.230 (NTY)"),
    (16, "Yeojun Jung", "Individuals Team 190", 2.929, 10, "6.656 (ALG)", "8.531 (GEO)"),
    (17, "Xinqi Jessie Wang", "PRISMS Young Falcons", 2.910, 6, "8.194 (GEO)", "10.051 (CMB)"),
    (18, "Arjun Pandey", "MH Math Knightmares", 2.876, 3, "8.639 (CMB)", "24.740 (NTY)"),
    (19, "Jay Wang", "PHS Avocado", 2.873, 8, "6.823 (ALG)", "9.042 (GEO)"),
    (20, "Brayden Choi", "OSS ORCAS", 2.841, 8, "8.847 (ALG)", "5.832 (NTY)"),
    (21, "Gabriele Herr", "BCA 2", 2.838, 7, "10.508 (CMB)", "5.832 (NTY)"),
    (22, "Alexander Wang", "BCA 2", 2.768, 7, "10.019 (GEO)", "3.455 (NTY)"),
    (23, "Hridaan Mehta", "CRH", 2.745, 7, "8.458 (ALG)", "4.892 (GEO)"),
    (24, "Monish Saravana Kumar", "Pirates B", 2.724, 9, "3.039 (ALG)", "14.260 (CMB)"),
    (25, "Kevin Feng", "EightTimesEpsilon", 2.713, 4, "12.344 (GEO)", "5.165 (CMB)"),
    (26, "Hanru Zhang", "Jericho A", 2.699, 11, "3.039 (ALG)", "9.042 (GEO)"),
    (27, "Shlok Mukund", "Greater Boston", 2.681, 17, "1.411 (ALG)", "9.346 (NTY)"),
    (28, "Maiya Qiu", "PHS Avocado", 2.670, 8, "2.270 (CMB)", "11.577 (NTY)"),
    (29, "Ryan Gong", "Individuals Team 191", 2.661, 5, "8.531 (GEO)", "5.056 (NTY)"),
    (30, "Atticus Masuzawa", "Sierra Canyon School", 2.620, 5, "10.891 (GEO)", "3.039 (CMB)"),
    (31, "Suvid Bordia", "Pingry", 2.316, 2, "6.085 (ALG)", "10.948 (NTY)"),
    (32, "Zili Chang", "Millburn Mathematical Madpeople 2", 2.270, 5, "9.702 (ALG)", "0.000 (NTY)"),
    (33, "Eric Zhong", "Ward Melville Math Team", 2.125, 2, "3.039 (ALG)", "11.678 (CMB)"),
    (34, "Evan Goldman", "Small L Club", 1.720, 1, "0.000 (ALG)", "12.352 (CMB)"),
    (35, "Fiona Chen", "Big L Club", 1.364, 0, "1.411 (ALG)", "9.042 (GEO)"),
    (36, "Joshua Shi", "THE Labubu", 1.344, 0, "1.411 (ALG)", "8.531 (GEO)"),
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
            out_rows.append((row["student_id"], row["student_name"], 2025, "B", rank, total, finals, test1, test2))
            continue

        sid = next_id
        next_id += 1
        canon_name = name.strip()
        key_to_row[key] = {"student_id": sid, "student_name": canon_name, "state": state}
        new_students.append(
            {"student_id": sid, "student_name": canon_name, "state": state, "team_ids": "", "alias": ""}
        )
        out_rows.append((sid, canon_name, 2025, "B", rank, total, finals, test1, test2))

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
                w.writerow([r["student_id"], r["student_name"], r["state"], r.get("team_ids", ""), r.get("alias", "")])
        print(f"Appended {len(new_students)} new students: {[s['student_name'] for s in new_students]}")
    else:
        print("No new students to add.")

    print("Run: python scripts/build_search_data.py")


if __name__ == "__main__":
    main()

