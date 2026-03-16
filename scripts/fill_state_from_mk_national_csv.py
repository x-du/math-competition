#!/usr/bin/env python3
"""
Fill missing state for students using database/contests/mk-national CSV files.

1. student_id-based: if student_id appears in mk-national, use that state.
2. name-based: if name appears in mk-national with exactly one state across
   all entries (no ambiguity), use that state. Same logic as fill_state_from_math_kangaroo.

Per prompts/fill-missing-state.md section 2.2 (Math Kangaroo).

Usage: python scripts/fill_state_from_mk_national_csv.py [--dry-run]
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parent.parent
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
MK_NATIONAL_DIR = ROOT / "database" / "contests" / "mk-national"


def _normalize_name(name: str) -> str:
    return " ".join((name or "").lower().split())


def _name_key_variants(name: str) -> List[str]:
    """Key and variant (first + last) for matching names with middle names."""
    parts = (name or "").lower().split()
    key = " ".join(parts)
    if len(parts) > 2:
        return [key, f"{parts[0]} {parts[-1]}"]
    return [key]


def build_sid_to_state() -> Dict[int, str]:
    """student_id -> state when student has single state in mk-national."""
    sid_to_states: Dict[int, Set[str]] = {}
    for csv_path in sorted(MK_NATIONAL_DIR.glob("**/results.csv")):
        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sid_s = (row.get("student_id") or "").strip()
                state = (row.get("state") or "").strip()
                if not sid_s or not state:
                    continue
                try:
                    sid = int(sid_s)
                except ValueError:
                    continue
                if sid not in sid_to_states:
                    sid_to_states[sid] = set()
                sid_to_states[sid].add(state)

    return {sid: next(iter(states)) for sid, states in sid_to_states.items() if len(states) == 1}


def build_name_to_state() -> Dict[str, str]:
    """(normalized_name) -> state when name appears with exactly one state."""
    name_to_states: Dict[str, Set[str]] = {}
    for csv_path in sorted(MK_NATIONAL_DIR.glob("**/results.csv")):
        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = (row.get("student_name") or "").strip()
                state = (row.get("state") or "").strip()
                if not name or not state:
                    continue
                key = _normalize_name(name)
                if key not in name_to_states:
                    name_to_states[key] = set()
                name_to_states[key].add(state)

    return {k: next(iter(v)) for k, v in name_to_states.items() if len(v) == 1}


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    # Get missing-state students from students.csv (source of truth)
    missing_ids: Set[int] = set()
    id_to_name: Dict[int, str] = {}
    with STUDENTS_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid_s = (row.get("student_id") or "").strip()
            state = (row.get("state") or "").strip()
            name = (row.get("student_name") or "").strip()
            if not sid_s or state:
                continue
            try:
                sid = int(sid_s)
            except ValueError:
                continue
            missing_ids.add(sid)
            id_to_name[sid] = name

    print(f"Students with missing state: {len(missing_ids)}", file=sys.stderr)
    print("Building lookup from mk-national...", file=sys.stderr)
    sid_to_state = build_sid_to_state()
    name_to_state = build_name_to_state()
    print(f"  student_id matches: {len(sid_to_state)}, name matches (unique state): {len(name_to_state)}", file=sys.stderr)

    updates: Dict[int, str] = {}
    for sid in missing_ids:
        if sid in sid_to_state:
            updates[sid] = sid_to_state[sid]
            continue
        name = id_to_name.get(sid, "")
        if not name:
            continue
        for key in _name_key_variants(name):
            if key in name_to_state:
                updates[sid] = name_to_state[key]
                break

    print(f"Matched {len(updates)} students from mk-national", file=sys.stderr)

    if dry_run:
        print("\n[DRY RUN] Would update:", file=sys.stderr)
        for sid in sorted(updates.keys()):
            print(f"  {sid} {id_to_name.get(sid)} -> {updates[sid]}")
        return

    if not updates:
        return

    with STUDENTS_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

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
