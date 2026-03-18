#!/usr/bin/env python3
"""
Add PUMAC Number Theory 2022 (Division A) from pasted table.
Resolves (name, state) via students.csv; adds new students as needed.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "pumac-number-theory" / "year=2022"

TEAM_TO_STATE = {
    "Lehigh Valley Fire": "Pennsylvania", "TJ A": "Virginia", "PRISMS Falcons": "California",
    "No Coast Best Coast": "Illinois", "Tin Man": "California", "Knights Alpha": "California",
    "Minnesota Maroon": "Minnesota", "BCA 1": "New Jersey", "Washington Gold": "Washington",
    "Phillips Academy": "Massachusetts", "Westchester Area Math Circle": "New York",
    "Random Math": "", "Pirates A": "California", "Florida Alligators": "Florida",
    "Poolesville Math Team A": "Maryland", "Lexington Alpha": "Massachusetts",
}

# Pasted table: rank, name, team, score, p1..p8
ROWS = [
    (1, "Alex Wang", "Lehigh Valley Fire", 21.772, 1, 1, 1, 1, 1, 1, 1, 1),
    (2, "Isabella Zhu", "TJ A", 14.397, 1, 1, 1, 1, 0, 1, 1, 0),
    (3, "Yichen Cedric Xiao", "PRISMS Falcons", 12.107, 1, 1, 0, 1, 0, 1, 1, 0),
    (4, "Jordan Lefkowitz", "Individuals Team 156", 11.512, 1, 1, 1, 1, 1, 0, 0, 0),
    (5, "Calvin Wang", "TJ A", 11.478, 1, 1, 1, 0, 0, 1, 1, 0),
    (6, "Wilbert Chu", "No Coast Best Coast", 11.344, 1, 1, 1, 1, 0, 0, 1, 0),
    (7, "Kailin Kevin Yang", "PRISMS Falcons", 11.270, 1, 1, 1, 1, 0, 1, 0, 0),
    (7, "Skyler Le", "Lehigh Valley Fire", 11.270, 1, 1, 1, 1, 0, 1, 0, 0),
    (9, "Ritwin Narra", "Individuals Team 157", 10.216, 1, 0, 1, 0, 1, 1, 0, 0),
    (10, "Paul Gutkovich", "Tin Man", 9.916, 1, 0, 1, 1, 0, 0, 1, 0),
    (11, "Zehan Peter Pan", "PRISMS Falcons", 9.690, 0, 1, 1, 1, 0, 1, 0, 0),
    (12, "Maximus Lu", "Individuals Team 156", 9.188, 1, 1, 0, 0, 0, 1, 1, 0),
    (13, "Eric Wang", "Knights Alpha", 8.593, 1, 1, 1, 0, 1, 0, 0, 0),
    (14, "Garv Khurana", "Minnesota Maroon", 8.426, 1, 1, 1, 0, 0, 0, 1, 0),
    (15, "Vincent Trang", "TJ A", 8.352, 1, 1, 1, 0, 0, 1, 0, 0),
    (16, "Nikhil Mudumbi", "BCA 1", 8.218, 1, 1, 1, 1, 0, 0, 0, 0),
    (17, "Sheldon Tan", "Individuals Team 157", 7.849, 0, 1, 0, 0, 1, 0, 1, 0),
    (18, "Owen Zhang", "Washington Gold", 7.474, 0, 1, 0, 1, 0, 0, 1, 0),
    (19, "Eric Wang", "Phillips Academy", 7.164, 1, 0, 1, 0, 1, 0, 0, 0),
    (20, "Jason Mao", "Lehigh Valley Fire", 7.091, 1, 1, 0, 0, 0, 0, 0, 1),
    (20, "Vikram Sarkar", "Westchester Area Math Circle", 7.091, 1, 1, 0, 0, 0, 0, 0, 1),
    (22, "Lawson Wang", "Random Math", 7.012, 0, 1, 1, 0, 1, 0, 0, 0),
    (23, "Raina Wu", "Washington Gold", 6.303, 1, 1, 0, 0, 1, 0, 0, 0),
    (24, "Pavan Jayaraman", "Pirates A", 6.136, 1, 1, 0, 0, 0, 0, 1, 0),
    (25, "Yuji Peter Wang", "PRISMS Falcons", 6.061, 1, 1, 0, 0, 0, 1, 0, 0),
    (25, "Rui Jiang", "Florida Alligators", 6.061, 1, 1, 0, 0, 0, 1, 0, 0),
    (27, "Andrew Yuan", "Poolesville Math Team A", 5.928, 1, 1, 0, 1, 0, 0, 0, 0),
    (27, "Zach Perry", "Lexington Alpha", 5.928, 1, 1, 0, 1, 0, 0, 0, 0),
    (27, "Vincent Zhang", "Lehigh Valley Fire", 5.928, 1, 1, 0, 1, 0, 0, 0, 0),
    (30, "Lucas Tang", "Washington Gold", 5.584, 0, 0, 1, 0, 1, 0, 0, 0),
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
