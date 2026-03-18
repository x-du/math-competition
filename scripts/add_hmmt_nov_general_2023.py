#!/usr/bin/env python3
"""
Add HMMT November 2023 General round to hmmt-nov-general/year=2023.
Schema: student_id, student_name, year, rank, score.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "hmmt-nov-general" / "year=2023"

TEAM_TO_STATE = {
    "PRISMS Falcons": "California",
    "Ward Melville Math Team D": "New York",
    "Lion Valley Alpha": "",
    "PRISMS Young Falcons": "California",
    "CCHS Math": "",
    "Russian School of Mathematics Team A": "",
    "MN gold": "Minnesota",
    "Maryland United": "Maryland",
    "LS Math Team B": "",
    "Clarke Middle School Math Team": "",
    "Traditional Salad": "",
    "Texas Thunder": "Texas",
    "Lexington Armadillo": "Massachusetts",
    "Lexington Banana": "Massachusetts",
    "Texas Academy of Math and Science A": "Texas",
    "Texas Typhoon": "Texas",
    "Math 4 Fun": "",
    "fun math": "",
    "Yu's Alligator": "Florida",
    "Maple": "",
    "The NH Celestials 2": "New Hampshire",
    "University of Toronto Schools A": "",
    "Montgomery County Team 1 November": "Maryland",
    "Bayview Team A1": "California",
    "MathTeam007": "",
    "Benet Academy": "Illinois",
    "St. Paul's School": "",
    "Westchester Area Math Circle": "New York",
    "Texas Tornado": "Texas",
    "Syo Math A": "",
    "Individuals 4": "",
    "CRLS Team One": "Massachusetts",
    "Individuals 6": "",
}

# (rank, score, name, team)
ROWS = [
    (1, 51.30, "Sicheng Zhou", "PRISMS Falcons"),
    (2, 42.65, "David Taehee Lee", "PRISMS Falcons"),
    (2, 42.65, "Michael Lu", "Ward Melville Math Team D"),
    (4, 39.57, "Aaron Le", "Lion Valley Alpha"),
    (5, 38.55, "Yeyin Zhu", "PRISMS Young Falcons"),
    (6, 38.49, "Kevin Xuanhao Liu", "Lion Valley Alpha"),
    (7, 37.16, "Matthew Qian", "CCHS Math"),
    (7, 37.16, "Luca Pieleanu", "Russian School of Mathematics Team A"),
    (9, 35.34, "Henry Zheng", "MN gold"),
    (10, 35.08, "William Qian", "Maryland United"),
    (10, 35.08, "Sophia Hou", "LS Math Team B"),
    (10, 35.08, "David Kim", "Clarke Middle School Math Team"),
    (10, 35.08, "Sophia Zhang", "PRISMS Falcons"),
    (10, 35.08, "David Zhang", "Traditional Salad"),
    (10, 35.08, "Aidan Le", "Lion Valley Alpha"),
    (10, 35.08, "Richard Wang", "Texas Thunder"),
    (10, 35.08, "Xinyi Li", "Texas Thunder"),
    (10, 35.08, "Brandon Ni", "Lexington Armadillo"),
    (10, 35.08, "Jonathan Liu", "Lexington Banana"),
    (20, 32.81, "Austin Wang", "MN gold"),
    (21, 31.03, "Victor Lin", "Texas Academy of Math and Science A"),
    (21, 31.03, "Selena Ge", "Clarke Middle School Math Team"),
    (21, 31.03, "Le Yi Tan", "Texas Typhoon"),
    (24, 30.98, "Lingfei Sophia Tang", "Math 4 Fun"),
    (24, 30.98, "Hanqin Gu", "fun math"),
    (24, 30.98, "Eric Dai", "Yu's Alligator"),
    (24, 30.98, "Michael Sun", "Maple"),
    (28, 30.93, "Samuel J. Kretzschmar", "MN gold"),
    (29, 30.92, "Evan Zhang", "Lion Valley Alpha"),
    (30, 30.80, "Pratham Mukewar", "The NH Celestials 2"),
    (30, 30.80, "Vedant Patil", "The NH Celestials 2"),
    (32, 30.73, "Jeffery Zhang", "University of Toronto Schools A"),
    (32, 30.73, "Jerry Xu", "Lexington Armadillo"),
    (34, 30.67, "Lewis Lau", "Montgomery County Team 1 November"),
    (34, 30.67, "Leo Wu", "Bayview Team A1"),
    (34, 30.67, "Amogh Akella", "Texas Thunder"),
    (37, 29.80, "LU CHANG", "MathTeam007"),
    (38, 29.59, "William Jimenez", "Benet Academy"),
    (38, 29.59, "Nathan Lu", "Maryland United"),
    (38, 29.59, "David Wang", "Maryland United"),
    (38, 29.59, "Xingguo Ding", "St. Paul's School"),
    (38, 29.59, "Ethan Shi", "Westchester Area Math Circle"),
    (38, 29.59, "Andrew Shen", "Texas Tornado"),
    (38, 29.59, "Michael Ren", "Syo Math A"),
    (38, 29.59, "Yingshan Xiao", "Maple"),
    (38, 29.59, "Emma Tang", "University of Toronto Schools A"),
    (38, 29.59, "William Liu", "Lion Valley Alpha"),
    (38, 29.59, "Sebastian Prasanna", "CRLS Team One"),
    (38, 29.59, "Krithik Manoharan", "Texas Typhoon"),
    (38, 29.59, "Grace Liu", "Individuals 4"),
    (38, 29.59, "Aryan Saha", "Individuals 6"),
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
            out_rows.append((row["student_id"], row["student_name"], 2023, rank, score))
            continue
        sid = next_id
        next_id += 1
        canon_name = name.strip()
        key_to_row[(canon_name.lower(), state)] = {"student_id": sid, "student_name": canon_name, "state": state}
        new_students.append({
            "student_id": sid, "student_name": canon_name, "state": state,
            "team_ids": "", "alias": "", "gender": ""
        })
        out_rows.append((sid, canon_name, 2023, rank, score))

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
