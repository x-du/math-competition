#!/usr/bin/env python3
"""
Add BMT 2023 Calculus individual results from the PDF roster.
Resolves student_id from students.csv; appends new students as needed.
Includes year=2023 and bmt_student_id in results.
"""
import csv
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDENTS_CSV = os.path.join(REPO_ROOT, "database", "students", "students.csv")
RESULTS_CSV = os.path.join(REPO_ROOT, "database", "contests", "bmt-calculus", "year=2023", "results.csv")
YEAR = 2023

# Roster from BMT 2023 calculus.pdf — (bmt_student_id, source_name, award, rank, score)
ROSTER = [
    # Honorable Mention (Top 50%)
    ("004A", "Kevin Li", "Honorable Mention (Top 50%)", None, None),
    ("027F", "Patrick Chu", "Honorable Mention (Top 50%)", None, None),
    ("029C", "Evan Liu", "Honorable Mention (Top 50%)", None, None),
    ("037A", "Max Rombakh", "Honorable Mention (Top 50%)", None, None),
    ("039B", "Tanush Aggarwal", "Honorable Mention (Top 50%)", None, None),
    ("039F", "Nathan Ye", "Honorable Mention (Top 50%)", None, None),
    ("040E", "Haridas Chowdhury", "Honorable Mention (Top 50%)", None, None),
    ("041E", "Satvik Sivaraman", "Honorable Mention (Top 50%)", None, None),
    ("054B", "Krishan Gupta", "Honorable Mention (Top 50%)", None, None),
    ("065B", "Enze Chen", "Honorable Mention (Top 50%)", None, None),
    ("070D", "Julian Stockton", "Honorable Mention (Top 50%)", None, None),
    ("080A", "Mark Rhee", "Honorable Mention (Top 50%)", None, None),
    ("080B", "Sanjay Mukhyala", "Honorable Mention (Top 50%)", None, None),
    ("096E", "Ryan Li", "Honorable Mention (Top 50%)", None, None),
    ("099C", "Veenu Damarla", "Honorable Mention (Top 50%)", None, None),
    ("099D", "Nathan Jiang", "Honorable Mention (Top 50%)", None, None),
    ("099E", "William Wang", "Honorable Mention (Top 50%)", None, None),
    ("099F", "Forrest Chou", "Honorable Mention (Top 50%)", None, None),
    ("112A", "Koren Gila", "Honorable Mention (Top 50%)", None, None),
    ("116D", "Julian Kuang", "Honorable Mention (Top 50%)", None, None),
    ("117E", "Rohan Dhillon", "Honorable Mention (Top 50%)", None, None),
    ("120C", "Saravanan Valliappan", "Honorable Mention (Top 50%)", None, None),
    ("122B", "Marius Rutkowski", "Honorable Mention (Top 50%)", None, None),
    ("123B", "Noel Zhang", "Honorable Mention (Top 50%)", None, None),
    # Distinguished HM (Top 20%) with rank and score — PDF Top Scores order
    ("007D", "Rohan Das", "Distinguished HM (Top 20%)", 1, 9),
    ("105B", "Jacopo Rizzo", "Distinguished HM (Top 20%)", 2, 8),
    ("039D", "Roger Fan", "Distinguished HM (Top 20%)", 3, 8),
    ("007B", "Rohan Bodke", "Distinguished HM (Top 20%)", 4, 8),
    ("007F", "Ritwin Narra", "Distinguished HM (Top 20%)", 5, 8),
    ("115A", "Larry Xing", "Distinguished HM (Top 20%)", 6, 8),
    ("065A", "Zhan Jin", "Distinguished HM (Top 20%)", 7, 8),
    ("004C", "Eddy Li", "Distinguished HM (Top 20%)", 8, 7),
    ("005D", "Neil Kolekar", "Distinguished HM (Top 20%)", 8, 7),
    ("034F", "Sarthak Jain", "Distinguished HM (Top 20%)", 8, 7),
    ("041F", "Daniel Kou", "Distinguished HM (Top 20%)", 8, 7),
    ("064C", "Shenlone Wu", "Distinguished HM (Top 20%)", 8, 7),
    ("073D", "Vedanth Dala", "Distinguished HM (Top 20%)", 8, 7),
    ("099A", "Brian Lu", "Distinguished HM (Top 20%)", 8, 7),
    ("111B", "Ishaan Desai", "Distinguished HM (Top 20%)", 8, 7),
    ("119A", "Ricky Hu", "Distinguished HM (Top 20%)", 8, 7),
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
