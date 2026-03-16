#!/usr/bin/env python3
"""
Add Math Kangaroo 2022 Grade 12 National Winners.
Source: https://mathkangaroo.org/mks/wp-content/uploads/2022/05/2022_Level-12_National-Winners.pdf
Resolves (name, state) via students.csv; adds new students as needed.
Do NOT merge students with same name in different states - match strictly on (name, state).
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2022" / "grade=12"

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

# grade, name, score, rank, state (from 2022 Level 12 National Winners PDF)
ROWS = [
    (12, "Alex Gu", 120, 1, "CA"),
    (12, "Arushi Mantri", 120, 1, "OR"),
    (12, "Chirag Verma", 120, 1, "WA"),
    (12, "Clarence Lam", 120, 1, "MD"),
    (12, "Daniel Salkinder", 120, 1, "NY"),
    (12, "Dmitriy Shvydkoy", 120, 1, "IL"),
    (12, "James Rydell", 120, 1, "CA"),
    (12, "Justin Li", 120, 1, "TX"),
    (12, "Kevin Zhao", 120, 1, "MA"),
    (12, "Nathra Ramrajvel", 120, 1, "IL"),
    (12, "Saathvik Selvan", 120, 1, "FL"),
    (12, "Tony Tzolov", 120, 1, "PA"),
    (12, "Andrew Lee", 117, 2, "MA"),
    (12, "Daniel Yuan", 117, 2, "MD"),
    (12, "Eric Wang", 116, 3, "PA"),
    (12, "Garima Bansal", 116, 3, "CA"),
    (12, "Rahul Bansal", 116, 3, "CA"),
    (12, "Eric Lee", 115, 4, "CA"),
    (12, "Michael Ferguson", 115, 4, "NC"),
    (12, "Ori Helmer", 115, 4, "IL"),
    (12, "Sathvik Medapati", 115, 4, "NJ"),
    (12, "Shihan Kanungo", 115, 4, "CA"),
    (12, "Stefan Popescu", 115, 4, "VA"),
    (12, "Yunchan Hwang", 115, 4, "VA"),
    (12, "Kevin Xu", 112, 5, "VA"),
    (12, "Joshua Bennett", 111, 6, "VA"),
    (12, "Efe Eroz", 110, 7, "MD"),
    (12, "Lucas Guillet", 110, 7, "IL"),
    (12, "Simon Kerr", 110, 7, "UT"),
    (12, "Leonard Bian", 107, 8, "MD"),
    (12, "Joaquin Perkins", 105, 9, "CA"),
    (12, "Spencer May", 103, 10, "NH"),
    (12, "Mark Chudnovsky", 102, 11, "MA"),
    (12, "Ryan Badi", 98, 12, "NJ"),
    (12, "Ryan Grosso", 97, 13, "AZ"),
    (12, "Xinyi Li", 97, 13, "TX"),
    (12, "Andrew Dunstan", 94, 14, "UT"),
    (12, "Sara Kapasi", 94, 14, "GA"),
    (12, "Pranav Bandla", 92, 15, "VA"),
    (12, "Vidit Pokharna", 91, 16, "FL"),
    (12, "Ankur Moolky", 90, 17, "OR"),
    (12, "David Arthur", 89, 18, "WI"),
    (12, "Jayvik Joshi", 89, 18, "NC"),
    (12, "Theo Bakshi", 89, 18, "CA"),
    (12, "Iris Levey", 83, 19, "NH"),
    (12, "Sarah Lepkowitz", 81, 20, "CA"),
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
