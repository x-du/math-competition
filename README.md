# math-competition
Math Competition Records

Please report issues, official contest results, and cheating to **mathcontestintegrity@gmail.com**.

## Student search (GitHub Pages)

A static frontend lets you search students by name and view their competition records.

### Build data

From the repo root:

```bash
python scripts/build_search_data.py
```

This writes `docs/data.json` from the `database/` CSVs.

To validate MATHCOUNTS National — Rankings (≤3 appearances, all grades distinct):

```bash
python scripts/check_mathcounts_national_students.py
```

### Data quality

- **`scripts/check_all.py`** — Runs all six checks below in sequence; exits with status 1 if any fail. Run from repo root: `python scripts/check_all.py`.
- **`scripts/check_mathcounts_national_students.py`** — Validates MATHCOUNTS National — Rankings: each student has ≤3 appearances and all grades distinct; prints only violations and exits with status 1 if any. Run from repo root: `python scripts/check_mathcounts_national_students.py`.
- **`scripts/find_incomplete_students.py`** — Scans `database/students/students.csv` for students missing **state**, **gender**, or **grade_in_2026**. Writes results to `incomplete_students.json` (repo root) and prints only a summary of counts. Run from repo root: `python scripts/find_incomplete_students.py`.
- **`scripts/check_csv_integrity.py`** — Checks every CSV under `database/` so each data row has the same number of columns as the header; prints only files with row-length violations plus a summary table, and exits with status 1 if any file has mismatched row lengths. Run from repo root: `python scripts/check_csv_integrity.py`.
- **`scripts/check_student_ids.py`** — Checks consistency between `database/students/students.csv` and contest CSVs: reports (1) student IDs in the registry not referenced by any contest, and (2) student IDs referenced in contest CSVs that are missing from the registry. Run from repo root: `python scripts/check_student_ids.py`.
- **`scripts/check_hmmt_students.py`** — Checks for students who appear in both HMMT November (year Y) and HMMT February (year Y+1); prints overlapping students per year pair. Run from repo root: `python scripts/check_hmmt_students.py`.
- **`scripts/check_pumac_students.py`** — Checks for students who appear in both PUMaC division A and division B in the same year; prints overlapping students per year. Run from repo root: `python scripts/check_pumac_students.py`.

### Run locally

Serve the `docs` folder (e.g. `python -m http.server 8000 --directory docs` or any static server). Open the site and use the search box.

### Deploy to GitHub Pages

1. In the repo: **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
3. Choose the branch (e.g. `main`) and set the folder to **/docs**.
4. Save. The site will be at `https://<username>.github.io/math-competition/`.

After updating the database, run `python scripts/build_search_data.py` and commit the updated `docs/data.json`.
