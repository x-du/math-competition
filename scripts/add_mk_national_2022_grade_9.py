#!/usr/bin/env python3
"""
Add Math Kangaroo 2022 Grade 9 National Winners.
Source: https://mathkangaroo.org/mks/wp-content/uploads/2022/05/2022_Level-9_National-Winners.pdf
Resolves (name, state) via students.csv; adds new students as needed.
Do NOT merge students with same name in different states - match strictly on (name, state).
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2022" / "grade=9"

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

# grade, name, score, rank, state (from 2022 Level 9 National Winners PDF)
ROWS = [
    (9, "Abhinav Krishna", 120, 1, "CO"),
    (9, "Aidan Zhang", 120, 1, "CA"),
    (9, "Alex Hart", 120, 1, "GA"),
    (9, "Alexander Davi", 120, 1, "NV"),
    (9, "Alexander Song", 120, 1, "NY"),
    (9, "Andrew Brahms", 120, 1, "NJ"),
    (9, "Christopher Dickman", 120, 1, "WA"),
    (9, "Daniel Gilman", 120, 1, "NJ"),
    (9, "David Lu", 120, 1, "VA"),
    (9, "David Sheng", 120, 1, "VA"),
    (9, "David Zhang", 120, 1, "CA"),
    (9, "Elizabeth Levinshteyn", 120, 1, "MN"),
    (9, "Jefferson Ji", 120, 1, "MA"),
    (9, "Joyce Huang", 120, 1, "WA"),
    (9, "Kirby Fung", 120, 1, "CA"),
    (9, "Kylar Cheng", 120, 1, "CA"),
    (9, "Maxwell Gong", 120, 1, "NJ"),
    (9, "Patrick Du", 120, 1, "VA"),
    (9, "Rohin Garg", 120, 1, "CA"),
    (9, "Rohith Raghavan", 120, 1, "MA"),
    (9, "Sai Palireddy", 120, 1, "GA"),
    (9, "Tianyi Alicia Zhou", 120, 1, "MA"),
    (9, "Timothy Torubarov", 120, 1, "NJ"),
    (9, "William Chen", 120, 1, "CA"),
    (9, "Yufei Chen", 120, 1, "CA"),
    (9, "Benjamin Jiang", 117, 2, "FL"),
    (9, "Ishani Agarwal", 117, 2, "CA"),
    (9, "Aakash Gokhale", 116, 3, "CA"),
    (9, "Alexander Ung", 116, 3, "IL"),
    (9, "Anjan Yalamanchili", 116, 3, "NH"),
    (9, "Dana Chan", 116, 3, "CA"),
    (9, "David Zhang", 116, 3, "UT"),
    (9, "Fateh Aliyev", 116, 3, "CA"),
    (9, "Janice Lee", 116, 3, "CA"),
    (9, "Ken Yoshida", 116, 3, "PA"),
    (9, "Nicholas Volfbeyn", 116, 3, "WA"),
    (9, "Qiao Zhang", 116, 3, "CA"),
    (9, "Sajeev Magesh", 116, 3, "CA"),
    (9, "Sanya Badhe", 116, 3, "CA"),
    (9, "Stas Abakumov", 116, 3, "WA"),
    (9, "Aadi Dash", 115, 4, "MA"),
    (9, "Aidan Zhong", 115, 4, "OH"),
    (9, "Anshul Gokul", 115, 4, "GA"),
    (9, "Collin Keopanya", 115, 4, "WI"),
    (9, "Dashiel Lin", 115, 4, "NJ"),
    (9, "David Deutsch", 115, 4, "CA"),
    (9, "Egor Lazarevich", 115, 4, "MA"),
    (9, "Gil Yarsky", 115, 4, "NY"),
    (9, "Govind Velamoor", 115, 4, "MA"),
    (9, "Gregory Roudenko", 115, 4, "VA"),
    (9, "Isaac Nobles", 115, 4, "NC"),
    (9, "Joseph Widjaja", 115, 4, "PA"),
    (9, "Kyan Yang", 115, 4, "VA"),
    (9, "Phoebe Pan", 115, 4, "VA"),
    (9, "Rockwell Li", 115, 4, "VA"),
    (9, "Shreyas Ekanathan", 115, 4, "MA"),
    (9, "Anastasia Lee", 113, 5, "NY"),
    (9, "Ava Park", 113, 5, "CA"),
    (9, "Caleb Liu", 112, 6, "AZ"),
    (9, "Howard Liu", 112, 6, "CA"),
    (9, "Kyra Cui", 112, 6, "CA"),
    (9, "Michael Salko", 112, 6, "CA"),
    (9, "Rick Yang", 112, 6, "CA"),
    (9, "William Chu", 112, 6, "AZ"),
    (9, "Ananya Bezbaruah", 111, 7, "WA"),
    (9, "Brian Wei", 111, 7, "UT"),
    (9, "Bryan Yung", 111, 7, "MD"),
    (9, "Daron Simmons", 111, 7, "FL"),
    (9, "Hugh Cheng", 111, 7, "CA"),
    (9, "Ivan Zhang", 111, 7, "MD"),
    (9, "Lily Tjia", 111, 7, "MA"),
    (9, "Lingzi Wang", 111, 7, "CA"),
    (9, "Maulik Verma", 111, 7, "NC"),
    (9, "Meha Sekaran", 111, 7, "CA"),
    (9, "Niharika Prachanda", 111, 7, "CA"),
    (9, "Noel Prince Muthuplakal", 111, 7, "WA"),
    (9, "Ray Zhang", 111, 7, "VA"),
    (9, "Ryan Wu", 111, 7, "PA"),
    (9, "Sampath Kalagarla", 111, 7, "MA"),
    (9, "Sargam Mondal", 111, 7, "NJ"),
    (9, "Vibhush Sivakumar", 111, 7, "MA"),
    (9, "Yelisey Romanov", 111, 7, "KS"),
    (9, "Allison Hung", 110, 8, "CA"),
    (9, "Ella Wang", 110, 8, "CA"),
    (9, "Ian Weatherford", 110, 8, "VA"),
    (9, "Joshua Lin", 110, 8, "IL"),
    (9, "Karn Chutinan", 110, 8, "MA"),
    (9, "Levi Polsky", 110, 8, "WA"),
    (9, "Minh Nguyen", 110, 8, "VA"),
    (9, "Robert Leonardi", 110, 8, "SC"),
    (9, "Rose Cohen", 110, 8, "CA"),
    (9, "Sreeram Sai Vuppala", 110, 8, "NJ"),
    (9, "Yejoon Ham", 110, 8, "TN"),
    (9, "Zaven Kouchakdjian", 108, 9, "MA"),
    (9, "Brianna Zheng", 107, 10, "CA"),
    (9, "Eldrick Fan", 107, 10, "CA"),
    (9, "Elita You", 107, 10, "MI"),
    (9, "Eric Yee", 107, 10, "WA"),
    (9, "Ethan Do", 107, 10, "WA"),
    (9, "Haoming Zheng", 107, 10, "KY"),
    (9, "Iris Li", 107, 10, "CA"),
    (9, "Radea Raleva", 107, 10, "CT"),
    (9, "William Wang", 107, 10, "SC"),
    (9, "Yash Marpu", 107, 10, "VA"),
    (9, "Aneesh Devulapalli", 106, 11, "CA"),
    (9, "Brandon Holland", 106, 11, "CA"),
    (9, "Ellen Li", 106, 11, "TX"),
    (9, "Iris Tang", 106, 11, "WA"),
    (9, "Madeline Liachenko", 106, 11, "AR"),
    (9, "Praneeth Otthi", 106, 11, "PA"),
    (9, "Raine Wen", 106, 11, "CA"),
    (9, "Ryon Das", 106, 11, "MA"),
    (9, "Saravanan Valliappan", 106, 11, "CA"),
    (9, "Siyona Jain", 106, 11, "TX"),
    (9, "Azaria Hileman", 105, 12, "MD"),
    (9, "Jiya Singla", 105, 12, "AZ"),
    (9, "Leonardo Chung", 105, 12, "NH"),
    (9, "Sophia Lin", 105, 12, "VA"),
    (9, "Sounak Bagchi", 105, 12, "NJ"),
    (9, "Suhas Beeravelli", 105, 12, "OH"),
    (9, "Westley Rae", 105, 12, "UT"),
    (9, "Thomas Ye", 104, 13, "VA"),
    (9, "Alex Seojoon Kim", 103, 14, "OK"),
    (9, "Dhruv Vallurupalli", 103, 14, "MA"),
    (9, "Franklin Yang", 103, 14, "CA"),
    (9, "Gabriel Dunu", 103, 14, "CA"),
    (9, "Sri Sumukh Vulava", 103, 14, "KY"),
    (9, "Cameron Kelm", 102, 15, "CA"),
    (9, "Daniel Wu", 102, 15, "MD"),
    (9, "David Katsman", 102, 15, "MA"),
    (9, "Mahanth Komuravelli", 102, 15, "NJ"),
    (9, "Paras Aggarwal", 102, 15, "TX"),
    (9, "Rainier Mayo", 102, 15, "CA"),
    (9, "Smithi Gopalakrishnan", 102, 15, "TX"),
    (9, "Alisa Bryantseva", 101, 16, "TN"),
    (9, "Audrey Perry", 101, 16, "TX"),
    (9, "Bodie Woods", 101, 16, "CA"),
    (9, "Mohith Ram Narendra Babu", 101, 16, "WA"),
    (9, "Rishabh Rao", 101, 16, "MI"),
    (9, "Sanat Gupta", 101, 16, "CA"),
    (9, "Yourui Shao", 101, 16, "CA"),
    (9, "Aidan Mascoli", 100, 17, "NJ"),
    (9, "Alan Zhong", 100, 17, "OR"),
    (9, "Gabriel Xu", 100, 17, "VA"),
    (9, "Yanwen Zhao", 100, 17, "VA"),
    (9, "Anthony Du", 99, 18, "VA"),
    (9, "Armaan Sidhu", 99, 18, "IL"),
    (9, "Lilian Pamula", 99, 18, "CA"),
    (9, "Mikhail Alexeykin", 99, 18, "TX"),
    (9, "Siddhant Ganeshwaran", 99, 18, "MA"),
    (9, "William Yang", 99, 18, "CA"),
    (9, "Alexander Loo", 98, 19, "MA"),
    (9, "Amit Sail", 98, 19, "NJ"),
    (9, "Anagh Gupta", 98, 19, "NY"),
    (9, "Anika Mittal", 98, 19, "MA"),
    (9, "Mingchuan Cheng", 98, 19, "UT"),
    (9, "Pinak Paliwal", 98, 19, "CA"),
    (9, "William Gochnour", 98, 19, "NV"),
    (9, "Ben Nir", 97, 20, "MA"),
    (9, "Bhuvan Sanga", 97, 20, "KY"),
    (9, "Dylan Mihovski", 97, 20, "PA"),
    (9, "George Durrett", 97, 20, "KS"),
    (9, "Grace Lee", 97, 20, "VA"),
    (9, "Hanning Yan", 97, 20, "PA"),
    (9, "Ishaan Adhikary", 97, 20, "MA"),
    (9, "Kelly Gao", 97, 20, "CA"),
    (9, "Krrish Mishra", 97, 20, "NH"),
    (9, "Pranamya Keshkamat", 97, 20, "MA"),
    (9, "Saidivyesh Tunguturu", 97, 20, "CA"),
    (9, "Tanish Ghosh", 97, 20, "MA"),
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
