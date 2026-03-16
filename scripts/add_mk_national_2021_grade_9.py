#!/usr/bin/env python3
"""
Add Math Kangaroo 2021 Grade 9 National Winners.
Source: https://mathkangaroo.org/mks/wp-content/uploads/2021/08/2021_Level-9_National-Winners.pdf
Resolves (name, state) via students.csv; adds new students as needed.
If student_id exists with missing state, fills state from MK data.
Do NOT merge students with same name in different states - match strictly on (name, state).
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2021" / "grade=9"

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

# grade, name, score, rank, state (from 2021 Level 9 National Winners PDF)
ROWS = [
    (9, "Aiden Ye", 120, 1, "CA"),
    (9, "Alexander Bai", 120, 1, "CA"),
    (9, "Amudhan Gurumoorthy", 120, 1, "CA"),
    (9, "Aniketh Tummala", 120, 1, "CA"),
    (9, "Catherine Li", 120, 1, "CA"),
    (9, "David Benjamin Lee", 120, 1, "CA"),
    (9, "Ethan Tran", 120, 1, "CA"),
    (9, "Jamin Xie", 120, 1, "CA"),
    (9, "Kyle Lei", 120, 1, "CA"),
    (9, "Zaee Shah", 120, 1, "CA"),
    (9, "Aaron Hu", 120, 1, "FL"),
    (9, "Maya Viswanathan", 120, 1, "IL"),
    (9, "Sebastian Prasanna", 120, 1, "MA"),
    (9, "Kevin Tang", 120, 1, "MO"),
    (9, "Harsh Akunuri", 120, 1, "NJ"),
    (9, "Matthew Fakler", 120, 1, "NV"),
    (9, "Derek Xu", 120, 1, "NY"),
    (9, "Angelina Berg", 120, 1, "PA"),
    (9, "David Wei", 120, 1, "VA"),
    (9, "Vishal Nandakumar", 120, 1, "VA"),
    (9, "Isaac Dcruz", 117, 2, "CT"),
    (9, "Raina Wu", 116, 3, "WA"),
    (9, "Avi Gupta", 115, 4, "CA"),
    (9, "Srinivas Arun", 115, 4, "CO"),
    (9, "Shreyas Singh", 115, 4, "IL"),
    (9, "Julian Vertigan", 115, 4, "LA"),
    (9, "Elena Baskakova", 115, 4, "MA"),
    (9, "Ethan Kuang", 115, 4, "MA"),
    (9, "Thomas Du", 115, 4, "MA"),
    (9, "Stephen Zhang", 115, 4, "MD"),
    (9, "Michael Lu", 115, 4, "NY"),
    (9, "Zayeed Saffat", 115, 4, "OR"),
    (9, "Ria Garg", 115, 4, "TX"),
    (9, "Katherine Nogin", 112, 5, "CA"),
    (9, "Canis Li", 111, 6, "CA"),
    (9, "Daniel Matsui Smola", 111, 6, "CA"),
    (9, "Jack Fasching", 111, 6, "CA"),
    (9, "Anvi Padhi", 111, 6, "IL"),
    (9, "Evan Zhang", 111, 6, "MA"),
    (9, "Roshen Nair", 111, 6, "OR"),
    (9, "Andon Epp", 111, 6, "TX"),
    (9, "Mihika Dusad", 111, 6, "VA"),
    (9, "Isaac McGreevy", 110, 7, "CA"),
    (9, "Jannie Xu", 110, 7, "CA"),
    (9, "Ryan Chin", 110, 7, "CA"),
    (9, "Wesley Rullman", 110, 7, "CA"),
    (9, "Vedant Aryan", 110, 7, "CT"),
    (9, "Aditya Gupta", 110, 7, "IL"),
    (9, "Ariel Lyanda-Geller", 110, 7, "IN"),
    (9, "Charles Fang", 110, 7, "MA"),
    (9, "Jessica Wang", 110, 7, "MA"),
    (9, "Annie Guo", 110, 7, "MD"),
    (9, "Parth Joshi", 110, 7, "NV"),
    (9, "Samarth Das", 110, 7, "TX"),
    (9, "Arsenii Zharkov", 110, 7, "VA"),
    (9, "Arnav Busani", 108, 8, "MO"),
    (9, "Prisha Jain", 107, 9, "CA"),
    (9, "Lakshya Jain", 107, 9, "MA"),
    (9, "Gabe Nather", 107, 9, "MD"),
    (9, "Sumedh Vangara", 107, 9, "MD"),
    (9, "Athena Nie", 107, 9, "NY"),
    (9, "Mingchuan Cheng", 107, 9, "UT"),
    (9, "Timason Wan", 107, 9, "WA"),
    (9, "Harshil Pathri", 106, 10, "CA"),
    (9, "Nathan Han", 106, 10, "CA"),
    (9, "Sneha Muppalla", 106, 10, "CA"),
    (9, "Peter Liang", 106, 10, "MA"),
    (9, "Swann Li", 106, 10, "MA"),
    (9, "Athena Devashish", 106, 10, "MD"),
    (9, "Polaris Hayes", 106, 10, "NJ"),
    (9, "Peter Duers", 106, 10, "NY"),
    (9, "Alicia Ye", 106, 10, "OR"),
    (9, "Shreev Goyal", 106, 10, "TX"),
    (9, "Satvik Kabbur", 106, 10, "WA"),
    (9, "Ellie Feng", 105, 11, "AR"),
    (9, "Bhadra Rupesh", 105, 11, "CA"),
    (9, "Junsung Henry Kim", 105, 11, "CA"),
    (9, "Rinoa Oliver", 105, 11, "CA"),
    (9, "Anne Wu", 105, 11, "MA"),
    (9, "Veronika Moroz", 105, 11, "MA"),
    (9, "Kriste An", 104, 12, "CA"),
    (9, "Alexander Korchev", 103, 13, "MA"),
    (9, "Jakub Pienkowski", 103, 13, "NY"),
    (9, "Filip Icev", 103, 13, "WA"),
    (9, "Alexander Chen", 102, 14, "AZ"),
    (9, "Joelle Kim", 102, 14, "CA"),
    (9, "Ronit Kapoor", 102, 14, "CA"),
    (9, "Riddhi Sharma", 102, 14, "CT"),
    (9, "Varun Suvvari", 102, 14, "NV"),
    (9, "Matthew Patkowski", 101, 15, "AL"),
    (9, "Angela Yang", 101, 15, "CA"),
    (9, "Michael Liu", 101, 15, "CA"),
    (9, "Ronak Ramesh", 101, 15, "CT"),
    (9, "Sharanya Chatterjee", 101, 15, "FL"),
    (9, "Gavin Valentino", 101, 15, "GA"),
    (9, "Ryan Ferguson", 101, 15, "NC"),
    (9, "Sonny Chen", 101, 15, "VA"),
    (9, "Sam Tippett", 101, 15, "WA"),
    (9, "Abhiraj Bhashkar", 100, 16, "CA"),
    (9, "Lucia Moscola", 100, 16, "CA"),
    (9, "Grace Murray", 100, 16, "IL"),
    (9, "Venkatraman Varatharajan", 100, 16, "MA"),
    (9, "Dohyeong Lee", 98, 17, "CA"),
    (9, "Kangsan Yoon", 98, 17, "GU"),
    (9, "Rithik Thekiniath", 98, 17, "IL"),
    (9, "Sai Javvadi", 98, 17, "KY"),
    (9, "Kyvalya Reddy", 98, 17, "WA"),
    (9, "Ananya Mahadevan", 97, 18, "CA"),
    (9, "Maya Sriram", 97, 18, "CA"),
    (9, "Raymond Yao", 97, 18, "GA"),
    (9, "Jasmine Xing", 97, 18, "MA"),
    (9, "Sayan Bhattacharya", 97, 18, "NH"),
    (9, "Hyewon Park", 97, 18, "NJ"),
    (9, "Aashrith Chejerla", 97, 18, "NV"),
    (9, "Chloe Parke", 97, 18, "UT"),
    (9, "William Liu", 97, 18, "WA"),
    (9, "Alexander Radulescu", 96, 19, "CA"),
    (9, "Stanley Shi", 96, 19, "CA"),
    (9, "Ethan Zhang", 96, 19, "IL"),
    (9, "Vedant Rathi", 96, 19, "IL"),
    (9, "Apurva Varigonda", 96, 19, "MA"),
    (9, "Kaloyan Draganov", 96, 19, "MA"),
    (9, "Rahul Tacke", 96, 19, "MA"),
    (9, "Evan Zhang", 96, 19, "MD"),
    (9, "Eshaan Debnath", 96, 19, "NJ"),
    (9, "Adil Oryspayev", 96, 19, "NY"),
    (9, "Ryan Peng", 96, 19, "NY"),
    (9, "Asher Wu", 96, 19, "WA"),
    (9, "Victoria Outkin", 95, 20, "NM"),
    (9, "Shoshana Elgart", 95, 20, "VA"),
]


def load_students():
    key_to_row = {}
    name_to_blank_state_rows = {}
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
                if not state:
                    nl = name.lower()
                    if nl not in name_to_blank_state_rows:
                        name_to_blank_state_rows[nl] = []
                    name_to_blank_state_rows[nl].append(r)
            for a in (row.get("alias") or "").split("|"):
                a = a.strip()
                if a:
                    key = (a.lower(), state)
                    if key not in key_to_row:
                        key_to_row[key] = r
    return key_to_row, name_to_blank_state_rows, next_id


def main():
    key_to_row, name_to_blank_state_rows, next_id = load_students()
    new_students = []
    out_rows = []
    state_updates = {}

    for grade, name, score, rank, state_abbrev in ROWS:
        state = STATE_ABBREV_TO_FULL.get(state_abbrev.strip().upper(), state_abbrev.strip())
        name_clean = name.strip()
        key = (name_clean.lower(), state)
        row = key_to_row.get(key)
        if row:
            out_rows.append((row["student_id"], row["student_name"], state, grade, score, rank, ""))
            continue

        blank_rows = name_to_blank_state_rows.get(name_clean.lower(), [])
        if len(blank_rows) == 1:
            row = blank_rows[0]
            state_updates[row["student_id"]] = state
            key_to_row[key] = row
            row["state"] = state
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

    if new_students:
        with open(STUDENTS_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["student_id", "student_name", "state", "team_ids", "alias", "gender", "grade_in_2026"], extrasaction="ignore")
            for r in new_students:
                w.writerow(r)
        print(f"Added {len(new_students)} new students")

    if state_updates:
        with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = list(reader.fieldnames or [])
        for row in rows:
            sid_s = (row.get("student_id") or "").strip()
            try:
                sid = int(sid_s)
            except ValueError:
                continue
            if sid in state_updates:
                row["state"] = state_updates[sid]
        tmp_path = STUDENTS_CSV.with_suffix(".csv.tmp")
        with tmp_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        tmp_path.replace(STUDENTS_CSV)
        print(f"Filled missing state for {len(state_updates)} students: {state_updates}")

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
