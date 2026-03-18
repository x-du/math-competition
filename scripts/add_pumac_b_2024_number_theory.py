#!/usr/bin/env python3
"""
One-off: Add PUMaC 2024 Number Theory B results from pasted table.
Resolves (name, state) via students.csv; adds new students as needed.
"""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "pumac-b-number-theory" / "year=2024"


# Pasted table: rank, name, score, p1..p8
ROWS: list[tuple[int, str, float, int, int, int, int, int, int, int, int]] = [
    (1, "Harry Gao", 16.297, 1, 1, 1, 1, 1, 1, 0, 0),
    (2, "Participant 123 - 1 (Liran Zhou)", 15.450, 1, 1, 1, 1, 0, 1, 1, 0),
    (3, "Advait Joshi", 15.191, 1, 1, 0, 0, 0, 1, 1, 1),
    (4, "Jason Lu", 13.533, 1, 1, 0, 1, 1, 0, 1, 0),
    (5, "Benjamin Song", 11.336, 1, 1, 1, 1, 0, 0, 1, 0),
    (6, "Katherine Li", 10.761, 1, 0, 1, 1, 1, 0, 0, 0),
    (7, "Guanjie Zhao", 8.475, 1, 1, 1, 0, 0, 0, 1, 0),
    (8, "Sophie Chen", 7.782, 1, 1, 1, 1, 0, 0, 0, 0),
    (8, "Shirley Xiong", 7.782, 1, 1, 1, 1, 0, 0, 0, 0),
    (8, "William Liu", 7.782, 1, 1, 1, 1, 0, 0, 0, 0),
    (11, "Shining Sun", 6.831, 1, 1, 0, 0, 0, 1, 0, 0),
    (12, "Andrew Zhou", 6.360, 1, 0, 1, 1, 0, 0, 0, 0),
    (13, "Pranav Vijay", 6.271, 1, 1, 0, 0, 0, 0, 1, 0),
    (14, "Thomas McCurley", 6.102, 1, 0, 0, 0, 0, 0, 0, 1),
    (15, "April Sun", 5.578, 1, 1, 0, 1, 0, 0, 0, 0),
    (15, "Lindsay Miao", 5.578, 1, 1, 0, 1, 0, 0, 0, 0),
    (15, "Orion Lan", 5.578, 1, 1, 0, 1, 0, 0, 0, 0),
    (15, "Yunlu Rafi Shang", 5.578, 1, 1, 0, 1, 0, 0, 0, 0),
    (19, "Kellen Xue", 4.921, 1, 1, 1, 0, 0, 0, 0, 0),
    (19, "Ethan Li", 4.921, 1, 1, 1, 0, 0, 0, 0, 0),
    (19, "Suvid Bordia", 4.921, 1, 1, 1, 0, 0, 0, 0, 0),
    (19, "Dawson Park", 4.921, 1, 1, 1, 0, 0, 0, 0, 0),
    (19, "Nikhil Byrapuram", 4.921, 1, 1, 1, 0, 0, 0, 0, 0),
    (19, "Andrew Xie", 4.921, 1, 1, 1, 0, 0, 0, 0, 0),
    (19, "Alice Kim", 4.921, 1, 1, 1, 0, 0, 0, 0, 0),
    (19, "Jiawen Huang", 4.921, 1, 1, 1, 0, 0, 0, 0, 0),
    (19, "Lydia Zhou", 4.921, 1, 1, 1, 0, 0, 0, 0, 0),
    (19, "Jacob Chung", 4.921, 1, 1, 1, 0, 0, 0, 0, 0),
    (19, "Florina Zhu", 4.921, 1, 1, 1, 0, 0, 0, 0, 0),
    (19, "Daniel Wu", 4.921, 1, 1, 1, 0, 0, 0, 0, 0),
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

    for rank, name, score, p1, p2, p3, p4, p5, p6, p7, p8 in ROWS:
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
            out_rows.append(
                (row["student_id"], row["student_name"], 2024, "B", rank, score, p1, p2, p3, p4, p5, p6, p7, p8)
            )
            continue

        sid = next_id
        next_id += 1
        canon_name = name.strip()
        key_to_row[key] = {"student_id": sid, "student_name": canon_name, "state": state}
        new_students.append(
            {"student_id": sid, "student_name": canon_name, "state": state, "team_ids": "", "alias": ""}
        )
        out_rows.append((sid, canon_name, 2024, "B", rank, score, p1, p2, p3, p4, p5, p6, p7, p8))

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
                "score",
                "p1",
                "p2",
                "p3",
                "p4",
                "p5",
                "p6",
                "p7",
                "p8",
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

