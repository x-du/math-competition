#!/usr/bin/env python3
"""
Add PUMAC Geometry 2022 (Division A) from pasted table.
Resolves (name, state) via students.csv; adds new students as needed.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "pumac-geometry" / "year=2022"

TEAM_TO_STATE = {
    "TJ A": "Virginia", "Minnesota Gold": "Minnesota", "Florida Alligators": "Florida",
    "Lexington Alpha": "Massachusetts", "Washington Gold": "Washington",
    "No Coast Best Coast": "Illinois", "PRISMS Falcons": "California",
    "Lehigh Valley Ice": "Pennsylvania", "Phillips Academy": "Massachusetts",
    "Knights Alpha": "California", "Random Math": "", "Tin Man": "California",
    "Pirates A": "California", "BCA 1": "New Jersey", "TX Momentum Circle": "Texas",
    "Scarecrow": "California", "Westchester Area Math Circle": "New York",
}

# Pasted table: rank, name, team, score, p1..p8
ROWS = [
    (1, "Isabella Zhu", "TJ A", 16.158, 1, 0, 1, 1, 1, 1, 1, 0),
    (2, "Matthew Chen", "Minnesota Gold", 13.208, 1, 1, 0, 1, 1, 1, 0, 0),
    (3, "Aaron Hu", "Florida Alligators", 12.872, 0, 1, 1, 1, 1, 0, 1, 0),
    (4, "William Hua", "Lexington Alpha", 10.893, 0, 1, 1, 0, 1, 1, 0, 0),
    (5, "Alex Zhao", "Washington Gold", 10.866, 0, 1, 0, 1, 1, 0, 1, 0),
    (6, "Krishna Pothapragada", "No Coast Best Coast", 9.929, 0, 1, 1, 0, 0, 0, 0, 1),
    (7, "Jordan Lefkowitz", "Individuals Team 156", 9.101, 1, 1, 1, 0, 1, 0, 0, 0),
    (8, "Sophia Zhang", "PRISMS Falcons", 8.843, 1, 1, 1, 1, 0, 0, 0, 0),
    (9, "Isaac Chen", "Lehigh Valley Ice", 8.376, 1, 0, 0, 0, 1, 1, 0, 0),
    (10, "Angeline Zhao", "Phillips Academy", 8.319, 1, 1, 0, 0, 0, 1, 0, 0),
    (11, "Vivian Loh", "Individuals Team 156", 8.040, 1, 0, 0, 0, 1, 0, 1, 0),
    (12, "Aprameya Tripathy", "Knights Alpha", 7.472, 1, 0, 1, 0, 0, 0, 1, 0),
    (13, "Nikhil Mathihalli", "Random Math", 6.895, 0, 0, 1, 1, 1, 0, 0, 0),
    (14, "Nilay Mishra", "Random Math", 6.838, 0, 1, 1, 1, 0, 0, 0, 0),
    (15, "Lucas Tang", "Washington Gold", 6.585, 1, 0, 1, 0, 1, 0, 0, 0),
    (16, "John Gupta-She", "Tin Man", 6.527, 1, 1, 1, 0, 0, 0, 0, 0),
    (17, "Locke Cai", "Pirates A", 6.327, 1, 0, 1, 1, 0, 0, 0, 0),
    (17, "Raina Wu", "Washington Gold", 6.327, 1, 0, 1, 1, 0, 0, 0, 0),
    (17, "Nikhil Pesaladinne", "TJ A", 6.327, 1, 0, 1, 1, 0, 0, 0, 0),
    (20, "Maximus Lu", "Individuals Team 156", 5.466, 0, 0, 1, 0, 0, 0, 1, 0),
    (21, "Sicheng Kevin Zhou", "PRISMS Falcons", 5.090, 0, 1, 0, 0, 1, 0, 0, 0),
    (21, "Hongyi Huang", "Individuals Team 155", 5.090, 0, 1, 0, 0, 1, 0, 0, 0),
    (23, "David Wei", "TJ A", 4.889, 0, 0, 0, 1, 1, 0, 0, 0),
    (23, "Nikhil Mudumbi", "BCA 1", 4.889, 0, 0, 0, 1, 1, 0, 0, 0),
    (25, "Leo Yu", "TX Momentum Circle", 4.832, 0, 1, 0, 1, 0, 0, 0, 0),
    (26, "Steven Lou", "Scarecrow", 4.579, 1, 0, 0, 0, 1, 0, 0, 0),
    (27, "Daniel Potievsky", "Scarecrow", 4.522, 0, 1, 1, 0, 0, 0, 0, 0),
    (27, "Jack Fang", "Scarecrow", 4.522, 0, 1, 1, 0, 0, 0, 0, 0),
    (27, "Jaemin Kim", "Tin Man", 4.522, 0, 1, 1, 0, 0, 0, 0, 0),
    (27, "Andrew Tu", "Westchester Area Math Circle", 4.522, 0, 1, 1, 0, 0, 0, 0, 0),
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
