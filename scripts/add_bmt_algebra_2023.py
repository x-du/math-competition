#!/usr/bin/env python3
"""
Add BMT 2023 Algebra individual results from the PDF roster.
Resolves student_id from students.csv; appends new students as needed.
Includes year=2023 and bmt_student_id in results.
"""
import csv
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDENTS_CSV = os.path.join(REPO_ROOT, "database", "students", "students.csv")
RESULTS_CSV = os.path.join(REPO_ROOT, "database", "contests", "bmt-algebra", "year=2023", "results.csv")
YEAR = 2023

# Roster from BMT 2023 algebra.pdf — (bmt_student_id, source_name, award, rank, score)
ROSTER = [
    # Honorable Mention (Top 50%) — 116D Julian Kuang appears once (deduped)
    ("004D", "Qi Huang", "Honorable Mention (Top 50%)", None, None),
    ("004E", "Eddie Wang", "Honorable Mention (Top 50%)", None, None),
    ("005C", "Jeffery Wang", "Honorable Mention (Top 50%)", None, None),
    ("010A", "Chloe So", "Honorable Mention (Top 50%)", None, None),
    ("011A", "Pranav Bodapati", "Honorable Mention (Top 50%)", None, None),
    ("011B", "Brianna Zheng", "Honorable Mention (Top 50%)", None, None),
    ("011D", "Joshua Balmin", "Honorable Mention (Top 50%)", None, None),
    ("011F", "Lorraine Wang", "Honorable Mention (Top 50%)", None, None),
    ("014B", "Anna Deng", "Honorable Mention (Top 50%)", None, None),
    ("014E", "Nicholas Wang", "Honorable Mention (Top 50%)", None, None),
    ("015B", "Katrina Liu", "Honorable Mention (Top 50%)", None, None),
    ("015C", "Alex Backues", "Honorable Mention (Top 50%)", None, None),
    ("015E", "Andrew Tian", "Honorable Mention (Top 50%)", None, None),
    ("016B", "Dylan Kim", "Honorable Mention (Top 50%)", None, None),
    ("016C", "Delong Mao", "Honorable Mention (Top 50%)", None, None),
    ("016D", "Chen Andrew", "Honorable Mention (Top 50%)", None, None),
    ("016E", "Justin Zhang", "Honorable Mention (Top 50%)", None, None),
    ("017F", "Larry Wu", "Honorable Mention (Top 50%)", None, None),
    ("018F", "Gaurav Gupta", "Honorable Mention (Top 50%)", None, None),
    ("019B", "Pratham Mehta", "Honorable Mention (Top 50%)", None, None),
    ("019C", "Yuan Chen", "Honorable Mention (Top 50%)", None, None),
    ("019D", "Aster Deng", "Honorable Mention (Top 50%)", None, None),
    ("019F", "Amber Mo", "Honorable Mention (Top 50%)", None, None),
    ("021C", "Asher Ding", "Honorable Mention (Top 50%)", None, None),
    ("021F", "Matthew Sun", "Honorable Mention (Top 50%)", None, None),
    ("022A", "Kathleen Chen", "Honorable Mention (Top 50%)", None, None),
    ("023F", "Ishaan Rout", "Honorable Mention (Top 50%)", None, None),
    ("025D", "Arsh Shah", "Honorable Mention (Top 50%)", None, None),
    ("026A", "Jessica Yan", "Honorable Mention (Top 50%)", None, None),
    ("026E", "Ethan Yan", "Honorable Mention (Top 50%)", None, None),
    ("027B", "Jeffrey Li", "Honorable Mention (Top 50%)", None, None),
    ("027C", "Advaith Mopuri", "Honorable Mention (Top 50%)", None, None),
    ("027D", "Varun Rao", "Honorable Mention (Top 50%)", None, None),
    ("028B", "Abhinav Raja", "Honorable Mention (Top 50%)", None, None),
    ("028C", "Zachary Pan", "Honorable Mention (Top 50%)", None, None),
    ("030B", "Ryan Bansal", "Honorable Mention (Top 50%)", None, None),
    ("034B", "Vihaan Gupta", "Honorable Mention (Top 50%)", None, None),
    ("034D", "Andy Lu", "Honorable Mention (Top 50%)", None, None),
    ("034F", "Sarthak Jain", "Honorable Mention (Top 50%)", None, None),
    ("035C", "Shomak Tan", "Honorable Mention (Top 50%)", None, None),
    ("035E", "Arthur Li", "Honorable Mention (Top 50%)", None, None),
    ("036B", "Rhishi Balaa Sakthivel", "Honorable Mention (Top 50%)", None, None),
    ("036C", "Abhi Kotari", "Honorable Mention (Top 50%)", None, None),
    ("036F", "Henry He", "Honorable Mention (Top 50%)", None, None),
    ("040E", "Haridas Chowdhury", "Honorable Mention (Top 50%)", None, None),
    ("041B", "Benjamin Liu", "Honorable Mention (Top 50%)", None, None),
    ("042E", "Arvin Hormati", "Honorable Mention (Top 50%)", None, None),
    ("044C", "Ella Li", "Honorable Mention (Top 50%)", None, None),
    ("045A", "Caden Ruan", "Honorable Mention (Top 50%)", None, None),
    ("045C", "Terry Xie", "Honorable Mention (Top 50%)", None, None),
    ("045F", "Eddie Zhang", "Honorable Mention (Top 50%)", None, None),
    ("048A", "Aman Chandra", "Honorable Mention (Top 50%)", None, None),
    ("050B", "Jonathan Li", "Honorable Mention (Top 50%)", None, None),
    ("052B", "Jaewoo Park", "Honorable Mention (Top 50%)", None, None),
    ("052C", "Kyle Lei", "Honorable Mention (Top 50%)", None, None),
    ("053B", "Dayeon Lim", "Honorable Mention (Top 50%)", None, None),
    ("054B", "Krishan Gupta", "Honorable Mention (Top 50%)", None, None),
    ("057E", "Shaun Masada", "Honorable Mention (Top 50%)", None, None),
    ("059A", "Radhika Shah", "Honorable Mention (Top 50%)", None, None),
    ("061B", "Alex Zhao", "Honorable Mention (Top 50%)", None, None),
    ("061F", "Jake Hu", "Honorable Mention (Top 50%)", None, None),
    ("064B", "Samuel Chen", "Honorable Mention (Top 50%)", None, None),
    ("069B", "Alex Cao", "Honorable Mention (Top 50%)", None, None),
    ("070D", "Julian Stockton", "Honorable Mention (Top 50%)", None, None),
    ("073D", "Vedanth Dala", "Honorable Mention (Top 50%)", None, None),
    ("073E", "Harshil Nukala", "Honorable Mention (Top 50%)", None, None),
    ("073F", "Andrew Peng", "Honorable Mention (Top 50%)", None, None),
    ("074B", "Ankit Muppala", "Honorable Mention (Top 50%)", None, None),
    ("074C", "William Zhao", "Honorable Mention (Top 50%)", None, None),
    ("074D", "Hunter Bian", "Honorable Mention (Top 50%)", None, None),
    ("075C", "Aaron Shen", "Honorable Mention (Top 50%)", None, None),
    ("076B", "Isaac Lee", "Honorable Mention (Top 50%)", None, None),
    ("079B", "Elaina Li", "Honorable Mention (Top 50%)", None, None),
    ("080D", "Bruce Zhang", "Honorable Mention (Top 50%)", None, None),
    ("091A", "Athena Richter", "Honorable Mention (Top 50%)", None, None),
    ("092B", "Arnav Ahuja", "Honorable Mention (Top 50%)", None, None),
    ("096C", "Kevin Yan", "Honorable Mention (Top 50%)", None, None),
    ("096E", "Ryan Li", "Honorable Mention (Top 50%)", None, None),
    ("096F", "Kai Lum", "Honorable Mention (Top 50%)", None, None),
    ("098D", "Sean Li", "Honorable Mention (Top 50%)", None, None),
    ("099A", "Brian Lu", "Honorable Mention (Top 50%)", None, None),
    ("099D", "Nathan Jiang", "Honorable Mention (Top 50%)", None, None),
    ("099F", "Forrest Chou", "Honorable Mention (Top 50%)", None, None),
    ("101A", "Jessica Wu", "Honorable Mention (Top 50%)", None, None),
    ("101C", "Sheldon Tan", "Honorable Mention (Top 50%)", None, None),
    ("103A", "Eric Xiao", "Honorable Mention (Top 50%)", None, None),
    ("103D", "Sophia Henningsen", "Honorable Mention (Top 50%)", None, None),
    ("105A", "Teddy Xu", "Honorable Mention (Top 50%)", None, None),
    ("105E", "Charles Zhang", "Honorable Mention (Top 50%)", None, None),
    ("106B", "Xuehan Zhang", "Honorable Mention (Top 50%)", None, None),
    ("108A", "Sabrina Wang", "Honorable Mention (Top 50%)", None, None),
    ("111A", "Carolyn Ruan", "Honorable Mention (Top 50%)", None, None),
    ("111B", "Ishaan Desai", "Honorable Mention (Top 50%)", None, None),
    ("112F", "Owen Lu", "Honorable Mention (Top 50%)", None, None),
    ("115A", "Larry Xing", "Honorable Mention (Top 50%)", None, None),
    ("116A", "Pengyu Chen", "Honorable Mention (Top 50%)", None, None),
    ("116D", "Julian Kuang", "Honorable Mention (Top 50%)", None, None),
    ("117A", "Edward Li", "Honorable Mention (Top 50%)", None, None),
    ("117C", "Wesley Wu", "Honorable Mention (Top 50%)", None, None),
    ("117D", "Christopher Peng", "Honorable Mention (Top 50%)", None, None),
    ("118B", "Immanuel Whang", "Honorable Mention (Top 50%)", None, None),
    ("120D", "Claire Zhao", "Honorable Mention (Top 50%)", None, None),
    ("122A", "Neal Frankenberg", "Honorable Mention (Top 50%)", None, None),
    ("122E", "Blake Chang", "Honorable Mention (Top 50%)", None, None),
    ("123A", "Leo Tsai", "Honorable Mention (Top 50%)", None, None),
    ("123B", "Noel Zhang", "Honorable Mention (Top 50%)", None, None),
    ("123C", "Zheyuan Li", "Honorable Mention (Top 50%)", None, None),
    ("123E", "Henry McNamara", "Honorable Mention (Top 50%)", None, None),
    ("124D", "Larry Zhou", "Honorable Mention (Top 50%)", None, None),
    ("124E", "Yan Lee", "Honorable Mention (Top 50%)", None, None),
    ("125A", "DongLin Jin", "Honorable Mention (Top 50%)", None, None),
    ("125B", "Eric Wang", "Honorable Mention (Top 50%)", None, None),
    ("125D", "Amudhan Gurumoorthy", "Honorable Mention (Top 50%)", None, None),
    ("126D", "Sanya Badhe", "Honorable Mention (Top 50%)", None, None),
    # Distinguished HM (Top 20%) — exclude top 10
    ("003B", "Rohan Garg", "Distinguished HM (Top 20%)", None, None),
    ("003D", "Peter Ferolito", "Distinguished HM (Top 20%)", None, None),
    ("011C", "Robert Feng", "Distinguished HM (Top 20%)", None, None),
    ("015A", "Kai Yi", "Distinguished HM (Top 20%)", None, None),
    ("017A", "Ryan Bai", "Distinguished HM (Top 20%)", None, None),
    ("017B", "Bryan Guo", "Distinguished HM (Top 20%)", None, None),
    ("017E", "Ryan Wu", "Distinguished HM (Top 20%)", None, None),
    ("018B", "Gore Fee", "Distinguished HM (Top 20%)", None, None),
    ("018C", "Ryan Fu", "Distinguished HM (Top 20%)", None, None),
    ("018E", "Kailua Cheng", "Distinguished HM (Top 20%)", None, None),
    ("020A", "Daniel Nie", "Distinguished HM (Top 20%)", None, None),
    ("030A", "Daniel Kim", "Distinguished HM (Top 20%)", None, None),
    ("030C", "Brian Bi", "Distinguished HM (Top 20%)", None, None),
    ("030D", "Sohil Rathi", "Distinguished HM (Top 20%)", None, None),
    ("030F", "Brian Xue", "Distinguished HM (Top 20%)", None, None),
    ("034A", "Chenghao HU", "Distinguished HM (Top 20%)", None, None),
    ("034E", "Seabert Mao", "Distinguished HM (Top 20%)", None, None),
    ("039C", "Josh Shin", "Distinguished HM (Top 20%)", None, None),
    ("041A", "Nicholas Weng", "Distinguished HM (Top 20%)", None, None),
    ("043B", "Victoria Hu", "Distinguished HM (Top 20%)", None, None),
    ("043C", "Alan Lu", "Distinguished HM (Top 20%)", None, None),
    ("044E", "Vivian Zhong", "Distinguished HM (Top 20%)", None, None),
    ("046D", "Aarush Vailaya", "Distinguished HM (Top 20%)", None, None),
    ("048C", "Cyrus Ghane", "Distinguished HM (Top 20%)", None, None),
    ("049D", "Haofang Zhu", "Distinguished HM (Top 20%)", None, None),
    ("052F", "Kaleb So", "Distinguished HM (Top 20%)", None, None),
    ("061E", "Akilan Paramasivam", "Distinguished HM (Top 20%)", None, None),
    ("064F", "Dev Saxena", "Distinguished HM (Top 20%)", None, None),
    ("065A", "Zhan Jin", "Distinguished HM (Top 20%)", None, None),
    ("069E", "David Fox", "Distinguished HM (Top 20%)", None, None),
    ("069F", "Agniv Sarkar", "Distinguished HM (Top 20%)", None, None),
    ("074E", "Julia Xiang", "Distinguished HM (Top 20%)", None, None),
    ("092E", "Anish Roy", "Distinguished HM (Top 20%)", None, None),
    ("099B", "Andrew Wen", "Distinguished HM (Top 20%)", None, None),
    ("099C", "Veenu Damarla", "Distinguished HM (Top 20%)", None, None),
    ("105C", "Sidarth Erat", "Distinguished HM (Top 20%)", None, None),
    ("105D", "Anthony Wang", "Distinguished HM (Top 20%)", None, None),
    ("105F", "Elliott Liu", "Distinguished HM (Top 20%)", None, None),
    ("106D", "Xinyu Meng", "Distinguished HM (Top 20%)", None, None),
    ("111F", "William Wu", "Distinguished HM (Top 20%)", None, None),
    ("115C", "Aaron Chen", "Distinguished HM (Top 20%)", None, None),
    ("115D", "Neal Yan", "Distinguished HM (Top 20%)", None, None),
    ("115E", "Justin Mu", "Distinguished HM (Top 20%)", None, None),
    ("118D", "Mingyue Yang", "Distinguished HM (Top 20%)", None, None),
    ("118E", "Benjamin Fu", "Distinguished HM (Top 20%)", None, None),
    ("118F", "Alansha Jiang", "Distinguished HM (Top 20%)", None, None),
    ("119A", "Ricky Hu", "Distinguished HM (Top 20%)", None, None),
    ("122D", "Uma Shukla", "Distinguished HM (Top 20%)", None, None),
    # Top 10 (rank and score) — PDF order; rank 3 tied (two people)
    ("007C", "Christopher Bao", "Distinguished HM (Top 20%)", 1, 9),
    ("043E", "Advaith Avadhanam", "Distinguished HM (Top 20%)", 2, 8),
    ("027A", "Brian Li", "Distinguished HM (Top 20%)", 3, 8),
    ("105B", "Jacopo Rizzo", "Distinguished HM (Top 20%)", 3, 8),
    ("115F", "Vivian Loh", "Distinguished HM (Top 20%)", 5, 8),
    ("030E", "Neel Kolhe", "Distinguished HM (Top 20%)", 6, 8),
    ("043A", "Bryan Li", "Distinguished HM (Top 20%)", 7, 8),
    ("049A", "Hengrui Liang", "Distinguished HM (Top 20%)", 8, 8),
    ("115B", "Feodor Yevtushenko", "Distinguished HM (Top 20%)", 9, 8),
    ("043F", "Lawson Wang", "Distinguished HM (Top 20%)", 10, 8),
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
