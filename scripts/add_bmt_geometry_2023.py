#!/usr/bin/env python3
"""
Add BMT 2023 Geometry individual results from the PDF roster.
Resolves student_id from students.csv; appends new students as needed.
Includes year=2023 and bmt_student_id in results.
"""
import csv
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDENTS_CSV = os.path.join(REPO_ROOT, "database", "students", "students.csv")
RESULTS_CSV = os.path.join(REPO_ROOT, "database", "contests", "bmt-geometry", "year=2023", "results.csv")
YEAR = 2023

# Roster from BMT 2023 geometry.pdf — (bmt_student_id, source_name, award, rank, score)
ROSTER = [
    # Honorable Mention (Top 50%)
    ("003A", "Aiden Jeong", "Honorable Mention (Top 50%)", None, None),
    ("003C", "Hannah Fox", "Honorable Mention (Top 50%)", None, None),
    ("004B", "Rachel Li", "Honorable Mention (Top 50%)", None, None),
    ("004C", "Eddy Li", "Honorable Mention (Top 50%)", None, None),
    ("005B", "Tejo Madhavarapu", "Honorable Mention (Top 50%)", None, None),
    ("005C", "Jeffery Wang", "Honorable Mention (Top 50%)", None, None),
    ("005E", "Alena Kutsuk", "Honorable Mention (Top 50%)", None, None),
    ("005F", "Suhani Pahuja", "Honorable Mention (Top 50%)", None, None),
    ("011C", "Robert Feng", "Honorable Mention (Top 50%)", None, None),
    ("011F", "Lorraine Wang", "Honorable Mention (Top 50%)", None, None),
    ("014D", "Yourui Shao", "Honorable Mention (Top 50%)", None, None),
    ("015A", "Kai Yi", "Honorable Mention (Top 50%)", None, None),
    ("015F", "Lawrence Liu", "Honorable Mention (Top 50%)", None, None),
    ("016B", "Dylan Kim", "Honorable Mention (Top 50%)", None, None),
    ("016D", "Chen Andrew", "Honorable Mention (Top 50%)", None, None),
    ("017C", "Ethan K Song", "Honorable Mention (Top 50%)", None, None),
    ("017D", "Michelle Liang", "Honorable Mention (Top 50%)", None, None),
    ("018C", "Ryan Fu", "Honorable Mention (Top 50%)", None, None),
    ("018E", "Kailua Cheng", "Honorable Mention (Top 50%)", None, None),
    ("018F", "Gaurav Gupta", "Honorable Mention (Top 50%)", None, None),
    ("021D", "Nicole Sun", "Honorable Mention (Top 50%)", None, None),
    ("026E", "Ethan Yan", "Honorable Mention (Top 50%)", None, None),
    ("027E", "Evan Yang", "Honorable Mention (Top 50%)", None, None),
    ("028E", "Sambhu Ganesan", "Honorable Mention (Top 50%)", None, None),
    ("029C", "Evan Liu", "Honorable Mention (Top 50%)", None, None),
    ("030A", "Daniel Kim", "Honorable Mention (Top 50%)", None, None),
    ("031E", "Ankita Ramabadran", "Honorable Mention (Top 50%)", None, None),
    ("034C", "Harish Loghashankar", "Honorable Mention (Top 50%)", None, None),
    ("034E", "Seabert Mao", "Honorable Mention (Top 50%)", None, None),
    ("036B", "Rhishi Balaa Sakthivel", "Honorable Mention (Top 50%)", None, None),
    ("036D", "Camea Caprita", "Honorable Mention (Top 50%)", None, None),
    ("036E", "Kristiyan Kurtev", "Honorable Mention (Top 50%)", None, None),
    ("039A", "Shihan Kanungo", "Honorable Mention (Top 50%)", None, None),
    ("039E", "Steve Zhang", "Honorable Mention (Top 50%)", None, None),
    ("044A", "Emily Wu", "Honorable Mention (Top 50%)", None, None),
    ("044C", "Ella Li", "Honorable Mention (Top 50%)", None, None),
    ("045A", "Caden Ruan", "Honorable Mention (Top 50%)", None, None),
    ("045C", "Terry Xie", "Honorable Mention (Top 50%)", None, None),
    ("045E", "Mihir Kotbagi", "Honorable Mention (Top 50%)", None, None),
    ("045F", "Eddie Zhang", "Honorable Mention (Top 50%)", None, None),
    ("046B", "Neil Krishnan", "Honorable Mention (Top 50%)", None, None),
    ("047B", "Sylvia Chen", "Honorable Mention (Top 50%)", None, None),
    ("047E", "Aishani Singh", "Honorable Mention (Top 50%)", None, None),
    ("048A", "Aman Chandra", "Honorable Mention (Top 50%)", None, None),
    ("048D", "Jaden Fu", "Honorable Mention (Top 50%)", None, None),
    ("049D", "Haofang Zhu", "Honorable Mention (Top 50%)", None, None),
    ("052A", "Jacqueline Shan", "Honorable Mention (Top 50%)", None, None),
    ("052D", "Mingshi Liu", "Honorable Mention (Top 50%)", None, None),
    ("056A", "Atticus Masuzawa", "Honorable Mention (Top 50%)", None, None),
    ("056C", "James Browning", "Honorable Mention (Top 50%)", None, None),
    ("057A", "Frank Yuan", "Honorable Mention (Top 50%)", None, None),
    ("057B", "Alex Bai", "Honorable Mention (Top 50%)", None, None),
    ("059B", "Rohan Shivakumar", "Honorable Mention (Top 50%)", None, None),
    ("059C", "Edwin Hou", "Honorable Mention (Top 50%)", None, None),
    ("061F", "Jake Hu", "Honorable Mention (Top 50%)", None, None),
    ("062B", "Allinah Zhan", "Honorable Mention (Top 50%)", None, None),
    ("063C", "Yujun Lee", "Honorable Mention (Top 50%)", None, None),
    ("065B", "Enze Chen", "Honorable Mention (Top 50%)", None, None),
    ("065C", "Chengyu Wang", "Honorable Mention (Top 50%)", None, None),
    ("075C", "Aaron Shen", "Honorable Mention (Top 50%)", None, None),
    ("076E", "Chase Hikida", "Honorable Mention (Top 50%)", None, None),
    ("080A", "Mark Rhee", "Honorable Mention (Top 50%)", None, None),
    ("080C", "Zaee Shah", "Honorable Mention (Top 50%)", None, None),
    ("080F", "Arush Bisht", "Honorable Mention (Top 50%)", None, None),
    ("099E", "William Wang", "Honorable Mention (Top 50%)", None, None),
    ("100E", "Raphael Leung", "Honorable Mention (Top 50%)", None, None),
    ("101A", "Jessica Wu", "Honorable Mention (Top 50%)", None, None),
    ("103D", "Sophia Henningsen", "Honorable Mention (Top 50%)", None, None),
    ("105A", "Teddy Xu", "Honorable Mention (Top 50%)", None, None),
    ("105D", "Anthony Wang", "Honorable Mention (Top 50%)", None, None),
    ("111A", "Carolyn Ruan", "Honorable Mention (Top 50%)", None, None),
    ("111C", "Yuan Xing", "Honorable Mention (Top 50%)", None, None),
    ("111D", "Raymond Feng", "Honorable Mention (Top 50%)", None, None),
    ("112F", "Owen Lu", "Honorable Mention (Top 50%)", None, None),
    ("116A", "Pengyu Chen", "Honorable Mention (Top 50%)", None, None),
    ("117A", "Edward Li", "Honorable Mention (Top 50%)", None, None),
    ("117C", "Wesley Wu", "Honorable Mention (Top 50%)", None, None),
    ("117D", "Christopher Peng", "Honorable Mention (Top 50%)", None, None),
    ("125A", "DongLin Jin", "Honorable Mention (Top 50%)", None, None),
    ("125E", "Ivan Yu", "Honorable Mention (Top 50%)", None, None),
    ("126E", "Ava Chen", "Honorable Mention (Top 50%)", None, None),
    ("128A", "Jack Jin", "Honorable Mention (Top 50%)", None, None),
    # Distinguished HM (Top 20%) — not in top scores list
    ("003F", "Aarush Khare", "Distinguished HM (Top 20%)", None, None),
    ("004D", "Qi Huang", "Distinguished HM (Top 20%)", None, None),
    ("005A", "Alex Zhan", "Distinguished HM (Top 20%)", None, None),
    ("005D", "Neil Kolekar", "Distinguished HM (Top 20%)", None, None),
    ("007E", "Alex Chen", "Distinguished HM (Top 20%)", None, None),
    ("015D", "Aidan Bai", "Distinguished HM (Top 20%)", None, None),
    ("020A", "Daniel Nie", "Distinguished HM (Top 20%)", None, None),
    ("027A", "Brian Li", "Distinguished HM (Top 20%)", None, None),
    ("039B", "Tanush Aggarwal", "Distinguished HM (Top 20%)", None, None),
    ("043C", "Alan Lu", "Distinguished HM (Top 20%)", None, None),
    ("043D", "Skyler Mao", "Distinguished HM (Top 20%)", None, None),
    ("044E", "Vivian Zhong", "Distinguished HM (Top 20%)", None, None),
    ("049A", "Hengrui Liang", "Distinguished HM (Top 20%)", None, None),
    ("061E", "Akilan Paramasivam", "Distinguished HM (Top 20%)", None, None),
    ("096A", "Christopher Chen", "Distinguished HM (Top 20%)", None, None),
    ("117F", "Onkit Samanta", "Distinguished HM (Top 20%)", None, None),
    ("118A", "Alex Zhao", "Distinguished HM (Top 20%)", None, None),
    # Top scores (rank and score) — PDF order
    ("043E", "Advaith Avadhanam", "Distinguished HM (Top 20%)", 1, 9),
    ("115F", "Vivian Loh", "Distinguished HM (Top 20%)", 2, 8),
    ("007A", "Linus Tang", "Distinguished HM (Top 20%)", 3, 8),
    ("115D", "Neal Yan", "Distinguished HM (Top 20%)", 4, 8),
    ("106D", "Xinyu Meng", "Distinguished HM (Top 20%)", 5, 8),
    ("105F", "Elliott Liu", "Distinguished HM (Top 20%)", 6, 8),
    ("003E", "Jonathan Du", "Distinguished HM (Top 20%)", 7, 8),
    ("017B", "Bryan Guo", "Distinguished HM (Top 20%)", 8, 7),
    ("017E", "Ryan Wu", "Distinguished HM (Top 20%)", 8, 7),
    ("030B", "Ryan Bansal", "Distinguished HM (Top 20%)", 8, 7),
    ("052F", "Kaleb So", "Distinguished HM (Top 20%)", 8, 7),
    ("057C", "Qiao Zhang", "Distinguished HM (Top 20%)", 8, 7),
    ("074C", "William Zhao", "Distinguished HM (Top 20%)", 8, 7),
    ("074F", "David Zhang", "Distinguished HM (Top 20%)", 8, 7),
    ("105E", "Charles Zhang", "Distinguished HM (Top 20%)", 8, 7),
    ("118E", "Benjamin Fu", "Distinguished HM (Top 20%)", 8, 7),
]

