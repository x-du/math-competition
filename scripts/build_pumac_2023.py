#!/usr/bin/env python3
"""
Build PUMaC 2023 results (Individual Rankings A + 4 subjects) from the official page.
Uses (name, state) for student identity; infers state from team when possible.
Adds new students to database/students/students.csv.

Usage (from repo root):
    python scripts/build_pumac_2023.py

Reads: https://pumac.princeton.edu/results/2023/IndividualsA.html
Writes:
  - database/contests/pumac/year=2023/results_A.csv
  - database/contests/pumac-algebra/year=2023/results_A.csv
  - database/contests/pumac-geometry/year=2023/results_A.csv
  - database/contests/pumac-number-theory/year=2023/results_A.csv
  - database/contests/pumac-combinator/year=2023/results_A.csv
  - appends new students to database/students/students.csv
"""

import csv
import re
import urllib.request
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
URL_2023 = "https://pumac.princeton.edu/results/2023/IndividualsA.html"

# Column offsets for subject tables: "  rank Name(19) Team(23) Score 1..8"
SUBJ_NAME_START, SUBJ_NAME_END = 4, 23
SUBJ_TEAM_START, SUBJ_TEAM_END = 23, 46
# Rankings: lines are ~96 chars; "  rank Name(19) Team(27) Total Finals..."
RANK_NAME_START, RANK_NAME_END = 4, 23
RANK_TEAM_START, RANK_TEAM_END = 23, 50
RANK_REST_START = 50  # total_score, finals_score from line[50:].split()

SUBJECT_SECTIONS = {"algebra": "ALG", "geometry": "GEO", "number theory": "NTY", "combinatorics": "CMB"}
TEST_SCORE_RE = re.compile(r"([\d.]+)\s*\(([A-Z]+)\)")

# Team name -> state (for student identity). Leave unknown teams as "".
TEAM_TO_STATE = {
    "Lehigh Valley Fire": "Pennsylvania",
    "Lehigh Valley Ice": "Pennsylvania",
    "TJ A": "Virginia",
    "TJ B": "Virginia",
    "BCA 1": "New Jersey",
    "CT Cyborgs": "Connecticut",
    "Connecticut A1": "Connecticut",
    "Connecticut A2": "Connecticut",
    "Lexington Alpha": "Massachusetts",
    "Lexington Beta": "Massachusetts",
    "Florida Alligators": "Florida",
    "Florida Beaches": "Florida",
    "Texas Ramanujan": "Texas",
    "Texas Hardy": "Texas",
    "Phillips Academy": "Massachusetts",
    "PEA Red Lion": "New Hampshire",
    "PEA Lions A1": "New Hampshire",
    "MoCoSwaggaSquad": "Maryland",
    "Montgomery B1": "Maryland",
    "Central Maryland United": "Maryland",
    "Poolesville Math Team A": "Maryland",
    "GWe UAre Not NAffiliated": "Georgia",
    "BBMC-math Delta": "Maryland",
    "Tin Man": "California",
    "Scarecrow": "California",
    "Athemath Owls": "California",
    "Knights A": "California",
    "PRISMS Falcons": "California",
    "Lion": "California",
    "404 Error": "Virginia",
    "Pirates A": "California",
    "Pirates B": "California",
    "Western PA A1": "Pennsylvania",
    "WWP^2": "New Jersey",
    "Yu's Alligator": "Florida",
    "Frazer A2": "Georgia",
}


def fetch_pre_text(url: str) -> str:
    with urllib.request.urlopen(url) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    m = re.search(r"<pre[^>]*>(.*?)</pre>", html, re.DOTALL | re.IGNORECASE)
    block = m.group(1) if m else html
    text = re.sub(r"<[^>]+>", "", block)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&nbsp;", " ")
    return text


def detect_section(line: str) -> Optional[str]:
    lower = line.strip().lower()
    for kw in SUBJECT_SECTIONS:
        if lower.startswith(kw):
            return kw
    if "individual rankings" in lower or lower.startswith("rankings"):
        return "rankings"
    return None


def is_data_line(line: str) -> bool:
    return bool(re.match(r"^\s{0,2}\d{1,3}\s", line))


def parse_subject_line(line: str, subject_abbr: str) -> Optional[dict]:
    if len(line) < SUBJ_TEAM_END:
        line = line.ljust(SUBJ_TEAM_END + 30)
    name = line[SUBJ_NAME_START:SUBJ_NAME_END].strip()
    team = line[SUBJ_TEAM_START:SUBJ_TEAM_END].strip()
    rest = line[SUBJ_TEAM_END:].strip()
    if not name or not team:
        return None
    tokens = rest.split()
    if len(tokens) < 9:
        return None
    try:
        score = float(tokens[0])
        p1, p2, p3, p4, p5, p6, p7, p8 = (int(tokens[i]) for i in range(1, 9))
    except (ValueError, IndexError):
        return None
    rank_str = line[:SUBJ_NAME_START].strip()
    try:
        rank = int(rank_str)
    except ValueError:
        rank = 0
    return {
        "rank": rank,
        "name": name,
        "team": team,
        "subject_abbr": subject_abbr,
        "score": score,
        "p1": p1, "p2": p2, "p3": p3, "p4": p4,
        "p5": p5, "p6": p6, "p7": p7, "p8": p8,
    }


