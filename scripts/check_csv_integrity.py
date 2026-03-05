#!/usr/bin/env python3
"""
Check basic table integrity for all CSV files under the database directory.

For each CSV file, this script checks that every non-empty data row has the
same number of comma‑separated values as the header row.

Run from the repo root:

    python scripts/check_csv_integrity.py

Only files with row-length issues are printed. Exits with status 1 if any
file has mismatched row lengths.
"""

import csv
import sys
from pathlib import Path
from typing import List, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent
DATABASE = REPO_ROOT / "database"


def iter_csv_files() -> List[Path]:
    """Return a sorted list of all CSV files under the database directory."""
    if not DATABASE.exists():
        return []
    return sorted(DATABASE.rglob("*.csv"))


def check_csv_file(csv_path: Path) -> List[Tuple[int, int, int, list]]:
    """Return a list of row-length issues for a single CSV file.

    Each entry in the returned list is a tuple:
        (row_number, expected_num_columns, actual_num_columns, row_values)
    """
    issues: List[Tuple[int, int, int, list]] = []

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            # Empty file; nothing to check.
            return issues
        except csv.Error as e:
            # Malformed header line; treat as a single issue on row 1.
            issues.append((1, 0, 0, [f"CSV error in header: {e}"]))
            return issues

        expected_len = len(header)
        row_number = 1
        for row in reader:
            row_number += 1

            # Skip completely blank rows so trailing newlines don't count as errors.
            if not any((cell or "").strip() for cell in row):
                continue

            actual_len = len(row)
            if actual_len != expected_len:
                issues.append((row_number, expected_len, actual_len, row))

    return issues


def main() -> None:
    csv_files = iter_csv_files()
    if not csv_files:
        print(f"No CSV files found under {DATABASE}")
        return

    total = len(csv_files)
    with_issues = 0
    for csv_path in csv_files:
        issues = check_csv_file(csv_path)
        if not issues:
            continue

        with_issues += 1
        rel_path = csv_path.relative_to(REPO_ROOT)
        print(f"{rel_path}: {len(issues)} issue(s)")
        for row_number, expected, actual, row in issues:
            preview = ", ".join(row)
            if len(preview) > 200:
                preview = preview[:197] + "..."
            print(
                f"  Row {row_number}: expected {expected} value(s), "
                f"found {actual}: {preview}"
            )
        print()

    print("Summary:")
    print(f"  Total tables:     {total}")
    print(f"  With violations: {with_issues}")
    print(f"  OK:              {total - with_issues}")

    if with_issues:
        sys.exit(1)


if __name__ == "__main__":
    main()

