#!/usr/bin/env python3
"""
Add BMT 2025 Distinguished HM (Top 20%) to results.csv.
Resolves student_id from students.csv and existing bmt-geometry results; appends new students as needed.
"""
import csv
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDENTS_CSV = os.path.join(REPO_ROOT, "database", "students", "students.csv")
RESULTS_CSV = os.path.join(REPO_ROOT, "database", "contests", "bmt-geometry", "year=2025", "results.csv")

# Distinguished HM (Top 20%) from user input: bmt_student_id, name
DISTINGUISHED_HM = [
    ("013A", "Brett Chang"),
    ("013B", "Evan Li"),
    ("018A", "Harshith Sai Mannaru"),
    ("029B", "Bryant Wang"),
    ("032C", "Alexannder Kong"),
    ("040D", "Justin Guo"),
    ("041E", "Anne Huang"),
    ("041F", "Melody Song"),
    ("048C", "Nolan Lin"),
    ("048F", "Franklin Zhou"),
    ("051A", "Junu Pae"),
    ("051B", "Thomas Liu"),
    ("051D", "Junwon Jahng"),
    ("051F", "Rishav Bhattacharjee"),
    ("053C", "Kevin Yang"),
    ("053E", "Rebecca Luo"),
    ("053F", "Zhenghua Xie"),
    ("054A", "Katrina Liu"),
    ("054B", "Aidan Bai"),
    ("054D", "Rohan Mallick"),
    ("054E", "Sepehr Golsefidy"),
    ("054F", "Xiaoran Han"),
    ("063B", "Matthew Hsiao"),
    ("063C", "Chris Chen"),
    ("063F", "Alex Chen"),
    ("074D", "Ryan Wang"),
    ("079E", "Gabriel Wang"),
    ("083D", "Nikhil McGowan"),
    ("083E", "Thomas McCurley"),
    ("083F", "Michael Wang"),
    ("088D", "John Oh"),
    ("088E", "Laura Chen"),
    ("089A", "Amy Zhang"),
    ("089D", "Iurii Kirpichev"),
    ("089F", "Niranjan Rao"),
    ("093B", "Utsav Lal"),
    ("093D", "Amelia Chen"),
    ("095F", "Elizabeth Ying"),
    ("097A", "Bryant Hu"),
    ("097C", "Kevin Li"),
    ("106D", "Ruixun Du"),
    ("108B", "Hank SUN"),
    ("110C", "Rutvik Arora"),
    ("110F", "Edward Zeng"),
    ("113C", "Terry Huang"),
    ("117A", "Eric Zou"),
    ("117C", "William Xin"),
    ("122A", "Bowen Wu"),
    ("122B", "Kevin Li"),
    ("122D", "Aidan Shin"),
    ("126C", "Jeffrey Ding"),
    ("127E", "Seabert Mao"),
    ("142B", "Vihaan Byahatti"),
    ("144E", "Hannah Ma"),
    ("144F", "Benjamin Fu"),
    ("156B", "Garrett Cai"),
    ("156D", "Yujun Lee"),
    ("157A", "Anlong Liu"),
    ("157C", "Carter Cai"),
    ("157E", "Ryan Santosh"),
    ("159B", "Mihir Tomar"),
    ("161A", "Jingxuan Bo"),
    ("161C", "Eric Shu"),
    ("161E", "Ashwin Shekhar"),
    ("161F", "HANS ZHONG-HONG CHEN"),
    ("163E", "Brian Lai"),
    ("164F", "Ruoyu Zhou"),
    ("165A", "Shihan Kanungo"),
    ("165B", "Ryan Bansal"),
    ("165D", "Jonathan Du"),
    ("167A", "Jason Yang"),
    ("167B", "Dylan Wang"),
    ("167C", "Alex Tsagaan"),
    ("167D", "Justin Kim"),
    ("169A", "Tianlin Liu"),
    ("169B", "Alena Kutsuk"),
    ("169E", "Kennan Suen"),
    ("169F", "Katherine Li"),
    ("171B", "Leia Kao"),
    ("176A", "Rohan Agarwal"),
    ("177A", "Andrew Shi"),
    ("177B", "Lucas Yuan"),
    ("177C", "Vihaan Gupta"),
    ("177D", "Jeffery Wang"),
    ("181F", "Sunay Miduthuri"),
    ("190C", "Jack He"),
    ("190E", "Yanxun Pu"),
    ("199A", "Alex Zhan"),
    ("201A", "Albert Li"),
    ("202C", "Leo Zeng"),
    ("206E", "Alexander Ruan"),
    ("209D", "Charlie Wang"),
    ("210D", "Ayan Sharma"),
    ("211A", "Daniel Nie"),
    ("211E", "Kailua Cheng"),
    ("221C", "Oscar Varodayan"),
    ("221E", "Sayan Singh"),
    ("228B", "Daniel Jin"),
    ("228F", "Alex Bae"),
    ("236B", "Liyan Xu"),
    ("236D", "Yuan Xing"),
    ("236F", "Peilin Lan"),
    ("242B", "Ben Oh"),
    ("244C", "Henry Wang"),
    ("244D", "Tanish Kolhe"),
    ("244E", "Yunfei Xia"),
    ("248B", "Isabella Li"),
    ("248E", "Eli Ying"),
]


