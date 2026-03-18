#!/usr/bin/env python3
"""
Deduplicate contest results only: do not remove or merge rows in students.csv.
- Build a remap duplicate_student_id -> canonical_student_id using (name, state) and alias rules.
- Update all contest CSVs to use the canonical student_id so the same person appears once in search.
- students.csv is left unchanged (no rows removed).
"""

import csv
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
CONTESTS_DIR = ROOT / "database" / "contests"


def main() -> None:
    # Load all rows with 5 columns
    rows: list[dict] = []
    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        fieldnames = list(r.fieldnames or [])
        for row in r:
            sid_s = (row.get("student_id") or "").strip()
            if not sid_s:
                continue
            try:
                sid = int(sid_s)
            except ValueError:
                continue
            name = (row.get("student_name") or "").strip()
            state = (row.get("state") or "").strip()
            team_ids = (row.get("team_ids") or "").strip()
            alias = (row.get("alias") or "").strip()
            if not name:
                continue
            rows.append({
                "student_id": sid,
                "student_name": name,
                "state": state,
                "team_ids": team_ids,
                "alias": alias,
            })

    # Canonical sid per (name_lower, state). First pass: same key -> min sid.
    key_to_sids: dict[tuple[str, str], list[int]] = defaultdict(list)
    for r in rows:
        key = (r["student_name"].lower(), r["state"])
        key_to_sids[key].append(r["student_id"])

    canonical_by_key: dict[tuple[str, str], int] = {}
    for key, sids in key_to_sids.items():
        canonical_by_key[key] = min(sids)

    # Remap: old_sid -> canonical_sid (within same name+state)
    remap: dict[int, int] = {}
    for r in rows:
        key = (r["student_name"].lower(), r["state"])
        can = canonical_by_key[key]
        if r["student_id"] != can:
            remap[r["student_id"]] = can

    # Second: (name_lower, "") should merge to (name_lower, state) for any state if exists.
    name_lower_to_canonical_with_state: dict[str, int] = {}
    for (name_lower, state), can in canonical_by_key.items():
        if state:
            # Prefer keeping one with state; take min sid among those with state for this name
            if name_lower not in name_lower_to_canonical_with_state or can < name_lower_to_canonical_with_state[name_lower]:
                name_lower_to_canonical_with_state[name_lower] = can

    for r in rows:
        if r["state"]:
            continue
        name_lower = r["student_name"].lower()
        if name_lower in name_lower_to_canonical_with_state:
            target = name_lower_to_canonical_with_state[name_lower]
            if r["student_id"] != target:
                remap[r["student_id"]] = target

    # Third: alias: if row has name "Calvin Wang" and no state, and some other row has alias "Calvin Wang", merge to that row.
    alias_to_canonical: dict[tuple[str, str], int] = {}
    for r in rows:
        can = remap.get(r["student_id"], r["student_id"])
        key = (r["student_name"].lower(), r["state"])
        canonical_by_key[key] = min(canonical_by_key.get(key, can), can)
        for a in (r.get("alias") or "").split("|"):
            a = a.strip().lower()
            if a:
                alias_key = (a, r["state"])
                if alias_key not in alias_to_canonical or can < alias_to_canonical[alias_key]:
                    alias_to_canonical[alias_key] = can
                # also register (alias, "") so no-state "Calvin Wang" finds Ruilin Wang (Virginia)
                if r["state"]:
                    alias_key_empty = (a, "")
                    if alias_key_empty not in alias_to_canonical or can < alias_to_canonical[alias_key_empty]:
                        alias_to_canonical[alias_key_empty] = can

    for r in rows:
        if r["student_id"] in remap:
            continue
        # Only merge no-state rows to an alias match (don't merge (name, state) to (alias, other_state))
        if r["state"]:
            continue
        name_lower = r["student_name"].lower()
        # This row's name (with no state) might be an alias of another canonical row
        for state_variant in [r["state"], ""]:
            key = (name_lower, state_variant)
            if key in alias_to_canonical:
                target = alias_to_canonical[key]
                if target != r["student_id"]:
                    remap[r["student_id"]] = target
                    break

    # Resolve transitive remaps (1471 -> 10, and 10 might be remapped -> stay 10)
    for old, new in list(remap.items()):
        while new in remap and remap[new] != new:
            new = remap[new]
        remap[old] = new

    # Do not modify students.csv: keep all rows. Only update contest CSVs to use canonical ids.
    print(f"Remap: {len(remap)} student_ids -> canonical (students.csv unchanged)")

    # Update contest CSVs
    for csv_path in sorted(CONTESTS_DIR.rglob("*.csv")):
        if not csv_path.is_file():
            continue
        with open(csv_path, newline="", encoding="utf-8") as f:
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
                # Do not overwrite student_name: keep the name from the contest source (e.g. website)
                updated += 1
        if updated:
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                w.writerows(rows_out)
            print(f"  {csv_path.relative_to(ROOT)}: remapped {updated} rows")


if __name__ == "__main__":
    main()
