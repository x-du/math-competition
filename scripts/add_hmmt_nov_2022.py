#!/usr/bin/env python3
"""
Add HMMT November 2022 Overall Individual to hmmt-nov/year=2022.
Resolves (name, state) via students.csv; adds new students as needed.
Schema: student_id, student_name, year, rank, total_score, general_score, theme_score.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "hmmt-nov" / "year=2022"

TEAM_TO_STATE = {
    "Sierra Canyon School": "California",
    "Westchester Area Math Circle": "New York",
    "Clarke Middle School Math Team": "",
    "Western PA Math 1": "Pennsylvania",
    "PRISMS Falcons": "California",
    "Montgomery County Team 1 November": "Maryland",
    "duPont Manual High School Red": "Kentucky",
    "Texas Tornado": "Texas",
    "Lexington Gamma": "Massachusetts",
    "Albany Area Math Circle Cardinals": "New York",
    "Individuals 2": "",
    "Populus-1": "",
    "Pingry A": "New Jersey",
    "CRLS Team One": "Massachusetts",
    "Gunn Black": "California",
    "Taipei Math Team": "",
    "Westford Academy": "Massachusetts",
    "The Punching Protractors": "",
    "Wayland High": "Massachusetts",
    "Texas Academy of Math and Science A": "Texas",
    "Russian School of Mathematics Team A": "",
    "PRISMS Young Falcons": "California",
    "The Mathematicals": "",
    "Texas Thunder": "Texas",
    "Lexington Gigachads": "Massachusetts",
    "Knights Gold": "",
    "Lollipop Guild": "",
}

# (rank, total_score, general_score, theme_score, name, team)
ROWS = [
    (1, 92.61, 59.30, 33.31, "Qiao Zhang", "Sierra Canyon School"),
    (2, 73.33, 40.08, 33.24, "Vikram Sarkar", "Westchester Area Math Circle"),
    (3, 71.48, 30.75, 40.73, "Selena Ge", "Clarke Middle School Math Team"),
    (4, 64.06, 35.98, 28.08, "Tanishq Pauskar", "Western PA Math 1"),
    (5, 60.76, 34.80, 25.96, "Vivian Loh", "Western PA Math 1"),
    (6, 60.75, 40.08, 20.66, "Zehan Pan", "PRISMS Falcons"),
    (7, 60.69, 34.80, 25.89, "Yunyi Ling", "Montgomery County Team 1 November"),
    (8, 59.42, 33.59, 25.82, "Ivy Guo", "Montgomery County Team 1 November"),
    (9, 58.45, 29.38, 29.07, "Joseph Vulakh", "duPont Manual High School Red"),
    (10, 56.32, 28.17, 28.15, "Alexander Yunjae Jun", "Texas Tornado"),
    (11, 54.44, 28.55, 25.89, "Boyan", "Lexington Gamma"),
    (12, 53.23, 12.43, 40.80, "James Lian", "Albany Area Math Circle Cardinals"),
    (13, 51.31, 23.02, 28.29, "Tina Li", "Texas Tornado"),
    (14, 50.25, 29.38, 20.87, "Jeffrey Yin", "Populus-1"),
    (15, 49.18, 28.31, 20.87, "Channing Yang", "Texas Tornado"),
    (15, 49.18, 28.31, 20.87, "Leo Xu", "Pingry A"),
    (17, 49.15, 30.61, 18.54, "Jeremy Yang", "Individuals 2"),
    (18, 49.10, 33.59, 15.51, "Sebastian Prasanna", "CRLS Team One"),
    (19, 48.18, 34.80, 13.38, "Samuel Ren", "Gunn Black"),
    (20, 47.05, 33.73, 13.32, "Elbert Ho", "Pingry A"),
    (21, 46.03, 25.22, 20.81, "Kailin Yang", "PRISMS Falcons"),
    (22, 45.92, 20.10, 25.82, "Andrew Tu", "Westchester Area Math Circle"),
    (23, 45.16, 9.52, 35.64, "David Taehee Lee", "PRISMS Falcons"),
    (24, 45.03, 23.19, 21.84, "Alex Lige Dong", "Taipei Math Team"),
    (25, 43.93, 30.61, 13.32, "Jeffrey Xu", "Westford Academy"),
    (26, 43.88, 34.67, 9.21, "Kai", "The Punching Protractors"),
    (27, 43.86, 23.19, 20.67, "Michael Yang", "Lexington Gamma"),
    (28, 43.73, 17.77, 25.96, "Henry Han", "Wayland High"),
    (29, 43.56, 17.60, 25.96, "Alexander Duncan", "Clarke Middle School Math Team"),
    (30, 43.55, 22.89, 20.66, "Hansen Shieh", "Westford Academy"),
    (31, 42.69, 24.15, 18.54, "Jason Zhong", "Westchester Area Math Circle"),
    (32, 41.69, 28.31, 13.38, "Maximus Liu", "Pingry A"),
    (33, 41.63, 28.32, 13.32, "Kylan Z Huang", "Lollipop Guild"),
    (34, 41.62, 23.08, 18.54, "Alexander Bai", "Sierra Canyon School"),
    (35, 40.64, 12.49, 28.15, "Sophia Zhang", "PRISMS Falcons"),
    (36, 40.50, 21.96, 18.54, "Victor Lin", "Texas Academy of Math and Science A"),
    (37, 40.36, 21.82, 18.54, "Sally Yuejie Wang", "Clarke Middle School Math Team"),
    (38, 39.59, 24.01, 15.58, "Rajarshi Mandal", "Russian School of Mathematics Team A"),
    (39, 39.19, 23.54, 15.65, "Peter Wang", "PRISMS Falcons"),
    (40, 37.59, 28.32, 9.27, "Yeyin Zhu", "PRISMS Young Falcons"),
    (41, 37.57, 23.08, 14.49, "Tanush Aggarwal", "Gunn Black"),
    (42, 37.52, 11.63, 25.89, "Jefferson Ji", "Russian School of Mathematics Team A"),
    (43, 37.50, 24.12, 13.38, "Benjamin", "Lexington Gigachads"),
    (44, 37.41, 18.87, 18.54, "Jason Z. Liu", "Western PA Math 1"),
    (45, 37.32, 18.78, 18.54, "Bryan Li", "The Mathematicals"),
    (46, 37.27, 16.54, 20.73, "Derek Xu", "Westchester Area Math Circle"),
    (47, 36.86, 15.99, 20.87, "Tarun Rapaka", "Texas Thunder"),
    (48, 36.31, 17.77, 18.54, "Derek Yimo Gao", "Lexington Gigachads"),
    (49, 36.21, 22.89, 13.32, "Adam Ge", "Clarke Middle School Math Team"),
    (50, 35.40, 27.24, 8.16, "Charles Chen", "Knights Gold"),
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
        rank, total_score, general_score, theme_score, name, team = tup
        state = TEAM_TO_STATE.get(team, "")
        key = (name.strip().lower(), state)
        row = key_to_row.get(key) or key_to_row.get((name.strip().lower(), ""))
        if not row:
            for (k, v) in key_to_row.items():
                if k[0] == name.strip().lower() and (not state or k[1] == state):
                    row = v
                    break
        if row:
            out_rows.append((row["student_id"], row["student_name"], 2022, rank, total_score, general_score, theme_score))
            continue
        sid = next_id
        next_id += 1
        canon_name = name.strip()
        key_to_row[(canon_name.lower(), state)] = {"student_id": sid, "student_name": canon_name, "state": state}
        new_students.append({
            "student_id": sid, "student_name": canon_name, "state": state,
            "team_ids": "", "alias": "", "gender": ""
        })
        out_rows.append((sid, canon_name, 2022, rank, total_score, general_score, theme_score))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "results.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["student_id", "student_name", "year", "rank", "total_score", "general_score", "theme_score"])
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
