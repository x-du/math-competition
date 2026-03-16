#!/usr/bin/env python3
"""
Add BMT 2023 Discrete individual results from the PDF roster.
Resolves student_id from students.csv; appends new students as needed.
Includes year=2023 and bmt_student_id in results.
"""
import csv
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDENTS_CSV = os.path.join(REPO_ROOT, "database", "students", "students.csv")
RESULTS_CSV = os.path.join(REPO_ROOT, "database", "contests", "bmt-discrete", "year=2023", "results.csv")
YEAR = 2023

# Roster from BMT 2023 discrete.pdf — (bmt_student_id, source_name, award, rank, score)
ROSTER = [
    # Honorable Mention (Top 50%)
    ("003C", "Hannah Fox", "Honorable Mention (Top 50%)", None, None),
    ("003D", "Peter Ferolito", "Honorable Mention (Top 50%)", None, None),
    ("003F", "Aarush Khare", "Honorable Mention (Top 50%)", None, None),
    ("004E", "Eddie Wang", "Honorable Mention (Top 50%)", None, None),
    ("005E", "Alena Kutsuk", "Honorable Mention (Top 50%)", None, None),
    ("011B", "Brianna Zheng", "Honorable Mention (Top 50%)", None, None),
    ("014B", "Anna Deng", "Honorable Mention (Top 50%)", None, None),
    ("015B", "Katrina Liu", "Honorable Mention (Top 50%)", None, None),
    ("015C", "Alex Backues", "Honorable Mention (Top 50%)", None, None),
    ("015D", "Aidan Bai", "Honorable Mention (Top 50%)", None, None),
    ("017A", "Ryan Bai", "Honorable Mention (Top 50%)", None, None),
    ("017F", "Larry Wu", "Honorable Mention (Top 50%)", None, None),
    ("018B", "Gore Fee", "Honorable Mention (Top 50%)", None, None),
    ("019C", "Yuan Chen", "Honorable Mention (Top 50%)", None, None),
    ("027C", "Advaith Mopuri", "Honorable Mention (Top 50%)", None, None),
    ("027D", "Varun Rao", "Honorable Mention (Top 50%)", None, None),
    ("028B", "Abhinav Raja", "Honorable Mention (Top 50%)", None, None),
    ("028C", "Zachary Pan", "Honorable Mention (Top 50%)", None, None),
    ("028D", "Veeral Shroff", "Honorable Mention (Top 50%)", None, None),
    ("032C", "Lucas Yuan", "Honorable Mention (Top 50%)", None, None),
    ("034B", "Vihaan Gupta", "Honorable Mention (Top 50%)", None, None),
    ("034D", "Andy Lu", "Honorable Mention (Top 50%)", None, None),
    ("036E", "Kristiyan Kurtev", "Honorable Mention (Top 50%)", None, None),
    ("036F", "Henry He", "Honorable Mention (Top 50%)", None, None),
    ("039A", "Shihan Kanungo", "Honorable Mention (Top 50%)", None, None),
    ("039D", "Roger Fan", "Honorable Mention (Top 50%)", None, None),
    ("039F", "Nathan Ye", "Honorable Mention (Top 50%)", None, None),
    ("041A", "Nicholas Weng", "Honorable Mention (Top 50%)", None, None),
    ("043A", "Bryan Li", "Honorable Mention (Top 50%)", None, None),
    ("046D", "Aarush Vailaya", "Honorable Mention (Top 50%)", None, None),
    ("047B", "Sylvia Chen", "Honorable Mention (Top 50%)", None, None),
    ("052C", "Kyle Lei", "Honorable Mention (Top 50%)", None, None),
    ("053F", "Daniel Yang", "Honorable Mention (Top 50%)", None, None),
    ("057B", "Alex Bai", "Honorable Mention (Top 50%)", None, None),
    ("064A", "Matthew Fakler", "Honorable Mention (Top 50%)", None, None),
    ("069E", "David Fox", "Honorable Mention (Top 50%)", None, None),
    ("069F", "Agniv Sarkar", "Honorable Mention (Top 50%)", None, None),
    ("070F", "Rivka Lipkovitz", "Honorable Mention (Top 50%)", None, None),
    ("073C", "Taran Ajith", "Honorable Mention (Top 50%)", None, None),
    ("074B", "Ankit Muppala", "Honorable Mention (Top 50%)", None, None),
    ("076B", "Isaac Lee", "Honorable Mention (Top 50%)", None, None),
    ("096A", "Christopher Chen", "Honorable Mention (Top 50%)", None, None),
    ("099B", "Andrew Wen", "Honorable Mention (Top 50%)", None, None),
    ("100C", "Andrew Wang", "Honorable Mention (Top 50%)", None, None),
    ("115C", "Aaron Chen", "Honorable Mention (Top 50%)", None, None),
    ("118F", "Alansha Jiang", "Honorable Mention (Top 50%)", None, None),
    ("122E", "Blake Chang", "Honorable Mention (Top 50%)", None, None),
    ("123C", "Zheyuan Li", "Honorable Mention (Top 50%)", None, None),
    ("123E", "Henry McNamara", "Honorable Mention (Top 50%)", None, None),
    ("124F", "Tommy Zhou", "Honorable Mention (Top 50%)", None, None),
    ("125B", "Eric Wang", "Honorable Mention (Top 50%)", None, None),
    ("125D", "Amudhan Gurumoorthy", "Honorable Mention (Top 50%)", None, None),
    ("125E", "Ivan Yu", "Honorable Mention (Top 50%)", None, None),
    ("126D", "Sanya Badhe", "Honorable Mention (Top 50%)", None, None),
    # Distinguished HM (Top 20%) — not in top scores list
    ("003A", "Aiden Jeong", "Distinguished HM (Top 20%)", None, None),
    ("005B", "Tejo Madhavarapu", "Distinguished HM (Top 20%)", None, None),
    ("011A", "Pranav Bodapati", "Distinguished HM (Top 20%)", None, None),
    ("015E", "Andrew Tian", "Distinguished HM (Top 20%)", None, None),
    ("017C", "Ethan K Song", "Distinguished HM (Top 20%)", None, None),
    ("030D", "Sohil Rathi", "Distinguished HM (Top 20%)", None, None),
    ("030E", "Neel Kolhe", "Distinguished HM (Top 20%)", None, None),
    ("034A", "Chenghao HU", "Distinguished HM (Top 20%)", None, None),
    ("034C", "Harish Loghashankar", "Distinguished HM (Top 20%)", None, None),
    ("039C", "Josh Shin", "Distinguished HM (Top 20%)", None, None),
    ("044A", "Emily Wu", "Distinguished HM (Top 20%)", None, None),
    ("046B", "Neil Krishnan", "Distinguished HM (Top 20%)", None, None),
    ("064F", "Dev Saxena", "Distinguished HM (Top 20%)", None, None),
    ("080C", "Zaee Shah", "Distinguished HM (Top 20%)", None, None),
    ("105C", "Sidarth Erat", "Distinguished HM (Top 20%)", None, None),
    ("115B", "Feodor Yevtushenko", "Distinguished HM (Top 20%)", None, None),
    ("115E", "Justin Mu", "Distinguished HM (Top 20%)", None, None),
    ("117E", "Rohan Dhillon", "Distinguished HM (Top 20%)", None, None),
    ("117F", "Onkit Samanta", "Distinguished HM (Top 20%)", None, None),
    ("122A", "Neal Frankenberg", "Distinguished HM (Top 20%)", None, None),
    # Top scores (rank and score) — PDF order: 1st through 8th (14-way tie)
    ("007A", "Linus Tang", "Distinguished HM (Top 20%)", 1, 9),
    ("118A", "Alex Zhao", "Distinguished HM (Top 20%)", 2, 9),
    ("007B", "Rohan Bodke", "Distinguished HM (Top 20%)", 3, 9),
    ("030F", "Brian Xue", "Distinguished HM (Top 20%)", 4, 8),
    ("007C", "Christopher Bao", "Distinguished HM (Top 20%)", 5, 8),
    ("007F", "Ritwin Narra", "Distinguished HM (Top 20%)", 6, 8),
    ("003B", "Rohan Garg", "Distinguished HM (Top 20%)", 6, 8),
    ("003E", "Jonathan Du", "Distinguished HM (Top 20%)", 8, 7),
    ("007D", "Rohan Das", "Distinguished HM (Top 20%)", 8, 7),
    ("007E", "Alex Chen", "Distinguished HM (Top 20%)", 8, 7),
    ("017D", "Michelle Liang", "Distinguished HM (Top 20%)", 8, 7),
    ("027E", "Evan Yang", "Distinguished HM (Top 20%)", 8, 7),
    ("039E", "Steve Zhang", "Distinguished HM (Top 20%)", 8, 7),
    ("043B", "Victoria Hu", "Distinguished HM (Top 20%)", 8, 7),
    ("043D", "Skyler Mao", "Distinguished HM (Top 20%)", 8, 7),
    ("043F", "Lawson Wang", "Distinguished HM (Top 20%)", 8, 7),
    ("057C", "Qiao Zhang", "Distinguished HM (Top 20%)", 8, 7),
    ("074F", "David Zhang", "Distinguished HM (Top 20%)", 8, 7),
    ("111F", "William Wu", "Distinguished HM (Top 20%)", 8, 7),
    ("118B", "Immanuel Whang", "Distinguished HM (Top 20%)", 8, 7),
    ("118D", "Mingyue Yang", "Distinguished HM (Top 20%)", 8, 7),
    ("122D", "Uma Shukla", "Distinguished HM (Top 20%)", 8, 7),
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
