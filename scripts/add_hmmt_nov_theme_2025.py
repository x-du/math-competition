#!/usr/bin/env python3
"""
Add HMMT November 2025 Theme round to hmmt-nov-theme/year=2025.
Schema: student_id, student_name, year, rank, score.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "hmmt-nov-theme" / "year=2025"

TEAM_TO_STATE = {
    "Phillips Academy A1": "Massachusetts",
    "Ward Melville Math Team D": "New York",
    "Brunswick School A": "Connecticut",
    "Leading Aces Academy 1": "California",
    "Mustangs": "",
    "Mustangs ": "",
    "Individuals 1": "",
    "Yu's Alligator": "Florida",
    "PRISMS Falcons": "California",
    "Lexington Gamma": "Massachusetts",
    "AB Math League": "",
    "Bayview Team A1": "California",
    "Texas Thunder": "Texas",
    "Jericho A": "New York",
    "Beijing Mingcheng Academy Red Panda": "",
    "Montgomery County Team 1 November": "Maryland",
    "Raritan Valley Math Team - Newton": "New Jersey",
    "Texas Academy of Math and Science A": "Texas",
    "Westchester Area Math Circle A": "New York",
    "Fish": "",
    "Nittany Lions": "Pennsylvania",
    "Seoul Foreign School": "",
    "PEA Chestnuts": "Massachusetts",
    "Nobles Math Club": "Massachusetts",
    "Pingry Bears": "New Jersey",
    "BUA Terriers": "Massachusetts",
    "Areteem Institute": "California",
    "Georgia Mathletes Team 2": "Georgia",
    "Beaver B": "Massachusetts",
    "Great Neck North": "New York",
    "Scarsdale A": "New York",
    "Rockville Friends": "Maryland",
    "pauvres de saint félicien": "",
    "pauvres de saint félicien ": "",
    "Glenbrook North Green": "Illinois",
    "BronxHMMT": "New York",
}

# (rank, score, name, team)
ROWS = [
    (1, 33.80, "Huanqi Zhang", "Phillips Academy A1"),
    (2, 31.73, "Harry Haiwen Gao", "Ward Melville Math Team D"),
    (2, 31.73, "Vikram Sarkar", "Brunswick School A"),
    (4, 31.67, "Jack Whitney-Epstein", "Brunswick School A"),
    (4, 31.67, "Aiden Yudong Wei", "Mustangs"),
    (6, 30.59, "Xuanyi Zhang", "Leading Aces Academy 1"),
    (6, 30.59, "Woojin Seong", "Individuals 1"),
    (8, 27.54, "Aaron Xie", "Yu's Alligator"),
    (8, 27.54, "Hongming Allan Zhao", "PRISMS Falcons"),
    (10, 26.39, "Ray Huang Cui", "Lexington Gamma"),
    (10, 26.39, "Bryan Li", "AB Math League"),
    (12, 26.31, "Leo Wu", "Bayview Team A1"),
    (12, 26.31, "Aaron Wu", "Texas Thunder"),
    (14, 25.32, "Yutong Zhao", "PRISMS Falcons"),
    (14, 25.32, "Ryan Zhang", "Jericho A"),
    (14, 25.32, "Liran Zhou", "Jericho A"),
    (14, 25.32, "Guo,yizhang", "Beijing Mingcheng Academy Red Panda"),
    (14, 25.32, "Tane Park", "Montgomery County Team 1 November"),
    (19, 24.24, "Kristin Zhang", "Raritan Valley Math Team - Newton"),
    (19, 24.24, "Larry Lee", "Texas Academy of Math and Science A"),
    (19, 24.24, "Ethan Shi", "Westchester Area Math Circle A"),
    (19, 24.24, "Yunong Wu", "Westchester Area Math Circle A"),
    (19, 24.24, "Sophie Zhang", "Leading Aces Academy 1"),
    (24, 24.17, "Eric Huang", "Fish"),
    (24, 24.17, "Michael Pok Hon Chen", "PRISMS Falcons"),
    (24, 24.17, "Aaron Le", "Nittany Lions"),
    (24, 24.17, "SHAO, JUNNING", "Beijing Mingcheng Academy Red Panda"),
    (24, 24.17, "David Yoongeun Oh", "Seoul Foreign School"),
    (24, 24.17, "Alex Ren", "PEA Chestnuts"),
    (24, 24.17, "Emmett Chen", "Nobles Math Club"),
    (24, 24.17, "Madeline Zhu", "Pingry Bears"),
    (24, 24.17, "Benjamin Taycher", "BUA Terriers"),
    (24, 24.17, "Patrick Liang", "Areteem Institute"),
    (24, 24.17, "Adrian Fong", "Areteem Institute"),
    (24, 24.17, "Max Lin", "Georgia Mathletes Team 2"),
    (24, 24.17, "Chaojie Lin", "Beaver B"),
    (37, 22.26, "Soham Samanta", "Fish"),
    (38, 22.15, "Bohan Wang", "PRISMS Falcons"),
    (38, 22.15, "Girish Prasad", "Westchester Area Math Circle A"),
    (40, 21.12, "Aaron Xu", "Great Neck North"),
    (41, 21.03, "WU, SIRUI", "Beijing Mingcheng Academy Red Panda"),
    (42, 21.02, "Benjamin Li", "Fish"),
    (43, 20.08, "Eric Shi Chen", "Fish"),
    (43, 20.08, "Arda Eroz", "Montgomery County Team 1 November"),
    (43, 20.08, "Yutong Wang", "Scarsdale A"),
    (46, 20.01, "Daniel Gong Li", "Rockville Friends"),
    (46, 20.01, "David Luo", "pauvres de saint félicien"),
    (46, 20.01, "Alvin Fang", "Glenbrook North Green"),
    (46, 20.01, "Justin Lee", "BronxHMMT"),
    (46, 20.01, "Benjamin Huang", "BronxHMMT"),
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
    # Alias: Guo,yizhang -> yizhang Guo
    for (k, v) in list(key_to_row.items()):
        if k[0] == "yizhang guo":
            key_to_row[("guo,yizhang", k[1])] = v
            key_to_row[("guo,yizhang", "")] = v
            break
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
