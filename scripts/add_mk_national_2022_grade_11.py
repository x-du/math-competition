#!/usr/bin/env python3
"""
Add Math Kangaroo 2022 Grade 11 National Winners.
Source: https://mathkangaroo.org/mks/wp-content/uploads/2022/05/2022_Level-11_National-Winners.pdf
Resolves (name, state) via students.csv; adds new students as needed.
Do NOT merge students with same name in different states - match strictly on (name, state).
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2022" / "grade=11"

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

# grade, name, score, rank, state (from 2022 Level 11 National Winners PDF)
ROWS = [
    (11, "Alan Kappler", 120, 1, "OR"),
    (11, "Alan Vladimiroff", 120, 1, "VA"),
    (11, "Aman Jain", 120, 1, "CA"),
    (11, "Arul Mazumder", 120, 1, "MA"),
    (11, "Kaden Nguyen", 120, 1, "CA"),
    (11, "Nicole Shen", 120, 1, "CA"),
    (11, "Nilay Mishra", 120, 1, "CA"),
    (11, "Ritvik Garg", 120, 1, "MA"),
    (11, "Sai Konkimalla", 120, 1, "AZ"),
    (11, "Sharvaa Selvan", 120, 1, "FL"),
    (11, "Sophia Sun", 120, 1, "MD"),
    (11, "Suyash Pandit", 120, 1, "OR"),
    (11, "Ari Wang", 116, 2, "CO"),
    (11, "Arianna Cao", 116, 2, "CA"),
    (11, "Asher Wu", 116, 2, "WA"),
    (11, "Darsh Patel", 116, 2, "NV"),
    (11, "David Magidson", 116, 2, "WA"),
    (11, "Jake Langlois", 116, 2, "PA"),
    (11, "Siddharth Doppalapudi", 116, 2, "AL"),
    (11, "William Du", 116, 2, "MA"),
    (11, "Alexey Tatarinov", 115, 3, "PA"),
    (11, "Arul Kolla", 115, 3, "CA"),
    (11, "Chun Yeung Wong", 115, 3, "NY"),
    (11, "Guanzhen Song", 115, 3, "CA"),
    (11, "Julia Kozak", 115, 3, "NY"),
    (11, "Kavan Doctor", 115, 3, "CA"),
    (11, "Lisa Fung", 115, 3, "CA"),
    (11, "Megan Gu", 115, 3, "MD"),
    (11, "Nikhil Mudumbi", 115, 3, "NJ"),
    (11, "Nividh Singh", 115, 3, "OR"),
    (11, "Noah Shi", 115, 3, "WA"),
    (11, "Riya Gupta", 115, 3, "CA"),
    (11, "Shishir Vargheese", 115, 3, "KS"),
    (11, "Tanmay Gupta", 115, 3, "MA"),
    (11, "Vishal Thyagarajan", 115, 3, "TX"),
    (11, "Vivek Vallurupalli", 115, 3, "MA"),
    (11, "Jettae Schroff", 113, 4, "CA"),
    (11, "Amruta Dharmapurikar", 112, 5, "CA"),
    (11, "Daniel Ma", 112, 5, "IL"),
    (11, "Ramsey Makan", 112, 5, "FL"),
    (11, "Ananth Kashyap", 111, 6, "PA"),
    (11, "Artem Torubarov", 111, 6, "NJ"),
    (11, "David Rubin", 111, 6, "NY"),
    (11, "Mark Neumann", 111, 6, "CA"),
    (11, "Megan Davi", 111, 6, "NV"),
    (11, "Richard Yu", 111, 6, "GA"),
    (11, "Victor Donchenko", 111, 6, "CA"),
    (11, "Victor Li", 111, 6, "OR"),
    (11, "Baomo Zhu", 110, 7, "CA"),
    (11, "Daniel Zhao", 110, 7, "AL"),
    (11, "Richard Zhu", 110, 7, "CA"),
    (11, "Ayan Bhatia", 108, 8, "CA"),
    (11, "Daniel Long", 108, 8, "NJ"),
    (11, "Asanshay Gupta", 107, 9, "GA"),
    (11, "Daniel (Dawn) McCrorey", 107, 9, "WA"),
    (11, "Manan Vora", 107, 9, "WA"),
    (11, "Duong Le", 106, 10, "NY"),
    (11, "Isaac Mitchell", 106, 10, "CO"),
    (11, "Keaton Xu", 106, 10, "KS"),
    (11, "Maya Smith", 106, 10, "MA"),
    (11, "Apoorva Talwalkar", 105, 11, "CA"),
    (11, "Yiran Wang", 105, 11, "CA"),
    (11, "Shashwat Rao", 104, 12, "VA"),
    (11, "Kevin Yao", 103, 13, "MD"),
    (11, "Krishna Grandhe", 103, 13, "TX"),
    (11, "William Opich", 103, 13, "NY"),
    (11, "Alisha Paul", 102, 14, "CT"),
    (11, "Andrew Jin", 102, 14, "CA"),
    (11, "Charles Chen", 102, 14, "CA"),
    (11, "Lynn Tao", 102, 14, "VA"),
    (11, "Madeline Jiang", 102, 14, "MA"),
    (11, "Riley Bonner", 102, 14, "CA"),
    (11, "Alexandra Levinshteyn", 101, 15, "MN"),
    (11, "Casey Kong", 101, 15, "KS"),
    (11, "Colin Colbert", 101, 15, "NV"),
    (11, "Phoebe Ong", 101, 15, "CA"),
    (11, "Riley Chin", 101, 15, "NH"),
    (11, "Stewart Kwok", 101, 15, "CA"),
    (11, "Yash Agrawal", 101, 15, "FL"),
    (11, "Alexander Khilko", 100, 16, "CT"),
    (11, "Aswath Karai", 100, 16, "MI"),
    (11, "Joshua Sujo", 100, 16, "CA"),
    (11, "Stephanie Han", 100, 16, "MI"),
    (11, "Thomas Breydo", 100, 16, "NY"),
    (11, "Edward Ju", 99, 17, "GU"),
    (11, "Francis Wang", 99, 17, "MI"),
    (11, "Qinzi (Wendy) Wang", 99, 17, "CA"),
    (11, "David Zhukovsky", 98, 18, "MA"),
    (11, "Kimberly You", 98, 18, "MI"),
    (11, "Rebecca Serodio", 98, 18, "MA"),
    (11, "Samarth Pusegaonkar", 98, 18, "CA"),
    (11, "Srikar Mallajosyula", 98, 18, "MA"),
    (11, "Anna Gu", 97, 19, "MD"),
    (11, "Constantin Matros", 97, 19, "PA"),
    (11, "Elina Lee", 97, 19, "MD"),
    (11, "Mihir Nagarkatti", 97, 19, "MA"),
    (11, "Mollee Ye", 97, 19, "NH"),
    (11, "Nathan Wang", 97, 19, "NV"),
    (11, "Victor Proykov", 97, 19, "NV"),
    (11, "Eunyul Kim", 96, 20, "CA"),
    (11, "Patrick Kulaga", 96, 20, "IL"),
    (11, "Samantha Wu", 96, 20, "MD"),
    (11, "Sean Lim", 96, 20, "NY"),
    (11, "Shaher Naser", 96, 20, "NJ"),
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
