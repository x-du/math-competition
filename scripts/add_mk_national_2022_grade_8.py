#!/usr/bin/env python3
"""
Add Math Kangaroo 2022 Grade 8 National Winners.
Source: https://mathkangaroo.org/mks/wp-content/uploads/2022/05/2022_Level-8_National-Winners.pdf
Resolves (name, state) via students.csv; adds new students as needed.
Do NOT merge students with same name in different states - match strictly on (name, state).
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2022" / "grade=8"

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

# grade, name, score, rank, state (from 2022 Level 8 National Winners PDF)
ROWS = [
    (8, "Adam Ge", 120, 1, "MA"),
    (8, "Adam Yanco", 120, 1, "MA"),
    (8, "Aishwarya Agrawal", 120, 1, "WA"),
    (8, "Alexander Sheffield", 120, 1, "NY"),
    (8, "Allan Yuan", 120, 1, "AL"),
    (8, "Elaine Zeng", 120, 1, "IN"),
    (8, "Eric Min", 120, 1, "OR"),
    (8, "Harini Venkatesh", 120, 1, "TX"),
    (8, "Jason Liu", 120, 1, "PA"),
    (8, "Kai Marcelais", 120, 1, "WA"),
    (8, "Kedaar Shankarnarayan", 120, 1, "NJ"),
    (8, "Plato Wong", 120, 1, "CA"),
    (8, "Shon Skarbnik", 120, 1, "CA"),
    (8, "Sohil Rathi", 120, 1, "CA"),
    (8, "Sophie He", 120, 1, "MA"),
    (8, "Sophie Hong", 120, 1, "IL"),
    (8, "Aahan Mahakud", 117, 2, "NJ"),
    (8, "Henry Chen", 117, 2, "IL"),
    (8, "Ishaan Agarwal", 117, 2, "TX"),
    (8, "Keenan Park", 117, 2, "CA"),
    (8, "Peter Karamanov", 117, 2, "NC"),
    (8, "Ryan Chung", 117, 2, "VA"),
    (8, "Aiden Yejoon Kim", 116, 3, "OK"),
    (8, "Baixuan Chen", 116, 3, "CA"),
    (8, "Luke Li", 116, 3, "MA"),
    (8, "Natalie Han", 116, 3, "MA"),
    (8, "Alexander Peev", 115, 4, "WA"),
    (8, "Anika Sivarasa", 115, 4, "MA"),
    (8, "Arush Goswami", 115, 4, "OR"),
    (8, "Aryan Agrawal", 115, 4, "WA"),
    (8, "Aryan Raj", 115, 4, "VA"),
    (8, "Bryant Wang", 115, 4, "CA"),
    (8, "Dharveen Suntheresen", 115, 4, "WA"),
    (8, "Ellen Kolesnikova", 115, 4, "GA"),
    (8, "Hayden Chen", 115, 4, "CA"),
    (8, "Ishaan Agarwal", 115, 4, "CA"),
    (8, "Ishika Shah", 115, 4, "CA"),
    (8, "Justin Li", 115, 4, "MD"),
    (8, "Leya Balayoghan", 115, 4, "WA"),
    (8, "Michael Iofin", 115, 4, "NY"),
    (8, "Michelle Nogin", 115, 4, "CA"),
    (8, "Shruti Arun", 115, 4, "CO"),
    (8, "Siddarth Suresh", 115, 4, "GA"),
    (8, "Soham Dam", 115, 4, "PA"),
    (8, "Tony Song", 115, 4, "MD"),
    (8, "Vishnu Mangipudi", 115, 4, "WA"),
    (8, "David Chen", 114, 5, "IL"),
    (8, "Ekaansh Agrawal", 114, 5, "WA"),
    (8, "Shimon Schlessinger", 114, 5, "CA"),
    (8, "Suvam Konar", 114, 5, "OH"),
    (8, "Krithik Prasad", 113, 6, "IL"),
    (8, "Yuna Cho", 113, 6, "GA"),
    (8, "Abhinav Bhagavan", 112, 7, "TX"),
    (8, "Aryan Garg", 112, 7, "VA"),
    (8, "Clayton Song", 112, 7, "MA"),
    (8, "Connor Zhao", 112, 7, "CA"),
    (8, "Gaurav Gupta", 112, 7, "CA"),
    (8, "Jaeyoon Kim", 112, 7, "VA"),
    (8, "Kai Lum", 112, 7, "CA"),
    (8, "Karthik Prasad", 112, 7, "IL"),
    (8, "Leonid Chernyakhovskiy", 112, 7, "CA"),
    (8, "Michael Chen", 112, 7, "NC"),
    (8, "Neil Sriram", 112, 7, "NY"),
    (8, "Noah Kim", 112, 7, "MA"),
    (8, "Oliver Francois Watkins", 112, 7, "GA"),
    (8, "Samanyu Ganesh", 112, 7, "GA"),
    (8, "Srinivas Vijaybabu", 112, 7, "NC"),
    (8, "Susie Lu", 112, 7, "WA"),
    (8, "Aaratrika Mondal", 111, 8, "MN"),
    (8, "Aarush Mane", 111, 8, "NJ"),
    (8, "Anish Sankar", 111, 8, "MA"),
    (8, "Anran Liu", 111, 8, "MA"),
    (8, "Arnav Dagar", 111, 8, "CA"),
    (8, "Brandon Hu", 111, 8, "VA"),
    (8, "Ertan Dogan", 111, 8, "MD"),
    (8, "Kai Lidzborski", 111, 8, "CA"),
    (8, "Kerry Luo", 111, 8, "NC"),
    (8, "Lev Strougov", 111, 8, "MA"),
    (8, "Mark Menaker", 111, 8, "CA"),
    (8, "Michael Antipov", 111, 8, "IL"),
    (8, "Michael Retakh", 111, 8, "NY"),
    (8, "Olivia Lee", 111, 8, "CA"),
    (8, "Owen Xuan", 111, 8, "WA"),
    (8, "Raahil Parikh", 111, 8, "MA"),
    (8, "Rishi Gupta", 111, 8, "CA"),
    (8, "Sachi Sharma", 111, 8, "NC"),
    (8, "Siddharth Nair", 111, 8, "CT"),
    (8, "Siming Chen", 111, 8, "MA"),
    (8, "William Gao", 111, 8, "CA"),
    (8, "Yashnil Mohanty", 111, 8, "CA"),
    (8, "Andrey Kalashnikov", 110, 9, "MA"),
    (8, "Arjun Agarwal", 110, 9, "OR"),
    (8, "Bhavin Dang", 110, 9, "AZ"),
    (8, "Katherine Liu", 110, 9, "OK"),
    (8, "Pranav Balasubramanian", 110, 9, "CA"),
    (8, "Shubhi Jain", 110, 9, "NJ"),
    (8, "Sohan Nelakudity", 109, 10, "CT"),
    (8, "Aadhya Shenoy", 108, 11, "CA"),
    (8, "Adelia Poyarkov", 108, 11, "CA"),
    (8, "Aiden Liu", 108, 11, "MD"),
    (8, "Alex Wang", 108, 11, "MD"),
    (8, "Amish Tyagi", 108, 11, "CA"),
    (8, "Ethan Qian-Tsuchida", 108, 11, "MA"),
    (8, "Jasper Ng", 108, 11, "CA"),
    (8, "Jessica Caruso", 108, 11, "GA"),
    (8, "Jonas Wilderman", 108, 11, "MA"),
    (8, "Matthew Kokhan", 108, 11, "WA"),
    (8, "Nikhil McGowan", 108, 11, "CA"),
    (8, "Paul Pan", 108, 11, "MA"),
    (8, "Aarav Nair", 107, 12, "IL"),
    (8, "Abir Bhatia", 107, 12, "CA"),
    (8, "Andrew Jo", 107, 12, "CA"),
    (8, "Arun Skanda Rebbapragada", 107, 12, "TX"),
    (8, "Asteris Ling", 107, 12, "CA"),
    (8, "Evan Zhang", 107, 12, "MD"),
    (8, "Kedar Vernekar", 107, 12, "TX"),
    (8, "Maja Vuletic", 107, 12, "CA"),
    (8, "Mia Liu", 107, 12, "CA"),
    (8, "Mikayil Mustafayev", 107, 12, "MA"),
    (8, "Naveen Talla", 107, 12, "NY"),
    (8, "Parth Dhaulakhandi", 107, 12, "CA"),
    (8, "Rishi Salvi", 107, 12, "CA"),
    (8, "Shomak Tan", 107, 12, "IL"),
    (8, "Allen John", 106, 13, "CA"),
    (8, "Ayan Dalmia", 106, 13, "NJ"),
    (8, "Eric Nie", 106, 13, "MA"),
    (8, "Harshil Nukala", 106, 13, "CA"),
    (8, "Kaden Zhao", 106, 13, "AZ"),
    (8, "Leo Yang", 106, 13, "NC"),
    (8, "Peter Kisselev", 106, 13, "VA"),
    (8, "Sowmya Erukulapati", 106, 13, "MO"),
    (8, "Timothy Pan", 106, 13, "MA"),
    (8, "Tyler Germain", 106, 13, "MA"),
    (8, "Aditya Sengupta", 105, 14, "WA"),
    (8, "Arnav Gupta", 105, 14, "VA"),
    (8, "Ava Chen", 105, 14, "CA"),
    (8, "Aarav Kumar", 104, 15, "NJ"),
    (8, "Arjun Joisha", 104, 15, "CA"),
    (8, "Eric Liao", 104, 15, "CA"),
    (8, "Pulak Agarwalla", 104, 15, "NC"),
    (8, "Thomas Ha", 104, 15, "MA"),
    (8, "Tomasz Czajkowski", 104, 15, "CA"),
    (8, "Zain Irfan", 104, 15, "MA"),
    (8, "Adhvay Karthikeyan", 103, 16, "MA"),
    (8, "Akshara Kumar", 103, 16, "NJ"),
    (8, "Alyssa Yu", 103, 16, "MD"),
    (8, "Ansh Thakkar", 103, 16, "CA"),
    (8, "Austin Shu", 103, 16, "CA"),
    (8, "Christopher Chor", 103, 16, "NH"),
    (8, "David He", 103, 16, "MD"),
    (8, "Eli Cui", 103, 16, "IL"),
    (8, "Jason Yao", 103, 16, "MD"),
    (8, "Nirvik Kasula", 103, 16, "CA"),
    (8, "Soham Bhattacharya", 103, 16, "CA"),
    (8, "Sophia Lin", 103, 16, "NY"),
    (8, "Utsav Lal", 103, 16, "CA"),
    (8, "William Xie", 103, 16, "CA"),
    (8, "Alisa Aleynikov", 102, 17, "NJ"),
    (8, "Gordon Wong", 102, 17, "CA"),
    (8, "Jacob Kohhayting", 102, 17, "FL"),
    (8, "Pranav Satapathy", 102, 17, "IL"),
    (8, "Raymond Menkov", 102, 17, "NH"),
    (8, "Rithik Vir", 102, 17, "CA"),
    (8, "Shrihan Dasari", 102, 17, "TX"),
    (8, "Sriaditya Vaddadi", 102, 17, "MA"),
    (8, "Yury Bychkov", 102, 17, "CA"),
    (8, "Aditya Shirgur", 101, 18, "CA"),
    (8, "Aparna Acharya", 101, 18, "CT"),
    (8, "Jianing Huang", 101, 18, "MA"),
    (8, "Lesia Zhurba", 101, 18, "MA"),
    (8, "Luke An", 101, 18, "PA"),
    (8, "Matthew Karp", 101, 18, "NY"),
    (8, "Sahaj Bhandari", 101, 18, "NJ"),
    (8, "Srishti Hazra", 101, 18, "NJ"),
    (8, "Albert Zhu", 100, 19, "VA"),
    (8, "Andrew Chen", 100, 19, "VA"),
    (8, "Cameron Ngai", 100, 19, "CA"),
    (8, "Gavin Warnakulasooriya", 100, 19, "MA"),
    (8, "Jamie Hosier", 100, 19, "MA"),
    (8, "Julian Kovalovsky", 100, 19, "MD"),
    (8, "Lawrence Pang", 100, 19, "CA"),
    (8, "Lulu Huang", 100, 19, "VA"),
    (8, "Rohan Rao", 100, 19, "NJ"),
    (8, "Rohit Barua", 100, 19, "NJ"),
    (8, "Shannon Xu", 100, 19, "NJ"),
    (8, "Sophie Huang", 100, 19, "MD"),
    (8, "Andrew Tsai", 99, 20, "NY"),
    (8, "Daniel Mezhirov", 99, 20, "MA"),
    (8, "Kyan Mui", 99, 20, "CA"),
    (8, "Nithin Ravikumar", 99, 20, "IL"),
    (8, "Rishit Rakapali", 99, 20, "CA"),
    (8, "Trisha Manipatruni", 99, 20, "CA"),
    (8, "William Fezzie", 99, 20, "MA"),
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
