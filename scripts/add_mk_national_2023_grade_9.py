#!/usr/bin/env python3
"""
Add Math Kangaroo 2023 Grade 9 National Winners.
Resolves (name, state) via students.csv; adds new students as needed.
2023 format: no national_percentile in source.
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2023" / "grade=9"

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
    (9, "Aiden Yejoon Kim", 120, 1, "OK"),
    (9, "Aishwarya Agrawal", 120, 1, "WA"),
    (9, "Alexander Sheffield", 120, 1, "NY"),
    (9, "Arjun Agarwal", 120, 1, "OR"),
    (9, "Aryan Agrawal", 120, 1, "WA"),
    (9, "David Wang", 120, 1, "MD"),
    (9, "Eric Min", 120, 1, "TX"),
    (9, "Evan Zhang", 120, 1, "MD"),
    (9, "Harini Venkatesh", 120, 1, "NH"),
    (9, "Jason Liu", 120, 1, "PA"),
    (9, "Kedaar Shankarnarayan", 120, 1, "NJ"),
    (9, "Plato Wong", 120, 1, "CA"),
    (9, "Samanyu Ganesh", 120, 1, "GA"),
    (9, "Shruti Arun", 120, 1, "CO"),
    (9, "Sohil Rathi", 120, 1, "CA"),
    (9, "Tony Song", 120, 1, "MD"),
    (9, "Allan Yuan", 117, 2, "AL"),
    (9, "Matthew Kokhan", 117, 2, "WA"),
    (9, "Arush Goswami", 116, 3, "OR"),
    (9, "Brandon Hu", 116, 3, "VA"),
    (9, "Hugo Hu", 116, 3, "NY"),
    (9, "Michelle Nogin", 116, 3, "CA"),
    (9, "Aryan Raj", 115, 4, "VA"),
    (9, "David Kong", 115, 4, "OR"),
    (9, "Keenan Park", 115, 4, "CA"),
    (9, "Lucas Hinds", 115, 4, "TN"),
    (9, "Orion Phan", 115, 4, "CA"),
    (9, "Ray Menkov", 115, 4, "NH"),
    (9, "Thomas Amdur", 115, 4, "PA"),
    (9, "Leya Balayoghan", 113, 5, "WA"),
    (9, "Justin Ma", 112, 6, "VA"),
    (9, "Adam Yanco", 111, 7, "MA"),
    (9, "Alex Wang", 111, 7, "MD"),
    (9, "Eric Zou", 111, 7, "NY"),
    (9, "Mia Liu", 111, 7, "CA"),
    (9, "Neil Sriram", 111, 7, "NY"),
    (9, "Oliver Francois Watkins", 111, 7, "GA"),
    (9, "Soham Dam", 111, 7, "PA"),
    (9, "Sophie He", 111, 7, "MA"),
    (9, "Suhani Pahuja", 111, 7, "CA"),
    (9, "William Du", 111, 7, "TX"),
    (9, "Andrew Tsai", 110, 8, "NY"),
    (9, "Anna Tang", 110, 8, "MA"),
    (9, "Bhavin Dang", 110, 8, "AZ"),
    (9, "Clayton Song", 110, 8, "MA"),
    (9, "Crystal Huang", 110, 8, "CA"),
    (9, "Tyler Germain", 110, 8, "MA"),
    (9, "Aahan Mahakud", 109, 9, "NJ"),
    (9, "Andrey Kalashnikov", 108, 10, "MA"),
    (9, "Anika Patel", 108, 10, "CA"),
    (9, "Pranav Balasubramanian", 108, 10, "CA"),
    (9, "Albert Ding", 107, 11, "TN"),
    (9, "Andrew Feng", 107, 11, "PA"),
    (9, "Ayan Dalmia", 107, 11, "NJ"),
    (9, "Jianing Huang", 107, 11, "MA"),
    (9, "Mihir Gupta", 107, 11, "CA"),
    (9, "Siddharth Nair", 107, 11, "CT"),
    (9, "Yury Bychkov", 107, 11, "CA"),
    (9, "Anish Sankar", 106, 12, "MA"),
    (9, "Edward Feng", 106, 12, "CA"),
    (9, "Ekaansh Agrawal", 106, 12, "WA"),
    (9, "Isabel Wang", 106, 12, "CT"),
    (9, "Jeeho Lee", 106, 12, "CA"),
    (9, "Noah Kim", 106, 12, "MA"),
    (9, "Peter Karamanov", 106, 12, "NC"),
    (9, "Siming Chen", 106, 12, "MA"),
    (9, "Baixuan Chen", 105, 13, "CA"),
    (9, "Henry Chen", 105, 13, "IL"),
    (9, "Kai Marcelais", 105, 13, "WA"),
    (9, "Olivia Lee", 105, 13, "CA"),
    (9, "Rishi Gupta", 105, 13, "CA"),
    (9, "Rishi Salvi", 105, 13, "CA"),
    (9, "Shreya Sharma", 105, 13, "CA"),
    (9, "Tang Tang", 105, 13, "VA"),
    (9, "Utsav Lal", 105, 13, "CA"),
    (9, "Yohan Kim", 105, 13, "GA"),
    (9, "Charles Breeden", 103, 14, "CA"),
    (9, "Rhubyn Letuchy", 103, 14, "IL"),
    (9, "Shrihan Dasari", 103, 14, "TX"),
    (9, "Aman Kumar", 102, 15, "MA"),
    (9, "Audrey Jing", 102, 15, "NY"),
    (9, "Jessica Caruso", 102, 15, "GA"),
    (9, "Justin Lee", 102, 15, "CA"),
    (9, "Mark Menaker", 102, 15, "CA"),
    (9, "Rishit Agrawal", 102, 15, "CA"),
    (9, "Rithik Vir", 102, 15, "CA"),
    (9, "Zach Hagelberg", 102, 15, "WA"),
    (9, "Alim Utemisov", 101, 16, "CA"),
    (9, "Elaine Zeng", 101, 16, "IN"),
    (9, "Kabir Gupta", 101, 16, "CA"),
    (9, "Timothy Pan", 101, 16, "MA"),
    (9, "Aditya Yadav", 100, 17, "AZ"),
    (9, "Amelia Zhang", 100, 17, "CA"),
    (9, "Dhruv Mallick", 100, 17, "CA"),
    (9, "Haojun Wu", 100, 17, "CA"),
    (9, "Harry Park", 100, 17, "CA"),
    (9, "Ishaan Agarwal", 100, 17, "TX"),
    (9, "Mahita Penmetsa", 100, 17, "NC"),
    (9, "Renee Wang", 100, 17, "IL"),
    (9, "Siddharaj Gangwal", 100, 17, "NJ"),
    (9, "Trisha Manipatruni", 100, 17, "CA"),
    (9, "Michael Chen", 99, 18, "NC"),
    (9, "Andrew Kamin", 98, 19, "GA"),
    (9, "Paul Pan", 98, 19, "MA"),
    (9, "Alexis Tan", 97, 20, "GA"),
    (9, "Matthew Karp", 97, 20, "NY"),
    (9, "Nithin Ravikumar", 97, 20, "TX"),
    (9, "Rishit Avadhuta", 97, 20, "MA"),
    (9, "Shannon Xu", 97, 20, "NJ"),
    (9, "Yanlin Lu", 97, 20, "CA"),
    (9, "Zunaid Jafar", 97, 20, "GU"),
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
