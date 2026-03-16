#!/usr/bin/env python3
"""
Add Math Kangaroo 2022 Grade 10 National Winners.
Source: https://mathkangaroo.org/mks/wp-content/uploads/2022/05/2022_Level-10_National-Winners.pdf
Resolves (name, state) via students.csv; adds new students as needed.
Do NOT merge students with same name in different states - match strictly on (name, state).
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2022" / "grade=10"

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

# grade, name, score, rank, state (from 2022 Level 10 National Winners PDF)
ROWS = [
    (10, "Aaron Hu", 120, 1, "FL"),
    (10, "Aditya Gupta", 120, 1, "IL"),
    (10, "Alexander Korchev", 120, 1, "MA"),
    (10, "Amudhan Gurumoorthy", 120, 1, "CA"),
    (10, "Athena Devashish", 120, 1, "MD"),
    (10, "Catherine Li", 120, 1, "CA"),
    (10, "David Benjamin Lee", 120, 1, "CA"),
    (10, "David Jiang", 120, 1, "NY"),
    (10, "Derek Xu", 120, 1, "NY"),
    (10, "Elena Baskakova", 120, 1, "MA"),
    (10, "Evan Zhang", 120, 1, "MA"),
    (10, "Jakub Pienkowski", 120, 1, "NY"),
    (10, "Karolina Bajda", 120, 1, "NY"),
    (10, "Katherine Nogin", 120, 1, "CA"),
    (10, "Michael Liu", 120, 1, "CA"),
    (10, "Michael Lu", 120, 1, "NY"),
    (10, "Roshen Nair", 120, 1, "OR"),
    (10, "Sam Rozansky", 120, 1, "NC"),
    (10, "Satvik Kabbur", 120, 1, "WA"),
    (10, "Shreev Goyal", 120, 1, "TX"),
    (10, "Shreyas Singh", 120, 1, "IL"),
    (10, "Srinivas Arun", 120, 1, "CO"),
    (10, "Taohan Lin", 120, 1, "VA"),
    (10, "Vedant Aryan", 120, 1, "CT"),
    (10, "Zaee Shah", 120, 1, "CA"),
    (10, "Henry Burton", 117, 2, "NY"),
    (10, "Sumedh Vangara", 117, 2, "MD"),
    (10, "Albert Lu", 116, 3, "MD"),
    (10, "Alexander Bai", 116, 3, "CA"),
    (10, "Alexus Lee", 116, 3, "NY"),
    (10, "Bhargava Mortha", 116, 3, "IN"),
    (10, "Daniel Li", 116, 3, "MD"),
    (10, "David Wei", 116, 3, "VA"),
    (10, "Gideon Heltzer", 116, 3, "IL"),
    (10, "Julian Vertigan", 116, 3, "LA"),
    (10, "Maya Viswanathan", 116, 3, "IL"),
    (10, "Michael Marchev", 116, 3, "MA"),
    (10, "Vishal Nandakumar", 116, 3, "VA"),
    (10, "Alexander Chen", 115, 4, "AZ"),
    (10, "Arnav Busani", 115, 4, "MO"),
    (10, "Cyrus Zhou", 115, 4, "GA"),
    (10, "Eshaan Debnath", 115, 4, "NJ"),
    (10, "Gabe Nather", 115, 4, "MD"),
    (10, "Harsh Akunuri", 115, 4, "NJ"),
    (10, "Harshil Pathri", 115, 4, "CA"),
    (10, "Justin Chan", 115, 4, "WA"),
    (10, "Kevin Shi", 115, 4, "NY"),
    (10, "Matthew Patkowski", 115, 4, "GA"),
    (10, "Patrick Ying", 115, 4, "VA"),
    (10, "Rahul Tacke", 115, 4, "MA"),
    (10, "Sebastian Prasanna", 115, 4, "MA"),
    (10, "Thomas Du", 115, 4, "MA"),
    (10, "Vedant Rathi", 115, 4, "IL"),
    (10, "Venkatraman Varatharajan", 115, 4, "MA"),
    (10, "Jannie Xu", 113, 5, "CA"),
    (10, "Mihika Dusad", 113, 5, "VA"),
    (10, "William Qian", 113, 5, "MD"),
    (10, "Amish Patra", 112, 6, "WA"),
    (10, "Anant Asthana", 112, 6, "TX"),
    (10, "Ariel Lyanda-Geller", 112, 6, "IN"),
    (10, "Arnav Ashok", 112, 6, "CA"),
    (10, "Ethan Kuang", 112, 6, "MA"),
    (10, "Kangsan Yoon", 112, 6, "GU"),
    (10, "Noam Pasman", 112, 6, "NY"),
    (10, "Priya Adiga", 112, 6, "IL"),
    (10, "Yejun Yun", 112, 6, "KS"),
    (10, "Amy Xu", 111, 7, "MD"),
    (10, "Ananya Mahadevan", 111, 7, "CA"),
    (10, "Angelina Berg", 111, 7, "PA"),
    (10, "Avi Gupta", 111, 7, "CA"),
    (10, "Evan Grosso", 111, 7, "AZ"),
    (10, "Joshua Cortright", 111, 7, "CA"),
    (10, "Matthew Sun", 111, 7, "NC"),
    (10, "Ryan Chin", 111, 7, "TX"),
    (10, "Samarth Das", 111, 7, "TX"),
    (10, "Shoshana Elgart", 111, 7, "VA"),
    (10, "Vamsi Krishna Ankalu", 111, 7, "MA"),
    (10, "Anthony Piotrowski", 110, 8, "NH"),
    (10, "Eney Tkachenko", 110, 8, "NY"),
    (10, "Ruthvik Singireddy", 110, 8, "CA"),
    (10, "Ryan Chao", 110, 8, "MA"),
    (10, "Haokai Ma", 109, 9, "NY"),
    (10, "Izabella Zaleski", 109, 9, "NY"),
    (10, "Daniel Matsui Smola", 108, 10, "CA"),
    (10, "Grace To", 108, 10, "IL"),
    (10, "James Kim", 108, 10, "AL"),
    (10, "Alicia Ye", 107, 11, "OR"),
    (10, "Aniketh Tummala", 107, 11, "CA"),
    (10, "Christopher Weng", 107, 11, "CA"),
    (10, "Lakshya Jain", 107, 11, "MA"),
    (10, "Sirius Ling", 107, 11, "CA"),
    (10, "Timason Wan", 107, 11, "WA"),
    (10, "William Liu", 107, 11, "WA"),
    (10, "Abhiraj Bhashkar", 106, 12, "CA"),
    (10, "Aidan Paul", 106, 12, "MD"),
    (10, "Alexander Doboli", 106, 12, "NY"),
    (10, "Anthony Yan", 106, 12, "CA"),
    (10, "Dean Cardner", 106, 12, "MA"),
    (10, "Jaan Srimurthy", 106, 12, "MA"),
    (10, "Jack Fasching", 106, 12, "CA"),
    (10, "Kaloyan Draganov", 106, 12, "MA"),
    (10, "Polaris Hayes", 106, 12, "NJ"),
    (10, "Prisha Jain", 106, 12, "CA"),
    (10, "Riddhi Sharma", 106, 12, "CT"),
    (10, "Serkan Salik", 106, 12, "CA"),
    (10, "Sreedathan Menon", 106, 12, "TX"),
    (10, "Tomas Maranga", 106, 12, "MA"),
    (10, "Vrajesh Daga", 106, 12, "CA"),
    (10, "Angela Yang", 105, 13, "CA"),
    (10, "Cindy Yan", 105, 13, "MO"),
    (10, "Grace Murray", 105, 13, "IL"),
    (10, "Madhav Mandala", 105, 13, "NJ"),
    (10, "Medha Mittal", 105, 13, "WA"),
    (10, "Wesley Rullman", 105, 13, "CA"),
    (10, "Leonardo Serodio", 104, 14, "MA"),
    (10, "Sharanya Chatterjee", 103, 15, "FL"),
    (10, "Zichang Wang", 103, 15, "VA"),
    (10, "Abjini Chattopadhyay", 102, 16, "MD"),
    (10, "Alexander Radulescu", 102, 16, "CA"),
    (10, "Amanda Hong", 102, 16, "CA"),
    (10, "Annie Guo", 102, 16, "MD"),
    (10, "Chloe Parke", 102, 16, "UT"),
    (10, "Golden Peng", 102, 16, "MN"),
    (10, "Henry Ji", 102, 16, "NY"),
    (10, "Neel Bhattacharyya", 102, 16, "MD"),
    (10, "Rishabh Mohapatra", 102, 16, "CT"),
    (10, "Alexander Recce", 101, 17, "NJ"),
    (10, "Alfred Joshua Morales", 101, 17, "GU"),
    (10, "Daphne Ma", 101, 17, "OR"),
    (10, "Oleg Polin", 101, 17, "MA"),
    (10, "Peter (PJ) Duers", 101, 17, "NY"),
    (10, "Siddharth Bhumpelli", 101, 17, "IL"),
    (10, "Swann Li", 101, 17, "MA"),
    (10, "Aadithya Srinivasan", 100, 18, "NJ"),
    (10, "Achyudt Narayanan Venkat", 100, 18, "MI"),
    (10, "Bhadra Rupesh", 100, 18, "CA"),
    (10, "Kavya Desai", 100, 18, "CA"),
    (10, "Megan Weng", 100, 18, "MD"),
    (10, "Nicholas Kieffer", 100, 18, "FL"),
    (10, "Maya Sriram", 98, 19, "CA"),
    (10, "Pranav Puttagunta", 98, 19, "TX"),
    (10, "Rama Chaithanya Bachimanchi", 98, 19, "MA"),
    (10, "Ryan Ferguson", 98, 19, "NC"),
    (10, "Sameer Agrawal", 98, 19, "TX"),
    (10, "Aayushi Nair", 97, 20, "IL"),
    (10, "Advait Kartik", 97, 20, "CA"),
    (10, "Anuj Sheth", 97, 20, "CA"),
    (10, "Arin Van Somphone", 97, 20, "CA"),
    (10, "Haruki Ohara", 97, 20, "MA"),
    (10, "Isaac D'Cruz", 97, 20, "CT"),
    (10, "Jayani Srinivasan", 97, 20, "CA"),
    (10, "Leonard Yang", 97, 20, "NC"),
    (10, "Rohan Singh", 97, 20, "CA"),
    (10, "Shiven Ajwaliya", 97, 20, "MA"),
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
