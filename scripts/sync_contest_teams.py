#!/usr/bin/env python3
"""Sync contest team rosters and `team_id` in results.

See prompts/sync-contest-teams.md.

- **BMT** (`bmt <year>` or a single numeric year, legacy): rebuild
  `database/contests/bmt-teams/year=<YEAR>/teams.csv` from the five BMT
  `results.csv` files. See prompts/add-bmt-teams.md.

- **Generic** (`sync <contest> <year>`): if `results.csv` has a `team_name` or
  `team` column, create or update `<contest>-teams/year=<year>/teams.csv` and
  ensure `results.csv` has a `team_id` column (after the team name column),
  reusing `team_id` from an existing `teams.csv` when team names match.

- **All contests** (`sync-all <year>`): run BMT aggregate when `bmt/` has that
  year, then run generic sync for every other contest folder (skipping
  `bmt-algebra` etc., which are included in the BMT aggregate).

If a competition has no `team` or `team_name` column, generic sync skips it.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CONTESTS_DIR = REPO / "database" / "contests"

BMT_FOLDERS = ["bmt", "bmt-algebra", "bmt-calculus", "bmt-discrete", "bmt-geometry"]
BMT_SUBFOLDERS = {"bmt-algebra", "bmt-calculus", "bmt-discrete", "bmt-geometry"}
TOP_LEVEL_SKIP = {"contests.csv", "contests_by_year.csv"}

# BMT 2024 overall top 10 (optional metadata for teams that appear in published standings)
STANDINGS_BMT_2024 = {
    "032": ("!?", "Palo Alto HS"),
    "057": ("CCA Conspiracy", "Canyon Crest Academy Math Team"),
    "208": ("GMC Anaconda", "Gunn Math Circle"),
    "023": ("Cupertino Gold", "Cupertino HS"),
    "100": ("Lynbrook Purple", "Lynbrook HS"),
    "017": ("Utah Arches", "Utah ARML"),
    "013": ("Washington Gold", "Seattle Infinity Math Circle"),
    "128": ("Saratoga 1", "Saratoga HS"),
    "117": ("AlphaStar Pythagoras", "AlphaStar Academy"),
    "115": ("AlphaStar Newton", "AlphaStar Academy"),
}

STATE_HINTS = [
    ("Utah ARML", "Utah"),
    ("Utah Arches", "Utah"),
    ("Seattle Infinity", "Washington"),
    ("Washington Gold", "Washington"),
    ("Minnesota All State", "Minnesota"),
    ("Minnesota Gold", "Minnesota"),
    ("Davidson Academy", "Nevada"),
    ("BASIS Independent", "California"),
    ("Lynbrook", "California"),
    ("Saratoga HS", "California"),
    ("Palo Alto HS", "California"),
    ("Cupertino HS", "California"),
    ("The Harker School", "California"),
    ("Harker ", "California"),
    ("Canyon Crest", "California"),
    ("Monta Vista", "California"),
    ("Folsom HS", "California"),
    ("Gunn Math Circle", "California"),
    ("AV Math Team", "California"),
    ("Think Academy", "California"),
    ("AlphaStar", "California"),
    ("YEA", "California"),
    ("Proof School", "California"),
    ("Stratford Preparatory", "California"),
    ("OC Math Team", "California"),
    ("Sierra Canyon", "California"),
    ("RSM Bay Area", "California"),
    ("Math Nuts", "California"),
    ("Invent the Future", "California"),
    ("MSJ A", "California"),
]


def normalize_team_id(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw:
        return ""
    if raw.isdigit():
        return raw.zfill(3)
    return raw


def team_id_from_bmt(bmt: str) -> str:
    bmt = (bmt or "").strip()
    m = re.match(r"^(\d+)[A-Z]$", bmt)
    if not m:
        return ""
    return normalize_team_id(m.group(1))


def infer_state(team_name: str, school: str) -> str:
    blob = f" {team_name} {school} "
    compact = re.sub(r"\s+", "", blob)
    for needle, st in STATE_HINTS:
        if needle in blob:
            return st
        if re.sub(r"\s+", "", needle) in compact:
            return st
    return ""


def mode_meta(samples: list[tuple[str, str]]) -> tuple[str, str]:
    filtered = [(t, s) for t, s in samples if t.strip() or s.strip()]
    if not filtered:
        return "", ""
    (tn, sc), _ = Counter(filtered).most_common(1)[0]
    return tn.strip(), sc.strip()


def normalize_team_label(s: str) -> str:
    return " ".join((s or "").strip().split())


def detect_team_column(fieldnames: list[str] | None) -> str | None:
    """Use `team_name` if present, else `team`. If both headers exist, use `team_name`."""
    if not fieldnames:
        return None
    for name in ("team_name", "team"):
        if name in fieldnames:
            return name
    return None


def parse_int_team_ids(ids: list[str]) -> tuple[list[int], int]:
    """Return (integer values, max width of digit strings for zero-padding)."""
    ints: list[int] = []
    width = 0
    for s in ids:
        s = (s or "").strip()
        if s.isdigit():
            ints.append(int(s))
            width = max(width, len(s))
    return ints, width


def rebuild_bmt_aggregate(year: str) -> None:
    teams_path = REPO / f"database/contests/bmt-teams/year={year}/teams.csv"
    existing: dict[str, dict[str, str]] = {}
    if teams_path.exists():
        with teams_path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                tid = normalize_team_id(row["team_id"])
                existing[tid] = {
                    "team_name": (row.get("team_name") or "").strip(),
                    "school": (row.get("school") or "").strip(),
                    "state": (row.get("state") or "").strip(),
                }

    roster: dict[str, dict[int, set[str]]] = defaultdict(lambda: defaultdict(set))
    meta_lines: dict[str, list[tuple[str, str]]] = defaultdict(list)

    for folder in BMT_FOLDERS:
        p = REPO / f"database/contests/{folder}/year={year}/results.csv"
        if not p.exists():
            continue
        with p.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                bmt = (row.get("bmt_student_id") or "").strip()
                tid = normalize_team_id(row.get("team_id") or "") or team_id_from_bmt(bmt)
                if not tid:
                    continue
                roster[tid][int(row["student_id"])].add(bmt)
                tn = (row.get("team_name") or "").strip()
                sc = (row.get("school") or "").strip()
                if tn or sc:
                    meta_lines[tid].append((tn, sc))

    standings = STANDINGS_BMT_2024 if year == "2024" else {}

    all_ids = set(roster.keys()) | set(existing.keys()) | set(standings.keys())

    out_rows: list[list[str]] = []
    for tid in sorted(all_ids, key=lambda x: int(x)):
        sid_map = roster.get(tid, {})
        pairs: list[tuple[int, str]] = []
        for sid in sorted(sid_map.keys()):
            bmts = sorted(sid_map[sid])
            pairs.append((sid, bmts[0]))
        sids_str = "|".join(str(p[0]) for p in pairs) if pairs else ""
        bmts_str = "|".join(p[1] for p in pairs) if pairs else ""

        ex = existing.get(tid, {})
        tn_mode, sc_mode = mode_meta(meta_lines.get(tid, []))

        tn_std, sc_std = standings.get(tid, ("", ""))
        if tn_std in ("-1", ""):
            tn_std = ""
        if sc_std in ("-1", ""):
            sc_std = ""

        if tn_mode or sc_mode:
            team_name = tn_mode or ex.get("team_name") or tn_std
            school = sc_mode or ex.get("school") or sc_std
        else:
            team_name = ex.get("team_name") or tn_std or tn_mode
            school = ex.get("school") or sc_std or sc_mode
        state = ex.get("state") or infer_state(team_name, school)

        out_rows.append([tid, team_name, sids_str, bmts_str, school, state])

    teams_path.parent.mkdir(parents=True, exist_ok=True)
    with teams_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["team_id", "team_name", "student_ids", "bmt_student_ids", "school", "state"])
        w.writerows(out_rows)

    print(f"[bmt] Wrote {len(out_rows)} teams to {teams_path}")


def _sort_tid_key(t: str) -> tuple[int, int | str]:
    ts = (t or "").strip()
    if ts.isdigit():
        return (0, int(ts))
    return (1, ts)


def sync_generic_contest(contest: str, year: str) -> str | None:
    """Return a short log line if work ran; None if skipped."""
    if contest == "bmt":
        rebuild_bmt_aggregate(year)
        return None

    results_path = CONTESTS_DIR / contest / f"year={year}" / "results.csv"
    if not results_path.exists():
        print(f"[skip] {contest}/{year}: no results.csv at {results_path}", file=sys.stderr)
        return None

    with results_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        if not headers:
            return None
        rows = list(reader)

    team_col = detect_team_column(list(headers))
    if not team_col:
        print(f"[skip] {contest}/{year}: no team_name or team column", file=sys.stderr)
        return None

    teams_dir = CONTESTS_DIR / f"{contest}-teams" / f"year={year}"
    teams_path = teams_dir / "teams.csv"

    name_to_id: dict[str, str] = {}
    id_to_row: dict[str, dict[str, str]] = {}
    teams_fieldnames: list[str] | None = None

    if teams_path.exists():
        with teams_path.open(encoding="utf-8", newline="") as tf:
            tr = csv.DictReader(tf)
            teams_fieldnames = list(tr.fieldnames or [])
            for row in tr:
                tid = (row.get("team_id") or "").strip()
                tn = normalize_team_label(row.get("team_name") or row.get("team") or "")
                if tid:
                    id_to_row[tid] = {k: (row.get(k) or "") for k in (teams_fieldnames or [])}
                if tid and tn:
                    name_to_id[normalize_team_label(tn)] = tid

    # Order of first appearance for new team names
    ordered_norm_names: list[str] = []
    seen_n = set()
    for row in rows:
        raw_t = (row.get(team_col) or "").strip()
        if not raw_t:
            continue
        norm = normalize_team_label(raw_t)
        if norm not in seen_n:
            seen_n.add(norm)
            ordered_norm_names.append(norm)

    if not ordered_norm_names:
        print(f"[skip] {contest}/{year}: no non-empty {team_col} values", file=sys.stderr)
        return None

    used_ids: set[str] = set(name_to_id.values())

    # Prefer team_id values already present in results (mode per normalized name)
    for norm in ordered_norm_names:
        if norm in name_to_id:
            continue
        bucket: list[str] = []
        if "team_id" in headers:
            for row in rows:
                if normalize_team_label(row.get(team_col) or "") != norm:
                    continue
                v = (row.get("team_id") or "").strip()
                if v:
                    bucket.append(v)
        if bucket:
            chosen = Counter(bucket).most_common(1)[0][0]
            if chosen not in used_ids:
                name_to_id[norm] = chosen
                used_ids.add(chosen)

    ints, width = parse_int_team_ids(list(used_ids))
    next_num = max(ints) + 1 if ints else 1

    for norm in ordered_norm_names:
        if norm in name_to_id:
            continue
        while True:
            if width > 0:
                candidate = str(next_num).zfill(width)
            else:
                candidate = str(next_num)
            if candidate not in used_ids:
                name_to_id[norm] = candidate
                used_ids.add(candidate)
                next_num += 1
                break
            next_num += 1

    canonical_display: dict[str, str] = {}
    for row in rows:
        raw_t = (row.get(team_col) or "").strip()
        if not raw_t:
            continue
        norm = normalize_team_label(raw_t)
        if norm not in canonical_display:
            canonical_display[norm] = raw_t

    roster: dict[str, set[int]] = defaultdict(set)
    for row in rows:
        raw_t = (row.get(team_col) or "").strip()
        if not raw_t:
            continue
        norm = normalize_team_label(raw_t)
        tid = name_to_id.get(norm, "")
        if not tid:
            continue
        try:
            roster[tid].add(int(row["student_id"]))
        except (KeyError, ValueError):
            print(f"[warn] {contest}/{year}: skip row with missing or invalid student_id", file=sys.stderr)

    if teams_fieldnames:
        out_fields = list(teams_fieldnames)
        if "team_name" in out_fields:
            out_fields[out_fields.index("team_name")] = "team"
        for col in ("team_id", "team", "student_ids"):
            if col not in out_fields:
                out_fields.append(col)
    else:
        out_fields = ["team_id", "team", "student_ids", "state"]

    team_rows_out: list[dict[str, str]] = []
    for tid in sorted(roster.keys(), key=_sort_tid_key):
        norm_names = [n for n, i in name_to_id.items() if i == tid]
        display = canonical_display.get(norm_names[0], norm_names[0]) if norm_names else ""
        base = {k: "" for k in out_fields}
        base.update(id_to_row.get(tid, {}))
        base["team_id"] = tid
        base["team"] = display or base.get("team") or base.get("team_name", "")
        base.pop("team_name", None)
        base["student_ids"] = "|".join(str(s) for s in sorted(roster[tid]))
        for k in out_fields:
            if k not in base:
                base[k] = ""
        team_rows_out.append({k: base.get(k, "") for k in out_fields})

    teams_dir.mkdir(parents=True, exist_ok=True)
    with teams_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=out_fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(team_rows_out)

    # Update results.csv: ensure team_id column after team column
    out_headers = list(headers)
    if "team_id" in out_headers:
        out_headers.remove("team_id")
    insert_at = out_headers.index(team_col) + 1
    out_headers.insert(insert_at, "team_id")

    out_rows: list[dict[str, str]] = []
    for row in rows:
        new_r = {k: row.get(k, "") for k in headers}
        raw_t = (row.get(team_col) or "").strip()
        norm = normalize_team_label(raw_t) if raw_t else ""
        new_r["team_id"] = name_to_id.get(norm, "") if norm else ""
        out_rows.append(new_r)

    with results_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=out_headers, extrasaction="ignore")
        w.writeheader()
        for r in out_rows:
            w.writerow({k: r.get(k, "") for k in out_headers})

    return f"[sync] {contest}/{year}: {len(team_rows_out)} teams -> {teams_path}"


def sync_all(year: str) -> None:
    bmt_main = CONTESTS_DIR / "bmt" / f"year={year}" / "results.csv"
    if bmt_main.exists():
        rebuild_bmt_aggregate(year)

    for entry in sorted(CONTESTS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        name = entry.name
        if name.endswith("-teams"):
            continue
        if name in TOP_LEVEL_SKIP:
            continue
        if name in BMT_SUBFOLDERS:
            continue
        if name == "bmt":
            continue
        res = entry / f"year={year}" / "results.csv"
        if not res.exists():
            continue
        msg = sync_generic_contest(name, year)
        if msg:
            print(msg)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd")

    b = sub.add_parser("bmt", help="Rebuild bmt-teams from five BMT result files")
    b.add_argument("year")

    s = sub.add_parser("sync", help="Sync teams for one contest folder")
    s.add_argument("contest", help="Folder under database/contests, e.g. cmimc, hmmt-feb")
    s.add_argument("year")

    a = sub.add_parser("sync-all", help="BMT aggregate + sync every other contest for this year")
    a.add_argument("year")

    return p


def main() -> None:
    argv = sys.argv[1:]
    if len(argv) == 1 and argv[0].isdigit():
        rebuild_bmt_aggregate(argv[0])
        return

    parser = build_parser()
    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(2)

    if args.cmd == "bmt":
        rebuild_bmt_aggregate(args.year)
    elif args.cmd == "sync":
        msg = sync_generic_contest(args.contest, args.year)
        if msg:
            print(msg)
    elif args.cmd == "sync-all":
        sync_all(args.year)
    else:
        parser.error(f"unknown command {args.cmd}")


if __name__ == "__main__":
    main()