def parse_rankings_line(line: str) -> Optional[dict]:
    if len(line) < RANK_REST_START:
        line = line.ljust(RANK_REST_START + 20)
    name = line[RANK_NAME_START:RANK_NAME_END].strip()
    team = line[RANK_TEAM_START:RANK_TEAM_END].strip()
    rest = line[RANK_REST_START:].strip()
    if not name or not team:
        return None
    tokens = rest.split()
    if len(tokens) < 2:
        return None
    try:
        total = float(tokens[0])
        finals = int(tokens[1])
    except (ValueError, TypeError):
        return None
    rank_str = line[:RANK_NAME_START].strip()
    try:
        rank = int(rank_str)
    except ValueError:
        rank = 0
    return {"rank": rank, "name": name, "team": team, "total_score": total, "finals_score": finals}


def parse_pumac_page(text: str) -> tuple[list[dict], list[dict]]:
    subject_results = []
    ranking_results = []
    current_section = None
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


def load_students() -> tuple[dict, list[dict], int]:
    """(name_lower, state) -> row; list of rows; next_id."""
    key_to_row: dict[tuple[str, str], dict] = {}
    rows: list[dict] = []
    next_id = 1
    if not STUDENTS_CSV.exists():
        return key_to_row, rows, next_id
    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid_s = (row.get("student_id") or "").strip()
            if not sid_s:
                continue
            try:
                sid = int(sid_s)
            except ValueError:
                continue
            next_id = max(next_id, sid + 1)
            name = (row.get("student_name") or "").strip()
            state = (row.get("state") or "").strip()
            alias = (row.get("alias") or "").strip()
            r = {"student_id": sid, "student_name": name, "state": state, "team_ids": row.get("team_ids", ""), "alias": alias}
            rows.append(r)
            if name:
                key = (name.lower(), state)
                if key not in key_to_row:
                    key_to_row[key] = r
            if alias:
                for a in alias.split("|"):
                    a = a.strip()
                    if a:
                        key = (a.lower(), state)
                        if key not in key_to_row:
                            key_to_row[key] = r
    return key_to_row, rows, next_id


def find_or_add_student(
    name: str,
    team: str,
    key_to_row: dict,
    rows: list[dict],
    next_id: int,
    new_students: list[dict],
) -> tuple[int, str, int]:
    """Returns (student_id, student_name, next_id)."""
    state = TEAM_TO_STATE.get(team, "")
    key = (name.strip().lower(), state)
    if key in key_to_row:
        r = key_to_row[key]
        return int(r["student_id"]), r["student_name"], next_id
    sid = next_id
    next_id += 1
    canon_name = name.strip()
    r = {"student_id": sid, "student_name": canon_name, "state": state, "team_ids": "", "alias": ""}
    rows.append(r)
    key_to_row[key] = r
    new_students.append(r)
    return sid, canon_name, next_id


def main() -> None:
    print("Fetching", URL_2023)
    text = fetch_pre_text(URL_2023)
    subject_results, ranking_results = parse_pumac_page(text)
    print(f"Parsed {len(subject_results)} subject rows, {len(ranking_results)} ranking rows")

    key_to_row, rows, next_id = load_students()
    new_students: list[dict] = []

    year = 2023
    division = "A"

    def resolve(name: str, team: str):
        return find_or_add_student(name, team, key_to_row, rows, next_id, new_students)

    # Individual rankings
    pumac_dir = ROOT / "database" / "contests" / "pumac" / f"year={year}"
    pumac_dir.mkdir(parents=True, exist_ok=True)
    ranking_rows_out = []
    for r in ranking_results:
        sid, sname, next_id = resolve(r["name"], r["team"])
        # Use name as shown on the website (source), not canonical registry name
        ranking_rows_out.append((sid, r["name"], year, division, r["rank"], r["total_score"], r["finals_score"]))

    out_path = pumac_dir / "results_A.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["student_id", "student_name", "year", "division", "rank", "total_score", "finals_score"])
        for row in ranking_rows_out:
            w.writerow(row)
    print(f"Wrote {out_path} ({len(ranking_rows_out)} rows)")

    slug_by_abbr = {"ALG": "pumac-algebra", "GEO": "pumac-geometry", "NTY": "pumac-number-theory", "CMB": "pumac-combinator"}
    by_subject: dict[str, list] = {abbr: [] for abbr in slug_by_abbr}
    for r in subject_results:
        abbr = r["subject_abbr"]
        if abbr not in by_subject:
            continue
        sid, sname, next_id = resolve(r["name"], r["team"])
        # Use name as shown on the website (source), not canonical registry name
        by_subject[abbr].append((
            sid, r["name"], year, division, r["rank"], r["score"],
            r["p1"], r["p2"], r["p3"], r["p4"], r["p5"], r["p6"], r["p7"], r["p8"],
        ))

    for abbr, slug in slug_by_abbr.items():
        subj_rows = by_subject.get(abbr, [])
        if not subj_rows:
            continue
        subj_dir = ROOT / "database" / "contests" / slug / f"year={year}"
        subj_dir.mkdir(parents=True, exist_ok=True)
        path = subj_dir / "results_A.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["student_id", "student_name", "year", "division", "rank", "score", "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"])
            for row in subj_rows:
                w.writerow(row)
        print(f"Wrote {path} ({len(subj_rows)} rows)")

    if new_students:
        with open(STUDENTS_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            for r in new_students:
                w.writerow([r["student_id"], r["student_name"], r["state"], r.get("team_ids", ""), r.get("alias", "")])
        print(f"Appended {len(new_students)} new students to {STUDENTS_CSV}")
    else:
        print("No new students to add.")

    print("Done. Run: python scripts/build_search_data.py")


if __name__ == "__main__":
    main()
