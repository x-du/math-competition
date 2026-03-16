#!/usr/bin/env python3
"""
Build ARML 2025 Top Individuals `results.csv` directly from hard-coded data
and update `students.csv`. No input files are required.

Usage (run from repo root):

    python scripts/build_arml_2025.py

Output:
  - `database/contests/arml/year=2025/results.csv` with columns:
      student_id,student_name,place,site,team,tb_corr,tb_time,prize
  - Any new students are appended to `database/students/students.csv`
"""

import csv
from pathlib import Path


# Paths are relative to the repository root (run from project root).
STUDENTS_CSV = Path("database/students/students.csv")

# Hard-coded ARML 2025 Top Individuals data, based on the official results.
# Columns: place, site, name, team, tb_corr, tb_time, prize
RAW = [
    ("1", "P", "Christopher Qiu", "Central Jersey A1", "$1,500"),
    ("2", "I", "Nathan Liu", "Texas A1", "1", "80", "$1,250"),
    ("3", "N", "Andy Lu", "SFBA/NorCal A1", "1", "81", "$1,250"),
    ("4", "N", "Rohan Bodke", "SFBA/NorCal A1", "1", "82", "$1,000"),
    ("5", "I", "James Stewart", "Texas A2", "1", "100", "$1,000"),
    ("6", "P", "Angelica Feng", "WWP^2", "1", "109", "$1,000"),
    ("7", "P", "Eric Xie", "Montgomery B1", "1", "117", "$750"),
    ("8", "W", "Varun Gadi", "Georgia A1", "1", "121", "$750"),
    ("9", "I", "Kevin Hu", "Texas A3", "1", "125", "$750"),
    ("10", "P", "Soham Dam", "Western PA A1", "1", "128", "$750"),
    ("11", "N", "Aryan Agrawal", "Washington A1", "1", "130", "$500"),
    ("12", "S", "Eric Huang", "Massachusetts B1", "1", "143", "$500"),
    ("13", "N", "Royce Yao", "Wild Wild West B1", "1", "152", "$500"),
    ("14", "P", "Eddy Zhang", "Lehigh Valley A1", "1", "153", "$500"),
    ("15", "P", "Michael Sun", "Ontario Math Circles A1", "1", "172", "$500"),
    ("16", "N", "Jonathan Yu", "Southern California B1", "1", "173", "$500"),
    ("17", "P", "Leo Wu", "Ontario Math Circles A1", "1", "180", "$500"),
    ("18", "I", "Channing Yang", "Texas A1", "1", "191", "$500"),
    ("19", "P", "Jason Mao", "Lehigh Valley A1", "1", "194", "$500"),
    ("20 (tie)", "N", "Chris Bao", "Northern Nevada Math Club B1", "1", "207", "$500"),
    ("20 (tie)", "I", "Edward Li", "Iowa", "1", "207", "$500"),
    ("22", "I", "Ekam Kaur", "Texas A2", "1", "209", ""),
    ("23", "N", "Liam Reddy", "Utah B1", "1", "212", ""),
    ("24", "N", "Shruti Arun", "Colorado B1", "1", "213", ""),
    ("25", "P", "Benjamin Lu", "Lehigh Valley A2", "1", "222", ""),
    ("26", "S", "Oron Wang", "PEA Lions A1", "1", "222", ""),
    ("27", "N", "Rohith Thomas", "Colorado B1", "1", "232", ""),
    ("28", "S", "Alexander Svoronos", "Connecticut A1", "1", "253", ""),
    ("29", "I", "Shaheem Samsudeen", "Texas A3", "1", "265", ""),
    ("30", "I", "Vincent Wang", "Texas A1", "1", "280", ""),
    ("31", "P", "Kyle Wu", "NYC A1", "1", "287", ""),
    ("32", "P", "Tiger Li", "Ontario Math Circles A1", "1", "300", ""),
    ("33", "N", "Hannah Fox", "SFBA/NorCal A1", "1", "330", ""),
    ("34", "I", "Michael Chang", "Texas A2", "1", "332", ""),
    ("35", "P", "Ruilin Wang", "TJHSST A1", "1", "348", ""),
    ("36", "P", "Alexander Wang", "Lehigh Valley A1", "1", "365", ""),
    ("37", "I", "Jeff Zhou", "Minnesota B1", "1", "373", ""),
    ("38", "I", "Darren Han", "Texas A1", "1", "409", ""),
    ("39", "S", "Vikram Sarkar", "Connecticut A1", "1", "413", ""),
    ("40", "I", "Bach Kieu", "Indiana B1", "1", "493", ""),
    ("41", "W", "Allan Yuan", "Alabama B1", "1", "515", ""),
    ("42", "P", "Kaylyn Zhang", "Ontario Math Circles A1", "2", "58", ""),
    ("43", "P", "David Wang", "Montgomery B1", "2", "73", ""),
    ("44", "S", "Jack Whitney-Epstein", "Connecticut A1", "2", "77", ""),
    ("45", "I", "Michael Zhao", "Texas A1", "2", "96", ""),
    ("46", "N", "Ian Rui", "Washington A1", "2", "100", ""),
    ("47", "P", "Benjamin Song", "Upstate New York B1", "2", "113", ""),
    ("48", "P", "Perry Dai", "Ontario Math Circles A1", "2", "136", ""),
    ("49", "S", "Benny Wang", "PEA Lions A1", "2", "138", ""),
    ("50", "N", "Kiran Reddy", "Utah B1", "2", "199", ""),
    ("51", "N", "Dylan Wang", "SFBA/NorCal A2", "2", "209", ""),
    ("52", "N", "Rick Zhou", "Washington A2", "3", "51", ""),
    ("53", "P", "Lewis Lou", "Montgomery B1", "3", "61", ""),
    ("54", "N", "Jonathan Wu", "Utah B1", "3", "64", ""),
    ("55", "S", "Zenghan (Yoll) Feng", "Phillips Academy Andover", "3", "67", ""),
    ("56", "S", "Jonathan Zhou", "Connecticut A2", "3", "79", ""),
    ("57", "W", "George Paret", "Frazer A2", "3", "134", ""),
    ("58", "I", "Lanie Deng", "Missouri B1", "3", "172", ""),
    ("59", "S", "Raine Ma", "Connecticut A1", "3", "264", ""),
    ("60", "N", "Aarav Mann", "SFBA/NorCal A5", "4", "0", ""),
    ("61", "P", "Eden He", "Lehigh Valley A2", "4", "0", ""),
    ("62", "P", "Prince Zhang", "Ontario Math Circles A2", "4", "0", ""),
    ("63", "P", "Eric Jia", "Ontario Math Circles A1", "4", "0", ""),
    ("64", "I", "Michael Luo", "Minnesota B1", "4", "0", ""),
]


