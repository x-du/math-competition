#!/usr/bin/env python3
"""
Fill missing state for students using school/team from contest records.

1. Load students missing state from incomplete_students.json.
2. For each, collect school/team names from contest CSVs (student_id lookup)
   and from team_ids -> teams.csv team_name.
3. Call LLM to infer US state from school/team name; LLM must return both
   state and accuracy (0-100). We use the accuracy to decide: only when
   accuracy >= 80 do we accept the inferred state.
4. Update database/students/students.csv with those states.

Requires OPENAI_API_KEY (unless --no-llm). Usage:
  python scripts/infer_state_from_school_llm.py [--dry-run] [--no-llm]
  --no-llm   Only build and write school_team_for_state_inference.json; do not call LLM or update CSV.
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parent.parent
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
CONTESTS_DIR = ROOT / "database" / "contests"
INCOMPLETE_JSON = ROOT / "incomplete_students.json"
SCHOOL_TEAM_JSON = ROOT / "school_team_for_state_inference.json"

# Only use inferred state when LLM returns accuracy >= this (0-100).
ACCURACY_THRESHOLD = 80


def load_missing_state_student_ids() -> Set[int]:
    """Load student_ids that are missing state from incomplete_students.json."""
    ids, _ = _load_missing_state()
    return ids


def _load_missing_state() -> Tuple[Set[int], Dict[int, str]]:
    """Load missing_state from incomplete_students.json; return (ids, id -> student_name)."""
    if not INCOMPLETE_JSON.exists():
        raise FileNotFoundError(f"Missing {INCOMPLETE_JSON}")
    with INCOMPLETE_JSON.open(encoding="utf-8") as f:
        data = json.load(f)
    missing = data.get("missing_state") or []
    ids: Set[int] = set()
    id_to_name: Dict[int, str] = {}
    for entry in missing:
        sid_raw = entry.get("student_id")
        if not sid_raw:
            continue
        try:
            sid = int(sid_raw)
        except ValueError:
            continue
        ids.add(sid)
        id_to_name[sid] = (entry.get("student_name") or "").strip()
    return ids, id_to_name


def collect_school_team_by_student() -> Dict[int, List[str]]:
    """
    Build student_id -> list of school/team name strings from:
    - Contest CSVs with student_id and (school | team_name | team | club_name)
    - teams.csv (team_id -> team_name) and students' team_ids in students.csv
    """
    sid_to_strings: Dict[int, List[str]] = {}

    def add(sid: int, s: str) -> None:
        s = (s or "").strip()
        if not s or s.lower() in ("unknown", "n/a", "-", "individual", "homeschool", "homeschooled"):
            return
        if sid not in sid_to_strings:
            sid_to_strings[sid] = []
        if s not in sid_to_strings[sid]:
            sid_to_strings[sid].append(s)

    # Contest CSVs: student_id + school | team_name | team | club_name
    for csv_path in sorted(CONTESTS_DIR.rglob("*.csv")):
        if "teams.csv" in str(csv_path):
            continue
        try:
            with csv_path.open(newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                fn = [x.strip() for x in (reader.fieldnames or [])]
                if "student_id" not in fn:
                    continue
                for row in reader:
                    sid_raw = (row.get("student_id") or "").strip()
                    if not sid_raw:
                        continue
                    try:
                        sid = int(sid_raw)
                    except ValueError:
                        continue
                    for col in ("school", "team_name", "team", "club_name"):
                        if col in fn:
                            val = (row.get(col) or "").strip()
                            if val:
                                add(sid, val)
        except Exception:
            continue

    # teams.csv: team_id -> team_name; students have team_ids in students.csv
    with STUDENTS_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            team_ids_raw = (row.get("team_ids") or "").strip()
            if not team_ids_raw:
                continue
            sid_raw = (row.get("student_id") or "").strip()
            try:
                sid = int(sid_raw)
            except ValueError:
                continue
            for part in team_ids_raw.split("|"):
                part = part.strip()
                if not part:
                    continue
                try:
                    tid = int(part)
                except ValueError:
                    continue
                # Resolve team_id -> team_name from any teams.csv
                for teams_path in CONTESTS_DIR.rglob("teams.csv"):
                    try:
                        with teams_path.open(newline="", encoding="utf-8") as tf:
                            tr = csv.DictReader(tf)
                            tfn = [x.strip() for x in (tr.fieldnames or [])]
                            if "team_id" not in tfn or "team_name" not in tfn:
                                continue
                            for trow in tr:
                                if (trow.get("team_id") or "").strip() == str(tid):
                                    tname = (trow.get("team_name") or "").strip()
                                    if tname:
                                        add(sid, tname)
                                    break
                    except Exception:
                        continue

    return sid_to_strings


def _get_openai_client():
    try:
        import openai
    except ImportError:
        print("Install openai: pip install openai", file=sys.stderr)
        raise
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is not set")
    return openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def call_llm_infer_state_batch(
    items: List[Tuple[int, str]], batch_size: int = 25
) -> List[Tuple[int, str, int]]:
    """
    Call LLM to infer US state from school/team names (batched).
    items = [(student_id, school_or_team), ...]
    Returns [(student_id, state, accuracy_0_100), ...]. Only use when accuracy >= ACCURACY_THRESHOLD.
    """
    client = _get_openai_client()
    results: List[Tuple[int, str, int]] = []

    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        numbered = [
            f"{j+1}. (id={sid}) {name}" for j, (sid, name) in enumerate(batch)
        ]
        prompt = """Given these US school or team names (from math competition data), infer the most likely US state for each.

