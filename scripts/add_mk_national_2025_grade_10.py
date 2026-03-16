#!/usr/bin/env python3
"""
Add Math Kangaroo 2025 Grade 10 National Winners.
Resolves (name, state) via students.csv; adds new students as needed.
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2025" / "grade=10"

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
    (10, "Anshul Mantri", 120, 1, 98.8, "Sunshine Elite", "Beaverton", "OR"),
    (10, "David Wang", 120, 1, 98.8, "Russian School of Mathematics Chevy Chase", "Chevy Chase", "MD"),
    (10, "Jonathan Liu", 120, 1, 98.8, "Math & More Studio", "Lexington", "MA"),
    (10, "Varun Gadi", 120, 1, 98.8, "Fulton Science Academy ONLINE", "Alpharetta", "GA"),
    (10, "Wynn Marple", 120, 1, 98.8, "Grace Academy", "San Diego", "CA"),
    (10, "Zakhar Lazarevich", 120, 1, 98.8, "Mathnasium of BurlingtonLexington ONLINE", "Burlington", "MA"),
    (10, "Roni Shaheen", 117, 2, 98.3, "Cape Henry Collegiate", "Virginia Beach", "VA"),
    (10, "Solon Xia", 117, 2, 98.3, "Kansas State University", "Manhattan", "KS"),
    (10, "Connor Kong", 116, 3, 98.1, "MathSeed Cupertino ONLINE", "San Jose", "CA"),
    (10, "Aditya Jagavkar", 115, 4, 95.7, "RSM Princeton", "Princeton Junction", "NJ"),
    (10, "Anthony Wang", 115, 4, 95.7, "Nevada Math", "Sparks", "NV"),
    (10, "Dev Batra", 115, 4, 95.7, "RSM Irvine", "Irvine", "CA"),
    (10, "Josh Tsimberg", 115, 4, 95.7, "RSM Plano", "Plano", "TX"),
    (10, "Kalan Warusa", 115, 4, 95.7, "Sunshine Academy Vienna", "Vienna", "VA"),
    (10, "Levi Gould", 115, 4, 95.7, "Polish Saturday School in Minneapolis", "Minneapolis", "MN"),
    (10, "Raghav Arun", 115, 4, 95.7, "Thinking Feet ONLINE", "Charlotte", "NC"),
    (10, "SaiPranav Chamarthy", 115, 4, 95.7, "UCLA Olga Radko Endowed Math Circle ONLINE", "Los Angeles", "CA"),
    (10, "Sophia Zhu", 115, 4, 95.7, "Mathnasium of Redmond", "Redmond", "WA"),
    (10, "Vikram Goudar", 115, 4, 95.7, "Cape Henry Collegiate", "Virginia Beach", "VA"),
    (10, "Arnav Prabhudesai", 112, 5, 95.2, "Fun Learning Place", "Acton", "MA"),
    (10, "Nickita Korbut", 112, 5, 95.2, "Poes School of Accelerated Math", "Sarasota", "FL"),
    (10, "Caroline Huang", 111, 6, 94.2, "Emory University", "Atlanta", "GA"),
    (10, "Kristiyan Kurtev", 111, 6, 94.2, "AlphaStar Academy", "Cupertino", "CA"),
    (10, "Ray Zhao", 111, 6, 94.2, "RSM Belmont", "Waltham", "MA"),
    (10, "Shlok Datta Choudhury", 111, 6, 94.2, "98thPercentile ONLINE", "Grapevine", "TX"),
    (10, "Daisy Ying", 110, 7, 92.1, "Sunshine Academy Vienna", "Vienna", "VA"),
    (10, "Edward Zhang", 110, 7, 92.1, "NextGen Learning Center ONLINE", "Los Angeles", "CA"),
    (10, "Jacob Khohayting", 110, 7, 92.1, "Melbourne Math Circle REMOTE", "Melbourne", "FL"),
    (10, "Janie Zheng", 110, 7, 92.1, "Grace Academy", "San Diego", "CA"),
    (10, "Michael Jian", 110, 7, 92.1, "EDUBUS", "Irvine", "CA"),
    (10, "Rhea Srinivas", 110, 7, 92.1, "Stratford Preparatory Blackford", "San Jose", "CA"),
    (10, "Soham Pattnaik", 110, 7, 92.1, "Cape Henry Collegiate", "Virginia Beach", "VA"),
    (10, "Vlad Vynarchuk", 110, 7, 92.1, "RSM Newton", "Newton", "MA"),
    (10, "Zukhil Subramanian", 110, 7, 92.1, "Stratford Preparatory Blackford", "San Jose", "CA"),
    (10, "Lin Vincent", 109, 8, 91.6, "Asheville School", "Asheville", "NC"),
    (10, "Lucas Park", 109, 8, 91.6, "RSM Encino", "Encino", "CA"),
    (10, "Varyan Jain", 107, 9, 91.3, "Adarsha Academy", "Phoenix", "AZ"),
    (10, "Aidan Cao", 106, 10, 90.6, "Aborn Institute", "San Jose", "CA"),
    (10, "Caroline Fu", 106, 10, 90.6, "Sunshine Academy Vienna", "Vienna", "VA"),
    (10, "Nicholas Wang", 106, 10, 90.6, "Silicon Valley ONLINE", "San Jose", "CA"),
    (10, "Ethan Cao", 105, 11, 89.4, "RSM San Mateo", "San Mateo", "CA"),
    (10, "Ethan Mui", 105, 11, 89.4, "Aborn Institute", "San Jose", "CA"),
    (10, "Gina Li", 105, 11, 89.4, "TR Consulting Group Inc", "Newton", "MA"),
    (10, "Jason Dong", 105, 11, 89.4, "Clear Lake High School", "Houston", "TX"),
    (10, "Timothy Chen", 105, 11, 89.4, "EDUBUS", "Irvine", "CA"),
    (10, "Akash Krothapalli", 102, 12, 88.2, "Mathnasium of Redmond", "Redmond", "WA"),
    (10, "Jacob Barrett", 102, 12, 88.2, "RSM Stamford", "Greenwich", "CT"),
    (10, "Platon Gorkavy", 102, 12, 88.2, "RSM Lexington", "Lexington", "MA"),
    (10, "Rachel Shuai", 102, 12, 88.2, "University of Central Florida", "Orlando", "FL"),
    (10, "Victor Wang", 102, 12, 88.2, "CCACC Academy Center", "Rockville", "MD"),
    (10, "Alan Lin", 101, 13, 86.8, "Stratford Preparatory Blackford", "San Jose", "CA"),
    (10, "Joseph Franklin", 101, 13, 86.8, "Champion Education", "Morrisville", "NC"),
    (10, "Linor Lyanda-Geller", 101, 13, 86.8, "Math Kangaroo at Purdue", "West Lafayette", "IN"),
    (10, "Paul Harmon", 101, 13, 86.8, "Montana City School", "Clancy", "MT"),
    (10, "Shourya Vyas", 101, 13, 86.8, "RSM Plano", "Plano", "TX"),
    (10, "Stefan Donisa", 101, 13, 86.8, "ROCO (Romanian Community Center", "Chicago", "IL"),
    (10, "Amrik Majumdar", 100, 14, 86.1, "Math Competition Coaching ONLINE", "Ashburn", "VA"),
    (10, "Graham Hoggan", 100, 14, 86.1, "AoPS Academy Irvine", "Irvine", "CA"),
    (10, "Rohan Danda", 100, 14, 86.1, "RSM Lexington", "Lexington", "MA"),
    (10, "Samhitha Kamatala", 100, 14, 86.1, "Aurora Center", "Aurora", "IL"),
    (10, "Alisha Jain", 98, 15, 84.9, "EDUBUS", "Irvine", "CA"),
    (10, "Anshul Raghav", 98, 15, 84.9, "Mathnasium of Redmond", "Redmond", "WA"),
    (10, "Avery Xu", 98, 15, 84.9, "RSM Scarsdale", "Scarsdale", "NY"),
    (10, "Jennifer Wang", 98, 15, 84.9, "Vine & Branches Porter County Homeschool Co op", "CHESTERTON", "IN"),
    (10, "Toprak Celikel", 98, 15, 84.9, "RSM Factoria", "Bellevue", "WA"),
    (10, "Anirudh Sengupta", 97, 16, 84.1, "Thinking Feet ONLINE", "Charlotte", "NC"),
    (10, "Brais Macknik-Conde", 97, 16, 84.1, "MMC&M ONLINE", "Kingston", "TN"),
    (10, "Linyun Wang", 97, 16, 84.1, "AITE Institute", "Irvine", "CA"),
    (10, "Jevin Xu", 96, 17, 83.2, "Southwest Virginia Governor's School Pulaski", "Dublin", "VA"),
    (10, "Maxwell Lisuwandi", 96, 17, 83.2, "RSM Andover", "Andover", "MA"),
    (10, "Sophia Lin", 96, 17, 77.4, "RSM Schaumburg", "Hoffman Estates", "IL"),
    (10, "Tanay Mangal", 96, 17, 81.2, "RSM Shrewsbury", "Shrewsbury", "MA"),
    (10, "Zoya Tahmasian", 96, 17, 83.2, "RSM Lexington", "Lexington", "MA"),
    (10, "Eva Kastoun", 95, 18, 82.5, "Stuyvesant High School", "New York", "NY"),
    (10, "Liza Kanne", 95, 18, 82.5, "Madison Math Kangaroo", "Madison", "WI"),
    (10, "Somil Sarode", 95, 18, 82.5, "RSM Fremont", "Fremont", "CA"),
    (10, "Jai Bindlish", 93, 19, 82.2, "Mathnasium of Redmond", "Redmond", "WA"),
    (10, "Alexander Stronger", 92, 20, 80, "Basis Independent Manhattan Upper", "New York", "NY"),
    (10, "Anna Zhang", 92, 20, 80, "Fulton Science Academy ONLINE", "Alpharetta", "GA"),
    (10, "Bella Yuan", 92, 20, 80, "UNC CH Math Dept Phillips Bldg", "Chapel Hill", "NC"),
    (10, "Chenxi Huang", 92, 20, 80, "AITE Institute", "Irvine", "CA"),
    (10, "Hanlin Yang", 92, 20, 80, "Grace Academy", "San Diego", "CA"),
    (10, "Nathan Huang", 92, 20, 80, "iLearning Bayside ONLINE", "Bayside", "NY"),
    (10, "Ritwik Singh", 92, 20, 80, "Mathnasium of Redmond", "Redmond", "WA"),
    (10, "Timofey Gafurov", 92, 20, 80, "RSM Herndon", "Herndon", "VA"),
    (10, "Vaishnavi Mudumbi", 92, 20, 80, "Prime Academy", "Tenafly", "NJ"),
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
