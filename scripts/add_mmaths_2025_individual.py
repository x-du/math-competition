#!/usr/bin/env python3
"""
Add MMATHs 2025 individual results from hard-coded data.
Format: Team, Name, Rank, Score (tab-separated). Blank team or name -> "Unknown".
Resolves student_id from students.csv by name (and alias); adds new students as needed.
Creates database/contests/mmaths/year=2025/results.csv.

Run from repo root: python scripts/add_mmaths_2025_individual.py
"""
import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STUDENTS_CSV = REPO_ROOT / "database/students/students.csv"
MMATHS_DIR = REPO_ROOT / "database/contests/mmaths/year=2025"

# TSV: Team, Name, Rank, Score. Use "Unknown" for blank team or name.
RAW_TSV = """Westchester Area Math Circle A	Alexander Svoronos	1	11
Motown All-Stars	Vincent Pirozzo	2	11
Placeholder	Jack Whitney-Epstein	2	11
Placeholder	Vikram Sarkar	2	11
DMV Math Circle Sigma	Aryan Raj	2	11
the snorlaxes	Shunyao Yan	2	11
Not Great Valley	Eden He	7	10
Big L Club	Advait Joshi	8	10
koobee weadah	Max Zheng	8	10
Maryland United	Jeremy Yang	8	10
		11	10
FrostMath	Shlok Mukund	12	10
PRISMS Falcons	Youran Charlie Gu	12	10
The Hexacontakaiheptagons	Ethan Imanuel	12	10
The Hexacontakaiheptagons	Eric Guo	12	10
WWP Charizard	Maitian Sha	12	10
FrostMath	Brandon Ni	12	10
PRISMS Falcons	Michael Chen	12	10
Westchester Area Math Circle E	Max Salvestrini	12	10
DMV Math Circle Sigma	Eric Xie	12	10
DMV Math Circle Sigma	Arnav Lyengar	12	10
Maryland United	Nathan Lu	12	10
Lexington Zeta	James Wu	23	10
WWP Charizard	Samuel Ding	24	9
		25	9
Mass ARML	Daniel Ge	26	9
orzzzzzzzzzzzz	Jason Lu	27	9
Math-M-Addicts 1	Mihir Kumar	28	9
Motown All-Stars	Nathan Mei	29	9
The Hexacontakaiheptagons	Soham Samanta	30	9
Lexington Zeta	Danyang Xu	31	9
RSM - A	Anand Swaroop	31	9
Ultraviolet Catastrophe	Isaac Chan-Osborn	31	9
Maryland United	David Wang	31	9
VAMC2025	Steve Cui	31	9
Novi Unicorns	Arnav Vunnam	36	9
Westchester Area Math Circle B	Jonathan Zhou	36	9
Benjamin's Mom's Team	Daniel David	38	9
Big L Club	Benjamin Sun	38	9
FrostMath	Ben Li	38	9
Lexington Alpha	Benjamin Yin	38	9
Westchester Area Math Circle A	Abby Kesmodel	38	9
Maryland United	William Qian	38	9
Dallas Individuals 1	Sreehari Vijaybhaskar	38	9
Benjamin's Dad's Team	Brian Zhao	45	9
Daisy - AAMOC 1	Daniel Zhou	46	9
Motown All-Stars	Jiaxuan Gong	47	9
Novi Unicorns	Woojin Seong	47	9
Hotchkiss Blue	Dawson Park	47	9
Lexington Alpha	Peter Bai	47	9
Placeholder	Sohan Javeri	47	9
PRISMS Future Falcons	Mia Gan	47	9
PRISMS Young Falcons	Kaya Yang	47	9
Theta Math Club	Kevin Yu	47	9
Westchester Area Math Circle A	Yunong Wu	47	9
Westchester Area Math Circle A	Girish Prasad	47	9
Westchester Area Math Circle B	Henry Xue	47	9
WWP Charmander	Aarush Prasad	47	9
Ultraviolet Catastrophe	Jack Li	47	9
Ultraviolet Catastrophe	Christopher Sakaliyski	47	9
Lexington Alpha	William Hua	61	8
orzzzzzzzzzzzz	Lucas Wang	62	8
Cranbrook Aardvarks	Shaohuan Zhang	63	8
Stearns Middle School	Zenghan Feng	63	8
Cranbrook Aardvarks	Justin Seo	65	8
PESH Math Club	Shaheem Samsudeen	66	8
D1 Moggers	Michael Wu	67	8
Dallas Math Circle	Xinyi Li	67	8
Dallas Individuals 1	Samarth Das	67	8
Mass ARML	Alexander Liu	67	8
Theta Math Club	Tianze Qiu	71	8
Lexington Alpha	Jason Yang	72	8
OveRZealous TEsserAct Manufacturers	Zekai Wang	73	8
Cranbrook Aardvarks	Pun Tresattayapan	74	8
USC Individuals 1	Benjamin Tang	75	8
CRH 1	Hridaan Mehta	76	8
VAMC2025	Ian Cheng	76	8
the snorlaxes	Tiger Deng	78	8
Ultraviolet Catastrophe	William Wu	79	8
PHS Apricot	Emma Li	80	8
Hot Pot Lovers	Chloe Ma	81	8
RSM - B	Alexander Peev	82	8
REST Assured	Roy Brauwerman	83	8
PHS Apricot	Maiya Qiu	84	8
Mass ARML	Samhith Dewal	85	8
PRISMS Falcons	Bohan Wang	85	8
Academies Math Team	Anuraag Pasula	85	8
Cranbrook Aardvarks	Taiwen Feng	88	8
texington	Christopher Cheng	88	8
Lexington Zeta	Amy Zhang	90	8
Dallas Math Circle	Devin Li	91	8
RSM - A	April Sun	91	8
WWP Charizard	Anish Alapati	91	8
Academies Math Team	Abhinav Kandregula	91	8
PESH Math Club	William Prasetyo	95	8
texington	Jonathan Liu	95	8
OveRZealous TEsserAct Manufacturers	Bella Li	95	8
Ultraviolet Catastrophe	Boyou Huang	95	8
A Kettle of Hawks	Leon Du	95	8
"""


