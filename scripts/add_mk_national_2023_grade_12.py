#!/usr/bin/env python3
"""
Add Math Kangaroo 2023 Grade 12 National Winners.
Resolves (name, state) via students.csv; adds new students as needed.
2023 format: no national_percentile in source.
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2023" / "grade=12"

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
    (12, "Alan Vladimiroff", 120, 1, "VA"),
    (12, "Arianna Cao", 120, 1, "CA"),
    (12, "Kavan Doctor", 120, 1, "CA"),
    (12, "Sai Konkimalla", 120, 1, "AZ"),
    (12, "Suyash Pandit", 120, 1, "OR"),
    (12, "Navid Tajkhorshid", 116, 2, "IL"),
    (12, "Nikhil Mudumbi", 116, 2, "NJ"),
    (12, "Arul Kolla", 115, 3, "CA"),
    (12, "Kaden Nguyen", 115, 3, "CA"),
    (12, "Sharvaa Selvan", 115, 3, "FL"),
    (12, "Ganesh Sankar", 112, 4, "CA"),
    (12, "Alan Kappler", 111, 5, "NV"),
    (12, "David Rubin", 110, 6, "NY"),
    (12, "Noah Shi", 110, 6, "WA"),
    (12, "Stewart Kwok", 108, 7, "CA"),
    (12, "Tanmay Gupta", 107, 8, "MA"),
    (12, "Daniel Li", 106, 9, "MD"),
    (12, "Isaac Mitchell", 106, 9, "CO"),
    (12, "Daniel Zhao", 105, 10, "AL"),
    (12, "Krishna Grandhe", 102, 11, "TX"),
    (12, "Shreeya Garg", 102, 11, "CA"),
    (12, "Ari Wang", 101, 12, "CO"),
    (12, "Mark Neumann", 101, 12, "MD"),
    (12, "David Magidson", 98, 13, "WA"),
    (12, "Daniel (Dawn) McCrorey", 95, 14, "WA"),
    (12, "Maya Smith", 91, 15, "MA"),
    (12, "Phoebe Ong", 91, 15, "CA"),
    (12, "Riley Bonner", 90, 16, "CA"),
    (12, "Steven Reid", 90, 16, "GA"),
    (12, "Colin Colbert", 88, 17, "NV"),
    (12, "Keerthan Kumarappan", 88, 17, "NY"),
    (12, "Alexey Tatarinov", 85, 18, "PA"),
    (12, "Gabriel Kanarek", 84, 19, "MD"),
    (12, "Rishabh Purayil", 83, 20, "IL"),
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
