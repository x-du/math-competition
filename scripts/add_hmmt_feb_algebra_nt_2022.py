#!/usr/bin/env python3
"""
Add HMMT February 2022 Algebra & Number Theory round to hmmt-feb-algebra-number-theory/year=2022.
Resolves (name, state) via students.csv; adds new students as needed.
Schema: student_id, student_name, year, rank, score.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "hmmt-feb-algebra-number-theory" / "year=2022"

TEAM_TO_STATE = {
    "Texas Momentum A": "Texas",
    "Random Math Team C": "California",
    "Tin Man": "New York",
    "San Diego A1": "California",
    "AlphaStar Academy AIR": "California",
    "Lexington Alpha": "Massachusetts",
    "Washington Gold 1": "Washington",
    "Motown All Stars": "Michigan",
    "Yu's Buffalo": "",
    "OS Betelgeuse": "",
    "Montgomery County Team 1": "Maryland",
    "Lehigh Valley Fire": "",
    "Lehigh Valley Ice": "",
    "TJ-A": "Virginia",
    "Bergen County Academies Team 1": "New Jersey",
    "San Diego A2": "California",
    "Burgas B": "",
    "Knights Alpha": "California",
    "Orange County Math Circle BrawlphaStars": "California",
    "OHS Pixels Hardcore Team 1": "California",
    "Washington Gold 2": "Washington",
    "Gunn Red": "California",
    "Western Mass ARML Stars": "Massachusetts",
}

# (rank, score, name, team) from ALGEBRA AND NUMBER THEORY ROUND
ROWS = [
    (1, 43.08, "Luke Robitaille", "Texas Momentum A"),
    (2, 35.67, "Amol Rama", "Random Math Team C"),
    (3, 31.44, "Adi Jasuja", "Tin Man"),
    (3, 31.44, "Derek Liu", "San Diego A1"),
    (5, 29.38, "Raymond Feng", "AlphaStar Academy AIR"),
    (6, 29.32, "Huaye Lin", "Lexington Alpha"),
    (7, 29.31, "Rishabh Das", "Tin Man"),
    (8, 29.24, "Edward Yu", "Washington Gold 1"),
    (8, 29.24, "Dylan Yu", "Texas Momentum A"),
    (10, 28.17, "Reagan Choi", "Motown All Stars"),
    (10, 28.17, "Brandon Cai", "Yu's Buffalo"),
    (12, 25.16, "Kaixin Wang", "OS Betelgeuse"),
    (13, 25.15, "Nathan Cho", "Montgomery County Team 1"),
    (14, 23.95, "Andrew Lin", "Lehigh Valley Fire"),
    (14, 23.95, "Jack Albright", "AlphaStar Academy AIR"),
    (16, 23.15, "Christopher Wu", "Texas Momentum A"),
    (17, 23.03, "Alexander Wang", "Lehigh Valley Ice"),
    (18, 21.89, "Aaron Guo", "Texas Momentum A"),
    (18, 21.89, "Isabella Zhu", "TJ-A"),
    (20, 21.82, "Jason Mao", "Lehigh Valley Fire"),
    (20, 21.82, "Skyler Le", "Lehigh Valley Fire"),
    (20, 21.82, "Allen Wang", "Lehigh Valley Ice"),
    (20, 21.82, "Kevin Zhao", "Lexington Alpha"),
    (20, 21.82, "Razzi H. Masroor", "Motown All Stars"),
    (20, 21.82, "Nilay Mishra", "Random Math Team C"),
    (20, 21.82, "Advaith Avadhanam", "Random Math Team C"),
    (20, 21.82, "Neel Kolhe", "Random Math Team C"),
    (20, 21.82, "Eric Shen", "AlphaStar Academy AIR"),
    (20, 21.82, "William Chen", "AlphaStar Academy AIR"),
    (20, 21.82, "Yuuki Sawanoi", "Washington Gold 2"),
    (20, 21.82, "Andrew Gu", "Orange County Math Circle BrawlphaStars"),
    (20, 21.82, "Benjamin Andrew Fan", "Orange County Math Circle BrawlphaStars"),
    (20, 21.82, "Eddie Qiao", "San Diego A1"),
    (20, 21.82, "Robin Said Sharif", "San Diego A2"),
    (20, 21.82, "Marvin Mao", "Bergen County Academies Team 1"),
    (20, 21.82, "Jasen Plamenov Penchev", "Burgas B"),
    (20, 21.82, "Eric Yang", "Knights Alpha"),
    (20, 21.82, "Zani Xu", "TJ-A"),
    (39, 21.00, "Henry Jiang", "Motown All Stars"),
    (40, 20.99, "Paul Andrew Hamrick", "OHS Pixels Hardcore Team 1"),
    (41, 19.85, "Tristan Kay", "Washington Gold 1"),
    (42, 18.93, "Maximus Lu", "Bergen County Academies Team 1"),
    (43, 18.87, "Garrett A Heller", "TJ-A"),
    (44, 18.85, "Rowechen Zhong", "Texas Momentum A"),
    (44, 18.85, "Xinyi Guo", "Gunn Red"),
    (46, 18.81, "Maximus Liu", "Lehigh Valley Ice"),
    (46, 18.81, "Daniel Yuan", "Montgomery County Team 1"),
    (48, 18.74, "Bo Sun", "Lehigh Valley Fire"),
    (48, 18.74, "Samuel Wang", "TJ-A"),
    (48, 18.74, "Andrew Lee", "Western Mass ARML Stars"),
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
