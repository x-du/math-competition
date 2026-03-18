#!/usr/bin/env python3
"""
Add school names to JMO 2023 results from the USAJMO Awardees PDF.
When state is missing, use state from PDF or infer from school name.

Usage: python scripts/add_jmo_2023_school_and_state.py [--dry-run]
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parent.parent
JMO_2023_RESULTS = ROOT / "database" / "contests" / "jmo" / "year=2023" / "results.csv"
PDF_PATH = Path("/Users/xiaochendu/Dropbox/Xdu/Patrick/AMO/2023 USAJMO Awardees.pdf")

# School/team name (lowercase substring) -> (state, accuracy 0-100).
# Reuse and extend mapping from add_jmo_2022_school_and_state.py
SCHOOL_TO_STATE: list[tuple[str | re.Pattern, str, int]] = [
    ("millburn", "New Jersey", 92),
    ("ridge high school", "New Jersey", 88),
    ("phillips academy", "Massachusetts", 92),
    ("phillips exeter", "New Hampshire", 92),
    ("exeter academy", "New Hampshire", 92),
    ("thomas jefferson", "Virginia", 90),
    ("tjhsst", "Virginia", 92),
    ("lexington high school", "Massachusetts", 90),
    ("lexington ", "Massachusetts", 88),
    ("canyon crest academy", "California", 90),
    ("proof school", "California", 90),
    ("steam works", "New Jersey", 85),
    ("gunn high school", "California", 92),
    ("lakeside school", "Washington", 92),
    ("basis peoria", "Arizona", 90),
    ("beachwood high school", "Ohio", 90),
    ("florida atlantic university", "Florida", 95),
    ("florida atlantic", "Florida", 92),
    ("hotchkiss", "Connecticut", 92),
    ("hoover high school", "Alabama", 90),
    ("dougherty valley", "California", 90),
    ("science and arts academy", "Illinois", 88),
    ("stuyvesant", "New York", 92),
    ("harbour school", "State Department", 90),
    ("university of chicago lab", "Illinois", 92),
    ("uchicago lab", "Illinois", 90),
    ("cary chinese school", "North Carolina", 88),
    ("fulton science academy", "Georgia", 88),
    ("quarry lane", "California", 88),
    ("ut dallas", "Texas", 95),
    ("homestead high school", "California", 90),
    ("acton boxborough", "Massachusetts", 90),
    ("choate", "Connecticut", 90),
    ("rosemary hall", "Connecticut", 90),
    ("springlight education", "California", 85),
    ("arnold o beckman", "California", 90),
    ("beckman high school", "California", 90),
    ("alphastar academy", "California", 90),
    ("alpha star", "California", 88),
    ("phillips exeter", "New Hampshire", 92),
    ("st. mark's school of texas", "Texas", 92),
    ("st marks school of texas", "Texas", 92),
    ("clements high school", "Texas", 90),
    ("william p clements", "Texas", 90),
    ("elmbrook virtual", "Wisconsin", 90),
    ("elmbrook ", "Wisconsin", 88),
    ("brunswick school", "Connecticut", 88),
    ("university of north carolina", "North Carolina", 92),
    ("unc chapel hill", "North Carolina", 92),
    ("hunter college high school", "New York", 92),
    ("f w buchholz", "Florida", 90),
    ("buchholz", "Florida", 88),
    ("interlake high school", "Washington", 90),
    ("university high school", "Arizona", 85),
    ("pittsford sutherland", "New York", 90),
    ("hopkins school", "Connecticut", 90),
    ("cranbrook", "Michigan", 92),
    ("princeton international school", "New Jersey", 90),
    ("prisms", "New Jersey", 90),
    ("westbrook intermediate", "Texas", 85),
    ("saratoga high school", "California", 90),
    ("jesuit high school", "Oregon", 90),
    ("university of texas at austin", "Texas", 95),
    ("ut austin", "Texas", 92),
    ("cherry creek high school", "Colorado", 90),
    ("middlesex county academy", "New Jersey", 88),
    ("new jersey enrichment academy", "New Jersey", 88),
    ("arizona college prep", "Arizona", 90),
    ("icae", "Michigan", 80),
    ("carmel high school", "Indiana", 90),
    ("harvard-westlake", "California", 92),
    ("amador valley", "California", 90),
    ("santa margarita catholic", "California", 90),
    ("university of toronto", "Ontario, Canada", 95),
    ("mt lebanon high school", "Pennsylvania", 90),
    ("orange county math circle", "California", 88),
    ("mclean high school", "Virginia", 92),
    ("jonas clarke", "Massachusetts", 88),
    ("montgomery blair", "Maryland", 90),
    ("blair high school", "Maryland", 88),
    ("adlai e stevenson", "Illinois", 90),
    ("stevenson high school", "Illinois", 88),
    ("pingry", "New Jersey", 92),
    ("yu's elite education", "New Jersey", 85),
    ("yus elite", "New Jersey", 85),
    ("rsm ", "Massachusetts", 82),
    ("russian school of math", "Massachusetts", 85),
    ("newport high school", "Washington", 88),
    ("avenues", "New York", 85),
    ("rose l hardy", "District of Columbia", 88),
    ("branham high school", "California", 88),
    ("riverstone international", "Idaho", 90),
    ("bishop seabury academy", "Kansas", 90),
    ("spring branch academic", "Texas", 88),
    ("mission possible teens", "California", 85),
    ("syosset high school", "New York", 90),
    ("troy high school", "Michigan", 88),
    ("north allegheny", "Pennsylvania", 90),
    ("university of colorado", "Colorado", 95),
    ("colorado at boulder", "Colorado", 95),
    ("state college area high school", "Pennsylvania", 90),
    ("hamilton high school", "Arizona", 85),
    ("redwood middle school", "California", 85),
    ("collegiate school", "New York", 88),
    ("aops bellevue", "Washington", 85),
    ("basis independent fremont", "California", 88),
    ("rootofmath", "British Columbia, Canada", 90),
    ("rothesay netherwood", "New Brunswick, Canada", 90),
    ("panther creek", "North Carolina", 88),
    ("nds math", "California", 80),
    ("aragon high school", "California", 90),
    ("university laboratory high school", "Illinois", 90),
    ("uni high", "Illinois", 88),
    ("pullman high school", "Washington", 88),
    ("american heritage school", "Florida", 90),
    ("concord-carlisle", "Massachusetts", 90),
    ("olympiads school", "Ontario, Canada", 88),
    ("chantilly", "Virginia", 88),
    ("whitney m young", "Illinois", 90),
    ("bedford high school", "Massachusetts", 88),
    ("sartartia", "Texas", 88),
    ("timberline high school", "Idaho", 90),
    ("university of wisconsin", "Wisconsin", 92),
    ("wisconsin-milwaukee", "Wisconsin", 90),
    ("kean university", "New Jersey", 88),
    ("westford academy", "Massachusetts", 88),
    ("crescent valley", "Oregon", 88),
    ("longfellow middle school", "Virginia", 85),
    ("lower merion high school", "Pennsylvania", 90),
    ("maggie walker", "Virginia", 92),
    ("governor's school", "Virginia", 88),
    ("montgomery college", "Maryland", 88),
    ("jericho high school", "New York", 92),
    ("jericho ", "New York", 85),
    ("meadow glen middle school", "South Carolina", 88),
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
                if (name_cell or "").strip().lower() == "name":
                    continue
                if not (name_cell or "").strip():
                    continue
                last, first = _split_name(name_cell)
                if not last:
                    continue
                full_name = _normalize_name(first, last)
                key = _name_key(full_name)
                school_clean = " ".join((school or "").replace("\x00", " ").split()).strip()
                state_clean = (state_country or "").replace("\x00", " ").strip()
                if school_clean:
                    name_to_school[key] = school_clean
                if state_clean and state_clean.lower() not in ("award", "winner", "mention", "honorable", "top"):
                    name_to_state[key] = state_clean

    return name_to_school, name_to_state


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    name_to_school, name_to_state = parse_pdf_awardees()
    print(f"Parsed {len(name_to_school)} name->school, {len(name_to_state)} name->state from PDF")

    rows: list[dict[str, str]] = []
    with JMO_2023_RESULTS.open(newline="", encoding="utf-8") as f:
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
        key = _name_key(name)
        school = name_to_school.get(key)
        pdf_state = name_to_state.get(key)

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

    with JMO_2023_RESULTS.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Updated {JMO_2023_RESULTS}")


if __name__ == "__main__":
    main()