def normalize_name(name):
    return name.strip().lower()

def load_students():
    by_name = {}
    max_id = 0
    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            sid = int(row["student_id"])
            if sid > max_id:
                max_id = sid
            name = row["student_name"]
            state = row.get("state", "")
            key = normalize_name(name)
            by_name.setdefault(key, []).append((sid, name, state))
            for al in (row.get("alias", "") or "").split("|"):
                al = al.strip().lower()
                if al and al != key:
                    by_name.setdefault(al, []).append((sid, name, state))
    return by_name, max_id

def resolve_student(source_name, by_name, next_id, new_students):
    key = normalize_name(source_name)
    if key in by_name:
        candidates = by_name[key]
        if len(candidates) == 1:
            return candidates[0][0], candidates[0][1], candidates[0][2]
        for c in candidates:
            if c[2] == "":
                return c[0], c[1], c[2]
        return candidates[0][0], candidates[0][1], candidates[0][2]
    if "(" in source_name and ")" in source_name:
        m = re.match(r"(.+?)\((.+?)\)(.+)", source_name)
        if m:
            mid, right = m.group(2).strip(), m.group(3).strip()
            attempt_key = normalize_name(mid + " " + right)
            if attempt_key in by_name:
                c = by_name[attempt_key][0]
                return c[0], c[1], c[2]
    sid = next_id[0]
    next_id[0] += 1
    new_students.append((sid, source_name, ""))
    by_name.setdefault(key, []).append((sid, source_name, ""))
    return sid, source_name, ""

def main():
    by_name, max_id = load_students()
    next_id = [max_id + 1]
    new_students = []
    rows = []
    for bmt_id, source_name, award, rank, score in ROSTER:
        sid, canonical_name, state = resolve_student(source_name, by_name, next_id, new_students)
        rows.append({
            "student_id": sid,
            "student_name": canonical_name,
            "state": state,
            "year": YEAR,
            "bmt_student_id": bmt_id,
            "award": award,
            "rank": str(rank) if rank is not None else "",
            "score": str(score) if score is not None else "",
        })
    os.makedirs(os.path.dirname(RESULTS_CSV), exist_ok=True)
    fieldnames = ["student_id", "student_name", "state", "year", "bmt_student_id", "award", "rank", "score"]
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
