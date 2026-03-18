#!/usr/bin/env python3
"""
Fetch HMMT archive pages (feb and nov, 2022-2026) and match students with missing
state to their team names. Output results to student_team.json.
"""

import json
import re
import urllib.request
from pathlib import Path

# Base URL for HMMT archive
BASE_URL = "https://hmmt-archive.s3.amazonaws.com/tournaments/{year}/{month}/results/long.htm"

# Pattern: | Name (Team Name) at end of line
# Lines have format: O   XX. XX.XX | scores | Name (Team Name)
# We need the last | segment: " Name (Team Name)"
NAME_TEAM_PATTERN = re.compile(r"\|\s+([^|]+?)\s+\(([^)]+)\)\s*$")


def fetch_page(url: str) -> str:
    """Fetch page content from URL."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return ""


def normalize_name(name: str) -> str:
    """Normalize name for matching (lowercase, collapse spaces)."""
    return " ".join(name.lower().split())


def main():
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    incomplete_path = repo_root / "incomplete_students.json"
    output_path = repo_root / "student_team.json"

    with open(incomplete_path) as f:
        data = json.load(f)

    missing_state = data["missing_state"]
    print(f"Loaded {len(missing_state)} students with missing state")

    # Build name->(team, year, month) mapping from all HMMT pages
    # Key: normalized name, Value: list of (team, year, month) for all occurrences
    all_name_team: dict[str, list[tuple[str, int, str]]] = {}
    for year in range(2022, 2027):
        for month in ["feb", "nov"]:
            url = BASE_URL.format(year=year, month=month)
            print(f"Fetching {year}/{month}...")
            content = fetch_page(url)
            if content:
                for line in content.splitlines():
                    m = NAME_TEAM_PATTERN.search(line)
                    if m:
                        name = m.group(1).strip()
                        team = m.group(2).strip()
                        norm = normalize_name(name)
                        if norm not in all_name_team:
                            all_name_team[norm] = []
                        all_name_team[norm].append((team, year, month))

    # Match students
    results = []
    for student in missing_state:
        student_id = student["student_id"]
        student_name = student["student_name"]
        norm = normalize_name(student_name)
        occurrences = all_name_team.get(norm)
        if occurrences:
            # Use first occurrence; collect all unique (team, year, month) for output
            seen = set()
            matches = []
            for team, year, month in occurrences:
                key = (team, year, month)
                if key not in seen:
                    seen.add(key)
                    matches.append({"team": team, "year": year, "tournament": month})
            results.append(
                {
                    "student_id": student_id,
                    "student_name": student_name,
                    "teams": matches,
                }
            )

    output = {
        "source": "HMMT archive (feb/nov 2022-2026)",
        "url_template": "https://hmmt-archive.s3.amazonaws.com/tournaments/{year}/{month}/results/long.htm",
        "matches_count": len(results),
        "total_missing_state": len(missing_state),
        "student_teams": results,
    }

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nFound {len(results)} matches out of {len(missing_state)} students")
    print(f"Written to {output_path}")


if __name__ == "__main__":
    main()
