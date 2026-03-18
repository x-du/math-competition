#!/usr/bin/env python3
"""
Add Math Kangaroo 2023 Grade 10 National Winners.
Resolves (name, state) via students.csv; adds new students as needed.
2023 format: no national_percentile in source.
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2023" / "grade=10"

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
    (10, "Aidan Zhang", 120, 1, "CA"),
    (10, "Alex Hart", 120, 1, "GA"),
    (10, "Alexander Song", 120, 1, "NY"),
    (10, "Ananya Bezbaruah", 120, 1, "WA"),
    (10, "Brianna Zheng", 120, 1, "CA"),
    (10, "Bryan Yung", 120, 1, "MD"),
    (10, "Daniel Gilman", 120, 1, "NJ"),
    (10, "David Deutsch", 120, 1, "CA"),
    (10, "David Lu", 120, 1, "VA"),
    (10, "David Zhang", 120, 1, "CA"),
    (10, "Eric Jin", 120, 1, "IN"),
    (10, "Ethan Zhang", 120, 1, "OR"),
    (10, "Gil Yarsky", 120, 1, "NY"),
    (10, "Gregory Roudenko", 120, 1, "VA"),
    (10, "Joyce Huang", 120, 1, "WA"),
    (10, "Kylar Cheng", 120, 1, "CA"),
    (10, "Patrick Du", 120, 1, "VA"),
    (10, "Phoebe Pan", 120, 1, "VA"),
    (10, "Rockwell Li", 120, 1, "VA"),
    (10, "Rohith Raghavan", 120, 1, "MA"),
    (10, "Rose Cohen", 120, 1, "CA"),
    (10, "Sanjay Ravishankar", 120, 1, "CA"),
    (10, "Satvik Sivaraman", 120, 1, "CA"),
    (10, "Shrey Gupta", 120, 1, "FL"),
    (10, "Tatiana Medved", 120, 1, "NC"),
    (10, "Timothy Torubarov", 120, 1, "NJ"),
    (10, "William Chen", 120, 1, "CA"),
    (10, "Fateh Aliyev", 117, 2, "CA"),
    (10, "Janice Lee", 117, 2, "CA"),
    (10, "Sreeram Sai Vuppala", 117, 2, "NJ"),
    (10, "Tianyi Alicia Zhou", 117, 2, "MA"),
    (10, "William Qian", 117, 2, "MD"),
    (10, "Yufei Chen", 117, 2, "CA"),
    (10, "Andrew Zeng", 116, 3, "GA"),
    (10, "Anjena Raja", 115, 4, "CA"),
    (10, "Anthony Dokanchi", 115, 4, "CA"),
    (10, "Daron Simmons", 115, 4, "FL"),
    (10, "David Sheng", 115, 4, "VA"),
    (10, "Iris Tang", 115, 4, "WA"),
    (10, "Jefferson Ji", 115, 4, "MA"),
    (10, "Joshua Lin", 115, 4, "IL"),
    (10, "Neil Krishnan", 115, 4, "CA"),
    (10, "Sanya Badhe", 115, 4, "CA"),
    (10, "Shreyan Paliwal", 115, 4, "OR"),
    (10, "Shreyas Ekanathan", 115, 4, "MA"),
    (10, "Taran Knutson", 115, 4, "NY"),
    (10, "Tzuriel Justin Yu", 115, 4, "MA"),
    (10, "Vibhush Sivakumar", 115, 4, "MA"),
    (10, "Christopher Dickman", 112, 5, "WA"),
    (10, "Levi Polsky", 112, 5, "IL"),
    (10, "Madeline Liachenko", 112, 5, "AR"),
    (10, "Mina Yeh", 112, 5, "NY"),
    (10, "Andrew Brahms", 111, 6, "NJ"),
    (10, "Govind Velamoor", 111, 6, "MA"),
    (10, "Alicia Ye", 110, 7, "OR"),
    (10, "Donglin Jin", 110, 7, "CA"),
    (10, "Ethan Do", 110, 7, "WA"),
    (10, "Howard Liu", 110, 7, "CA"),
    (10, "Joseph Widjaja", 110, 7, "PA"),
    (10, "Krrish Mishra", 110, 7, "NH"),
    (10, "Minh Nguyen", 110, 7, "VA"),
    (10, "Sajeev Magesh", 110, 7, "CA"),
    (10, "Aidan Mascoli", 107, 8, "NJ"),
    (10, "Cole Glenn", 107, 8, "SC"),
    (10, "Leo Lhert", 107, 8, "CA"),
    (10, "Neil Nori", 107, 8, "MA"),
    (10, "Yanwen Zhao", 107, 8, "VA"),
    (10, "Arlan Zbarsky", 106, 9, "MA"),
    (10, "Audrey Perry", 106, 9, "TX"),
    (10, "Jiya Singla", 106, 9, "AZ"),
    (10, "Smithi Gopalakrishnan", 106, 9, "TX"),
    (10, "Alan Zhong", 105, 10, "OR"),
    (10, "Alexander Mitev", 105, 10, "IL"),
    (10, "Alexander Ung", 105, 10, "IL"),
    (10, "Daniel Fanaru", 105, 10, "WA"),
    (10, "Daniel Jin", 105, 10, "UT"),
    (10, "Dhruv Jena", 105, 10, "CA"),
    (10, "Dylan Li", 105, 10, "MI"),
    (10, "Ellen Li", 105, 10, "TX"),
    (10, "Jagan Mranal", 105, 10, "MA"),
    (10, "Mikhail Alexeykin", 105, 10, "TX"),
    (10, "Rafi Razmi", 105, 10, "MA"),
    (10, "Vrishabh Doshi", 105, 10, "GA"),
    (10, "Anthony Du", 103, 11, "VA"),
    (10, "Angela Zhan", 102, 12, "UT"),
    (10, "Cameron Kelm", 102, 12, "CA"),
    (10, "Collin Keopanya", 102, 12, "WI"),
    (10, "Ethan Nguyen", 102, 12, "CA"),
    (10, "Ivan Zhang", 102, 12, "MD"),
    (10, "Leo Feng", 102, 12, "CA"),
    (10, "Noel Prince Muthuplakal", 102, 12, "WA"),
    (10, "Paras Aggarwal", 102, 12, "TX"),
    (10, "Rhishi Sakthivel", 102, 12, "CA"),
    (10, "Siyona Dhingra", 102, 12, "CA"),
    (10, "Armaan Sidhu", 100, 13, "IL"),
    (10, "Brandon Cardamone", 100, 13, "NY"),
    (10, "Dana Chan", 100, 13, "CA"),
    (10, "Ken Yoshida", 100, 13, "DC"),
    (10, "Max Chen", 100, 13, "IL"),
    (10, "Patrick Liu", 100, 13, "CA"),
    (10, "Tanooj Kanike", 100, 13, "TX"),
    (10, "Zaven Kouchakdjian", 100, 13, "MA"),
    (10, "Travis Ferrin", 99, 14, "UT"),
    (10, "Aakash Gokhale", 98, 15, "CA"),
    (10, "Alexander Park", 97, 16, "NV"),
    (10, "Aliana Tang", 97, 16, "CA"),
    (10, "Aran Chakraborty", 97, 16, "MA"),
    (10, "Azaria Hileman", 97, 16, "MD"),
    (10, "Lucia Liu", 97, 16, "NY"),
    (10, "Mohith Ram Narendra Babu", 97, 16, "WA"),
    (10, "Natalie Kong", 97, 16, "CA"),
    (10, "Tejas Ravi", 97, 16, "CA"),
    (10, "Zhuojia Chen", 97, 16, "CT"),
    (10, "Anjan Yalamanchili", 96, 17, "NH"),
    (10, "Delia Brown", 96, 17, "PA"),
    (10, "Jared Rosen", 96, 17, "MA"),
    (10, "Lyev Pitram", 96, 17, "PA"),
    (10, "Marlena Zuo", 96, 17, "KS"),
    (10, "Anishka Jannu", 95, 18, "CA"),
    (10, "Bhuvan Sanga", 95, 18, "KY"),
    (10, "Sampath Kalagarla", 95, 18, "MA"),
    (10, "Bryan Lee", 94, 19, "GA"),
    (10, "Terry Ding", 94, 19, "MA"),
    (10, "Iris Li", 93, 20, "CA"),
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
