#!/usr/bin/env python3
"""
Add HMMT February 2022 Combinatorics round to hmmt-feb-combo/year=2022.
Resolves (name, state) via students.csv; adds new students as needed.
Schema: student_id, student_name, year, rank, score (same as other hmmt-feb-combo years).
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "hmmt-feb-combo" / "year=2022"

# Use "" for teams that are multi-state or where we want name-only match to avoid duplicates.
TEAM_TO_STATE = {
    "Texas Momentum A": "Texas",
    "San Diego A1": "California",
    "Tin Man": "New York",
    "Motown All Stars": "Michigan",
    "Pleasanton A": "California",
    "AlphaStar Academy FIRE": "California",
    "EddieSolo": "",
    "AlphaStar Academy AIR": "California",
    "Harker Omega": "California",
    "Lehigh Valley Fire": "",
    "Lehigh Valley Ice": "",
    "Lexington Alpha": "Massachusetts",
    "Florida Alligators": "Florida",
    "Washington Gold 1": "Washington",
    "MN All-State Math Team 1 - Gold": "Minnesota",
    "Spice": "California",
    "University of Toronto Schools A": "Ontario, Canada",
    "Pentagon Hexagon Oregon A": "Oregon",
    "Ontario Math Circles": "Ontario, Canada",
    "Mathematical Admirers of Chdenmathcounts": "",
    "Random Math Team C": "California",
    "AlphaStar Academy EARTH": "California",
    "Washington Gold 2": "Washington",
    "Washington Gold 3": "Washington",
    "Wild Boars": "",
    "Montgomery County Team 1": "Maryland",
    "Yellowjackets": "",
    "Orange County Math Circle BrawlphaStars": "California",
    "San Diego A2": "California",
    "OHS Pixels Hardcore Team 1": "California",
    "Bergen County Academies Team 1": "New Jersey",  # keep to disambiguate Justin Zhang NJ
    "Western Mass ARML Stars": "Massachusetts",
    "TJ-A": "Virginia",
    "No Coast Best Coast": "Illinois",
    "Burgas A": "",
    "NNHS Math TeamA": "",
    "Pirates A": "",
    "TJ-B": "Virginia",
    "Scarecrow": "California",
    "Lion": "",
}

# (rank, score, name, team) from COMBINATORICS ROUND paste
ROWS = [
    (1, 48.53, "Luke Robitaille", "Texas Momentum A"),
    (2, 37.74, "Dylan Yu", "Texas Momentum A"),
    (3, 28.17, "Alex Zhao", "Washington Gold 1"),
    (3, 28.17, "Jessica Wan", "Florida Alligators"),
    (3, 28.17, "Linden Marcus Lee", "MN All-State Math Team 1 - Gold"),
    (6, 26.14, "Derek Liu", "San Diego A1"),
    (7, 25.21, "Rishabh Das", "Tin Man"),
    (8, 24.12, "Reagan Choi", "Motown All Stars"),
    (9, 24.07, "Jerry Liu", "Pleasanton A"),
    (10, 23.95, "Rohan Das", "AlphaStar Academy FIRE"),
    (11, 21.92, "Eddie Wei", "EddieSolo"),
    (12, 20.99, "Espen Slettnes", "AlphaStar Academy AIR"),
    (13, 20.93, "Olivia Xu", "Harker Omega"),
    (14, 20.82, "Daniel Xia", "Lehigh Valley Fire"),
    (14, 20.82, "Skyler Le", "Lehigh Valley Fire"),
    (14, 20.82, "Allen Wang", "Lehigh Valley Ice"),
    (14, 20.82, "Alexander Wang", "Lehigh Valley Ice"),
    (14, 20.82, "Evan Fan", "Lehigh Valley Ice"),
    (14, 20.82, "Alex Hu", "Harker Omega"),
    (14, 20.82, "Samuel Charney", "Lexington Alpha"),
    (14, 20.82, "Huaye Lin", "Lexington Alpha"),
    (14, 20.82, "Jason Zhang", "Motown All Stars"),
    (14, 20.82, "Nicole Shen", "Spice"),
    (14, 20.82, "Chris Ge", "Spice"),
    (14, 20.82, "Daniel Yang", "University of Toronto Schools A"),
    (14, 20.82, "Suyash Pandit", "Pentagon Hexagon Oregon A"),
    (14, 20.82, "Jeffrey Fang", "Pentagon Hexagon Oregon A"),
    (14, 20.82, "Annabel Ge", "Washington Gold 1"),
    (14, 20.82, "William Chenfeng Dai", "Ontario Math Circles"),
    (14, 20.82, "Jefferey", "Mathematical Admirers of Chdenmathcounts"),
    (14, 20.82, "Owen Yang", "Mathematical Admirers of Chdenmathcounts"),
    (14, 20.82, "Nilay Mishra", "Random Math Team C"),
    (14, 20.82, "Kavan Doctor", "Random Math Team C"),
    (14, 20.82, "Eric Shen", "AlphaStar Academy AIR"),
    (14, 20.82, "Johan Ko", "AlphaStar Academy AIR"),
    (14, 20.82, "Henry Wang", "AlphaStar Academy AIR"),
    (14, 20.82, "Catherine Li", "AlphaStar Academy EARTH"),
    (14, 20.82, "Alex Chen", "AlphaStar Academy EARTH"),
    (14, 20.82, "David Jiahui Zhang", "AlphaStar Academy FIRE"),
    (14, 20.82, "Yuuki Sawanoi", "Washington Gold 2"),
    (14, 20.82, "Owen J Zhang", "Washington Gold 2"),
    (14, 20.82, "Cecilia Sun", "Washington Gold 3"),
    (14, 20.82, "Adi Jasuja", "Tin Man"),
    (14, 20.82, "Brandon Lou", "Tin Man"),
    (14, 20.82, "Joy An", "Wild Boars"),
    (14, 20.82, "Kevin Joshua Wu", "Montgomery County Team 1"),
    (14, 20.82, "Hankai Zhang", "Yellowjackets"),
    (14, 20.82, "Benjamin Andrew Fan", "Orange County Math Circle BrawlphaStars"),
    (14, 20.82, "Won Jang", "Orange County Math Circle BrawlphaStars"),
    (14, 20.82, "Justin Zhang", "San Diego A2"),
    (14, 20.82, "Michelle Liang", "San Diego A2"),
    (14, 20.82, "Jiakang Chen", "Pleasanton A"),
    (14, 20.82, "Paul Andrew Hamrick", "OHS Pixels Hardcore Team 1"),
    (14, 20.82, "Alex Li", "Florida Alligators"),
    (14, 20.82, "Kevin Yang", "MN All-State Math Team 1 - Gold"),
    (14, 20.82, "Kenneth Ang Chen", "MN All-State Math Team 1 - Gold"),
    (14, 20.82, "Justin Zhang", "Bergen County Academies Team 1"),
    (14, 20.82, "Nikhil Mudumbi", "Bergen County Academies Team 1"),
    (14, 20.82, "Aaron Guo", "Texas Momentum A"),
    (14, 20.82, "Christopher Wu", "Texas Momentum A"),
    (14, 20.82, "Isabella Quan", "Texas Momentum A"),
    (14, 20.82, "Maxwell Zen", "Scarecrow"),
    (14, 20.82, "Ashley Zhu", "Lion"),
    (14, 20.82, "Benjamin Chen", "No Coast Best Coast"),
    (14, 20.82, "Boris Tsvetanov Gachevski", "Burgas A"),
    (14, 20.82, "Jason Jiang", "NNHS Math TeamA"),
    (14, 20.82, "Michael Chen", "Pirates A"),
    (14, 20.82, "Pavan Jayaraman", "Pirates A"),
    (14, 20.82, "Isabella Zhu", "TJ-A"),
    (14, 20.82, "Garrett A Heller", "TJ-A"),
    (14, 20.82, "Zani Xu", "TJ-A"),
    (14, 20.82, "Karthik Seetharaman", "Western Mass ARML Stars"),
    (14, 20.82, "Utkarsh Goyal", "TJ-B"),
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
    # Map "Garrett A Heller" -> Garrett Heller (Virginia)
    for (k, v) in list(key_to_row.items()):
        if k[0] == "garrett heller":
            key_to_row[("garrett a heller", k[1])] = v
            key_to_row[("garrett a heller", "")] = v
        if k[0] == "paul hamrick":
            key_to_row[("paul andrew hamrick", k[1])] = v
            key_to_row[("paul andrew hamrick", "")] = v
    return key_to_row, next_id


def main():
    key_to_row, next_id = load_students()
    new_students = []
    out_rows = []

    for (rank, score, name, team) in ROWS:
        state = TEAM_TO_STATE.get(team, "")
        key = (name.strip().lower(), state)
        row = key_to_row.get(key) or key_to_row.get((name.strip().lower(), ""))
        # When state is "", also try matching by name only (any state). When state is set, only match same state.
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
