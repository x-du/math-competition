#!/usr/bin/env python3
"""
Add BMT 2025 General individual results from the PDF roster.
Resolves student_id from students.csv; appends new students as needed.
"""
import csv
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDENTS_CSV = os.path.join(REPO_ROOT, "database", "students", "students.csv")
RESULTS_CSV = os.path.join(REPO_ROOT, "database", "contests", "bmt", "year=2025", "results.csv")

# Roster from BMT 2025 General.pdf (Honorable Mention Top 50%, Distinguished HM Top 20%, Top 10 with rank/score)
# Format: (bmt_student_id, source_name, award, rank, score) — rank/score are None unless in top 10
ROSTER = [
    # Honorable Mention (Top 50%)
    ("001B", "Tianlin Liu", "Honorable Mention (Top 50%)", None, None),
    ("001C", "Elaine Gu", "Honorable Mention (Top 50%)", None, None),
    ("002A", "Eva Lin", "Honorable Mention (Top 50%)", None, None),
    ("002C", "Victoria Huang", "Honorable Mention (Top 50%)", None, None),
    ("002D", "Lusen Yao", "Honorable Mention (Top 50%)", None, None),
    ("002F", "Alber Wu", "Honorable Mention (Top 50%)", None, None),
    ("006A", "Shivansh Grover", "Honorable Mention (Top 50%)", None, None),
    ("006B", "Temujin Battulga", "Honorable Mention (Top 50%)", None, None),
    ("008B", "Gilbert Jiang", "Honorable Mention (Top 50%)", None, None),
    ("008D", "Catherine Jian", "Honorable Mention (Top 50%)", None, None),
    ("008E", "Brianna Su", "Honorable Mention (Top 50%)", None, None),
    ("010B", "Mittansh Bhatia", "Honorable Mention (Top 50%)", None, None),
    ("012B", "Weiping(Jessica) Li", "Honorable Mention (Top 50%)", None, None),
    ("012C", "Vihan Kalsi", "Honorable Mention (Top 50%)", None, None),
    ("012D", "Manant Kochar", "Honorable Mention (Top 50%)", None, None),
    ("013B", "Evan Zhou", "Honorable Mention (Top 50%)", None, None),
    ("013F", "Yanlin Huang", "Honorable Mention (Top 50%)", None, None),
    ("014A", "Yichen Wu", "Honorable Mention (Top 50%)", None, None),
    ("014C", "Yifan Hu", "Honorable Mention (Top 50%)", None, None),
    ("028A", "Sohum Uttamchandani", "Honorable Mention (Top 50%)", None, None),
    ("029B", "Situ Zhao", "Honorable Mention (Top 50%)", None, None),
    ("031A", "Rucha Kore", "Honorable Mention (Top 50%)", None, None),
    ("031D", "Shannon Zhang", "Honorable Mention (Top 50%)", None, None),
    ("032A", "Richard Fan", "Honorable Mention (Top 50%)", None, None),
    ("032B", "Aanya Gupta", "Honorable Mention (Top 50%)", None, None),
    ("032D", "Fiona Liu", "Honorable Mention (Top 50%)", None, None),
    ("032E", "Tanish Kolhe", "Honorable Mention (Top 50%)", None, None),
    ("033A", "NitinReddy Vaka", "Honorable Mention (Top 50%)", None, None),
    ("033B", "Aarav Mann", "Honorable Mention (Top 50%)", None, None),
    ("035D", "Ethan Chen", "Honorable Mention (Top 50%)", None, None),
    ("035F", "Pranav Mallina", "Honorable Mention (Top 50%)", None, None),
    ("037E", "Shaurya Chauhan", "Honorable Mention (Top 50%)", None, None),
    ("037F", "Sri Sumukh Vulava", "Honorable Mention (Top 50%)", None, None),
    ("040C", "Aminjin Battulga", "Honorable Mention (Top 50%)", None, None),
    ("044B", "Alan Cai", "Honorable Mention (Top 50%)", None, None),
    ("044D", "Vivian Lei", "Honorable Mention (Top 50%)", None, None),
    ("047D", "Katherine Wang", "Honorable Mention (Top 50%)", None, None),
    ("049B", "Ryan Miao", "Honorable Mention (Top 50%)", None, None),
    ("050F", "Lucas Lum", "Honorable Mention (Top 50%)", None, None),
    ("054C", "Carson Winter", "Honorable Mention (Top 50%)", None, None),
    ("055C", "Andrew Ton", "Honorable Mention (Top 50%)", None, None),
    ("056B", "Miranda Li", "Honorable Mention (Top 50%)", None, None),
    ("058B", "Rener Li", "Honorable Mention (Top 50%)", None, None),
    ("059D", "Nikita Das", "Honorable Mention (Top 50%)", None, None),
    ("061A", "Anson Yu", "Honorable Mention (Top 50%)", None, None),
    ("061D", "William Ye", "Honorable Mention (Top 50%)", None, None),
    ("064D", "Ali Fasihuddin", "Honorable Mention (Top 50%)", None, None),
    ("069A", "Thomas Della Vigna", "Honorable Mention (Top 50%)", None, None),
    ("069C", "Utsav Lal", "Honorable Mention (Top 50%)", None, None),
    ("070B", "Elizabeth Ying", "Honorable Mention (Top 50%)", None, None),
    ("071B", "Hunter Liu", "Honorable Mention (Top 50%)", None, None),
    ("071C", "David Li", "Honorable Mention (Top 50%)", None, None),
    ("071D", "Zhiyuan Ma", "Honorable Mention (Top 50%)", None, None),
    ("072A", "Austin Zou", "Honorable Mention (Top 50%)", None, None),
    ("072B", "Ray He", "Honorable Mention (Top 50%)", None, None),
    ("073A", "Elisa Zhang", "Honorable Mention (Top 50%)", None, None),
    ("075D", "Joy Wang", "Honorable Mention (Top 50%)", None, None),
    ("076F", "Bosman Botha", "Honorable Mention (Top 50%)", None, None),
    ("077D", "Jonathan Yang", "Honorable Mention (Top 50%)", None, None),
    ("080E", "Niels Voss", "Honorable Mention (Top 50%)", None, None),
    ("085A", "Laurence Huang", "Honorable Mention (Top 50%)", None, None),
    ("091B", "Anrui Hong", "Honorable Mention (Top 50%)", None, None),
    ("091C", "Colin Zhao", "Honorable Mention (Top 50%)", None, None),
    ("091E", "Ankang Hong", "Honorable Mention (Top 50%)", None, None),
    ("092D", "Vivaan Daxini", "Honorable Mention (Top 50%)", None, None),
    ("093A", "Clara Burke", "Honorable Mention (Top 50%)", None, None),
    ("093B", "Harrison Qian", "Honorable Mention (Top 50%)", None, None),
    ("093C", "Pablo Zhang", "Honorable Mention (Top 50%)", None, None),
    ("093D", "Davina Rahnpaur", "Honorable Mention (Top 50%)", None, None),
    ("096B", "Yagnik Chilamakuri", "Honorable Mention (Top 50%)", None, None),
    ("096D", "Rishi Gupta", "Honorable Mention (Top 50%)", None, None),
    ("097B", "Jason Lee", "Honorable Mention (Top 50%)", None, None),
    ("097C", "Grace Zuo", "Honorable Mention (Top 50%)", None, None),
    ("098C", "Aaron Ely", "Honorable Mention (Top 50%)", None, None),
    ("098E", "Elaine Sun", "Honorable Mention (Top 50%)", None, None),
    ("106A", "Eric Xie", "Honorable Mention (Top 50%)", None, None),
    ("110C", "Samuel Chen", "Honorable Mention (Top 50%)", None, None),
    ("119B", "Ada Ji", "Honorable Mention (Top 50%)", None, None),
    ("119E", "Anisha Raghu", "Honorable Mention (Top 50%)", None, None),
    ("120F", "Anson Ng", "Honorable Mention (Top 50%)", None, None),
    ("126A", "Kevin Zhu", "Honorable Mention (Top 50%)", None, None),
    ("126C", "Kush Goel", "Honorable Mention (Top 50%)", None, None),
    # Distinguished HM (Top 20%) — not in top 10
    ("001D", "Jason Yang", "Distinguished HM (Top 20%)", None, None),
    ("001E", "Franklin Zhou", "Distinguished HM (Top 20%)", None, None),
    ("002B", "Lucas Lin", "Distinguished HM (Top 20%)", None, None),
    ("002E", "Atticus Lin", "Distinguished HM (Top 20%)", None, None),
    ("006D", "Matthew Yuan", "Distinguished HM (Top 20%)", None, None),
    ("008C", "Alex Tsagaan", "Distinguished HM (Top 20%)", None, None),
    ("008F", "Katherine Li", "Distinguished HM (Top 20%)", None, None),
    ("012A", "Albert Li", "Distinguished HM (Top 20%)", None, None),
    ("029A", "Kartik Gudapati", "Distinguished HM (Top 20%)", None, None),
    ("031C", "Alex Zhu", "Distinguished HM (Top 20%)", None, None),
    ("033C", "Andrew Shin", "Distinguished HM (Top 20%)", None, None),
    ("033D", "Ayush Bansal", "Distinguished HM (Top 20%)", None, None),
    ("033E", "Abhigyan Singh", "Distinguished HM (Top 20%)", None, None),
    ("033F", "Niranjan Rao", "Distinguished HM (Top 20%)", None, None),
    ("035A", "Rahul Tacke", "Distinguished HM (Top 20%)", None, None),
    ("044F", "Zitian Li", "Distinguished HM (Top 20%)", None, None),
    ("045D", "James Lin", "Distinguished HM (Top 20%)", None, None),
    ("046C", "Jessica Hu", "Distinguished HM (Top 20%)", None, None),
    ("047F", "Elaine Xu", "Distinguished HM (Top 20%)", None, None),
    ("049E", "Daniel Zhu", "Distinguished HM (Top 20%)", None, None),
    ("050A", "Shamik Khowala", "Distinguished HM (Top 20%)", None, None),
    ("050C", "Christine Deng", "Distinguished HM (Top 20%)", None, None),
    ("050D", "Heather Wang", "Distinguished HM (Top 20%)", None, None),
    ("050E", "Lily Peng", "Distinguished HM (Top 20%)", None, None),
    ("054A", "Dominic Handsborough", "Distinguished HM (Top 20%)", None, None),
    ("054E", "Ivan Liu", "Distinguished HM (Top 20%)", None, None),
    ("070E", "Brandon Nam", "Distinguished HM (Top 20%)", None, None),
    ("074A", "Henry Yao", "Distinguished HM (Top 20%)", None, None),
    ("076C", "Jason Yuan", "Distinguished HM (Top 20%)", None, None),
    ("077A", "Isabella Li", "Distinguished HM (Top 20%)", None, None),
    ("077B", "Eli Ying", "Distinguished HM (Top 20%)", None, None),
    ("077C", "Edward Zeng", "Distinguished HM (Top 20%)", None, None),
    ("077E", "Andy Liu", "Distinguished HM (Top 20%)", None, None),
    ("095A", "Alex Ruan", "Distinguished HM (Top 20%)", None, None),
    ("097A", "Keith Li", "Distinguished HM (Top 20%)", None, None),
    ("098A", "Ronald Wang", "Distinguished HM (Top 20%)", None, None),
    ("109A", "Angela Zhang", "Distinguished HM (Top 20%)", None, None),
    ("109D", "Cindy Zhao", "Distinguished HM (Top 20%)", None, None),
    ("113A", "Shrey Vishen", "Distinguished HM (Top 20%)", None, None),
    ("113B", "Liyan Xu", "Distinguished HM (Top 20%)", None, None),
    ("117B", "Erin Bian", "Distinguished HM (Top 20%)", None, None),
    ("118C", "Ananya Raghu", "Distinguished HM (Top 20%)", None, None),
    # Top 10 (rank and score) — PDF order: 047F, 031C, 011E, 033C, 001F, 050A, 001A, 118C, 119C, 119F
    ("119F", "Myungbeen Choi", "Distinguished HM (Top 20%)", 1, 24),
    ("119C", "Rishi Rajesh", "Distinguished HM (Top 20%)", 2, 23),
    ("118C", "Vishnu Mangipudi", "Distinguished HM (Top 20%)", 3, 23),
    ("001A", "Andrew Shi", "Distinguished HM (Top 20%)", 4, 22),
    ("050A", "Shamik Khowala", "Distinguished HM (Top 20%)", 5, 21),
    ("001F", "Ryan Wang", "Distinguished HM (Top 20%)", 6, 21),
    ("033C", "Andrew Shin", "Distinguished HM (Top 20%)", 7, 21),
    ("011E", "Yueqian Zhang", "Distinguished HM (Top 20%)", 8, 21),
    ("031C", "Alex Zhu", "Distinguished HM (Top 20%)", 9, 21),
    ("047F", "Elaine Xu", "Distinguished HM (Top 20%)", 10, 21),
]

