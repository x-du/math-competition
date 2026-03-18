#!/usr/bin/env python3
"""
Add Math Kangaroo 2022 Grade 7 National Winners.
Source: https://mathkangaroo.org/mks/wp-content/uploads/2022/05/2022_Level-7_National-Winners.pdf
Resolves (name, state) via students.csv; adds new students as needed.
Do NOT merge students with same name in different states - match strictly on (name, state).
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2022" / "grade=7"

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

# grade, name, score, rank, state (from 2022 Level 7 National Winners PDF)
ROWS = [
    (7, "Akshay Chokshi", 120, 1, "MA"),
    (7, "Harish Loghashankar", 120, 1, "CA"),
    (7, "Jason Lee", 120, 1, "NJ"),
    (7, "Rajarshi Mandal", 120, 1, "MA"),
    (7, "Rehan Babu", 120, 1, "CA"),
    (7, "Selena Ge", 120, 1, "MA"),
    (7, "Shailen Shah", 120, 1, "NJ"),
    (7, "Solon Xia", 120, 1, "KS"),
    (7, "Varun Gadi", 120, 1, "GA"),
    (7, "Advik Kishore", 117, 2, "TX"),
    (7, "Alexandra Zykova", 117, 2, "CA"),
    (7, "Harry Gao", 117, 2, "NY"),
    (7, "Jeremy Yang", 117, 2, "MD"),
    (7, "Sohini Mukherjee", 117, 2, "WA"),
    (7, "Vihaan Paliwal", 117, 2, "OR"),
    (7, "Anirudh Sengupta", 116, 3, "NC"),
    (7, "Eric Zhang", 116, 3, "IL"),
    (7, "Guillem Elizalde", 116, 3, "NH"),
    (7, "Jai Mukherjee", 116, 3, "WA"),
    (7, "Sriyan Yarlagadda", 116, 3, "NJ"),
    (7, "Taarun Ganesh", 116, 3, "VA"),
    (7, "Abhrottha Roy", 115, 4, "MA"),
    (7, "Anand Swaroop", 115, 4, "MA"),
    (7, "Anshul Mantri", 115, 4, "OR"),
    (7, "Austin James Candidato", 115, 4, "NY"),
    (7, "Connor Leong", 115, 4, "CA"),
    (7, "Daniel David", 115, 4, "MA"),
    (7, "Gentry Thatcher", 115, 4, "MA"),
    (7, "Kesav Kalanidhi", 115, 4, "NC"),
    (7, "Kristiyan Kurtev", 115, 4, "CA"),
    (7, "Leo Elieson", 115, 4, "WA"),
    (7, "Max Xie", 115, 4, "WA"),
    (7, "Prince Aditya Rohatgi", 115, 4, "CA"),
    (7, "Rohan Danda", 115, 4, "MA"),
    (7, "Vikram Goudar", 115, 4, "VA"),
    (7, "Zukhil Subramanian", 115, 4, "CA"),
    (7, "Jacob Wu", 114, 5, "CA"),
    (7, "Amber Weng", 113, 6, "MD"),
    (7, "Michael Mirkin", 113, 6, "MA"),
    (7, "Michael Tang", 113, 6, "CA"),
    (7, "Nikhil Byrapuram", 113, 6, "MA"),
    (7, "Tahmin Uddin", 113, 6, "MA"),
    (7, "William Wu", 113, 6, "VA"),
    (7, "Alena Kutsuk", 112, 7, "CA"),
    (7, "Anthony Wang", 112, 7, "NV"),
    (7, "Curtis Wu", 112, 7, "MA"),
    (7, "Dou Lai", 112, 7, "IL"),
    (7, "Evander Protopapas", 112, 7, "NY"),
    (7, "Hanyu Zhang", 112, 7, "CA"),
    (7, "Maria Tzanova", 112, 7, "NY"),
    (7, "Neel Jindal", 112, 7, "CA"),
    (7, "Raghav Arun", 112, 7, "NC"),
    (7, "Teddy Hsu", 112, 7, "MA"),
    (7, "Vlad Vynarchuk", 112, 7, "MA"),
    (7, "Ziyao Ma", 112, 7, "MA"),
    (7, "Anish Kodali", 111, 8, "TN"),
    (7, "Avery Xu", 111, 8, "NY"),
    (7, "Krivi Partani", 111, 8, "NJ"),
    (7, "Lucas Park", 111, 8, "CA"),
    (7, "Michael Jian", 111, 8, "CA"),
    (7, "Nathan Mei", 111, 8, "MI"),
    (7, "Nicholas Wang", 111, 8, "CA"),
    (7, "Paul Norberg", 111, 8, "CA"),
    (7, "Syna Goyal", 111, 8, "NJ"),
    (7, "Tanvi Varangaonkar", 111, 8, "WA"),
    (7, "Taran Ajith", 111, 8, "CA"),
    (7, "Twisha Sharma", 111, 8, "CA"),
    (7, "Varyan Jain", 111, 8, "AZ"),
    (7, "Yixuan Li", 111, 8, "MD"),
    (7, "Annabel Rong", 110, 9, "GA"),
    (7, "Arnav Prabhudesai", 110, 9, "TX"),
    (7, "Christopher Wang", 110, 9, "MD"),
    (7, "Darsh Maheshwari", 110, 9, "CA"),
    (7, "Ella Fang", 110, 9, "IL"),
    (7, "Hannah Thomas", 110, 9, "NH"),
    (7, "Joshua Liu", 110, 9, "CO"),
    (7, "Levi Gould", 110, 9, "MN"),
    (7, "Mihir Busani", 110, 9, "MO"),
    (7, "Yixuan Xu", 110, 9, "WA"),
    (7, "Rafael Ptashny", 109, 10, "NJ"),
    (7, "Anika Patel", 108, 11, "CA"),
    (7, "Ayush Ayyagari", 108, 11, "MA"),
    (7, "David Wang", 108, 11, "MD"),
    (7, "Dylan Wang", 108, 11, "CA"),
    (7, "Eric Mu", 108, 11, "CA"),
    (7, "Lucas Lum", 108, 11, "CA"),
    (7, "Michael Pylypovych", 108, 11, "NJ"),
    (7, "Nathaniel Lee", 108, 11, "CA"),
    (7, "Samuel Kingston", 108, 11, "KY"),
    (7, "Zachary Cha", 108, 11, "CA"),
    (7, "Aalok Pathak", 107, 12, "NJ"),
    (7, "Aditya Jagavkar", 107, 12, "NJ"),
    (7, "Avishi Anurag", 107, 12, "VA"),
    (7, "Leeoz Nebat", 107, 12, "NV"),
    (7, "Melody Ma", 107, 12, "KS"),
    (7, "Yudhish Kumar", 107, 12, "WA"),
    (7, "Aditya Singla", 106, 13, "CA"),
    (7, "Akash Krothapalli", 106, 13, "WA"),
    (7, "Atticus Masuzawa", 106, 13, "CA"),
    (7, "Evan Zhang", 106, 13, "PA"),
    (7, "Harry Furst", 106, 13, "CA"),
    (7, "Jennifer Wang", 106, 13, "IN"),
    (7, "Julia Salamacha", 106, 13, "CA"),
    (7, "Olivia Xu", 106, 13, "NY"),
    (7, "Pranav Sivakumar", 106, 13, "CA"),
    (7, "Yedong Yu", 106, 13, "OR"),
    (7, "Yuehan Ma", 106, 13, "WA"),
    (7, "Aayan Ansary", 105, 14, "KY"),
    (7, "Angela Song", 105, 14, "MA"),
    (7, "David Liu", 105, 14, "CA"),
    (7, "Dylan Zhong", 105, 14, "MN"),
    (7, "Leo Shi", 105, 14, "MA"),
    (7, "Rohith Thomas", 105, 14, "CO"),
    (7, "Shamik Khowala", 105, 14, "CA"),
    (7, "Shuyin Liu", 105, 14, "WA"),
    (7, "Utshaho Gupta", 105, 14, "GA"),
    (7, "William Liu", 105, 14, "CA"),
    (7, "Anshul Dandekar", 104, 15, "CA"),
    (7, "Mahi Kohli", 104, 15, "KS"),
    (7, "Max Brueggeman", 104, 15, "OH"),
    (7, "Miguel Shim", 104, 15, "SC"),
    (7, "Phil Yao", 104, 15, "WA"),
    (7, "Taras Abakumov", 104, 15, "WA"),
    (7, "Toprak Celikel", 104, 15, "WA"),
    (7, "Athena Gottlieb", 103, 16, "IL"),
    (7, "Haolin Li", 103, 16, "NJ"),
    (7, "Jason Lu", 103, 16, "NY"),
    (7, "Max Wang", 103, 16, "IL"),
    (7, "Neil Dutta", 103, 16, "MA"),
    (7, "Osvin Alaphat", 103, 16, "MO"),
    (7, "Sathvik Kurapati", 103, 16, "WA"),
    (7, "Theenash Sengupta", 103, 16, "CA"),
    (7, "Vikrant Chintanaboina", 103, 16, "CA"),
    (7, "Arkar Tan", 102, 17, "CA"),
    (7, "Connor Kong", 102, 17, "CA"),
    (7, "Emmett Chen", 102, 17, "MA"),
    (7, "Kalyan Cherukuri", 102, 17, "IL"),
    (7, "Naaisha Agarwal", 102, 17, "MA"),
    (7, "Ray Zhao", 102, 17, "MA"),
    (7, "Shawn Badre", 102, 17, "RI"),
    (7, "Soham Pattnaik", 102, 17, "VA"),
    (7, "Sophia Zhu", 102, 17, "WA"),
    (7, "Caroline Huang", 101, 18, "GA"),
    (7, "Daniil Yakavets", 101, 18, "CA"),
    (7, "Jason Lee", 101, 18, "CA"),
    (7, "Krish Behera", 101, 18, "VA"),
    (7, "Zephan Calhoun", 101, 18, "CA"),
    (7, "Aniket Mangalampalli", 100, 19, "CA"),
    (7, "Anray Sheng", 100, 19, "MA"),
    (7, "Bethesda Yeh", 100, 19, "MA"),
    (7, "Harsevran Bhullar", 100, 19, "CA"),
    (7, "Jevin Xu", 100, 19, "VA"),
    (7, "Praneel Mukherjee", 100, 19, "VA"),
    (7, "Rushil Sengupta", 100, 19, "CA"),
    (7, "Sophia Fan", 100, 19, "CA"),
    (7, "Stefan Donisa", 100, 19, "IL"),
    (7, "Timothy Chen", 100, 19, "CA"),
    (7, "Zachary Shen", 100, 19, "CA"),
    (7, "Edward Zhang", 99, 20, "CA"),
    (7, "Ender Ramsby", 99, 20, "WA"),
    (7, "Ethan Han", 99, 20, "CA"),
    (7, "Lily Xing", 99, 20, "MA"),
    (7, "Lucas Quan", 99, 20, "CA"),
    (7, "Nathan Ye", 99, 20, "OR"),
    (7, "Navya Jain", 99, 20, "WA"),
    (7, "Sanjith Senthil", 99, 20, "CA"),
    (7, "Shveta Sunkar", 99, 20, "VA"),
    (7, "Surie Feng", 99, 20, "AZ"),
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
