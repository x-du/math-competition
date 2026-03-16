#!/usr/bin/env python3
"""
Match students missing state with SMO 2025 results and set state=Singapore for matches.
SMO 2025 results from: https://sgmathsociety.org/results-for-smo-2025/
"""

import json
import csv
import re
from pathlib import Path

# All names from SMO 2025 Individual Awards (Junior, Senior, Open sections)
# Format on website: typically "FAMILY_NAME GIVEN_NAME(s)" for Asian names
SMO_2025_NAMES = [
    # Junior Section
    "ZHU YIXUAN", "LEE JIA-EN ELIAS", "ZHONG ZHANCHEN", "HAN XU ETHAN",
    "WU CHONGXI ORSON", "NGHIA LAM", "DENG MAOYU", "LIM CHEE HANN",
    "WU YIKUN", "SIEW JING YE", "FAN XUEZHE", "SUN JINCHENG", "SUN MINGYUAN",
    "MATTHAN PANG YEW LOONG", "LEE WEI EN", "CHEN YIFEI", "WANG ZIYUAN",
    "XU DUO", "HU JIYANG", "TAN YUCHEN", "XU RUICHEN", "GE YUANKANG",
    "WANG ZIHAN HECTOR", "NG GEN LONG", "YEE HONG SHYAN",
    "ELWIN ANTOINE SANMARTIN", "CHEN CHUXUAN ETHAN", "LUO XINYA",
    "WANG YAN CHUAN, JUDE", "ZHU XIAOYE AUSTIN", "LU YANHENG",
    # Senior Section
    "RYKER XU HAOHAN", "XUE JINZE", "GAO YUXIANG LUCAS", "GAO ZIXIANG",
    "ZHANG CHANGJUN", "TEY YI XIANG", "CHEN JIAQI", "WANG YI",
    "YONG SIU HEI", "ZHONG JINGYAO", "LUO XINDI", "GU SIMIAO", "XIA JIAHAO",
    "LIM ZU WAN", "JAYDEN HOO DUN JIE", "TIMOTHY GOH ZHI BIN", "ZHEN MINGYUAN",
    "CHONG YU TENG, ADEN", "WANG YAN LI, LUKE", "CHUA SHANG AN LUCIEN",
    "MAO RUIYANG", "KABIR SRIVASTAV", "YING LIQIAN", "LI SIXING",
    "SEAH BING XUAN AARON", "KAN RUI HONG ANDREW (JIAN RUIHONG)",
    "WONG NAIJIE", "LOU YEHUI", "MINGEON CHOI", "YU KUAI, CHRISTOPHER",
    "JUSTIN LING CHUN XU",
    # Open Section
    "SUN WENYUAN", "ZHAO YAOQI", "YANG YIHAN", "AKASH THIAGARAJAN",
    "CHEN RUI AN", "RAPHAEL TENG ZHI XIANG", "DERRICK LUKIMIN",
    "BRIAN XIAO BOYANG", "DING CHENGHAO", "KONG JIA LE", "LOO WAYHAN BRIAN",
    "SIEW JING HONG", "ARNAB MISHRA", "LEONG SAU MAN WENDY (LIANG XIUWEN)",
]


def normalize_name(name: str) -> str:
    """Normalize name for comparison: uppercase, remove extra spaces, punctuation in parens."""
    # Remove content in parentheses for matching
    name = re.sub(r'\s*\([^)]*\)', '', name)
    name = re.sub(r'\s*,\s*', ' ', name)  # Replace comma with space
    name = ' '.join(name.upper().split())
    return name


def name_parts(name: str) -> set:
    """Get set of name parts (words) for flexible matching."""
    normalized = normalize_name(name)
    return set(normalized.split())


def names_match(db_name: str, smo_name: str) -> bool:
    """
    Check if database name matches SMO name.
    Handles: "First Last" vs "LAST FIRST", different ordering, etc.
    """
    db_parts = name_parts(db_name)
    smo_parts = name_parts(smo_name)

    # Must have same number of significant parts (ignore single-char like middle initial)
    db_parts = {p for p in db_parts if len(p) > 1}
    smo_parts = {p for p in smo_parts if len(p) > 1}

    # Exact set match
    if db_parts == smo_parts:
        return True

    # All db parts must be in smo (db might have fewer - e.g., "Ben Song" vs "BENJAMIN SONG")
    if db_parts and db_parts <= smo_parts:
        return True

    # All smo parts must be in db (smo might have fewer - e.g., nickname)
    if smo_parts and smo_parts <= db_parts:
        return True

    # Check if normalized strings match when we try "Last First" format
    db_norm = normalize_name(db_name)
    smo_norm = normalize_name(smo_name)

    # Direct match
    if db_norm == smo_norm:
        return True

    # Try reversing: "First Last" -> "Last First"
    db_reversed = ' '.join(reversed(db_norm.split()))
    if db_reversed == smo_norm:
        return True

    return False


def main():
    base = Path(__file__).parent.parent
    incomplete_path = base / "incomplete_students.json"
    students_path = base / "database" / "students" / "students.csv"

    with open(incomplete_path) as f:
        data = json.load(f)

    missing_state = data["missing_state"]
    smo_names_set = set(SMO_2025_NAMES)

    matches = []
    for student in missing_state:
        student_id = student["student_id"]
        student_name = student["student_name"]
        for smo_name in smo_names_set:
            if names_match(student_name, smo_name):
                matches.append((student_id, student_name, smo_name))
                break

    print(f"Found {len(matches)} matches between missing_state and SMO 2025:")
    for sid, db_name, smo_name in matches:
        print(f"  {sid}: {db_name} <-> {smo_name}")

    if not matches:
        print("No matches found. No updates needed.")
        return

    # Read students.csv and update
    rows = []
    with open(students_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if row['student_id'] in [m[0] for m in matches]:
                row['state'] = 'Singapore'
                print(f"Updating student_id {row['student_id']} ({row['student_name']}) -> Singapore")
            rows.append(row)

    # Write back
    with open(students_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nUpdated {len(matches)} students with state=Singapore")


if __name__ == "__main__":
    main()
