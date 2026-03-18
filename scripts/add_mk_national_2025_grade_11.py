#!/usr/bin/env python3
"""
Add Math Kangaroo 2025 Grade 11 National Winners.
Resolves (name, state) via students.csv; adds new students as needed.
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2025" / "grade=11"

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

# grade, name, score, rank, percentile, center, city, state
ROWS = [
    (11, "Allan Yuan", 120, 1, 99.3, "Birmingham Math Academy", "Birmingham", "AL"),
    (11, "Jason Liu", 120, 1, 99.3, "World Wonder Education", "PITTSBURGH", "PA"),
    (11, "Lucas Hinds", 120, 1, 99.3, "MMC&M ONLINE", "Kingston", "TN"),
    (11, "Siddharth Nair", 116, 2, 99, "Mathico at St. Gregory's Learning Hall", "White Plains", "NY"),
    (11, "Adam Yanco", 115, 3, 96.6, "MathAltitude School of Mathematics", "Worcester", "MA"),
    (11, "Aishwarya Agrawal", 115, 3, 96.6, "Washington State REMOTE", "", "WA"),
    (11, "Alexander Sheffield", 115, 3, 96.6, "Basis Independent Manhattan Upper", "New York", "NY"),
    (11, "Andrey Kalashnikov", 115, 3, 96.6, "TR Consulting Group Inc", "Newton", "MA"),
    (11, "Arnav Adepu", 115, 3, 96.6, "MindzQ Education", "Fair Lawn", "NJ"),
    (11, "Kavin Nathan", 115, 3, 96.6, "BrightPath Academy", "Coppell", "TX"),
    (11, "Tyler Germain", 115, 3, 96.6, "RSM Newton", "Newton", "MA"),
    (11, "Wonjun Choi", 112, 4, 96.3, "Asheville School", "Asheville", "NC"),
    (11, "Evan Zhang", 111, 5, 95.2, "CCACC Academy Center", "Rockville", "MD"),
    (11, "Haydn Chan", 111, 5, 95.2, "Illinois State REMOTE", "", "IL"),
    (11, "Kefei Liao", 111, 5, 95.2, "AITE Institute", "Irvine", "CA"),
    (11, "Aiden Yejoon Kim", 110, 6, 91.5, "OSU Stillwater", "Stillwater", "OK"),
    (11, "Andrew Feng", 110, 6, 91.5, "Carnegie Mellon University", "Pittsburgh", "PA"),
    (11, "Anish Sankar", 110, 6, 91.5, "RSM Wellesley", "Wellesley Hills", "MA"),
    (11, "Aryan Raj", 110, 6, 91.5, "RSM Herndon", "Herndon", "VA"),
    (11, "Baixuan Chen", 110, 6, 91.5, "RSM Irvine", "Irvine", "CA"),
    (11, "Edward Feng", 110, 6, 91.5, "Stratford Preparatory Blackford", "San Jose", "CA"),
    (11, "Gordon Cheng", 110, 6, 91.5, "Gigamind Explorer Education San Mateo", "San Mateo", "CA"),
    (11, "Harini Venkatesh", 110, 6, 91.5, "Math Rangers at Brentwood Library", "Brentwood", "NH"),
    (11, "Leya Balayoghan", 110, 6, 91.5, "Prime Factor at Overlake", "Redmond", "WA"),
    (11, "Samanyu Ganesh", 110, 6, 91.5, "Emory University", "Atlanta", "GA"),
    (11, "Tony Song", 110, 6, 91.5, "CCACC Academy Center", "Rockville", "MD"),
    (11, "Clemens Brass", 108, 7, 91.2, "RSM Scarsdale", "Scarsdale", "NY"),
    (11, "Ayan Dalmia", 107, 8, 90.5, "New Jersey Enrichment Academy", "Millburn", "NJ"),
    (11, "Kedaar Shankarnarayan", 107, 8, 90.5, "RSM Livingston", "Livingston", "NJ"),
    (11, "Krithik Prasad", 106, 9, 89.1, "RSM Naperville", "Naperville", "IL"),
    (11, "Michelle Nogin", 106, 9, 89.1, "California State University Fresno", "Fresno", "CA"),
    (11, "Siddharth Pasari", 106, 9, 89.1, "RSM Manhattan Upper East Side ONLINE", "New York", "NY"),
    (11, "Soham Dam", 106, 9, 89.1, "Carnegie Mellon University", "Pittsburgh", "PA"),
    (11, "Arush Goswami", 105, 10, 87.1, "Sunshine Elite", "Beaverton", "OR"),
    (11, "Bhavin Dang", 105, 10, 87.1, "School of Mathematical and Statistical Sciences ASU", "Tempe", "AZ"),
    (11, "Henry Chen", 105, 10, 87.1, "Adventures with Mr. Math REMOTE", "Oak Brook", "IL"),
    (11, "Ishaan Nagireddi", 105, 10, 87.1, "Hendricks Middle School", "Cumming", "GA"),
    (11, "Jiajun Luo", 105, 10, 87.1, "RSM Stamford", "Greenwich", "CT"),
    (11, "Serena Feng", 105, 10, 87.1, "AITE Institute", "Irvine", "CA"),
    (11, "Ellen Kolesnikova", 103, 11, 86.7, "Emory University", "Atlanta", "GA"),
    (11, "Alexa Chang", 102, 12, 84.7, "Caltech", "Pasadena", "CA"),
    (11, "Kai Marcelais", 102, 12, 84.7, "Mathnasium of Redmond", "Redmond", "WA"),
    (11, "Plato Wong", 102, 12, 84.7, "MathSeed Fremont Stevenson", "Fremont", "CA"),
    (11, "Yiting Zhu", 102, 12, 84.7, "AITE Institute", "Irvine", "CA"),
    (11, "Yuting Liu", 102, 12, 84.7, "Sunshine Academy Vienna", "Vienna", "VA"),
    (11, "Zarif Ahanaf", 102, 12, 84.7, "Carnegie Mellon University", "Pittsburgh", "PA"),
    (11, "Brandon Hu", 101, 13, 82.3, "Blacksburg Chinese School", "Blacksburg", "VA"),
    (11, "Philemon Kuo", 101, 13, 82.3, "Russian School of Mathematics Chevy Chase", "Chevy Chase", "MD"),
    (11, "Raymond Menkov", 101, 13, 82.3, "Hanover High School ONLINE", "Hanover", "NH"),
    (11, "Rithik Vir", 101, 13, 82.3, "Random Math", "Cupertino", "CA"),
    (11, "Ritvik Ranjan", 101, 13, 82.3, "Emory University", "Atlanta", "GA"),
    (11, "Roy Wang", 101, 13, 82.3, "Champaign Urbana Math Circle ONLINE", "Urbana", "IL"),
    (11, "Samarth Das", 101, 13, 82.3, "RSM Plano", "Plano", "TX"),
    (11, "Albert Ding", 100, 14, 81.6, "Cordova Branch Library", "Cordova", "TN"),
    (11, "Jessica Wu", 100, 14, 81.6, "Ann Hua Chinese School ONLINE", "Ann Arbor", "MI"),
    (11, "Michael Chen", 99, 15, 81.3, "Science & Math Interactive Learning Experience", "Raleigh", "NC"),
    (11, "Redger Xu", 98, 16, 81, "Stratford Preparatory Blackford", "San Jose", "CA"),
    (11, "Allen Li", 97, 17, 78.6, "NEST+m", "New York", "NY"),
    (11, "Brian Tay", 97, 17, 78.6, "RSM Herndon", "Herndon", "VA"),
    (11, "Daniel Liu", 97, 17, 78.6, "AITE Institute", "Irvine", "CA"),
    (11, "Karthik Prasad", 97, 17, 78.6, "RSM Naperville", "Naperville", "IL"),
    (11, "Mihir Kotbagi", 97, 17, 78.6, "RSM San Jose Westgate", "San Jose", "CA"),
    (11, "Nathan Chan", 97, 17, 78.6, "RSM Irvine", "Irvine", "CA"),
    (11, "Prithvi Anickode", 97, 17, 78.6, "Scottsdale MMRA", "Scottsdale", "AZ"),
    (11, "Daniel Mezhirov", 96, 18, 77.2, "Math & More Studio", "Lexington", "MA"),
    (11, "Darius Cleaver", 96, 18, 77.2, "Francis W. Parker School", "Chicago", "IL"),
    (11, "Justin Li", 96, 18, 77.2, "Russian School of Mathematics Chevy Chase", "Chevy Chase", "MD"),
    (11, "Rachit Sakurikar", 96, 18, 77.2, "RSM Edison", "Edison", "NJ"),
    (11, "Akshara Kumar", 95, 19, 75.9, "New Jersey Enrichment Academy", "Millburn", "NJ"),
    (11, "Sophie Huang", 95, 19, 75.9, "CCACC Academy Center", "Rockville", "MD"),
    (11, "Yifan Sheng", 95, 19, 75.9, "Think Academy U.S. ONLINE", "San Jose", "CA"),
    (11, "Zhuoqun Yang", 95, 19, 75.9, "iLearning Bayside ONLINE", "Bayside", "NY"),
    (11, "Pranav Balasubramanian", 93, 20, 75.5, "AlphaStar Academy", "Cupertino", "CA"),
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

    for grade, name, score, rank, pct, center, city, state_abbrev in ROWS:
        state = STATE_ABBREV_TO_FULL.get(state_abbrev.strip().upper(), state_abbrev.strip())
        name_clean = name.strip()
        key = (name_clean.lower(), state)
        row = key_to_row.get(key)
        if row:
            out_rows.append((row["student_id"], row["student_name"], state, grade, score, rank, pct))
            continue

        sid = next_id
        next_id += 1
        key_to_row[key] = {"student_id": sid, "student_name": name_clean, "state": state}
        new_students.append({
            "student_id": sid, "student_name": name_clean, "state": state,
            "team_ids": "", "alias": "", "gender": "", "grade_in_2026": ""
        })
        out_rows.append((sid, name_clean, state, grade, score, rank, pct))

    # Append new students
    if new_students:
        with open(STUDENTS_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["student_id", "student_name", "state", "team_ids", "alias", "gender", "grade_in_2026"], extrasaction="ignore")
            for r in new_students:
                w.writerow(r)
        print(f"Added {len(new_students)} new students")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "results.csv"
    # Compute fractional mcp_rank for ties (average of rank range)
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