def normalize_name(name):
    return name.strip().lower()


def load_students():
    """Return (by_name: dict[str, list of (id, name, state)], max_id, header_row)."""
    by_name = {}
    max_id = 0
    header = None
    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        header = r.fieldnames
        for row in r:
            sid = int(row["student_id"])
            if sid > max_id:
                max_id = sid
            name = row["student_name"]
            state = row.get("state", "") or ""
            key = normalize_name(name)
            by_name.setdefault(key, []).append((sid, name, state))
            alias_str = row.get("alias", "") or ""
            for al in alias_str.split("|"):
                al = al.strip().lower()
                if al and al != key:
                    by_name.setdefault(al, []).append((sid, name, state))
    return by_name, max_id, header


def resolve_student(source_name, by_name, next_id, new_students):
    """Resolve source_name to (student_id, canonical_name). Add to new_students if new."""
    key = normalize_name(source_name)
    if key in by_name:
        candidates = by_name[key]
        if len(candidates) == 1:
            sid, canonical_name, _ = candidates[0]
            return sid, canonical_name
        for sid, canonical_name, state in candidates:
            if state == "":
                return sid, canonical_name
        sid, canonical_name, _ = candidates[0]
        return sid, canonical_name
    if "(" in source_name and ")" in source_name:
        m = re.match(r"(.+?)\((.+?)\)(.+)", source_name)
        if m:
            left, mid, right = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
            for attempt in [mid + " " + right, left + right]:
                attempt_key = normalize_name(attempt)
                if attempt_key in by_name:
                    candidates = by_name[attempt_key]
                    if len(candidates) == 1:
                        sid, canonical_name, _ = candidates[0]
                        return sid, canonical_name
                    sid, canonical_name, _ = candidates[0]
                    return sid, canonical_name
    sid = next_id[0]
    next_id[0] += 1
    new_students.append((sid, source_name, ""))
    by_name.setdefault(key, []).append((sid, source_name, ""))
    return sid, source_name


def main():
    by_name, max_id, header = load_students()
    next_id = [max_id + 1]
    new_students = []

    # Load existing results for bmt_student_id -> (student_id, student_name) lookup
    existing_by_bmt = {}
    fieldnames = [
        "student_id", "student_name", "year", "subject", "bmt_student_id",
        "team_name", "school", "award", "rank", "score", "mcp_rank"
    ]
    existing_rows = []
    if os.path.exists(RESULTS_CSV):
        with open(RESULTS_CSV, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            existing_rows = list(r)
            for row in existing_rows:
                bid = row.get("bmt_student_id", "")
                if bid:
                    existing_by_bmt[bid] = (int(row["student_id"]), row["student_name"])

    award = "Distinguished HM (Top 20%)"
    new_rows = []
    for bmt_id, source_name in DISTINGUISHED_HM:
        if bmt_id in existing_by_bmt:
            sid, canonical_name = existing_by_bmt[bmt_id]
        else:
            sid, canonical_name = resolve_student(source_name, by_name, next_id, new_students)
        row = {
            "student_id": sid,
            "student_name": canonical_name,
            "year": 2025,
            "subject": "Geometry",
            "bmt_student_id": bmt_id,
            "team_name": "",
            "school": "",
            "award": award,
            "rank": "",
            "score": "",
            "mcp_rank": "",
        }
        new_rows.append(row)

    # Avoid duplicates: same bmt_student_id + award
    existing_bmt_awards = {(r["bmt_student_id"], r["award"]) for r in existing_rows}
    to_append = [
        r for r in new_rows
        if (r["bmt_student_id"], r["award"]) not in existing_bmt_awards
    ]

    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(existing_rows)
        w.writerows(to_append)

    print(f"Appended {len(to_append)} Geometry Distinguished HM rows to {RESULTS_CSV}")

    if new_students:
        with open(STUDENTS_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            for sid, name, state in new_students:
                w.writerow([sid, name, state, "", "", "", ""])
        print(f"Appended {len(new_students)} new students to {STUDENTS_CSV}")
    else:
        print("No new students added.")


if __name__ == "__main__":
    main()
