#!/usr/bin/env python3
"""Find AMO 2025 Gold medalists who have never been in JMO or AMO before 2025."""

import csv
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "database"

def load_student_ids(csv_path):
    with open(csv_path) as f:
        r = csv.DictReader(f)
        return set(int(row["student_id"]) for row in r)

def main():
    # AMO 2025 Gold
    amo_2025 = load_student_ids(DB / "contests/amo/year=2025/results.csv")
    with open(DB / "contests/amo/year=2025/results.csv") as f:
        r = csv.DictReader(f)
        amo_2025_gold = {
            (int(row["student_id"]), row["student_name"], row["state"])
            for row in r if row["award"] == "Gold"
        }

    # Prior JMO/AMO (2022, 2023, 2024)
    prior_ids = set()
    for contest in ("jmo", "amo"):
        for year in ("2022", "2023", "2024"):
            p = DB / f"contests/{contest}/year={year}/results.csv"
            if p.exists():
                prior_ids |= load_student_ids(p)

    # AMO 2025 Gold who were NOT in JMO/AMO before
    first_time = [(sid, name, state) for sid, name, state in amo_2025_gold if sid not in prior_ids]
    first_time.sort(key=lambda x: x[1])

    print("AMO 2025 Gold medalists who had NOT been in JMO or AMO before 2025:\n")
    for sid, name, state in first_time:
        print(f"  {sid},{name},{state}")
    print(f"\nTotal: {len(first_time)}")

if __name__ == "__main__":
    main()
