#!/usr/bin/env python3
"""Check for same student (by name or id) with different grades in the same competition."""
import json
from collections import defaultdict

def main():
    with open("docs/data.json") as f:
        data = json.load(f)

    # --- Check 1: Same student ID, same contest+year, different grades ---
    by_id = []
    for student in data["students"]:
        sid = student["id"]
        name = student["name"]
        by_comp = defaultdict(list)
        for rec in student.get("records", []):
            slug, year = rec.get("contest_slug"), rec.get("year")
            if slug is None or year is None:
                continue
            grade = rec.get("grade")
            by_comp[(slug, year)].append(grade)
        for (slug, year), grades in by_comp.items():
            grades_present = [g for g in grades if g is not None]
            if len(grades_present) >= 2:
                unique = set(str(g).strip() for g in grades_present)
                if len(unique) > 1:
                    by_id.append({
                        "student_id": sid, "name": name,
                        "contest_slug": slug, "year": year,
                        "grades": sorted(unique),
                    })

    # --- Check 2: Same competition (contest_slug + year), same student_name, different grades ---
    # Build list of (contest_slug, year, student_name, grade) from all records
    all_records = []
    for student in data["students"]:
        name = student["name"]
        for rec in student.get("records", []):
            slug = rec.get("contest_slug")
            year = rec.get("year")
            grade = rec.get("grade")
            if slug is None or year is None:
                continue
            all_records.append((slug, year, rec.get("student_name") or name, grade))

    by_name = defaultdict(list)  # (slug, year, student_name) -> list of grades
    for slug, year, sname, grade in all_records:
        key = (slug, str(year).strip(), (sname or "").strip())
        by_name[key].append(grade)

    by_name_issues = []
    for (slug, year, sname), grades in by_name.items():
        grades_present = [g for g in grades if g is not None]
        if len(grades_present) < 2:
            continue
        unique = set(str(g).strip() for g in grades_present)
        if len(unique) > 1:
            by_name_issues.append({
                "contest_slug": slug, "year": year, "student_name": sname,
                "grades": sorted(unique), "count": len(grades),
            })

    # Report
    print("=== By student ID (same person, same competition, multiple grades) ===")
    if not by_id:
        print("None found.")
    else:
        for i in by_id:
            print(f"  id={i['student_id']} ({i['name']}): {i['contest_slug']} {i['year']} -> {i['grades']}")

    print("\n=== By student name (same name in same competition with different grades) ===")
    if not by_name_issues:
        print("None found.")
    else:
        for i in by_name_issues:
            print(f"  \"{i['student_name']}\": {i['contest_slug']} {i['year']} -> grades {i['grades']} (records: {i['count']})")

if __name__ == "__main__":
    main()
