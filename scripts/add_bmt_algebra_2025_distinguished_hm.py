#!/usr/bin/env python3
"""
Add BMT 2025 Distinguished HM (Top 20%) to results.csv.
Resolves student_id from students.csv and existing bmt-algebra results; appends new students as needed.
"""
import csv
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDENTS_CSV = os.path.join(REPO_ROOT, "database", "students", "students.csv")
RESULTS_CSV = os.path.join(REPO_ROOT, "database", "contests", "bmt-algebra", "year=2025", "results.csv")

# Distinguished HM (Top 20%) from user input: bmt_student_id, name
DISTINGUISHED_HM = [
    ("001B", "Luca Busracamwongs"),
    ("001E", "Lawrence Zhao"),
    ("004D", "Pranav Krishnapuram"),
    ("011C", "Elena Beckman"),
    ("013A", "Brett Chang"),
    ("013B", "Evan Li"),
    ("013C", "Max Zhou"),
    ("013D", "Angela Wang"),
    ("016D", "Prashanth Prabhala"),
    ("018A", "Harshith Sai Mannaru"),
    ("018F", "Bidith Chatterjee"),
    ("019A", "Alvin Yu"),
    ("024B", "Shiven Bhargava"),
    ("029B", "Bryant Wang"),
    ("032C", "Alexannder Kong"),
    ("038D", "Kai Lidzborski"),
    ("040B", "Pengyu Chen"),
    ("041A", "Julian Kuang"),
    ("041B", "Aaron Lei"),
    ("041D", "Ethan Chan"),
    ("044B", "Aria Sanil"),
    ("044F", "Alice Wang"),
    ("048B", "Lucas (Zihe) Wang"),
    ("048C", "Nolan Lin"),
    ("053A", "Dylan Kim"),
    ("053B", "Kaden Wu"),
    ("053E", "Rebecca Luo"),
    ("054E", "Sepehr Golsefidy"),
    ("055A", "Aarav Ashwani"),
    ("073A", "Tianran Li"),
    ("073E", "Adam Fang"),
    ("074D", "Ryan Wang"),
    ("086F", "Zhoulei (Charlie) Huang"),
    ("088B", "Aditya Singla"),
    ("089C", "Ayush Bansal"),
    ("089D", "Iurii Kirpichev"),
    ("089E", "Harish Loghashankar"),
    ("089F", "Niranjan Rao"),
    ("090B", "Brandon Young"),
    ("091C", "Ziqi (Lisa) Zheng"),
    ("092A", "Royce Yao"),
    ("092C", "Feodor Yevtushenko"),
    ("092D", "Haofang Zhu"),
    ("092E", "Jonathan Duh"),
    ("092F", "Connor Leong"),
    ("093F", "Thomas Della Vigna"),
    ("096D", "Yuze Zheng"),
    ("097F", "Arthur Li"),
    ("107A", "Jessica Yan"),
    ("107B", "Troy Yang"),
    ("107C", "Jeffrey Li"),
    ("107E", "Janet Guan"),
    ("107F", "Ali Zaman"),
    ("108A", "Aniket Mangalampalli"),
    ("108B", "Hank SUN"),
    ("108E", "Andy Liu"),
    ("108F", "Advaith Mopuri"),
    ("109B", "Hamsini Vegi"),
    ("110C", "Rutvik Arora"),
    ("111E", "Brian Zhao"),
    ("112D", "Weiyang Liu"),
    ("113B", "Ethan Mak"),
    ("113D", "Michael Jian"),
    ("122B", "Kevin Li"),
    ("122D", "Aidan Shin"),
    ("122F", "melissa yu"),
    ("126C", "Jeffrey Ding"),
    ("127F", "Lawson Wang"),
    ("128C", "Jiaheng Li"),
    ("142B", "Vihaan Byahatti"),
    ("144A", "Zixi Zhang"),
    ("144C", "Mingyue Yang"),
    ("144D", "Christopher Peng"),
    ("144F", "Benjamin Fu"),
    ("148A", "Tate Nomura"),
    ("150B", "Allinah Zhan"),
    ("150F", "Jake Hu"),
    ("153D", "Sahasra Chappidi"),
    ("157A", "Anlong Liu"),
    ("159C", "Vedanth Chakravarthi"),
    ("161A", "Jingxuan Bo"),
    ("161B", "Max Li"),
    ("161C", "Eric Shu"),
    ("161D", "Atticus Lin"),
    ("161E", "Ashwin Shekhar"),
    ("162B", "William Xiao"),
    ("162C", "Lucas Lin"),
    ("162D", "Calvin Strohmann"),
    ("162F", "Gareth Lee"),
    ("163E", "Brian Lai"),
    ("164F", "Ruoyu Zhou"),
    ("165A", "Shihan Kanungo"),
    ("165C", "Eddy Li"),
    ("165F", "Sohil Rathi"),
    ("167A", "Jason Yang"),
    ("167B", "Dylan Wang"),
    ("167C", "Alex Tsagaan"),
    ("167D", "Justin Kim"),
    ("167F", "Bosman Botha"),
    ("169A", "Tianlin Liu"),
    ("174A", "Zukhil Subramanian"),
    ("176B", "Tarun Gandhi"),
    ("176C", "Vivaan Daxini"),
    ("176E", "Derek Li"),
    ("176F", "Nandan Surabhi"),
    ("177F", "Aarav Mann"),
    ("179C", "Lucas Wu"),
    ("180C", "Jonathan Li"),
    ("181E", "David He"),
    ("182C", "Eric Dong"),
    ("184C", "Cameron Rampell"),
    ("186A", "Yingkai Shao"),
    ("186C", "Vedanth Dala"),
    ("190E", "Yanxun Pu"),
    ("190F", "Amy Fang"),
    ("191D", "Richard Li"),
    ("199A", "Alex Zhan"),
    ("199B", "Mittansh Bhatia"),
    ("199D", "Nathan Chen"),
    ("199E", "Mehul Biala"),
    ("202C", "Leo Zeng"),
    ("205C", "David Liu"),
    ("206E", "Alexander Ruan"),
    ("211A", "Daniel Nie"),
    ("211B", "Dalbert Wu"),
    ("211C", "Rohan Garg"),
    ("211D", "Ryan Fu"),
    ("211E", "Kailua Cheng"),
    ("211F", "Seojin Kim"),
    ("215A", "Ethan Bao"),
    ("216D", "Sean Gao"),
    ("218D", "Jacob Lee"),
    ("221D", "Krittika Chandra"),
    ("222A", "Inhoo Chang"),
    ("222C", "Raymond Zhou"),
    ("228A", "Nicholas Weng"),
    ("228B", "Daniel Jin"),
    ("229A", "Leonardo Nguyen"),
    ("232E", "Pratham Prasanna"),
    ("236A", "Chenghao HU"),
    ("236B", "Liyan Xu"),
    ("236E", "Raymond Feng"),
    ("238B", "Akshatha Arunkumar"),
    ("242A", "NitinReddy Vaka"),
    ("242C", "Sohum Uttamchandani"),
    ("242D", "Ryan Wang"),
    ("242E", "Benjamin Zhang"),
    ("242F", "Abhigyan Singh"),
    ("244C", "Henry Wang"),
    ("244E", "Yunfei Xia"),
    ("248D", "Ryan Lu"),
    ("250C", "Karthik Pasupuleti"),
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
    # Try Chenghao HU -> Chenghao Hu style
    if key == "chenghao hu":
        if "chenghao hu" in by_name:
            candidates = by_name["chenghao hu"]
            sid, canonical_name, _ = candidates[0]
            return sid, canonical_name
    # Try parenthetical name variants
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
            "subject": "Algebra",
            "bmt_student_id": bmt_id,
            "team_name": "",
            "school": "",
            "award": "Distinguished HM (Top 20%)",
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

    print(f"Appended {len(to_append)} Algebra Distinguished HM rows to {RESULTS_CSV}")

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
