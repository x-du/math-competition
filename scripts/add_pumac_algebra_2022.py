#!/usr/bin/env python3
"""
Add PUMAC Algebra 2022 (Division A) from pasted table.
Resolves (name, state) via students.csv; adds new students as needed.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "pumac-algebra" / "year=2022"

TEAM_TO_STATE = {
    "TJ A": "Virginia", "Lehigh Valley Fire": "Pennsylvania", "Lehigh Valley Ice": "Pennsylvania",
    "PRISMS Falcons": "California", "Florida Alligators": "Florida", "BCA 1": "New Jersey",
    "Lexington Alpha": "Massachusetts", "Westchester Area Math Circle": "New York",
    "Tin Man": "California", "Phillips Academy": "Massachusetts", "Random Math": "",
    "No Coast Best Coast": "Illinois", "Pirates A": "California", "BBMC-math Delta": "Maryland",
    "Poolesville Math Team A": "Maryland", "Scarecrow": "California",
}

# Pasted table: rank, name, team, score, p1..p8
ROWS = [
    (1, "Aaron Hu", "Florida Alligators", 17.868, 1, 1, 1, 1, 1, 1, 1, 0),
    (2, "Vikram Sarkar", "Westchester Area Math Circle", 14.015, 1, 1, 1, 1, 1, 1, 0, 0),
    (3, "Zach Perry", "Lexington Alpha", 12.165, 0, 0, 0, 1, 1, 1, 1, 0),
    (4, "Andrew Lin", "Lehigh Valley Fire", 11.572, 0, 1, 0, 1, 0, 1, 1, 0),
    (5, "Andrew Wen", "Phillips Academy", 11.416, 1, 1, 1, 1, 0, 1, 0, 0),
    (6, "Alex Wang", "Lehigh Valley Fire", 10.769, 1, 1, 1, 1, 1, 0, 0, 0),
    (6, "Nilay Mishra", "Random Math", 10.769, 1, 1, 1, 1, 1, 0, 0, 0),
    (6, "Zani Xu", "TJ A", 10.769, 1, 1, 1, 1, 1, 0, 0, 0),
    (9, "Jeff Lin", "Lexington Alpha", 9.798, 1, 0, 0, 1, 1, 1, 0, 0),
    (9, "Sargam Mondal", "Individuals Team 155", 9.798, 1, 0, 0, 1, 1, 1, 0, 0),
    (11, "Paul Gutkovich", "Tin Man", 9.283, 0, 1, 1, 1, 1, 0, 0, 0),
    (12, "Aiden Feyerherm", "BBMC-math Delta", 9.205, 1, 1, 0, 1, 0, 1, 0, 0),
    (13, "Josiah Moltz", "Tin Man", 8.559, 1, 1, 0, 1, 1, 0, 0, 0),
    (14, "Amol Rama", "Random Math", 8.459, 0, 1, 0, 0, 1, 0, 1, 0),
    (15, "Zehan Peter Pan", "PRISMS Falcons", 8.303, 1, 1, 1, 0, 1, 0, 0, 0),
    (16, "Aryan Raj", "Individuals Team 155", 8.169, 1, 1, 1, 1, 0, 0, 0, 0),
    (16, "Krishna Pothapragada", "No Coast Best Coast", 8.169, 1, 1, 1, 1, 0, 0, 0, 0),
    (16, "Edward Xiong", "Pirates A", 8.169, 1, 1, 1, 1, 0, 0, 0, 0),
    (19, "Milo Stammers", "Poolesville Math Team A", 7.720, 0, 1, 0, 1, 0, 1, 0, 0),
    (20, "Calvin Wang", "TJ A", 7.345, 1, 1, 0, 0, 0, 0, 1, 0),
    (21, "David Wei", "TJ A", 6.817, 0, 1, 1, 0, 1, 0, 0, 0),
    (21, "Neel Kolhe", "Random Math", 6.817, 0, 1, 1, 0, 1, 0, 0, 0),
    (23, "Marvin Mao", "BCA 1", 6.684, 0, 1, 1, 1, 0, 0, 0, 0),
    (24, "William Li", "Florida Alligators", 6.296, 1, 0, 1, 0, 1, 0, 0, 0),
    (25, "Alan Vladimiroff", "TJ A", 6.162, 1, 0, 1, 1, 0, 0, 0, 0),
    (26, "Vincent Zhang", "Lehigh Valley Fire", 6.092, 1, 1, 0, 0, 1, 0, 0, 0),
    (26, "Nikhil Mathihalli", "Random Math", 6.092, 1, 1, 0, 0, 1, 0, 0, 0),
    (26, "Sicheng Kevin Zhou", "PRISMS Falcons", 6.092, 1, 1, 0, 0, 1, 0, 0, 0),
    (29, "Varun Gupta", "Lehigh Valley Ice", 5.959, 1, 1, 0, 1, 0, 0, 0, 0),
    (30, "Max Shepard", "Scarecrow", 5.703, 1, 1, 1, 0, 0, 0, 0, 0),
    (30, "Yifan Kang", "Phillips Academy", 5.703, 1, 1, 1, 0, 0, 0, 0, 0),
    (30, "Steven Yu", "Lexington Alpha", 5.703, 1, 1, 1, 0, 0, 0, 0, 0),
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

    for tup in ROWS:
        rank, name, team, score = tup[0], tup[1], tup[2], tup[3]
        p1, p2, p3, p4, p5, p6, p7, p8 = tup[4], tup[5], tup[6], tup[7], tup[8], tup[9], tup[10], tup[11]
        state = TEAM_TO_STATE.get(team, "")
        key = (name.strip().lower(), state)
        row = key_to_row.get(key) or key_to_row.get((name.strip().lower(), ""))
        if not row:
            for (k, v) in key_to_row.items():
                if k[0] == name.strip().lower():
                    row = v
                    break
        if row:
            out_rows.append((row["student_id"], row["student_name"], 2022, "A", rank, score, p1, p2, p3, p4, p5, p6, p7, p8))
            continue
        sid = next_id
        next_id += 1
        canon_name = name.strip()
        key_to_row[key] = {"student_id": sid, "student_name": canon_name, "state": state}
        new_students.append({"student_id": sid, "student_name": canon_name, "state": state, "team_ids": "", "alias": ""})
        out_rows.append((sid, canon_name, 2022, "A", rank, score, p1, p2, p3, p4, p5, p6, p7, p8))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "results_A.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["student_id", "student_name", "year", "division", "rank", "score", "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"])
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
