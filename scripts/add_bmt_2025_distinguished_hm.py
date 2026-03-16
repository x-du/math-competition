#!/usr/bin/env python3
"""
Add BMT 2025 General Test Distinguished HM (Top 20%) to results.csv.
Resolves student_id from students.csv; appends new students as needed.
"""
import csv
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDENTS_CSV = os.path.join(REPO_ROOT, "database", "students", "students.csv")
RESULTS_CSV = os.path.join(REPO_ROOT, "database", "contests", "bmt", "year=2025", "results.csv")

# Distinguished HM (Top 20%) from user input: bmt_student_id, name
DISTINGUISHED_HM = [
    ("002B", "Haani Khurshid"),
    ("002E", "Linus Tan"),
    ("003B", "Peilin Cao"),
    ("003E", "Samir Acharya"),
    ("007A", "Shivsai Sharda"),
    ("007B", "Sayan Roy"),
    ("011A", "Eddie Wei"),
    ("011B", "Seojin Lee"),
    ("022C", "Ethan Huang"),
    ("029D", "Ethan Mui"),
    ("029F", "Jackson Lei"),
    ("040C", "Minwei Chen"),
    ("041C", "Jonathan Yu"),
    ("043B", "Avi Malhotra"),
    ("057B", "Andy Xing"),
    ("059E", "Uy Nguyen"),
    ("061B", "Yixuan Dai"),
    ("061C", "James Hang"),
    ("062C", "Evan Jiang"),
    ("062D", "Evelyn Wang"),
    ("063E", "Brian Su"),
    ("065A", "Saatvik Chauhan"),
    ("065B", "Anrui Hong"),
    ("069B", "Anirrudha Shivakumara"),
    ("074B", "Ananya Garg"),
    ("076D", "Ibrahim Nadeem"),
    ("079B", "Sebastian Liang"),
    ("079C", "Henry Deng"),
    ("079D", "Ronald Wang"),
    ("081B", "Arjun Shivakumar"),
    ("094D", "Jasmine Ge"),
    ("102A", "Batu Bozdag"),
    ("104C", "Zejia Lai"),
    ("106B", "Chaehwan Lee"),
    ("110E", "Ishaan Kabra"),
    ("113A", "Oliver Lu"),
    ("117B", "Minglang Li"),
    ("117E", "Matthew Wang"),
    ("118A", "Yi Wang"),
    ("118B", "Minxing Yang"),
    ("118D", "Jinghan Chu"),
    ("118E", "Arthur Chang"),
    ("119B", "Steven Yang"),
    ("119E", "Melissa Zhao"),
    ("120A", "Aaron Guan"),
    ("120D", "Fred Huang"),
    ("120E", "Bokai Yan"),
    ("125B", "Muyi Chen"),
    ("126B", "Boyan Han"),
    ("132B", "Chunyue Yi"),
    ("138C", "Anay Mehta"),
    ("139A", "Vyom Aggarwal"),
    ("139C", "Aahlad Bysani"),
    ("147A", "Andrew Xu"),
    ("147B", "Brian Ma"),
    ("147C", "Daniel Luo"),
    ("147D", "Pinmo Yu"),
    ("153B", "Sabrina Wang"),
    ("158E", "Pranay Bokde"),
    ("163B", "Eason Li"),
    ("163C", "Brian Hii"),
    ("163D", "Asher Luo"),
    ("164A", "Rajit Pandey"),
    ("164B", "Alexander Braun"),
    ("164C", "Temujin Battulga"),
    ("164D", "Advik Garg"),
    ("166B", "Rosie Pan"),
    ("166C", "Angela Chen"),
    ("166D", "Zi-Jie(Thomas) Ni"),
    ("166F", "Liana Lee"),
    ("168A", "Rebeca Costin"),
    ("168C", "Alexander Widjaja"),
    ("173B", "Akshay Thirumalai Vijaysrinivasan"),
    ("174B", "Parnika Gupta"),
    ("178C", "Charlene Li"),
    ("178E", "Ruoqi Li"),
    ("182A", "Leo Zhang"),
    ("182D", "Kevin He"),
    ("183A", "Rohan Rajaram"),
    ("183C", "Bartu Milci"),
    ("194B", "Nathaniel Lee"),
    ("194E", "Anika Sharma"),
    ("195C", "Jiayuan Fu"),
    ("195F", "Angie Li"),
    ("198A", "Raymond Li"),
    ("198E", "Isabelle Wang"),
    ("200A", "Edward Han"),
    ("200B", "Chloe So"),
    ("200C", "Vincent Huang"),
    ("200D", "Gilbert Jiang"),
    ("200E", "Alexander Shi"),
    ("201B", "Eva Lin"),
    ("202E", "Jacob Liu"),
    ("202F", "Tiffany Han"),
    ("210C", "Ruikang Wang"),
    ("216C", "Shaurya Chauhan"),
    ("216E", "Sri Sumukh Vulava"),
    ("219B", "Sri Shubhaan Vulava"),
    ("220E", "Yuantao Tang"),
    ("223E", "Alex Zha"),
    ("230A", "Olivia Kim"),
    ("231F", "Chris She"),
    ("233A", "Matt Li"),
    ("236C", "Zhengyin Zhu"),
    ("238A", "Ella Zheng"),
    ("238E", "Natalie Yao"),
    ("238F", "Vishakha Shastri"),
    ("241A", "Derek Hu"),
    ("241F", "Mason Shu"),
    ("243A", "Kevin Zhu"),
    ("243C", "Kartik Gudapati"),
    ("244F", "Sophia Fan"),
    ("248F", "Alyssa Li"),
    ("251B", "Richard Zheng"),
    ("251D", "Michael Zhao"),
    ("254C", "Dashan Liu"),
    ("255A", "Marvin Liang"),
    ("255F", "Aiden Chen"),
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

    new_rows = []
    for bmt_id, source_name in DISTINGUISHED_HM:
        sid, canonical_name = resolve_student(source_name, by_name, next_id, new_students)
        row = {
            "student_id": sid,
            "student_name": canonical_name,
            "year": 2025,
            "subject": "General",
            "bmt_student_id": bmt_id,
            "team_name": "",
            "school": "",
            "award": "Distinguished HM (Top 20%)",
            "rank": "",
            "score": "",
            "mcp_rank": "",
        }
        new_rows.append(row)

    # Load existing results
    existing_rows = []
    fieldnames = [
        "student_id", "student_name", "year", "subject", "bmt_student_id",
        "team_name", "school", "award", "rank", "score", "mcp_rank"
    ]
    if os.path.exists(RESULTS_CSV):
        with open(RESULTS_CSV, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            existing_rows = list(r)

    # Append new rows (avoid duplicates: same bmt_student_id + Distinguished HM)
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

    print(f"Appended {len(to_append)} Distinguished HM rows to {RESULTS_CSV}")

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
