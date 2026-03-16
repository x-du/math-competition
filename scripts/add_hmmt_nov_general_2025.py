#!/usr/bin/env python3
"""
Add HMMT November 2025 General round to hmmt-nov-general/year=2025.
Schema: student_id, student_name, year, rank, score.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "hmmt-nov-general" / "year=2025"

TEAM_TO_STATE = {
    "Bayview Team A1": "California",
    "Big L Club": "",
    "Clarke A": "New York",
    "Montgomery County Team 1 November": "Maryland",
    "Jericho A": "New York",
    "Brunswick School A": "Connecticut",
    "Raritan Valley Math Team - Newton": "New Jersey",
    "PRISMS Falcons": "California",
    "Leading Aces Academy 1": "California",
    "Nittany Lions": "Pennsylvania",
    "PHS Apricot": "California",
    "Beijing Mingcheng Academy Red Panda": "",
    "DA Math Team": "",
    "Ward Melville Math Team D": "New York",
    "All Aces Spade": "",
    "Rockville Friends": "Maryland",
    "Westchester Area Math Circle A": "New York",
    "Pingry Bears": "New Jersey",
    "Areteem Institute": "California",
    "Lexington Gamma": "Massachusetts",
    "Elton Academy Math": "",
    "Mass ARML Stars": "Massachusetts",
    "Winchester 1": "Massachusetts",
    "Yu's Alligator": "Florida",
    "Beijing Forbidden City": "",
    "Texas Tornado": "Texas",
    "Fish": "",
    "Georgia Mathletes Team 1": "Georgia",
    "Westborough High School Rangers": "Massachusetts",
    "AB Math League": "",
    "The Tigers": "",
    "pauvres de saint félicien": "",
    "pauvres de saint félicien ": "",
    "ICALC Learning Centre Math A": "",
    "USCHS": "California",
    "Ontario Math Circles": "Ontario, Canada",
    "SAS Eagles A": "",
    "BronxHMMT": "New York",
    "Phillips Academy A1": "Massachusetts",
    "Russian School of Mathematics Team D": "",
    "Individuals 1": "",
    "Individuals 3": "",
    "Euler": "",
    "Emma Willard School (Jesters)": "New York",
    "Great Neck North": "New York",
    "PEA Chestnuts": "Massachusetts",
    "Lexington Delta": "Massachusetts",
    "Wild Boars": "",
    "Albany Area Math Circle Cardinals": "New York",
}

# (rank, score, name, team)
ROWS = [
    (1, 44.37, "Leo Wu", "Bayview Team A1"),
    (2, 41.39, "Advait Joshi", "Big L Club"),
    (3, 41.24, "Brandon Ni", "Clarke A"),
    (4, 41.08, "Eric Xie", "Montgomery County Team 1 November"),
    (5, 34.73, "Ryan Zhang", "Jericho A"),
    (6, 33.82, "Jack Whitney-Epstein", "Brunswick School A"),
    (7, 33.74, "David Zhang", "Raritan Valley Math Team - Newton"),
    (8, 33.67, "Youran Gu", "PRISMS Falcons"),
    (8, 33.67, "Xuanyi Zhang", "Leading Aces Academy 1"),
    (10, 33.59, "Sohan Javeri", "Brunswick School A"),
    (11, 30.61, "Alexander Yu", "Nittany Lions"),
    (12, 29.58, "Jay Wang", "PHS Apricot"),
    (13, 29.50, "SHAO, JUNNING", "Beijing Mingcheng Academy Red Panda"),
    (14, 28.60, "Michael Pok Hon Chen", "PRISMS Falcons"),
    (15, 28.44, "Kyle Yang", "DA Math Team"),
    (15, 28.44, "Harry Haiwen Gao", "Ward Melville Math Team D"),
    (17, 27.24, "Liran Zhou", "Jericho A"),
    (18, 26.17, "Ethan Gu", "All Aces Spade"),
    (18, 26.17, "Daniel Gong Li", "Rockville Friends"),
    (18, 26.17, "Yunong Wu", "Westchester Area Math Circle A"),
    (18, 26.17, "Vikram Sarkar", "Brunswick School A"),
    (18, 26.17, "Felix Yu", "PHS Apricot"),
    (18, 26.17, "Madeline Zhu", "Pingry Bears"),
    (18, 26.17, "Aashritha Kolli", "Pingry Bears"),
    (18, 26.17, "Patrick Liang", "Areteem Institute"),
    (18, 26.17, "James Wu", "Lexington Gamma"),
    (27, 25.39, "Johnson Jiang", "Elton Academy Math"),
    (28, 24.32, "Adam Oliver Yanco", "Mass ARML Stars"),
    (29, 24.28, "Daniel Tian Wu", "Winchester 1"),
    (30, 23.15, "WU, SIRUI", "Beijing Mingcheng Academy Red Panda"),
    (31, 23.12, "Aaron Xie", "Yu's Alligator"),
    (32, 23.11, "YI SUIHAN", "Beijing Mingcheng Academy Red Panda"),
    (33, 22.33, "Samuel Ding", "Individuals 3"),
    (34, 22.25, "XIAOYUETENG", "Beijing Forbidden City"),
    (35, 22.17, "WANG WEIHAO", "Beijing Forbidden City"),
    (35, 22.17, "Shaheem Samsudeen", "Texas Tornado"),
    (37, 22.09, "Benjamin Li", "Fish"),
    (37, 22.09, "Quang (Benny) Le", "Georgia Mathletes Team 1"),
    (39, 22.02, "Samhith Dewal", "Westborough High School Rangers"),
    (39, 22.02, "Bryan Li", "AB Math League"),
    (41, 22.01, "Bohan Wang", "PRISMS Falcons"),
    (42, 21.89, "Hongming Allan Zhao", "PRISMS Falcons"),
    (42, 21.89, "Eric Zhong", "Ward Melville Math Team D"),
    (42, 21.89, "Girish Prasad", "Westchester Area Math Circle A"),
    (45, 20.95, "Max Liang", "Yu's Alligator"),
    (45, 20.95, "Sidarth Singh", "The Tigers"),
    (45, 20.95, "Brian Sun", "Euler"),
    (45, 20.95, "David Luo", "pauvres de saint félicien"),
    (45, 20.95, "Jeremy Zhang", "ICALC Learning Centre Math A"),
    (50, 19.82, "Luke Song An", "USCHS"),
    (50, 19.82, "Yutong Zhao", "PRISMS Falcons"),
    (50, 19.82, "Raymond Wang", "Raritan Valley Math Team - Newton"),
    (50, 19.82, "Ryan Zhu", "Raritan Valley Math Team - Newton"),
    (50, 19.82, "Ethan Shi", "Westchester Area Math Circle A"),
    (50, 19.82, "Hayden Hughes", "Westchester Area Math Circle A"),
    (50, 19.82, "Hanru Zhang", "Jericho A"),
    (50, 19.82, "Nanxuan Zhang", "pauvres de saint félicien"),
    (50, 19.82, "Arjun Leih", "Brunswick School A"),
    (50, 19.82, "Jason Lian", "Albany Area Math Circle Cardinals"),
    (50, 19.82, "Samuel Lin", "Albany Area Math Circle Cardinals"),
    (50, 19.82, "Mingdong Ma", "Albany Area Math Circle Cardinals"),
    (50, 19.82, "JiSu Bang", "Emma Willard School (Jesters)"),
    (50, 19.82, "张鑫野", "Beijing Forbidden City"),
    (50, 19.82, "Victor Yang", "Great Neck North"),
    (50, 19.82, "Michael Yang", "PEA Chestnuts"),
    (50, 19.82, "Danyang Xu", "Lexington Delta"),
    (50, 19.82, "Arnab Dasgupta", "Lexington Delta"),
    (50, 19.82, "Sophie Liu", "Wild Boars"),
    (50, 19.82, "Donald Li", "Ontario Math Circles"),
    (50, 19.82, "Arda Eroz", "Montgomery County Team 1 November"),
    (50, 19.82, "Kayla Jian", "SAS Eagles A"),
    (50, 19.82, "Charles Yuanrui Zheng", "Lexington Gamma"),
    (50, 19.82, "Aaron Krasinski", "BronxHMMT"),
    (50, 19.82, "Rajdeep Banik", "BronxHMMT"),
    (50, 19.82, "Justin Lee", "BronxHMMT"),
    (50, 19.82, "Caroline Jiang", "BronxHMMT"),
    (50, 19.82, "Benjamin Huang", "BronxHMMT"),
    (50, 19.82, "Daniel Cai", "AB Math League"),
    (50, 19.82, "Christopher Zhang", "AB Math League"),
    (50, 19.82, "Paige Zhu", "Phillips Academy A1"),
    (50, 19.82, "Eileen Lee", "Russian School of Mathematics Team D"),
    (50, 19.82, "Woojin Seong", "Individuals 1"),
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
        state = TEAM_TO_STATE.get(team, "").strip() or TEAM_TO_STATE.get(team.strip(), "")
        key = (name.strip().lower(), state)
        row = key_to_row.get(key) or key_to_row.get((name.strip().lower(), ""))
        if not row:
            for (k, v) in key_to_row.items():
                if k[0] == name.strip().lower() and (not state or k[1] == state):
                    row = v
                    break
        if row:
            out_rows.append((row["student_id"], row["student_name"], 2025, rank, score))
            continue
        sid = next_id
        next_id += 1
        canon_name = name.strip()
        key_to_row[(canon_name.lower(), state)] = {"student_id": sid, "student_name": canon_name, "state": state}
        new_students.append({
            "student_id": sid, "student_name": canon_name, "state": state,
            "team_ids": "", "alias": "", "gender": ""
        })
        out_rows.append((sid, canon_name, 2025, rank, score))

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
