#!/usr/bin/env python3
"""
Add Math Kangaroo 2021 Grade 7 National Winners.
Source: https://mathkangaroo.org/mks/wp-content/uploads/2021/08/2021_Level-7_National-Winners.pdf
Resolves (name, state) via students.csv; adds new students as needed.
If student_id exists with missing state, fills state from MK data.
Do NOT merge students with same name in different states - match strictly on (name, state).
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2021" / "grade=7"

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

# grade, name, score, rank, state (from 2021 Level 7 National Winners PDF)
# Excluded: Nikolay Nazarov, Jeonghyun Han (Saudi Arabia - no US state)
ROWS = [
    (7, "Plato Wong", 120, 1, "CA"),
    (7, "Troy Yang", 120, 1, "CA"),
    (7, "Alexander Sheffield", 120, 1, "NY"),
    (7, "Michael Iofin", 120, 1, "NY"),
    (7, "Arjun Agarwal", 120, 1, "OR"),
    (7, "Aaron Le", 120, 1, "PA"),
    (7, "Soham Dam", 120, 1, "PA"),
    (7, "Harini Venkatesh", 120, 1, "TX"),
    (7, "Aishwarya Agrawal", 120, 1, "WA"),
    (7, "Susie Lu", 120, 1, "WA"),
    (7, "Vishnu Mangipudi", 120, 1, "WA"),
    (7, "Gaurav Gupta", 117, 2, "CA"),
    (7, "Aryan Agrawal", 117, 2, "WA"),
    (7, "Sohil Rathi", 116, 3, "CA"),
    (7, "Benjamin Jiang", 116, 3, "FL"),
    (7, "Ryan Chung", 116, 3, "VA"),
    (7, "Allan Yuan", 115, 4, "AL"),
    (7, "Arnav Dagar", 115, 4, "CA"),
    (7, "Ethan Y.", 115, 4, "CA"),
    (7, "Isabella Tran", 115, 4, "CA"),
    (7, "Ishika Shah", 115, 4, "CA"),
    (7, "Jonathan Du", 115, 4, "CA"),
    (7, "Kai Lum", 115, 4, "CA"),
    (7, "Leonid Chernyakhovskiy", 115, 4, "CA"),
    (7, "Mia Liu", 115, 4, "CA"),
    (7, "Shruti Arun", 115, 4, "CO"),
    (7, "Adam Yanco", 115, 4, "MA"),
    (7, "Eric Zhang", 115, 4, "MA"),
    (7, "Grace Zhang", 115, 4, "MA"),
    (7, "Jason Deng", 115, 4, "MA"),
    (7, "Anna Zhou", 115, 4, "MD"),
    (7, "Tony Song", 115, 4, "MD"),
    (7, "Pratham Mukewar", 115, 4, "NH"),
    (7, "Aahan Mahakud", 115, 4, "NJ"),
    (7, "Ayan Dalmia", 115, 4, "NJ"),
    (7, "Sophia Lin", 115, 4, "NY"),
    (7, "Suvam Konar", 115, 4, "OH"),
    (7, "Katherine Liu", 115, 4, "OK"),
    (7, "Arush Goswami", 115, 4, "OR"),
    (7, "Justin Yu", 115, 4, "TX"),
    (7, "Arnav Gupta", 115, 4, "VA"),
    (7, "Brandon Hu", 115, 4, "VA"),
    (7, "Benjamin Fu", 115, 4, "WA"),
    (7, "Ekaansh Agrawal", 115, 4, "WA"),
    (7, "Keenan Park", 112, 5, "CA"),
    (7, "Vikram Sarkar", 112, 5, "CT"),
    (7, "Samanyu Ganesh", 112, 5, "GA"),
    (7, "Siddarth Suresh", 112, 5, "GA"),
    (7, "Jianing Huang", 112, 5, "MA"),
    (7, "Kedaar Shankarnarayan", 112, 5, "NJ"),
    (7, "Owen Xuan", 112, 5, "WA"),
    (7, "Ana Shrivastava", 111, 6, "AZ"),
    (7, "Rishi Salvi", 111, 6, "CA"),
    (7, "Braden Grosshandler", 111, 6, "MA"),
    (7, "Erica Hou", 111, 6, "MA"),
    (7, "Jessica Wu", 111, 6, "MI"),
    (7, "Michael Wu", 111, 6, "MI"),
    (7, "Matthew Karp", 111, 6, "NY"),
    (7, "Alex Mihailovici", 110, 7, "CA"),
    (7, "Alexander Huang", 110, 7, "CA"),
    (7, "Arjun Joisha", 110, 7, "CA"),
    (7, "Brandon Chang", 110, 7, "CA"),
    (7, "Dhruv Mallick", 110, 7, "CA"),
    (7, "Jing Zhou", 110, 7, "CA"),
    (7, "Madison Tran", 110, 7, "CA"),
    (7, "Mihika Deshpande", 110, 7, "CA"),
    (7, "Nathan Chan", 110, 7, "CA"),
    (7, "Remy Xie", 110, 7, "CA"),
    (7, "Shon Skarbnik", 110, 7, "CA"),
    (7, "Yifan Sheng", 110, 7, "CA"),
    (7, "Oliver Francois Watkins", 110, 7, "GA"),
    (7, "Rohan Morgan", 110, 7, "GA"),
    (7, "Eric Nie", 110, 7, "MA"),
    (7, "Lev Strougov", 110, 7, "MA"),
    (7, "Siming Chen", 110, 7, "MA"),
    (7, "Adrian Sun", 110, 7, "MD"),
    (7, "Alex Wang", 110, 7, "MD"),
    (7, "Justin Li", 110, 7, "MD"),
    (7, "Sanjana Ramesh", 110, 7, "MI"),
    (7, "Leo Yang", 110, 7, "NC"),
    (7, "Alicia Li", 110, 7, "NY"),
    (7, "Michael Retakh", 110, 7, "NY"),
    (7, "Aiden Yejoon Kim", 110, 7, "OK"),
    (7, "Alex Dosev", 110, 7, "OK"),
    (7, "Alik Polishchuk", 110, 7, "OR"),
    (7, "Anay Aggarwal", 110, 7, "OR"),
    (7, "Devin Chen", 110, 7, "OR"),
    (7, "Aidan Le", 110, 7, "PA"),
    (7, "Aditya Sengupta", 110, 7, "WA"),
    (7, "Alexander Peev", 110, 7, "WA"),
    (7, "Oliver Kahng", 109, 8, "NJ"),
    (7, "Julien Wang", 109, 8, "WA"),
    (7, "Andy Xing", 108, 9, "CA"),
    (7, "Cameron Ngai", 108, 9, "CA"),
    (7, "Eli Cui", 108, 9, "IL"),
    (7, "Arnesh Kundu", 108, 9, "NV"),
    (7, "Aditya Shirgur", 107, 10, "CA"),
    (7, "Chloe Fua", 107, 10, "CA"),
    (7, "Suhani Pahuja", 107, 10, "CA"),
    (7, "Sophie Hong", 107, 10, "IL"),
    (7, "Sri Sumukh Vulava", 107, 10, "KY"),
    (7, "Andrey Kalashnikov", 107, 10, "MA"),
    (7, "Katie Ji", 107, 10, "MA"),
    (7, "Daphne Ma", 107, 10, "OR"),
    (7, "Daniel Shunko", 107, 10, "WA"),
    (7, "Alexa Chang", 106, 11, "CA"),
    (7, "Andrew Jo", 106, 11, "CA"),
    (7, "Ava Chen", 106, 11, "CA"),
    (7, "Crystal Huang", 106, 11, "CA"),
    (7, "Exner Stanat", 106, 11, "CA"),
    (7, "Jerry Yu", 106, 11, "CA"),
    (7, "Kabir Gupta", 106, 11, "CA"),
    (7, "Manant Kochar", 106, 11, "CA"),
    (7, "Shaurya Mittal", 106, 11, "CA"),
    (7, "Xindi Liu", 106, 11, "CT"),
    (7, "Ellen Kolesnikova", 106, 11, "GA"),
    (7, "Elaine Zeng", 106, 11, "IN"),
    (7, "Clayton Song", 106, 11, "MA"),
    (7, "Jamie Hosier", 106, 11, "MA"),
    (7, "Natalie Han", 106, 11, "MA"),
    (7, "Athena Zhou", 106, 11, "MD"),
    (7, "Anika Sivarasa", 106, 11, "NH"),
    (7, "Alexander Choi", 106, 11, "NJ"),
    (7, "Siddharth Nair", 106, 11, "NY"),
    (7, "Isha Garg", 106, 11, "OR"),
    (7, "Peter Kisselev", 106, 11, "VA"),
    (7, "Donghee Kim", 105, 12, "CA"),
    (7, "Gloria Ma", 105, 12, "CA"),
    (7, "Mark Menaker", 105, 12, "CA"),
    (7, "Ryka Jain", 105, 12, "CA"),
    (7, "Trisha Manipatruni", 105, 12, "CA"),
    (7, "Zunaid Jafar", 105, 12, "GU"),
    (7, "Yutong Minerva Cao", 105, 12, "IA"),
    (7, "David Chen", 105, 12, "IL"),
    (7, "Henry Chen", 105, 12, "IL"),
    (7, "Sophia Qiu", 105, 12, "KS"),
    (7, "Daniil Landau", 105, 12, "MA"),
    (7, "Ethan Qian-Tsuchida", 105, 12, "MA"),
    (7, "Hansen Shieh", 105, 12, "MA"),
    (7, "Ira Singh", 105, 12, "MA"),
    (7, "Jeffrey Wang", 105, 12, "MI"),
    (7, "Michael Chen", 105, 12, "NC"),
    (7, "Logan Yoon", 105, 12, "NJ"),
    (7, "Analise Chen", 105, 12, "NY"),
    (7, "David Kong", 105, 12, "OR"),
    (7, "William Liu", 105, 12, "PA"),
    (7, "Justin Kim", 105, 12, "VA"),
    (7, "Kai Marcelais", 105, 12, "WA"),
    (7, "Alli Katila-Miikkulainen", 104, 13, "CA"),
    (7, "Soham Bhattacharya", 104, 13, "CA"),
    (7, "Thomas Ha", 104, 13, "MA"),
    (7, "Arjun Samavedam", 104, 13, "MD"),
    (7, "Austin Shu", 103, 14, "CA"),
    (7, "Riya Patel", 103, 14, "CA"),
    (7, "Rohan Reddy", 103, 14, "CA"),
    (7, "Michael Antipov", 103, 14, "IL"),
    (7, "Neel Balija", 103, 14, "NJ"),
    (7, "Rushil Kukreja", 103, 14, "VA"),
    (7, "Shota Ogushi", 103, 14, "WA"),
    (7, "Bhavin Dang", 102, 15, "AZ"),
    (7, "Aarush Parikh", 102, 15, "CA"),
    (7, "Aiden Wang", 102, 15, "CA"),
    (7, "Darren Yilmaz", 102, 15, "CA"),
    (7, "Gordon Wong", 102, 15, "CA"),
    (7, "Lucas Bai", 102, 15, "CA"),
    (7, "Phillip Zeng", 102, 15, "CA"),
    (7, "Suhani Gupta", 102, 15, "CA"),
    (7, "Vedanth Narsina", 102, 15, "CA"),
    (7, "Nithin Ravikumar", 102, 15, "IL"),
    (7, "Karanveer Nair", 102, 15, "MA"),
    (7, "Nathan Kessler", 102, 15, "MA"),
    (7, "Sophia Tatar", 102, 15, "MA"),
    (7, "Sriaditya Vaddadi", 102, 15, "MA"),
    (7, "Tyler Germain", 102, 15, "MA"),
    (7, "Srinivas Vijaybabu", 102, 15, "NC"),
    (7, "Akshara Kumar", 102, 15, "NJ"),
    (7, "Arnav Adepu", 102, 15, "NJ"),
    (7, "Eric Min", 102, 15, "OR"),
    (7, "Agrim Vishnoi", 102, 15, "TX"),
    (7, "Aryan Raj", 102, 15, "VA"),
    (7, "Adelia Poyarkov", 101, 16, "CA"),
    (7, "Aminjin Battulga", 101, 16, "CA"),
    (7, "Ashish Naveen", 101, 16, "CA"),
    (7, "Connor Zhao", 101, 16, "CA"),
    (7, "Harry Park", 101, 16, "CA"),
    (7, "Kyan Mui", 101, 16, "CA"),
    (7, "Lawrence Pang", 101, 16, "CA"),
    (7, "Lucas Serebrennikov", 101, 16, "CA"),
    (7, "Rishi Ranga", 101, 16, "CA"),
    (7, "Yashnil Mohanty", 101, 16, "CA"),
    (7, "Jiajun Luo", 101, 16, "CT"),
    (7, "Jiya Singla", 101, 16, "IL"),
    (7, "Aaryan Arora", 101, 16, "MA"),
    (7, "Jonas Wilderman", 101, 16, "MA"),
    (7, "Luke Li", 101, 16, "MA"),
    (7, "Michelle Chow", 101, 16, "MA"),
    (7, "Yixuan Li", 101, 16, "MD"),
    (7, "Matthew Guo", 101, 16, "NC"),
    (7, "Peter Karamanov", 101, 16, "NC"),
    (7, "Neil Sriram", 101, 16, "NJ"),
    (7, "Daniel Obstgarten", 101, 16, "NV"),
    (7, "Eric Zou", 101, 16, "NY"),
    (7, "Isabel Wang", 101, 16, "NY"),
    (7, "Shriya Sreeju", 101, 16, "TX"),
    (7, "Advaith Mopuri", 100, 17, "CA"),
    (7, "Baixuan Chen", 100, 17, "CA"),
    (7, "Bryant Wang", 100, 17, "CA"),
    (7, "Jacqueline Shan", 100, 17, "CA"),
    (7, "Jake Hu", 100, 17, "CA"),
    (7, "Kevin Zhu", 100, 17, "CA"),
    (7, "Rishabh Venkataramani", 100, 17, "CA"),
    (7, "Varshaa Nuthi", 100, 17, "CA"),
    (7, "Anran Liu", 100, 17, "MA"),
    (7, "Raahil Parikh", 100, 17, "MA"),
    (7, "Sukhmani Dhindsa", 100, 17, "NJ"),
    (7, "Ainsley Martin", 100, 17, "PA"),
    (7, "Ishita Sengar", 100, 17, "VA"),
    (7, "Annabelle Chen", 99, 18, "CA"),
    (7, "Yury Bychkov", 99, 18, "CA"),
    (7, "Aman Kumar", 99, 18, "MA"),
    (7, "Abir Bhatia", 98, 19, "CA"),
    (7, "Rithik Vir", 98, 19, "CA"),
    (7, "Timothy Liu", 98, 19, "CA"),
    (7, "Daria Stoyanova", 98, 19, "MA"),
    (7, "Mikayil Mustafayev", 98, 19, "MA"),
    (7, "Myles Breguet", 98, 19, "NJ"),
    (7, "Arkady Kokush", 98, 19, "NY"),
    (7, "Avyukt Ajit", 98, 19, "VA"),
    (7, "Rohit Rajakumar", 98, 19, "VA"),
    (7, "Annicka Hsue", 98, 19, "WA"),
    (7, "Ariya Shendure", 98, 19, "WA"),
    (7, "Aadhya Shenoy", 97, 20, "CA"),
    (7, "Eddie Zhang", 97, 20, "CA"),
    (7, "Ethan Moon", 97, 20, "CA"),
    (7, "Kai Lidzborski", 97, 20, "CA"),
    (7, "Lucas Han", 97, 20, "CA"),
    (7, "Shin Masada", 97, 20, "CA"),
    (7, "Ameya Patel", 97, 20, "CT"),
    (7, "Sohan Nelakudity", 97, 20, "CT"),
    (7, "Sankeerth Seella", 97, 20, "GA"),
    (7, "Gavin Warnakulasooriya", 97, 20, "MA"),
    (7, "Krish Kalla", 97, 20, "MA"),
    (7, "William Fezzie", 97, 20, "MA"),
    (7, "William Mountjoy", 97, 20, "MA"),
    (7, "Siddharth Pasari", 97, 20, "NY"),
    (7, "Nikaansh Singh", 97, 20, "OR"),
    (7, "Sophia Wang", 97, 20, "OR"),
    (7, "Keith Zheng", 97, 20, "TN"),
    (7, "Adit Roy Choudhury", 97, 20, "TX"),
    (7, "Alexander Yu", 97, 20, "VA"),
    (7, "Aryan Garg", 97, 20, "VA"),
    (7, "Jovina Arulandu", 97, 20, "VA"),
    (7, "Siri Kalidindi", 97, 20, "VA"),
    (7, "Yuexin Jiang", 97, 20, "WA"),
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
