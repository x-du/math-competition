#!/usr/bin/env python3
"""
One-off: Add PUMaC 2025 Geometry B results from pasted table.
Resolves (name, state) via students.csv; adds new students as needed.
"""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "pumac-b-geometry" / "year=2025"


# Pasted table: rank, name, score, p1..p8
ROWS: list[tuple[int, str, float, int, int, int, int, int, int, int, int]] = [
    (1, "Liran Zhou", 15.983, 1, 1, 1, 1, 1, 1, 0, 0),
    (2, "Kevin Feng", 12.344, 1, 1, 1, 1, 0, 1, 0, 0),
    (3, "Eden He", 11.833, 1, 1, 1, 1, 1, 0, 0, 0),
    (4, "Atticus Masuzawa", 10.891, 0, 1, 1, 1, 0, 1, 0, 0),
    (5, "Alexander Wang", 10.019, 1, 0, 1, 1, 1, 0, 0, 0),
    (6, "Jay Wang", 9.042, 1, 1, 1, 0, 0, 1, 0, 0),
    (6, "Hanru Zhang", 9.042, 1, 1, 1, 0, 0, 1, 0, 0),
    (6, "Fiona Chen", 9.042, 1, 1, 1, 0, 0, 1, 0, 0),
    (9, "Kevin Chen", 8.531, 1, 1, 1, 0, 1, 0, 0, 0),
    (9, "Yeojun Jung", 8.531, 1, 1, 1, 0, 1, 0, 0, 0),
    (9, "Joshua Shi", 8.531, 1, 1, 1, 0, 1, 0, 0, 0),
    (9, "Ryan Gong", 8.531, 1, 1, 1, 0, 1, 0, 0, 0),
    (13, "William Liu", 8.194, 1, 1, 1, 1, 0, 0, 0, 0),
    (13, "Xinqi Jessie Wang", 8.194, 1, 1, 1, 1, 0, 0, 0, 0),
    (15, "Kalina Liu", 6.907, 1, 1, 0, 0, 1, 0, 0, 0),
    (16, "Sidarth Singh", 6.716, 1, 0, 1, 0, 1, 0, 0, 0),
    (17, "Sophie Liu", 5.263, 0, 0, 1, 0, 1, 0, 0, 0),
    (18, "Arda Eroz", 5.117, 0, 1, 0, 1, 0, 0, 0, 0),
    (18, "Andy Wu", 5.117, 0, 1, 0, 1, 0, 0, 0, 0),
    (20, "Alexander Choi", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Olivia Fang", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Srinivasa Polisetty", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Alethea Liu", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Alexander Buteau", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Oscar Huang", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Iris Gao", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Eric Yuan", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Chris Ping Liu", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Dhagesh Desai", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Angelina Gao", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Albert Wu", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Arav Sonawane", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Sean Gao", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Maggie Li", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Sky Chen", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Hridaan Mehta", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Thomas McCurley", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "James Browning", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Tane Park", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Eric Chen", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Daniel Wu", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Victor Wang", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Miles Zhang", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Shreyan Dutt", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Sophie Chen", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Oma Makhija", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Nikhil McGowan", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Ray Cui", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Ekantika Chaudhuri", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Bowen Li", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
    (20, "Rithik Gumpu", 4.892, 1, 1, 1, 0, 0, 0, 0, 0),
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

