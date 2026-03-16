#!/usr/bin/env python3
"""
Add HMMT November 2022 Theme round to hmmt-nov-theme/year=2022.
Schema: student_id, student_name, year, rank, score.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "hmmt-nov-theme" / "year=2022"

TEAM_TO_STATE = {
    "Albany Area Math Circle Cardinals": "New York",
    "Clarke Middle School Math Team": "",
    "PRISMS Falcons": "California",
    "Sierra Canyon School": "California",
    "Westchester Area Math Circle": "New York",
    "duPont Manual High School Red": "Kentucky",
    "Texas Tornado": "Texas",
    "Western PA Math 1": "Pennsylvania",
    "Wayland High": "Massachusetts",
    "Montgomery County Team 1 November": "Maryland",
    "Russian School of Mathematics Team A": "",
    "Lexington Gamma": "Massachusetts",
    "Pingry A": "New Jersey",
    "Texas Thunder": "Texas",
    "Populus-1": "",
    "Taipei Math Team": "",
    "Raritan Valley Math Team - Newton": "New Jersey",
    "Westford Academy": "Massachusetts",
    "The Mathematicals": "",
    "Emma Willard School (Jesters)": "New York",
    "Texas Academy of Math and Science A": "Texas",
    "St. Paul's School": "",
    "Russian School of Mathematics Team B": "",
    "Lexington Gigachads": "Massachusetts",
    "Individuals 2": "",
    "Individuals 1": "",
    "Garnet Valley Math Team 1": "Pennsylvania",
    "Lollipop Guild": "",
    "Mathletes of GBN": "Illinois",
}

# (rank, score, name, team)
ROWS = [
    (1, 40.80, "James Lian", "Albany Area Math Circle Cardinals"),
    (2, 40.73, "Selena Ge", "Clarke Middle School Math Team"),
    (3, 35.64, "David Taehee Lee", "PRISMS Falcons"),
    (4, 33.31, "Qiao Zhang", "Sierra Canyon School"),
    (5, 33.24, "Vikram Sarkar", "Westchester Area Math Circle"),
    (6, 29.07, "Joseph Vulakh", "duPont Manual High School Red"),
    (7, 28.29, "Tina Li", "Texas Tornado"),
    (8, 28.15, "Sophia Zhang", "PRISMS Falcons"),
    (8, 28.15, "Alexander Yunjae Jun", "Texas Tornado"),
    (10, 28.08, "Tanishq Pauskar", "Western PA Math 1"),
    (11, 25.96, "Henry Han", "Wayland High"),
    (11, 25.96, "Alexander Duncan", "Clarke Middle School Math Team"),
    (11, 25.96, "Vivian Loh", "Western PA Math 1"),
    (14, 25.89, "Jefferson Ji", "Russian School of Mathematics Team A"),
    (14, 25.89, "Yunyi Ling", "Montgomery County Team 1 November"),
    (14, 25.89, "Boyan", "Lexington Gamma"),
    (17, 25.82, "Andrew Tu", "Westchester Area Math Circle"),
    (17, 25.82, "Ivy Guo", "Montgomery County Team 1 November"),
    (19, 21.84, "Alex Lige Dong", "Taipei Math Team"),
    (20, 20.87, "Channing Yang", "Texas Tornado"),
    (20, 20.87, "Tarun Rapaka", "Texas Thunder"),
    (20, 20.87, "Leo Xu", "Pingry A"),
    (20, 20.87, "Jeffrey Yin", "Populus-1"),
    (24, 20.81, "Kailin Yang", "PRISMS Falcons"),
    (24, 20.81, "Abdd Sharma", "Raritan Valley Math Team - Newton"),
    (26, 20.73, "Derek Xu", "Westchester Area Math Circle"),
    (26, 20.73, "Anton Levonian", "Raritan Valley Math Team - Newton"),
    (28, 20.67, "Michael Yang", "Lexington Gamma"),
    (29, 20.66, "Zehan Pan", "PRISMS Falcons"),
    (29, 20.66, "Hansen Shieh", "Westford Academy"),
    (31, 20.60, "Benjamin Walsh", "Mathletes of GBN"),
    (32, 18.54, "Bryan Li", "The Mathematicals"),
    (32, 18.54, "Sitong Yi", "Emma Willard School (Jesters)"),
    (32, 18.54, "Sally Yuejie Wang", "Clarke Middle School Math Team"),
    (32, 18.54, "Victor Lin", "Texas Academy of Math and Science A"),
    (32, 18.54, "Jason Zhong", "Westchester Area Math Circle"),
    (32, 18.54, "Alexander Bai", "Sierra Canyon School"),
    (32, 18.54, "Andrew Shen", "Texas Tornado"),
    (32, 18.54, "Jason Z. Liu", "Western PA Math 1"),
    (32, 18.54, "Xingguo Ding", "St. Paul's School"),
    (32, 18.54, "Arsenii Zharkov", "Russian School of Mathematics Team B"),
    (32, 18.54, "Derek Yimo Gao", "Lexington Gigachads"),
    (32, 18.54, "Jeremy Yang", "Individuals 2"),
    (44, 16.69, "Aren", "Individuals 1"),
    (45, 16.50, "Benjamin Wu", "Garnet Valley Math Team 1"),
    (46, 15.65, "Peter Wang", "PRISMS Falcons"),
    (46, 15.65, "Harry Shen", "Albany Area Math Circle Cardinals"),
    (48, 15.58, "Justin Lai", "Texas Tornado"),
    (48, 15.58, "Rajarshi Mandal", "Russian School of Mathematics Team A"),
    (48, 15.58, "Kyle Wu", "Lollipop Guild"),
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
