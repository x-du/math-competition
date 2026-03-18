#!/usr/bin/env python3
"""
One-off: Add PUMAC 2023 Individual Rankings A from pasted table.
Resolves (name, state) via students.csv; adds new students as needed.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "pumac" / "year=2023"

TEAM_TO_STATE = {
    "Lehigh Valley Fire": "Pennsylvania", "TJ A": "Virginia", "BCA 1": "New Jersey",
    "Texas Ramanujan": "Texas", "Florida Alligators": "Florida", "PEA Red Lion": "New Hampshire",
    "CT Cyborgs": "Connecticut", "Knights A": "California", "MoCoSwaggaSquad": "Maryland",
    "Athemath Owls": "California", "Florida Beaches": "Florida", "Phillips Academy": "Massachusetts",
    "Lexington Alpha": "Massachusetts", "Lexington Beta": "Massachusetts",
    "GWe UAre Not NAffiliated": "Georgia", "PRISMS Falcons": "California", "TJ B": "Virginia",
    "404 Error": "Virginia", "BBMC-math Delta": "Maryland", "Tin Man": "California",
}

# Pasted table: rank, name, team, total, finals
ROWS = [
    (1, "Alex Wang", "Lehigh Valley Fire", 3.883, 20),
    (2, "Calvin Wang", "TJ A", 3.562, 12),
    (3, "Marvin Mao", "BCA 1", 3.503, 12),
    (4, "Channing Yang", "Texas Ramanujan", 3.454, 14),
    (5, "Aaron Hu", "Florida Alligators", 3.352, 10),
    (6, "Oron Wang", "PEA Red Lion", 3.310, 8),
    (7, "Vikram Sarkar", "CT Cyborgs", 3.263, 14),
    (8, "Aprameya Tripathy", "Knights A", 3.240, 18),
    (9, "Kelin Zhu", "MoCoSwaggaSquad", 3.191, 14),
    (10, "Vivian Loh", "Athemath Owls", 3.178, 11),
    (11, "Allen Wang", "Lehigh Valley Fire", 3.105, 9),
    (12, "Andrew Lin", "Lehigh Valley Fire", 3.063, 12),
    (13, "Steve Zhang", "GWe UAre Not NAffiliated", 2.915, 10),
    (14, "Andrew Li", "Tin Man", 2.891, 4),
    (15, "Sargam Mondal", "Lehigh Valley Fire", 2.849, 1),
    (16, "Alexander Jun", "Texas Ramanujan", 2.840, 7),
    (17, "Jiahe Liu", "404 Error", 2.830, 7),
    (18, "Benny Wang", "PEA Red Lion", 2.817, 11),
    (19, "Andrew Zhao", "Lexington Alpha", 2.787, 8),
    (20, "Roger Fan", "GWe UAre Not NAffiliated", 2.772, 9),
    (21, "Kailin Kevin Yang", "PRISMS Falcons", 2.771, 6),
    (22, "Darsh Patel", "Florida Beaches", 2.732, 11),
    (23, "Yifan Kang", "Phillips Academy", 2.712, 14),
    (24, "David Wei", "TJ A", 2.623, 2),
    (25, "Jordan Lefkowitz", "CT Cyborgs", 2.618, 7),
    (26, "Sitta Tantikul", "Individuals Team 161", 2.590, 3),
    (27, "Zani Xu", "TJ A", 2.544, 4),
    (28, "Yutong Mark Zhao", "PRISMS Falcons", 2.521, 4),
    (29, "Sam Wang", "Lexington Beta", 2.500, 7),
    (30, "Daniel He", "MoCoSwaggaSquad", 2.489, 10),
    (31, "Isaac Chen", "Lehigh Valley Fire", 2.389, 3),
    (32, "Bole Ying", "Lehigh Valley Fire", 2.294, 5),
    (33, "Vishal Nandakumar", "TJ B", 2.101, 1),
    (34, "Andrew Xing", "Florida Alligators", 2.071, 1),
    (35, "Adam Ge", "Lexington Alpha", 2.050, 1),
    (36, "Harry Kim", "Phillips Academy", 1.968, 1),
    (37, "Albert Cao", "BBMC-math Delta", 1.888, 1),
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
    # Alex Wang (Lehigh Valley Fire / PA) = Alexander Wang (id 1)
    if ("alexander wang", "new jersey") in key_to_row:
        key_to_row[("alex wang", "pennsylvania")] = key_to_row[("alexander wang", "new jersey")]
    # State in CSV can be title case; ensure PA lookup finds Alexander Wang
    for (k, v) in list(key_to_row.items()):
        if k[0] == "alexander wang" and v["student_id"] == 1:
            key_to_row[("alex wang", "pennsylvania")] = v
            key_to_row[("alex wang", "Pennsylvania")] = v
            break
    return key_to_row, next_id


def main():
    key_to_row, next_id = load_students()
    new_students = []
    out_rows = []

    for rank, name, team, total, finals in ROWS:
        state = TEAM_TO_STATE.get(team, "")
        key = (name.strip().lower(), state)
        row = key_to_row.get(key)
        if not row and state:
            row = key_to_row.get((name.strip().lower(), ""))
        if not row:
            # Fallback: same name, any state (avoid duplicate for cross-state teams)
            for (k, v) in key_to_row.items():
                if k[0] == name.strip().lower():
                    row = v
                    break
        if row:
            out_rows.append((row["student_id"], row["student_name"], 2023, "A", rank, total, finals))
            continue
        sid = next_id
        next_id += 1
        canon_name = name.strip()
        key_to_row[key] = {"student_id": sid, "student_name": canon_name, "state": state}
        new_students.append({"student_id": sid, "student_name": canon_name, "state": state, "team_ids": "", "alias": ""})
        out_rows.append((sid, canon_name, 2023, "A", rank, total, finals))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "results_A.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["student_id", "student_name", "year", "division", "rank", "total_score", "finals_score"])
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
