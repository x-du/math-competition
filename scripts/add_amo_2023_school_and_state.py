#!/usr/bin/env python3
"""
Add school names to AMO 2023 results from the USAMO Awardees PDF.
When state is missing, use state from PDF or infer from school name.

Usage: python scripts/add_amo_2023_school_and_state.py [--dry-run]
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parent.parent
AMO_2023_RESULTS = ROOT / "database" / "contests" / "amo" / "year=2023" / "results.csv"
PDF_PATH = Path("/Users/xiaochendu/Dropbox/Xdu/Patrick/AMO/2023 USAMO Awardees.pdf")

# School/team name (lowercase substring) -> (state, accuracy 0-100).
# Reuse mapping from add_amo_2022 and add_jmo_2023
SCHOOL_TO_STATE: list[tuple[str | re.Pattern, str, int]] = [
    ("vancouver olympiad school", "British Columbia, Canada", 92),
    ("phillips exeter", "New Hampshire", 92),
    ("exeter academy", "New Hampshire", 92),
    ("brewster academy", "New Hampshire", 90),
    ("univ of chicago laboratory", "Illinois", 92),
    ("uchicago lab", "Illinois", 90),
    ("stuyvesant", "New York", 92),
    ("lexington high school", "Massachusetts", 90),
    ("torrey pines", "California", 90),
    ("lynbrook high school", "California", 90),
    ("princeton international school", "New Jersey", 90),
    ("nueva", "California", 90),
    ("saratoga high school", "California", 90),
    ("west-windsor plainsboro", "New Jersey", 90),
    ("west windsor plainsboro", "New Jersey", 90),
    ("hunter college high school", "New York", 92),
    ("basis independent silicon valley", "California", 90),
    ("thomas jefferson", "Virginia", 90),
    ("tjhsst", "Virginia", 92),
    ("florida atlantic university", "Florida", 95),
    ("florida atlantic", "Florida", 92),
    ("montgomery blair", "Maryland", 90),
    ("phillips academy", "Massachusetts", 92),
    ("cherry creek high school", "Colorado", 90),
    ("adlai e stevenson", "Illinois", 90),
    ("dougherty valley", "California", 90),
    ("proof school", "California", 90),
    ("alphastar academy", "California", 90),
    ("davidson academy", "Nevada", 90),
    ("acton-boxborough", "Massachusetts", 90),
    ("acton boxborough", "Massachusetts", 90),
    ("ridge high school", "New Jersey", 88),
    ("choate", "Connecticut", 90),
    ("rosemary hall", "Connecticut", 90),
    ("interlake high school", "Washington", 90),
    ("gunn high school", "California", 90),
    ("university of texas at austin", "Texas", 95),
    ("ut austin", "Texas", 92),
    ("mclean high school", "Virginia", 92),
    ("westlake high school", "Texas", 90),
    ("millburn", "New Jersey", 92),
    ("canyon crest academy", "California", 90),
    ("lakeside school", "Washington", 92),
    ("st. mark's school of texas", "Texas", 92),
    ("st marks school of texas", "Texas", 92),
    ("clements high school", "Texas", 90),
    ("william p clements", "Texas", 90),
    ("cranbrook", "Michigan", 92),
    ("pingry", "New Jersey", 92),
    ("montgomery college", "Maryland", 88),
    ("jericho high school", "New York", 92),
    ("lower merion high school", "Pennsylvania", 90),
    ("maggie walker", "Virginia", 92),
    ("governor's school", "Virginia", 88),
    ("university of toronto", "Ontario, Canada", 95),
    ("rootofmath", "British Columbia, Canada", 90),
]

ACCURACY_THRESHOLD = 80


def _split_name(name_cell: str) -> tuple[str, str]:
    """Parse 'Last, First' format."""
    raw = (name_cell or "").strip()
    if "," in raw:
        last, first = raw.split(",", 1)
        return last.strip(), first.strip()
    parts = raw.split()
    if len(parts) <= 1:
        return raw, ""
    return parts[-1], " ".join(parts[:-1])


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


def parse_pdf_awardees() -> tuple[dict[str, str], dict[str, str]]:
    """Parse PDF and return (name_to_school, name_to_state). 2023 has Name, School, State/Country, Award."""
    name_to_school: dict[str, str] = {}
    name_to_state: dict[str, str] = {}
    if not PDF_PATH.exists():
        print(f"PDF not found: {PDF_PATH}", file=sys.stderr)
        return name_to_school, name_to_state

    pending_last: str | None = None
    pending_school: str | None = None
    pending_state: str | None = None

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
                name_cell, school, state_country, award_raw = (r or "" for r in row[:4])
                name_str = (name_cell or "").strip()
                school_clean = " ".join((school or "").replace("\x00", " ").split()).strip()
                state_clean = (state_country or "").replace("\x00", " ").strip()
                if state_clean and state_clean.lower() in ("award", "winner", "mention", "honorable", "top"):
                    state_clean = ""

                if (name_str or "").lower() == "name":
                    pending_last = pending_school = pending_state = None
                    continue

                if name_str.endswith(","):
                    pending_last = name_str.rstrip(",").strip()
                    if school_clean:
                        pending_school = school_clean
                        pending_state = state_clean or None
                    continue

                if not name_str:
                    if school_clean:
                        pending_school = school_clean
                        pending_state = state_clean or None
                    continue

                last, first = _split_name(name_str)
                if not last and not first:
                    continue

                if pending_last and not first:
                    first = name_str
                    last = pending_last
                full_name = _normalize_name(first, last)
                key = _name_key(full_name)

                use_school = school_clean or pending_school
                use_state = state_clean or pending_state

                if use_school:
                    name_to_school[key] = use_school
                if use_state:
                    name_to_state[key] = use_state

                pending_last = pending_school = pending_state = None

    return name_to_school, name_to_state


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    name_to_school, name_to_state = parse_pdf_awardees()
    print(f"Parsed {len(name_to_school)} name->school, {len(name_to_state)} name->state from PDF")

    rows: list[dict[str, str]] = []
    with AMO_2023_RESULTS.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        if "school" not in fieldnames:
            fieldnames.insert(fieldnames.index("state") + 1, "school")
        for row in reader:
            rows.append(dict(row))

    matched_school = 0
    state_filled = 0
    for row in rows:
        name = (row.get("student_name") or "").strip()
        school = None
        pdf_state = None
        for key in _name_key_variants(name):
            if key in name_to_school:
                school = name_to_school[key]
                break
        for key in _name_key_variants(name):
            if key in name_to_state:
                pdf_state = name_to_state[key]
                break

        if school:
            row["school"] = school
            matched_school += 1
        else:
            row["school"] = row.get("school", "")

        state = (row.get("state") or "").strip()
        if not state:
            if pdf_state:
                row["state"] = pdf_state
                state_filled += 1
            elif school:
                inferred = infer_state_from_school(school)
                if inferred:
                    row["state"] = inferred
                    state_filled += 1

    print(f"Matched school for {matched_school} rows, filled state for {state_filled} rows with missing state")

    if dry_run:
        print("\n[DRY RUN] Sample rows with school/state updates:")
        for row in rows[:25]:
            print(f"  {row.get('student_name')}: school={row.get('school', '')!r} state={row.get('state', '')!r}")
        return

    with AMO_2023_RESULTS.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Updated {AMO_2023_RESULTS}")


if __name__ == "__main__":
    main()
