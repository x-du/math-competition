import csv
import glob
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_team_names():
    teams_path = REPO_ROOT / "database" / "students" / "teams.csv"
    team_id_to_name = {}
    with teams_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "team_id" not in reader.fieldnames or "team_name" not in reader.fieldnames:
            raise RuntimeError("Expected 'team_id' and 'team_name' columns in teams.csv")
        for row in reader:
            tid = (row.get("team_id") or "").strip()
            name = (row.get("team_name") or "").strip()
            if not tid:
                continue
            if not name:
                raise RuntimeError(f"Missing team_name for team_id={tid} in teams.csv")
            team_id_to_name[tid] = name
    return team_id_to_name


def update_contest_file(path: Path, team_id_to_name: dict):
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if fieldnames is None:
            return
        if "team_id" not in fieldnames:
            # Nothing to do for this file.
            return
        new_fieldnames = list(fieldnames)
        idx = new_fieldnames.index("team_id")
        new_fieldnames[idx] = "team_name"

        rows = []
        for row in reader:
            tid_raw = row.get("team_id")
            tid = (tid_raw or "").strip()
            if not tid:
                # Preserve empty / missing team entries.
                row.pop("team_id", None)
                row["team_name"] = ""
            else:
                if tid not in team_id_to_name:
                    raise RuntimeError(f"Unknown team_id {tid} in {path}")
                row.pop("team_id", None)
                row["team_name"] = team_id_to_name[tid]
            rows.append(row)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    team_id_to_name = load_team_names()

    pattern = str(REPO_ROOT / "database" / "contests" / "pumac-b*/*/results_B.csv")
    paths = sorted(Path(p) for p in glob.glob(pattern))

    if not paths:
        raise SystemExit("No pumac-b results_B.csv files found.")

    for path in paths:
        update_contest_file(path, team_id_to_name)


if __name__ == "__main__":
    main()

