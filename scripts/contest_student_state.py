"""Fill empty students.csv `state` from contest country names (IMO / EGMO imports)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict


def fill_missing_state_from_country(
    students_csv: Path,
    student_id_to_country: Dict[str, str],
) -> int:
    """
    For each student_id in student_id_to_country, if students.csv has an empty state,
    set state to the given country name.

    Returns the number of rows updated.
    """
    if not student_id_to_country:
        return 0

    with open(students_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if not fieldnames or "student_id" not in fieldnames or "state" not in fieldnames:
            raise ValueError(f"students.csv must have student_id and state columns: {students_csv}")
        rows = list(reader)

    # Normalize keys for lookup
    norm_map = {str(k).strip(): v.strip() for k, v in student_id_to_country.items() if str(k).strip() and v.strip()}

    updated = 0
    for row in rows:
        sid = (row.get("student_id") or "").strip()
        if sid not in norm_map:
            continue
        current = (row.get("state") or "").strip()
        if current:
            continue
        row["state"] = norm_map[sid]
        updated += 1

    if updated:
        with open(students_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    return updated
