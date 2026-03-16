#!/usr/bin/env python3
"""
Add Math Kangaroo 2024 Grade 9 National Winners.
Resolves (name, state) via students.csv; adds new students as needed.
2024 format: no national_percentile in source.
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2024" / "grade=9"

STATE_ABBREV_TO_FULL = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut",
    "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida",
    "GA": "Georgia", "GU": "Guam", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
    "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
    "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
    "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}

# grade, name, score, rank, state
ROWS = [
    (9, "Jason Yin", 120, 1, "NY"),
    (9, "Rehan Babu", 120, 1, "CA"),
    (9, "Varun Gadi", 117, 2, "GA"),
    (9, "Caroline Huang", 115, 3, "GA"),
    (9, "Daisy Ying", 115, 3, "VA"),
    (9, "Jacob Khohayting", 115, 3, "FL"),
    (9, "Vlad Vynarchuk", 115, 3, "MA"),
    (9, "Jacob Wu", 112, 4, "CA"),
    (9, "Solon Xia", 112, 4, "KS"),
    (9, "Chit Ming Yuen", 111, 5, "CA"),
    (9, "Curtis Wu", 111, 5, "MA"),
    (9, "Ziqi Wang", 111, 5, "CA"),
    (9, "Annabel Rong", 110, 6, "GA"),
    (9, "Brais Macknik-Conde", 110, 6, "TN"),
    (9, "Michael Mirkin", 110, 6, "MA"),
    (9, "Hauming Yuen", 109, 7, "CA"),
    (9, "Jonathan Liu", 109, 7, "MA"),
    (9, "Gina Li", 108, 8, "MA"),
    (9, "Anshul Mantri", 107, 9, "OR"),
    (9, "Michael Jian", 107, 9, "CA"),
    (9, "Raghav Arun", 107, 9, "NC"),
    (9, "Rohith Thomas", 107, 9, "CO"),
    (9, "Timothy Chen", 107, 9, "CA"),
    (9, "Aidan Cao", 106, 10, "CA"),
    (9, "Edward Zhang", 106, 10, "CA"),
    (9, "Haruka Kimura", 106, 10, "CT"),
    (9, "Jason Lee", 106, 10, "NJ"),
    (9, "Jeremy Yang", 106, 10, "MD"),
    (9, "Josh Tsimberg", 106, 10, "TX"),
    (9, "Kesav Kalanidhi", 106, 10, "NC"),
    (9, "Shuyin Liu", 106, 10, "WA"),
    (9, "Akash Krothapalli", 105, 11, "WA"),
    (9, "Anirudh Sengupta", 105, 11, "NC"),
    (9, "Billy Leng", 105, 11, "CA"),
    (9, "Chenxi Lu", 105, 11, "NY"),
    (9, "Narnia Poddar", 103, 12, "NY"),
    (9, "Wynn Marple", 103, 12, "CA"),
    (9, "Aniket Mangalampalli", 102, 13, "CA"),
    (9, "Bethesda Yeh", 102, 13, "MA"),
    (9, "Alena Kutsuk", 101, 14, "CA"),
    (9, "Charles Wang", 101, 14, "NJ"),
    (9, "Jisu Bang", 101, 14, "NY"),
    (9, "Levi Gould", 101, 14, "MN"),
    (9, "Soham Pattnaik", 101, 14, "VA"),
    (9, "Victor Wang", 101, 14, "MD"),
    (9, "Vikram Goudar", 101, 14, "VA"),
    (9, "Zachary Wong", 101, 14, "IL"),
    (9, "Anthony Wang", 100, 15, "NV"),
    (9, "Maxwell Lisuwandi", 100, 15, "MA"),
    (9, "Shourya Vyas", 100, 15, "TX"),
    (9, "Guillem Elizalde", 99, 16, "NH"),
    (9, "Alexander Ordukhanyan", 98, 17, "NY"),
    (9, "Jevin Xu", 98, 17, "VA"),
    (9, "Joey Yeong", 98, 17, "NY"),
    (9, "Raj Randery", 98, 17, "MA"),
    (9, "Samhitha Kamatala", 98, 17, "IL"),
    (9, "Somil Sarode", 98, 17, "CA"),
    (9, "Vibhun Naredla", 98, 17, "VA"),
    (9, "Anshul Raghav", 97, 18, "WA"),
    (9, "Nancy Zhang", 97, 18, "TX"),
    (9, "Amber Weng", 96, 19, "MD"),
    (9, "Arnav Prabhudesai", 96, 19, "MA"),
    (9, "Connor Kong", 96, 19, "CA"),
    (9, "Dev Batra", 96, 19, "CA"),
    (9, "Pablo Zhang", 96, 19, "CA"),
    (9, "Stas Chadrys", 96, 19, "NY"),
    (9, "Avery Xu", 95, 20, "NY"),
    (9, "Platon Gorkavy", 95, 20, "MA"),
    (9, "Revanth Raparla", 95, 20, "TX"),
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

    for grade, name, score, rank, state_abbrev in ROWS:
        state = STATE_ABBREV_TO_FULL.get(state_abbrev.strip().upper(), state_abbrev.strip())
        name_clean = name.strip()
        key = (name_clean.lower(), state)
        row = key_to_row.get(key)
        if row:
            out_rows.append((row["student_id"], row["student_name"], state, grade, score, rank, ""))
            continue

        sid = next_id
        next_id += 1
        key_to_row[key] = {"student_id": sid, "student_name": name_clean, "state": state}
        new_students.append({
            "student_id": sid, "student_name": name_clean, "state": state,
            "team_ids": "", "alias": "", "gender": "", "grade_in_2026": ""
        })
        out_rows.append((sid, name_clean, state, grade, score, rank, ""))

    # Append new students
    if new_students:
        with open(STUDENTS_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["student_id", "student_name", "state", "team_ids", "alias", "gender", "grade_in_2026"], extrasaction="ignore")
            for r in new_students:
                w.writerow(r)
        print(f"Added {len(new_students)} new students")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "results.csv"
    rank_counts = {}
    for _, _, _, _, _, r, _ in out_rows:
        rank_counts[r] = rank_counts.get(r, 0) + 1
    rank_to_mcp = {}
    r = 1
    for rank_val in sorted(rank_counts.keys()):
        n = rank_counts[rank_val]
        rank_to_mcp[rank_val] = (r + r + n - 1) / 2
        r += n

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["student_id", "student_name", "state", "grade", "score", "rank", "national_percentile", "mcp_rank"])
        for sid, name, state, grade, score, rank, pct in out_rows:
            w.writerow([sid, name, state, grade, score, rank, pct, rank_to_mcp[rank]])
    print(f"Wrote {out_path} ({len(out_rows)} rows)")


if __name__ == "__main__":
    main()
