#!/usr/bin/env python3
"""
Fill blank gender in database/students/students.csv based on student_name.

Uses same rules as add_gender_column.py:
- If the student appears in database/contests/mpfg (any year), gender = female.
- Else if the student's name looks like a female name, gender = female.
- Otherwise gender = male.
Only updates rows where gender is currently blank.
"""

import csv
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
STUDENTS_CSV = os.path.join(REPO_ROOT, "database", "students", "students.csv")
MPFG_BASE = os.path.join(REPO_ROOT, "database", "contests", "mpfg")

FEMALE_FIRST_NAMES = frozenset({
    "Abigail", "Adya", "Alicia", "Alice", "Alyssa", "Alyara", "Amelia", "Amy",
    "Angela", "Angeline", "Angie", "Annabel", "Anne", "Annie", "Ashley",
    "Audrey", "Aashita", "Adya", "Alena", "Alina", "Allison", "Alyssa",
    "Angelina", "Anna", "Annabel", "Carol", "Camea", "Caroline", "Catherine",
    "Cecily", "Celina", "Charlotte", "Chloe", "Cordelia", "Dahlia", "Diana",
    "Doris", "Elena", "Elaine", "Elita", "Ellie", "Emily", "Emma", "Enya",
    "Erin", "Eva", "Evelyn", "Fiona", "Grace", "Greta", "Gloria", "Hadley", "Hailey",
    "Hannah", "Haruka", "Heather", "Helen", "Himani", "Irene", "Iris", "Ishani",
    "Ivy", "Jane", "Janice", "Jennifer", "Jessica", "Jessie", "Jiayu", "Joyce",
    "Julia", "Kailua", "Kallie", "Kalina", "Katherine", "Katie", "Kaylee",
    "Kaylyn", "Kelsey", "Kira", "Kristin", "Kristine", "Kristie", "Laura",
    "Lanie", "Linda", "Lillian", "Lingfei", "Lisa", "Lorraine", "Lucy",
    "Madeline", "Maiya", "Maya", "Medha", "Melody", "Michelle", "Mikayla",
    "Mina", "Miranda", "Natalie", "Naomi", "Nina", "Olivia", "Paige", "Patricia",
    "Raina", "Reese", "Riya", "Saanvi", "Sadie", "Sally", "Sarah", "Scarlet",
    "Selena", "Shirley", "Shruti", "Simona", "Sophia", "Sophie", "Sneha",
    "Susie", "Sylvia", "Tatiana", "Tiffany", "Tina", "Victoria", "Vivian",
    "Vaidehi", "Wensi", "Yunong", "Zaee", "Zhara", "Ariel", "Brooke", "Brianna", "Cady",
    "Ekam", "Honjar", "Kaitlyn", "Keming", "Malory", "Rania", "Rafi", "Liran",
    "Melissa", "Meredith", "Molly", "Nadia", "Nicole", "Nora", "Rachel",
    "Rebecca", "Sandra", "Sara", "Shreyan", "Sola", "Sylvia", "Worrawat",
})


def load_mpfg_student_ids():
    ids = set()
    for year_dir in ("year=2022", "year=2023", "year=2024", "year=2025"):
        path = os.path.join(MPFG_BASE, year_dir, "results.csv")
        if not os.path.isfile(path):
            continue
        with open(path, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                try:
                    ids.add(int(row["student_id"]))
                except (KeyError, ValueError):
                    pass
    return ids


def name_looks_female(student_name):
    if not (student_name and student_name.strip()):
        return False
    tokens = [t.strip() for t in student_name.replace(",", " ").split() if t.strip()]
    lower_set = {n.lower() for n in FEMALE_FIRST_NAMES}
    for t in tokens:
        t_clean = t.split("(")[0].strip()
        if len(t_clean) <= 1:
            continue
        # Check parenthetical nickname too (e.g. Weiping(Jessica) Li)
        if "(" in t:
            for part in t.split("(")[1].rstrip(")").split():
                if part.strip().lower() in lower_set:
                    return True
        if t_clean.lower() in lower_set:
            return True
    return False


def main():
    mpfg_ids = load_mpfg_student_ids()

    rows = []
    filled = 0
    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        for row in reader:
            gender = (row.get("gender") or "").strip()
            if not gender:
                try:
                    sid_int = int(row.get("student_id", ""))
                except ValueError:
                    sid_int = None
                name = (row.get("student_name") or "").strip()
                if sid_int is not None and sid_int in mpfg_ids:
                    row["gender"] = "female"
                elif name_looks_female(name):
                    row["gender"] = "female"
                else:
                    row["gender"] = "male"
                filled += 1
            rows.append(row)

    with open(STUDENTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Filled {filled} blank gender(s) in {STUDENTS_CSV}")


if __name__ == "__main__":
    main()
