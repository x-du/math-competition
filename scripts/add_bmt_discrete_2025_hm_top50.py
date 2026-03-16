#!/usr/bin/env python3
"""
Add BMT 2025 Honorable Mention (Top 50%) to results.csv.
Resolves student_id from students.csv and existing bmt-discrete results; appends new students as needed.
"""
import csv
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDENTS_CSV = os.path.join(REPO_ROOT, "database", "students", "students.csv")
RESULTS_CSV = os.path.join(REPO_ROOT, "database", "contests", "bmt-discrete", "year=2025", "results.csv")

# Honorable Mention (Top 50%) from user input: bmt_student_id, name
HONORABLE_MENTION = [
    ("001B", "Luca Busracamwongs"),
    ("004C", "Aarushi Srivastava"),
    ("005E", "Nikita Das"),
    ("015A", "Mahi Kumar"),
    ("016B", "Rithwik Gupta"),
    ("016E", "Roland Pratt"),
    ("023C", "Mehul Bhattacharya"),
    ("024D", "Caden Claussen"),
    ("032D", "Ziming Tang"),
    ("044C", "Joshua Koo"),
    ("044D", "William Sun"),
    ("044E", "Surbhi Sakshi"),
    ("050D", "Hoang Dang"),
    ("051A", "Junu Pae"),
    ("051C", "Smaran Mukkavilli"),
    ("051D", "Junwon Jahng"),
    ("053F", "Zhenghua Xie"),
    ("054A", "Katrina Liu"),
    ("054C", "Ethan K Song"),
    ("063C", "Chris Chen"),
    ("083C", "James Browning"),
    ("083D", "Nikhil McGowan"),
    ("088E", "Laura Chen"),
    ("089E", "Harish Loghashankar"),
    ("091C", "Ziqi (Lisa) Zheng"),
    ("091D", "Alexander Yoon"),
    ("092E", "Jonathan Duh"),
    ("093B", "Utsav Lal"),
    ("093F", "Thomas Della Vigna"),
    ("095F", "Elizabeth Ying"),
    ("097E", "Wenhai Rong"),
    ("098C", "Jasper Verma"),
    ("107A", "Jessica Yan"),
    ("108F", "Advaith Mopuri"),
    ("109F", "Ethan Chen"),
    ("110D", "Jonathan Yang"),
    ("110F", "Edward Zeng"),
    ("112D", "Weiyang Liu"),
    ("113D", "Michael Jian"),
    ("117D", "Jasper Leung"),
    ("122C", "Brandon Chiu"),
    ("122F", "melissa yu"),
    ("128D", "Ethan Han"),
    ("134B", "Jacob Kawako"),
    ("142A", "Ansh Taneja"),
    ("142C", "Justin Cheong"),
    ("142D", "Caleb Loh"),
    ("148A", "Tate Nomura"),
    ("150A", "Yury Bychkov"),
    ("150D", "Aiden Shan"),
    ("156D", "Yujun Lee"),
    ("161B", "Max Li"),
    ("162A", "Satyaki Sen"),
    ("162B", "William Xiao"),
    ("162C", "Lucas Lin"),
    ("164E", "Yakup Pala"),
    ("166E", "Paixiao Seeluangsawat"),
    ("169F", "Katherine Li"),
    ("171A", "Isha Marthi"),
    ("171C", "Arav Bansal"),
    ("174C", "Alan Lin"),
    ("177B", "Lucas Yuan"),
    ("179B", "Benjamin Li"),
    ("180D", "Kristiyan Kurtev"),
    ("180F", "Elaine Xu"),
    ("181A", "Guiqing Eric Zhang"),
    ("181C", "Rafa deGoma"),
    ("184F", "Pascal Qin"),
    ("190A", "Ryan Li"),
    ("191E", "Sachit Hegde"),
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

    print(f"Appended {len(to_append)} Discrete Honorable Mention (Top 50%) rows to {RESULTS_CSV}")

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
