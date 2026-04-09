#!/usr/bin/env python3
"""
Build a single JSON file from database CSVs for the student search frontend.
Run from repo root: python scripts/build_search_data.py
Output: docs/data.json
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATABASE = REPO_ROOT / "database"
STUDENTS_CSV = DATABASE / "students" / "students.csv"
CONTESTS_DIR = DATABASE / "contests"
CONTESTS_CSV = CONTESTS_DIR / "contests.csv"
OUTPUT_JSON = REPO_ROOT / "docs" / "data.json"

CONTESTS_SKIP_FOR_SEARCH = {
    "mathcounts-national",
    "mk-national",  # Record only (statement info); not shown on website, no MCP
}

BMT_CONTESTS = {"bmt", "bmt-algebra", "bmt-calculus", "bmt-discrete", "bmt-geometry"}
MPFG_SLUGS = {"mpfg", "mpfg-olympiad", "egmo"}  # Gender-restricted: count toward MCP-W only
MATHCOUNTS_SLUG = "mathcounts-national-rank"
# Contests where state comes from results.csv (not students.csv): the state the student
# represented at that competition, which may differ from their current state.
CONTESTS_WITH_CSV_STATE = {MATHCOUNTS_SLUG, "amo", "jmo"}
GRAND_SLAM_SLUGS = {"imo", "egmo", "rmm"}  # Award-based points: Gold=100%, Silver=75%, Bronze=50%

# US states: full name -> USPS abbreviation. Exported in data.json as us_state_lookup (abbr -> full).
STATE_TO_ABBR: dict[str, str] = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY",
}
US_STATE_ABBRS = frozenset(STATE_TO_ABBR.values())
ABBR_TO_FULL: dict[str, str] = {abbr: full for full, abbr in STATE_TO_ABBR.items()}


def compress_record_state(raw: str) -> str:
    """Store USPS code for US states/proper DC; keep full string for non-US (e.g. provinces)."""
    s = (raw or "").strip()
    if not s:
        return ""
    if s in STATE_TO_ABBR:
        return STATE_TO_ABBR[s]
    su = s.upper()
    if len(su) == 2 and su in US_STATE_ABBRS:
        return su
    return s


K_STEEPNESS = 3

# MCP v2: (competition_size_N, min_pts) per (slug, year).
# N = total participants; min_pts = 10 for open, higher for selective.
# Each slug maps to { year: (N, min_pts) }; use "default" for years not explicitly listed.
# Subject tests inherit from parent (e.g. hmmt-feb-algebra-number-theory -> hmmt-feb).
# See docs/articles/mcp.md for source.
MCP_V2_PARAMS = {
    "hmmt-feb": {"default": (800, 100)},
    "hmmt-nov": {"default": (720, 10)},
    "pumac": {"default": (180, 10)},
    "pumac-b": {"default": (180, 10)},
    "bmt": {"default": (630, 10), 2025: (630, 10), 2023:(270, 10)},
    "arml": {"default": (1600, 10)},
    "amo": {"default": (280, 200)},
    "jmo": {"default": (220, 200)},
    "cmimc": {"default": (200, 10)},
    "bamo-12": {"default": (240, 10)},
    "bamo-8": {"default": (420, 10)},
    "mathcounts-national-rank": {"default": (224, 100)},
    "mpfg": {"default": (275, 100)},
    "mpfg-olympiad": {"default": (75, 100)},
    "mmaths": {"default": (750, 10)},
    "dmm": {"default": (270, 10)},
    "cmm": {"default": (60, 10)},
    "brumo-a": {"default": (300, 10)},
}


def get_mcp_v2_params(slug: str, year: str) -> tuple[int | None, int | None]:
    """Return (N, min_pts) for MCP v2. Returns (None, None) if not in map (fallback to v1)."""
    base_slug = slug
    if slug not in MCP_V2_PARAMS:
        if slug.startswith("hmmt-feb-"):
            base_slug = "hmmt-feb"
        elif slug.startswith("hmmt-nov-"):
            base_slug = "hmmt-nov"
        elif slug.startswith("pumac-b-"):
            base_slug = "pumac-b"
        elif slug.startswith("pumac-") and slug != "pumac-b":
            base_slug = "pumac"
        elif slug.startswith("bmt-"):
            base_slug = "bmt"
        elif slug.startswith("cmimc-"):
            base_slug = "cmimc"
        else:
            return (None, None)

    params = MCP_V2_PARAMS[base_slug]
    try:
        y = int(year)
    except (ValueError, TypeError):
        y = None
    if isinstance(params, dict):
        if y is not None and y in params:
            return params[y]
        return params.get("default", (None, None))
    return (None, None)


GRAND_SLAM_AWARD_MULTIPLIERS = {
    "gold": 1.0,
    "silver": 0.75,
    "bronze": 0.50,
}


def compute_grand_slam_mcp_points(award: str, tier: int, weight: float = 1.0) -> int | None:
    """Grand Slam: points by medal. Gold=100%, Silver=75%, Bronze=50%. Returns None if no recognized award.
    Looks for 'gold', 'silver', or 'bronze' in the award text (case-insensitive). Handles variants like 'Gold Medal'."""
    if not award:
        return None
    a = award.strip().lower()
    for key, mult in GRAND_SLAM_AWARD_MULTIPLIERS.items():
        if key in a:
            return round(tier * weight * mult)
    return None


def compute_mcp_points(
    mcp_rank: float,
    N: int,
    tier: int,
    weight: float = 1.0,
    min_pts: float | None = None,
) -> int:
    """MCP v2 power-law: rank 1 -> max_pts, rank N -> min_pts.
    If min_pts is None (v1 fallback), use 50% of max_pts."""
    max_pts = tier * weight
    if min_pts is None:
        min_pts = tier * 0.5 * weight
    if N <= 1:
        return round(max_pts)
    return round(min_pts + (max_pts - min_pts) * ((N - mcp_rank) / (N - 1)) ** K_STEEPNESS)


def get_time_weight(year: str, slug: str, current_year: int) -> float:
    """Time decay: 100% current year, 50% per year older. No decay for MathCounts."""
    if slug == MATHCOUNTS_SLUG:
        return 1.0
    try:
        y = int(year)
    except (ValueError, TypeError):
        return 0.0
    years_ago = current_year - y
    if years_ago < 0 or years_ago > 3:
        return 0.0
    return 0.5 ** years_ago


def humanize_contest(slug: str) -> str:
    """Turn contest slug into title, e.g. hmmt-feb-geometry -> HMMT Feb Geometry."""
    parts = slug.split("-")
    known_acronyms = {"hmmt", "pumac", "arml", "amc", "aime", "usamo", "mathcounts", "cmimc", "imo", "egmo", "rmm"}
    out = []
    for p in parts:
        if p.lower() in known_acronyms:
            out.append(p.upper())
        else:
            out.append(p.capitalize())
    return " ".join(out)


def load_contests():
    """Load contests.csv -> ({ folder_name: { contest_name, description, website } }, [folder_name order])."""
    by_slug = {}
    order = []
    if not CONTESTS_CSV.exists():
        return by_slug
    with open(CONTESTS_CSV, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            folder = (row.get("folder_name") or "").strip()
            if not folder:
                continue
            if folder not in by_slug:
                order.append(folder)
            tier_str = (row.get("mcp_tier") or "").strip()
            weight_str = (row.get("mcp_weight") or "").strip()
            by_slug[folder] = {
                "contest_name": (row.get("contest_name") or "").strip(),
                "description": (row.get("description") or "").strip(),
                "website": (row.get("website") or "").strip(),
                "mcp_tier": int(tier_str) if tier_str else None,
                "mcp_weight": float(weight_str) if weight_str else None,
            }
    return by_slug, order


def load_students() -> dict:
    """Load students.csv -> { student_id: { name, aliases (may be empty), state, gender, ... } }."""
    by_id = {}
    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            sid = row["student_id"].strip()
            if not sid:
                continue
            try:
                sid = int(sid)
            except ValueError:
                continue
            name = (row.get("student_name") or "").strip()
            state = (row.get("state") or "").strip()
            alias = (row.get("alias") or "").strip()
            aliases = [a.strip() for a in alias.split("|") if a.strip()] if alias else []
            gender = (row.get("gender") or "").strip().lower() or "male"
            grade_in_2026 = (row.get("grade_in_2026") or "").strip()
            by_id[sid] = {"name": name, "aliases": aliases, "state": state, "gender": gender, "grade_in_2026": grade_in_2026 or None}
    return by_id


def collect_result_files() -> list:
    """Return list of (contest_slug, year, path) for every result/competitors CSV.
    Includes all contest dirs (e.g. mathcounts-national-rank, hmmt-feb, pumac, etc.)."""
    out = []
    for contest_dir in sorted(CONTESTS_DIR.iterdir()):
        if not contest_dir.is_dir():
            continue
        slug = contest_dir.name
        for year_dir in sorted(contest_dir.iterdir()):
            if not year_dir.is_dir() or not year_dir.name.startswith("year="):
                continue
            year = year_dir.name.replace("year=", "")
            for csv_path in sorted(year_dir.glob("**/*.csv")):
                out.append((slug, year, csv_path))
    return out


def main() -> None:
    students = load_students()
    contests, contest_order = load_contests()
    records_by_id = {}
    contest_year_files = {}  # slug -> { year -> filename or [filenames] }

    result_files = collect_result_files()

    # Determine the most recent year per contest (for time-decay)
    max_year_by_slug = {}
    for slug, year, _ in result_files:
        try:
            y = int(year)
        except ValueError:
            continue
        if slug not in max_year_by_slug or y > max_year_by_slug[slug]:
            max_year_by_slug[slug] = y

    for slug, year, csv_path in result_files:
        if slug in CONTESTS_SKIP_FOR_SEARCH:
            continue
        contest_info = contests.get(slug, {})
        contest_title = (contest_info.get("contest_name") or "").strip() or humanize_contest(slug)
        mcp_tier = contest_info.get("mcp_tier")
        mcp_weight = contest_info.get("mcp_weight")

        if slug not in contest_year_files:
            contest_year_files[slug] = {}
        if year not in contest_year_files[slug]:
            contest_year_files[slug][year] = []
        contest_year_files[slug][year].append(csv_path.name)
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        if not rows:
            continue

        # MCP v2: N = competition size; min_pts from selection. Fallback: N = awardees, min_pts = 50% of max.
        v2_N, v2_min_pts = get_mcp_v2_params(slug, year)
        if v2_N is not None and v2_min_pts is not None:
            N = v2_N
            min_pts_for_mcp = v2_min_pts
        else:
            N = sum(1 for r in rows if (r.get("mcp_rank") or "").strip())
            min_pts_for_mcp = None

        for row in rows:
            if slug in BMT_CONTESTS:
                mcp_rank_str = (row.get("mcp_rank") or "").strip()
                if not mcp_rank_str:
                    continue
                try:
                    mcp_rank_val = float(mcp_rank_str)
                except (ValueError, TypeError):
                    continue
                if mcp_rank_val > 0.2 * N:
                    continue
            sid = row.get("student_id") or row.get("student_id ")
            if sid is not None:
                sid = str(sid).strip()
            if not sid:
                continue
            try:
                sid = int(sid)
            except ValueError:
                continue
            record = {
                "year": year,
                "contest_slug": slug,
            }
            skip_keys = {"student_id", "student_id ", "student_name", "state"}
            # Don't expose school from AMO/JMO results on the website (still in .csv)
            if slug in ("amo", "jmo"):
                skip_keys = skip_keys | {"school"}
            # Don't expose team from ARML/MMATHS results on the website (still in .csv)
            if slug in ("arml", "mmaths"):
                skip_keys = skip_keys | {"team"}
            # Don't expose team_name from DMM results on the website (still in .csv)
            if slug == "dmm":
                skip_keys = skip_keys | {"team_name"}
            for k, v in row.items():
                if k is None:
                    continue
                k = k.strip()
                if k and k not in skip_keys:
                    if v is not None and str(v).strip() != "":
                        record[k] = v.strip() if isinstance(v, str) else v

            # For MATHCOUNTS, USAMO, USJMO: store state from the CSV (not students.csv) so we show
            # the state the student represented at that competition, which may differ from their
            # current state in students.csv.
            if slug in CONTESTS_WITH_CSV_STATE:
                state_val = (row.get("state") or "").strip()
                if state_val:
                    record["state"] = compress_record_state(state_val)

            # Compute mcp_points from mcp_rank if MCP-eligible
            mcp_rank_str = (row.get("mcp_rank") or "").strip()
            if mcp_tier and mcp_weight:
                pts = None
                if slug in GRAND_SLAM_SLUGS:
                    award = (row.get("award") or "").strip()
                    pts = compute_grand_slam_mcp_points(award, mcp_tier, mcp_weight)
                if pts is None and mcp_rank_str and N > 0:
                    mcp_rank = float(mcp_rank_str)
                    pts = compute_mcp_points(
                        mcp_rank, N, mcp_tier, mcp_weight, min_pts=min_pts_for_mcp
                    )
                if pts is not None:
                    record["mcp_points"] = pts
                    tw = get_time_weight(year, slug, max_year_by_slug.get(slug, 2026))
                    contrib = round(pts * tw, 2)
                    if contrib > 0:
                        record["mcp_contrib"] = int(contrib) if contrib == int(contrib) else contrib

            if sid not in records_by_id:
                records_by_id[sid] = []
            recs = records_by_id[sid]
            key = (record["contest_slug"], record["year"])
            if any((r.get("contest_slug"), r.get("year")) == key for r in recs):
                continue
            recs.append(record)
            if sid not in students:
                name = (row.get("student_name") or "").strip()
                state = (row.get("state") or "").strip()
                students[sid] = {"name": name or f"Student {sid}", "aliases": [], "state": state, "gender": "male", "grade_in_2026": None}

    # Normalize any record-level state (US -> abbreviation; non-US unchanged)
    for recs in records_by_id.values():
        for r in recs:
            if r.get("state"):
                r["state"] = compress_record_state(r["state"])

    def infer_state_from_records(records: list[dict]) -> str:
        """Best-effort fallback: first non-empty state on a record (already USPS abbr for US)."""
        for r in records:
            state = (r.get("state") or "").strip()
            if state:
                return state
        return ""

    result_students = []
    for sid in sorted(records_by_id.keys()):
        recs = records_by_id[sid]
        recs.sort(key=lambda r: (r.get("year", ""), r.get("contest", "")), reverse=True)
        info = students.get(sid, {"name": f"Student {sid}", "aliases": [], "state": "", "gender": "male", "grade_in_2026": None})
        state = (info.get("state") or "").strip() or infer_state_from_records(recs)
        state = compress_record_state(state) if state else ""

        # Compute MCP and MCP-W totals with time decay
        mcp_total = 0.0
        mcp_w_extra = 0.0
        for r in recs:
            pts = r.get("mcp_points")
            if not pts:
                continue
            slug = r.get("contest_slug", "")
            tw = get_time_weight(r.get("year", ""), slug, max_year_by_slug.get(slug, 2026))
            if tw <= 0:
                continue
            weighted = pts * tw
            if slug in MPFG_SLUGS:
                mcp_w_extra += weighted
            else:
                mcp_total += weighted

        gender = (info.get("gender") or "male").strip().lower() or "male"
        student_entry = {
            "id": sid,
            "name": info["name"],
            "state": state,
            "gender": gender,
            "grade_in_2026": info.get("grade_in_2026"),
            "mcp": round(mcp_total, 2),
            "records": recs,
        }
        aliases = info.get("aliases") or []
        if aliases:
            student_entry["aliases"] = aliases
        if gender == "female" or mcp_w_extra > 0:
            student_entry["mcp_w"] = round(mcp_total + mcp_w_extra, 2)

        result_students.append(student_entry)

    # Normalize contest_year_files: single file -> string, multiple -> array
    for slug in contest_year_files:
        for year in contest_year_files[slug]:
            files = contest_year_files[slug][year]
            if len(files) == 1:
                contest_year_files[slug][year] = files[0]
            # else keep as list for multiple files

    # Build slug_index and replace contest_slug strings with compact numeric indices
    slug_set = set()
    for s in result_students:
        for r in s["records"]:
            slug_set.add(r["contest_slug"])
    slug_index = sorted(slug_set)
    slug_to_idx = {s: i for i, s in enumerate(slug_index)}
    for s in result_students:
        for r in s["records"]:
            r["c"] = slug_to_idx[r.pop("contest_slug")]

    # Shorten record keys; key_map maps short -> long for frontend hydration.
    # Student object keys use the same map (nm, rec, st, …).
    KEY_MAP = {
        "y": "year", "rk": "rank", "sc": "score", "aw": "award",
        "dv": "division", "ts": "total_score", "tn": "team_name",
        "sh": "school", "gr": "grade", "tm": "team", "pz": "prize",
        "pl": "place", "su": "subject", "si": "site",
        "mr": "mcp_rank", "mp": "mcp_points", "mc": "mcp_contrib",
        "fs": "finals_score", "as": "algebra_score", "gs": "geometry_score",
        "cs": "combinatorics_score", "ge": "general_score", "th": "theme_score",
        "ir": "international_rank", "ur": "us_rank", "bi": "bmt_student_id",
        "cn": "club_name", "t1": "test1", "t2": "test2", "tt": "total",
        "qa": "q10", "st": "state",
        "nm": "name", "gd": "gender", "g26": "grade_in_2026",
        "rec": "records", "al": "aliases", "mw": "mcp_w",
    }
    long_to_short = {v: k for k, v in KEY_MAP.items()}
    for s in result_students:
        for r in s["records"]:
            for long_key in list(r.keys()):
                if long_key in long_to_short:
                    r[long_to_short[long_key]] = r.pop(long_key)
    for s in result_students:
        for long_key in list(s.keys()):
            if long_key in long_to_short:
                s[long_to_short[long_key]] = s.pop(long_key)

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    # Write branch.json for csv-viewer to fetch from current branch
    branch = "main"
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            branch = result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    with open(REPO_ROOT / "docs" / "branch.json", "w", encoding="utf-8") as f:
        json.dump({"branch": branch}, f)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        # Student "st" and record "st" (→ state): USPS 2-letter for US; full string if not US. Client expands via us_state_lookup.
        json.dump(
            {
                "slug_index": slug_index,
                "key_map": KEY_MAP,
                "us_state_lookup": ABBR_TO_FULL,
                "students": result_students,
                "contests": contests,
                "contest_year_files": contest_year_files,
                "contest_order": contest_order,
            },
            f,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    print(f"Wrote {len(result_students)} students with records to {OUTPUT_JSON}")

    # Build competition_data.json for crank.html
    try:
        subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "build_competition_data.py")],
            cwd=REPO_ROOT,
            check=True,
            timeout=30,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass  # Non-fatal; crank page can use stale competition_data.json


if __name__ == "__main__":
    main()
