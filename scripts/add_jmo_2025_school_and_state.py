#!/usr/bin/env python3
"""
Add school names to JMO 2025 results from the USAJMO Awardees PDF.
When state is missing, use state from PDF or infer from school name.

Usage: python scripts/add_jmo_2025_school_and_state.py [--dry-run]
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parent.parent
JMO_2025_RESULTS = ROOT / "database" / "contests" / "jmo" / "year=2025" / "results.csv"
PDF_PATH = Path("/Users/xiaochendu/Dropbox/Xdu/Patrick/AMO/2025-USAJMO-Awardees-List.pdf")

# School/team name (lowercase substring) -> (state, accuracy 0-100).
SCHOOL_TO_STATE: list[tuple[str | re.Pattern, str, int]] = [
    ("prepedu", "Massachusetts", 85),
    ("proof school", "California", 90),
    ("harker", "California", 92),
    ("telra institute", "North Carolina", 85),
    ("university of texas at dallas", "Texas", 95),
    ("ut dallas", "Texas", 95),
    ("tt math school", "Ontario, Canada", 88),
    ("st. mark's school of texas", "Texas", 92),
    ("st marks school of texas", "Texas", 92),
    ("rutgers", "New Jersey", 92),
    ("minnetonka high school", "Minnesota", 90),
    ("san diego math circle", "California", 88),
    ("myers park high school", "North Carolina", 90),
    ("bergen county academies", "New Jersey", 90),
    ("bergen co academies", "New Jersey", 90),
    ("aces learning center", "Texas", 85),
    ("ivymax", "California", 88),
    ("fremont learning", "California", 88),
    ("jericho high school", "New York", 92),
    ("jericho ", "New York", 85),
    ("springlight education", "California", 85),
    ("lakeside school", "Washington", 92),
    ("lakeside ", "Washington", 90),
    ("alphastar academy", "California", 90),
    ("alpha star", "California", 88),
    ("yu's elite education", "New Jersey", 85),
    ("yus elite", "New Jersey", 85),
    ("lexington high school", "Massachusetts", 90),
    ("lexington ", "Massachusetts", 88),
    ("eastside preparatory", "Washington", 88),
    ("thomas jefferson", "Virginia", 90),
    ("tjhsst", "Virginia", 92),
    ("paul laurence dunbar", "Kentucky", 90),
    ("dunbar high school", "Kentucky", 88),
    ("pine view", "Florida", 90),
    ("renaissance high school", "Idaho", 85),
    ("walnut hills high school", "Ohio", 90),
    ("aops bellevue", "Washington", 85),
    ("think academy", "California", 85),
    ("seven lakes high school", "Texas", 90),
    ("saratoga high school", "California", 90),
    ("saratoga ", "California", 88),
    ("northfield mount hermon", "Massachusetts", 90),
    ("university of california, davis", "California", 92),
    ("uc davis", "California", 92),
    ("pittsford mendon", "New York", 90),
    ("geffen academy", "California", 90),
    ("ucla", "California", 90),
    ("william p clements", "Texas", 90),
    ("clements high school", "Texas", 90),
    ("brown university", "Rhode Island", 95),
    ("middleton high school", "Wisconsin", 90),
    ("stamford polytechnic", "New Mexico", 88),
    ("cary academy", "North Carolina", 90),
    ("carleton university", "Ontario, Canada", 90),
    ("montgomery blair", "Maryland", 90),
    ("blair high school", "Maryland", 88),
    ("west point grey academy", "British Columbia, Canada", 90),
    ("waterford school", "Utah", 90),
    ("eastern technical high school", "Maryland", 88),
    ("henry gunn high", "California", 92),
    ("gunn high school", "California", 92),
    ("dos pueblos high", "California", 88),
    ("mounds view high school", "Minnesota", 90),
    ("st. marks school of texas", "Texas", 92),
    ("think academy", "New York", 85),
    ("carmel high school", "Indiana", 90),
    ("jordan high school", "Texas", 85),
    ("illinois mathematics and science academy", "Illinois", 92),
    ("imsa", "Illinois", 90),
    ("central high school", "Missouri", 85),
    ("springfield", "Missouri", 85),
    ("innovation academy", "Georgia", 85),
    ("alpharetta", "Georgia", 85),
    ("kean university", "New Jersey", 88),
    ("jesuit high school", "Oregon", 90),
    ("portland", "Oregon", 85),
    ("oakville trafalgar", "Ontario, Canada", 88),
    ("basis tucson", "Arizona", 90),
    ("random math", "California", 85),
    ("gauss academy", "New Jersey", 85),
    ("monta vista high school", "California", 90),
    ("hunter college high school", "New York", 92),
    ("mountain view high school", "California", 88),
    ("lake norman charter", "North Carolina", 88),
    ("los gatos high school", "California", 90),
    ("cherry creek high school", "Colorado", 90),
    ("greenhills school", "Michigan", 88),
    ("interlake high school", "Washington", 90),
    ("jonas clarke", "Massachusetts", 88),
    ("stuyvesant", "New York", 92),
    ("sharon high school", "Massachusetts", 88),
    ("stoney creek high school", "Michigan", 88),
    ("west windsor plainsboro", "New Jersey", 90),
    ("ww-p", "New Jersey", 88),
    ("great valley high school", "Pennsylvania", 90),
    ("james s. rickards", "Massachusetts", 85),
    ("riverside elementary", "Connecticut", 85),
    ("hammond school", "South Carolina", 88),
    ("sage hill school", "California", 88),
    ("linkedkey", "Ontario, Canada", 85),
    ("waterford high school", "Connecticut", 88),
    ("university of texas at dallas", "Texas", 95),
    ("amador valley", "California", 90),
    ("university prep", "Washington", 88),
    ("archmere academy", "Delaware", 90),
    ("centennial high school", "Maryland", 88),
    ("ellicott city", "Maryland", 85),
    ("great neck north", "New York", 88),
    ("james madison memorial", "Wisconsin", 90),
    ("palos verdes high school", "California", 90),
    ("lynbrook high school", "California", 90),
    ("lynbrook", "California", 88),
    ("parkland high school", "Pennsylvania", 90),
    ("uci math circle", "California", 88),
    ("harker school", "California", 92),
    ("amarillo high school", "Texas", 90),
    ("pingry", "New Jersey", 92),
    ("oakton community college", "Illinois", 88),
    ("american heritage school", "Florida", 90),
    ("plantation", "Florida", 85),
    ("belmont high school", "Massachusetts", 88),
    ("san marino high school", "California", 88),
    ("maxfield academy", "Ontario, Canada", 85),
    ("emory university", "Georgia", 92),
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
    """Parse PDF and return (name_to_school, name_to_state). 2025 has Name, School, State/Country, Award."""
    name_to_school: dict[str, str] = {}
    name_to_state: dict[str, str] = {}
    if not PDF_PATH.exists():
        print(f"PDF not found: {PDF_PATH}", file=sys.stderr)
        return name_to_school, name_to_state

    skip_headers = ("name", "school", "state", "country", "award")
    last_school = ""
    last_state = ""
    pending: tuple[str, str, str] | None = None  # (key, school, state)

    def emit_pending() -> None:
        nonlocal pending
        if pending:
            k, sc, st = pending
            if sc:
                name_to_school[k] = sc
            if st and st.lower() not in ("winner", "mention", "honorable", "top", "honors"):
                name_to_state[k] = st
            pending = None

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
                school_text = " ".join((school or "").replace("\x00", " ").split()).strip()
                state_text = (state_country or "").replace("\x00", " ").strip()

                if name_text and name_text.lower() not in skip_headers:
                    last_name, first_name = _split_name(name_text)
                    if last_name:
                        full_name = _normalize_name(first_name, last_name)
                        key = _name_key(full_name)
                        school_clean = " ".join((last_school + " " + school_text).split()).strip() if (last_school or school_text) else ""
                        state_clean = state_text or last_state
                        emit_pending()
                        pending = (key, school_clean, state_clean)
                    last_school = ""
                    last_state = ""
                elif not name_text and school_text:
                    # School with no name - could be continuation of pending or next person's school
                    if pending:
                        # Check if this looks like continuation (fragment) or new school
                        # Fragments often lack "School", "Academy" at end, or are short
                        pk, ps, pst = pending
                        if ps and (len(school_text.split()) <= 3 or " and " in school_text or " for " in school_text):
                            # Likely continuation (e.g. "for Science and Technology")
                            ps = " ".join((ps + " " + school_text).split()).strip()
                            pending = (pk, ps, pst)
                        else:
                            # New person's school - emit and start fresh
                            emit_pending()
                            last_school = school_text
                    else:
                        last_school = " ".join((last_school + " " + school_text).split()) if last_school else school_text
                elif pending and state_text and state_text.lower() not in skip_headers:
                    pk, ps, pst = pending
                    pending = (pk, ps, state_text)
                if state_text and state_text.lower() not in skip_headers:
                    last_state = state_text
                elif not name_text and not school_text and not state_text:
                    # Empty row - emit pending, next row may start new person's school
                    emit_pending()

    emit_pending()
    return name_to_school, name_to_state


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    name_to_school, name_to_state = parse_pdf_awardees()
    print(f"Parsed {len(name_to_school)} name->school, {len(name_to_state)} name->state from PDF")

    rows: list[dict[str, str]] = []
    with JMO_2025_RESULTS.open(newline="", encoding="utf-8") as f:
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
            if school and pdf_state:
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
        for row in rows[:30]:
            print(f"  {row.get('student_name')}: school={row.get('school', '')!r} state={row.get('state', '')!r}")
        return

    with JMO_2025_RESULTS.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Updated {JMO_2025_RESULTS}")


if __name__ == "__main__":
    main()
