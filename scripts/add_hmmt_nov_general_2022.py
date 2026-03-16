#!/usr/bin/env python3
"""
Add HMMT November 2022 General round to hmmt-nov-general/year=2022.
Schema: student_id, student_name, year, rank, score.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "hmmt-nov-general" / "year=2022"

TEAM_TO_STATE = {
    "Sierra Canyon School": "California",
    "PRISMS Falcons": "California",
    "Westchester Area Math Circle": "New York",
    "Western PA Math 1": "Pennsylvania",
    "Gunn Black": "California",
    "Montgomery County Team 1 November": "Maryland",
    "The Punching Protractors": "",
    "Pingry A": "New Jersey",
    "CRLS Team One": "Massachusetts",
    "Clarke Middle School Math Team": "",
    "Westford Academy": "Massachusetts",
    "Individuals 2": "",
    "duPont Manual High School Red": "Kentucky",
    "Populus-1": "",
    "Lexington Gamma": "Massachusetts",
    "PRISMS Young Falcons": "California",
    "Lollipop Guild": "",
    "Texas Tornado": "Texas",
    "Knights Gold": "",
    "Taipei Math Team": "",
    "LS Math Team": "",
    "Russian School of Mathematics Team A": "",
    "Texas Academy of Math and Science A": "Texas",
    "Bonnie Branch Math Circle-Foxfort": "Maryland",
    "Albany Area Math Circle Cardinals": "New York",
    "Mathletes of GBN": "Illinois",
    "Belmont i": "Massachusetts",
    "Western PA Math 2": "Pennsylvania",
}

# (rank, score, name, team)
ROWS = [
    (1, 59.30, "Qiao Zhang", "Sierra Canyon School"),
    (2, 40.08, "Zehan Pan", "PRISMS Falcons"),
    (2, 40.08, "Vikram Sarkar", "Westchester Area Math Circle"),
    (4, 35.98, "Tanishq Pauskar", "Western PA Math 1"),
    (5, 34.80, "Samuel Ren", "Gunn Black"),
    (5, 34.80, "Vivian Loh", "Western PA Math 1"),
    (5, 34.80, "Yunyi Ling", "Montgomery County Team 1 November"),
    (8, 34.67, "Kai", "The Punching Protractors"),
    (9, 33.73, "Elbert Ho", "Pingry A"),
    (10, 33.59, "Sebastian Prasanna", "CRLS Team One"),
    (10, 33.59, "Ivy Guo", "Montgomery County Team 1 November"),
    (12, 30.75, "Selena Ge", "Clarke Middle School Math Team"),
    (13, 30.61, "Jeffrey Xu", "Westford Academy"),
    (13, 30.61, "Jeremy Yang", "Individuals 2"),
    (15, 29.38, "Joseph Vulakh", "duPont Manual High School Red"),
    (15, 29.38, "Jeffrey Yin", "Populus-1"),
    (17, 28.55, "Boyan", "Lexington Gamma"),
    (18, 28.32, "Yeyin Zhu", "PRISMS Young Falcons"),
    (18, 28.32, "Kylan Z Huang", "Lollipop Guild"),
    (20, 28.31, "Andrew Li", "Texas Tornado"),
    (20, 28.31, "Channing Yang", "Texas Tornado"),
    (20, 28.31, "Maximus Liu", "Pingry A"),
    (20, 28.31, "Leo Xu", "Pingry A"),
    (24, 28.17, "Alexander Yunjae Jun", "Texas Tornado"),
    (25, 27.71, "Xuancheng Li", "PRISMS Young Falcons"),
    (26, 27.24, "Charles Chen", "Knights Gold"),
    (27, 25.22, "Kailin Yang", "PRISMS Falcons"),
    (28, 24.26, "Heyang Ni", "PRISMS Falcons"),
    (29, 24.20, "Isaac Jo", "LS Math Team"),
    (30, 24.15, "Jason Zhong", "Westchester Area Math Circle"),
    (31, 24.12, "Benjamin", "Lexington Gigachads"),
    (32, 24.09, "David Li", "Gunn Black"),
    (33, 24.01, "Rajarshi Mandal", "Russian School of Mathematics Team A"),
    (34, 23.54, "Peter Wang", "PRISMS Falcons"),
    (35, 23.19, "Alex Lige Dong", "Taipei Math Team"),
    (35, 23.19, "Michael Yang", "Lexington Gamma"),
    (37, 23.08, "Tanush Aggarwal", "Gunn Black"),
    (37, 23.08, "Alexander Bai", "Sierra Canyon School"),
    (39, 23.03, "Om Mahesh", "Gunn Black"),
    (40, 23.02, "Tina Li", "Texas Tornado"),
    (41, 22.89, "Adam Ge", "Clarke Middle School Math Team"),
    (41, 22.89, "Hansen Shieh", "Westford Academy"),
    (43, 21.96, "Victor Lin", "Texas Academy of Math and Science A"),
    (44, 21.82, "Tony Zhang", "Bonnie Branch Math Circle-Foxfort"),
    (44, 21.82, "Justin Mo", "Albany Area Math Circle Cardinals"),
    (44, 21.82, "Sally Yuejie Wang", "Clarke Middle School Math Team"),
    (44, 21.82, "Lillian Wang", "Texas Academy of Math and Science A"),
    (44, 21.82, "Benjamin Witzel", "Mathletes of GBN"),
    (44, 21.82, "Michael Voigt", "Belmont i"),
    (44, 21.82, "Alex Todd", "Western PA Math 2"),
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

    for (rank, score, name, team) in ROWS:
        state = TEAM_TO_STATE.get(team, "").strip()
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
