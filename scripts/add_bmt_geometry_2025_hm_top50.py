#!/usr/bin/env python3
"""
Add BMT 2025 Honorable Mention (Top 50%) to results.csv.
Resolves student_id from students.csv and existing bmt-geometry results; appends new students as needed.
"""
import csv
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDENTS_CSV = os.path.join(REPO_ROOT, "database", "students", "students.csv")
RESULTS_CSV = os.path.join(REPO_ROOT, "database", "contests", "bmt-geometry", "year=2025", "results.csv")

# Honorable Mention (Top 50%) from user input: bmt_student_id, name
HONORABLE_MENTION = [
    ("001E", "Lawrence Zhao"),
    ("002F", "Revaant Srivastav"),
    ("012A", "Amber Mo"),
    ("014A", "Aariv Aggarwal"),
    ("015A", "Mahi Kumar"),
    ("016A", "Rishabh Thakur"),
    ("016C", "Grant Ho"),
    ("018F", "Bidith Chatterjee"),
    ("033C", "Ashwin Ganapathi"),
    ("037D", "Avi Shirgur"),
    ("037E", "Yash Ambasta"),
    ("040B", "Pengyu Chen"),
    ("040E", "Jason Wang"),
    ("044B", "Aria Sanil"),
    ("044F", "Alice Wang"),
    ("050A", "Zenan Li"),
    ("050E", "Derek Liu"),
    ("052F", "Nayeon Moon"),
    ("054C", "Ethan K Song"),
    ("060D", "Kristen Zhou"),
    ("063D", "Xuehan Zhang"),
    ("073E", "Adam Fang"),
    ("083B", "Atticus Masuzawa"),
    ("092D", "Haofang Zhu"),
    ("096C", "Eli Chen"),
    ("096D", "Yuze Zheng"),
    ("096E", "Gavin Wang"),
    ("097B", "Dennis Yang"),
    ("107E", "Janet Guan"),
    ("108D", "Ethan Yan"),
    ("109A", "Anish Agarwal"),
    ("117D", "Jasper Leung"),
    ("117F", "Ethan Han"),
    ("119A", "Caroline Yuan"),
    ("127B", "Emily Wu"),
    ("128B", "Johnson Peng"),
    ("128D", "Ethan Han"),
    ("129D", "Brandon Zhu"),
    ("138F", "Andy Wu"),
    ("142A", "Ansh Taneja"),
    ("143A", "Mihika Bobbarjung"),
    ("143C", "Kevin Zhang"),
    ("144A", "Zixi Zhang"),
    ("150B", "Allinah Zhan"),
    ("151D", "Dylan Shao"),
    ("151E", "Kevin Lu"),
    ("155E", "Zeen Zheng"),
    ("156A", "Arjun Khokhar"),
    ("157B", "Ayden Bi"),
    ("157D", "Michael Shi"),
    ("157F", "Johann Qiu"),
    ("162A", "Satyaki Sen"),
    ("169D", "Daniel Li"),
    ("176F", "Nandan Surabhi"),
    ("177F", "Aarav Mann"),
    ("180D", "Kristiyan Kurtev"),
    ("180E", "Lily Peng"),
    ("184B", "Andrew Shin"),
    ("184E", "Daniel Zhu"),
    ("190D", "Anshul Panda"),
    ("193C", "Yamei Li"),
    ("199C", "Yichen Wu"),
    ("201E", "Tiancheng Zheng"),
    ("205A", "Jason Yuan"),
    ("216B", "Aditya Hariharan"),
    ("216D", "Sean Gao"),
    ("219F", "Sabina Erkbol"),
    ("221F", "Fan Jin"),
    ("223A", "Steven Shu"),
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

    print(f"Appended {len(to_append)} Geometry Honorable Mention (Top 50%) rows to {RESULTS_CSV}")

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
