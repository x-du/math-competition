#!/usr/bin/env python3
"""
Add BMT 2025 Honorable Mention (Top 50%) to results.csv.
Resolves student_id from students.csv and existing bmt-algebra results; appends new students as needed.
"""
import csv
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDENTS_CSV = os.path.join(REPO_ROOT, "database", "students", "students.csv")
RESULTS_CSV = os.path.join(REPO_ROOT, "database", "contests", "bmt-algebra", "year=2025", "results.csv")

# Honorable Mention (Top 50%) from user input: bmt_student_id, name
HONORABLE_MENTION = [
    ("004E", "Prerana Manekar"),
    ("005E", "Nikita Das"),
    ("006D", "Brian Qin"),
    ("012A", "Amber Mo"),
    ("012B", "Rutvi Mudalagi"),
    ("013E", "Alexa Chang"),
    ("013F", "Yash Jaju"),
    ("014A", "Aariv Aggarwal"),
    ("014D", "Tanvi Nasika"),
    ("015E", "Arjun Pillai"),
    ("015F", "Saketh Elumalai"),
    ("017A", "Shiva Srinath"),
    ("017B", "Ishaan Patel"),
    ("017C", "Anish Yarrakonda"),
    ("019C", "Xiaoxing Zhou"),
    ("020F", "Thomas Huang"),
    ("022E", "Divya Raghuraman"),
    ("023A", "Avi Agarwal"),
    ("023D", "Anaye Agrawal"),
    ("028F", "Steven Qi"),
    ("031D", "Forrest Su"),
    ("032D", "Ziming Tang"),
    ("037B", "Cailyn Fang"),
    ("038B", "Liheng Liu"),
    ("038E", "Sitar Eswar"),
    ("040A", "Tymon Tao"),
    ("040D", "Justin Guo"),
    ("042C", "Oren Grills"),
    ("044A", "Aiden Zeng"),
    ("048A", "Hao Hsiang Chen"),
    ("050B", "Neo Zhang"),
    ("050D", "Hoang Dang"),
    ("051C", "Smaran Mukkavilli"),
    ("052C", "Zitong (Alice) Xu"),
    ("052D", "Aditya Bisain"),
    ("055B", "Sparsh Gupta"),
    ("055E", "Joshua Huang"),
    ("057A", "Pranshu Sharma"),
    ("057F", "Anish Muralikrishnan"),
    ("060D", "Kristen Zhou"),
    ("062A", "Leo Xie"),
    ("062B", "Mrinal Agarwal"),
    ("063D", "Xuehan Zhang"),
    ("064A", "Bryan Pan"),
    ("065E", "Anish Roy"),
    ("065F", "Jonathan Nguyen"),
    ("067D", "Arhaan Reddy"),
    ("067E", "Aarav Agarwal"),
    ("068B", "Elaine Gu"),
    ("073F", "Aaron Cheng"),
    ("078D", "Lexing Liu"),
    ("079A", "Keith Li"),
    ("079F", "Kai Lum"),
    ("083A", "Ryan Xie"),
    ("086C", "Eric Aranjo"),
    ("089B", "David Guo"),
    ("091D", "Alexander Yoon"),
    ("093A", "Theo Wolens"),
    ("093E", "James Micheltorena"),
    ("095C", "Jayden Gong"),
    ("095E", "Ethan Sun"),
    ("096C", "Eli Chen"),
    ("096E", "Gavin Wang"),
    ("096F", "Le Yu Yang"),
    ("097A", "Bryant Hu"),
    ("097B", "Dennis Yang"),
    ("097D", "Dylan Huang"),
    ("098C", "Jasper Verma"),
    ("101B", "Sarvesh Madullapalli"),
    ("101F", "Arjun Kenthapadi"),
    ("103B", "Athithan Elamaran"),
    ("108C", "Shuhan Li"),
    ("109A", "Anish Agarwal"),
    ("109C", "Kaavin Prasanna"),
    ("109D", "Guhan Bhagatram"),
    ("109F", "Ethan Chen"),
    ("110D", "Jonathan Yang"),
    ("112C", "Rohan Aynor"),
    ("119A", "Caroline Yuan"),
    ("120B", "Shawn Zeng"),
    ("123C", "Abhishek Jolad"),
    ("125C", "Seungheon Yoo"),
    ("125E", "Nika Svizhenko"),
    ("126A", "Jonathan Li"),
    ("126D", "Luca Perfetto"),
    ("127A", "Max Rombakh"),
    ("127E", "Seabert Mao"),
    ("129A", "Sean Guo"),
    ("142C", "Justin Cheong"),
    ("143C", "Kevin Zhang"),
    ("143D", "Julian Chaw"),
    ("150A", "Yury Bychkov"),
    ("151A", "Claire Qi"),
    ("151E", "Kevin Lu"),
    ("152A", "Ray Zhang"),
    ("154A", "Anumitha Arun"),
    ("155A", "William Xing"),
    ("155F", "Joonseok Lee"),
    ("157F", "Johann Qiu"),
    ("162E", "Shreyus Sane"),
    ("164E", "Yakup Pala"),
    ("166A", "William Tao"),
    ("166E", "Paixiao Seeluangsawat"),
    ("167E", "Jessica Hu"),
    ("169C", "Victoria Huang"),
    ("171A", "Isha Marthi"),
    ("171B", "Leia Kao"),
    ("171D", "Saranya Duggirala"),
    ("172A", "Justin Tran"),
    ("174C", "Alan Lin"),
    ("176A", "Rohan Agarwal"),
    ("176D", "Ishaan Mishra"),
    ("179F", "Alexander Maxim"),
    ("180A", "Helena Liang"),
    ("180B", "Sylvia Chen"),
    ("180E", "Lily Peng"),
    ("181A", "Guiqing Eric Zhang"),
    ("181C", "Rafa deGoma"),
    ("184A", "Shamik Khowala"),
    ("184D", "William Jiang"),
    ("186B", "Taran Ajith"),
    ("186E", "Harshil Nukala"),
    ("186F", "Daniel Liao"),
    ("187B", "Shravan Sundar"),
    ("187E", "Adit Gupta"),
    ("187F", "Vachan Bhogi"),
    ("188C", "Andrew Sun"),
    ("190A", "Ryan Li"),
    ("190C", "Jack He"),
    ("191E", "Sachit Hegde"),
    ("191F", "Vikram Snyder"),
    ("193C", "Yamei Li"),
    ("199F", "Anna Deng"),
    ("201A", "Albert Li"),
    ("201C", "Manant Kochar"),
    ("201D", "William Mao"),
    ("202A", "Evan Zhou"),
    ("202D", "Lucas Quan"),
    ("205B", "Ethan C"),
    ("209D", "Charlie Wang"),
    ("210D", "Ayan Sharma"),
    ("213D", "Praneet Udgata"),
    ("216F", "Shujun Han"),
    ("217B", "Abhrottha Roy"),
    ("217E", "Maksim Gerasimov"),
    ("217F", "Dylan Raman"),
    ("218A", "Aayaan Khandelwal"),
    ("218B", "Michelle Li"),
    ("218C", "Vihaan Paka-Hegde"),
    ("218E", "Aarnav Khandelwal"),
    ("219C", "Aryan Naik"),
    ("219F", "Sabina Erkbol"),
    ("221A", "Andrew Wen"),
    ("221F", "Fan Jin"),
    ("222B", "Albert Xu"),
    ("222E", "Leia Lin"),
    ("223D", "Brian Chung"),
    ("224D", "Jewon Shin"),
    ("228C", "Chanew Kim"),
    ("228D", "Neil Dixit"),
    ("228E", "Aarush Rachakonda"),
    ("230E", "James Dong"),
    ("230F", "Michael Ma"),
    ("231A", "Ethan Huang"),
    ("233B", "Leo Tsai"),
    ("240C", "Evan Gai"),
    ("240D", "Vincent Qin"),
    ("240F", "Sungrok Kim"),
    ("241B", "Zhaitong Wang"),
    ("243B", "Jasmine Lien"),
    ("243D", "Yutong Qiu"),
    ("248A", "Grace Gao"),
    ("248B", "Isabella Li"),
    ("260E", "Dhilan Belur"),
    ("263C", "Aoife Hennessey"),
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
            "subject": "Algebra",
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

    print(f"Appended {len(to_append)} Algebra Honorable Mention (Top 50%) rows to {RESULTS_CSV}")

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
