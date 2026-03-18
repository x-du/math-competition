#!/usr/bin/env python3
"""
Add HMMT November 2025 Overall Individual to hmmt-nov/year=2025.
Resolves (name, state) via students.csv; adds new students as needed.
Schema: student_id, student_name, year, rank, total_score, score_1, score_2 (General, Theme).
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "hmmt-nov" / "year=2025"

TEAM_TO_STATE = {
    "Bayview Team A1": "California",
    "Brunswick School A": "Connecticut",
    "Leading Aces Academy 1": "California",
    "Ward Melville Math Team D": "New York",
    "Jericho A": "New York",
    "Big L Club": "",
    "Montgomery County Team 1 November": "Maryland",
    "Clarke A": "New York",
    "Beijing Mingcheng Academy Red Panda": "",
    "PRISMS Falcons": "California",
    "Raritan Valley Math Team - Newton": "New Jersey",
    "Yu's Alligator": "Florida",
    "Westchester Area Math Circle A": "New York",
    "Individuals 1": "",
    "Pingry Bears": "New Jersey",
    "Areteem Institute": "California",
    "Mustangs": "",
    "AB Math League": "",
    "Phillips Academy A1": "Massachusetts",
    "Rockville Friends": "Maryland",
    "Fish": "",
    "Texas Tornado": "Texas",
    "pauvres de saint félicien": "",
    "Beijing Forbidden City": "",
    "Nittany Lions": "Pennsylvania",
    "PHS Apricot": "California",
    "BronxHMMT": "New York",
    "All Aces Spade": "",
    "Individuals 3": "",
}

# (rank, total_score, score_1, score_2, name, team)
ROWS = [
    (1, 70.68, 44.37, 26.31, "Leo Wu", "Bayview Team A1"),
    (2, 65.49, 33.82, 31.67, "Jack Whitney-Epstein", "Brunswick School A"),
    (3, 64.26, 33.67, 30.59, "Xuanyi Zhang", "Leading Aces Academy 1"),
    (4, 60.18, 28.44, 31.73, "Harry Haiwen Gao", "Ward Melville Math Team D"),
    (5, 60.05, 34.73, 25.32, "Ryan Zhang", "Jericho A"),
    (6, 59.21, 41.39, 17.82, "Advait Joshi", "Big L Club"),
    (7, 58.91, 41.08, 17.82, "Eric Xie", "Montgomery County Team 1 November"),
    (8, 57.91, 26.17, 31.73, "Vikram Sarkar", "Brunswick School A"),
    (9, 54.90, 41.24, 13.66, "Brandon Ni", "Clarke A"),
    (10, 53.68, 29.50, 24.17, "SHAO, JUNNING", "Beijing Mingcheng Academy Red Panda"),
    (11, 52.77, 28.60, 24.17, "Michael Pok Hon Chen", "PRISMS Falcons"),
    (12, 52.56, 27.24, 25.32, "Liran Zhou", "Jericho A"),
    (13, 51.57, 33.74, 17.82, "David Zhang", "Raritan Valley Math Team - Newton"),
    (14, 51.42, 33.59, 17.82, "Sohan Javeri", "Brunswick School A"),
    (15, 50.66, 23.12, 27.54, "Aaron Xie", "Yu's Alligator"),
    (16, 50.42, 26.17, 24.24, "Yunong Wu", "Westchester Area Math Circle A"),
    (16, 50.42, 19.82, 30.59, "Woojin Seong", "Individuals 1"),
    (18, 50.35, 26.17, 24.17, "Madeline Zhu", "Pingry Bears"),
    (18, 50.35, 26.17, 24.17, "Patrick Liang", "Areteem Institute"),
    (20, 49.57, 17.90, 31.67, "Aiden Yudong Wei", "Mustangs"),
    (21, 49.43, 21.89, 27.54, "Hongming Allan Zhao", "PRISMS Falcons"),
    (22, 48.41, 22.02, 26.39, "Bryan Li", "AB Math League"),
    (23, 48.40, 14.60, 33.80, "Huanqi Zhang", "Phillips Academy A1"),
    (24, 46.19, 26.17, 20.01, "Daniel Gong Li", "Rockville Friends"),
    (25, 46.17, 33.67, 12.51, "Youran Gu", "PRISMS Falcons"),
    (26, 45.14, 19.82, 25.32, "Yutong Zhao", "PRISMS Falcons"),
    (27, 44.19, 23.15, 21.03, "WU, SIRUI", "Beijing Mingcheng Academy Red Panda"),
    (28, 44.16, 22.01, 22.15, "Bohan Wang", "PRISMS Falcons"),
    (29, 44.07, 19.82, 24.24, "Ethan Shi", "Westchester Area Math Circle A"),
    (30, 44.04, 21.89, 22.15, "Girish Prasad", "Westchester Area Math Circle A"),
    (31, 44.00, 26.17, 17.82, "Aashritha Kolli", "Pingry Bears"),
    (32, 43.12, 29.58, 13.54, "Jay Wang", "PHS Apricot"),
    (33, 43.12, 22.09, 21.02, "Benjamin Li", "Fish"),
    (34, 42.13, 22.17, 19.96, "Shaheem Samsudeen", "Texas Tornado"),
    (35, 42.03, 16.72, 25.32, "Guo,yizhang", "Beijing Mingcheng Academy Red Panda"),
    (36, 41.85, 21.89, 19.96, "Eric Zhong", "Ward Melville Math Team D"),
    (37, 41.38, 19.12, 22.26, "Soham Samanta", "Fish"),
    (38, 40.96, 20.95, 20.01, "David Luo", "pauvres de saint félicien"),
    (39, 40.95, 16.77, 24.17, "Eric Huang", "Fish"),
    (40, 40.14, 14.83, 25.32, "Tane Park", "Montgomery County Team 1 November"),
    (41, 40.07, 22.25, 17.82, "XIAOYUETENG", "Beijing Forbidden City"),
    (42, 39.99, 22.17, 17.82, "WANG WEIHAO", "Beijing Forbidden City"),
    (43, 39.99, 30.61, 9.38, "Alexander Yu", "Nittany Lions"),
    (44, 39.90, 19.82, 20.08, "Arda Eroz", "Montgomery County Team 1 November"),
    (45, 39.84, 15.66, 24.17, "Aaron Le", "Nittany Lions"),
    (45, 39.84, 26.17, 13.66, "Felix Yu", "PHS Apricot"),
    (45, 39.84, 19.82, 20.01, "Justin Lee", "BronxHMMT"),
    (45, 39.84, 19.82, 20.01, "Benjamin Huang", "BronxHMMT"),
    (49, 39.71, 26.17, 13.54, "Ethan Gu", "All Aces Spade"),
    (50, 39.20, 22.33, 16.87, "Samuel Ding", "Individuals 3"),
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
        rank, total_score, score_1, score_2, name, team = tup
        state = TEAM_TO_STATE.get(team, "")
        key = (name.strip().lower(), state)
        row = key_to_row.get(key) or key_to_row.get((name.strip().lower(), ""))
        if not row:
            for (k, v) in key_to_row.items():
                if k[0] == name.strip().lower() and (not state or k[1] == state):
                    row = v
                    break
        if row:
            out_rows.append((row["student_id"], row["student_name"], 2025, rank, total_score, score_1, score_2))
            continue
        sid = next_id
        next_id += 1
        canon_name = name.strip()
        key_to_row[(canon_name.lower(), state)] = {"student_id": sid, "student_name": canon_name, "state": state}
        new_students.append({
            "student_id": sid, "student_name": canon_name, "state": state,
            "team_ids": "", "alias": "", "gender": ""
        })
        out_rows.append((sid, canon_name, 2025, rank, total_score, score_1, score_2))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "results.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["student_id", "student_name", "year", "rank", "total_score", "score_1", "score_2"])
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
