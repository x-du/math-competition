#!/usr/bin/env python3
"""
Build competition_data.json for the crank.html page (impact index and geographic attraction).
Reads from data.json (run build_search_data.py first) and outputs a compact JSON.
Run from repo root: python scripts/build_competition_data.py
Output: docs/competition_data.json

Optimizations: no scores (id/name only), shared names lookup, US state abbreviations.
"""
import csv
import json
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
# Most recent N editions per competition (e.g. HMMT Feb: 2023, 2024, 2025, 2026 = 4 editions)
YEARS_WINDOW = 2
MATHCOUNTS_YEARS = 6  # MathCounts: 6 most recent (middle school)
JMO_YEARS = 4  # USAJMO: 4 most recent
BAMO_8_YEARS = 6  # BAMO-8: 6 most recent (middle school)
HMMT_NOV_YEARS = 4  # HMMT November: 4 most recent
PUMAC_B_YEARS = 4  # PUMaC Division B: 4 most recent
DATA_JSON = REPO_ROOT / "docs" / "data.json"
OUTPUT_JSON = REPO_ROOT / "docs" / "competition_data.json"
CONTESTS_CSV = REPO_ROOT / "database" / "contests" / "contests.csv"

CONTESTS_WITH_CSV_STATE = {"amo", "jmo", "mathcounts-national-rank"}
MIN_STUDENTS = 1  # Include all contests (show all competitions)
EXCLUDED_CONTESTS = {"imo", "egmo", "rmm"}  # International olympiads, exclude from CII list

# Map subject tests to their main competition (for grouping)
SLUG_TO_GROUP = {
    "hmmt-feb": "hmmt-feb",
    "hmmt-feb-algebra-number-theory": "hmmt-feb",
    "hmmt-feb-combo": "hmmt-feb",
    "hmmt-feb-geometry": "hmmt-feb",
    "hmmt-nov": "hmmt-nov",
    "hmmt-nov-general": "hmmt-nov",
    "hmmt-nov-theme": "hmmt-nov",
    "pumac": "pumac",
    "pumac-algebra": "pumac",
    "pumac-combinator": "pumac",
    "pumac-geometry": "pumac",
    "pumac-number-theory": "pumac",
    "pumac-b": "pumac-b",
    "pumac-b-algebra": "pumac-b",
    "pumac-b-combinator": "pumac-b",
    "pumac-b-geometry": "pumac-b",
    "pumac-b-number-theory": "pumac-b",
    "bmt": "bmt",
    "bmt-algebra": "bmt",
    "bmt-calculus": "bmt",
    "bmt-discrete": "bmt",
    "bmt-geometry": "bmt",
    "cmimc": "cmimc",
    "cmimc-algebra": "cmimc",
    "cmimc-comb": "cmimc",
    "cmimc-geometry": "cmimc",
}

