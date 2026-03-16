#!/usr/bin/env python3
"""
Add HMMT February 2022 Geometry round to hmmt-feb-geometry/year=2022.
Resolves (name, state) via students.csv; adds new students as needed.
Schema: student_id, student_name, year, rank, score.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "hmmt-feb-geometry" / "year=2022"

TEAM_TO_STATE = {
    "Texas Momentum A": "Texas",
    "AlphaStar Academy AIR": "California",
    "Florida Alligators": "Florida",
    "Orange County Math Circle BrawlphaStars": "California",
    "Lehigh Valley Fire": "",
    "Motown All Stars": "Michigan",
    "Pentagon Hexagon Oregon A": "Oregon",
    "San Diego A1": "California",
    "TJ-A": "Virginia",
    "Western Mass ARML Stars": "Massachusetts",
    "Lexington Alpha": "Massachusetts",
    "MN All-State Math Team 1 - Gold": "Minnesota",
    "Washington Gold 1": "Washington",
    "Tin Man": "New York",
    "EddieSolo": "",
    "AlphaStar Academy FIRE": "California",
    "OS Betelgeuse": "",
    "Bergen County Academies Team 1": "New Jersey",
    "Individuals 3": "",
    "Lehigh Valley Ice": "",
    "NC School of Science & Math - Team alpha": "North Carolina",
    "San Diego A2": "California",
    "Harker Omega": "California",
    "Spice": "California",
    "Pleasanton A": "California",
    "No Coast Best Coast": "Illinois",
    "Burgas A": "",
    "Populus-3": "",
    "Scarecrow": "California",
    "BISV Bobcats A": "California",
    "Raritan Valley Math Team - Euler": "New Jersey",
}

# (rank, score, name, team) from GEOMETRY ROUND
ROWS = [
    (1, 53.81, "Luke Robitaille", "Texas Momentum A"),
    (2, 43.08, "Dylan Yu", "Texas Momentum A"),
    (3, 29.31, "Eric Shen", "AlphaStar Academy AIR"),
    (3, 29.31, "Karthik Vedula", "Florida Alligators"),
    (5, 28.24, "Andrew Gu", "Orange County Math Circle BrawlphaStars"),
    (6, 27.17, "Christopher Qiu", "Lehigh Valley Fire"),
    (6, 27.17, "Henry Jiang", "Motown All Stars"),
    (6, 27.17, "Suyash Pandit", "Pentagon Hexagon Oregon A"),
    (6, 27.17, "Derek Liu", "San Diego A1"),
    (6, 27.17, "Aaron Guo", "Texas Momentum A"),
    (6, 27.17, "Isabella Zhu", "TJ-A"),
    (6, 27.17, "Andrew Lee", "Western Mass ARML Stars"),
    (13, 25.21, "Kevin Zhao", "Lexington Alpha"),
    (14, 24.08, "Kenneth Ang Chen", "MN All-State Math Team 1 - Gold"),
    (15, 23.01, "Lucas Tang", "Washington Gold 1"),
    (15, 23.01, "Joseph Othman", "Tin Man"),
    (15, 23.01, "Eddie Wei", "EddieSolo"),
    (18, 21.95, "Jason Mao", "Lehigh Valley Fire"),
    (18, 21.95, "Ben Li", "NC School of Science & Math - Team alpha"),
    (18, 21.95, "Angela Liu", "AlphaStar Academy FIRE"),
    (18, 21.95, "Elliott Liu", "San Diego A1"),
    (18, 21.95, "Justin Zhang", "San Diego A2"),
    (18, 21.95, "Xuezhi Wang", "OS Betelgeuse"),
    (18, 21.95, "Jessica Wan", "Florida Alligators"),
    (18, 21.95, "Alex Li", "Florida Alligators"),
    (18, 21.95, "Aaron Hu", "Florida Alligators"),
    (18, 21.95, "Boris Tsvetanov Gachevski", "Burgas A"),
    (18, 21.95, "Saanvi Thummalapally", "Individuals 3"),
    (29, 21.89, "Alexander Wang", "Lehigh Valley Ice"),
    (29, 21.89, "Johan Ko", "AlphaStar Academy AIR"),
    (29, 21.89, "Karthik Seetharaman", "Western Mass ARML Stars"),
    (32, 20.82, "Skyler Le", "Lehigh Valley Fire"),
    (32, 20.82, "Olivia Xu", "Harker Omega"),
    (32, 20.82, "Razzi H. Masroor", "Motown All Stars"),
    (32, 20.82, "Justin Lee", "Spice"),
    (32, 20.82, "David Jiahui Zhang", "AlphaStar Academy FIRE"),
    (32, 20.82, "Jerry Liang", "Tin Man"),
    (32, 20.82, "Vivian Loh", "EddieSolo"),
    (32, 20.82, "Nicholas Song", "San Diego A1"),
    (32, 20.82, "Justin Li", "San Diego A2"),
    (32, 20.82, "Akash Madiraju", "Pleasanton A"),
    (32, 20.82, "Rowechen Zhong", "Texas Momentum A"),
    (32, 20.82, "Wilbert Chu", "No Coast Best Coast"),
    (44, 19.93, "Chengcheng Qian", "Populus-3"),
    (44, 19.93, "Bryan Zhang", "Scarecrow"),
    (46, 17.79, "Adam Tang", "BISV Bobcats A"),
    (46, 17.79, "Brandon Lou", "Tin Man"),
    (46, 17.79, "Matthew Ji Chen", "MN All-State Math Team 1 - Gold"),
    (46, 17.79, "Sargam Mondal", "Raritan Valley Math Team - Euler"),
    (50, 17.73, "Daeho Jacob Lee", "San Diego A2"),
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
    # Alias: Daeho Jacob Lee -> Daeho Lee
    for (k, v) in list(key_to_row.items()):
        if k[0] == "daeho lee":
            key_to_row[("daeho jacob lee", k[1])] = v
            key_to_row[("daeho jacob lee", "")] = v
            break
    # Alias: Bryan Zhang -> Brian Zhang (common typo)
    for (k, v) in list(key_to_row.items()):
        if k[0] == "brian zhang":
            key_to_row[("bryan zhang", k[1])] = v
            key_to_row[("bryan zhang", "")] = v
            break
    return key_to_row, next_id


def main():
    key_to_row, next_id = load_students()
    new_students = []
    out_rows = []

    for (rank, score, name, team) in ROWS:
        state = TEAM_TO_STATE.get(team, "")
        key = (name.strip().lower(), state)
        row = key_to_row.get(key) or key_to_row.get((name.strip().lower(), ""))
        if not row:
            for (k, v) in key_to_row.items():
                if k[0] == name.strip().lower() and (not state or k[1] == state):
                    row = v
                    break
        if row:
            out_rows.append((row["student_id"], row["student_name"], 2022, rank, score))
            continue
        sid = next_id
        next_id += 1
        canon_name = name.strip()
        key_to_row[(canon_name.lower(), state)] = {"student_id": sid, "student_name": canon_name, "state": state}
        new_students.append({
            "student_id": sid, "student_name": canon_name, "state": state,
            "team_ids": "", "alias": "", "gender": ""
        })
        out_rows.append((sid, canon_name, 2022, rank, score))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "results.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["student_id", "student_name", "year", "rank", "score"])
        for r in out_rows:
            w.writerow(r)
    print(f"Wrote {out_path} ({len(out_rows)} rows)")

    if new_students:
        with open(STUDENTS_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            for r in new_students:
                w.writerow([r["student_id"], r["student_name"], r["state"], r["team_ids"], r["alias"], r["gender"]])
        print(f"Appended {len(new_students)} new students: {[s['student_name'] for s in new_students]}")
    else:
        print("No new students to add.")

    print("Run: python scripts/build_search_data.py")


if __name__ == "__main__":
    main()
