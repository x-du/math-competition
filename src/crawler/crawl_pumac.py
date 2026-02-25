#!/usr/bin/env python3
"""
Crawler for PUMaC individual results (Division A or B).

The results page is a <pre> block with fixed-width plain-text columns.

Sections within the page:
  Algebra A / Geometry A / Number Theory A / Combinatorics A
    header line:  "    Name               Team                    Score   1 … 8"
    data columns: rank(3) | space(1) | name(19) | team(24) | score …

  Individual Rankings A
    header line:  "    Name                   Team                           Total   Finals …"
    data columns: rank(3) | space(1) | name(23) | team(31) | total | finals | test1 | test2

Writes:
  - database/students/students.csv  (merged with existing)
  - database/students/teams.csv     (merged with existing)
  - database/contests/pumac/year={year}/results_{division}.csv

Usage:
  python crawl_pumac.py           # 2025, Division A
  python crawl_pumac.py 2024
  python crawl_pumac.py 2025 --division B
"""

import argparse
import csv
import re
import urllib.request
from pathlib import Path


# ── Constants ──────────────────────────────────────────────────────────────────

SUBJECT_SECTIONS: dict[str, str] = {
    "algebra":       "ALG",
    "geometry":      "GEO",
    "number theory": "NTY",
    "combinatorics": "CMB",
}

ABBR_TO_COL: dict[str, str] = {
    "ALG": "algebra_score",
    "GEO": "geometry_score",
    "NTY": "number_theory_score",
    "CMB": "combinatorics_score",
}

# Fixed column offsets for subject-round lines.
# "    Name               Team                    Score   1 … 8"
SUBJ_NAME_START = 4
SUBJ_NAME_END   = 23   # exclusive  (name = 19 chars)
SUBJ_TEAM_START = 23
SUBJ_TEAM_END   = 46   # exclusive  (team = 23 chars, score starts at 46)

# Fixed column offsets for Individual Rankings lines.
# "    Name                   Team                           Total   Finals …"
RANK_NAME_START = 4
RANK_NAME_END   = 27   # exclusive
RANK_TEAM_START = 27
RANK_TEAM_END   = 58   # exclusive → total/finals/tests follow at 58+


# ── HTTP helpers ───────────────────────────────────────────────────────────────

def pumac_url(year: int, division: str = "A") -> str:
    return f"https://pumac.princeton.edu/results/{year}/Individuals{division}.html"


def fetch_pre_text(url: str) -> str:
    """Fetch the URL and return the plain text inside the first <pre> block."""
    with urllib.request.urlopen(url) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    m = re.search(r"<pre[^>]*>(.*?)</pre>", html, re.DOTALL | re.IGNORECASE)
    block = m.group(1) if m else html
    # Strip any remaining HTML tags (links, breaks, headings, etc.).
    text = re.sub(r"<[^>]+>", "", block)
    text = (
        text.replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&nbsp;", " ")
    )
    return text


# ── Page structure detection ───────────────────────────────────────────────────

def detect_section(line: str) -> str | None:
    """
    If the line is a section heading return the section key
    ('algebra', 'geometry', 'number theory', 'combinatorics', 'rankings').
    Otherwise return None.
    """
    stripped = line.strip()
    lower = stripped.lower()
    for keyword, _ in SUBJECT_SECTIONS.items():
        if lower.startswith(keyword):
            return keyword
    if "individual rankings" in lower or lower.startswith("rankings"):
        return "rankings"
    return None


DATA_LINE_RE = re.compile(r"^\s{0,2}(\d{1,3})\s")


def is_data_line(line: str) -> bool:
    return bool(DATA_LINE_RE.match(line))


# ── Per-subject section parser ─────────────────────────────────────────────────