# US state full name -> 2-letter abbreviation (for smaller JSON)
STATE_TO_ABBR = {
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


def slug_to_group(slug: str) -> str:
    """Return the main competition slug (group subject tests with overall)."""
    return SLUG_TO_GROUP.get(slug, slug)


def get_window_size(group: str) -> int:
    """Return the number of most recent editions to include for this contest group."""
    if group == "mathcounts-national-rank":
        return MATHCOUNTS_YEARS
    if group == "jmo":
        return JMO_YEARS
    if group == "bamo-8":
        return BAMO_8_YEARS
    if group == "hmmt-nov":
        return HMMT_NOV_YEARS
    if group == "pumac-b":
        return PUMAC_B_YEARS
    return YEARS_WINDOW


def load_contest_websites() -> dict[str, str]:
    """Load slug -> website from contests.csv."""
    websites: dict[str, str] = {}
    with open(CONTESTS_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            slug = (row.get("folder_name") or "").strip()
            url = (row.get("website") or "").strip()
            if slug and url:
                websites[slug] = url
    return websites


def main() -> None:
    with open(DATA_JSON, encoding="utf-8") as f:
        data = json.load(f)

    students = data.get("students", [])
    slug_index = data.get("slug_index", [])

    # Collect years that have data per contest group (only editions that exist)
    group_years: dict[str, set[int]] = {}
    for s in students:
        for r in s.get("records", []):
            c_idx = r.get("c")
            if c_idx is None or c_idx >= len(slug_index):
                continue
            mr = r.get("mr") or r.get("mcp_rank")
            if mr is None:
                continue
            group = slug_to_group(slug_index[c_idx])
            y = r.get("y") or r.get("year")
            if y is not None:
                try:
                    year_val = int(y)
                    if group not in group_years:
                        group_years[group] = set()
                    group_years[group].add(year_val)
                except (ValueError, TypeError):
                    pass

    # For each group, take the N most recent editions (years with data)
    group_allowed_years: dict[str, set[int]] = {}
    for group, years in group_years.items():
        n = get_window_size(group)
        sorted_years = sorted(years, reverse=True)[:n]
        group_allowed_years[group] = set(sorted_years)

    def record_in_window(r: dict) -> bool:
        y = r.get("y") or r.get("year")
        if not y:
            return True
        try:
            year_val = int(y)
        except (ValueError, TypeError):
            return True
        c_idx = r.get("c")
        if c_idx is None or c_idx >= len(slug_index):
            return True
        group = slug_to_group(slug_index[c_idx])
        allowed = group_allowed_years.get(group)
        if allowed is None:
            return True
        return year_val in allowed

    # Build sid -> name, sid -> mcp
    sid_to_name: dict[int, str] = {s["id"]: (s.get("name") or "").strip() for s in students}
    sid_to_mcp: dict[int, float] = {s["id"]: float(s.get("mcp") or 0) for s in students}

    # Top 100 overall by MCP (from full data - MCP uses time decay)
    sorted_by_mcp = sorted(
        [s for s in students if (s.get("mcp") or 0) > 0],
        key=lambda x: x.get("mcp", 0),
        reverse=True,
    )
    top100_overall = [(s["id"], sid_to_name.get(s["id"], "")) for s in sorted_by_mcp[:100]]
    top100_ids = set(s["id"] for s in sorted_by_mcp[:100])
    sum_mcp_overall_100 = sum(sid_to_mcp[s["id"]] for s in sorted_by_mcp[:100])

    # Per-contest: best mcp_rank per student (group subject tests, most recent N editions)
    contest_to_students: dict[str, dict[int, float]] = {}
    for s in students:
        for r in s.get("records", []):
            if not record_in_window(r):
                continue
            c_idx = r.get("c")
            if c_idx is None:
                continue
            slug = slug_index[c_idx] if c_idx < len(slug_index) else ""
            if not slug:
                continue
            group = slug_to_group(slug)
            mr = r.get("mr") or r.get("mcp_rank")
            if mr is None:
                continue
            try:
                rank = float(mr)
            except (ValueError, TypeError):
                continue
            sid = s["id"]
            if group not in contest_to_students:
                contest_to_students[group] = {}
            if sid not in contest_to_students[group] or contest_to_students[group][sid] > rank:
                contest_to_students[group][sid] = rank

    # Impact index (only contests with >= MIN_STUDENTS)
    # CII = % of overall elite MCP captured by this contest's top 100 (MCP-weighted, not count)
    impact_rows = []
    for slug, student_ranks in contest_to_students.items():
        if slug in EXCLUDED_CONTESTS:
            continue
        if len(student_ranks) < MIN_STUDENTS:
            continue
        sorted_students = sorted(student_ranks.items(), key=lambda x: x[1])[:100]
        top100_contest = set(x[0] for x in sorted_students)
        overlap_ids = top100_contest & top100_ids
        overlap_count = len(overlap_ids)
        sum_mcp_overlap = sum(sid_to_mcp[sid] for sid in overlap_ids)
        n = min(100, len(sorted_students))
        pct = (sum_mcp_overlap / sum_mcp_overall_100 * 100) if sum_mcp_overall_100 > 0 else 0
        top100_ids_list = [sid for sid, _ in sorted_students]
        impact_rows.append({
            "slug": slug,
            "overlap": overlap_count,
            "n": n,
            "pct": round(pct, 1),
            "top100": top100_ids_list,
        })
    impact_rows.sort(key=lambda x: -x["pct"])

    # Build sid -> state (prefer contest-specific state for AMO/JMO/MathCounts)
    sid_to_state: dict[int, str] = {}
    for s in students:
        sid_to_state[s["id"]] = (s.get("state") or "").strip()
    for s in students:
        for r in s.get("records", []):
            st = (r.get("st") or r.get("state") or "").strip()
            if st and r.get("c") is not None:
                c = slug_index[r["c"]] if r["c"] < len(slug_index) else ""
                if c in CONTESTS_WITH_CSV_STATE:
                    sid_to_state[s["id"]] = st

    # Attraction: state counts per contest (all data, no time filter)
    attraction: dict[str, dict[str, int]] = {"__all__": {}}
    for s in students:
        state = sid_to_state.get(s["id"], "") or (s.get("state") or "").strip()
        if state:
            attraction["__all__"][state] = attraction["__all__"].get(state, 0) + 1
        for r in s.get("records", []):
            c_idx = r.get("c")
            if c_idx is None:
                continue
            slug = slug_index[c_idx] if c_idx < len(slug_index) else ""
            group = slug_to_group(slug)
            st = sid_to_state.get(s["id"], "") or (r.get("st") or r.get("state") or "").strip()
            if not st:
                continue
            if group not in attraction:
                attraction[group] = {}
            attraction[group][st] = attraction[group].get(st, 0) + 1

    # Filter attraction to contests with >= MIN_STUDENTS
    slugs_with_100 = {r["slug"] for r in impact_rows}
    attraction_filtered = {k: v for k, v in attraction.items() if k == "__all__" or k in slugs_with_100}

    # Abbreviate US state names in attraction (non-US kept as-is)
    def abbr_state(s: str) -> str:
        return STATE_TO_ABBR.get(s, s)

    attraction_compact: dict[str, dict[str, int]] = {}
    for contest, state_counts in attraction_filtered.items():
        attraction_compact[contest] = {abbr_state(st): cnt for st, cnt in state_counts.items()}

    # Shared names lookup: collect all unique student ids from top100s
    all_top100_ids: set[int] = set()
    for row in impact_rows:
        all_top100_ids.update(row["top100"])
    all_top100_ids.update(sid for sid, _ in top100_overall)
    names_lookup: dict[str, str] = {str(sid): sid_to_name.get(sid, "") for sid in all_top100_ids}

    # Contest list for dropdown (sorted by display name)
    slugs = ["__all__"] + sorted(
        sorted(set(attraction_filtered.keys()) - {"__all__"}),
        key=lambda s: slug_to_display(s),
    )

    top100_overall_ids = [sid for sid, _ in top100_overall]

    # Contest websites from contests.csv (use group slug for subject tests)
    raw_websites = load_contest_websites()
    contest_websites: dict[str, str] = {}
    for slug in set(attraction_filtered.keys()) | {r["slug"] for r in impact_rows}:
        if slug == "__all__":
            continue
        group = slug_to_group(slug)
        if group in raw_websites:
            contest_websites[slug] = raw_websites[group]

    output = {
        "names": names_lookup,
        "impact": impact_rows,
        "attraction": attraction_compact,
        "contests": slugs,
        "top100_overall": top100_overall_ids,
        "contest_websites": contest_websites,
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, separators=(",", ":"), ensure_ascii=False)

    size_kb = OUTPUT_JSON.stat().st_size / 1024
    print(f"Wrote {len(impact_rows)} impact rows, {len(attraction_filtered)} contests to {OUTPUT_JSON} ({size_kb:.1f} KB)")


def slug_to_display(slug: str) -> str:
    """Human-readable contest name for sorting."""
    names = {
        "hmmt-feb": "HMMT February",
        "hmmt-nov": "HMMT November",
        "pumac": "PUMaC Division A",
        "pumac-b": "PUMaC Division B",
        "cmimc": "CMIMC",
        "arml": "ARML",
        "bmt": "BMT",
        "dmm": "DMM",
        "cmm": "CMM",
        "bamo-12": "BAMO-12",
        "bamo-8": "BAMO-8",
        "mmaths": "MMATHS",
        "brumo-a": "BrUMO Division A",
        "amo": "USAMO",
        "jmo": "USAJMO",
        "mathcounts-national-rank": "MathCounts National",
        "imo": "IMO",
        "egmo": "EGMO",
        "rmm": "RMM",
        "mpfg": "MPFG",
        "mpfg-olympiad": "MPFG Olympiad",
    }
    return names.get(slug) or slug.replace("-", " ").title()


if __name__ == "__main__":
    main()
