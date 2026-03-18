#!/usr/bin/env python3
"""
Add Math Kangaroo 2021 Grade 11 National Winners.
Source: https://mathkangaroo.org/mks/wp-content/uploads/2021/08/2021_Level-11_National-Winners.pdf
Resolves (name, state) via students.csv; adds new students as needed.
If student_id exists with missing state, fills state from MK data.
Do NOT merge students with same name in different states - match strictly on (name, state).
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2021" / "grade=11"

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

# grade, name, score, rank, state (from 2021 Level 11 National Winners PDF)
ROWS = [
    (11, "Alex Gu", 120, 1, "CA"),
    (11, "Eric Lee", 120, 1, "CA"),
    (11, "Fengyi Huang", 120, 1, "CA"),
    (11, "James Rydell", 120, 1, "CA"),
    (11, "Andrew Lee", 120, 1, "MA"),
    (11, "Karthik Seetharaman", 120, 1, "MA"),
    (11, "Kevin Zhao", 120, 1, "MA"),
    (11, "Daniel Yuan", 120, 1, "MD"),
    (11, "Daniel Salkinder", 120, 1, "NY"),
    (11, "Arushi Mantri", 120, 1, "OR"),
    (11, "Samuel James Esteban", 120, 1, "VA"),
    (11, "Zimeng Liu", 120, 1, "WA"),
    (11, "Eric Ren", 116, 2, "CA"),
    (11, "Nathra Ramrajvel", 116, 2, "IL"),
    (11, "Stefan Popescu", 116, 2, "VA"),
    (11, "Rahul Bansal", 115, 3, "CA"),
    (11, "Xuhui Miao", 115, 3, "CA"),
    (11, "Dmitriy Shvydkoy", 115, 3, "IL"),
    (11, "Clarence Lam", 113, 4, "MD"),
    (11, "Efe Eroz", 113, 4, "MD"),
    (11, "Natalie Shell", 112, 5, "CT"),
    (11, "Michael Ferguson", 111, 6, "NC"),
    (11, "Tony Tzolov", 111, 6, "PA"),
    (11, "Simon Kerr", 111, 6, "UT"),
    (11, "Joshua Bennett", 111, 6, "VA"),
    (11, "Chirag Verma", 111, 6, "WA"),
    (11, "Jennifer Xia", 110, 7, "IL"),
    (11, "Lawrence Zhao", 110, 7, "IL"),
    (11, "Amy Feng", 110, 7, "NY"),
    (11, "Edward Chen", 109, 8, "GA"),
    (11, "Lucas Guillet", 108, 9, "IL"),
    (11, "Saathvik Selvan", 107, 10, "FL"),
    (11, "Leonard Bian", 107, 10, "MD"),
    (11, "Orion Foo", 105, 11, "MD"),
    (11, "Robert Song", 105, 11, "MD"),
    (11, "Arosh De Silva", 104, 12, "NJ"),
    (11, "Sejal Rathi", 103, 13, "CA"),
    (11, "Parth Dedhiya", 103, 13, "PA"),
    (11, "Sophia Shi", 102, 14, "CA"),
    (11, "Joaquin Perkins", 101, 15, "CA"),
    (11, "Tanush Mittal", 101, 15, "MA"),
    (11, "Satvik Lolla", 101, 15, "MD"),
    (11, "Alexandra Fefelova", 101, 15, "OR"),
    (11, "Kripa Kini", 100, 16, "CA"),
    (11, "Otto Rahmel", 100, 16, "CA"),
    (11, "Eric Wang", 99, 17, "PA"),
    (11, "Justin Li", 99, 17, "TX"),
    (11, "Ankur Moolky", 98, 18, "OR"),
    (11, "Amy Xiu", 97, 19, "MI"),
    (11, "Boyang Zhao", 97, 19, "NJ"),
    (11, "Marcus Ho", 97, 19, "OR"),
    (11, "Oliver Britton", 96, 20, "CA"),
    (11, "Abhinav Mummaneni", 96, 20, "MA"),
    (11, "Jayvik Joshi", 96, 20, "NC"),
    (11, "Carolyn Liu", 96, 20, "NY"),
    (11, "Yunchan Hwang", 96, 20, "VA"),
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
