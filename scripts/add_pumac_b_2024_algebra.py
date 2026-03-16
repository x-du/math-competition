#!/usr/bin/env python3
"""
One-off: Add PUMaC 2024 Algebra B results from pasted table.
Resolves (name, state) via students.csv; adds new students as needed.
Uses student_id 2214 for Qiao Zhang as requested.
"""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "pumac-b-algebra" / "year=2024"


# Pasted table: rank, name, score, p1..p8
ROWS: list[tuple[int, str, float, int, int, int, int, int, int, int, int]] = [
    (1, "Qiao Zhang", 20.112, 1, 1, 1, 0, 1, 1, 1, 1),
    (2, "Elbert Ho", 12.043, 1, 1, 1, 0, 0, 1, 0, 1),
    (3, "Kevin Chen", 11.638, 1, 1, 1, 0, 0, 1, 1, 0),
    (4, "Hongjian Gary Zheng", 10.539, 1, 1, 1, 0, 1, 1, 0, 0),
    (4, "Eden He", 10.539, 1, 1, 1, 0, 1, 1, 0, 0),
    (4, "Benjamin Sun", 10.539, 1, 1, 1, 0, 1, 1, 0, 0),
    (7, "YEOJUN JAY JUNG", 8.354, 1, 1, 1, 0, 0, 0, 1, 0),
    (8, "Derrick Chen", 7.255, 1, 1, 1, 0, 1, 0, 0, 0),
    (8, "Krivi Partani", 7.255, 1, 1, 1, 0, 1, 0, 0, 0),
    (8, "Charles Wang", 7.255, 1, 1, 1, 0, 1, 0, 0, 0),
    (8, "Eric Zhong", 7.255, 1, 1, 1, 0, 1, 0, 0, 0),
    (12, "Shining Sun", 7.054, 1, 1, 1, 0, 0, 1, 0, 0),
    (12, "Michael Retakh", 7.054, 1, 1, 1, 0, 0, 1, 0, 0),
    (12, "Jason Lu", 7.054, 1, 1, 1, 0, 0, 1, 0, 0),
    (15, "Felix Liu", 5.93, 1, 1, 0, 0, 1, 0, 0, 0),
    (16, "Amy Lin", 5.861, 0, 1, 1, 0, 0, 1, 0, 0),
    (17, "Joel Pulikkan", 5.729, 1, 1, 0, 0, 0, 1, 0, 0),
    (18, "Brian Sun", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Hanyu Ivey Wang", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Bowen Li", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Hyunjae Cho", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Sean Guo", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Kellen Xue", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Franklin Lee", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Tianze Qiu", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Ethan Li", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Yeojin Jean Jung", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Jason Lian", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Cameron Rampell", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Charles Wang", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Aashritha Kolli", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Kaiqi Xu", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Jack Wang", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Eric Chen", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Diyansha Singh", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Madeline Zhu", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Suvid Bordia", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Alice Kim", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Bogdan Kremeznoy", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Christian ZhouZheng", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Alexander Mitev", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Emmett Chen", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Tina Zhao", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Amelie Huang", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Eric Zou", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Karson Jiang", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Alexander Sheng", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Alethea Liu", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Vyom Siriyapu", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Manas Goyal", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Ziyi Kaya Yang", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Yuming Su", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Akshay Gupta", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Advait Joshi", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Erika Kawakami", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Atiksh Akunuri", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Emma Li", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Benjamin Zhao", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Jacqueline Lu", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Dian Yang", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Vincent Yang", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Maggie Li", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
    (18, "Allen Ma", 3.77, 1, 1, 1, 0, 0, 0, 0, 0),
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
            # Use canonical name from students.csv if present; otherwise use given.
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

