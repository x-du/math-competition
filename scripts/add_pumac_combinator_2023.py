#!/usr/bin/env python3
"""
Add PUMAC Combinatorics 2023 (Division A) from pasted table.
Resolves (name, state) via students.csv; adds new students as needed.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "pumac-combinator" / "year=2023"

TEAM_TO_STATE = {
    "Lehigh Valley Fire": "Pennsylvania", "TJ A": "Virginia", "TJ B": "Virginia", "BCA 1": "New Jersey",
    "Texas Ramanujan": "Texas", "Texas Hardy": "Texas", "Florida Alligators": "Florida",
    "Florida Beaches": "Florida", "CT Cyborgs": "Connecticut", "MoCoSwaggaSquad": "Maryland",
    "Tin Man": "California", "Phillips Academy": "Massachusetts", "Lexington Alpha": "Massachusetts",
    "GWe UAre Not NAffiliated": "Georgia", "BBMC-math Delta": "Maryland", "PRISMS Falcons": "California",
    "404 Error": "Virginia", "Athemath Owls": "California", "PEA Red Lion": "New Hampshire",
    "Pirates A": "California", "Lion": "California", "Poolesville Math Team A": "Maryland",
}

# Pasted table: rank, name, team, score, p1..p8
ROWS = [
    (1, "Marvin Mao", "BCA 1", 10.883, 1, 1, 1, 1, 1, 0, 0, 0),
    (1, "Oron Wang", "PEA Red Lion", 10.883, 1, 1, 1, 1, 1, 0, 0, 0),
    (1, "Andrew Xing", "Florida Alligators", 10.883, 1, 1, 1, 1, 1, 0, 0, 0),
    (4, "Jiahe Liu", "404 Error", 9.115, 1, 1, 0, 1, 1, 0, 0, 0),
    (5, "Allen Wang", "Lehigh Valley Fire", 8.581, 0, 1, 1, 1, 1, 0, 0, 0),
    (6, "Zani Xu", "TJ A", 7.694, 1, 1, 1, 0, 1, 0, 0, 0),
    (6, "Andrew Zhao", "Lexington Alpha", 7.694, 1, 1, 1, 0, 1, 0, 0, 0),
    (6, "Harry Kim", "Phillips Academy", 7.694, 1, 1, 1, 0, 1, 0, 0, 0),
    (6, "Vishal Nandakumar", "TJ B", 7.694, 1, 1, 1, 0, 1, 0, 0, 0),
    (6, "Roger Fan", "GWe UAre Not NAffiliated", 7.694, 1, 1, 1, 0, 1, 0, 0, 0),
    (6, "Steve Zhang", "GWe UAre Not NAffiliated", 7.694, 1, 1, 1, 0, 1, 0, 0, 0),
    (12, "Ashley Zhu", "Tin Man", 7.097, 0, 0, 1, 1, 1, 0, 0, 0),
    (13, "Raymond Zhao", "Texas Ramanujan", 6.976, 1, 1, 0, 1, 0, 0, 0, 0),
    (14, "Andrew Li", "Tin Man", 6.813, 0, 1, 0, 1, 1, 0, 0, 0),
    (14, "Eric Wang", "Phillips Academy", 6.813, 0, 1, 0, 1, 1, 0, 0, 0),
    (16, "Xuancheng Benjamin Li", "PRISMS Falcons", 6.442, 0, 1, 1, 1, 0, 0, 0, 0),
    (16, "Vivian Loh", "Athemath Owls", 6.442, 0, 1, 1, 1, 0, 0, 0, 0),
    (18, "Andrew Lin", "Lehigh Valley Fire", 6.209, 1, 0, 1, 0, 1, 0, 0, 0),
    (19, "Nathan Liu", "Texas Hardy", 5.926, 1, 1, 0, 0, 1, 0, 0, 0),
    (19, "Amogh Akella", "Texas Hardy", 5.926, 1, 1, 0, 0, 1, 0, 0, 0),
    (19, "Alexander Jun", "Texas Ramanujan", 5.926, 1, 1, 0, 0, 1, 0, 0, 0),
    (19, "Katherine Liu", "Texas Ramanujan", 5.926, 1, 1, 0, 0, 1, 0, 0, 0),
    (19, "Kelin Zhu", "MoCoSwaggaSquad", 5.926, 1, 1, 0, 0, 1, 0, 0, 0),
    (19, "Maitian Sha", "Pirates A", 5.926, 1, 1, 0, 0, 1, 0, 0, 0),
    (25, "Alicia Li", "Lion", 5.554, 1, 1, 1, 0, 0, 0, 0, 0),
    (25, "Sumedh Vangara", "Poolesville Math Team A", 5.554, 1, 1, 1, 0, 0, 0, 0, 0),
    (25, "David Ruan", "Poolesville Math Team A", 5.554, 1, 1, 1, 0, 0, 0, 0, 0),
    (25, "Aaron Xiong", "Florida Beaches", 5.554, 1, 1, 1, 0, 0, 0, 0, 0),
    (25, "Yeyin Eva Zhu", "PRISMS Falcons", 5.554, 1, 1, 1, 0, 0, 0, 0, 0),
    (25, "Jeffrey Yin", "BBMC-math Delta", 5.554, 1, 1, 1, 0, 0, 0, 0, 0),
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
