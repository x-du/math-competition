#!/usr/bin/env python3
"""
Add Math Kangaroo 2023 Grade 8 (Level 8) National Winners.
Source: https://mathkangaroo.org/mks/wp-content/uploads/2023/05/2023_Level-8_National-Winners.pdf
Resolves (name, state) via students.csv; adds new students as needed.
2023 format: no national_percentile in source.
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2023" / "grade=8"

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

# grade, name, score, rank, state (VARYAN JAIN: Scottsdale AZ per Arizona Persian Cultural Center)
ROWS = [
    (8, "Akshay Chokshi", 120, 1, "IL"),
    (8, "Anshul Mantri", 120, 1, "OR"),
    (8, "Avery Xu", 120, 1, "NY"),
    (8, "Daniel David", 120, 1, "MA"),
    (8, "Evan Zhang", 120, 1, "PA"),
    (8, "Jevin Xu", 120, 1, "VA"),
    (8, "Michael Mirkin", 120, 1, "MA"),
    (8, "Timothy Chen", 120, 1, "CA"),
    (8, "Varun Gadi", 120, 1, "GA"),
    (8, "Vikram Goudar", 120, 1, "VA"),
    (8, "Atticus Masuzawa", 117, 2, "CA"),
    (8, "Harish Loghashankar", 117, 2, "CA"),
    (8, "Nathan Mei", 117, 2, "MI"),
    (8, "Solon Xia", 117, 2, "KS"),
    (8, "Thomas Isernhagen", 117, 2, "NJ"),
    (8, "Anirudh Sengupta", 116, 3, "NC"),
    (8, "Austin James Candidato", 116, 3, "NY"),
    (8, "Connor Kong", 116, 3, "CA"),
    (8, "Connor Leong", 116, 3, "CA"),
    (8, "Curtis Wu", 116, 3, "MA"),
    (8, "Edward Zhang", 116, 3, "CA"),
    (8, "Ethan Guo", 116, 3, "MD"),
    (8, "Gina Li", 116, 3, "MA"),
    (8, "Jack Lu", 116, 3, "NY"),
    (8, "Mason Boucher", 116, 3, "MD"),
    (8, "Mihir Busani", 116, 3, "MO"),
    (8, "Rehan Babu", 116, 3, "CA"),
    (8, "Varyan Jain", 116, 3, "AZ"),
    (8, "Zachary Wong", 116, 3, "NJ"),
    (8, "Annabel Rong", 115, 4, "GA"),
    (8, "Jacob Khohayting", 115, 4, "FL"),
    (8, "Michael Jian", 115, 4, "CA"),
    (8, "Shamik Khowala", 115, 4, "CA"),
    (8, "Ashmit Arasada", 114, 5, "CA"),
    (8, "Harry Gao", 113, 6, "NY"),
    (8, "Lucas Cai", 113, 6, "CA"),
    (8, "Anand Swaroop", 112, 7, "MA"),
    (8, "Anish Kodali", 112, 7, "TN"),
    (8, "Charles Huang", 112, 7, "CA"),
    (8, "Christopher Wang", 112, 7, "MD"),
    (8, "Jason Yin", 112, 7, "NY"),
    (8, "Kristiyan Kurtev", 112, 7, "CA"),
    (8, "Lucas Park", 112, 7, "CA"),
    (8, "Neil Dutta", 112, 7, "MA"),
    (8, "Paul Harmon", 112, 7, "MT"),
    (8, "Sarah Li", 112, 7, "VA"),
    (8, "Yixuan Li", 112, 7, "MD"),
    (8, "Aditya Jagavkar", 111, 8, "NJ"),
    (8, "Aniket Mangalampalli", 111, 8, "CA"),
    (8, "Anthony Wang", 111, 8, "NV"),
    (8, "Graham Hoggan", 111, 8, "CA"),
    (8, "Jasmine Li", 111, 8, "CA"),
    (8, "Kyle Chian", 111, 8, "CA"),
    (8, "Michael Pylypovych", 111, 8, "NJ"),
    (8, "Nana Kim", 111, 8, "GA"),
    (8, "Platon Gorkavy", 111, 8, "MA"),
    (8, "Rajarshi Mandal", 111, 8, "MA"),
    (8, "Sameer Nagarkatti", 111, 8, "MA"),
    (8, "Soham Pattnaik", 111, 8, "VA"),
    (8, "Tahmin Uddin", 111, 8, "MA"),
    (8, "William Liu", 111, 8, "CA"),
    (8, "Yixuan Xu", 111, 8, "WA"),
    (8, "Ziyao Ma", 111, 8, "MA"),
    (8, "Kesav Kalanidhi", 110, 9, "NC"),
    (8, "Pranav Sivakumar", 110, 9, "CA"),
    (8, "Abhinav Eadhara", 108, 10, "VA"),
    (8, "Harry Furst", 108, 10, "CA"),
    (8, "Jason Lee", 108, 10, "NJ"),
    (8, "Rishik Shenolikar", 108, 10, "MD"),
    (8, "Shaurya Chauhan", 108, 10, "CA"),
    (8, "Somil Sarode", 108, 10, "CA"),
    (8, "Theenash Sengupta", 108, 10, "CA"),
    (8, "Aarav Ashwani", 107, 11, "CA"),
    (8, "Alice Luo", 107, 11, "CA"),
    (8, "Anthony Mokhov", 107, 11, "CA"),
    (8, "Ethan Cao", 107, 11, "CA"),
    (8, "Jason Lee", 107, 11, "CA"),
    (8, "Jennifer Wang", 107, 11, "IN"),
    (8, "Jessica Hsieh", 107, 11, "MD"),
    (8, "Krish Jha", 107, 11, "WA"),
    (8, "Nathan Ye", 107, 11, "OR"),
    (8, "Paxton Lin", 107, 11, "CA"),
    (8, "Roy Wang", 107, 11, "IL"),
    (8, "Vlad Vynarchuk", 107, 11, "MA"),
    (8, "Zachary Cha", 107, 11, "CA"),
    (8, "Alexander Ordukhanyan", 106, 12, "NY"),
    (8, "Caroline Huang", 106, 12, "GA"),
    (8, "Jai Bindlish", 106, 12, "WA"),
    (8, "Julia Salamacha", 106, 12, "CA"),
    (8, "Kaartic Muralidharan", 106, 12, "PA"),
    (8, "Max Xie", 106, 12, "WA"),
    (8, "Narnia Poddar", 106, 12, "NY"),
    (8, "Neel Chellapilla", 106, 12, "CA"),
    (8, "Samuel Kingston", 106, 12, "KY"),
    (8, "Timofey Gafurov", 106, 12, "VA"),
    (8, "Vatsal Srivastava", 106, 12, "CA"),
    (8, "Anray Sheng", 105, 13, "MA"),
    (8, "Arkar Tan", 105, 13, "CA"),
    (8, "Rohith Thomas", 105, 13, "CO"),
    (8, "Ruijing Tang", 105, 13, "IL"),
    (8, "William Hong", 105, 13, "CA"),
    (8, "Angela Jing", 104, 14, "NY"),
    (8, "Sophia Zhu", 104, 14, "WA"),
    (8, "Aarush Prasad", 103, 15, "CA"),
    (8, "Aiden Tretyak", 103, 15, "IL"),
    (8, "Ansh Gupta", 103, 15, "VA"),
    (8, "Anshul Raghav", 103, 15, "WA"),
    (8, "Atharv Joshi", 103, 15, "MA"),
    (8, "Brian Sun", 103, 15, "MA"),
    (8, "Derek Peng", 103, 15, "NJ"),
    (8, "Naaisha Agarwal", 103, 15, "MA"),
    (8, "Navya Jain", 103, 15, "WA"),
    (8, "Parsa Adhami", 103, 15, "SC"),
    (8, "Samhitha Kamatala", 103, 15, "IL"),
    (8, "Vihaan Paliwal", 103, 15, "OR"),
    (8, "Abhrottha Roy", 102, 16, "MA"),
    (8, "Avishi Anurag", 102, 16, "VA"),
    (8, "Cooper Ho", 102, 16, "NY"),
    (8, "Derek Zhao", 102, 16, "OR"),
    (8, "Jeffrey Dong", 102, 16, "MA"),
    (8, "Jiaxin Xu", 102, 16, "IL"),
    (8, "Joseph Franklin", 102, 16, "NC"),
    (8, "Mahi Kohli", 102, 16, "KS"),
    (8, "Nikhil Tamvada", 102, 16, "CA"),
    (8, "Oscar Lee", 102, 16, "IL"),
    (8, "Raghav Arun", 102, 16, "NC"),
    (8, "Rayyan Ahmed Siddiq", 102, 16, "MA"),
    (8, "Revanth Raparla", 102, 16, "TX"),
    (8, "Rohan Kommareddy", 102, 16, "CA"),
    (8, "Rushil Yeole", 102, 16, "MI"),
    (8, "Sadie Enright", 102, 16, "RI"),
    (8, "Stefan Donisa", 102, 16, "IL"),
    (8, "Summer Chu", 102, 16, "NC"),
    (8, "Theeran Sathish Kumar", 102, 16, "CA"),
    (8, "Victor Wang", 102, 16, "MD"),
    (8, "Vishnu Mukku", 102, 16, "CT"),
    (8, "Arden Peng", 101, 17, "MN"),
    (8, "Daniel Vaidhyan", 101, 17, "CA"),
    (8, "Naoki Matsuda", 101, 17, "CA"),
    (8, "Paul Norberg", 101, 17, "CA"),
    (8, "Poorva Khambekar", 101, 17, "CA"),
    (8, "Richard Sun", 101, 17, "CA"),
    (8, "Sohum Uttamchandani", 101, 17, "CA"),
    (8, "Alena Kutsuk", 100, 18, "CA"),
    (8, "Doyoon Lee", 100, 18, "CA"),
    (8, "Magaranth Rajkumar", 100, 18, "IL"),
    (8, "Ryder Morton", 100, 18, "MA"),
    (8, "Shripriya Kalbhavi", 100, 18, "CA"),
    (8, "Srijith Abhyuday Sathyanarayanan", 100, 18, "CA"),
    (8, "Akash Krothapalli", 99, 19, "WA"),
    (8, "Jack Iyer", 99, 19, "PA"),
    (8, "Jacob Peyghambarian", 99, 19, "UT"),
    (8, "Kaylee Zhao", 99, 19, "AL"),
    (8, "Rachel Shuai", 99, 19, "FL"),
    (8, "Rohan Danda", 99, 19, "MA"),
    (8, "Sanya Doshi", 99, 19, "WA"),
    (8, "Shriyadita De", 99, 19, "MD"),
    (8, "Aidan Tan", 98, 20, "MA"),
    (8, "Alan Sai", 98, 20, "MD"),
    (8, "Alex Kim", 98, 20, "CA"),
    (8, "Aryan Mootakoduru", 98, 20, "MA"),
    (8, "Atharv Dirisala", 98, 20, "CA"),
    (8, "Cavon Hajimiri", 98, 20, "CA"),
    (8, "Jihoo Won", 98, 20, "CA"),
    (8, "Max Malyk", 98, 20, "WI"),
    (8, "Maxwell Lisuwandi", 98, 20, "MA"),
    (8, "Nicholas Kim", 98, 20, "NJ"),
    (8, "Nitinreddy Vaka", 98, 20, "CA"),
    (8, "Noah Nixon", 98, 20, "TN"),
    (8, "Taison Scofield", 98, 20, "MN"),
    (8, "Vaibhav Varadha", 98, 20, "DE"),
    (8, "Vasu Ganesa", 98, 20, "CA"),
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
