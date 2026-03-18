#!/usr/bin/env python3
"""
Add Math Kangaroo 2024 Grade 11 National Winners.
Resolves (name, state) via students.csv; adds new students as needed.
2024 format: no national_percentile in source.
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2024" / "grade=11"

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
    (11, "Andrew Brahms", 120, 1, "NJ"),
    (11, "Daniel Gilman", 120, 1, "NJ"),
    (11, "David Zhang", 120, 1, "CA"),
    (11, "Gabriel Xu", 120, 1, "VA"),
    (11, "Gregory Roudenko", 120, 1, "VA"),
    (11, "Joyce Huang", 120, 1, "WA"),
    (11, "Lily Tjia", 120, 1, "MA"),
    (11, "Phoebe Pan", 120, 1, "VA"),
    (11, "Shrey Gupta", 120, 1, "FL"),
    (11, "Tatiana Medved", 120, 1, "NC"),
    (11, "Thomas Zheleznyak", 120, 1, "VA"),
    (11, "Timothy Torubarov", 120, 1, "NJ"),
    (11, "William Chen", 120, 1, "CA"),
    (11, "Anshul Gokul", 117, 2, "GA"),
    (11, "Ethan Do", 117, 2, "WA"),
    (11, "Joseph Widjaja", 117, 2, "PA"),
    (11, "Aidan Zhang", 115, 3, "CA"),
    (11, "Alex Hart", 115, 3, "GA"),
    (11, "Eric Jin", 115, 3, "IN"),
    (11, "Jagan Mranal", 115, 3, "MA"),
    (11, "Patrick Liu", 115, 3, "CA"),
    (11, "Sai Palireddy", 115, 3, "GA"),
    (11, "Benjamin Jiang", 114, 4, "FL"),
    (11, "Tianzhuo Lu", 114, 4, "CA"),
    (11, "David Deutsch", 111, 5, "CA"),
    (11, "Jefferson Ji", 111, 5, "MA"),
    (11, "Kevin Zhang", 111, 5, "NJ"),
    (11, "Kylar Cheng", 111, 5, "CA"),
    (11, "Brianna Zheng", 110, 6, "CA"),
    (11, "Sanjay Ravishankar", 110, 6, "CA"),
    (11, "Ishani Agarwal", 109, 7, "CA"),
    (11, "Tejas Ravi", 108, 8, "CA"),
    (11, "Yujun Wang", 108, 8, "CA"),
    (11, "Alexander Ung", 107, 9, "IL"),
    (11, "Rockwell Li", 107, 9, "VA"),
    (11, "Sreeram Sai Vuppala", 107, 9, "NJ"),
    (11, "Ava Park", 106, 10, "CA"),
    (11, "Rohith Raghavan", 106, 10, "MA"),
    (11, "Elita You", 105, 11, "MI"),
    (11, "Joshua Lin", 103, 12, "IL"),
    (11, "Tzuriel Justin Yu", 103, 12, "MA"),
    (11, "Zaven Kouchakdjian", 103, 12, "MA"),
    (11, "Prattay Bhattacharya", 102, 13, "MA"),
    (11, "Rose Cohen", 102, 13, "CA"),
    (11, "Amara Fuchs", 101, 14, "NH"),
    (11, "Bryan Yung", 101, 14, "MD"),
    (11, "Ivan Zhang", 101, 14, "MD"),
    (11, "Shreyan Paliwal", 100, 15, "OR"),
    (11, "Minh Nguyen", 99, 16, "VA"),
    (11, "Ananya Bezbaruah", 98, 17, "WA"),
    (11, "Anthony Dokanchi", 98, 17, "CA"),
    (11, "Haresh Muralidharan", 98, 17, "PA"),
    (11, "Gil Yarsky", 97, 18, "NY"),
    (11, "Kelly Tai", 97, 18, "PA"),
    (11, "Richard Xie", 97, 18, "CA"),
    (11, "Howard Liu", 96, 19, "CA"),
    (11, "Janice Lee", 96, 19, "CA"),
    (11, "Jared Rosen", 96, 19, "MA"),
    (11, "Samarth Das", 96, 19, "TX"),
    (11, "Ethan Nguyen", 95, 20, "CA"),
    (11, "Satvik Sivaraman", 95, 20, "CA"),
    (11, "Tsz Hin Yuen", 95, 20, "CA"),
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
