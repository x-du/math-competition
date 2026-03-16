#!/usr/bin/env python3
"""Build 2022 USAMO results.csv from PDF data and students.csv."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STUDENTS_CSV = ROOT / "database/students/students.csv"

# 2022 USAMO Awardees from PDF: (last, first, state, award). State inferred from school when known.
RAW = [
    # Gold
    ("Bei", "Warren", "British Columbia, Canada", "Gold"),
    ("Bu", "Alan", "New Hampshire", "Gold"),
    ("Chen", "Jeffrey", "Illinois", "Gold"),
    ("Cong", "Kevin", "New Hampshire", "Gold"),
    ("Das", "Rishabh", "New York", "Gold"),
    ("Dong", "David", "Washington", "Gold"),
    ("Goel", "Ram", "California", "Gold"),  # Krishna Home School - assumed CA
    ("Gu", "Andrew", "California", "Gold"),
    ("Lapate", "Papon", "New Hampshire", "Gold"),
    ("Lin", "Andrew", "New Jersey", "Gold"),
    ("Lin", "Huaye", "Massachusetts", "Gold"),
    ("Liu", "Derek", "California", "Gold"),
    ("Lu", "Maximus", "New York", "Gold"),
    ("Min", "Kevin", "California", "Gold"),
    ("Robitaille", "Luke", "Texas", "Gold"),
    ("Saengrungkongka", "Pitchayut", "New Hampshire", "Gold"),
    ("Shen", "Eric", "California", "Gold"),
    ("Slettnes", "Espen", "California", "Gold"),
    ("Xiao", "Yichen", "New Jersey", "Gold"),
    # Silver
    ("Albright", "Jack", "California", "Silver"),
    ("Avadhanam", "Advaith", "California", "Silver"),
    ("Cai", "Locke", "New Jersey", "Silver"),
    ("Choi", "Reagan", "Michigan", "Silver"),
    ("Fang", "Jason", "British Columbia, Canada", "Silver"),
    ("Geng", "Austin", "Louisiana", "Silver"),
    ("Jang", "Ryan", "South Korea", "Silver"),
    ("Jasuja", "Adi", "New York", "Silver"),
    ("Ji", "Kaylee", "California", "Silver"),
    ("Jung", "Aiden", "South Korea", "Silver"),
    ("Laksanawisit", "Mutiraj", "New Hampshire", "Silver"),
    ("Lee", "Justin", "California", "Silver"),
    ("Li", "Ryan", "Ohio", "Silver"),
    ("Masroor", "Razzi", "Michigan", "Silver"),
    ("Parthasarathy", "Rishab", "California", "Silver"),
    ("Rama", "Amol", "California", "Silver"),
    ("Samuthrsindh", "Paramuth", "New Hampshire", "Silver"),
    ("Tang", "Adam", "California", "Silver"),
    ("Trang", "Vincent", "Virginia", "Silver"),
    ("Vedula", "Karthik", "Florida", "Silver"),
    ("Wan", "Jessica", "Florida", "Silver"),
    ("Wang", "Albert", "Florida", "Silver"),
    ("Wang", "Anthony", "California", "Silver"),
    ("Wang", "Zifan", "New Jersey", "Silver"),
    ("Wang", "Kaixin", "China", "Silver"),
    ("Wang", "Samuel", "Virginia", "Silver"),
    ("Whyte", "Jaedon", "Florida", "Silver"),
    ("Wu", "Kevin", "Maryland", "Silver"),
    ("Xiong", "Edward", "New Jersey", "Silver"),
    ("Xu", "Daniel", "California", "Silver"),
    ("Xu", "Max", "New Hampshire", "Silver"),
    ("Yang", "Eric", "New Hampshire", "Silver"),
    ("Yuan", "Daniel", "Maryland", "Silver"),
    ("Yue", "William", "Massachusetts", "Silver"),
    ("Zhang", "George", "Texas", "Silver"),
    ("Zhao", "Kevin", "Massachusetts", "Silver"),
    ("Zhao", "Alex", "Washington", "Silver"),
    # Bronze
    ("Arun", "Srinivas", "Colorado", "Bronze"),
    ("Cao", "George", "New Jersey", "Bronze"),
    ("Chang", "Evan", "New Jersey", "Bronze"),
    ("Chen", "Benjamin", "Illinois", "Bronze"),
    ("Chen", "Kenneth", "Minnesota", "Bronze"),
    ("Chen", "Matthew", "Minnesota", "Bronze"),
    ("Dong", "Jessica", "China", "Bronze"),
    ("Fang", "Mason", "California", "Bronze"),
    ("Ge", "Chris", "California", "Bronze"),
    ("Gilman", "Pico", "California", "Bronze"),
    ("Goel", "Arnav", "Illinois", "Bronze"),
    ("Gutkovich", "Paul", "New York", "Bronze"),
    ("Hamrick", "Paul", "California", "Bronze"),
    ("Heller", "Garrett", "Virginia", "Bronze"),
    ("Hu", "Qingcheng", "California", "Bronze"),
    ("Ji", "Jay", "United Kingdom", "Bronze"),
    ("Kay", "Tristan", "Washington", "Bronze"),
    ("Kunapuli", "Sasidhar", "California", "Bronze"),
    ("Lee", "Daeho", "California", "Bronze"),
    ("Lin", "Mugeng", "British Columbia, Canada", "Bronze"),
    ("Liu", "Sophie", "Nevada", "Bronze"),
    ("Lu", "Evan", "Ontario, Canada", "Bronze"),
    ("Madiraju", "Akash", "California", "Bronze"),
    ("Mai", "Daniel", "Massachusetts", "Bronze"),
    ("Mao", "Marvin", "New Jersey", "Bronze"),
    ("Mishra", "Nilay", "California", "Bronze"),
    ("Pan", "Zehan", "New Jersey", "Bronze"),
    ("Rydell", "James", "California", "Bronze"),
    ("Shen", "Qingzhou", "Georgia", "Bronze"),
    ("Singer", "Easton", "Ohio", "Bronze"),
    ("Sue", "Kristie", "California", "Bronze"),
    ("Tang", "Linus", "Nevada", "Bronze"),
    ("Vladimiroff", "Alan", "Virginia", "Bronze"),
    ("Wang", "Henry", "California", "Bronze"),
    ("Wu", "Christopher", "Texas", "Bronze"),
    ("Xia", "Daniel", "New Jersey", "Bronze"),
    ("Xiao", "Ai", "New Hampshire", "Bronze"),
    ("Yang", "Haozhe", "Saskatchewan, Canada", "Bronze"),
    ("Yang", "Owen", "Arizona", "Bronze"),
    ("Yang", "Ryan", "Connecticut", "Bronze"),
    ("Yin", "Victor", "California", "Bronze"),
    ("Yu", "Dylan", "Texas", "Bronze"),
    ("Zhang", "Hankai", "Michigan", "Bronze"),
    ("Zhang", "Qiao", "California", "Bronze"),
    ("Zhang", "Steve", "California", "Bronze"),
    ("Zhong", "Rowechen", "Texas", "Bronze"),
    ("Zhou", "Ethan", "Virginia", "Bronze"),
    ("Zhou", "Samuel", "California", "Bronze"),
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
    used_sid_states = {}
    for last, first, state, award in RAW:
        full_name = f"{first} {last}"
        sid = name_to_id.get(full_name)
        if sid is not None:
            used = used_sid_states.setdefault(sid, set())
            if (full_name, state) in used:
                pass
            elif any(s != state for (n, s) in used if n == full_name):
                sid = None
        if sid is None:
            sid = next_id
            next_id += 1
            new_students.append((sid, full_name))
            if full_name not in name_to_id:
                name_to_id[full_name] = sid
        used_sid_states.setdefault(sid, set()).add((full_name, state))
        rows.append((sid, full_name, state, award))

    out_dir = ROOT / "database/contests/amo/year=2022"
    out_dir.mkdir(parents=True, exist_ok=True)
    results_path = out_dir / "results.csv"
    with results_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["student_id", "student_name", "state", "award"])
        for r in rows:
            w.writerow(r)

    if new_students:
        with STUDENTS_CSV.open("a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            for sid, name in new_students:
                w.writerow([sid, name, "", ""])

    print(f"Wrote {results_path} with {len(rows)} rows")
    print(f"Added {len(new_students)} new students to {STUDENTS_CSV}")


if __name__ == "__main__":
    main()
