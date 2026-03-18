#!/usr/bin/env python3
"""
One-off: Add PUMaC 2024 Combinatorics B results from pasted table.
Resolves (name, state) via students.csv; adds new students as needed.
Uses student_id 2214 for Qiao Zhang as requested.
"""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "pumac-b-combinator" / "year=2024"


# Pasted table: rank, name, score, p1..p8
ROWS: list[tuple[int, str, float, int, int, int, int, int, int, int, int]] = [
    (1, "Qiao Zhang", 17.527, 1, 1, 1, 1, 1, 1, 0, 1),
    (2, "Alex Zhao", 15.581, 1, 1, 1, 1, 1, 1, 1, 0),
    (2, "Elbert Ho", 15.581, 1, 1, 1, 1, 1, 1, 1, 0),
    (2, "Peyton Li", 15.581, 1, 1, 1, 1, 1, 1, 1, 0),
    (5, "Derrick Chen", 10.486, 1, 1, 1, 1, 0, 0, 1, 0),
    (6, "Jacob Chung", 10.456, 1, 1, 0, 1, 1, 1, 0, 0),
    (7, "Andrew Zhou", 10.088, 0, 1, 1, 1, 1, 1, 0, 0),
    (8, "Thomas McCurley", 9.213, 1, 1, 1, 1, 1, 0, 0, 0),
    (8, "Eric Zhong", 9.213, 1, 1, 1, 1, 1, 0, 0, 0),
    (10, "Suhas Kondapalli", 8.825, 1, 0, 1, 1, 0, 0, 1, 0),
    (11, "Rhys Llewellyn-Jones", 8.713, 1, 1, 1, 0, 0, 0, 1, 0),
    (12, "Nathan Lee", 8.582, 1, 0, 1, 0, 1, 1, 0, 0),
    (13, "Maiya Qiu", 8.315, 0, 1, 1, 0, 1, 1, 0, 0),
    (14, "Nikhil Byrapuram", 8.164, 1, 1, 0, 1, 0, 1, 0, 0),
    (15, "Eric Dai", 7.653, 1, 1, 0, 1, 1, 0, 0, 0),
    (16, "Yuming Su", 7.552, 1, 0, 1, 1, 1, 0, 0, 0),
    (17, "Atticus Masuzawa", 7.440, 1, 1, 1, 0, 1, 0, 0, 0),
    (18, "Harrison Chen", 7.286, 0, 1, 1, 1, 1, 0, 0, 0),
    (18, "Andrew Xie", 7.286, 0, 1, 1, 1, 1, 0, 0, 0),
    (18, "Ayan Dalmia", 7.286, 0, 1, 1, 1, 1, 0, 0, 0),
    (21, "Ryan Zhang", 6.921, 1, 1, 1, 1, 0, 0, 0, 0),
    (21, "Tianze Qiu", 6.921, 1, 1, 1, 1, 0, 0, 0, 0),
    (21, "Jason Liu", 6.921, 1, 1, 1, 1, 0, 0, 0, 0),
    (21, "Emmett Chen", 6.921, 1, 1, 1, 1, 0, 0, 0, 0),
    (21, "Benjamin Sun", 6.921, 1, 1, 1, 1, 0, 0, 0, 0),
    (21, "April Sun", 6.921, 1, 1, 1, 1, 0, 0, 0, 0),
    (21, "Xinqi Jessie Wang", 6.921, 1, 1, 1, 1, 0, 0, 0, 0),
    (28, "Ziyi Kaya Yang", 6.136, 0, 0, 1, 1, 0, 1, 0, 0),
    (28, "Wenqing Eric Mao", 6.136, 0, 0, 1, 1, 0, 1, 0, 0),
    (30, "Hridaan Mehta", 5.726, 0, 1, 0, 1, 1, 0, 0, 0),
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
        state = ""
        # Special-case: Qiao Zhang should use student_id 2214.
        if name == "Qiao Zhang":
            sid = 2214
            row = None
            for (k, v) in key_to_row.items():
                if v["student_id"] == sid:
                    row = v
                    break
            sname = row["student_name"] if row else name
            out_rows.append((sid, sname, 2024, "B", rank, score, p1, p2, p3, p4, p5, p6, p7, p8))
            continue

        # State is unknown from this table; resolve primarily by name.
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

