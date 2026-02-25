#!/usr/bin/env python3
"""
One-off script: merge duplicate student names in students.csv.
- Groups rows by student_name; for each name with multiple rows, keeps min(student_id) as canonical.
- Merges team_ids (union, sorted) and keeps first non-empty alias.
- Removes duplicate rows, updates all contest results CSV to use canonical student_id.
"""

import csv
from pathlib import Path


def parse_team_ids(s: str) -> set[int]:
    out = set()
    for x in (s or "").split("|"):
        x = x.strip()
        if not x:
            continue
        try:
            out.add(int(x))
        except ValueError:
            pass
    return out


def main() -> None:
    base = Path(__file__).resolve().parent.parent
    students_path = base / "database" / "students" / "students.csv"
    contests_dir = base / "database" / "contests"

    # Load all student rows
    rows: list[tuple[int, str, str, str]] = []
    with open(students_path, encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            sid = int(row["student_id"])
            name = (row.get("student_name", row.get("name", "")) or "").strip()
            team_ids = (row.get("team_ids", row.get("team_id", "")) or "").strip()
            alias = (row.get("alias") or "").strip()
            if not name:
                continue
            rows.append((sid, name, team_ids, alias))

    # Group by name (case-sensitive to match existing behavior)
    by_name: dict[str, list[tuple[int, str, str]]] = {}
    for sid, name, team_ids, alias in rows:
        by_name.setdefault(name, []).append((sid, team_ids, alias))

    # Build merged rows and remap
    merged: list[tuple[int, str, str, str]] = []
    remap: dict[int, int] = {}  # old_sid -> canonical_sid

    for name, group in by_name.items():
        if len(group) == 1:
            sid, team_ids, alias = group[0]
            merged.append((sid, name, team_ids, alias))
            continue
        # Multiple rows: pick min id as canonical, merge team_ids and alias
        canonical = min(g[0] for g in group)
        all_team_ids: set[int] = set()
        alias_merged = ""
        for sid, team_ids, alias in group:
            all_team_ids |= parse_team_ids(team_ids)
            if alias and not alias_merged:
                alias_merged = alias
            if sid != canonical:
                remap[sid] = canonical
        team_ids_str = "|".join(str(t) for t in sorted(all_team_ids)) if all_team_ids else ""
        merged.append((canonical, name, team_ids_str, alias_merged))

    merged.sort(key=lambda x: x[0])

    # Write merged students.csv
    with open(students_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["student_id", "student_name", "team_ids", "alias"])
        for sid, name, team_ids_str, alias in merged:
            w.writerow([sid, name, team_ids_str or "", alias or ""])
    print(f"Wrote {students_path} with {len(merged)} rows (removed {len(rows) - len(merged)} duplicates)")

    # Update all results CSV files
    for results_path in sorted(contests_dir.rglob("results*.csv")):
        if not results_path.is_file():
            continue
        with open(results_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames or [])
            rows_out = list(reader)
        if "student_id" not in fieldnames:
            continue
        updated = 0
        for row in rows_out:
            try:
                old_id = int(row["student_id"])
            except (ValueError, KeyError):
                continue
            if old_id in remap:
                row["student_id"] = str(remap[old_id])
                updated += 1
        with open(results_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows_out)
        if updated:
            print(f"  {results_path.relative_to(base)}: remapped {updated} student_id(s)")


if __name__ == "__main__":
    main()
