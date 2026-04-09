#!/usr/bin/env python3
"""
Check students with "MATHCOUNTS National — Rankings":
- Each such student must have NO MORE than 3 appearances (i.e. <= 3).
- All appearances must have different grade values (no duplicate grades).
"""

import json
from pathlib import Path

DATA_JSON = Path(__file__).resolve().parent.parent / "docs" / "data.json"
CONTEST_NAME = "MATHCOUNTS National — Rankings"


def main():
    with open(DATA_JSON) as f:
        data = json.load(f)

    violations = []

    for student in data["students"]:
        recs = student.get("rec") or student.get("records") or []
        mc_records = [
            r for r in recs
            if r.get("contest") == CONTEST_NAME
        ]
        if not mc_records:
            continue

        count = len(mc_records)
        grades = [r.get("grade") for r in mc_records if r.get("grade") is not None]
        # Treat missing grade as a distinct "value" for uniqueness
        grades_with_missing = [r.get("grade", "__MISSING__") for r in mc_records]
        unique_grades = len(set(grades_with_missing)) == len(grades_with_missing)

        if count > 3:
            violations.append({
                "id": student["id"],
                "name": student.get("nm") or student.get("name"),
                "issue": ">3 appearances",
                "count": count,
                "grades": sorted(grades_with_missing),
            })
        elif not unique_grades:
            from collections import Counter
            dupes = {g: c for g, c in Counter(grades_with_missing).items() if c > 1}
            violations.append({
                "id": student["id"],
                "name": student.get("nm") or student.get("name"),
                "issue": "duplicate grade values",
                "count": count,
                "grades": sorted(grades_with_missing),
                "duplicates": dupes,
            })
        # else: valid (count <= 3, all grades distinct) — not printed

    for v in sorted(violations, key=lambda x: (x["name"], x["id"])):
        print(f"id={v['id']}  {v['name']}")
        print(f"  {v['issue']}  (appearances: {v['count']})  grades: {v['grades']}")
        if "duplicates" in v:
            print(f"  duplicate counts: {v['duplicates']}")
        print()

    return 0 if not violations else 1


if __name__ == "__main__":
    exit(main())
