#!/usr/bin/env python3
"""
Add PUMAC Combinatorics 2022 (Division A) from pasted table.
Resolves (name, state) via students.csv; adds new students as needed.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "pumac-combinator" / "year=2022"

TEAM_TO_STATE = {
    "BCA 1": "New Jersey", "Pirates A": "California", "PRISMS Falcons": "California",
    "No Coast Best Coast": "Illinois", "Washington Gold": "Washington", "Tin Man": "California",
    "Lehigh Valley Fire": "Pennsylvania", "BBMC-math Delta": "Maryland",
    "TJ A": "Virginia", "Lexington Alpha": "Massachusetts", "Phillips Academy": "Massachusetts",
    "Poolesville Math Team A": "Maryland", "Montgomery A": "Maryland", "Knights Alpha": "California",
    "TX Momentum Circle": "Texas", "Scarecrow": "California",
    "Westchester Area Math Circle": "New York",
}

# Pasted table: rank, name, team, score, p1..p8
ROWS = [
    (1, "Marvin Mao", "BCA 1", 16.229, 1, 1, 1, 1, 1, 1, 1, 0),
    (2, "Pavan Jayaraman", "Pirates A", 14.808, 0, 1, 1, 1, 1, 1, 1, 0),
    (3, "Yichen Cedric Xiao", "PRISMS Falcons", 13.954, 1, 1, 0, 1, 1, 0, 0, 1),
    (4, "Wilbert Chu", "No Coast Best Coast", 11.079, 1, 1, 0, 1, 0, 1, 1, 0),
    (5, "Owen Zhang", "Washington Gold", 10.622, 1, 1, 1, 1, 1, 0, 0, 0),
    (6, "Jacob Paltrowitz", "Tin Man", 10.317, 1, 1, 0, 1, 1, 1, 0, 0),
    (7, "Alex Zhao", "Washington Gold", 10.220, 1, 0, 1, 0, 1, 0, 1, 0),
    (8, "Andrew Lin", "Lehigh Valley Fire", 9.875, 1, 1, 1, 0, 1, 1, 0, 0),
    (9, "Chris Qiu", "Lehigh Valley Fire", 9.693, 1, 1, 1, 1, 0, 1, 0, 0),
    (10, "Skyler Le", "Lehigh Valley Fire", 8.374, 1, 1, 0, 0, 0, 1, 1, 0),
    (11, "John Gupta-She", "Tin Man", 8.359, 1, 1, 0, 1, 1, 0, 0, 0),
    (12, "Edward Xiong", "Pirates A", 7.917, 1, 1, 1, 0, 1, 0, 0, 0),
    (12, "Jeffrey Yin", "BBMC-math Delta", 7.917, 1, 1, 1, 0, 1, 0, 0, 0),
    (14, "Ritwin Narra", "Individuals Team 157", 7.870, 0, 0, 1, 0, 0, 1, 1, 0),
    (15, "Jerry Zhang", "TX Momentum Circle", 7.612, 1, 1, 0, 0, 1, 1, 0, 0),
    (16, "Andrew Li", "Scarecrow", 7.549, 0, 0, 0, 1, 1, 1, 0, 0),
    (17, "Joseph Othman", "Tin Man", 7.259, 0, 1, 1, 0, 0, 0, 1, 0),
    (18, "Zani Xu", "TJ A", 6.988, 1, 1, 1, 0, 0, 1, 0, 0),
    (18, "Jeff Lin", "Lexington Alpha", 6.988, 1, 1, 1, 0, 0, 1, 0, 0),
    (18, "Eric Wang", "Phillips Academy", 6.988, 1, 1, 1, 0, 0, 1, 0, 0),
    (18, "Andrew Yuan", "Poolesville Math Team A", 6.988, 1, 1, 1, 0, 0, 1, 0, 0),
    (18, "Lewis Lau", "Montgomery A", 6.988, 1, 1, 1, 0, 0, 1, 0, 0),
    (18, "Harry Kim", "Phillips Academy", 6.988, 1, 1, 1, 0, 0, 1, 0, 0),
    (24, "Alan Vladimiroff", "TJ A", 6.497, 0, 1, 1, 0, 1, 0, 0, 0),
    (25, "Vincent Trang", "TJ A", 6.388, 1, 0, 1, 1, 0, 0, 0, 0),
    (26, "Aiden Feyerherm", "BBMC-math Delta", 6.083, 1, 0, 0, 1, 0, 1, 0, 0),
    (26, "Vincent Chen", "Washington Gold", 6.083, 1, 0, 0, 1, 0, 1, 0, 0),
    (28, "Vivian Loh", "Individuals Team 156", 6.009, 0, 1, 0, 1, 0, 1, 0, 0),
    (28, "Eric Wang", "Knights Alpha", 6.009, 0, 1, 0, 1, 0, 1, 0, 0),
    (30, "Frank Wong", "Scarecrow", 5.472, 1, 1, 0, 1, 0, 0, 0, 0),
    (30, "Solon Sun", "Individuals Team 155", 5.472, 1, 1, 0, 1, 0, 0, 0, 0),
    (30, "Derek Xu", "Westchester Area Math Circle", 5.472, 1, 1, 0, 1, 0, 0, 0, 0),
    (30, "Jason Mao", "Lehigh Valley Fire", 5.472, 1, 1, 0, 1, 0, 0, 0, 0),
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
        if k[0] == "christopher qiu":
            key_to_row[("chris qiu", "pennsylvania")] = v
            key_to_row[("chris qiu", "Pennsylvania")] = v
            key_to_row[("chris qiu", v["state"])] = v
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
