#!/usr/bin/env python3
"""
Validate contest student rows against students.csv.

A row passes if student_name matches student_name or any alias in
students.csv, or if student_name does not match but student_id is
present and exists in students.csv (resolved to that student's canonical
student_name).

After that resolution step, an extra check runs on the same rows: when
both student_id and student_name are present and student_id exists in
students.csv, the contest name must match that id's primary name or an
alias (otherwise a warning is printed). This is layered on top of the
resolution rules above and does not change which rows count as errors.

Run from the repo root:

    python scripts/check_student_name.py
"""

import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent
STUDENTS_CSV = REPO_ROOT / "database" / "students" / "students.csv"
CONTESTS_DIR = REPO_ROOT / "database" / "contests"


def load_students_csv() -> Tuple[Set[str], Dict[str, str], Dict[str, Set[str]]]:
    """
    Load students.csv.

    Returns:
        allowed: all student_name and alias strings (global name pool)
        id_to_canonical: student_id -> primary student_name
        id_to_known_names: student_id -> {canonical, ...aliases} for that id
    """
    allowed: Set[str] = set()
    id_to_canonical: Dict[str, str] = {}
    id_to_known_names: Dict[str, Set[str]] = defaultdict(set)

    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        if "student_name" not in fieldnames or "student_id" not in fieldnames:
            raise SystemExit(
                f"'student_name' and 'student_id' columns are required in {STUDENTS_CSV}"
            )

        for row in reader:
            primary = (row.get("student_name") or "").strip()
            sid = (row.get("student_id") or "").strip()

            alias_field = (row.get("alias") or "").strip()
            aliases: List[str] = []
            if alias_field:
                for a in alias_field.split("|"):
                    a = a.strip()
                    if a:
                        aliases.append(a)

            if primary:
                allowed.add(primary)
                if sid:
                    id_to_known_names[sid].add(primary)
                    id_to_canonical[sid] = primary

            for alias in aliases:
                allowed.add(alias)
                if sid:
                    id_to_known_names[sid].add(alias)

    return allowed, id_to_canonical, {k: set(v) for k, v in id_to_known_names.items()}


def iter_contest_csv_files() -> Iterable[Path]:
    """Yield all CSV files under the contests directory."""
    if not CONTESTS_DIR.exists():
        return []
    return sorted(CONTESTS_DIR.rglob("*.csv"))


def scan_contest_csvs(
    allowed_names: Set[str],
    id_to_canonical: Dict[str, str],
    id_to_known_names: Dict[str, Set[str]],
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]], int, int]:
    """
    Single pass over contest CSVs: resolution checks first, then id/name
    consistency warnings on top (same visit per row).

    Resolution (errors): a row violates when student_name is non-empty,
    not in allowed_names, and (no student_id or student_id not in
    id_to_canonical).

    Warnings: when student_id and student_name are both non-empty and
    student_id is in id_to_known_names but student_name is not in that id's
    allowed set.

    Returns:
        (violations, mismatch_warnings, files_with_student_name_col,
         total_checked_rows)
    """
    violations: List[Dict[str, object]] = []
    mismatch_warnings: List[Dict[str, object]] = []
    files_with_student_name = 0
    total_rows_checked = 0

    for csv_path in iter_contest_csv_files():
        with open(csv_path, newline="", encoding="utf-8") as f:
            try:
                reader = csv.DictReader(f)
            except csv.Error:
                # Skip malformed files; integrity can be checked separately.
                continue

            fieldnames = reader.fieldnames or []
            if "student_name" not in fieldnames:
                continue

            has_student_id = "student_id" in fieldnames
            files_with_student_name += 1
            row_number = 1  # header
            for row in reader:
                row_number += 1
                name = (row.get("student_name") or "").strip()
                if not name:
                    continue

                total_rows_checked += 1
                sid = (row.get("student_id") or "").strip() if has_student_id else ""

                # Existing check: must resolve by global name or by student_id.
                if name not in allowed_names:
                    if sid and sid in id_to_canonical:
                        pass
                    else:
                        violations.append(
                            {
                                "student_id": sid,
                                "students_name": "",
                                "contest_name": name,
                                "csv_path": csv_path,
                                "row_number": row_number,
                            }
                        )

                # Layered check: id present in DB -> name must match that id.
                if has_student_id and sid and name:
                    known = id_to_known_names.get(sid)
                    if known is not None and name not in known:
                        mismatch_warnings.append(
                            {
                                "student_id": sid,
                                "expected_names": sorted(known),
                                "contest_name": name,
                                "csv_path": csv_path,
                                "row_number": row_number,
                            }
                        )

    return violations, mismatch_warnings, files_with_student_name, total_rows_checked


