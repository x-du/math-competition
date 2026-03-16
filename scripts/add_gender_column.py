#!/usr/bin/env python3
"""
Add a 'gender' column to database/students/students.csv.

Rules:
- If the student appears in database/contests/mpfg (any year), gender = female.
- Else if the student's name looks like a female name (any token matches a known
  female first name), gender = female.
- Otherwise gender = male.
"""

import csv
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
STUDENTS_CSV = os.path.join(REPO_ROOT, "database", "students", "students.csv")
MPFG_BASE = os.path.join(REPO_ROOT, "database", "contests", "mpfg")

# Common female first names (English and others seen in the data).
# Used only when the student is NOT in MPFG.
FEMALE_FIRST_NAMES = frozenset({
    "Abigail", "Adya", "Alicia", "Alice", "Alyssa", "Alyara", "Amelia", "Amy",
    "Angela", "Angeline", "Angie", "Annabel", "Anne", "Annie", "Ashley",
    "Audrey", "Aashita", "Adya", "Alena", "Alina", "Allison", "Alyssa",
    "Angelina", "Anna", "Annabel", "Carol", "Camea", "Caroline", "Catherine",
    "Cecily", "Celina", "Charlotte", "Chloe", "Cordelia", "Dahlia", "Diana",
    "Doris", "Elena", "Elaine", "Elita", "Ellie", "Emily", "Emma", "Enya",
    "Erin", "Evelyn", "Fiona", "Grace", "Greta", "Gloria", "Hadley", "Hailey",
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
    "Vaidehi", "Wensi", "Yunong", "Zaee", "Zhara", "Ariel", "Brooke", "Cady",
    "Ekam", "Honjar", "Kaitlyn", "Keming", "Malory", "Rania", "Rafi", "Liran",
    "Melissa", "Meredith", "Molly", "Nadia", "Nicole", "Nora", "Rachel",
    "Rebecca", "Sandra", "Sara", "Shreyan", "Sola", "Sylvia", "Worrawat",
})


def load_mpfg_student_ids():
    """Return set of student_id that appear in any MPFG results."""
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
    """True if any token of the name is in FEMALE_FIRST_NAMES (case-insensitive)."""
    if not (student_name and student_name.strip()):
        return False
    tokens = [t.strip() for t in student_name.replace(",", " ").split() if t.strip()]
    lower_set = {n.lower() for n in FEMALE_FIRST_NAMES}
    for t in tokens:
        # Ignore parenthetical nicknames and single letters
        t_clean = t.split("(")[0].strip()
        if len(t_clean) <= 1:
            continue
        if t_clean.lower() in lower_set:
            return True
    return False


def main():
    mpfg_ids = load_mpfg_student_ids()

    rows = []
    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames) + ["gender"]
        for row in reader:
            sid = row.get("student_id", "")
            try:
                sid_int = int(sid)
            except ValueError:
                sid_int = None
            name = (row.get("student_name") or "").strip()

            if sid_int is not None and sid_int in mpfg_ids:
                row["gender"] = "female"
            elif name_looks_female(name):
                row["gender"] = "female"
            else:
                row["gender"] = "male"
            rows.append(row)

    with open(STUDENTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Updated {STUDENTS_CSV}: added column 'gender'.")
    female_count = sum(1 for r in rows if r["gender"] == "female")
    male_count = sum(1 for r in rows if r["gender"] == "male")
    print(f"  female: {female_count}, male: {male_count}")


if __name__ == "__main__":
    main()
