#!/usr/bin/env python3
"""
Add Math Kangaroo 2024 Grade 10 National Winners.
Resolves (name, state) via students.csv; adds new students as needed.
2024 format: no national_percentile in source.
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2024" / "grade=10"

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
    (10, "Cheng Ma", 120, 1, "CA"),
    (10, "Jason Liu", 120, 1, "PA"),
    (10, "Lucas Hinds", 120, 1, "TN"),
    (10, "Samanyu Ganesh", 120, 1, "GA"),
    (10, "Shruti Arun", 116, 2, "CO"),
    (10, "Sohil Rathi", 116, 2, "CA"),
    (10, "Allan Yuan", 115, 3, "AL"),
    (10, "David Wang", 115, 3, "MD"),
    (10, "Michelle Nogin", 115, 3, "CA"),
    (10, "Soham Dam", 115, 3, "PA"),
    (10, "Tony Song", 115, 3, "MD"),
    (10, "Arjun Agarwal", 112, 4, "OR"),
    (10, "Baixuan Chen", 111, 5, "CA"),
    (10, "Plato Wong", 111, 5, "CA"),
    (10, "Alexander Sheffield", 110, 6, "NY"),
    (10, "Harini Venkatesh", 110, 6, "NH"),
    (10, "Kedaar Shankarnarayan", 110, 6, "NJ"),
    (10, "Renee Wang", 110, 6, "IL"),
    (10, "Aryan Agrawal", 108, 7, "WA"),
    (10, "Aishwarya Agrawal", 107, 8, "WA"),
    (10, "Mia Liu", 107, 8, "CA"),
    (10, "Alexa Chang", 106, 9, "CA"),
    (10, "Arnav Ahuja", 106, 9, "CA"),
    (10, "Aryan Raj", 106, 9, "VA"),
    (10, "Krithik Prasad", 106, 9, "IL"),
    (10, "Matthew Lkhagvasuren", 106, 9, "CA"),
    (10, "Andrey Kalashnikov", 105, 10, "MA"),
    (10, "Bhavin Dang", 105, 10, "AZ"),
    (10, "Brandon Hu", 105, 10, "VA"),
    (10, "Hanyuan Qu", 105, 10, "CA"),
    (10, "Jessica Wu", 105, 10, "MI"),
    (10, "Matthew Kokhan", 105, 10, "WA"),
    (10, "Michael Retakh", 105, 10, "NY"),
    (10, "Xizhi Zhang", 105, 10, "CA"),
    (10, "Mark Menaker", 104, 11, "CA"),
    (10, "Fedor Myshkin", 103, 12, "MA"),
    (10, "Rithik Vir", 103, 12, "CA"),
    (10, "Vishwa Srinivasan", 103, 12, "MA"),
    (10, "Alexander Peev", 102, 13, "WA"),
    (10, "Ishaan Nagireddi", 102, 13, "GA"),
    (10, "Neil Sriram", 102, 13, "NY"),
    (10, "Arush Goswami", 101, 14, "OR"),
    (10, "Ekaansh Agrawal", 101, 14, "WA"),
    (10, "Henry Chen", 101, 14, "IL"),
    (10, "Kefei Liao", 101, 14, "CA"),
    (10, "Matthew Karp", 101, 14, "NY"),
    (10, "Rishi Salvi", 101, 14, "CA"),
    (10, "Sophie Huang", 101, 14, "MD"),
    (10, "Suhani Pahuja", 101, 14, "CA"),
    (10, "Aahan Mahakud", 100, 15, "NJ"),
    (10, "Mihir Gupta", 100, 15, "CA"),
    (10, "Yifan Sheng", 100, 15, "CA"),
    (10, "Daniel Adler", 99, 16, "CA"),
    (10, "Petr Kisselev", 99, 16, "VA"),
    (10, "Siming Chen", 99, 16, "MA"),
    (10, "Clemens Brass", 98, 17, "NY"),
    (10, "Nathan Chan", 98, 17, "CA"),
    (10, "Sri Sumukh Vulava", 98, 17, "KY"),
    (10, "Adam Yanco", 97, 18, "MA"),
    (10, "Arnav Adepu", 97, 18, "NJ"),
    (10, "Crystal Huang", 97, 18, "CA"),
    (10, "Dan Wiechman", 97, 18, "NY"),
    (10, "Jake Y Lee", 97, 18, "CA"),
    (10, "Sophie He", 97, 18, "MA"),
    (10, "Jiajun Luo", 96, 19, "CT"),
    (10, "Karthik Prasad", 96, 19, "IL"),
    (10, "Roy Wang", 96, 19, "IL"),
    (10, "Sanjana Ramesh", 96, 19, "MI"),
    (10, "Aiden Yejoon Kim", 95, 20, "OK"),
    (10, "Albert Ding", 95, 20, "TN"),
    (10, "Andrew Feng", 95, 20, "PA"),
    (10, "Anna Voorhis", 95, 20, "CA"),
    (10, "Leya Balayoghan", 95, 20, "WA"),
    (10, "Noah Kim", 95, 20, "MA"),
    (10, "Paul Pan", 95, 20, "MA"),
    (10, "Xiyuan Zhang", 95, 20, "CA"),
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