def load_students():
    """Load existing students and aliases -> { name_or_alias: sid }, next_id."""
    name_to_id: dict[str, int] = {}
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
                name_to_id.setdefault(name, sid)

            alias = (row.get("alias") or "").strip()
            if alias:
                for a in alias.split("|"):
                    a = a.strip()
                    if a:
                        name_to_id.setdefault(a, sid)

    return name_to_id, next_id


def main() -> None:
    base_dir = Path("database/contests/arml/year=2025")

    name_to_id, next_id = load_students()

    rows: list[tuple[int, str, str, str, str, str, str, str]] = []
    new_students: list[tuple[int, str]] = []

    for place, site, name, team, tb_corr, tb_time, prize in RAW:
        name = name.strip()
        if not name:
            continue

        sid = name_to_id.get(name)
        if sid is None:
            sid = next_id
            next_id += 1
            new_students.append((sid, name))
            if name not in name_to_id:
                name_to_id[name] = sid

        rows.append((sid, name, place, site, team, tb_corr, tb_time, prize))

    # Write ARML 2025 results (relative to repo root).
    out_dir = base_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    results_path = out_dir / "results.csv"
    with results_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "student_name", "place", "site", "team", "tb_corr", "tb_time", "prize"])
        for r in rows:
            writer.writerow(r)

    # Append any new students
    if new_students:
        with STUDENTS_CSV.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for sid, name in new_students:
                # state, team_ids, alias left blank; can be filled later.
                writer.writerow([sid, name, "", "", ""])

    print(f"Wrote {results_path} with {len(rows)} ARML 2025 rows")
    print(f"Added {len(new_students)} new students to {STUDENTS_CSV}")


if __name__ == "__main__":
    main()

