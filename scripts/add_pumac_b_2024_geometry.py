#!/usr/bin/env python3
"""
One-off: Add PUMaC 2024 Geometry B results from pasted table.
Resolves (name, state) via students.csv; adds new students as needed.
"""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "pumac-b-geometry" / "year=2024"


# Pasted table: rank, name, score, p1..p8
ROWS: list[tuple[int, str, float, int, int, int, int, int, int, int, int]] = [
    (1, "Jason Lian", 14.960, 1, 1, 1, 1, 1, 1, 0, 1),
    (2, "Jiawen Huang", 14.554, 1, 1, 1, 1, 1, 1, 1, 0),
    (3, "YEOJUN JAY JUNG", 13.082, 1, 0, 1, 1, 1, 1, 1, 0),
    (4, "Eden He", 10.309, 1, 1, 1, 1, 1, 1, 0, 0),
    (4, "Terry Huang", 10.309, 1, 1, 1, 1, 1, 1, 0, 0),
    (6, "Shirley Xiong", 9.786, 1, 1, 1, 1, 0, 0, 1, 0),
    (7, "Minhe Liu", 9.135, 0, 0, 1, 1, 1, 0, 0, 1),
    (8, "Katherine Li", 8.837, 1, 0, 1, 1, 1, 1, 0, 0),
    (9, "Alexander Mitev", 8.816, 0, 1, 1, 1, 1, 1, 0, 0),
    (9, "Participant 123 - 1 (Liran Zhou)", 8.816, 0, 1, 1, 1, 1, 1, 0, 0),
    (11, "James Browning", 8.399, 1, 1, 1, 1, 0, 1, 0, 0),
    (11, "Joel Pulikkan", 8.399, 1, 1, 1, 1, 0, 1, 0, 0),
    (13, "Franklin Lee", 7.450, 1, 1, 1, 1, 1, 0, 0, 0),
    (13, "Krivi Partani", 7.450, 1, 1, 1, 1, 1, 0, 0, 0),
    (13, "Karson Jiang", 7.450, 1, 1, 1, 1, 1, 0, 0, 0),
    (13, "Alethea Liu", 7.450, 1, 1, 1, 1, 1, 0, 0, 0),
    (13, "Daniel Wu", 7.450, 1, 1, 1, 1, 1, 0, 0, 0),
    (13, "Harry Gao", 7.450, 1, 1, 1, 1, 1, 0, 0, 0),
    (13, "Dian Yang", 7.450, 1, 1, 1, 1, 1, 0, 0, 0),
    (13, "William Liu", 7.450, 1, 1, 1, 1, 1, 0, 0, 0),
    (13, "Zihan Yu", 7.450, 1, 1, 1, 1, 1, 0, 0, 0),
    (13, "Ryan Zhang", 7.450, 1, 1, 1, 1, 1, 0, 0, 0),
    (13, "Shannon Xu", 7.450, 1, 1, 1, 1, 1, 0, 0, 0),
    (13, "Michael Wang", 7.450, 1, 1, 1, 1, 1, 0, 0, 0),
    (25, "Alex Zhao", 6.906, 0, 1, 1, 1, 0, 1, 0, 0),
    (26, "Kevin Zhao", 6.077, 1, 1, 1, 0, 1, 0, 0, 0),
    (27, "Benjamin Song", 5.978, 1, 0, 1, 1, 1, 0, 0, 0),
    (27, "Derek Peng", 5.978, 1, 0, 1, 1, 1, 0, 0, 0),
    (29, "Eric Dai", 5.957, 0, 1, 1, 1, 1, 0, 0, 0),
    (30, "Terence Wu", 5.540, 1, 1, 1, 1, 0, 0, 0, 0),
    (30, "Kaiqi Xu", 5.540, 1, 1, 1, 1, 0, 0, 0, 0),
    (30, "Xinqi Jessie Wang", 5.540, 1, 1, 1, 1, 0, 0, 0, 0),
    (30, "Vincent Yang", 5.540, 1, 1, 1, 1, 0, 0, 0, 0),
    (30, "Zachary Ji", 5.540, 1, 1, 1, 1, 0, 0, 0, 0),
    (30, "Atticus Masuzawa", 5.540, 1, 1, 1, 1, 0, 0, 0, 0),
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

