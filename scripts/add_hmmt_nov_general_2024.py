#!/usr/bin/env python3
"""
Add HMMT November 2024 General round to hmmt-nov-general/year=2024.
Names normalized to "First_Name Last_Name". Schema: student_id, student_name, year, rank, score.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "hmmt-nov-general" / "year=2024"

# Paste name -> normalized "First Last" for display and matching
NAME_NORMALIZE = {
    "GONG YICHEN": "Yichen Gong",
    "Bowen Deng": "Bowen Deng",
    "WU, ZIYANG": "Ziyang Wu",
    "WU,PENGYU": "PengYu Wu",
    "chen zizhuang": "Zizhuang Chen",
    "Weihong Sun": "Weihong Sun",
    "Li Tianyi": "Tianyi Li",
    "Xuan Mengqi": "Mengqi Xuan",
    "Zhang Kaicheng": "Kaicheng Zhang",
}

TEAM_TO_STATE = {
    "Math 4 Fun": "",
    "PRISMS Young Falcons": "California",
    "Gunn Black": "California",
    "The NH Celestials 2": "New Hampshire",
    "Individuals 5": "",
    "Bayview Team A1": "California",
    "The Pingry School": "New Jersey",
    "Shanghai High School Stallions": "",
    "Beijing Forbidden City": "",
    "Math School A": "",
    "Aftermath": "",
    "Lexington Delta": "Massachusetts",
    "SH Team 001": "",
    "All Aces Spade": "",
    "Paly Trolls": "California",
    "Maple": "",
    "Doozy Math Team B": "",
    "Sugar Club": "",
    "University of Toronto Schools A": "",
    "St. Paul's School": "",
    "Individuals 4": "",
    "AlphaStar Academy THUNDER": "California",
    "Lexington Gamma": "Massachusetts",
    "Maryland hmmt interest": "Maryland",
    "Texas Thunder": "Texas",
    "Texas Tornado": "Texas",
    "Westborough High School stRangers": "Massachusetts",
    "Bouncing Seals": "",
    "University of Toronto Schools A": "",
    "LS Math Team": "",
    "Géomètres du nord | Club Math Cégep de Sherbrooke": "",
    "Scarsdale C": "New York",
    "Tennessee Math Coalition Blue": "Tennessee",
    "CCHS A Team": "",
    "Clarke A": "New York",
    "All Aces Heart": "",
    "Ward Melville Math Team E": "New York",
}

# (rank, score, name_as_in_paste, team)
ROWS = [
    (1, 37.16, "Eric P Zhu", "Math 4 Fun"),
    (2, 36.30, "Peter Wang", "PRISMS Young Falcons"),
    (2, 36.30, "Dongyoon Shin", "Gunn Black"),
    (4, 36.08, "Pratham Mukewar", "The NH Celestials 2"),
    (4, 36.08, "Joanna Wu", "Individuals 5"),
    (6, 34.21, "Leo Wu", "Bayview Team A1"),
    (7, 32.94, "Elbert Ho", "The Pingry School"),
    (8, 32.08, "GONG YICHEN", "Shanghai High School Stallions"),
    (9, 30.81, "Bowen Deng", "Beijing Forbidden City"),
    (9, 30.81, "Soham Samanta", "Math School A"),
    (11, 30.67, "Gavin Guojun Zhao", "Shanghai High School Stallions"),
    (11, 30.67, "Michael Retakh", "Ward Melville Math Team E"),
    (11, 30.67, "Sohan Javeri", "Aftermath"),
    (11, 30.67, "Charles Yuanrui Zheng", "Lexington Delta"),
    (11, 30.67, "Weihong Sun", "SH Team 001"),
    (11, 30.67, "Li Tianyi", "SH Team 001"),
    (11, 30.67, "Xuan Mengqi", "SH Team 001"),
    (18, 30.59, "Hyun-Jin Kim", "All Aces Spade"),
    (18, 30.59, "Krittika Chandra", "Paly Trolls"),
    (18, 30.59, "Anji Wang", "Maple"),
    (18, 30.59, "Annabel Rong", "Doozy Math Team B"),
    (22, 29.73, "Gong Cheng", "Sugar Club"),
    (22, 29.73, "WU, ZIYANG", "Sugar Club"),
    (22, 29.73, "Perry Dai", "University of Toronto Schools A"),
    (22, 29.73, "Xingguo Ding", "St. Paul's School"),
    (22, 29.73, "Lingfei Sophia Tang", "Math 4 Fun"),
    (27, 27.76, "Alexander Svoronos", "Aftermath"),
    (28, 26.66, "Dylan Wang", "AlphaStar Academy THUNDER"),
    (29, 26.65, "chen zizhuang", "Shanghai High School Stallions"),
    (29, 26.65, "Susie Lu", "Individuals 4"),
    (31, 26.59, "WU,PENGYU", "Sugar Club"),
    (31, 26.59, "Zhang Kaicheng", "Beijing Forbidden City"),
    (33, 26.37, "Albert Wu", "The Pingry School"),
    (34, 25.57, "Jiya", "Individuals 4"),
    (35, 25.51, "Clark Hu", "Maryland hmmt interest"),
    (35, 25.51, "Chloe Weng", "Texas Thunder"),
    (37, 25.45, "Krithik Manoharan", "Texas Tornado"),
    (37, 25.45, "Mia Zhao", "Westborough High School stRangers"),
    (39, 25.39, "Siyuan Du", "Bouncing Seals"),
    (39, 25.39, "Vincent Wang", "All Aces Spade"),
    (39, 25.39, "Kaylyn Jinglin Zhang", "University of Toronto Schools A"),
    (42, 25.17, "Jonathan Liu", "Lexington Gamma"),
    (42, 25.17, "Samuel Tsui", "Lexington Gamma"),
    (42, 25.17, "Andrew Lau", "Texas Thunder"),
    (45, 24.32, "Jagan Mranal", "LS Math Team"),
    (45, 24.32, "Maxime Demers", "Géomètres du nord | Club Math Cégep de Sherbrooke"),
    (45, 24.32, "Kaiqi Xu", "Sugar Club"),
    (45, 24.32, "Yutong Wang", "Scarsdale C"),
    (45, 24.32, "Justin Guo", "Tennessee Math Coalition Blue"),
    (45, 24.32, "Eric Zang", "Texas Tornado"),
    (45, 24.32, "Zizhan Wang", "Doozy Math Team B"),
    (45, 24.32, "Brandon Ni", "Clarke A"),
    (45, 24.32, "Matthew Qian", "CCHS A Team"),
    (45, 24.32, "William Du", "All Aces Heart"),
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

    for (rank, score, paste_name, team) in ROWS:
        state = TEAM_TO_STATE.get(team, "").strip()
        normalized = NAME_NORMALIZE.get(paste_name.strip(), paste_name.strip())
        orig_lower = paste_name.strip().lower()
        norm_lower = normalized.lower()

        # Try normalized then original, with state then ""
        row = (
            key_to_row.get((norm_lower, state))
            or key_to_row.get((orig_lower, state))
            or key_to_row.get((norm_lower, ""))
            or key_to_row.get((orig_lower, ""))
        )
        if not row:
            for (k, v) in key_to_row.items():
                if (k[0] == norm_lower or k[0] == orig_lower) and (not state or k[1] == state):
                    row = v
                    break
        if row:
            # Output normalized name for 2024 general
            out_rows.append((row["student_id"], normalized, 2024, rank, score))
            continue
        sid = next_id
        next_id += 1
        key_to_row[(norm_lower, state)] = {"student_id": sid, "student_name": normalized, "state": state}
        new_students.append({
            "student_id": sid, "student_name": normalized, "state": state,
            "team_ids": "", "alias": "", "gender": ""
        })
        out_rows.append((sid, normalized, 2024, rank, score))

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
