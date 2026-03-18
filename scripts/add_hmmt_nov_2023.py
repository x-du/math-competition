#!/usr/bin/env python3
"""
Add HMMT November 2023 Overall Individual to hmmt-nov/year=2023.
Resolves (name, state) via students.csv; adds new students as needed.
Schema: student_id, student_name, year, rank, total_score, general_score, theme_score.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "hmmt-nov" / "year=2023"

TEAM_TO_STATE = {
    "PRISMS Falcons": "California",
    "Ward Melville Math Team D": "New York",
    "All Aces Spade": "",
    "Texas Thunder": "Texas",
    "fun math": "",
    "Lion Valley Alpha": "",
    "Math 4 Fun": "",
    "Texas Typhoon": "Texas",
    "Maryland United": "Maryland",
    "Individuals 2": "",
    "MathTeam007": "",
    "Russian School of Mathematics Team A": "",
    "University of Toronto Schools A": "",
    "Lexington Armadillo": "Massachusetts",
    "Texas Tornado": "Texas",
    "St. Paul's School": "",
    "Maple": "",
    "LS Math Team B": "",
    "Traditional Salad": "",
    "The NH Celestials 2": "New Hampshire",
    "Bayview Team A1": "California",
    "PRISMS Young Falcons": "California",
    "Westchester Area Math Circle": "New York",
    "MN gold": "Minnesota",
    "Texas Academy of Math and Science A": "Texas",
    "Lexington Banana": "Massachusetts",
    "Syo Math A": "",
    "Benet Academy": "Illinois",
    "Choate Math Team": "Connecticut",
    "CCHS Math": "",
}

# (rank, total_score, general_score, theme_score, name, team)
ROWS = [
    (1, 82.89, 51.30, 31.59, "Sicheng Zhou", "PRISMS Falcons"),
    (2, 67.83, 42.65, 25.17, "David Taehee Lee", "PRISMS Falcons"),
    (2, 67.83, 42.65, 25.17, "Michael Lu", "Ward Melville Math Team D"),
    (4, 64.52, 25.43, 39.08, "Vincent Wang", "All Aces Spade"),
    (5, 63.59, 35.08, 28.50, "Richard Wang", "Texas Thunder"),
    (6, 62.57, 30.98, 31.59, "Hanqin Gu", "fun math"),
    (7, 60.58, 39.57, 21.01, "Aaron Le", "Lion Valley Alpha"),
    (8, 60.42, 28.83, 31.59, "Alan Cheng", "Math 4 Fun"),
    (9, 58.35, 30.92, 27.43, "Evan Zhang", "Lion Valley Alpha"),
    (10, 58.28, 25.54, 32.73, "Eric Zang", "Texas Typhoon"),
    (11, 57.45, 28.89, 28.56, "Jeremy Yang", "Maryland United"),
    (12, 57.31, 38.49, 18.82, "Kevin Xuanhao Liu", "Lion Valley Alpha"),
    (13, 56.96, 25.37, 31.59, "Susie Lu", "Individuals 2"),
    (14, 56.21, 31.03, 25.17, "Le Yi Tan", "Texas Typhoon"),
    (15, 56.11, 29.80, 26.32, "LU CHANG", "MathTeam007"),
    (16, 55.98, 37.16, 18.82, "Luca Pieleanu", "Russian School of Mathematics Team A"),
    (17, 55.98, 30.73, 25.24, "Jeffery Zhang", "University of Toronto Schools A"),
    (18, 55.91, 30.73, 25.17, "Jerry Xu", "Lexington Armadillo"),
    (19, 54.84, 29.59, 25.24, "Andrew Shen", "Texas Tornado"),
    (20, 54.77, 29.59, 25.17, "Xingguo Ding", "St. Paul's School"),
    (20, 54.77, 29.59, 25.17, "Yingshan Xiao", "Maple"),
    (22, 53.91, 35.08, 18.82, "William Qian", "Maryland United"),
    (22, 53.91, 35.08, 18.82, "Sophia Hou", "LS Math Team B"),
    (22, 53.91, 35.08, 18.82, "Sophia Zhang", "PRISMS Falcons"),
    (22, 53.91, 35.08, 18.82, "David Zhang", "Traditional Salad"),
    (26, 53.70, 28.53, 25.17, "David Yu", "Maryland United"),
    (27, 52.12, 30.98, 21.14, "Lingfei Sophia Tang", "Math 4 Fun"),
    (28, 52.06, 35.08, 16.98, "Aidan Le", "Lion Valley Alpha"),
    (28, 52.06, 35.08, 16.98, "Xinyi Li", "Texas Thunder"),
    (30, 51.87, 35.08, 16.79, "Brandon Ni", "Lexington Armadillo"),
    (31, 51.49, 25.17, 26.32, "Samuel Tsui", "Lexington Armadillo"),
    (32, 50.73, 25.49, 25.24, "Troy Yang", "BISV Bobcats A"),
    (33, 50.67, 29.59, 21.08, "Nathan Lu", "Maryland United"),
    (34, 50.66, 25.49, 25.17, "Hwiseo", "Lexington Armadillo"),
    (35, 50.49, 25.24, 25.24, "Isaac Jo", "LS Math Team B"),
    (36, 50.15, 35.34, 14.80, "Henry Zheng", "MN gold"),
    (37, 49.86, 31.03, 18.82, "Victor Lin", "Texas Academy of Math and Science A"),
    (38, 49.75, 35.08, 14.66, "Jonathan Liu", "Lexington Banana"),
    (39, 49.62, 30.80, 18.82, "Vedant Patil", "The NH Celestials 2"),
    (40, 49.49, 30.67, 18.82, "Leo Wu", "Bayview Team A1"),
    (40, 49.49, 30.67, 18.82, "Amogh Akella", "Texas Thunder"),
    (42, 49.04, 38.55, 10.50, "Yeyin Zhu", "PRISMS Young Falcons"),
    (43, 48.76, 26.57, 22.19, "Jiya Neelesh Deo Dani", "Texas Tornado"),
    (44, 48.42, 29.59, 18.82, "William Jimenez", "Benet Academy"),
    (44, 48.42, 29.59, 18.82, "Ethan Shi", "Westchester Area Math Circle"),
    (44, 48.42, 29.59, 18.82, "Michael Ren", "Syo Math A"),
    (44, 48.42, 29.59, 18.82, "William Liu", "Lion Valley Alpha"),
    (48, 48.26, 16.67, 31.59, "Peyton Li", "Choate Math Team"),
    (49, 47.72, 37.16, 10.56, "Matthew Qian", "CCHS Math"),
    (50, 47.70, 25.49, 22.21, "Jason Yang", "Lexington Armadillo"),
]

TEAM_TO_STATE["BISV Bobcats A"] = "California"


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
            out_rows.append((row["student_id"], row["student_name"], 2023, rank, total_score, general_score, theme_score))
            continue
        sid = next_id
        next_id += 1
        canon_name = name.strip()
        key_to_row[(canon_name.lower(), state)] = {"student_id": sid, "student_name": canon_name, "state": state}
        new_students.append({
            "student_id": sid, "student_name": canon_name, "state": state,
            "team_ids": "", "alias": "", "gender": ""
        })
        out_rows.append((sid, canon_name, 2023, rank, total_score, general_score, theme_score))

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
