#!/usr/bin/env python3
"""
Add PUMAC Geometry 2023 (Division A) from pasted table.
Resolves (name, state) via students.csv; adds new students as needed.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "pumac-geometry" / "year=2023"

TEAM_TO_STATE = {
    "Lehigh Valley Fire": "Pennsylvania", "TJ A": "Virginia", "TJ B": "Virginia", "BCA 1": "New Jersey",
    "Texas Ramanujan": "Texas", "Florida Alligators": "Florida", "CT Cyborgs": "Connecticut",
    "Knights A": "California", "Athemath Owls": "California", "Phillips Academy": "Massachusetts",
    "Lexington Alpha": "Massachusetts", "Lexington Beta": "Massachusetts",
    "GWe UAre Not NAffiliated": "Georgia", "BBMC-math Delta": "Maryland", "Tin Man": "California",
    "PEA Red Lion": "New Hampshire", "PRISMS Falcons": "California", "Scarecrow": "California",
    "Central Maryland United": "Maryland", "Lion": "California",
}

# Pasted table: rank, name, team, score, p1..p8
ROWS = [
    (1, "Aaron Hu", "Florida Alligators", 15.426, 1, 0, 1, 1, 1, 1, 1, 0),
    (1, "Channing Yang", "Texas Ramanujan", 15.426, 1, 0, 1, 1, 1, 1, 1, 0),
    (3, "Aprameya Tripathy", "Knights A", 14.685, 1, 0, 1, 1, 0, 1, 0, 1),
    (4, "Vivian Loh", "Athemath Owls", 12.795, 0, 1, 1, 1, 1, 1, 0, 0),
    (5, "Isaac Chen", "Lehigh Valley Fire", 11.584, 0, 0, 0, 1, 1, 1, 1, 0),
    (6, "Benny Wang", "PEA Red Lion", 11.130, 1, 0, 1, 1, 1, 1, 0, 0),
    (7, "Oron Wang", "PEA Red Lion", 11.056, 1, 1, 1, 1, 1, 0, 0, 0),
    (7, "David Wei", "TJ A", 11.056, 1, 1, 1, 1, 1, 0, 0, 0),
    (9, "Jordan Lefkowitz", "CT Cyborgs", 9.011, 1, 1, 1, 0, 1, 0, 0, 0),
    (10, "Sitta Tantikul", "Individuals Team 161", 8.667, 1, 0, 0, 1, 1, 1, 0, 0),
    (10, "Albert Cao", "BBMC-math Delta", 8.667, 1, 0, 0, 1, 1, 1, 0, 0),
    (12, "Aditya Pahuja", "Tin Man", 8.592, 1, 1, 0, 1, 1, 0, 0, 0),
    (12, "Heyang Felicity Ni", "PRISMS Falcons", 8.592, 1, 1, 0, 1, 1, 0, 0, 0),
    (14, "Ian Buchanan", "Scarecrow", 8.013, 1, 0, 1, 1, 1, 0, 0, 0),
    (15, "Michelle Wang", "TJ A", 7.718, 1, 0, 0, 1, 0, 0, 1, 0),
    (16, "Sylvia Lee", "Lexington Beta", 7.551, 0, 1, 1, 1, 0, 0, 0, 0),
    (17, "Raymond Zhao", "Texas Ramanujan", 6.884, 1, 1, 1, 0, 0, 0, 0, 0),
    (17, "Nathan Lu", "Central Maryland United", 6.884, 1, 1, 1, 0, 0, 0, 0, 0),
    (19, "Derek Zhao", "Lexington Alpha", 6.635, 0, 0, 1, 1, 1, 0, 0, 0),
    (19, "Kailin Kevin Yang", "PRISMS Falcons", 6.635, 0, 0, 1, 1, 1, 0, 0, 0),
    (21, "Grant Blitz", "PEA Red Lion", 6.622, 1, 0, 0, 0, 1, 1, 0, 0),
    (21, "Jason Mao", "Lehigh Valley Fire", 6.622, 1, 0, 0, 0, 1, 1, 0, 0),
    (23, "Yusuf Sheikh", "Florida Alligators", 6.540, 1, 0, 0, 1, 0, 1, 0, 0),
    (23, "Steve Zhang", "GWe UAre Not NAffiliated", 6.540, 1, 0, 0, 1, 0, 1, 0, 0),
    (25, "Zander Li", "Individuals Team 161", 6.466, 1, 1, 0, 1, 0, 0, 0, 0),
    (25, "Sophia Jin", "Lion", 6.466, 1, 1, 0, 1, 0, 0, 0, 0),
    (27, "Jaemin Kim", "Tin Man", 5.968, 1, 0, 1, 0, 1, 0, 0, 0),
    (27, "Sophia Zhang", "PRISMS Falcons", 5.968, 1, 0, 1, 0, 1, 0, 0, 0),
    (29, "Olivia Wu", "TJ B", 5.886, 1, 0, 1, 1, 0, 0, 0, 0),
    (29, "Katherine Liu", "Texas Ramanujan", 5.886, 1, 0, 1, 1, 0, 0, 0, 0),
    (29, "Andy Xu", "Phillips Academy", 5.886, 1, 0, 1, 1, 0, 0, 0, 0),
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
