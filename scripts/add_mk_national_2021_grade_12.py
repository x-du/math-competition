#!/usr/bin/env python3
"""
Add Math Kangaroo 2021 Grade 12 National Winners.
Source: https://mathkangaroo.org/mks/wp-content/uploads/2021/08/2021_Level-12_National-Winners.pdf
Resolves (name, state) via students.csv; adds new students as needed.
If student_id exists with missing state, fills state from MK data.
Do NOT merge students with same name in different states - match strictly on (name, state).
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2021" / "grade=12"

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

# grade, name, score, rank, state (from 2021 Level 12 National Winners PDF)
ROWS = [
    (12, "Rahul Thomas", 120, 1, "CO"),
    (12, "Alan Abraham", 120, 1, "KS"),
    (12, "Chinmay Krishna", 120, 1, "KS"),
    (12, "Gabriel Wu", 120, 1, "MD"),
    (12, "Parth Shastri", 120, 1, "NJ"),
    (12, "Andrei Mandelshtam", 116, 2, "CA"),
    (12, "Sophie Wu", 116, 2, "CA"),
    (12, "Alice Wu", 116, 2, "MA"),
    (12, "Samuel Lerner", 116, 2, "MA"),
    (12, "Tyler Weigand", 115, 3, "CA"),
    (12, "Alex Hu", 115, 3, "FL"),
    (12, "Saketh Mynampati", 115, 3, "MA"),
    (12, "Daniel Dickman", 115, 3, "WA"),
    (12, "Kishore Rajesh", 112, 4, "AZ"),
    (12, "Youbin Cho", 112, 4, "CA"),
    (12, "Praneet Rathi", 112, 4, "IL"),
    (12, "Gregory Pylypovych", 112, 4, "NJ"),
    (12, "Timothy Palamarchuk", 112, 4, "VA"),
    (12, "David Mengel", 111, 5, "IL"),
    (12, "Aayush Gupta", 111, 5, "NJ"),
    (12, "Pranav Addepalli", 110, 6, "IL"),
    (12, "Neil Kale", 110, 6, "MA"),
    (12, "Divyesh Murugan", 110, 6, "NJ"),
    (12, "Ryan Tsai", 108, 7, "CA"),
    (12, "Jennifer Zhang", 107, 8, "CA"),
    (12, "Ashish Dhanalakota", 107, 8, "MO"),
    (12, "Sri Jaladi", 107, 8, "MO"),
    (12, "Kanav Mittal", 106, 9, "CA"),
    (12, "Marcus Gozon", 106, 9, "MI"),
    (12, "Philip Xue", 106, 9, "OR"),
    (12, "Taiki Aiba", 105, 10, "MA"),
    (12, "Sarah Mitchell", 103, 11, "CO"),
    (12, "Ayush Agrawal", 102, 12, "WA"),
    (12, "Agustya Matheth", 101, 13, "AZ"),
    (12, "George Radoslavov", 101, 13, "CT"),
    (12, "Jerrae Schroff", 99, 14, "CA"),
    (12, "Michael Doboli", 99, 14, "NY"),
    (12, "Alicia Chen", 98, 15, "IL"),
    (12, "Rohit Chand", 97, 16, "KS"),
    (12, "Lydia Ignatova", 94, 17, "CA"),
    (12, "Ji Hong Cha", 94, 17, "GU"),
    (12, "Sai Vedagiri", 94, 17, "NJ"),
    (12, "Khushi Kohli", 93, 18, "KS"),
    (12, "Michael Wojdak", 93, 18, "VA"),
    (12, "Kieran Campbell", 92, 19, "NY"),
    (12, "Pranav Mandyam", 92, 19, "OR"),
    (12, "Eric Li", 92, 19, "VA"),
    (12, "Brian Joseph", 88, 20, "GU"),
]


def load_students():
    key_to_row = {}
    name_to_blank_state_rows = {}  # name_lower -> list of rows with blank state
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
    state_updates = {}  # sid -> state (for students with missing state)

    for grade, name, score, rank, state_abbrev in ROWS:
        state = STATE_ABBREV_TO_FULL.get(state_abbrev.strip().upper(), state_abbrev.strip())
        name_clean = name.strip()
        key = (name_clean.lower(), state)
        row = key_to_row.get(key)
        if row:
            out_rows.append((row["student_id"], row["student_name"], state, grade, score, rank, ""))
            continue

        # Try match by name with blank state (exactly one such student)
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

    # Append new students
    if new_students:
        with open(STUDENTS_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["student_id", "student_name", "state", "team_ids", "alias", "gender", "grade_in_2026"], extrasaction="ignore")
            for r in new_students:
                w.writerow(r)
        print(f"Added {len(new_students)} new students")

    # Update missing state for existing students
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
