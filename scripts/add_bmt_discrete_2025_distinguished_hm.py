#!/usr/bin/env python3
"""
Add BMT 2025 Distinguished HM (Top 20%) to results.csv.
Resolves student_id from students.csv and existing bmt-discrete results; appends new students as needed.
"""
import csv
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDENTS_CSV = os.path.join(REPO_ROOT, "database", "students", "students.csv")
RESULTS_CSV = os.path.join(REPO_ROOT, "database", "contests", "bmt-discrete", "year=2025", "results.csv")

# Distinguished HM (Top 20%) from user input: bmt_student_id, name
DISTINGUISHED_HM = [
    ("011C", "Elena Beckman"),
    ("013C", "Max Zhou"),
    ("016C", "Grant Ho"),
    ("024B", "Shiven Bhargava"),
    ("044A", "Aiden Zeng"),
    ("048B", "Lucas (Zihe) Wang"),
    ("048F", "Franklin Zhou"),
    ("051B", "Thomas Liu"),
    ("051F", "Rishav Bhattacharjee"),
    ("053C", "Kevin Yang"),
    ("054B", "Aidan Bai"),
    ("054D", "Rohan Mallick"),
    ("054F", "Xiaoran Han"),
    ("055A", "Aarav Ashwani"),
    ("063B", "Matthew Hsiao"),
    ("063F", "Alex Chen"),
    ("068B", "Elaine Gu"),
    ("079A", "Keith Li"),
    ("079F", "Kai Lum"),
    ("083E", "Thomas McCurley"),
    ("086C", "Eric Aranjo"),
    ("086F", "Zhoulei (Charlie) Huang"),
    ("089A", "Amy Zhang"),
    ("092A", "Royce Yao"),
    ("092B", "David Fox"),
    ("092C", "Feodor Yevtushenko"),
    ("092F", "Connor Leong"),
    ("093D", "Amelia Chen"),
    ("101F", "Arjun Kenthapadi"),
    ("103B", "Athithan Elamaran"),
    ("107B", "Troy Yang"),
    ("107F", "Ali Zaman"),
    ("111E", "Brian Zhao"),
    ("113B", "Ethan Mak"),
    ("113C", "Terry Huang"),
    ("117C", "William Xin"),
    ("122A", "Bowen Wu"),
    ("127D", "Andy Lu"),
    ("144B", "Erin Bian"),
    ("144C", "Mingyue Yang"),
    ("144E", "Hannah Ma"),
    ("155C", "Camea Caprita"),
    ("157C", "Carter Cai"),
    ("159C", "Vedanth Chakravarthi"),
    ("162D", "Calvin Strohmann"),
    ("162F", "Gareth Lee"),
    ("165B", "Ryan Bansal"),
    ("165D", "Jonathan Du"),
    ("165F", "Sohil Rathi"),
    ("167F", "Bosman Botha"),
    ("169D", "Daniel Li"),
    ("176C", "Vivaan Daxini"),
    ("177A", "Andrew Shi"),
    ("177C", "Vihaan Gupta"),
    ("180B", "Sylvia Chen"),
    ("180C", "Jonathan Li"),
    ("181E", "David He"),
    ("184A", "Shamik Khowala"),
    ("184E", "Daniel Zhu"),
    ("190D", "Anshul Panda"),
    ("190F", "Amy Fang"),
    ("199B", "Mittansh Bhatia"),
    ("199D", "Nathan Chen"),
    ("200F", "Timothy Li"),
    ("205A", "Jason Yuan"),
    ("211B", "Dalbert Wu"),
    ("211C", "Rohan Garg"),
    ("211D", "Ryan Fu"),
    ("211F", "Seojin Kim"),
    ("215A", "Ethan Bao"),
    ("219C", "Aryan Naik"),
    ("221C", "Oscar Varodayan"),
    ("221D", "Krittika Chandra"),
    ("222E", "Leia Lin"),
    ("224C", "Zhendi Cao"),
    ("227A", "Aiden Jeong"),
    ("228A", "Nicholas Weng"),
    ("232E", "Pratham Prasanna"),
    ("233B", "Leo Tsai"),
    ("236A", "Chenghao HU"),
    ("236D", "Yuan Xing"),
    ("238B", "Akshatha Arunkumar"),
    ("242A", "NitinReddy Vaka"),
    ("242B", "Ben Oh"),
    ("242C", "Sohum Uttamchandani"),
    ("242E", "Benjamin Zhang"),
    ("248C", "Keshav Venkatesh"),
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
            "subject": "Discrete",
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

    print(f"Appended {len(to_append)} Discrete Distinguished HM rows to {RESULTS_CSV}")

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
