#!/usr/bin/env python3
"""
Fetch PUMAC result pages (IndividualsA and IndividualsB, 2022-2025) and match
students with missing state to their team names. Output results to
student_team_pumac.json.
"""

import json
import re
import urllib.request
from pathlib import Path

# PUMAC URLs: IndividualsA and IndividualsB for each year
BASE_URLS = [
    "https://pumac.princeton.edu/results/{year}/IndividualsA.html",
    "https://pumac.princeton.edu/results/{year}/IndividualsB.html",
]

# PUMAC format: "  1 Zongshu Wu            Random Math                    15.843   1   0 ..."
# Rank, Name (padded), Team (padded), Score (decimal), then 1/0 values
# Match: digits, then name and team (two groups of non-empty text) before score
NAME_TEAM_PATTERN = re.compile(
    r"^\s*\d+\s+(.+?)\s{2,}(.+?)\s+(\d+\.\d{3})\s+[\d.\s]+$"
)


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


def extract_name_team_pairs(content: str) -> list[tuple[str, str]]:
    """Extract (name, team) pairs from PUMAC HTML content."""
    pairs = []
    for line in content.splitlines():
        m = NAME_TEAM_PATTERN.match(line.strip())
        if m:
            name = m.group(1).strip()
            team = m.group(2).strip()
            if name and team and not name.isdigit():
                pairs.append((name, team))
    return pairs


def main():
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    incomplete_path = repo_root / "incomplete_students.json"
    output_path = repo_root / "student_team_pumac.json"

    with open(incomplete_path) as f:
        data = json.load(f)

    missing_state = data["missing_state"]
    print(f"Loaded {len(missing_state)} students with missing state")

    # Build name->(team, year, division) mapping from all PUMAC pages
    all_name_team: dict[str, list[tuple[str, int, str]]] = {}
    for year in range(2022, 2026):
        for i, url_template in enumerate(BASE_URLS):
            division = "A" if i == 0 else "B"
            url = url_template.format(year=year)
            print(f"Fetching {year} Individuals{division}...")
            content = fetch_page(url)
            if content:
                pairs = extract_name_team_pairs(content)
                for name, team in pairs:
                    norm = normalize_name(name)
                    if norm not in all_name_team:
                        all_name_team[norm] = []
                    all_name_team[norm].append((team, year, division))

    # Match students
    results = []
    for student in missing_state:
        student_id = student["student_id"]
        student_name = student["student_name"]
        norm = normalize_name(student_name)
        occurrences = all_name_team.get(norm)
        if occurrences:
            seen = set()
            matches = []
            for team, year, division in occurrences:
                key = (team, year, division)
                if key not in seen:
                    seen.add(key)
                    matches.append(
                        {"team": team, "year": year, "division": division}
                    )
            results.append(
                {
                    "student_id": student_id,
                    "student_name": student_name,
                    "teams": matches,
                }
            )

    output = {
        "source": "PUMAC Individuals A/B (2022-2025)",
        "url_templates": [
            "https://pumac.princeton.edu/results/{year}/IndividualsA.html",
            "https://pumac.princeton.edu/results/{year}/IndividualsB.html",
        ],
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
