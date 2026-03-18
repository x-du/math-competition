#!/usr/bin/env python3
"""
Add HMMT November 2024 Theme round to hmmt-nov-theme/year=2024.
Names normalized to "First_Name Last_Name". Schema: student_id, student_name, year, rank, score.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "hmmt-nov-theme" / "year=2024"

NAME_NORMALIZE = {
    "GONG YICHEN": "Yichen Gong",
    "Bowen Deng": "Bowen Deng",
    "WU,PENGYU": "PengYu Wu",
    "chen zizhuang": "Zizhuang Chen",
    "Sirawit Pipittanabanâ€‹": "Sirawit Pipittanaban",
    "Zhang Xinye": "Xinye Zhang",
}

TEAM_TO_STATE = {
    "Shanghai High School Stallions": "",
    "Bayview Team A1": "California",
    "University of Toronto Schools A": "",
    "Maple": "",
    "Individuals 2": "",
    "Individuals 5": "",
    "Beijing Forbidden City": "",
    "Bellaire A": "Texas",
    "Big L Club": "",
    "PRISMS Young Falcons": "California",
    "Ward Melville Math Team E": "New York",
    "Math School A": "",
    "Westchester Area Math Circle": "New York",
    "Phillips Academy A1": "Massachusetts",
    "Lexington Gamma": "Massachusetts",
    "Math 4 Fun": "",
    "Maryland United": "Maryland",
    "St. Paul's School": "",
    "Sugar Club": "",
    "CCHS A Team": "",
    "Swiszczypylki": "",
    "CA Chameleons": "California",
    "Davidson A": "North Carolina",
    "The NH Celestials 2": "New Hampshire",
    "Texas Thunder": "Texas",
    "The Real Prizes Were The Friends We Made Along The Way": "",
    "Wayland High": "Massachusetts",
    "Gunn Black": "California",
    "fun math": "",
    "CRLS": "Massachusetts",
    "Collegiate School": "Virginia",
    "4 Factorials": "",
    "Scarsdale C": "New York",
    "OC Math Team 1": "California",
    "Albany Area Math Circle Cardinals": "New York",
    "Tennessee Math Coalition Blue": "Tennessee",
    "AB Math League": "",
    "Texas Tornado": "Texas",
    "Paly Trolls": "California",
    "R4E-1": "",
    "TAS Math Circle": "",
    "Lexington Delta": "Massachusetts",
    "The Limit Does Not Exist": "",
    "Hotchkiss Blue": "Connecticut",
}

# (rank, score, name_as_in_paste, team)
ROWS = [
    (1, 40.24, "GONG YICHEN", "Shanghai High School Stallions"),
    (2, 37.08, "Leo Wu", "Bayview Team A1"),
    (2, 37.08, "Perry Dai", "University of Toronto Schools A"),
    (4, 32.92, "Alexander Zhang", "Maple"),
    (5, 32.67, "Aadish Jain", "Individuals 2"),
    (5, 32.67, "Joanna Wu", "Individuals 5"),
    (7, 31.81, "Bowen Deng", "Beijing Forbidden City"),
    (7, 31.81, "Jerry Zhang", "Bellaire A"),
    (9, 30.73, "Advait Joshi", "Big L Club"),
    (9, 30.73, "Yeyin Zhu", "PRISMS Young Falcons"),
    (9, 30.73, "Harry Haiwen Gao", "Ward Melville Math Team E"),
    (9, 30.73, "Anand Swaroop", "Math School A"),
    (9, 30.73, "Andrew M Kalashnikov", "Math School A"),
    (14, 30.59, "Yunong Wu", "Westchester Area Math Circle"),
    (14, 30.59, "Anji Wang", "Maple"),
    (14, 30.59, "Michael Sun", "Maple"),
    (14, 30.59, "Paige Zhu", "Phillips Academy A1"),
    (14, 30.59, "Danyang Xu", "Lexington Gamma"),
    (14, 30.59, "Aaron Zhu", "Math 4 Fun"),
    (14, 30.59, "Daniel Yu", "Maryland United"),
    (21, 29.93, "Siravit Hengsuvanich", "Phillips Academy A1"),
    (22, 27.71, "Raymond Ge", "Math 4 Fun"),
    (23, 27.65, "Matthew Qian", "CCHS A Team"),
    (24, 26.63, "Xingguo Ding", "St. Paul's School"),
    (24, 26.63, "Ryan Tang", "Lexington Gamma"),
    (26, 26.57, "Tymon Sidor", "Swiszczypylki"),
    (26, 26.57, "Sirawit Pipittanabanâ€‹", "CA Chameleons"),
    (26, 26.57, "Casey Fong", "Davidson A"),
    (29, 26.51, "Pratham Mukewar", "The NH Celestials 2"),
    (30, 26.49, "WU,PENGYU", "Sugar Club"),
    (30, 26.49, "Samuel Tsui", "Lexington Gamma"),
    (32, 26.45, "Tianxiang Zhang", "Shanghai High School Stallions"),
    (32, 26.45, "Colin Wei", "Texas Thunder"),
    (34, 26.43, "chen zizhuang", "Shanghai High School Stallions"),
    (34, 26.43, "Eric Huang", "The Real Prizes Were The Friends We Made Along The Way"),
    (36, 26.37, "Henry Han", "Wayland High"),
    (37, 26.32, "Juncheng Zhu", "Bayview Team A1"),
    (37, 26.32, "Peter Wang", "PRISMS Young Falcons"),
    (39, 26.17, "Kevin Chen", "fun math"),
    (39, 26.17, "Dongyoon Shin", "Gunn Black"),
    (39, 26.17, "Nathan Lu", "Maryland United"),
    (39, 26.17, "Charlotte Younger", "CRLS"),
    (43, 24.60, "Magdalena Pudełko", "Swiszczypylki"),
    (44, 24.24, "Joseph Peter Girotto", "Westchester Area Math Circle"),
    (44, 24.24, "Justin Y. Yu", "All Aces Spade"),
    (44, 24.24, "Christopher Lu", "Collegiate School"),
    (44, 24.24, "Adam Henry Smith", "4 Factorials"),
    (44, 24.24, "Kabir Goyal", "4 Factorials"),
    (44, 24.24, "Hans Sihan Zhu", "Shanghai High School Stallions"),
    (44, 24.24, "Gavin Guojun Zhao", "Shanghai High School Stallions"),
    (44, 24.24, "Kenneth Ren", "Scarsdale C"),
    (44, 24.24, "Zion Paul QU", "OC Math Team 1"),
    (44, 24.24, "Jason Lian", "Albany Area Math Circle Cardinals"),
    (44, 24.24, "Justin Guo", "Tennessee Math Coalition Blue"),
    (44, 24.24, "Bryan Li", "AB Math League"),
    (44, 24.24, "Aaron Yuqi Fan", "Texas Tornado"),
    (44, 24.24, "Andrew Ma", "University of Toronto Schools A"),
    (44, 24.24, "James Qiu", "University of Toronto Schools A"),
    (44, 24.24, "Kaylyn Jinglin Zhang", "University of Toronto Schools A"),
    (44, 24.24, "Andrew Wang", "Paly Trolls"),
    (44, 24.24, "Nathan Ye", "Paly Trolls"),
    (44, 24.24, "Raymond Wang", "R4E-1"),
    (44, 24.24, "Victoria Sheung", "TAS Math Circle"),
    (44, 24.24, "Eric Zhong", "Ward Melville Math Team E"),
    (44, 24.24, "Jonathan Liu", "Lexington Gamma"),
    (44, 24.24, "James Wu", "Lexington Gamma"),
    (44, 24.24, "Xinyi Guo", "Gunn Black"),
    (44, 24.24, "Eric P Zhu", "Math 4 Fun"),
    (44, 24.24, "Isabella Li", "Lexington Delta"),
    (44, 24.24, "Zhang Xinye", "The Limit Does Not Exist"),
    (44, 24.24, "Lindsay Miao", "Hotchkiss Blue"),
]

TEAM_TO_STATE["All Aces Spade"] = ""


def load_students():
    key_to_row = {}
    next_id = 1
    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid_s = (row.get("student_id") or "").strip()
            if not sid_s:
                continue
            try:
                sid = int(sid_s)
            except ValueError:
                continue
            next_id = max(next_id, sid + 1)
            name = (row.get("student_name") or "").strip()
            state = (row.get("state") or "").strip()
            r = {"student_id": sid, "student_name": name, "state": state}
            if name:
                key = (name.lower(), state)
                if key not in key_to_row:
                    key_to_row[key] = r
            for a in (row.get("alias") or "").split("|"):
                a = a.strip()
                if a:
                    key = (a.lower(), state)
                    if key not in key_to_row:
                        key_to_row[key] = r
    return key_to_row, next_id


def main():
    key_to_row, next_id = load_students()
    new_students = []
    out_rows = []

    for (rank, score, paste_name, team) in ROWS:
        state = TEAM_TO_STATE.get(team, "").strip()
        normalized = NAME_NORMALIZE.get(paste_name.strip(), paste_name.strip())
        orig_lower = paste_name.strip().lower()
        norm_lower = normalized.lower()

        row = (
            key_to_row.get((norm_lower, state))
            or key_to_row.get((orig_lower, state))
            or key_to_row.get((norm_lower, ""))
            or key_to_row.get((orig_lower, ""))
        )
        if not row:
            for (k, v) in key_to_row.items():
                if (k[0] == norm_lower or k[0] == orig_lower) and (not state or k[1] == state):
                    row = v
                    break
        if row:
            out_rows.append((row["student_id"], normalized, 2024, rank, score))
            continue
        sid = next_id
        next_id += 1
        key_to_row[(norm_lower, state)] = {"student_id": sid, "student_name": normalized, "state": state}
        new_students.append({
            "student_id": sid, "student_name": normalized, "state": state,
            "team_ids": "", "alias": "", "gender": ""
        })
        out_rows.append((sid, normalized, 2024, rank, score))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "results.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["student_id", "student_name", "year", "rank", "score"])
        for r in out_rows:
            w.writerow(r)
    print(f"Wrote {out_path} ({len(out_rows)} rows)")

    if new_students:
        with open(STUDENTS_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            for r in new_students:
                w.writerow([r["student_id"], r["student_name"], r["state"], r["team_ids"], r["alias"], r["gender"]])
        print(f"Appended {len(new_students)} new students: {[s['student_name'] for s in new_students]}")
    else:
        print("No new students to add.")

    print("Run: python scripts/build_search_data.py")


if __name__ == "__main__":
    main()
