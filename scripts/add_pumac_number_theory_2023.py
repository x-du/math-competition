#!/usr/bin/env python3
"""
Add PUMAC Number Theory 2023 (Division A) from pasted table.
Resolves (name, state) via students.csv; adds new students as needed.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "pumac-number-theory" / "year=2023"

TEAM_TO_STATE = {
    "Lehigh Valley Fire": "Pennsylvania", "Lehigh Valley Ice": "Pennsylvania",
    "TJ A": "Virginia", "TJ B": "Virginia", "BCA 1": "New Jersey",
    "Texas Ramanujan": "Texas", "Texas Hardy": "Texas", "Florida Alligators": "Florida",
    "CT Cyborgs": "Connecticut", "MoCoSwaggaSquad": "Maryland", "Tin Man": "California",
    "Phillips Academy": "Massachusetts", "GWe UAre Not NAffiliated": "Georgia",
    "BBMC-math Delta": "Maryland", "PRISMS Falcons": "California", "404 Error": "Virginia",
    "Pirates A": "California", "Pirates B": "California", "Scarecrow": "California",
    "Yu's Alligator": "Florida", "Lion": "California",
}

# Pasted table: rank, name, team, score, p1..p8 (row 33 has no name - omitted)
ROWS = [
    (1, "Calvin Wang", "TJ A", 15.192, 1, 1, 1, 0, 0, 1, 0, 1),
    (1, "Sargam Mondal", "Lehigh Valley Fire", 15.192, 1, 1, 1, 0, 0, 1, 0, 1),
    (1, "Alex Wang", "Lehigh Valley Fire", 15.192, 1, 1, 1, 0, 0, 1, 0, 1),
    (4, "Andrew Li", "Tin Man", 13.195, 1, 0, 0, 1, 1, 0, 1, 0),
    (5, "Kelin Zhu", "MoCoSwaggaSquad", 11.403, 1, 0, 1, 1, 1, 0, 0, 0),
    (6, "Kailin Kevin Yang", "PRISMS Falcons", 10.240, 1, 1, 1, 1, 0, 0, 0, 0),
    (7, "Yutong Mark Zhao", "PRISMS Falcons", 9.025, 1, 0, 0, 1, 0, 0, 1, 0),
    (8, "Channing Yang", "Texas Ramanujan", 8.891, 1, 0, 0, 0, 0, 1, 0, 1),
    (9, "Allen Wang", "Lehigh Valley Fire", 8.668, 1, 0, 1, 0, 1, 0, 0, 0),
    (10, "Vikram Sarkar", "CT Cyborgs", 8.198, 1, 0, 1, 0, 0, 0, 0, 1),
    (11, "Royce Yao", "Individuals Team 160", 7.233, 1, 0, 1, 1, 0, 0, 0, 0),
    (12, "Haokai Ma", "Tin Man", 6.946, 1, 1, 0, 1, 0, 0, 0, 0),
    (12, "Michael Middlezong", "BCA 1", 6.946, 1, 1, 0, 1, 0, 0, 0, 0),
    (12, "Pavan Jayaraman", "Pirates A", 6.946, 1, 1, 0, 1, 0, 0, 0, 0),
    (15, "Patrick Du", "404 Error", 5.192, 1, 0, 0, 0, 0, 1, 0, 0),
    (15, "Jeffrey Yin", "BBMC-math Delta", 5.192, 1, 0, 0, 0, 0, 1, 0, 0),
    (17, "Aditya Pahuja", "Tin Man", 4.904, 1, 0, 0, 0, 0, 0, 0, 1),
    (17, "Abhi Palikala", "TJ A", 4.904, 1, 0, 0, 0, 0, 0, 0, 1),
    (17, "Arjun Pagidi", "TJ A", 4.904, 1, 0, 0, 0, 0, 0, 0, 1),
    (20, "Kyle Wu", "Scarecrow", 4.499, 1, 0, 1, 0, 0, 0, 0, 0),
    (20, "Tony Zhang", "404 Error", 4.499, 1, 0, 1, 0, 0, 0, 0, 0),
    (20, "David Ji", "Yu's Alligator", 4.499, 1, 0, 1, 0, 0, 0, 0, 0),
    (20, "Amogh Akella", "Texas Hardy", 4.499, 1, 0, 1, 0, 0, 0, 0, 0),
    (24, "Sophia Jin", "Lion", 4.211, 1, 1, 0, 0, 0, 0, 0, 0),
    (24, "Jiwu Jang", "Individuals Team 160", 4.211, 1, 1, 0, 0, 0, 0, 0, 0),
    (24, "Miranda Wang", "Lehigh Valley Ice", 4.211, 1, 1, 0, 0, 0, 0, 0, 0),
    (24, "Jason Mao", "Lehigh Valley Fire", 4.211, 1, 1, 0, 0, 0, 0, 0, 0),
    (24, "Aarush Prasad", "Pirates B", 4.211, 1, 1, 0, 0, 0, 0, 0, 0),
    (24, "David Wang", "MoCoSwaggaSquad", 4.211, 1, 1, 0, 0, 0, 0, 0, 0),
    (24, "Heyang Felicity Ni", "PRISMS Falcons", 4.211, 1, 1, 0, 0, 0, 0, 0, 0),
    (24, "Roger Fan", "GWe UAre Not NAffiliated", 4.211, 1, 1, 0, 0, 0, 0, 0, 0),
    (24, "Jordan Lefkowitz", "CT Cyborgs", 4.211, 1, 1, 0, 0, 0, 0, 0, 0),
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
