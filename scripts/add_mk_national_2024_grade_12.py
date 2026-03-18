#!/usr/bin/env python3
"""
Add Math Kangaroo 2024 Grade 12 National Winners.
Resolves (name, state) via students.csv; adds new students as needed.
2024 format: no national_percentile in source.
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2024" / "grade=12"

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

# grade, name, score, rank, state (no percentile in 2024 source)
ROWS = [
    (12, "Aaron Hu", 120, 1, "FL"),
    (12, "David Wei", 120, 1, "VA"),
    (12, "Derek Xu", 120, 1, "NY"),
    (12, "Elena Baskakova", 120, 1, "MA"),
    (12, "Michael Lu", 120, 1, "NY"),
    (12, "Patrick Ying", 120, 1, "VA"),
    (12, "Sam Rozansky", 120, 1, "NC"),
    (12, "Shreyas Singh", 120, 1, "IL"),
    (12, "Srinivas Arun", 120, 1, "CO"),
    (12, "Zaee Shah", 120, 1, "CA"),
    (12, "Sebastian Prasanna", 117, 2, "MA"),
    (12, "Golden Peng", 116, 3, "MN"),
    (12, "Chinmay Govind", 115, 4, "PA"),
    (12, "Justin Chan", 111, 5, "WA"),
    (12, "Aditya Gupta", 108, 6, "IL"),
    (12, "Harsh Akunuri", 108, 6, "NJ"),
    (12, "James Kim", 108, 6, "AL"),
    (12, "Maya Viswanathan", 108, 6, "IL"),
    (12, "Taohan Lin", 107, 7, "VA"),
    (12, "Rahul Tacke", 106, 8, "MA"),
    (12, "Ryan Chin", 106, 8, "TX"),
    (12, "Eshaan Debnath", 105, 9, "NJ"),
    (12, "Priya Adiga", 103, 10, "IL"),
    (12, "Ethan Kuang", 101, 11, "MA"),
    (12, "Vedant Rathi", 99, 12, "IL"),
    (12, "Ananya Mahadevan", 97, 13, "CA"),
    (12, "Kangsan Yoon", 92, 14, "GU"),
    (12, "Alexandra Kim", 91, 15, "CA"),
    (12, "Arjun Saha Choudhury", 88, 16, "NJ"),
    (12, "Katherine Li", 84, 17, "AZ"),
    (12, "Sharanya Chatterjee", 83, 18, "FL"),
    (12, "Anshul Prabu", 81, 19, "CA"),
    (12, "Jakub Pienkowski", 81, 19, "NY"),
    (12, "Jason Nguyen", 81, 19, "TX"),
    (12, "Victor Longinov", 80, 20, "MA"),
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
    # Compute fractional mcp_rank for ties
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
