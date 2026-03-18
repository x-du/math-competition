#!/usr/bin/env python3
"""Build 2023 USAMO results.csv from PDF data and students.csv. Outputs CSV rows and new students."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STUDENTS_CSV = ROOT / "database/students/students.csv"

# 2023 USAMO Awardees from PDF: (last, first) -> (state, award)
# We'll convert to "First Last" for lookup
RAW = [
    # Gold
    ("Avadhanam", "Advaith", "California", "Gold"),
    ("Bei", "Warren", "British Columbia, Canada", "Gold"),
    ("Chang", "Evan", "New Jersey", "Gold"),
    ("Chen", "Jeffrey", "Illinois", "Gold"),
    ("Choi", "Aidan Woojin", "South Korea", "Gold"),
    ("Lin", "Huaye", "Massachusetts", "Gold"),
    ("Liu", "Derek", "California", "Gold"),
    ("Liu", "Elliott", "California", "Gold"),
    ("Lu", "Maximus", "New York", "Gold"),
    ("Pothapragada", "Krishna", "Illinois", "Gold"),
    ("Reddy", "Liam", "Nevada", "Gold"),
    ("Shen", "Eric", "California", "Gold"),
    ("Wan", "Jessica", "Florida", "Gold"),
    ("Wang", "Alexander", "New Jersey", "Gold"),
    ("Wang", "Anthony", "California", "Gold"),
    ("Zhang", "Qiao", "California", "Gold"),
    # Silver
    ("Anchaleenukoon", "Nithid", "New Hampshire", "Silver"),
    ("Arun", "Srinivas", "Colorado", "Silver"),
    ("Bao", "Christopher", "Nevada", "Silver"),
    ("Bu", "Alan", "New Hampshire", "Silver"),
    ("Dastrup", "Caleb", "Maryland", "Silver"),
    ("Dong", "David", "Washington", "Silver"),
    ("Gupta-She", "John", "New York", "Silver"),
    ("Jiang", "Henry", "Michigan", "Silver"),
    ("Kang", "Roy", "New York", "Silver"),
    ("Kim", "Juni", "New Jersey", "Silver"),
    ("Lefkowitz", "Jordan", "Connecticut", "Silver"),
    ("Li", "Edward", "Iowa", "Silver"),
    ("Lin", "Andrew", "New Jersey", "Silver"),
    ("Loh", "Vivian", "Pennsylvania", "Silver"),
    ("Mao", "Marvin", "New Jersey", "Silver"),
    ("Masroor", "Razzi", "Massachusetts", "Silver"),
    ("Slettnes", "Espen", "California", "Silver"),
    ("Wang", "Allen", "New Jersey", "Silver"),
    ("Xiao", "Yichen", "New Jersey", "Silver"),
    ("Xu", "Max", "New Hampshire", "Silver"),
    ("Yan", "Neal", "California", "Silver"),
    ("Yang", "Ryan", "Connecticut", "Silver"),
    ("Yu", "Edward", "Washington", "Silver"),
    ("Zhang", "Hankai", "Michigan", "Silver"),
    ("Zhang", "Steve", "California", "Silver"),
    ("Zhao", "Alex", "Washington", "Silver"),
    ("Zhou", "Ethan", "Virginia", "Silver"),
    # Bronze
    ("Bodke", "Rohan", "California", "Bronze"),
    ("Carratu", "Andrew", "New Hampshire", "Bronze"),
    ("Chen", "Alex", "California", "Bronze"),
    ("Chen", "Benjamin", "Illinois", "Bronze"),
    ("Chen", "Michael", "New Jersey", "Bronze"),
    ("Chu", "Wilbert", "Illinois", "Bronze"),
    ("Dai", "William", "Ontario, Canada", "Bronze"),
    ("Das", "Rohan", "California", "Bronze"),
    ("Ge", "Annabel", "Washington", "Bronze"),
    ("Ge", "Chris", "California", "Bronze"),
    ("Geng", "Austin", "Louisiana", "Bronze"),
    ("Hu", "Cordelia", "Tennessee", "Bronze"),
    ("Jayaraman", "Pavan", "New Jersey", "Bronze"),
    ("Law", "Ray", "California", "Bronze"),
    ("Lee", "Alan", "California", "Bronze"),
    ("Lee", "David", "California", "Bronze"),
    ("Lee", "Ethan", "California", "Bronze"),
    ("Li", "Nina", "British Columbia, Canada", "Bronze"),
    ("Lin", "Aaron", "Missouri", "Bronze"),
    ("Liu", "Ethan", "California", "Bronze"),
    ("Lu", "Kristine", "California", "Bronze"),
    ("Moltz", "Josiah", "New York", "Bronze"),
    ("Othman", "Joseph", "New York", "Bronze"),
    ("Pandit", "Suyash", "Oregon", "Bronze"),
    ("Singh", "Shreyas", "Illinois", "Bronze"),
    ("Sue", "Kristie", "California", "Bronze"),
    ("Tang", "Linus", "California", "Bronze"),
    ("Trang", "Vincent", "Virginia", "Bronze"),
    ("Tripathy", "Aprameya", "New Jersey", "Bronze"),
    ("Vedula", "Karthik", "Florida", "Bronze"),
    ("Vladimiroff", "Alan", "Virginia", "Bronze"),
    ("Wang", "Eric", "New Jersey", "Bronze"),  # West Windsor
    ("Wang", "Eric", "Massachusetts", "Bronze"),  # Phillips Academy - second Eric Wang
    ("Wu", "Xiaoyang", "California", "Bronze"),
    ("Xu", "Zani", "Virginia", "Bronze"),
    ("Yang", "Haozhe", "Saskatchewan, Canada", "Bronze"),
    ("Yevtushenko", "Feodor", "California", "Bronze"),
    ("Zhan", "Eric", "Washington", "Bronze"),
    ("Zhong", "Lerchen", "Texas", "Bronze"),
    ("Zhu", "Isabella", "Virginia", "Bronze"),
    ("Zhu", "Kelin", "Maryland", "Bronze"),
    # Honorable Mention
    ("Atlan", "Sebastian", "Illinois", "Honorable Mention"),
    ("Basu", "Dhruv", "Ontario, Canada", "Honorable Mention"),
    ("Chen", "Aaron", "California", "Honorable Mention"),
    ("Chen", "Matthew", "Minnesota", "Honorable Mention"),
    ("Chin", "Ryan", "Texas", "Honorable Mention"),
    ("Demir", "Omer", "Florida", "Honorable Mention"),
    ("Dryg", "Jackson", "Colorado", "Honorable Mention"),
    ("Fan", "Roger", "California", "Honorable Mention"),
    ("Gilman", "Pico", "California", "Honorable Mention"),
    ("He", "Katie", "Florida", "Honorable Mention"),
    ("Hu", "Aaron", "Florida", "Honorable Mention"),
    ("Hu", "Victoria", "California", "Honorable Mention"),
    ("Jang", "Won", "California", "Honorable Mention"),
    ("Kang", "Michelle", "Virginia", "Honorable Mention"),
    ("Kang", "Yifan", "Massachusetts", "Honorable Mention"),
    ("Kappler", "Alan", "Nevada", "Honorable Mention"),
    ("Kiselov", "Nikita", "Pennsylvania", "Honorable Mention"),
    ("Kweon", "Jian", "California", "Honorable Mention"),
    ("Li", "Brian", "California", "Honorable Mention"),
    ("Li", "Catherine", "California", "Honorable Mention"),
    ("Liang", "Michelle", "California", "Honorable Mention"),
    ("Liu", "Jerry", "California", "Honorable Mention"),
    ("Mai", "Daniel", "Massachusetts", "Honorable Mention"),
    ("Mao", "Jason", "New Jersey", "Honorable Mention"),
    ("Ni", "Heyang", "New Jersey", "Honorable Mention"),
    ("Nishida", "Taiga", "California", "Honorable Mention"),
    ("Park", "Minseok", "North Carolina", "Honorable Mention"),
    ("Pauskar", "Tanishq", "Ohio", "Honorable Mention"),
    ("Perry", "Zachary", "Massachusetts", "Honorable Mention"),
    ("Prasanna", "Sebastian", "Massachusetts", "Honorable Mention"),
    ("Reddy", "Kiran", "Nevada", "Honorable Mention"),
    ("Rizzo", "Jacopo", "California", "Honorable Mention"),
    ("Sawanoi", "Yuuki", "Washington", "Honorable Mention"),
    ("Shankar", "Pranav", "New Jersey", "Honorable Mention"),
    ("Sharma", "Romir", "New Jersey", "Honorable Mention"),
    ("Song", "Bryan", "New Jersey", "Honorable Mention"),
    ("Tang", "Lucas", "Washington", "Honorable Mention"),
    ("Vaishya", "Aaryan", "Florida", "Honorable Mention"),
    ("Villani", "David", "New York", "Honorable Mention"),
    ("Wang", "Kaile", "New Jersey", "Honorable Mention"),
    ("Wang", "Yizhou", "Quebec, Canada", "Honorable Mention"),
    ("Wang", "Yuji", "New Jersey", "Honorable Mention"),
    ("Wei", "David", "Virginia", "Honorable Mention"),
    ("Wen", "Aiden", "Texas", "Honorable Mention"),
    ("Wen", "Andrew", "Massachusetts", "Honorable Mention"),
    ("Xia", "Stephen", "California", "Honorable Mention"),
    ("Yang", "Gene", "Washington", "Honorable Mention"),
    ("Yang", "Michael", "Washington", "Honorable Mention"),
    ("Yang", "Ming", "Arizona", "Honorable Mention"),
    ("Zhang", "Brian", "North Carolina", "Honorable Mention"),
    ("Zhang", "Vincent", "Pennsylvania", "Honorable Mention"),
    ("Zhao", "Matthew", "New York", "Honorable Mention"),
    ("Zhong", "Jason", "Connecticut", "Honorable Mention"),
    ("Zhou", "Aaron", "Texas", "Honorable Mention"),
    ("Zhou", "Samuel", "California", "Honorable Mention"),
    ("Zhou", "Sicheng", "New Jersey", "Honorable Mention"),
    ("Zweiger", "Adam", "California", "Honorable Mention"),
]


def main():
    name_to_id = {}
    next_id = 1
    with STUDENTS_CSV.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            sid = (row.get("student_id") or "").strip()
            if not sid:
                continue
            try:
                i = int(sid)
            except ValueError:
                continue
            next_id = max(next_id, i + 1)
            name = (row.get("student_name") or "").strip()
            if name:
                name_to_id[name] = i
            alias = (row.get("alias") or "").strip()
            if alias:
                for a in alias.split("|"):
                    a = a.strip()
                    if a:
                        name_to_id[a] = i

    rows = []
    new_students = []
    used_sid_states = {}  # sid -> set of (full_name, state) already used
    for last, first, state, award in RAW:
        full_name = f"{first} {last}"
        sid = name_to_id.get(full_name)
        if sid is not None:
            used = used_sid_states.setdefault(sid, set())
            if (full_name, state) in used:
                pass  # same person, same state (duplicate row)
            elif any(s != state for (n, s) in used if n == full_name):
                # same name, different state -> different person
                sid = None
        if sid is None:
            sid = next_id
            next_id += 1
            new_students.append((sid, full_name))
            if full_name not in name_to_id:
                name_to_id[full_name] = sid
        used_sid_states.setdefault(sid, set()).add((full_name, state))
        rows.append((sid, full_name, state, award))

    out_dir = ROOT / "database/contests/amo/year=2023"
    out_dir.mkdir(parents=True, exist_ok=True)
    results_path = out_dir / "results.csv"
    with results_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["student_id", "student_name", "state", "award"])
        for r in rows:
            w.writerow(r)

    # Append new students
    if new_students:
        with STUDENTS_CSV.open("a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            for sid, name in new_students:
                w.writerow([sid, name, "", ""])

    print(f"Wrote {results_path} with {len(rows)} rows")
    print(f"Added {len(new_students)} new students to {STUDENTS_CSV}")


if __name__ == "__main__":
    main()
