#!/usr/bin/env python3
"""
One-off: Add PUMaC 2025 Algebra B results from pasted table.
Resolves (name, state) via students.csv; adds new students as needed.
"""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "pumac-b-algebra" / "year=2025"


# Pasted table: rank, name, score, p1..p8
ROWS: list[tuple[int, str, float, int, int, int, int, int, int, int, int]] = [
    (1, "Eden He", 12.464, 1, 0, 1, 1, 1, 0, 0, 0),
    (2, "Alexander Sheng", 12.107, 1, 1, 0, 0, 0, 0, 1, 1),
    (3, "Kevin Chen", 12.059, 1, 0, 1, 0, 1, 0, 1, 0),
    (4, "Derrick Chen", 10.475, 1, 1, 1, 1, 0, 0, 0, 0),
    (5, "Max Li", 9.702, 1, 1, 1, 0, 1, 0, 0, 0),
    (5, "Angelica Feng", 9.702, 1, 1, 1, 0, 1, 0, 0, 0),
    (5, "Zili Chang", 9.702, 1, 1, 1, 0, 1, 0, 0, 0),
    (5, "Alex Bae", 9.702, 1, 1, 1, 0, 1, 0, 0, 0),
    (9, "Brayden Choi", 8.847, 1, 0, 1, 1, 0, 0, 0, 0),
    (10, "Hridaan Mehta", 8.458, 0, 1, 1, 0, 0, 1, 0, 0),
    (11, "Aryaveer Shishodia", 8.174, 0, 0, 0, 1, 0, 1, 0, 0),
    (12, "Bret Huang", 7.024, 1, 1, 0, 0, 0, 0, 1, 0),
    (12, "Alexander Choi", 7.024, 1, 1, 0, 0, 0, 0, 1, 0),
    (12, "Benjamin Sun", 7.024, 1, 1, 0, 0, 0, 0, 1, 0),
    (12, "Grace Liang", 7.024, 1, 1, 0, 0, 0, 0, 1, 0),
    (16, "Jay Wang", 6.823, 1, 1, 0, 0, 0, 1, 0, 0),
    (16, "Aadya Kolli", 6.823, 1, 1, 0, 0, 0, 1, 0, 0),
    (18, "Karam Gill", 6.656, 1, 1, 0, 0, 1, 0, 0, 0),
    (18, "Yeojun Jung", 6.656, 1, 1, 0, 0, 1, 0, 0, 0),
    (18, "Jason Lu", 6.656, 1, 1, 0, 0, 1, 0, 0, 0),
    (18, "Likhith Malipati", 6.656, 1, 1, 0, 0, 1, 0, 0, 0),
    (22, "Yejoon Na", 6.494, 1, 0, 0, 0, 0, 0, 0, 1),
    (22, "Eric Zou", 6.494, 1, 0, 0, 0, 0, 0, 0, 1),
    (24, "Derek Peng", 6.085, 1, 1, 1, 0, 0, 0, 0, 0),
    (24, "Cameron Rampell", 6.085, 1, 1, 1, 0, 0, 0, 0, 0),
    (24, "Alan Zhang", 6.085, 1, 1, 1, 0, 0, 0, 0, 0),
    (24, "Jingxuan Wang", 6.085, 1, 1, 1, 0, 0, 0, 0, 0),
    (24, "Madeline Zhu", 6.085, 1, 1, 1, 0, 0, 0, 0, 0),
    (24, "Suvid Bordia", 6.085, 1, 1, 1, 0, 0, 0, 0, 0),
    (24, "Atiksh Akunuri", 6.085, 1, 1, 1, 0, 0, 0, 0, 0),
    (24, "Karson Jiang", 6.085, 1, 1, 1, 0, 0, 0, 0, 0),
    (24, "Sean Gao", 6.085, 1, 1, 1, 0, 0, 0, 0, 0),
    (24, "Charles Chen", 6.085, 1, 1, 1, 0, 0, 0, 0, 0),
    (24, "Minhe Liu", 6.085, 1, 1, 1, 0, 0, 0, 0, 0),
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

