#!/usr/bin/env python3
"""
Add Math Kangaroo 2025 Grade 12 National Winners.
Resolves (name, state) via students.csv; adds new students as needed.
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2025" / "grade=12"

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

# grade, name, score, rank, percentile, center, city, state
ROWS = [
    (12, "Alex Hart", 120, 1, 97.4, "Emory University", "Atlanta", "GA"),
    (12, "Andrew Brahms", 120, 1, 97.4, "New Jersey Enrichment Academy", "Millburn", "NJ"),
    (12, "Christopher Dickman", 120, 1, 97.4, "C2 Education Sammamish", "Sammamish", "WA"),
    (12, "David Deutsch", 120, 1, 97.4, "Pacific Beach Elementary", "San Diego", "CA"),
    (12, "David Zhang", 120, 1, 97.4, "Thomas Hart Middle School", "Pleasanton", "CA"),
    (12, "Anjena Raja", 115, 2, 88.7, "Integna's Orange Elephant", "LA CRESCENTA", "CA"),
    (12, "Elita You", 115, 2, 88.7, "Ann Hua Chinese School ONLINE", "Ann Arbor", "MI"),
    (12, "Eric Jin", 115, 2, 88.7, "Math Kangaroo at Purdue", "West Lafayette", "IN"),
    (12, "Ethan Do", 115, 2, 88.7, "Mathnasium of Bellevue", "Bellevue", "WA"),
    (12, "Ivan Zhang", 115, 2, 88.7, "CCACC Academy Center", "Rockville", "MD"),
    (12, "Kylar Cheng", 115, 2, 88.7, "Geffen Academy at UCLA", "Los Angeles", "CA"),
    (12, "Rockwell Li", 115, 2, 88.7, "Old Dominion University", "Norfolk", "VA"),
    (12, "Rohith Raghavan", 115, 2, 88.7, "Einstein's Workshop", "Burlington", "MA"),
    (12, "Satvik Sivaraman", 115, 2, 88.7, "AlphaStar Academy", "Cupertino", "CA"),
    (12, "Timothy Torubarov", 115, 2, 88.7, "MindzQ Education", "Fair Lawn", "NJ"),
    (12, "Aidan Zhang", 110, 3, 83.5, "NextGen Learning Center ONLINE", "Los Angeles", "CA"),
    (12, "Daniel Gilman", 110, 3, 83.5, "MindzQ Education", "Fair Lawn", "NJ"),
    (12, "Gary Sun", 110, 3, 83.5, "Clear Lake High School", "Houston", "TX"),
    (12, "Gregory Roudenko", 110, 3, 83.5, "Russian Kids House", "Reston", "VA"),
    (12, "Jagan Mranal", 110, 3, 83.5, "RSM Metrowest", "Framingham", "MA"),
    (12, "Shrey Gupta", 110, 3, 83.5, "Orlando Math Circle Maitland REMOTE", "Maitland", "FL"),
    (12, "Anshul Gokul", 108, 4, 82.6, "Forsyth County Schools", "Cumming", "GA"),
    (12, "Joshua Lin", 107, 5, 80, "RSM Schaumburg", "Hoffman Estates", "IL"),
    (12, "Lily Tjia", 107, 5, 80, "RSM West Newton", "Newtonville", "MA"),
    (12, "Thiruchelvam Thirunavukkarasu", 107, 5, 80, "Radiance Learning of Bellevue", "Bellevue", "WA"),
    (12, "Daniil Arnold", 106, 6, 78.3, "RSM Plano", "Plano", "TX"),
    (12, "SAI PALIREDDY", 106, 6, 78.3, "Curie Learning of Cumming", "Cumming", "GA"),
    (12, "Gabriel Xu", 105, 7, 77.4, "Sunshine Academy Vienna", "Vienna", "VA"),
    (12, "JOYCE HUANG", 101, 8, 74.8, "Mathnasium of Redmond", "Redmond", "WA"),
    (12, "Kevin Park", 101, 8, 74.8, "Old Dominion University", "Norfolk", "VA"),
    (12, "Sofia Alfenito", 101, 8, 74.8, "SchoolNova at Stony Brook", "Stony Brook", "NY"),
    (12, "Justin Bernal", 98, 9, 73.9, "Mathnasium of Sammamish", "Sammamish", "WA"),
    (12, "Miles Wind", 97, 10, 71.3, "Jon M. Huntsman School of Business", "Logan", "UT"),
    (12, "Sreeram Sai Vuppala", 97, 10, 71.3, "DARUL ARQAM", "South River", "NJ"),
    (12, "Yejoon Ham", 97, 10, 71.3, "MMC&M ONLINE", "Kingston", "TN"),
    (12, "Cameron Kelm", 96, 11, 69.6, "California State University Fresno", "Fresno", "CA"),
    (12, "Hamed Fazel-Rezai", 96, 11, 69.6, "Silicon Valley ONLINE", "San Jose", "CA"),
    (12, "Isaac Young", 91, 12, 67, "Louisiana School for Math, Science, and the Arts ONLINE", "Natchitoches", "LA"),
    (12, "Prattay Bhattacharya", 91, 12, 67, "RSM Winchester", "Winchester", "MA"),
    (12, "Rose Cohen", 91, 12, 67, "Geffen Academy at UCLA", "Los Angeles", "CA"),
    (12, "Lyev Pitram", 90, 13, 66.1, "Mathnasium of Center City", "Philadelphia", "PA"),
    (12, "Neelansh Samanta", 89, 14, 65.2, "Carnegie Mellon University", "Pittsburgh", "PA"),
    (12, "Dakota Pippins", 87, 15, 62.6, "Russian School of Mathematics Chevy Chase", "Chevy Chase", "MD"),
    (12, "Daron Simmons", 87, 15, 62.6, "Orlando Math Circle", "Maitland", "FL"),
    (12, "Krrish Mishra", 87, 15, 62.6, "Hanover High School ONLINE", "Hanover", "NH"),
    (12, "Eli Tomiak", 86, 16, 59.1, "Southwest Virginia Governor's School Pulaski", "Dublin", "VA"),
    (12, "Kriti Nandakumar", 86, 16, 59.1, "UNC CH Math Dept Phillips Bldg", "Chapel Hill", "NC"),
    (12, "Smithi Gopalakrishnan", 86, 16, 59.1, "RSM Sugar Land", "Sugar Land", "TX"),
    (12, "Sruthi Gopalakrishnan", 86, 16, 59.1, "RSM Sugar Land", "Sugar Land", "TX"),
    (12, "Aditya Singh Panwar", 83, 17, 56.5, "RSM Plano", "Plano", "TX"),
    (12, "Anjan Yalamanchili", 83, 17, 56.5, "RSM Southern NH", "Nashua", "NH"),
    (12, "Shashwath Inamdar", 83, 17, 56.5, "Secaucus High School", "Secaucus", "NJ"),
    (12, "Wesley Maidoh", 82, 18, 55.7, "Louisiana School for Math, Science, and the Arts ONLINE", "Natchitoches", "LA"),
    (12, "Anthony Lin", 81, 19, 53, "Clear Lake High School", "Houston", "TX"),
    (12, "Dan Haidau", 81, 19, 53, "ROCO (Romanian Community Center", "Chicago", "IL"),
    (12, "Tanooj Kanike", 81, 19, 53, "GEM Academy and Center", "Plano", "TX"),
    (12, "Sandarika Warjri", 80, 20, 52.2, "Girls Code Lincoln", "Lincoln", "NE"),
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

    for grade, name, score, rank, pct, center, city, state_abbrev in ROWS:
        state = STATE_ABBREV_TO_FULL.get(state_abbrev.strip().upper(), state_abbrev.strip())
        name_clean = name.strip()
        key = (name_clean.lower(), state)
        row = key_to_row.get(key)
        if row:
            out_rows.append((row["student_id"], row["student_name"], state, grade, score, rank, pct))
            continue

        sid = next_id
        next_id += 1
        key_to_row[key] = {"student_id": sid, "student_name": name_clean, "state": state}
        new_students.append({
            "student_id": sid, "student_name": name_clean, "state": state,
            "team_ids": "", "alias": "", "gender": "", "grade_in_2026": ""
        })
        out_rows.append((sid, name_clean, state, grade, score, rank, pct))

    # Append new students
    if new_students:
        with open(STUDENTS_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["student_id", "student_name", "state", "team_ids", "alias", "gender", "grade_in_2026"], extrasaction="ignore")
            for r in new_students:
                w.writerow(r)
        print(f"Added {len(new_students)} new students")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "results.csv"
    # Compute fractional mcp_rank for ties (average of rank range)
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
