#!/usr/bin/env python3
"""
Fill missing state for students using Math Kangaroo USA winners.
https://mathkangaroo.org/mks/national-and-state-winners/

Downloads PDFs for 2024 (Grade), 2023 (state), 2022 (state), 2021 (Level), parses
(name, grade, state), matches missing-state students by name and grade.

2021 uses Level instead of Grade: uploads/2021/08/2021_Level-N_National-Winners.pdf
2020 uses Level, archived in 2022/04: uploads/2022/04/2020_Level-N_National-Winners.pdf

Usage: python scripts/fill_state_from_math_kangaroo.py [--dry-run]
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
INCOMPLETE_JSON = ROOT / "incomplete_students.json"

# 2-letter state code -> full name (US + DC, territories)
STATE_ABBREV_TO_FULL: Dict[str, str] = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut",
    "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida",
    "GA": "Georgia", "GU": "Guam", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
    "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
    "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
    "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}

MK_BASE = "https://mathkangaroo.org/mks/wp-content/uploads"
# States to try for state-winners PDFs (2022, 2023)
STATE_CODES = [c for c in STATE_ABBREV_TO_FULL if c not in ("GU",)]


def _normalize_name(name: str) -> str:
    """Lowercase, collapse spaces, strip."""
    return " ".join((name or "").lower().split())


def _name_key_variants(name: str) -> List[str]:
    """Return key and variant (first + last word) for matching names with middle names."""
    parts = (name or "").lower().split()
    key = " ".join(parts)
    if len(parts) > 2:
        return [key, f"{parts[0]} {parts[-1]}"]
    return [key]


def parse_national_winners(text: str, year: int, grade: int) -> List[Tuple[str, int, str]]:
    """
    Parse 2024 national grade PDFs. Format: YEAR GRADE NAME SCORE RANK CENTER STATE.
    """
    results: List[Tuple[str, int, str]] = []
    valid_states = set(STATE_ABBREV_TO_FULL.keys())
    year_str = str(year)

    parts = re.split(r"\n(?=" + year_str + r"\s+\d+)", text)
    for part in parts:
        part = part.strip()
        if not part or not part.startswith(year_str):
            continue
        rest = " ".join(part.split("\n"))
        tokens = rest.split()
        if len(tokens) < 6:
            continue
        state_idx = -1
        for i in range(len(tokens) - 1, 1, -1):
            if len(tokens[i]) == 2 and tokens[i].upper() in valid_states:
                state_idx = i
                break
        if state_idx < 0:
            continue
        state_full = STATE_ABBREV_TO_FULL.get(tokens[state_idx].upper(), tokens[state_idx])
        score_idx = -1
        for j in range(state_idx - 1, 1, -1):
            try:
                int(tokens[j])
                int(tokens[j - 1])
                score_idx = j - 1
                break
            except (ValueError, IndexError):
                continue
        if score_idx < 2:
            continue
        name = " ".join(tokens[2:score_idx])
        if name:
            g = int(tokens[1]) if tokens[1].isdigit() else grade
            results.append((_normalize_name(name), g, state_full))

    return results


def parse_state_winners(text: str, year: int, state_abbrev: str) -> List[Tuple[str, int, str]]:
    """
    Parse state-winners PDFs (2022, 2023). Format: YEAR GRADE NAME STATE_RANK STATE CENTER...
    """
    results: List[Tuple[str, int, str]] = []
    valid_states = set(STATE_ABBREV_TO_FULL.keys())
    year_str = str(year)
    state_full = STATE_ABBREV_TO_FULL.get(state_abbrev.upper(), state_abbrev)

    parts = re.split(r"\n(?=" + year_str + r"\s+\d+)", text)
    for part in parts:
        part = part.strip()
        if not part or not part.startswith(year_str):
            continue
        rest = " ".join(part.split("\n"))
        tokens = rest.split()
        if len(tokens) < 6:
            continue
        state_idx = -1
        for i in range(len(tokens) - 1, 1, -1):
            if len(tokens[i]) == 2 and tokens[i].upper() in valid_states:
                state_idx = i
                break
        if state_idx < 0:
            continue
        rank_idx = state_idx - 1
        try:
            int(tokens[rank_idx])
        except (ValueError, IndexError):
            continue
        name = " ".join(tokens[2:rank_idx])
        if name:
            g = int(tokens[1]) if tokens[1].isdigit() else 0
            if 1 <= g <= 12:
                results.append((_normalize_name(name), g, state_full))

    return results


def fetch_mk_pdf_text(url: str) -> str:
    """Download PDF from URL and extract text."""
    try:
        import pdfplumber
        from io import BytesIO
        with urlopen(url, timeout=30) as resp:
            data = resp.read()
        with pdfplumber.open(BytesIO(data)) as pdf:
            text_parts = []
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
            return "\n".join(text_parts)
    except Exception as e:
        print(f"Could not fetch {url}: {e}", file=sys.stderr)
        return ""


def fetch_national_grade(year: int, grade: int) -> str:
    """Download 2024 national grade PDF."""
    url = f"{MK_BASE}/{year}/05/{year}_Grade-{grade}_National-Winners.pdf"
    return fetch_mk_pdf_text(url)


def fetch_2021_level(level: int) -> str:
    """Download 2021 Level PDF (Level N = grade N, in 08/ folder)."""
    url = f"{MK_BASE}/2021/08/2021_Level-{level}_National-Winners.pdf"
    return fetch_mk_pdf_text(url)


def fetch_2020_level(level: int) -> str:
    """Download 2020 Level PDF (archived in 2022/04 folder)."""
    url = f"{MK_BASE}/2022/04/2020_Level-{level}_National-Winners.pdf"
    return fetch_mk_pdf_text(url)


def fetch_state_winners(year: int, state_abbrev: str) -> str:
    """Download state-winners PDF (2022, 2023)."""
    url = f"{MK_BASE}/{year}/05/{year}_{state_abbrev}-Winners.pdf"
    return fetch_mk_pdf_text(url)


def build_mk_name_grade_to_state() -> Dict[Tuple[str, int], str]:
    """Build (normalized_name, grade) -> state from Math Kangaroo PDFs (2024, 2023, 2022, 2021, 2020)."""
    name_grade_to_state: Dict[Tuple[str, int], str] = {}

    # 2020: Level PDFs (archived in 2022/04, same format as 2021)
    print("  2020 Level PDFs...", file=sys.stderr)
    for level in range(1, 13):
        text = fetch_2020_level(level)
        if not text:
            continue
        n = 0
        for norm_name, g, state in parse_national_winners(text, 2020, level):
            key = (norm_name, g)
            if key not in name_grade_to_state:
                name_grade_to_state[key] = state
                n += 1
        if n:
            print(f"    2020 Level {level}: {n} new", file=sys.stderr)

    # 2021: Level PDFs (Level 1-12, format: YEAR LEVEL NAME RANK SCORE CENTER STATE)
    print("  2021 Level PDFs...", file=sys.stderr)
    for level in range(1, 13):
        text = fetch_2021_level(level)
        if not text:
            continue
        n = 0
        for norm_name, g, state in parse_national_winners(text, 2021, level):
            key = (norm_name, g)
            if key not in name_grade_to_state:
                name_grade_to_state[key] = state
                n += 1
        if n:
            print(f"    2021 Level {level}: {n} new", file=sys.stderr)

    # 2024: National Grade PDFs (grades 2-12)
    print("  2024 national grade PDFs...", file=sys.stderr)
    for grade in range(2, 13):
        text = fetch_national_grade(2024, grade)
        if not text:
            continue
        n = 0
        for norm_name, g, state in parse_national_winners(text, 2024, grade):
            key = (norm_name, g)
            if key not in name_grade_to_state:
                name_grade_to_state[key] = state
                n += 1
        if n:
            print(f"    2024 Grade {grade}: {n} new", file=sys.stderr)

    # 2023: State PDFs
    print("  2023 state PDFs...", file=sys.stderr)
    for state_abbrev in STATE_CODES:
        text = fetch_state_winners(2023, state_abbrev)
        if not text:
            continue
        n = 0
        for norm_name, g, state in parse_state_winners(text, 2023, state_abbrev):
            key = (norm_name, g)
            if key not in name_grade_to_state:
                name_grade_to_state[key] = state
                n += 1
        if n:
            print(f"    2023 {state_abbrev}: {n} new", file=sys.stderr)

    # 2022: State PDFs
    print("  2022 state PDFs...", file=sys.stderr)
    for state_abbrev in STATE_CODES:
        text = fetch_state_winners(2022, state_abbrev)
        if not text:
            continue
        n = 0
        for norm_name, g, state in parse_state_winners(text, 2022, state_abbrev):
            key = (norm_name, g)
            if key not in name_grade_to_state:
                name_grade_to_state[key] = state
                n += 1
        if n:
            print(f"    2022 {state_abbrev}: {n} new", file=sys.stderr)

    return name_grade_to_state


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    if not INCOMPLETE_JSON.exists():
        print(f"Missing {INCOMPLETE_JSON}. Run find_incomplete_students.py first.", file=sys.stderr)
        sys.exit(1)

    import json
    with INCOMPLETE_JSON.open(encoding="utf-8") as f:
        data = json.load(f)
    missing = data.get("missing_state") or []
    missing_ids: Set[int] = set()
    id_to_name: Dict[int, str] = {}
    for entry in missing:
        sid_raw = entry.get("student_id")
        if not sid_raw:
            continue
        try:
            sid = int(sid_raw)
        except ValueError:
            continue
        missing_ids.add(sid)
        id_to_name[sid] = (entry.get("student_name") or "").strip()

    with STUDENTS_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    print("Fetching Math Kangaroo winners...", file=sys.stderr)
    name_grade_to_state = build_mk_name_grade_to_state()
    print(f"Total MK entries: {len(name_grade_to_state)}", file=sys.stderr)

    updates: Dict[int, str] = {}
    for sid in missing_ids:
        name = id_to_name.get(sid, "")
        if not name:
            continue
        for key in _name_key_variants(name):
            matches = [name_grade_to_state[(key, g)] for g in range(1, 13)
                       if (key, g) in name_grade_to_state]
            unique_states = list(dict.fromkeys(matches))
            if len(unique_states) == 1:
                updates[sid] = unique_states[0]
                break

    print(f"Matched {len(updates)} students from Math Kangaroo", file=sys.stderr)

    if dry_run:
        print("\n[DRY RUN] Would update:")
        for sid in sorted(updates.keys()):
            print(f"  {sid} {id_to_name.get(sid)} -> {updates[sid]}")
        return

    if not updates:
        return

    for row in rows:
        sid_raw = (row.get("student_id") or "").strip()
        try:
            sid = int(sid_raw)
        except ValueError:
            continue
        if sid in updates:
            row["state"] = updates[sid]

    tmp_path = STUDENTS_CSV.with_suffix(".csv.tmp")
    with tmp_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    tmp_path.replace(STUDENTS_CSV)
    print(f"Updated {len(updates)} rows in {STUDENTS_CSV}")


if __name__ == "__main__":
    main()
