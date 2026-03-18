#!/usr/bin/env python3
"""
Add school names to JMO 2022 results from the USAJMO Awardees PDF.
When state is missing, infer it from the school name.

Usage: python scripts/add_jmo_2022_school_and_state.py [--dry-run]
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parent.parent
JMO_2022_RESULTS = ROOT / "database" / "contests" / "jmo" / "year=2022" / "results.csv"
PDF_PATH = Path("/Users/xiaochendu/Dropbox/Xdu/Patrick/AMO/2022 USAJMO Awardees.pdf")

# School/team name (lowercase substring) -> (state, accuracy 0-100).
# Extended mapping for 2022 USAJMO schools from the PDF.
SCHOOL_TO_STATE: list[tuple[str | re.Pattern, str, int]] = [
    # From fill_state_from_school_team_web.py (reused)
    ("millburn", "New Jersey", 92),
    ("ridge high school", "New Jersey", 88),
    ("ridge ", "New Jersey", 85),
    ("phillips academy", "Massachusetts", 92),
    ("phillips exeter", "New Hampshire", 92),
    ("exeter academy", "New Hampshire", 92),
    ("thomas jefferson", "Virginia", 90),
    ("tjhsst", "Virginia", 92),
    ("lexington high school", "Massachusetts", 90),
    ("lexington ", "Massachusetts", 88),
    ("cambridge rindge", "Massachusetts", 90),
    ("rindge and latin", "Massachusetts", 90),
    ("stanford online", "California", 90),
    ("davidson academy", "Nevada", 90),
    ("gunn high school", "California", 92),
    ("gunn ", "California", 90),
    ("lakeside school", "Washington", 92),
    ("lakeside ", "Washington", 90),
    ("west-windsor", "New Jersey", 90),
    ("west windsor", "New Jersey", 90),
    ("plainsboro", "New Jersey", 90),
    ("ww-p", "New Jersey", 88),
    ("wwp ", "New Jersey", 88),
    ("pingry", "New Jersey", 92),
    ("hotchkiss", "Connecticut", 92),
    ("hopkins school", "Connecticut", 90),
    ("choate", "Connecticut", 90),
    ("rosemary hall", "Connecticut", 90),
    ("edina high school", "Minnesota", 92),
    ("edina ", "Minnesota", 90),
    ("dougherty valley", "California", 90),
    ("lynbrook high school", "California", 90),
    ("lynbrook", "California", 88),
    ("saratoga high school", "California", 90),
    ("saratoga ", "California", 88),
    ("homestead high school", "California", 90),
    ("homestead ", "California", 88),
    ("torrey pines", "California", 90),
    ("basis independent silicon valley", "California", 90),
    ("basis silicon valley", "California", 90),
    ("basis peoria", "Arizona", 90),
    ("arizona college prep", "Arizona", 90),
    ("st. mark's school of texas", "Texas", 92),
    ("st mark's school of texas", "Texas", 92),
    ("st marks school of texas", "Texas", 92),
    ("clements high school", "Texas", 90),
    ("william p clements", "Texas", 90),
    ("university of texas at austin", "Texas", 95),
    ("ut austin", "Texas", 92),
    ("fort settlement", "Texas", 90),
    ("carnegie vanguard", "Texas", 92),
    ("carnegie vanguard hs", "Texas", 92),
    ("highland park high school", "Texas", 88),  # TX or IL - TX more common for math
    ("lebanon trail", "Texas", 90),
    ("coppell high school", "Texas", 90),
    ("bellaire high school", "Texas", 90),
    ("jasper high", "Texas", 90),
    ("jericho high school", "New York", 92),
    ("jericho ", "New York", 85),
    ("pace academy", "Georgia", 90),
    ("meadow glen middle school", "South Carolina", 88),
    ("university of colorado", "Colorado", 95),
    ("colorado at boulder", "Colorado", 95),
    ("detroit country day", "Michigan", 90),
    ("russian school of math", "Massachusetts", 85),
    ("russian school of mathematics", "Massachusetts", 85),
    ("rsm ", "Massachusetts", 82),
    ("random math", "California", 85),
    ("cary chinese school", "North Carolina", 88),
    ("cary ", "North Carolina", 85),
    ("cornell university", "New York", 95),
    ("california baptist university", "California", 90),
    ("riverstone international", "Idaho", 90),
    ("waterford school", "Utah", 90),
    ("winchester thurston", "Pennsylvania", 90),
    ("winchester high school", "Massachusetts", 88),
    ("robert louis stevenson", "California", 88),
    ("eastside education", "Washington", 85),
    ("university of toronto", "Ontario, Canada", 95),
    ("university of california, irvine", "California", 95),
    ("uc irvine", "California", 92),
    ("westview high school", "California", 88),
    ("mountain view high school", "California", 88),
    ("interlake high school", "Washington", 90),
    ("arnold o beckman", "California", 90),
    ("beckman high school", "California", 90),
    ("jackson hs", "Ohio", 85),
    ("yu's elite education", "New Jersey", 85),
    ("yus elite", "New Jersey", 85),
    ("evergreen valley", "California", 88),
    ("palo alto high school", "California", 90),
    ("hong kong international", "State Department", 95),
    ("chadwick international", "State Department", 95),  # South Korea
    ("fuss", "California", 80),
    ("univ of chicago laboratory", "Illinois", 92),
    ("uchicago lab", "Illinois", 90),
    ("olga radko math circle", "California", 88),
    ("ucla", "California", 90),
    ("think academy", "California", 85),
    ("alphastar academy", "California", 90),
    ("alpha star", "California", 88),
    ("east lyme high school", "Connecticut", 90),
    ("mclean high school", "Virginia", 92),
    ("mclean ", "Virginia", 90),
    ("florida atlantic university", "Florida", 95),
    ("florida atlantic", "Florida", 92),
    ("montgomery blair", "Maryland", 90),
    ("blair high school", "Maryland", 88),
    ("hunter college high school", "New York", 92),
    ("syosset high school", "New York", 90),
    ("oakton community college", "Illinois", 88),
    ("elmbrook virtual", "Wisconsin", 90),
    ("elmbrook ", "Wisconsin", 88),
    ("gauss academy", "North Carolina", 85),
    ("iowa city west", "Iowa", 92),
    ("harriton", "Pennsylvania", 90),
    ("lower merion", "Pennsylvania", 88),
    ("paul laurence dunbar", "Kentucky", 90),
    ("dunbar high school", "Kentucky", 88),
    ("westminster schools", "Georgia", 90),
    ("springlight education", "California", 85),
    ("eo smith", "Connecticut", 88),
    ("granite ridge", "California", 85),
    ("clovis", "California", 85),
    ("university laboratory high school", "Illinois", 90),
    ("uni high", "Illinois", 88),
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
                    # Also store with "Last First" in case PDF has different order
                    name_to_school[_name_key(f"{last} {first}")] = school_clean

    return name_to_school


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    name_to_school = parse_pdf_awardees()
    print(f"Parsed {len(name_to_school)} name->school entries from PDF")

    rows: list[dict[str, str]] = []
    with JMO_2022_RESULTS.open(newline="", encoding="utf-8") as f:
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
        key = _name_key(name)
        school = name_to_school.get(key)
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
        for row in rows[:20]:
            print(f"  {row.get('student_name')}: school={row.get('school', '')!r} state={row.get('state', '')!r}")
        return

    with JMO_2022_RESULTS.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Updated {JMO_2022_RESULTS}")


if __name__ == "__main__":
    main()