def normalize_name(name):
    return name.strip().lower()

def load_students():
    """Return (by_name: dict[str, list of (id, name, state)], max_id, header_row)."""
    by_name = {}
    max_id = 0
    header = None
    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        header = r.fieldnames
        for row in r:
            sid = int(row["student_id"])
            if sid > max_id:
                max_id = sid
            name = row["student_name"]
            state = row.get("state", "")
            key = normalize_name(name)
            by_name.setdefault(key, []).append((sid, name, state))
            alias_str = row.get("alias", "") or ""
            for al in alias_str.split("|"):
                al = al.strip().lower()
                if al and al != key:
                    by_name.setdefault(al, []).append((sid, name, state))
    return by_name, max_id, header

def resolve_student(source_name, by_name, next_id, new_students):
    """Resolve source_name to (student_id, canonical_name, state). Add to new_students if new."""
    key = normalize_name(source_name)
    if key in by_name:
        candidates = by_name[key]
        if len(candidates) == 1:
            sid, canonical_name, state = candidates[0]
            return sid, canonical_name, state
        for sid, canonical_name, state in candidates:
            if state == "":
                return sid, canonical_name, state
        sid, canonical_name, state = candidates[0]
        return sid, canonical_name, state
    if "(" in source_name and ")" in source_name:
        m = re.match(r"(.+?)\((.+?)\)(.+)", source_name)
        if m:
            left, mid, right = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
            for attempt in [mid + " " + right, left + right]:
                attempt_key = normalize_name(attempt)
                if attempt_key in by_name:
                    candidates = by_name[attempt_key]
                    if len(candidates) == 1:
                        sid, canonical_name, state = candidates[0]
                        return sid, canonical_name, state
                    sid, canonical_name, state = candidates[0]
                    return sid, canonical_name, state
    sid = next_id[0]
    next_id[0] += 1
    new_students.append((sid, source_name, ""))
    by_name.setdefault(key, []).append((sid, source_name, ""))
    return sid, source_name, ""

def main():
    by_name, max_id, header = load_students()
    next_id = [max_id + 1]
    new_students = []

    rows = []
    for bmt_id, source_name, award, rank, score in ROSTER:
        sid, canonical_name, state = resolve_student(source_name, by_name, next_id, new_students)
        row = {
            "student_id": sid,
            "student_name": canonical_name,
            "state": state,
            "bmt_student_id": bmt_id,
            "award": award,
            "rank": str(rank) if rank is not None else "",
            "score": str(score) if score is not None else "",
        }
        rows.append(row)

    os.makedirs(os.path.dirname(RESULTS_CSV), exist_ok=True)
    fieldnames = ["student_id", "student_name", "state", "bmt_student_id", "award", "rank", "score"]
    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {len(rows)} rows to {RESULTS_CSV}")

    if new_students:
        with open(STUDENTS_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            for sid, name, state in new_students:
                w.writerow([sid, name, state, "", "", ""])
        print(f"Appended {len(new_students)} new students to {STUDENTS_CSV}")
    else:
        print("No new students added.")

if __name__ == "__main__":
    main()
