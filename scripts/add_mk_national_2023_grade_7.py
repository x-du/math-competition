#!/usr/bin/env python3
"""
Add Math Kangaroo 2023 Grade 7 (Level 7) National Winners.
Source: https://mathkangaroo.org/mks/wp-content/uploads/2023/05/2023_Level-7_National-Winners.pdf
Resolves (name, state) via students.csv; adds new students as needed.
2023 format: no national_percentile in source.
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2023" / "grade=7"

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

# grade, name, score, rank, state (ARPIT PANDA: Pleasanton CA per AoPS Pleasanton)
ROWS = [
    (7, "Eddy Zhang", 120, 1, "PA"),
    (7, "Mia Zhao", 120, 1, "MA"),
    (7, "Yunong Wu", 120, 1, "NY"),
    (7, "Aahana Shah", 116, 2, "NJ"),
    (7, "Alicia Fei", 116, 2, "CA"),
    (7, "Eric Ding", 116, 2, "MN"),
    (7, "Jasper Leung", 116, 2, "CA"),
    (7, "Joshua Liu", 116, 2, "CO"),
    (7, "Minghao Guo", 116, 2, "CA"),
    (7, "Taiwen Feng", 116, 2, "MI"),
    (7, "Vincent Pirozzo", 116, 2, "CA"),
    (7, "William Shan", 116, 2, "AZ"),
    (7, "Brianna Hou", 115, 3, "MA"),
    (7, "Daniel Vladimiroff", 115, 3, "VA"),
    (7, "Ishaan Mittal", 115, 3, "CA"),
    (7, "Oscar Varodayan", 115, 3, "CA"),
    (7, "Stephen Wang", 114, 4, "MA"),
    (7, "Christopher Sakaliyski", 113, 5, "IL"),
    (7, "Evander Protopapas", 113, 5, "NY"),
    (7, "Frederik Bultje", 113, 5, "NY"),
    (7, "Lucas Hayes", 113, 5, "NY"),
    (7, "Akansh Karthik", 112, 6, "TX"),
    (7, "Anish Thota", 112, 6, "VA"),
    (7, "Boyan Manolov", 112, 6, "CA"),
    (7, "Tanisha Bhugra", 112, 6, "CA"),
    (7, "Camea Caprita", 111, 7, "CA"),
    (7, "Ella Qiu", 111, 7, "WA"),
    (7, "Ethan Liu", 111, 7, "MI"),
    (7, "Girish Prasad", 111, 7, "CT"),
    (7, "Hayden Hughes", 111, 7, "CT"),
    (7, "Jiayu Su", 111, 7, "CT"),
    (7, "John Kong", 111, 7, "OR"),
    (7, "Maria Tzanova", 111, 7, "NY"),
    (7, "Michelle Zheng", 111, 7, "MA"),
    (7, "Minkyul Kim", 111, 7, "CA"),
    (7, "Sage Miller", 111, 7, "CA"),
    (7, "Trisha Sinha", 111, 7, "MA"),
    (7, "Vihaan Dev", 111, 7, "WA"),
    (7, "William Xiao", 111, 7, "CA"),
    (7, "Zoya Tahmasian", 111, 7, "MA"),
    (7, "Eva Lin", 110, 8, "CA"),
    (7, "Zhuoyi Samuel Wang", 110, 8, "CA"),
    (7, "Lucas Yang", 109, 9, "PA"),
    (7, "Anirudh Pulugurtha", 108, 10, "NH"),
    (7, "Anthony Zhou", 108, 10, "CA"),
    (7, "Arnav Sreeram", 108, 10, "MA"),
    (7, "Leyi Li", 108, 10, "CA"),
    (7, "Nathan Chen", 108, 10, "CA"),
    (7, "Tara Radoicic", 108, 10, "NJ"),
    (7, "Yuantao Tang", 108, 10, "PA"),
    (7, "Aanya Mittal", 107, 11, "MA"),
    (7, "Abhinav Vutukuri", 107, 11, "IL"),
    (7, "Anika Malyavanatham", 107, 11, "OR"),
    (7, "Joseph Peng", 107, 11, "MA"),
    (7, "Leonardo Deng", 107, 11, "MA"),
    (7, "Prajit Saravanan", 107, 11, "TX"),
    (7, "Ryan Chen", 107, 11, "NY"),
    (7, "Sriya Gomatam", 107, 11, "TX"),
    (7, "Waroon Thapanangkun", 107, 11, "CA"),
    (7, "Atticus Stewart", 106, 12, "CA"),
    (7, "Daniel Dimitrov", 106, 12, "NC"),
    (7, "Kiran Oliver", 106, 12, "MD"),
    (7, "Michael Zhao", 106, 12, "CA"),
    (7, "Srinandasa Ari", 106, 12, "VA"),
    (7, "Alexander Gao", 105, 13, "IN"),
    (7, "Arpit Panda", 105, 13, "CA"),
    (7, "Jonathan Zhou", 105, 13, "CT"),
    (7, "Aditya Bhide", 104, 14, "WA"),
    (7, "Anish Agarwal", 104, 14, "CA"),
    (7, "Avi Khurania", 104, 14, "CA"),
    (7, "Brandon Lowenstein", 104, 14, "CA"),
    (7, "Claire Wang", 104, 14, "IA"),
    (7, "Daniel Farcas", 104, 14, "CA"),
    (7, "Kabir Khandelwal", 104, 14, "WA"),
    (7, "Kevin Song", 104, 14, "WA"),
    (7, "Manan Ghosh", 104, 14, "WA"),
    (7, "Thomas Ludlam", 104, 14, "CA"),
    (7, "Ishaan Jain", 103, 15, "AL"),
    (7, "Jeffrey Yin", 103, 15, "MA"),
    (7, "Larry Cao", 103, 15, "CA"),
    (7, "Manas Aggarwal", 103, 15, "TX"),
    (7, "Matthew Lau", 103, 15, "CA"),
    (7, "Sankarshana Sudeendra", 103, 15, "CA"),
    (7, "Sravya Mandapati", 103, 15, "NJ"),
    (7, "Surya Raghavan", 103, 15, "NJ"),
    (7, "Vidyut Kartik", 103, 15, "MA"),
    (7, "Aditya Joshi", 102, 16, "NY"),
    (7, "Alex Shi", 102, 16, "CA"),
    (7, "Arda Eroz", 102, 16, "MD"),
    (7, "Atiksh Akunuri", 102, 16, "NJ"),
    (7, "Evan Han", 102, 16, "CA"),
    (7, "Grant Liu", 102, 16, "IL"),
    (7, "Jingxuan Bo", 102, 16, "CA"),
    (7, "Joshua Lee", 102, 16, "CA"),
    (7, "Matthew Wang", 102, 16, "CA"),
    (7, "Mohita Chepeni", 102, 16, "MA"),
    (7, "Nathaniel Zhang", 102, 16, "IL"),
    (7, "Satya Daftuar", 102, 16, "CT"),
    (7, "Shannon Imaoka", 102, 16, "CA"),
    (7, "Sruthi Manoj", 102, 16, "CA"),
    (7, "Amie Huang", 101, 17, "MA"),
    (7, "Christoffer Lamtan", 101, 17, "NY"),
    (7, "Christopher Gao", 101, 17, "GA"),
    (7, "Elizabeth Soldatenkov", 101, 17, "NJ"),
    (7, "Jonathan Hanna", 101, 17, "MA"),
    (7, "Kaustubh Bukkapatnam", 101, 17, "IL"),
    (7, "Rishi Balaji", 101, 17, "MA"),
    (7, "Trisha Dutta", 101, 17, "MA"),
    (7, "Yan Levin", 101, 17, "WA"),
    (7, "Brianna Xin", 100, 18, "MA"),
    (7, "Petey Bunsongsikul", 100, 18, "CA"),
    (7, "Pranav Kokati", 100, 18, "WA"),
    (7, "Reya Doctor", 100, 18, "CA"),
    (7, "Aarush Rachakonda", 99, 19, "CA"),
    (7, "Cara Wang", 99, 19, "CA"),
    (7, "Julia Matveyev", 99, 19, "CA"),
    (7, "Lawrence Du", 99, 19, "MD"),
    (7, "Rena Cao", 99, 19, "CA"),
    (7, "Thanishkka Vijayabaskar", 99, 19, "GA"),
    (7, "Vida Ristivojevic", 99, 19, "MA"),
    (7, "Anay Parikh", 98, 20, "CA"),
    (7, "Ariel Ioffe", 98, 20, "MA"),
    (7, "Chandhana Lingam Muhilan", 98, 20, "NJ"),
    (7, "Dheeraj Garg", 98, 20, "DE"),
    (7, "Elina Borodina", 98, 20, "IL"),
    (7, "Gautham Agilan", 98, 20, "VA"),
    (7, "George Paret", 98, 20, "FL"),
    (7, "Jacob Weng", 98, 20, "GA"),
    (7, "Julia Shtiliyanova", 98, 20, "MA"),
    (7, "Kabeer Arora", 98, 20, "NY"),
    (7, "Katherine Yang", 98, 20, "CA"),
    (7, "Lucas Chen", 98, 20, "CA"),
    (7, "Rujula Yeole", 98, 20, "MI"),
    (7, "Sonia Lee", 98, 20, "VA"),
    (7, "Steven Huang", 98, 20, "CA"),
    (7, "Steven Shu", 98, 20, "CA"),
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
