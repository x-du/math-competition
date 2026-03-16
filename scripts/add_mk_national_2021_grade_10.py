#!/usr/bin/env python3
"""
Add Math Kangaroo 2021 Grade 10 National Winners.
Source: https://mathkangaroo.org/mks/wp-content/uploads/2021/08/2021_Level-10_National-Winners.pdf
Resolves (name, state) via students.csv; adds new students as needed.
If student_id exists with missing state, fills state from MK data.
Do NOT merge students with same name in different states - match strictly on (name, state).
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2021" / "grade=10"

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

# grade, name, score, rank, state (from 2021 Level 10 National Winners PDF)
ROWS = [
    (10, "Daniel Zhao", 120, 1, "AL"),
    (10, "Siddharth Doppalapudi", 120, 1, "AL"),
    (10, "Sai Konkimalla", 120, 1, "AZ"),
    (10, "Aman Jain", 120, 1, "CA"),
    (10, "Arianna Cao", 120, 1, "CA"),
    (10, "Arul Kolla", 120, 1, "CA"),
    (10, "Lisa Fung", 120, 1, "CA"),
    (10, "Nilay Mishra", 120, 1, "CA"),
    (10, "Richard Zhu", 120, 1, "CA"),
    (10, "Riya Gupta", 120, 1, "CA"),
    (10, "Saanvi Thummalapally", 120, 1, "CA"),
    (10, "Nikhil Mudumbi", 120, 1, "NJ"),
    (10, "Megan Davi", 120, 1, "NV"),
    (10, "Ali El Moselhy", 120, 1, "NY"),
    (10, "Julia Kozak", 120, 1, "NY"),
    (10, "Alan Kappler", 120, 1, "OR"),
    (10, "Suyash Pandit", 120, 1, "OR"),
    (10, "Jessica Wang", 120, 1, "VA"),
    (10, "Noah Shi", 120, 1, "WA"),
    (10, "Stuti Agarwal", 117, 2, "CA"),
    (10, "Nicole Shen", 116, 3, "CA"),
    (10, "Shuming Zhao", 116, 3, "CA"),
    (10, "Arul Mazumder", 116, 3, "MA"),
    (10, "Artem Torubarov", 116, 3, "NJ"),
    (10, "Siddanth Pabba", 116, 3, "NJ"),
    (10, "Vishal Thyagarajan", 116, 3, "TX"),
    (10, "Alan Vladimiroff", 116, 3, "VA"),
    (10, "Lynn Tao", 116, 3, "VA"),
    (10, "Daniel McCrorey", 116, 3, "WA"),
    (10, "Anouksha Bansal", 115, 4, "AZ"),
    (10, "Ayan Bhatia", 115, 4, "CA"),
    (10, "Kaden Nguyen", 115, 4, "CA"),
    (10, "Kavan Doctor", 115, 4, "CA"),
    (10, "Qinzi Wang", 115, 4, "CA"),
    (10, "Shuya Wu", 115, 4, "CA"),
    (10, "Naveen Kannan", 115, 4, "KS"),
    (10, "Aditya Koul", 115, 4, "MA"),
    (10, "William Du", 115, 4, "MA"),
    (10, "Samantha Wu", 115, 4, "MD"),
    (10, "Nathan Wang", 115, 4, "NV"),
    (10, "John Gupta-She", 112, 5, "NY"),
    (10, "Ishir Garg", 111, 6, "CA"),
    (10, "Victor Li", 111, 6, "OR"),
    (10, "Alexey Tatarinov", 111, 6, "PA"),
    (10, "Madeleine Volfbeyn", 111, 6, "WA"),
    (10, "Victor Donchenko", 110, 7, "CA"),
    (10, "Sharvaa Selvan", 110, 7, "FL"),
    (10, "Richard Yu", 110, 7, "GA"),
    (10, "Daniel Ma", 110, 7, "IL"),
    (10, "Carlos Reyes", 110, 7, "MA"),
    (10, "Daniel Long", 110, 7, "NJ"),
    (10, "Kishan Bava", 110, 7, "NJ"),
    (10, "Nicholas Chang", 108, 8, "CA"),
    (10, "David Magidson", 108, 8, "WA"),
    (10, "Mark Neumann", 107, 9, "CA"),
    (10, "Ari Wang", 107, 9, "CO"),
    (10, "Maya Smith", 107, 9, "MA"),
    (10, "Veena Kailad", 107, 9, "MD"),
    (10, "Aswath Karai", 107, 9, "MI"),
    (10, "Ananth Kashyap", 107, 9, "PA"),
    (10, "Isaac Lee", 106, 10, "CA"),
    (10, "Ramsey Makan", 106, 10, "FL"),
    (10, "Shishir Vargheese", 106, 10, "KS"),
    (10, "Sanjay Govindarajan", 106, 10, "MA"),
    (10, "Vivek Vallurupalli", 106, 10, "MA"),
    (10, "Keval Shah", 106, 10, "NC"),
    (10, "Nividh Singh", 106, 10, "OR"),
    (10, "Alexander Bloom", 105, 11, "CA"),
    (10, "Ganesh Sankar", 105, 11, "CA"),
    (10, "Alexander Tong", 105, 11, "MA"),
    (10, "Amol Rama", 104, 12, "CA"),
    (10, "Samarth Pusegaonkar", 102, 13, "CA"),
    (10, "Isaac Mitchell", 102, 13, "CO"),
    (10, "Rohan Bandaru", 102, 13, "MA"),
    (10, "Dennis Malikov", 102, 13, "MD"),
    (10, "Frank Xiao", 101, 14, "CA"),
    (10, "Guanzhen Song", 101, 14, "CA"),
    (10, "Riley Bonner", 101, 14, "CA"),
    (10, "Stewart Kwok", 101, 14, "CA"),
    (10, "Alisha Paul", 101, 14, "CT"),
    (10, "Cody Wang", 101, 14, "GA"),
    (10, "Krishna Purimetla", 101, 14, "MA"),
    (10, "Kimberly You", 101, 14, "MI"),
    (10, "Aaron Gao", 101, 14, "OR"),
    (10, "Constantin Matros", 101, 14, "PA"),
    (10, "Siming Tang", 101, 14, "PA"),
    (10, "Alexander Chung", 101, 14, "VA"),
    (10, "Maya Vendhan", 100, 15, "CO"),
    (10, "Jake Tae", 100, 15, "GU"),
    (10, "Maxwell Lin", 100, 15, "MA"),
    (10, "Sean Shang", 100, 15, "MA"),
    (10, "Heerok Das", 100, 15, "MD"),
    (10, "Sean O-Lee", 100, 15, "NV"),
    (10, "Thomas Breydo", 100, 15, "NY"),
    (10, "Kiran Parthasarathy", 99, 16, "OR"),
    (10, "Peter Wang", 98, 17, "CA"),
    (10, "Ritvik Garg", 98, 17, "MA"),
    (10, "Eunyul Kim", 97, 18, "CA"),
    (10, "Rohan Mahesh", 97, 18, "CA"),
    (10, "Viren Mehta", 97, 18, "CA"),
    (10, "Alexander Khilko", 97, 18, "CT"),
    (10, "Navid Tajkhorshid", 97, 18, "IL"),
    (10, "Rebecca Serodio", 97, 18, "MA"),
    (10, "Alexander Yang", 97, 18, "OR"),
    (10, "Caleb Arulandu", 97, 18, "VA"),
    (10, "Amruta Dharmapurikar", 96, 19, "CA"),
    (10, "Aniket Kamat", 96, 19, "CA"),
    (10, "Phoebe Ong", 96, 19, "CA"),
    (10, "Joshua Caruso", 96, 19, "GA"),
    (10, "Rishika Agarwal", 96, 19, "MA"),
    (10, "Yulong Lian", 96, 19, "MA"),
    (10, "Alexandra Levinshteyn", 96, 19, "MN"),
    (10, "David Rubin", 96, 19, "NY"),
    (10, "Gabriel Ortner", 96, 19, "VA"),
    (10, "Sanjay Shivathanu Adhikesaven", 95, 20, "CA"),
    (10, "Sophie Zhu", 95, 20, "CA"),
    (10, "Denis Proskuryakov", 95, 20, "CT"),
    (10, "Victor Proykov", 95, 20, "NV"),
    (10, "Shashwat Rao", 95, 20, "VA"),
    (10, "Payton Gergen", 95, 20, "WA"),
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
