#!/usr/bin/env python3
"""
Import EGMO results from official-scores.csv into results.csv for students
present in students.csv.

Combines Given Name + Family Name for matching against student_name and aliases.
US students (Country Code USA): us_rank and mcp_rank are assigned by total score
among matched US students (higher total first; ties broken by official Rank).
Non-US students: us_rank and mcp_rank are left empty.

Run from repo root:
  python scripts/import_egmo_results.py
  python scripts/import_egmo_results.py --year 2026
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent
STUDENTS_CSV = REPO_ROOT / "database" / "students" / "students.csv"

RESULT_FIELDS = [
    "student_id",
    "student_name",
    "country",
    "award",
    "rank",
    "us_rank",
    "P1",
    "P2",
    "P3",
    "P4",
    "P5",
    "P6",
    "total",
    "mcp_rank",
]


def load_name_to_student_id() -> Tuple[Dict[str, str], Dict[str, str]]:
    """Map any student_name or alias string -> student_id; student_id -> canonical name."""
    name_to_sid: Dict[str, str] = {}
    sid_to_canonical: Dict[str, str] = {}

    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = (row.get("student_id") or "").strip()
            primary = (row.get("student_name") or "").strip()
            if not sid or not primary:
                continue
            sid_to_canonical[sid] = primary
            name_to_sid[primary] = sid
            alias_field = (row.get("alias") or "").strip()
            if alias_field:
                for a in alias_field.split("|"):
                    a = a.strip()
                    if a:
                        name_to_sid[a] = sid

    return name_to_sid, sid_to_canonical


def parse_int(s: str) -> Optional[int]:
    s = (s or "").strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description="Import EGMO official scores into results.csv")
    ap.add_argument("--year", type=int, default=2026, help="Contest year (folder year=YYYY)")
    args = ap.parse_args()
    year = args.year

    egmo_dir = REPO_ROOT / "database" / "contests" / "egmo" / f"year={year}"
    official_path = egmo_dir / "official-scores.csv"
    results_path = egmo_dir / "results.csv"

    if not official_path.is_file():
        raise SystemExit(f"Missing {official_path}")

    name_to_sid, sid_to_canonical = load_name_to_student_id()

    matched: List[Dict[str, Any]] = []

    with open(official_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            given = (row.get("Given Name") or "").strip()
            family = (row.get("Family Name") or "").strip()
            constructed = f"{given} {family}".strip()
            if not constructed:
                continue

            sid = name_to_sid.get(constructed)
            if not sid:
                continue

            country_code = (row.get("Country Code") or "").strip()
            country_name = (row.get("Country Name") or "").strip()
            is_us = country_code == "USA"

            overall_rank = (row.get("Rank") or "").strip()
            award = (row.get("Award") or "").strip()
            total_s = (row.get("Total") or "").strip()

            matched.append(
                {
                    "student_id": sid,
                    "student_name": sid_to_canonical[sid],
                    "country": country_name,
                    "award": award,
                    "rank": overall_rank,
                    "country_code": country_code,
                    "is_us": is_us,
                    "P1": (row.get("P1") or "").strip(),
                    "P2": (row.get("P2") or "").strip(),
                    "P3": (row.get("P3") or "").strip(),
                    "P4": (row.get("P4") or "").strip(),
                    "P5": (row.get("P5") or "").strip(),
                    "P6": (row.get("P6") or "").strip(),
                    "total": total_s,
                    "_total_i": parse_int(total_s),
                    "_official_rank_i": parse_int(overall_rank),
                }
            )

    us_rows = [r for r in matched if r["is_us"]]
    us_rows.sort(
        key=lambda r: (
            -(r["_total_i"] if r["_total_i"] is not None else -1),
            r["_official_rank_i"] if r["_official_rank_i"] is not None else 10**9,
            r["student_name"],
        )
    )
    us_order = {r["student_id"]: i + 1 for i, r in enumerate(us_rows)}

    out_rows: List[Dict[str, str]] = []
    matched.sort(
        key=lambda r: (
            -(r["_total_i"] if r["_total_i"] is not None else -1),
            r["student_name"],
        )
    )

    for r in matched:
        sid = r["student_id"]
        us_r = ""
        mcp_r = ""
        if r["is_us"]:
            pos = us_order.get(sid)
            if pos is not None:
                us_r = str(pos)
                mcp_r = str(pos)

        out_rows.append(
            {
                "student_id": sid,
                "student_name": r["student_name"],
                "country": r["country"],
                "award": r["award"],
                "rank": r["rank"],
                "us_rank": us_r,
                "P1": r["P1"],
                "P2": r["P2"],
                "P3": r["P3"],
                "P4": r["P4"],
                "P5": r["P5"],
                "P6": r["P6"],
                "total": r["total"],
                "mcp_rank": mcp_r,
            }
        )

    results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RESULT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Wrote {len(out_rows)} rows to {results_path}")


if __name__ == "__main__":
    main()
