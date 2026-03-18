#!/usr/bin/env python3
"""
Add HMMT November 2024 Overall Individual to hmmt-nov/year=2024.
Resolves (name, state) via students.csv; adds new students as needed.
Schema: student_id, student_name, year, rank, total_score, general_score, theme_score.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "hmmt-nov" / "year=2024"

TEAM_TO_STATE = {
    "Shanghai High School Stallions": "",
    "Bayview Team A1": "California",
    "Individuals 5": "",
    "University of Toronto Schools A": "",
    "Beijing Forbidden City": "",
    "PRISMS Young Falcons": "California",
    "The NH Celestials 2": "New Hampshire",
    "Gunn Black": "California",
    "Math 4 Fun": "",
    "Maple": "",
    "St. Paul's School": "",
    "Big L Club": "",
    "Phillips Academy A1": "Massachusetts",
    "Individuals 2": "",
    "Sugar Club": "",
    "The Pingry School": "New Jersey",
    "SH Team 001": "",
    "All Aces Spade": "",
    "CCHS A Team": "",
    "Bellaire A": "Texas",
    "Lexington Gamma": "Massachusetts",
    "Maryland United": "Maryland",
    "Doozy Math Team B": "",
    "Paly Trolls": "California",
    "Aftermath": "",
    "Lexington Delta": "Massachusetts",
    "Math School A": "",
    "CA Chameleons": "California",
    "Tennessee Math Coalition Blue": "Tennessee",
    "Collegiate School": "Virginia",
    "Albany Area Math Circle Cardinals": "New York",
    "Ward Melville Math Team E": "New York",
    "OSS Mu Alpha Theta": "",
    "The Real Prizes Were The Friends We Made Along The Way": "",
    "AlphaStar Academy THUNDER": "California",
    "Individuals 4": "",
    "Texas Thunder": "Texas",
}

# (rank, total_score, general_score, theme_score, name, team)
ROWS = [
    (1, 72.32, 32.08, 40.24, "GONG YICHEN", "Shanghai High School Stallions"),
    (2, 71.29, 34.21, 37.08, "Leo Wu", "Bayview Team A1"),
    (3, 68.75, 36.08, 32.67, "Joanna Wu", "Individuals 5"),
    (4, 66.82, 29.73, 37.08, "Perry Dai", "University of Toronto Schools A"),
    (5, 62.62, 30.81, 31.81, "Bowen Deng", "Beijing Forbidden City"),
    (6, 62.62, 36.30, 26.32, "Peter Wang", "PRISMS Young Falcons"),
    (7, 62.60, 36.08, 26.51, "Pratham Mukewar", "The NH Celestials 2"),
    (8, 62.48, 36.30, 26.17, "Dongyoon Shin", "Gunn Black"),
    (9, 61.40, 37.16, 24.24, "Eric P Zhu", "Math 4 Fun"),
    (10, 61.19, 30.59, 30.59, "Anji Wang", "Maple"),
    (11, 56.36, 29.73, 26.63, "Xingguo Ding", "St. Paul's School"),
    (12, 54.98, 24.24, 30.73, "Advait Joshi", "Big L Club"),
    (13, 54.91, 30.67, 24.24, "Gavin Guojun Zhao", "Shanghai High School Stallions"),
    (14, 54.17, 24.24, 29.93, "Siravit Hengsuvanich", "Phillips Academy A1"),
    (15, 53.55, 20.89, 32.67, "Aadish Jain", "Individuals 2"),
    (16, 53.08, 26.65, 26.43, "chen zizhuang", "Shanghai High School Stallions"),
    (17, 53.08, 26.59, 26.49, PengYu Wu, "Sugar Club"),
    (18, 53.02, 32.94, 20.08, "Elbert Ho", "The Pingry School"),
    (19, 52.70, 30.67, 22.03, "Weihong Sun", "SH Team 001"),
    (19, 52.70, 30.67, 22.03, "Li Tianyi", "SH Team 001"),
    (21, 52.48, 30.59, 21.89, "Hyun-Jin Kim", "All Aces Spade"),
    (22, 51.96, 24.32, 27.65, "Matthew Qian", "CCHS A Team"),
    (23, 51.91, 20.09, 31.81, "Jerry Zhang", "Bellaire A"),
    (24, 51.66, 25.17, 26.49, "Samuel Tsui", "Lexington Gamma"),
    (25, 51.54, 20.95, 30.59, "Yunong Wu", "Westchester Area Math Circle"),
    (26, 50.93, 29.73, 21.19, Ziyang Wu, "Sugar Club"),
    (27, 50.75, 20.15, 30.59, "Daniel Yu", "Maryland United"),
    (28, 50.73, 30.59, 20.14, "Annabel Rong", "Doozy Math Team B"),
    (29, 50.67, 20.08, 30.59, "Michael Sun", "Maple"),
    (30, 50.62, 20.03, 30.59, "Paige Zhu", "Phillips Academy A1"),
    (31, 50.61, 30.59, 20.02, "Krittika Chandra", "Paly Trolls"),
    (32, 50.49, 30.67, 19.82, "Sohan Javeri", "Aftermath"),
    (32, 50.49, 30.67, 19.82, "Charles Yuanrui Zheng", "Lexington Delta"),
    (34, 49.63, 25.39, 24.24, "Kaylyn Jinglin Zhang", "University of Toronto Schools A"),
    (35, 49.56, 18.82, 30.73, "Anand Swaroop", "Math School A"),
    (36, 49.42, 25.17, 24.24, "Jonathan Liu", "Lexington Gamma"),
    (37, 49.04, 22.47, 26.57, "Sirawit Pipittanaban", "CA Chameleons"),
    (38, 49.03, 29.73, 19.30, "Gong Cheng", "Sugar Club"),
    (39, 48.56, 24.32, 24.24, "Justin Guo", "Tennessee Math Coalition Blue"),
    (40, 48.49, 24.24, 24.24, "Christopher Lu", "Collegiate School"),
    (41, 47.62, 23.38, 24.24, "Jason Lian", "Albany Area Math Circle Cardinals"),
    (42, 47.57, 30.67, 16.91, "Michael Retakh", "Ward Melville Math Team E"),
    (43, 47.37, 24.24, 23.12, "Brayden Choi", "OSS Mu Alpha Theta"),
    (44, 46.53, 30.81, 15.72, "Soham Samanta", "Math School A"),
    (44, 46.53, 18.82, 27.71, "Raymond Ge", "Math 4 Fun"),
    (46, 46.52, 20.09, 26.43, "Eric Huang", "The Real Prizes Were The Friends We Made Along The Way"),
    (47, 46.51, 29.73, 16.77, "Lingfei Sophia Tang", "Math 4 Fun"),
    (48, 46.49, 26.66, 19.82, "Dylan Wang", "AlphaStar Academy THUNDER"),
    (49, 46.47, 26.65, 19.82, "Susie Lu", "Individuals 4"),
    (50, 46.47, 20.02, 26.45, "Colin Wei", "Texas Thunder"),
]

# Westchester Area Math Circle - add to TEAM_TO_STATE
TEAM_TO_STATE["Westchester Area Math Circle"] = "New York"


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
            out_rows.append((row["student_id"], row["student_name"], 2024, rank, total_score, general_score, theme_score))
            continue
        sid = next_id
        next_id += 1
        canon_name = name.strip()
        key_to_row[(canon_name.lower(), state)] = {"student_id": sid, "student_name": canon_name, "state": state}
        new_students.append({
            "student_id": sid, "student_name": canon_name, "state": state,
            "team_ids": "", "alias": "", "gender": ""
        })
        out_rows.append((sid, canon_name, 2024, rank, total_score, general_score, theme_score))

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