def parse_subject_line(line: str, subject_abbr: str) -> dict | None:
    """
    Parse one data line from a per-subject section.
    Returns dict(rank, name, team, subject_abbr, score) or None.
    """
    if len(line) < SUBJ_TEAM_END:
        line = line.ljust(SUBJ_TEAM_END)
    rank_str = line[:SUBJ_NAME_START].strip()
    name = line[SUBJ_NAME_START:SUBJ_NAME_END].strip()
    team = line[SUBJ_TEAM_START:SUBJ_TEAM_END].strip()
    rest = line[SUBJ_TEAM_END:].strip()

    if not name or not team:
        return None
    try:
        rank = int(rank_str)
    except ValueError:
        rank = 0
    score_m = re.match(r"([\d.]+)", rest)
    if not score_m:
        return None
    try:
        score = float(score_m.group(1))
    except ValueError:
        return None
    return {"rank": rank, "name": name, "team": team, "subject_abbr": subject_abbr, "score": score}


# ── Individual Rankings section parser ────────────────────────────────────────

# Matches one test-score cell: "18.403 (ALG)" or "15.837 (NTY)"
TEST_SCORE_RE = re.compile(r"([\d.]+)\s*\(([A-Z]+)\)")


def parse_rankings_line(line: str) -> dict | None:
    """
    Parse one data line from the Individual Rankings section.
    Returns dict(rank, name, team, total_score, finals_score, <subject>_score…) or None.
    """
    if len(line) < RANK_TEAM_END:
        line = line.ljust(RANK_TEAM_END)
    rank_str = line[:RANK_NAME_START].strip()
    name = line[RANK_NAME_START:RANK_NAME_END].strip()
    team = line[RANK_TEAM_START:RANK_TEAM_END].strip()
    rest = line[RANK_TEAM_END:].strip()

    if not name or not team:
        return None
    try:
        rank = int(rank_str)
    except ValueError:
        rank = 0

    # rest looks like: "3.723       19     18.403 (ALG)   15.837 (NTY)"
    tokens = rest.split()
    if len(tokens) < 2:
        return None
    try:
        total = float(tokens[0])
    except ValueError:
        return None
    try:
        finals = int(tokens[1])
    except ValueError:
        finals = 0

    test_scores: dict[str, float] = {}
    for m in TEST_SCORE_RE.finditer(rest):
        col = ABBR_TO_COL.get(m.group(2))
        if col:
            try:
                test_scores[col] = float(m.group(1))
            except ValueError:
                pass

    return {
        "rank": rank,
        "name": name,
        "team": team,
        "total_score": total,
        "finals_score": finals,
        **test_scores,
    }


# ── Main page parser ───────────────────────────────────────────────────────────

def parse_pumac_page(text: str) -> tuple[list[dict], list[dict]]:
    """
    Parse the full PUMaC Individuals page text.

    Returns:
      subject_results  – list of {rank, name, team, subject_abbr, score}
      ranking_results  – list of {rank, name, team, total_score, finals_score,
                                  algebra_score?, geometry_score?,
                                  number_theory_score?, combinatorics_score?}
    """
    subject_results: list[dict] = []
    ranking_results: list[dict] = []
    current_section: str | None = None

    for line in text.splitlines():
        section = detect_section(line)
        if section is not None:
            current_section = section
            continue

        if current_section is None or not is_data_line(line):
            continue

        if current_section == "rankings":
            row = parse_rankings_line(line)
            if row:
                ranking_results.append(row)
        else:
            abbr = SUBJECT_SECTIONS.get(current_section)
            if abbr:
                row = parse_subject_line(line, abbr)
                if row:
                    subject_results.append(row)

    return subject_results, ranking_results


# ── Student / team loading and merging (mirrors crawl_hmmt_feb.py) ─────────────

