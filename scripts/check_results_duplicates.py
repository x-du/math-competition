#!/usr/bin/env python3
"""
Detect duplicate student rows in each contest results.csv.

For every database/contests/**/results.csv with a student_id column, this
script reports student_ids that appear more than once (with CSV row numbers).
It also reports exact duplicate data rows (same values in every column).

Rows with an empty student_id are skipped for id-based duplicate detection.

student_id values listed in IGNORE_STUDENT_IDS are skipped (placeholders such as
unknown / unresolved students that may legitimately repeat).

Run from the repo root:

    python scripts/check_results_duplicates.py

Exits with status 1 if any file has duplicates.
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent
CONTESTS_DIR = REPO_ROOT / "database" / "contests"

# Reserved ids that may appear on multiple rows by convention (e.g. unknown student).
IGNORE_STUDENT_IDS = frozenset({"1597"})


def iter_results_csv_paths():
    if not CONTESTS_DIR.exists():
        return []
    return sorted(CONTESTS_DIR.rglob("results.csv"))


def check_file(
    path: Path,
) -> Tuple[
    List[Tuple[str, int, List[int]]],
    List[Tuple[List[int], Tuple[str, ...]]],
    List[str],
    bool,
]:
    """
    Returns:
      - dup_ids: (student_id, occurrence_count, row_numbers) for ids with count > 1
      - dup_tuples: (row_numbers, full_row_tuple) for tuples appearing more than once
      - fieldnames: header order for printing duplicate row previews
      - True if this file has a student_id column (otherwise skipped for id checks)
    """
    id_to_rows: Dict[str, List[int]] = defaultdict(list)
    tuple_to_rows: Dict[Tuple[str, ...], List[int]] = defaultdict(list)

    with open(path, newline="", encoding="utf-8") as f:
        try:
            reader = csv.DictReader(f)
        except csv.Error as e:
            raise RuntimeError(f"CSV read error: {e}") from e

        fieldnames = list(reader.fieldnames or [])
        if "student_id" not in fieldnames:
            return [], [], fieldnames, False

        row_number = 1  # header
        for row in reader:
            row_number += 1

            if not any((cell or "").strip() for cell in row.values()):
                continue

            sid = (row.get("student_id") or "").strip()
            if sid and sid not in IGNORE_STUDENT_IDS:
                id_to_rows[sid].append(row_number)

            key = tuple((row.get(h) or "").strip() for h in fieldnames)
            if (
                "student_id" in fieldnames
                and (row.get("student_id") or "").strip() in IGNORE_STUDENT_IDS
            ):
                continue
            tuple_to_rows[key].append(row_number)

    dup_ids: List[Tuple[str, int, List[int]]] = []
    for sid, rows in sorted(
        id_to_rows.items(),
        key=lambda x: int(x[0]) if x[0].isdigit() else x[0],
    ):
        if len(rows) > 1:
            dup_ids.append((sid, len(rows), rows))

    dup_tuples: List[Tuple[List[int], Tuple[str, ...]]] = []
    for key, rows in tuple_to_rows.items():
        if len(rows) > 1:
            dup_tuples.append((rows, key))

    dup_tuples.sort(key=lambda x: x[0][0])
    return dup_ids, dup_tuples, fieldnames, True


def main() -> int:
    paths = iter_results_csv_paths()
    if not paths:
        print(f"No results.csv files under {CONTESTS_DIR}")
        return 0

    any_issue = False
    skipped_no_column = 0

    for path in paths:
        try:
            dup_ids, dup_tuples, fieldnames, has_sid = check_file(path)
        except RuntimeError as e:
            rel = path.relative_to(REPO_ROOT)
            print(f"{rel}: {e}")
            any_issue = True
            continue

        if not has_sid:
            skipped_no_column += 1
            continue

        if not dup_ids and not dup_tuples:
            continue

        any_issue = True
        rel = path.relative_to(REPO_ROOT)
        print(f"{rel}")

        for sid, count, rows in dup_ids:
            rows_str = ", ".join(str(r) for r in rows)
            print(f"  student_id {sid} appears {count} times (rows {rows_str})")

        for rows, key in dup_tuples:
            preview = ", ".join(
                f"{k}={v!r}" for k, v in zip(fieldnames, key) if v
            )
            if len(preview) > 120:
                preview = preview[:117] + "..."
            print(f"  identical rows {rows}: {preview}")

        print()

    total = len(paths)
    print("Summary:")
    print(f"  results.csv files scanned: {total}")
    if skipped_no_column:
        print(f"  skipped (no student_id column): {skipped_no_column}")
    if any_issue:
        print("  status: FAIL (duplicates found)")
        return 1
    print("  status: OK (no duplicate student_id or identical rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
