#!/usr/bin/env python3
"""
Add PUMAC 2022 Individual Rankings A from pasted table.
Resolves (name, state) via students.csv; adds new students as needed.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "pumac" / "year=2022"

TEAM_TO_STATE = {
    "TJ A": "Virginia", "Lehigh Valley Fire": "Pennsylvania", "Lehigh Valley Ice": "Pennsylvania",
    "PRISMS Falcons": "California", "Florida Alligators": "Florida", "Washington Gold": "Washington",
    "BCA 1": "New Jersey", "No Coast Best Coast": "Illinois", "Pirates A": "California",
    "Lexington Alpha": "Massachusetts", "Westchester Area Math Circle": "New York",
    "Tin Man": "California", "Phillips Academy": "Massachusetts", "Minnesota Gold": "Minnesota",
    "Random Math": "",
}

# Pasted table: rank, name, team, total, finals
ROWS = [
    (1, "Isabella Zhu", "TJ A", 3.741, 20),
    (2, "Alex Wang", "Lehigh Valley Fire", 3.698, 21),
    (3, "Yichen Cedric Xiao", "PRISMS Falcons", 3.549, 18),
    (4, "Aaron Hu", "Florida Alligators", 3.364, 10),
    (5, "Owen Zhang", "Washington Gold", 3.294, 18),
    (6, "Marvin Mao", "BCA 1", 3.278, 14),
    (7, "Wilbert Chu", "No Coast Best Coast", 3.276, 14),
    (8, "Alex Zhao", "Washington Gold", 3.230, 13),
    (9, "Pavan Jayaraman", "Pirates A", 3.202, 13),
    (10, "Jordan Lefkowitz", "Individuals Team 156", 3.191, 13),
    (11, "Ritwin Narra", "Individuals Team 157", 3.187, 16),
    (12, "Andrew Lin", "Lehigh Valley Fire", 3.106, 11),
    (13, "Jeff Lin", "Lexington Alpha", 3.090, 15),
    (14, "Calvin Wang", "TJ A", 3.036, 12),
    (15, "Vikram Sarkar", "Westchester Area Math Circle", 2.981, 9),
    (16, "Zach Perry", "Lexington Alpha", 2.881, 9),
    (17, "Skyler Le", "Lehigh Valley Fire", 2.851, 8),
    (18, "Krishna Pothapragada", "No Coast Best Coast", 2.843, 8),
    (19, "Nilay Mishra", "Random Math", 2.667, 6),
    (20, "Zani Xu", "TJ A", 2.632, 6),
    (21, "William Hua", "Lexington Alpha", 2.561, 5),
    (22, "Chris Qiu", "Lehigh Valley Fire", 2.532, 6),
    (23, "Sophia Zhang", "PRISMS Falcons", 2.492, 7),
    (24, "Jacob Paltrowitz", "Tin Man", 2.446, 7),
    (25, "Paul Gutkovich", "Tin Man", 2.414, 3),
    (26, "Andrew Wen", "Phillips Academy", 2.411, 5),
    (27, "Kailin Kevin Yang", "PRISMS Falcons", 2.407, 11),
    (28, "Isaac Chen", "Lehigh Valley Ice", 2.366, 5),
    (29, "Matthew Chen", "Minnesota Gold", 1.974, 2),
    (30, "Angeline Zhao", "Phillips Academy", 1.678, 1),
    (31, "Sargam Mondal", "Individuals Team 155", 1.453, 0),
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
    for (k, v) in list(key_to_row.items()):
        if k[0] == "alexander wang" and v["student_id"] == 1:
            key_to_row[("alex wang", "pennsylvania")] = v
            key_to_row[("alex wang", "Pennsylvania")] = v
            break
    # Chris Qiu -> Christopher Qiu if present
    for (k, v) in list(key_to_row.items()):
        if k[0] == "christopher qiu":
            key_to_row[("chris qiu", v["state"])] = v
            key_to_row[("chris qiu", v["state"].lower())] = v
            key_to_row[("chris qiu", "pennsylvania")] = v
            break
    # Zach Perry -> Zachary Perry (Lexington Alpha = MA)
    for (k, v) in list(key_to_row.items()):
        if k[0] == "zachary perry" and v.get("state") == "Massachusetts":
            key_to_row[("zach perry", "massachusetts")] = v
            key_to_row[("zach perry", "Massachusetts")] = v
            break
    return key_to_row, next_id


def main():
    key_to_row, next_id = load_students()
    new_students = []
    out_rows = []

    for rank, name, team, total, finals in ROWS:
        state = TEAM_TO_STATE.get(team, "")
        key = (name.strip().lower(), state)
        row = key_to_row.get(key) or key_to_row.get((name.strip().lower(), ""))
        if not row:
            for (k, v) in key_to_row.items():
                if k[0] == name.strip().lower():
                    row = v
                    break
        if row:
            out_rows.append((row["student_id"], row["student_name"], 2022, "A", rank, total, finals))
            continue
        sid = next_id
        next_id += 1
        canon_name = name.strip()
        key_to_row[key] = {"student_id": sid, "student_name": canon_name, "state": state}
        new_students.append({"student_id": sid, "student_name": canon_name, "state": state, "team_ids": "", "alias": ""})
        out_rows.append((sid, canon_name, 2022, "A", rank, total, finals))

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