def load_existing_students_and_teams(
    students_path: Path, teams_path: Path
) -> tuple[
    dict[str, int],
    dict[str, int],
    list[tuple[int, str, str, str]],
    list[tuple[int, str]],
    int,
    int,
    dict[int, str],
]:
    """
    Load existing students.csv and teams.csv.
    Student identity is by name only: name -> student_id.
    Returns (student_name_to_id, team_name_to_id, student_list, team_list,
             next_sid, next_tid, team_id_to_associated).
    """
    team_id_to_name: dict[int, str] = {}
    team_name_to_id: dict[str, int] = {}
    team_id_to_associated: dict[int, str] = {}
    student_list: list[tuple[int, str, str, str]] = []
    student_name_to_id: dict[str, int] = {}
    next_sid, next_tid = 1, 1

    if teams_path.exists():
        with open(teams_path, encoding="utf-8") as f:
            r = csv.DictReader(f)
            has_associated = "associated_team_ids" in (r.fieldnames or [])
            for row in r:
                tid = int(row["team_id"])
                tname = (row.get("team_name") or "").strip()
                team_id_to_name[tid] = tname
                if tname:
                    team_name_to_id[tname] = tid
                if has_associated:
                    assoc_raw = (row.get("associated_team_ids") or "").strip()
                    if assoc_raw:
                        team_id_to_associated[tid] = assoc_raw
                next_tid = max(next_tid, tid + 1)

    if students_path.exists():
        with open(students_path, encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                sid = int(row["student_id"])
                name = (row.get("student_name", row.get("name", "")) or "").strip()
                if not name:
                    continue
                team_ids_raw = row.get("team_ids", row.get("team_id", ""))
                team_ids_str = "|".join(
                    str(int(x.strip()))
                    for x in str(team_ids_raw).split("|")
                    if x.strip()
                )
                alias = (row.get("alias") or "").strip()
                student_list.append((sid, name, team_ids_str, alias))
                student_name_to_id[name] = sid
                if alias:
                    student_name_to_id[alias] = sid
                next_sid = max(next_sid, sid + 1)

    team_list = [
        (tid, tname)
        for tname, tid in sorted(team_name_to_id.items(), key=lambda x: x[1])
    ]
    return (
        student_name_to_id,
        team_name_to_id,
        student_list,
        team_list,
        next_sid,
        next_tid,
        team_id_to_associated,
    )


def build_teams_and_students(
    parsed_rows: list[dict],
    existing_student_name_to_id: dict[str, int],
    existing_team_name_to_id: dict[str, int],
    existing_student_list: list[tuple[int, str, str, str]],
    existing_team_list: list[tuple[int, str]],
    existing_team_id_to_associated: dict[int, str],
    next_sid: int,
    next_tid: int,
) -> tuple[
    list[tuple[int, str]],
    list[tuple[int, str, str, str]],
    dict[str, int],
    dict[int, str],
]:
    """
    Merge parsed (name, team) rows into the existing student/team tables.
    Same name = same person; team_ids accumulate all teams for that name.
    Returns (team_list, student_list, student_name_to_id, team_id_to_associated).
    """
    student_name_to_id = dict(existing_student_name_to_id)
    team_name_to_id = dict(existing_team_name_to_id)
    team_id_to_associated = dict(existing_team_id_to_associated)

    sid_to_name_alias: dict[int, tuple[str, str]] = {}
    sid_to_team_ids: dict[int, set[int]] = {}
    for sid, name, team_ids_str, alias in existing_student_list:
        sid_to_name_alias[sid] = (name, alias)
        teams: set[int] = set()
        for tok in str(team_ids_str).split("|"):
            try:
                teams.add(int(tok.strip()))
            except ValueError:
                pass
        sid_to_team_ids[sid] = teams

    new_team_names: set[str] = set()

    for row in parsed_rows:
        name = (row.get("name") or "").strip()
        team = (row.get("team") or "").strip()
        if not name or not team:
            continue

        if name not in student_name_to_id:
            if team not in team_name_to_id:
                team_name_to_id[team] = next_tid
                next_tid += 1
                new_team_names.add(team)
            tid = team_name_to_id[team]
            student_name_to_id[name] = next_sid
            sid = next_sid
            next_sid += 1
            sid_to_name_alias[sid] = (name, "")
            sid_to_team_ids[sid] = {tid}
        else:
            sid = student_name_to_id[name]
            if team not in team_name_to_id:
                team_name_to_id[team] = next_tid
                next_tid += 1
                new_team_names.add(team)
            tid = team_name_to_id[team]
            sid_to_team_ids.setdefault(sid, set()).add(tid)

    # Append newly seen teams to the team list (preserves existing ordering).
    team_list = list(existing_team_list)
    for tname in sorted(new_team_names, key=lambda t: team_name_to_id[t]):
        tid = team_name_to_id[tname]
        team_list.append((tid, tname))
        team_id_to_associated.setdefault(tid, "")

    student_list: list[tuple[int, str, str, str]] = []
    for sid in sorted(sid_to_name_alias):
        name, alias = sid_to_name_alias[sid]
        teams = sid_to_team_ids.get(sid, set())
        team_ids_str = "|".join(str(t) for t in sorted(teams)) if teams else ""
        student_list.append((sid, name, team_ids_str, alias))

    return team_list, student_list, student_name_to_id, team_id_to_associated


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl PUMaC individual results.")
    parser.add_argument("year", type=int, nargs="?", default=2025, help="Year (e.g. 2025)")
    parser.add_argument(
        "--division", default="A", choices=["A", "B"],
        help="Division A or B (default: A)"
    )
    args = parser.parse_args()
    year, division = args.year, args.division

    base = Path(__file__).resolve().parent.parent.parent
    students_path = base / "database" / "students" / "students.csv"
    teams_path    = base / "database" / "students" / "teams.csv"
    results_path  = (
        base / "database" / "contests" / "pumac"
        / f"year={year}" / f"results_{division}.csv"
    )

    students_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.parent.mkdir(parents=True, exist_ok=True)

    url = pumac_url(year, division)
    print("Fetching", url)
    text = fetch_pre_text(url)

    subject_results, ranking_results = parse_pumac_page(text)
    print(
        f"Parsed {len(subject_results)} named subject-round entries, "
        f"{len(ranking_results)} overall ranking rows"
    )

    # Collect all unique named entries for student/team ID assignment.
    all_named: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for r in ranking_results:
        k = (r["name"], r["team"])
        if k not in seen:
            all_named.append({"name": r["name"], "team": r["team"]})
            seen.add(k)
    for r in subject_results:
        k = (r["name"], r["team"])
        if k not in seen:
            all_named.append({"name": r["name"], "team": r["team"]})
            seen.add(k)

    (
        existing_key_to_sid,
        existing_team_name_to_id,
        existing_student_list,
        existing_team_list,
        next_sid,
        next_tid,
        existing_team_id_to_associated,
    ) = load_existing_students_and_teams(students_path, teams_path)
    print(
        f"Loaded {len(existing_student_list)} existing students, "
        f"{len(existing_team_list)} existing teams"
    )

    (
        team_list,
        student_list,
        key_to_sid,
        team_id_to_associated,
    ) = build_teams_and_students(
        all_named,
        existing_key_to_sid,
        existing_team_name_to_id,
        existing_student_list,
        existing_team_list,
        existing_team_id_to_associated,
        next_sid,
        next_tid,
    )
    print(f"Merged: {len(team_list)} teams, {len(student_list)} students")

    # Write teams.csv.
    with open(teams_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["team_id", "team_name", "associated_team_ids"])
        for team_id, team_name in team_list:
            if (team_name or "").strip():
                assoc = (team_id_to_associated.get(team_id) or "").strip()
                w.writerow([team_id, team_name, assoc])
    print("Wrote", teams_path)

    # Write students.csv.
    with open(students_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["student_id", "student_name", "team_ids", "alias"])
        for student_id, name, team_ids_str, alias in student_list:
            w.writerow([student_id, name, team_ids_str or "", alias or ""])
    print("Wrote", students_path)

    # Write results CSV for this year/division (Individual Rankings only).
    with open(results_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "student_id", "student_name", "year", "division",
            "rank", "total_score", "finals_score",
        ])
        for row in ranking_results:
            name = row["name"]
            if name not in key_to_sid:
                continue
            student_id = key_to_sid[name]
            w.writerow([
                student_id,
                row["name"],
                year,
                division,
                row["rank"],
                row["total_score"],
                row.get("finals_score", ""),
            ])
    print("Wrote", results_path)


if __name__ == "__main__":
    main()
