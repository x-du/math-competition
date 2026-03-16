#!/usr/bin/env python3
"""
Add school names to AMO 2022 results from the USAMO Awardees PDF.
When state is missing, infer it from the school name.

Usage: python scripts/add_amo_2022_school_and_state.py [--dry-run]
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parent.parent
AMO_2022_RESULTS = ROOT / "database" / "contests" / "amo" / "year=2022" / "results.csv"
PDF_PATH = Path("/Users/xiaochendu/Dropbox/Xdu/Patrick/AMO/2022 USAMO Awardees.pdf")

# School/team name (lowercase substring) -> (state, accuracy 0-100).
SCHOOL_TO_STATE: list[tuple[str | re.Pattern, str, int]] = [
    ("vancouver olympiad school", "British Columbia, Canada", 92),
    ("phillips exeter", "New Hampshire", 92),
    ("exeter academy", "New Hampshire", 92),
    ("univ of chicago laboratory", "Illinois", 92),
    ("uchicago lab", "Illinois", 90),
    ("stuyvesant", "New York", 92),
    ("eastside education", "Washington", 85),
    ("krishna home school", "California", 80),
    ("orange county math circle", "California", 88),
    ("holderness school", "New Hampshire", 90),
    ("gauss academy", "North Carolina", 85),
    ("lexington high school", "Massachusetts", 90),
    ("torrey pines", "California", 90),
    ("cupertino high school", "California", 88),
    ("austin math circle", "Texas", 85),
    ("brewster academy", "New Hampshire", 90),
    ("lynbrook high school", "California", 90),
    ("springlight education", "California", 85),
    ("princeton international school", "New Jersey", 90),
    ("nueva", "California", 90),
    ("saratoga high school", "California", 90),
    ("west-windsor plainsboro", "New Jersey", 90),
    ("west windsor plainsboro", "New Jersey", 90),
    ("troy high school", "Michigan", 88),
    ("benjamin franklin high school", "Louisiana", 90),
    ("hunter college high school", "New York", 92),
    ("bishops school", "California", 90),
    ("bishop's school", "California", 90),
    ("kimball union academy", "New Hampshire", 90),
    ("basis independent silicon valley", "California", 90),
    ("thomas jefferson", "Virginia", 90),
    ("tjhsst", "Virginia", 92),
    ("james s. rickards", "Florida", 90),
    ("florida atlantic university", "Florida", 95),
    ("florida atlantic", "Florida", 92),
    ("archimedean middle conservatory", "Florida", 88),
    ("montgomery blair", "Maryland", 90),
    ("plano west", "Texas", 90),
    ("phillips academy", "Massachusetts", 92),
    ("cherry creek high school", "Colorado", 90),
    ("rutgers university", "New Jersey", 92),
    ("high technology high school", "New Jersey", 90),
    ("adlai e stevenson", "Illinois", 90),
    ("east ridge high school", "Minnesota", 90),
    ("wayzata high school", "Minnesota", 90),
    ("shanghai american school", "China", 95),
    ("dougherty valley", "California", 90),
    ("ivymax", "California", 88),
    ("proof school", "California", 90),
    ("whitney m young", "Illinois", 90),
    ("alphastar academy", "California", 90),
    ("westview high school", "California", 88),
    ("victoria international college", "British Columbia, Canada", 88),
    ("davidson academy", "Nevada", 90),
    ("olga radko math circle", "California", 88),
    ("ucla", "California", 90),
    ("acton-boxborough", "Massachusetts", 90),
    ("acton boxborough", "Massachusetts", 90),
    ("bergen co academies", "New Jersey", 90),
    ("bergen county academies", "New Jersey", 90),
    ("solon high school", "Ohio", 90),
    ("leland", "California", 85),
    ("mountain view high school", "California", 88),
    ("westminster schools", "Georgia", 90),
    ("ridge high school", "New Jersey", 88),
    ("desert vista high school", "Arizona", 90),
    ("choate", "Connecticut", 90),
    ("rosemary hall", "Connecticut", 90),
    ("xiaoyu education", "California", 80),
    ("harrow international school", "United Kingdom", 95),
    ("interlake high school", "Washington", 90),
    ("walter murray collegiate", "Saskatchewan, Canada", 90),
    ("dulles high school", "Texas", 90),
    ("detroit country day", "Michigan", 90),
    ("sierra canyon school", "California", 92),
    ("sierra canyon", "California", 90),
    ("henry m. gunn high school", "California", 92),
    ("gunn high school", "California", 90),
    ("university of texas at austin", "Texas", 95),
    ("ut austin", "Texas", 92),
    ("mclean high school", "Virginia", 92),
    ("mclean ", "Virginia", 90),
    ("westlake high school", "Texas", 90),
]

ACCURACY_THRESHOLD = 80


def _normalize_name(first: str, last: str) -> str:
    """Return 'First Last' with basic title-casing."""
    first = (first or "").strip()
    last = (last or "").strip()
    full = f"{first} {last}".strip()
    return " ".join(part[:1].upper() + part[1:].lower() for part in full.split() if part)


def _name_key(name: str) -> str:
    """Normalize for matching: lowercase, collapse spaces."""
    return " ".join((name or "").lower().split())


def _name_key_variants(name: str) -> list[str]:
    """Return key and variant (first + last word) for matching names with middle names."""
    parts = (name or "").lower().split()
    key = " ".join(parts)
    if len(parts) > 2:
        return [key, f"{parts[0]} {parts[-1]}"]
    return [key]


def infer_state_from_school(school: str) -> str | None:
    """Infer US state from school name. Returns None if no confident match."""
    if not (school or "").strip():
        return None
    n = school.strip().lower()
    best_state: str | None = None
    best_acc = 0
    for key, state, acc in SCHOOL_TO_STATE:
        if isinstance(key, re.Pattern):
            if key.search(n) and acc > best_acc:
                best_state = state
                best_acc = acc
        else:
            if key in n and acc > best_acc:
                best_state = state
                best_acc = acc
    if best_state and best_acc >= ACCURACY_THRESHOLD:
        return best_state
    return None


def parse_pdf_awardees() -> dict[str, str]:
    """Parse PDF and return normalized_name -> school_name mapping."""
    name_to_school: dict[str, str] = {}
    if not PDF_PATH.exists():
        print(f"PDF not found: {PDF_PATH}", file=sys.stderr)
        return name_to_school

    with pdfplumber.open(PDF_PATH) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if not table:
                continue
            for row in table:
                if not row or all(cell is None or str(cell).strip() == "" for cell in row):
                    continue
                if len(row) < 4:
                    continue
                last, first, school, award_raw = (r or "" for r in row[:4])
                if (last or "").strip().lower() == "last name":
                    continue
                if not first or not last:
                    continue
                full_name = _normalize_name(first, last)
                school_clean = " ".join((school or "").replace("\x00", " ").split()).strip()
                if school_clean:
                    name_to_school[_name_key(full_name)] = school_clean
                    name_to_school[_name_key(f"{last} {first}")] = school_clean

    return name_to_school


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    name_to_school = parse_pdf_awardees()
    print(f"Parsed {len(name_to_school)} name->school entries from PDF")

    rows: list[dict[str, str]] = []
    with AMO_2022_RESULTS.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        if "school" not in fieldnames:
            fieldnames.insert(fieldnames.index("state") + 1, "school")
        for row in reader:
            rows.append(dict(row))

    matched = 0
    state_filled = 0
    for row in rows:
        name = (row.get("student_name") or "").strip()
        school = None
        for key in _name_key_variants(name):
            if key in name_to_school:
                school = name_to_school[key]
                break

        if school:
            row["school"] = school
            matched += 1
        else:
            row["school"] = row.get("school", "")

        state = (row.get("state") or "").strip()
        if not state and school:
            inferred = infer_state_from_school(school)
            if inferred:
                row["state"] = inferred
                state_filled += 1

    print(f"Matched school for {matched} rows, inferred state for {state_filled} rows with missing state")

    if dry_run:
        print("\n[DRY RUN] Sample rows with school/state updates:")
        for row in rows[:25]:
            print(f"  {row.get('student_name')}: school={row.get('school', '')!r} state={row.get('state', '')!r}")
        return

    with AMO_2022_RESULTS.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Updated {AMO_2022_RESULTS}")


if __name__ == "__main__":
    main()
