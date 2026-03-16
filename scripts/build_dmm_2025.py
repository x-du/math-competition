#!/usr/bin/env python3
"""
Build Duke Math Meet 2025 Individual Standings results.csv from hard-coded data
and update students.csv with any new students.

Usage (run from repo root):

    python scripts/build_dmm_2025.py

Output:
  - database/contests/dmm/year=2025/results.csv with columns:
      student_id,student_name,state,rank,team_name,club_name,score,q1,q2,q3,q4,q5,q6,q7,q8,q9,q10
  - Any new students are appended to database/students/students.csv
"""

import csv
import re
from pathlib import Path


STUDENTS_CSV = Path("database/students/students.csv")

# Optional: map alternate spellings / typos to existing student_id to avoid duplicates.
NAME_TO_EXISTING_ID = {
    "Grisham Paimagan": 219,  # DB has Grisham Paimagam
}

# DMM 2025 Individual Standings: Rank, Name, Team Name, Club Name, Score, Q1..Q10
RAW = [
    (1, "Calvin Wang", "TJ A", "TJHSST", 9, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0),
    (2, "Chang Lu", "Shanghai Starriver Bilingual School", "Shanghai Starriver Bilingual School", 9, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0),
    (3, "Anthony Zou", "Columbia Math Circle Team 1", "Columbia Math Circle", 9, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1),
    (4, "Yucheng Zhang", "Shanghai Starriver Bilingual School", "Shanghai Starriver Bilingual School", 9, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0),
    (5, "Alan Cheng", "NCSSM Alpha", "NCSSM Math Team", 8, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0),
    (6, "David Wang", "MOO", "Maryland United", 8, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1),
    (6, "Qianmo Ni", "Shanghai Starriver Bilingual School", "Shanghai Starriver Bilingual School", 8, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0),
    (6, "Thomas Yao", "MOO", "Maryland United", 8, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1),
    (9, "Parsa Adhami", "Columbia Math Circle Team 2", "Columbia Math Circle", 7, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1),
    (9, "Lewis Lau", "MoCoSwaggaSquad", "RMHS Math Team", 7, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0),
    (9, "Mingfei Zhou", "Keystone Academy of Beijing", "Keystone Academy of Beijing", 7, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0),
    (9, "Jeffrey Yin", "McLean A", "McLean Highlander Math League", 7, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1),
    (9, "Gloria Lu", "McLean A", "McLean Highlander Math League", 7, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0),
    (9, "Grisham Paimagan", "NCSSM Alpha", "NCSSM Math Team", 7, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0),
    (9, "Nelson Huang", "NCSSM Beta", "NCSSM Math Team", 7, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0),
    (9, "Kesav Kalanidhi", "NCSSM Gamma", "NCSSM Math Team", 7, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0),
    (9, "Arnav  Iyengar", "DMV Math Circle", "DMV Math Circle", 7, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0),
    (9, "Eric Zhu", "Cary Academy 1", "Cary Academy 1", 7, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0),
    (9, "Sixun Zheng", "Shanghai Starriver Bilingual School", "Shanghai Starriver Bilingual School", 7, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0),
    (9, "Patrick Du", "TJ A", "TJHSST", 7, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0),
    (9, "Anderson Hao", "TJ B", "TJHSST", 7, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1),
    (9, "Ethan Shan", "TJ C", "TJHSST", 7, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0),
    (9, "Eden He", "DMV Math Circle", "DMV Math Circle", 7, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0),
    (9, "Liang Christopher", "East Chapel Hill HS Team A", "East Chapel Hill High school", 7, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0),
    (9, "Brandon Jia", "East Chapel Hill HS Team A", "East Chapel Hill High school", 7, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0),
    (9, "Jason Sliwowski", "East Chapel Hill HS Team A", "East Chapel Hill High school", 7, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1),
    (9, "David Dong", "East Chapel Hill HS Team A", "East Chapel Hill High school", 7, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0),
    (9, "Roman  Mecholsky", "BBMC-math Delta", "BBMC-math", 7, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1),
    (29, "Jahl Miraji-Khot", "Columbia Math Circle Team 1", "Columbia Math Circle", 6, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0),
    (29, "Dylan Zhang", "Team", "Club Name", 6, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0),
    (29, "Sarah Li", "McLean A", "McLean Highlander Math League", 6, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0),
    (29, "Aaron Wang", "NCSSM Alpha", "NCSSM Math Team", 6, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0),
    (29, "Raghav Arun", "NCSSM Alpha", "NCSSM Math Team", 6, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0),
    (29, "Aaron Zhu", "NCSSM Beta", "NCSSM Math Team", 6, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0),
    (29, "Srinivas Vijay Babu", "NCSSM Beta", "NCSSM Math Team", 6, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0),
    (29, "Ryan Karim", "DMV Math Circle", "DMV Math Circle", 6, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0),
    (29, "Thanh Can", "DMV Math Circle", "DMV Math Circle", 6, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0),
    (29, "Ved Vainateya", "Cary Academy 2", "Cary Academy 1", 6, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0),
    (29, "Avi Gupta", "MOO", "Maryland United", 6, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0),
    (29, "Yuwei Li", "Shanghai Starriver Bilingual School", "Shanghai Starriver Bilingual School", 6, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0),
    (29, "Yanming Huang", "Shanghai Starriver Bilingual School", "Shanghai Starriver Bilingual School", 6, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1),
    (29, "Angelo Chu", "TJ B", "TJHSST", 6, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0),
    (29, "Ryan Singh", "TJ B", "TJHSST", 6, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0),
    (29, "Jeffrey Du", "TJ C", "TJHSST", 6, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0),
    (29, "Shawn Bi", "TJ C", "TJHSST", 6, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0),
    (29, "Yeeyung Li", "TJ D", "TJHSST", 6, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0),
    (29, "William Li", "TJ D", "TJHSST", 6, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0),
    (29, "Watson Houck", "CMC - Harold", "Charlotte Math Club", 6, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0),
    (29, "Ryan Chan", "Chantilly A", "Chantilly Math Club", 6, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0),
    (29, "Ishidevesh Behera", "Ardrey Kell A Team", "Ardrey Kell High School", 6, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0),
    (29, "Atharv Mittal", "Ardrey Kell A Team", "Ardrey Kell High School", 6, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0),
]


