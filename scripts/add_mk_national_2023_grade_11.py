#!/usr/bin/env python3
"""
Add Math Kangaroo 2023 Grade 11 National Winners.
Resolves (name, state) via students.csv; adds new students as needed.
2023 format: no national_percentile in source.
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2023" / "grade=11"

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
    (11, "Amudhan Gurumoorthy", 120, 1, "CA"),
    (11, "David Wei", 120, 1, "VA"),
    (11, "Maya Viswanathan", 120, 1, "IL"),
    (11, "Michael Lu", 120, 1, "NY"),
    (11, "Sam Rozansky", 120, 1, "NC"),
    (11, "Sebastian Prasanna", 120, 1, "MA"),
    (11, "Shreyas Singh", 120, 1, "IL"),
    (11, "Elena Baskakova", 117, 2, "MA"),
    (11, "Sumedh Vangara", 116, 3, "MD"),
    (11, "Zaee Shah", 116, 3, "CA"),
    (11, "Aditya Gupta", 115, 4, "IL"),
    (11, "Alexander Korchev", 115, 4, "MA"),
    (11, "Patrick Ying", 115, 4, "VA"),
    (11, "Srinivas Arun", 115, 4, "CO"),
    (11, "Priya Adiga", 114, 5, "IL"),
    (11, "Ethan Kuang", 112, 6, "MA"),
    (11, "Harsh Akunuri", 112, 6, "NJ"),
    (11, "Benjamin Jiang", 111, 7, "FL"),
    (11, "Athena Nie", 110, 8, "NY"),
    (11, "Matthew Patkowski", 110, 8, "GA"),
    (11, "Zichang Wang", 109, 9, "VA"),
    (11, "Golden Peng", 108, 10, "MN"),
    (11, "Anna Chumakov", 107, 11, "MA"),
    (11, "Derek Xu", 107, 11, "NY"),
    (11, "Eshaan Debnath", 107, 11, "NJ"),
    (11, "Katherine Nogin", 107, 11, "CA"),
    (11, "Rishabh Mohapatra", 107, 11, "CT"),
    (11, "Hanson Du", 106, 12, "ND"),
    (11, "Vedant Rathi", 106, 12, "IL"),
    (11, "Laura Zhang", 105, 13, "VA"),
    (11, "Haruki Ohara", 104, 14, "MA"),
    (11, "Rohan Dalal", 104, 14, "GA"),
    (11, "Ariel Lyanda-Geller", 103, 15, "IN"),
    (11, "Ayush Kumar", 103, 15, "MA"),
    (11, "Athena Devashish", 102, 16, "MD"),
    (11, "Rahul Tacke", 102, 16, "MA"),
    (11, "Venkatraman Varatharajan", 101, 17, "MA"),
    (11, "Ananya Mahadevan", 100, 18, "CA"),
    (11, "Joshua Cortright", 100, 18, "CA"),
    (11, "Qinwen Zheng", 100, 18, "NY"),
    (11, "Adhitya Chandra", 99, 19, "AZ"),
    (11, "Alexandra Kim", 99, 19, "CA"),
    (11, "Justin Chan", 98, 20, "WA"),
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
