#!/usr/bin/env python3
"""
Add school names to JMO 2024 results from the USAJMO Awardees PDF.
When state is missing, use state from PDF or infer from school name.

Usage: python scripts/add_jmo_2024_school_and_state.py [--dry-run]
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parent.parent
JMO_2024_RESULTS = ROOT / "database" / "contests" / "jmo" / "year=2024" / "results.csv"
PDF_PATH = Path("/Users/xiaochendu/Dropbox/Xdu/Patrick/AMO/2024-USAJMO-Awardees-updated.pdf")

# School/team name (lowercase substring) -> (state, accuracy 0-100).
SCHOOL_TO_STATE: list[tuple[str | re.Pattern, str, int]] = [
    ("cary chinese school", "North Carolina", 88),
    ("art of problem solving", "North Carolina", 85),
    ("aops", "North Carolina", 80),
    ("american heritage school", "Florida", 90),
    ("brunswick school", "Connecticut", 88),
    ("phillips exeter", "New Hampshire", 92),
    ("interlake high school", "Washington", 90),
    ("cranbrook kingswood", "Michigan", 92),
    ("cranbrook", "Michigan", 90),
    ("princeton international school", "New Jersey", 90),
    ("round rock high school", "Texas", 90),
    ("northview high school", "Georgia", 88),
    ("university of colorado boulder", "Colorado", 95),
    ("lexington high school", "Massachusetts", 90),
    ("lynbrook high school", "California", 90),
    ("centennial high school", "Maryland", 88),
    ("carmel high school", "Indiana", 90),
    ("university of chicago lab", "Illinois", 92),
    ("uchicago lab", "Illinois", 90),
    ("lakeside school", "Washington", 92),
    ("yu's elite education", "New Jersey", 85),
    ("yus elite", "New Jersey", 85),
    ("tt math school", "Ontario, Canada", 88),
    ("thomas jefferson", "Virginia", 90),
    ("tjhsst", "Virginia", 92),
    ("proof school", "California", 90),
    ("bellevue high school", "Washington", 88),
    ("newport high school", "Washington", 88),
    ("adlai e stevenson", "Illinois", 90),
    ("stevenson high school", "Illinois", 88),
    ("branham high school", "California", 88),
    ("stuyvesant", "New York", 92),
    ("oakton college", "Illinois", 85),
    ("jonas clarke", "Massachusetts", 88),
    ("state college area high school", "Pennsylvania", 90),
    ("spring branch academic", "Texas", 88),
    ("burlingame high school", "California", 88),
    ("alpha stem", "Virginia", 85),
    ("st. marks school of texas", "Texas", 92),
    ("st marks school of texas", "Texas", 92),
    ("basis independent fremont", "California", 88),
    ("valley christian high school", "California", 88),
    ("elkins", "Texas", 85),
    ("bergen co academies", "New Jersey", 90),
    ("bergen county academies", "New Jersey", 90),
    ("iolani school", "Hawaii", 92),
    ("alphastar academy", "California", 90),
    ("alpha star", "California", 88),
    ("william p clements", "Texas", 90),
    ("clements high school", "Texas", 90),
    ("amador valley", "California", 90),
    ("university of texas at austin", "Texas", 95),
    ("ut austin", "Texas", 92),
    ("dougherty valley", "California", 90),
    ("iowa city west", "Iowa", 92),
    ("sartartia middle school", "Texas", 88),
    ("mclean hs", "Virginia", 92),
    ("mclean high school", "Virginia", 90),
    ("south pasadena", "California", 85),
    ("basis mesa", "Arizona", 88),
    ("aamoc", "Michigan", 80),
    ("jesuit high school", "Oregon", 90),
    ("homestead high school", "California", 90),
    ("aj tutoring", "California", 80),
    ("san diego math circle", "California", 88),
    ("mathemagics club", "California", 80),
    ("vancouver olympiad school", "British Columbia, Canada", 90),
    ("think academy", "Washington", 85),
    ("innovation academy", "Georgia", 85),
    ("westminster schools", "Georgia", 90),
    ("florida atlantic university", "Florida", 95),
    ("florida atlantic", "Florida", 92),
    ("rsm-acton", "Massachusetts", 85),
    ("rsm acton", "Massachusetts", 85),
    ("montgomery blair", "Maryland", 90),
    ("blair high school", "Maryland", 88),
    ("east ridge high school", "Minnesota", 88),
    ("avenues", "New York", 85),
    ("trinity school", "New York", 88),
    ("pine view", "Florida", 90),
    ("renaissance high school", "Idaho", 85),
    ("ut dallas", "Texas", 95),
    ("niskayuna high school", "New York", 88),
    ("aops academy bellevue", "Washington", 85),
    ("harker upper school", "California", 92),
    ("harker", "California", 90),
    ("north allegheny", "Pennsylvania", 90),
    ("university of colorado", "Colorado", 95),
    ("cupertino high school", "California", 88),
    ("university laboratory high school", "Illinois", 90),
    ("uni high", "Illinois", 88),
    ("sharon high school", "Massachusetts", 88),
    ("princeton high school", "New Jersey", 88),
    ("think academy cupertino", "California", 85),
    ("olympiads school", "Ontario, Canada", 88),
    ("random math", "California", 85),
    ("university of california davis", "California", 92),
    ("uc davis", "California", 92),
    ("mirman school", "California", 88),
    ("twin falls high school", "Idaho", 90),
    ("liberal arts and science academy", "Texas", 92),
    ("lasa", "Texas", 90),
    ("henry gunn high", "California", 92),
    ("gunn high school", "California", 90),
    ("phillips academy andover", "Massachusetts", 92),
    ("phillips academy", "Massachusetts", 92),
    ("longfellow middle school", "Virginia", 85),
    ("skyline high school", "Washington", 88),
    ("deerfield academy", "Massachusetts", 90),
    ("poolesville hs", "Maryland", 88),
    ("great neck south", "New York", 88),
    ("springlight education", "California", 85),
    ("maggie walker", "Virginia", 92),
    ("governor's school", "Virginia", 88),
    ("hinsdale central", "Illinois", 90),
    ("westbrook intermediate", "Texas", 85),
    ("basis scottsdale", "Arizona", 88),
]

ACCURACY_THRESHOLD = 80


def _un_camel(s: str) -> str:
    """Insert spaces: CaryChineseSchool -> Cary Chinese School, SchoolofMath -> School of Math."""
    if not s:
        return s
    # Avoid splitting "Proof" -> "Pro of": only split "of"/"and" when preceded by non-o
    s = re.sub(r"([b-np-z])(of)([A-Z])", r"\1 \2 \3", s, flags=re.I)
    s = re.sub(r"([a-z])(and)([A-Z])", r"\1 \2 \3", s, flags=re.I)
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", s)
    s = s.replace("TTMath", "TT Math")
    return s


def _split_name(name_cell: str) -> tuple[str, str]:
    """Parse 'Last, First' format (may have no space after comma in 2024 PDF)."""
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
    """Infer US state from school name."""
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
    """Parse 2024 PDF. Format: Name, School, State/Country, Award (camelCase, no spaces)."""
    name_to_school: dict[str, str] = {}
    name_to_state: dict[str, str] = {}
    if not PDF_PATH.exists():
        print(f"PDF not found: {PDF_PATH}", file=sys.stderr)
        return name_to_school, name_to_state

    skip_headers = ("name", "school", "state", "country", "award")

    with pdfplumber.open(PDF_PATH) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if not table:
                continue
            for row in table:
                if not row or len(row) < 4:
                    continue
                name_cell, school, state_country, award_raw = (r or "" for r in row[:4])
                name_text = (name_cell or "").strip()
                school_text = (school or "").replace("\x00", " ").replace("\n", " ").strip()
                state_text = (state_country or "").replace("\x00", " ").strip()

                if not name_text or name_text.lower() in skip_headers:
                    continue

                last_name, first_name = _split_name(name_text)
                if not last_name:
                    continue

                full_name = _normalize_name(first_name, last_name)
                key = _name_key(full_name)
                school_clean = " ".join(_un_camel(school_text).split())
                state_clean = " ".join(_un_camel(state_text).split())

                if school_clean:
                    name_to_school[key] = school_clean
                if state_clean and state_clean.lower() not in skip_headers + ("winner", "mention", "honorable", "top", "honors"):
                    name_to_state[key] = state_clean

    return name_to_school, name_to_state


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    name_to_school, name_to_state = parse_pdf_awardees()
    print(f"Parsed {len(name_to_school)} name->school, {len(name_to_state)} name->state from PDF")

    rows: list[dict[str, str]] = []
    with JMO_2024_RESULTS.open(newline="", encoding="utf-8") as f:
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
            if key in name_to_state:
                pdf_state = name_to_state[key]

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
        for row in rows[:35]:
            print(f"  {row.get('student_name')}: school={row.get('school', '')!r} state={row.get('state', '')!r}")
        return

    with JMO_2024_RESULTS.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Updated {JMO_2024_RESULTS}")


if __name__ == "__main__":
    main()