def normalize_name(name: str) -> str:
    return " ".join(name.split()).strip().lower()


def load_students():
    """name_lower -> (student_id, canonical_name); next_id."""
    name_to_id_name: dict[str, tuple[int, str]] = {}
    next_id = 1
    with STUDENTS_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid_raw = (row.get("student_id") or "").strip()
            if not sid_raw:
                continue
            try:
                sid = int(sid_raw)
            except ValueError:
                continue
            next_id = max(next_id, sid + 1)
            name = (row.get("student_name") or "").strip()
            if not name:
                continue
            n = normalize_name(name)
            name_to_id_name[n] = (sid, name)
            for a in (row.get("alias") or "").split("|"):
                a = a.strip()
                if a:
                    name_to_id_name[normalize_name(a)] = (sid, name)
    return name_to_id_name, next_id


def main() -> None:
    name_to_id_name, next_id = load_students()
    rows: list[tuple[int, str, str, str, str, str]] = []
    new_students: list[tuple[int, str]] = []

    for line in RAW_TSV.strip().splitlines():
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        team = (parts[0] or "").strip() or "Unknown"
        name = (parts[1] or "").strip() or "Unknown"
        rank = (parts[2] or "").strip()
        score = (parts[3] or "").strip()

        n = normalize_name(name)
        sid, canonical_name = name_to_id_name.get(n, (None, None))
        if sid is None or canonical_name is None:
            sid = next_id
            next_id += 1
            canonical_name = name
            new_students.append((sid, name))
            name_to_id_name[n] = (sid, canonical_name)

        rows.append((sid, canonical_name, "2025", rank, score, team))

    MMATHS_DIR.mkdir(parents=True, exist_ok=True)
    results_path = MMATHS_DIR / "results.csv"
    with results_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "student_name", "year", "rank", "score", "team"])
        for r in rows:
            writer.writerow(r)

    if new_students:
        with STUDENTS_CSV.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for sid, name in new_students:
                writer.writerow([sid, name, "", "", "", ""])

    print(f"Wrote {results_path} with {len(rows)} MMATHs 2025 individual results")
    print(f"Added {len(new_students)} new students to {STUDENTS_CSV}")


if __name__ == "__main__":
    main()
