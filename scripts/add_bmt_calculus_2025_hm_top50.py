#!/usr/bin/env python3
"""
Add BMT 2025 Honorable Mention (Top 50%) to results.csv.
Resolves student_id from students.csv and existing bmt-calculus results; appends new students as needed.
"""
import csv
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDENTS_CSV = os.path.join(REPO_ROOT, "database", "students", "students.csv")
RESULTS_CSV = os.path.join(REPO_ROOT, "database", "contests", "bmt-calculus", "year=2025", "results.csv")

# Honorable Mention (Top 50%) from user input: bmt_student_id, name
HONORABLE_MENTION = [
    ("002F", "Revaant Srivastav"),
    ("005A", "Grace Ji"),
    ("016B", "Rithwik Gupta"),
    ("016D", "Prashanth Prabhala"),
    ("021B", "Aarav Gupta"),
    ("022D", "Alex Mo"),
    ("028F", "Steven Qi"),
    ("031D", "Forrest Su"),
    ("032A", "Natalie Song"),
    ("048A", "Hao Hsiang Chen"),
    ("057A", "Pranshu Sharma"),
    ("057E", "Ruby Yan"),
    ("060F", "Vunal Jinasundera"),
    ("068F", "Xiuqi Shi"),
    ("091A", "Thomas Li"),
    ("091B", "Annika Lee"),
    ("091E", "Wiley Mallgren"),
    ("095B", "Cris Chai"),
    ("095C", "Jayden Gong"),
    ("097E", "Wenhai Rong"),
    ("101A", "Kosei Tsukamoto"),
    ("101B", "Sarvesh Madullapalli"),
    ("107C", "Jeffrey Li"),
    ("107D", "Akshay Murthy"),
    ("108C", "Shuhan Li"),
    ("108D", "Ethan Yan"),
    ("110A", "Veer Mahajan"),
    ("113F", "Timothy Chen"),
    ("125E", "Nika Svizhenko"),
    ("127A", "Max Rombakh"),
    ("127D", "Andy Lu"),
    ("141E", "Yewon Park"),
    ("148C", "Victor Tang"),
    ("153D", "Sahasra Chappidi"),
    ("167E", "Jessica Hu"),
    ("175C", "Victor Pan"),
    ("179B", "Benjamin Li"),
    ("180A", "Helena Liang"),
    ("181F", "Sunay Miduthuri"),
    ("182C", "Eric Dong"),
    ("183B", "Ethan Weyn"),
    ("184D", "William Jiang"),
    ("186B", "Taran Ajith"),
    ("186C", "Vedanth Dala"),
    ("193D", "Emily Li"),
    ("202D", "Lucas Quan"),
    ("206A", "Zhiming Qi"),
    ("222A", "Inhoo Chang"),
    ("222B", "Albert Xu"),
    ("222C", "Raymond Zhou"),
    ("224A", "Lucas Lin"),
    ("229D", "Elliot Boyce"),
    ("230D", "Haridas Chowdhury"),
    ("230E", "James Dong"),
    ("234F", "Maggie Shen"),
    ("236F", "Peilin Lan"),
    ("240D", "Vincent Qin"),
    ("244B", "Evan Liu"),
    ("269B", "russell gehrig"),
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

    award = "Honorable Mention (Top 50%)"
    new_rows = []
    for bmt_id, source_name in HONORABLE_MENTION:
        if bmt_id in existing_by_bmt:
            sid, canonical_name = existing_by_bmt[bmt_id]
        else:
            sid, canonical_name = resolve_student(source_name, by_name, next_id, new_students)
        row = {
            "student_id": sid,
            "student_name": canonical_name,
            "year": 2025,
            "subject": "Calculus",
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

    print(f"Appended {len(to_append)} Calculus Honorable Mention (Top 50%) rows to {RESULTS_CSV}")

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
