#!/usr/bin/env python3
"""
Add BMT 2025 General Test Honorable Mention (Top 50%) to results.csv.
Resolves student_id from students.csv; appends new students as needed.
"""
import csv
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDENTS_CSV = os.path.join(REPO_ROOT, "database", "students", "students.csv")
RESULTS_CSV = os.path.join(REPO_ROOT, "database", "contests", "bmt", "year=2025", "results.csv")

# Honorable Mention (Top 50%) from user input: bmt_student_id, name
HONORABLE_MENTION = [
    ("003A", "Mihir Modi"),
    ("003C", "Matthew Yang"),
    ("003D", "Sean Yue"),
    ("004B", "Radhika Shah"),
    ("005B", "Aneeka Rao"),
    ("006B", "Evelyn Shen"),
    ("006F", "Shanmugam Valliappan"),
    ("007C", "Ananya Nagar"),
    ("009B", "Phil Zou"),
    ("009C", "Aaron Jian"),
    ("009D", "Daniel Hu"),
    ("009F", "Aaron Lung"),
    ("010C", "Nihal Tej Gundu"),
    ("010E", "Aagam Doshi"),
    ("015B", "Max Zhang"),
    ("015C", "Ameen Patel"),
    ("026B", "Arjun Garg"),
    ("028A", "Kinshuk Pandey"),
    ("028E", "Samanvay Srivatsa"),
    ("030A", "Reyansh Sadhu"),
    ("031B", "Lucas Kim"),
    ("032B", "Dylan Zhong"),
    ("033A", "Siddharth Suresh"),
    ("033D", "Vedant Srivastava"),
    ("034A", "Ishaan Chaubal"),
    ("036A", "Caleb McEuen"),
    ("042E", "Andrew Park"),
    ("043A", "Arnold Zou"),
    ("043C", "Liam Kao"),
    ("043D", "Aarav Agarwal"),
    ("043E", "Raghav Joshi"),
    ("047A", "Andrew Qian"),
    ("047B", "Avyank Vanamali"),
    ("048D", "Ivan Habib"),
    ("048E", "Nathan Wu"),
    ("049C", "Nihtahli Anand"),
    ("049D", "Nayanika Das Roy"),
    ("057C", "Riyansh Goyal"),
    ("058B", "Aarav Kachudhane"),
    ("059B", "Minh Pham"),
    ("059D", "Kayla Bui"),
    ("059F", "Dang Pham"),
    ("060A", "Nikhil Tharakan"),
    ("060C", "Kyle Huang"),
    ("061A", "Daniel Zhang"),
    ("061D", "Max Pershin"),
    ("064C", "Kevin Lu"),
    ("068A", "Veer Singh"),
    ("068C", "Claire Zhao"),
    ("068D", "Ritam Adhikari"),
    ("069A", "Darshan Chaudhari"),
    ("069E", "Ishaan Ladha"),
    ("076B", "Haramrit Bal"),
    ("076C", "Maulik Rastogi"),
    ("076F", "Siddharth Krishna"),
    ("077A", "Ryan Yan"),
    ("077C", "Andrew Ho"),
    ("077D", "Vihaan Eusebius"),
    ("077E", "Aaron Ely"),
    ("078A", "Siddhi Jain"),
    ("078C", "Grace Zuo"),
    ("080A", "Eric Chen"),
    ("080C", "Caroline Zeng"),
    ("080D", "Cynthia Lu"),
    ("080E", "Trevor Liu"),
    ("081A", "Leaya Chen"),
    ("081D", "Nora Li"),
    ("082B", "Atishar Verma"),
    ("084A", "Baer Berlinski"),
    ("086B", "Henry Lo"),
    ("086D", "Kaden Leong"),
    ("087C", "Chloe Jin"),
    ("087F", "Emma Jin"),
    ("090A", "Inesh Chhabra"),
    ("090F", "Michael Zhao"),
    ("094A", "Sebastian Hong"),
    ("094B", "Aria Krishnamoorthy"),
    ("094C", "Aahana Pilani"),
    ("096A", "Andrew Liang"),
    ("098F", "Sofie Budman"),
    ("099A", "Zixuan Xu"),
    ("099D", "Samarth Iyer"),
    ("102B", "Jithesh Manoj"),
    ("102F", "Jenil Dalal"),
    ("105A", "Jazib Akram"),
    ("105B", "Nikhil Marepally"),
    ("106A", "Austin Lin"),
    ("109E", "Aayush Kothari"),
    ("111B", "Anant Kuppa"),
    ("112A", "Yiting Xu"),
    ("115C", "Daniel Tanguay"),
    ("116D", "Kareena Zheng"),
    ("116E", "Shirochka Janapati"),
    ("118C", "Sophia Wang"),
    ("119D", "Gavin Suen"),
    ("120C", "Ruijia Shang"),
    ("124A", "Aaron Lin"),
    ("124B", "Julie Ye"),
    ("124D", "Shyam Shroff"),
    ("130C", "Harsevran Bhullar"),
    ("134A", "Sonakshi Giri"),
    ("137B", "Ellen Yang"),
    ("138E", "Nate Arkin"),
    ("140C", "Sujay Adluri"),
    ("141B", "Anup Shanbhag"),
    ("141C", "Sumner Karr"),
    ("141D", "Mukundh Varadharaju Aravindh"),
    ("141F", "Paul Sopin"),
    ("148B", "Michael Hou"),
    ("148D", "Katie Hou"),
    ("153E", "Vladislav Khitrov"),
    ("156E", "Benjamin Ha"),
    ("158A", "Noah Song"),
    ("158C", "Arin Silva"),
    ("158D", "Saharsh Myneni"),
    ("158F", "Niral Poongovan"),
    ("163A", "James Liang-Cheng"),
    ("163F", "Reece Ng"),
    ("168B", "Aaroosh Basu"),
    ("174E", "Ashley Shen"),
    ("178A", "Victoria Ho"),
    ("178B", "Jinxian Cao"),
    ("179A", "Rex Huang"),
    ("181D", "Haoqi Xu"),
    ("182B", "Ian Lee"),
    ("182E", "Hongkang Zhao"),
    ("182F", "Sanjith Senthil"),
    ("183F", "Ethan Hao"),
    ("188B", "Riddhiman Rana"),
    ("188F", "Aarush Kommaraju"),
    ("191A", "Aryaman Majumder"),
    ("191C", "Naman Jain"),
    ("193B", "Joanna Wang"),
    ("194A", "Amy Lai"),
    ("194C", "Ryan Li"),
    ("195B", "Yash Shekhawat"),
    ("196B", "Jude Tecson"),
    ("196F", "Lakshmana Medam"),
    ("198B", "Kevin Zhong"),
    ("198C", "Celena So"),
    ("198D", "Anirvin Alapati"),
    ("202B", "Haoyun Yu"),
    ("203C", "Srinika Laha"),
    ("203E", "Christopher Lum"),
    ("204A", "Nicholas Simon"),
    ("206B", "Alden Raymond"),
    ("206C", "Hwan Chung"),
    ("208A", "Jonathan Chen"),
    ("209A", "Shihan Feng"),
    ("209E", "Leo Peng"),
    ("210B", "Nathan Han"),
    ("210E", "Neelkanth Brahmachari"),
    ("214A", "Vivian How"),
    ("216A", "Bella Chen"),
    ("219A", "Steven Brody"),
    ("219E", "Rishan Waghmare"),
    ("220C", "Luoyi Zhang"),
    ("226A", "Jiho Choi"),
    ("226B", "Dristi Roy"),
    ("227C", "Alex Soman"),
    ("229C", "Seyth Jain"),
    ("231B", "Aaden Medina"),
    ("231D", "Stephan Zhao"),
    ("232A", "Yixuan Wang"),
    ("232C", "Aarnav Kumta"),
    ("232D", "Hudson Rondonuwu"),
    ("234B", "Sophia Hao"),
    ("235B", "Kalkin Gandhi"),
    ("235D", "Saarang Agarwal"),
    ("237A", "Chloe Chen"),
    ("237C", "Arjun Rayankula"),
    ("240A", "Wenbo Xi"),
    ("240E", "Wenyuan Xi"),
    ("241C", "Astin Zhou"),
    ("241E", "Alber Wu"),
    ("243F", "Ashmit Arasada"),
    ("246B", "Thomas Nguyen"),
    ("251A", "Victor Wei"),
    ("251E", "Ruiyang Jiang"),
    ("252C", "Robert Wang"),
    ("252F", "Shivan Pordel"),
    ("254D", "David Li"),
    ("255E", "Pranav Tripathi"),
    ("256A", "Vishwesh Chinthukumar"),
    ("262C", "Srinadh Yenamandra"),
    ("264C", "Lucas Xu"),
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
    for bmt_id, source_name in HONORABLE_MENTION:
        sid, canonical_name = resolve_student(source_name, by_name, next_id, new_students)
        row = {
            "student_id": sid,
            "student_name": canonical_name,
            "year": 2025,
            "subject": "General",
            "bmt_student_id": bmt_id,
            "team_name": "",
            "school": "",
            "award": "Honorable Mention (Top 50%)",
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

    # Append new rows (avoid duplicates: same bmt_student_id + award)
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

    print(f"Appended {len(to_append)} Honorable Mention rows to {RESULTS_CSV}")

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
