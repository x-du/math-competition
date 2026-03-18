#!/usr/bin/env python3
"""
One-off: Add PUMaC 2025 Number Theory B results from pasted table.
Resolves (name, state) via students.csv; adds new students as needed.
"""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "pumac-b-combinator" / "year=2025"


# Pasted table: rank, name, score, p1..p8
ROWS: list[tuple[int, str, float, int, int, int, int, int, int, int, int]] = [
    (1, "Arjun Pandey", 24.740, 1, 1, 1, 1, 1, 1, 1, 1),
    (2, "Advait Joshi", 16.239, 1, 1, 1, 1, 0, 0, 1, 1),
    (3, "Andrew Chai", 16.174, 1, 1, 1, 1, 1, 1, 0, 0),
    (3, "Liran Zhou", 16.174, 1, 1, 1, 1, 1, 1, 0, 0),
    (3, "Eric Dai", 16.174, 1, 1, 1, 1, 1, 1, 0, 0),
    (6, "Maiya Qiu", 11.577, 1, 1, 1, 1, 1, 0, 0, 0),
    (6, "Max Li", 11.577, 1, 1, 1, 1, 1, 0, 0, 0),
    (8, "Eric Huang", 10.948, 1, 1, 1, 1, 0, 0, 1, 0),
    (8, "Suvid Bordia", 10.948, 1, 1, 1, 1, 0, 0, 1, 0),
    (10, "Shlok Mukund", 9.346, 0, 1, 1, 1, 0, 0, 1, 0),
    (11, "Brandon Ni", 9.108, 1, 1, 0, 1, 0, 0, 1, 0),
    (12, "Ryan Zhang", 8.960, 1, 1, 1, 0, 1, 0, 0, 0),
    (12, "Tane Park", 8.960, 1, 1, 1, 0, 1, 0, 0, 0),
    (14, "Bret Huang", 8.332, 1, 1, 1, 0, 0, 0, 1, 0),
    (14, "Ryan Zhu", 8.332, 1, 1, 1, 0, 0, 0, 1, 0),
    (16, "Sophie Chen", 7.673, 1, 1, 1, 1, 0, 0, 0, 0),
    (16, "Pimmy Maneepairoj", 7.673, 1, 1, 1, 1, 0, 0, 0, 0),
    (16, "Kalina Liu", 7.673, 1, 1, 1, 1, 0, 0, 0, 0),
    (16, "Kyle Chen", 7.673, 1, 1, 1, 1, 0, 0, 0, 0),
    (16, "Bobby Qian", 7.673, 1, 1, 1, 1, 0, 0, 0, 0),
    (16, "Karam Gill", 7.673, 1, 1, 1, 1, 0, 0, 0, 0),
    (16, "Aarush Rachakonda", 7.673, 1, 1, 1, 1, 0, 0, 0, 0),
    (23, "Angelica Feng", 6.730, 0, 1, 1, 0, 0, 0, 1, 0),
    (24, "Jonathan Borges", 6.718, 1, 0, 1, 0, 0, 0, 1, 0),
    (24, "Patrick Gao", 6.718, 1, 0, 1, 0, 0, 0, 1, 0),
    (24, "Florina Zhu", 6.718, 1, 0, 1, 0, 0, 0, 1, 0),
    (27, "Shaoyan (Evan) Chen", 6.491, 1, 1, 0, 0, 0, 0, 1, 0),
    (28, "Charles Zheng", 6.071, 0, 1, 1, 1, 0, 0, 0, 0),
    (28, "William Liu", 6.071, 0, 1, 1, 1, 0, 0, 0, 0),
    (28, "Oscar Huang", 6.071, 0, 1, 1, 1, 0, 0, 0, 0),
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
                (row["student_id"], row["student_name"], 2025, "B", rank, score, p1, p2, p3, p4, p5, p6, p7, p8)
            )
            continue

        sid = next_id
        next_id += 1
        canon_name = name.strip()
        key_to_row[key] = {"student_id": sid, "student_name": canon_name, "state": state}
        new_students.append(
            {"student_id": sid, "student_name": canon_name, "state": state, "team_ids": "", "alias": ""}
        )
        out_rows.append((sid, canon_name, 2025, "B", rank, score, p1, p2, p3, p4, p5, p6, p7, p8))

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

