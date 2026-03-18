#!/usr/bin/env python3
"""
Add HMMT November 2023 Theme round to hmmt-nov-theme/year=2023.
Schema: student_id, student_name, year, rank, score.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "hmmt-nov-theme" / "year=2023"

TEAM_TO_STATE = {
    "All Aces Spade": "",
    "Texas Typhoon": "Texas",
    "Math 4 Fun": "",
    "PRISMS Falcons": "California",
    "fun math": "",
    "Choate Math Team": "Connecticut",
    "Individuals 2": "",
    "Maryland United": "Maryland",
    "Texas Thunder": "Texas",
    "Lion Valley Alpha": "",
    "Traditional Salad": "",
    "MathTeam007": "",
    "Lexington Armadillo": "Massachusetts",
    "Lexington Banana": "Massachusetts",
    "LS Math Team B": "",
    "BISV Bobcats A": "California",
    "Texas Tornado": "Texas",
    "University of Toronto Schools A": "",
    "St. Paul's School": "",
    "Albany Area Math Circle Cardinals": "New York",
    "Maple": "",
    "Ward Melville Math Team D": "New York",
    "Individuals 5": "",
    "Beijing Forbidden City": "",
    "CRLS Team One": "Massachusetts",
    "The NH Celestials 2": "New Hampshire",
    "Fat L Club": "",
    "DA Math Team": "",
    "PRISMS Young Falcons": "California",
    "University of Toronto Schools B": "",
    "Glenbrook North Gold": "Illinois",
    "UCC Math Society Team C": "",
    "East Brunswick Math Circle Renegade Raiders": "New Jersey",
    "BASIS M&P": "",
    "WSHS Team 2": "",
}

# (rank, score, name, team)
ROWS = [
    (1, 39.08, "Vincent Wang", "All Aces Spade"),
    (2, 32.73, "Eric Zang", "Texas Typhoon"),
    (3, 31.59, "Alan Cheng", "Math 4 Fun"),
    (3, 31.59, "Sicheng Zhou", "PRISMS Falcons"),
    (3, 31.59, "Hanqin Gu", "fun math"),
    (3, 31.59, "Peyton Li", "Choate Math Team"),
    (3, 31.59, "Susie Lu", "Individuals 2"),
    (8, 28.56, "Jeremy Yang", "Maryland United"),
    (9, 28.50, "Richard Wang", "Texas Thunder"),
    (10, 27.43, "Evan Zhang", "Lion Valley Alpha"),
    (11, 26.32, "Raymond Ge", "Math 4 Fun"),
    (11, 26.32, "Sophie Yinuo Zheng", "Traditional Salad"),
    (11, 26.32, "LU CHANG", "MathTeam007"),
    (11, 26.32, "Samuel Tsui", "Lexington Armadillo"),
    (11, 26.32, "Eric Zhang", "Lexington Banana"),
    (16, 25.24, "Eric P Zhu", "Math 4 Fun"),
    (16, 25.24, "Isaac Jo", "LS Math Team B"),
    (16, 25.24, "Troy Yang", "BISV Bobcats A"),
    (16, 25.24, "Andrew Shen", "Texas Tornado"),
    (16, 25.24, "Jeffery Zhang", "University of Toronto Schools A"),
    (16, 25.24, "Andrew Ma", "University of Toronto Schools A"),
    (16, 25.24, "Aiden Dai", "Glenbrook North Gold"),
    (23, 25.17, "David Yu", "Maryland United"),
    (23, 25.17, "Xingguo Ding", "St. Paul's School"),
    (23, 25.17, "Kailin Yang", "PRISMS Falcons"),
    (23, 25.17, "David Taehee Lee", "PRISMS Falcons"),
    (23, 25.17, "Jason Lian", "Albany Area Math Circle Cardinals"),
    (23, 25.17, "Hongyi Huang", "UCC Math Society Team C"),
    (23, 25.17, "Yingshan Xiao", "Maple"),
    (23, 25.17, "Shirley Xiong", "Ward Melville Math Team D"),
    (23, 25.17, "Michael Lu", "Ward Melville Math Team D"),
    (23, 25.17, "Shraaptesh Lokanda", "East Brunswick Math Circle Renegade Raiders"),
    (23, 25.17, "Ian Wang", "BASIS M&P"),
    (23, 25.17, "Le Yi Tan", "Texas Typhoon"),
    (23, 25.17, "Jerry Xu", "Lexington Armadillo"),
    (23, 25.17, "Hwiseo", "Lexington Armadillo"),
    (23, 25.17, "Sohji Matsuda", "Individuals 5"),
    (38, 23.26, "Mingxuan Zhang", "Beijing Forbidden City"),
    (39, 22.21, "Jason Yang", "Lexington Armadillo"),
    (40, 22.19, "Jiya Neelesh Deo Dani", "Texas Tornado"),
    (41, 22.15, "Emily Zhang", "WSHS Team 2"),
    (42, 21.14, "Daniel Yu", "Maryland United"),
    (42, 21.14, "Lingfei Sophia Tang", "Math 4 Fun"),
    (42, 21.14, "Samuel Lin", "Albany Area Math Circle Cardinals"),
    (42, 21.14, "Joshua Kou", "Texas Tornado"),
    (42, 21.14, "Ryan Chase Casey", "The NH Celestials 2"),
    (42, 21.14, "Charlotte Younger", "CRLS Team One"),
    (48, 21.08, "Nathan Lu", "Maryland United"),
    (49, 21.07, "Kevin Zhang", "Fat L Club"),
    (49, 21.07, "Kyle Yang", "DA Math Team"),
    (49, 21.07, "Jagan Mranal", "LS Math Team B"),
    (49, 21.07, "Heyang Ni", "PRISMS Falcons"),
    (49, 21.07, "Huiran Zheng", "MathTeam007"),
    (49, 21.07, "James Qiu", "University of Toronto Schools B"),
    (49, 21.07, "Yutong Zhao", "PRISMS Young Falcons"),
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