def normalize_name(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def load_students():
    """Load existing students and aliases -> { normalized_name: sid }, next_id."""
    name_to_id: dict[str, int] = {}
    sid_to_state: dict[int, str] = {}
    next_id = 1

    with STUDENTS_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid_raw = (row.get("student_id") or "").strip()
            if not sid_raw:
                continue
            try:
                sid = int(sid_raw)
            except ValueError:
                continue
            next_id = max(next_id, sid + 1)

            name = (row.get("student_name") or "").strip()
            if name:
                name_to_id.setdefault(normalize_name(name), sid)
                sid_to_state[sid] = (row.get("state") or "").strip()

            alias = (row.get("alias") or "").strip()
            if alias:
                for a in alias.split("|"):
                    a = normalize_name(a)
                    if a:
                        name_to_id.setdefault(a, sid)

    return name_to_id, sid_to_state, next_id


def main() -> None:
    base_dir = Path("database/contests/dmm/year=2025")
    name_to_id, sid_to_state, next_id = load_students()

    rows: list[tuple] = []
    new_students: list[tuple[int, str]] = []

    for t in RAW:
        rank, name, team_name, club_name, score = t[0], t[1], t[2], t[3], t[4]
        q1, q2, q3, q4, q5, q6, q7, q8, q9, q10 = t[5], t[6], t[7], t[8], t[9], t[10], t[11], t[12], t[13], t[14]

        name_norm = normalize_name(name)
        sid = NAME_TO_EXISTING_ID.get(name) or NAME_TO_EXISTING_ID.get(name_norm)
        if sid is None:
            sid = name_to_id.get(name_norm)

        if sid is None:
            sid = next_id
            next_id += 1
            new_students.append((sid, name))
            name_to_id[name_norm] = sid

        state = sid_to_state.get(sid, "")
        canonical_name = name  # keep display name from results
        rows.append((sid, canonical_name, state, rank, team_name, club_name, score, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10))

    base_dir.mkdir(parents=True, exist_ok=True)
    results_path = base_dir / "results.csv"
    with results_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "student_id", "student_name", "state", "rank", "team_name", "club_name",
            "score", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10",
        ])
        for r in rows:
            writer.writerow(r)

    if new_students:
        with STUDENTS_CSV.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for sid, name in new_students:
                writer.writerow([sid, name, "", "", ""])

    print(f"Wrote {results_path} with {len(rows)} DMM 2025 rows")
    print(f"Added {len(new_students)} new students to {STUDENTS_CSV}")


if __name__ == "__main__":
    main()