def main() -> int:
    allowed_names, id_to_canonical, id_to_known_names = load_students_csv()
    (
        violations,
        mismatch_warnings,
        files_with_student_name,
        total_rows_checked,
    ) = scan_contest_csvs(allowed_names, id_to_canonical, id_to_known_names)

    print("=== Contest student_name validation against students.csv ===\n")
    print(f"Total unique allowed names (student_name + alias): {len(allowed_names)}")
    print(f"Contest CSV files with a student_name column: {files_with_student_name}")
    print(f"Contest rows with non-empty student_name checked: {total_rows_checked}\n")

    if not violations:
        print(
            "All contest student rows resolve to students.csv via student_name, "
            "alias, or student_id."
        )
    else:
        print(
            f"Found {len(violations)} contest row(s) with no matching name or student_id.\n"
        )
        print(
            "Each line below is:\n"
            "  student_id | students.csv name | contest student_name | file:row\n"
        )

        def sort_key_v(v: Dict[str, object]) -> Tuple[str, str, str, int]:
            sid = str(v.get("student_id") or "")
            cname = str(v.get("contest_name") or "")
            path = str(v.get("csv_path") or "")
            row = int(v.get("row_number") or 0)
            return (sid, cname, path, row)

        for v in sorted(violations, key=sort_key_v):
            sid = str(v.get("student_id") or "").strip() or "N/A"
            canonical = str(v.get("students_name") or "").strip() or "N/A"
            contest_name = str(v.get("contest_name") or "").strip()
            csv_path = v.get("csv_path")
            row_number = int(v.get("row_number") or 0)
            rel_path = (
                csv_path.relative_to(REPO_ROOT)
                if isinstance(csv_path, Path)
                else str(csv_path)
            )
            print(
                f"  {sid} | {canonical} | {contest_name} | {rel_path}: row {row_number}"
            )

    if mismatch_warnings:
        print()
        print(
            "=== Warnings (on top of resolution checks): student_id vs "
            "student_name in contest CSVs ===\n"
            f"Rows where student_id exists in students.csv but contest student_name "
            f"is not that student's primary name or an alias ({len(mismatch_warnings)}).\n"
            "Each line is:\n"
            "  WARNING: student_id | contest student_name | allowed names for id | file:row\n"
        )

        def sort_key_w(v: Dict[str, object]) -> Tuple[str, str, str, int]:
            sid = str(v.get("student_id") or "")
            cname = str(v.get("contest_name") or "")
            path = str(v.get("csv_path") or "")
            row = int(v.get("row_number") or 0)
            return (sid, cname, path, row)

        for w in sorted(mismatch_warnings, key=sort_key_w):
            sid = str(w.get("student_id") or "").strip()
            contest_name = str(w.get("contest_name") or "").strip()
            expected = w.get("expected_names")
            if isinstance(expected, list):
                allowed_str = " / ".join(str(x) for x in expected)
            else:
                allowed_str = str(expected or "")
            csv_path = w.get("csv_path")
            row_number = int(w.get("row_number") or 0)
            rel_path = (
                csv_path.relative_to(REPO_ROOT)
                if isinstance(csv_path, Path)
                else str(csv_path)
            )
            print(
                f"  WARNING: {sid} | {contest_name} | {allowed_str} | "
                f"{rel_path}: row {row_number}"
            )

    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())