List (each line: id=student_id, then school/team name):
%s

Reply with a JSON array. Each element must have:
- "id": the student_id number (integer)
- "state": Full US state name (e.g. "California", "New York") or "Unknown" if you cannot determine or it is outside the US.
- "accuracy": Your confidence that the state is correct, 0 to 100 (integer). Use lower values if the name is ambiguous or could be in multiple states.

Example: [{"id": 18, "state": "New Jersey", "accuracy": 85}, {"id": 36, "state": "Unknown", "accuracy": 0}]
Reply with only the JSON array, no other text."""

        body = "\n".join(numbered)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt % body}],
            temperature=0,
        )
        text = (response.choices[0].message.content or "").strip()
        if "```" in text:
            text = re.sub(r"^.*?```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```.*$", "", text)
        try:
            arr = json.loads(text)
            if not isinstance(arr, list):
                arr = [arr]
            id_to_item = {sid: (sid, name) for sid, name in batch}
            for elem in arr:
                try:
                    sid = int(elem.get("id")) if elem.get("id") is not None else None
                except (TypeError, ValueError):
                    sid = None
                if sid is None or sid not in id_to_item:
                    continue
                state = (elem.get("state") or "Unknown").strip()
                acc = elem.get("accuracy")
                acc = max(0, min(100, int(acc))) if acc is not None else 0
                results.append((sid, state, acc))
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            print(f"Batch parse error: {e}", file=sys.stderr)
            for sid, _ in batch:
                results.append((sid, "Unknown", 0))

    return results


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    no_llm = "--no-llm" in sys.argv

    missing_ids, id_to_name = _load_missing_state()
    print(f"Students missing state: {len(missing_ids)}")

    sid_to_strings = collect_school_team_by_student()
    # Restrict to missing-state students and those with at least one school/team
    candidates: Dict[int, List[str]] = {
        sid: strings for sid, strings in sid_to_strings.items()
        if sid in missing_ids and strings
    }
    print(f"Of those, with at least one school/team from records: {len(candidates)}")

    if not candidates:
        print("Nothing to infer.")
        return

    # Write JSON of school/team names before calling LLM
    out_entries = [
        {
            "student_id": sid,
            "student_name": id_to_name.get(sid, ""),
            "schools_and_teams": strings,
        }
        for sid, strings in sorted(candidates.items(), key=lambda x: x[0])
    ]
    with SCHOOL_TEAM_JSON.open("w", encoding="utf-8") as f:
        json.dump(out_entries, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(out_entries)} entries to {SCHOOL_TEAM_JSON}")

    if no_llm:
        print("--no-llm: skipping LLM calls and CSV update.")
        return

    # One (student_id, school_or_team) per student; use first available string
    items: List[Tuple[int, str]] = [
        (sid, strings[0]) for sid, strings in sorted(candidates.items(), key=lambda x: x[0])
    ]
    results = call_llm_infer_state_batch(items)

    updates: Dict[int, str] = {}
    skipped_low_accuracy = 0
    skipped_unknown = 0

    for sid, state, accuracy in results:
        if state and state.lower() != "unknown":
            if accuracy >= ACCURACY_THRESHOLD:
                updates[sid] = state
            else:
                skipped_low_accuracy += 1
        else:
            skipped_unknown += 1

    print(f"Inferred state with accuracy >= {ACCURACY_THRESHOLD}: {len(updates)}")
    print(f"Skipped (low accuracy): {skipped_low_accuracy}, unknown: {skipped_unknown}")

    if dry_run:
        print("\n[DRY RUN] Would update students.csv with:")
        for sid in sorted(updates.keys()):
            print(f"  student_id={sid} -> state={updates[sid]}")
        return

    if not updates:
        return

    with STUDENTS_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

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
