#!/usr/bin/env python3
"""
Add PUMAC Algebra 2023 (Division A) from pasted table.
Resolves (name, state) via students.csv; adds new students as needed.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "pumac-algebra" / "year=2023"

TEAM_TO_STATE = {
    "Lehigh Valley Fire": "Pennsylvania", "TJ A": "Virginia", "TJ B": "Virginia", "BCA 1": "New Jersey",
    "Texas Ramanujan": "Texas", "Texas Hardy": "Texas", "Florida Alligators": "Florida",
    "CT Cyborgs": "Connecticut", "MoCoSwaggaSquad": "Maryland", "Florida Beaches": "Florida",
    "Phillips Academy": "Massachusetts", "Lexington Alpha": "Massachusetts",
    "Lexington Beta": "Massachusetts", "GWe UAre Not NAffiliated": "Georgia",
    "BBMC-math Delta": "Maryland", "Tin Man": "California",
}

# Pasted table: rank, name, team, score, p1, p2, p3, p4, p5, p6, p7, p8
ROWS = [
    (1, "Alex Wang", "Lehigh Valley Fire", 15.913, 1, 1, 1, 1, 1, 1, 0, 0),
    (2, "Sargam Mondal", "Lehigh Valley Fire", 13.493, 1, 1, 0, 1, 1, 1, 0, 0),
    (3, "Calvin Wang", "TJ A", 11.384, 1, 0, 1, 1, 0, 0, 1, 0),
    (4, "Marvin Mao", "BCA 1", 9.998, 1, 0, 1, 1, 1, 0, 0, 0),
    (5, "Vikram Sarkar", "CT Cyborgs", 9.973, 1, 1, 1, 0, 1, 0, 0, 0),
    (6, "Sam Wang", "Lexington Beta", 9.438, 1, 0, 1, 1, 0, 1, 0, 0),
    (7, "Daniel He", "MoCoSwaggaSquad", 9.414, 1, 1, 1, 0, 0, 1, 0, 0),
    (8, "Aaron Hu", "Florida Alligators", 7.671, 1, 1, 1, 1, 0, 0, 0, 0),
    (8, "David Wei", "TJ A", 7.671, 1, 1, 1, 1, 0, 0, 0, 0),
    (8, "Bole Ying", "Lehigh Valley Fire", 7.671, 1, 1, 1, 1, 0, 0, 0, 0),
    (8, "Andrew Lin", "Lehigh Valley Fire", 7.671, 1, 1, 1, 1, 0, 0, 0, 0),
    (8, "Darsh Patel", "Florida Beaches", 7.671, 1, 1, 1, 1, 0, 0, 0, 0),
    (8, "Yifan Kang", "Phillips Academy", 7.671, 1, 1, 1, 1, 0, 0, 0, 0),
    (8, "Adam Ge", "Lexington Alpha", 7.671, 1, 1, 1, 1, 0, 0, 0, 0),
    (8, "Alexander Jun", "Texas Ramanujan", 7.671, 1, 1, 1, 1, 0, 0, 0, 0),
    (16, "Sitta Tantikul", "Individuals Team 161", 7.018, 1, 0, 0, 1, 0, 1, 0, 0),
    (17, "Kalan Warusa", "BBMC-math Delta", 6.993, 1, 1, 0, 0, 0, 1, 0, 0),
    (18, "Ashley Zhu", "Tin Man", 5.597, 1, 0, 1, 1, 0, 0, 0, 0),
    (18, "Daniel Potievsky", "Tin Man", 5.597, 1, 0, 1, 1, 0, 0, 0, 0),
    (18, "Jiwu Jang", "Individuals Team 160", 5.597, 1, 0, 1, 1, 0, 0, 0, 0),
    (18, "Yusuf Sheikh", "Florida Alligators", 5.597, 1, 0, 1, 1, 0, 0, 0, 0),
    (18, "Josh Shin", "GWe UAre Not NAffiliated", 5.597, 1, 0, 1, 1, 0, 0, 0, 0),
    (18, "Krithik Manoharan", "Texas Hardy", 5.597, 1, 0, 1, 1, 0, 0, 0, 0),
    (24, "Corey Zhao", "Lexington Beta", 5.572, 1, 1, 1, 0, 0, 0, 0, 0),
    (24, "Aryan Raj", "CT Cyborgs", 5.572, 1, 1, 1, 0, 0, 0, 0, 0),
    (26, "Zhan Jin", "Individuals Team 161", 5.250, 1, 1, 0, 1, 0, 0, 0, 0),
    (26, "William Li", "Florida Alligators", 5.250, 1, 1, 0, 1, 0, 0, 0, 0),
    (26, "Jason Hao", "TJ B", 5.250, 1, 1, 0, 1, 0, 0, 0, 0),
    (26, "Daniel Gilman", "BCA 1", 5.250, 1, 1, 0, 1, 0, 0, 0, 0),
    (26, "Jacob Xu", "Lexington Alpha", 5.250, 1, 1, 0, 1, 0, 0, 0, 0),
    (26, "Bill Qian", "MoCoSwaggaSquad", 5.250, 1, 1, 0, 1, 0, 0, 0, 0),
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
        if k[0] == "william qian":
            key_to_row[("bill qian", "maryland")] = v
            key_to_row[("bill qian", "")] = v
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
            out_rows.append((row["student_id"], row["student_name"], 2023, "A", rank, score, p1, p2, p3, p4, p5, p6, p7, p8))
            continue
        sid = next_id
        next_id += 1
        canon_name = name.strip()
        key_to_row[key] = {"student_id": sid, "student_name": canon_name, "state": state}
        new_students.append({"student_id": sid, "student_name": canon_name, "state": state, "team_ids": "", "alias": ""})
        out_rows.append((sid, canon_name, 2023, "A", rank, score, p1, p2, p3, p4, p5, p6, p7, p8))

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
