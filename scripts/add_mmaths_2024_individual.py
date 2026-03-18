#!/usr/bin/env python3
"""
Add MMATHs 2024 individual results from hard-coded data.
Resolves student_id from students.csv by (name, state); infers state from team/school when possible.
Creates database/contests/mmaths/year=2024/results.csv and appends any new students.

Run from repo root: python scripts/add_mmaths_2024_individual.py
"""

import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STUDENTS_CSV = REPO_ROOT / "database/students/students.csv"
MMATHS_DIR = REPO_ROOT / "database/contests/mmaths/year=2024"

# TSV rows: Team/School, Team name, First, Last, Code, Full Name, Rank, Score, P1..P12
# Source: https://www.mmaths.org/mmaths
RAW_TSV = """Motown All-Stars	Motown All-Stars	Henry	Jiang	605A	Henry Jiang	1	12	1	1	1	1	1	1	1	1	1	1	1	1
Morris Hills High School	MH Math Knights Bulbasaur	Jason	Mao	050C	Jason Mao	2	11	1	1	1	1	1		1	1	1	1	1	1
Russian School of Mathematics	MathSchool 1	Luca	Pieleanu	005A	Luca Pieleanu	3	11	1	1	1	1	1	1	1	1	1	1	1	
West Windsor Plainsboro High School North	Knights A	Aprameya	Tripathy	016A	Aprameya Tripathy	3	11	1	1	1	1	1	1	1	1	1	1	1	
The Pingry School	Pingry Blue Team	Elbert	Ho	032A	Elbert Ho	3	11	1	1	1	1	1	1	1	1	1	1	1	
Thomas Jefferson High School for Science and Technology	the snorlaxes	Alex	Liu	202B	Alex Liu	3	11	1	1	1	1	1	1	1	1	1	1	1	
TJ	Karkaboingus	Alexander	Gu	203B	Alexander Gu	3	11	1	1	1	1	1	1	1	1	1	1	1	
DMV Math Circle	DMV Math Circle Sigma	Aryan	Raj	210D	Aryan Raj	3	11	1	1	1	1	1	1	1	1	1	1	1	
Poolesville Math Team	Poolesville C	Alyssa	Yu	217B	Alyssa Yu	3	11	1	1	1	1	1	1	1	1	1	1	1	
skibidi six	skibidi six	Aaryan	Vaishya	307A	Aaryan Vaishya	3	11	1	1	1	1	1	1	1	1	1	1	1	
Dallas Math Circle	Dallas Math Circle	Andrew	Li	402B	Andrew Li	3	11	1	1	1	1	1	1	1	1	1	1	1	
Russian School of Mathematics	MathSchool 1	Soham	Samanta	005D	Soham Samanta	12	10	1	1	1	1	1	1	1	1		1		1
petTheSkibidi	petTheSkibidi	Patrick	Du	220E	Patrick Du	13	10	1	1	1	1		1	1	1	1	1	1	
Lexington High School	Lexington Muztaba 3rd Parties	Edwin	Zhao	031F	Edwin Zhao	14	10	1	1	1	1	1		1	1	1	1	
Westchester Area Math Circle	Westchester Area Math Circle A	Girish	Prasad	001B	Girish Prasad	15	10	1	1	1	1	1	1	1	1		1	1	
Mass ARML	Mass ARML Stars	Karn	Chutnian	048A	Karn Chutnian	15	10	1	1	1	1	1	1	1	1		1	1	
Brunswick School	Mass ARML Suns	Vikram	Sarkar	049E	Vikram Sarkar	15	10	1	1	1	1	1	1	1	1		1	1	
Lexington High School	Lexington Muztaba	Selena	Ge	103C	Selena Ge	15	10	1	1	1	1	1	1	1	1		1	1	
McLean High School	McLean A	Aiden	Feyerherm	204B	Aiden Feyerherm	15	10	1	1	1	1	1	1	1	1		1	1	
Maryland United	Maryland United A	David	Wang	221C	David Wang	15	10	1	1	1	1	1	1	1	1		1	1	
Dallas Math Circle	Dallas Math Circle	Xinyi	Li	402A	Xinyi Li	15	10	1	1	1	1	1	1	1	1		1	1	
Thomas Jefferson High School for Science and Technology	the snorlaxes	Shunyao	Yan	202E	Shunyao Yan	22	10	1	1	1	1	1	1	1	1	1	1		
Langley High School	Saxons	Bennett	Huang	214E	Bennett Huang	22	10	1	1	1	1	1	1	1	1	1	1		
Motown All-Stars	Motown All-Stars	Brandon	Chan	605B	Brandon Chan	24	9		1	1	1		1	1	1		1	1	1
ABML	ABML	Raymond	Gao	108B	Raymond Gao	25	9	1	1	1	1	1	1	1	1				1
Livingston High School	Small L Club	Rishi	Shah	058C	Rishi Shah	26	9	1	1	1	1		1	1	1		1	1	
Plano West	Plano West	Dekan	Chen	403B	Dekan Chen	26	9	1	1	1	1		1	1	1		1	1	
Motown All-Stars	Motown All-Stars	Shaohuan	Zhang	605C	Shaohuan Zhang	28	9	1	1	1	1	1		1	1		1	1	
Westchester Area Math Circle	Westchester Area Math Circle B	Michael	Aram	002A	Michael Aram	29	9	1	1	1	1	1	1	1			1	1	
Lexington High School	Lexington Muztaba	Adam	Ge	103B	Adam Ge	30	9	1	1	1	1	1		1	1	1		1	
Indus Center For Academic Excellence	ICAE2	Arnav	Vunnam	602F	Arnav Vunnam	30	9	1	1	1	1	1		1	1	1		1	
West Windsor Plainsboro High School South	Pirates B	Maitian	Sha	019F	Maitian Sha	32	9	1	1	1	1	1	1		1	1		1	
ABML	ABML	Daniel	Cai	108C	Daniel Cai	33	9	1	1	1	1	1	1	1		1		1	
PRISMS	PRISMS Falcons	Mark Yutong	Zhao	009C	Mark Yutong Zhao	34	9	1	1	1	1	1	1	1	1			1	
West Windsor Plainsboro High School South	Pirates A	Divit	Mehra	018B	Divit Mehra	34	9	1	1	1	1	1	1	1	1			1	
Brunswick School	Mass ARML Suns	Jack	Whitney-Epstein	049F	Jack Whitney-Epstein	34	9	1	1	1	1	1	1	1	1			1	
Maryland United	Maryland United A	Jeremy	Yang	221B	Jeremy Yang	34	9	1	1	1	1	1	1	1	1			1	
Orlando Science High School	OSS ORCAS Team 1	Brayden	Choi	303A	Brayden Choi	34	9	1	1	1	1	1	1	1	1			1	
Livingston High School	Big L Club	Advait	Joshi	057F	Advait Joshi	39	9	1	1	1	1	1	1	1	1		1		
Maryland Pi-rates	We Math Goodly	Albert	Cao	222B	Albert Cao	39	9	1	1	1	1	1	1	1	1		1		
Maryland Pi-rates	We Math Goodly	Clark	Hu	222C	Clark Hu	39	9	1	1	1	1	1	1	1	1		1		
AAMOC	Petunia	Daniel	Zhao	611A	Daniel Zhao	39	9	1	1	1	1	1	1	1	1		1		
Individual	The Skibidiest Sigmas	Catherine	Xu	701A	Catherine Xu	39	9	1	1	1	1	1	1	1	1		1		
Phillips Academy	Phillips Academy	Harry	Kim	004A	Harry Kim	44	9	1	1	1	1	1	1	1	1	1			
PRISMS	PRISMS Falcons	Samuel	Ding	009B	Samuel Ding	44	9	1	1	1	1	1	1	1	1	1			
Individual	CO Mathletes	Owen	Tang	503D	Owen Tang	44	9	1	1	1	1	1	1	1	1	1			
River Hill High School	Le club mathematique de River Hill	Patrick	Deng	206B	Patrick Deng	47	8	1	1	1	1	1	1				1		1
Princeton High School	PHS Apricot	Emma	Li	034A	Emma Li	48	8	1	1	1	1	1		1	1				1
The Pingry School	Pingry Blue Team	Eric	Chen	032E	Eric Chen	49	8	1	1	1	1	1	1	1					1
ABML	ABML	Bryan	Li	108A	Bryan Li	50	8		1	1	1	1	1		1		1	1	
DMV Math Circle	DMV Math Circle Sigma	Tony	Zhang	210F	Tony Zhang	51	8	1	1	1		1	1	1			1	1	
Motown All-Stars	Motown All-Stars	Vincent	Pirozzo	605D	Vincent Pirozzo	52	8	1	1	1		1		1	1	1		1	
Maryland United	Maryland United A	David	Yu	221F	David Yu	53	8	1	1		1	1	1	1	1			1	
Sai Chintagunta	Green Hamsters	Sai	Chintagunta	056F	Sai Chintagunta	54	8	1	1	1		1	1	1	1			1	
Russian School of Mathematics	MathSchool 1	Jefferson	Ji	005B	Jefferson Ji	55	8	1	1	1	1	1		1	1			1	
The Pingry School	Pingry Blue Team	Madeline	Zhu	032F	Madeline Zhu	55	8	1	1	1	1	1		1	1			1	
Pioneer High School	D1 Moggers	Michael	Wu	606A	Michael Wu	55	8	1	1	1	1	1		1	1			1	
TJ	Karkaboingus	Spencer	Wang	203F	Spencer Wang	58	8	1	1	1	1	1	1	1				1	
Orlando Science High School	OSS ORCAS Team 1	Joshua	Oliver	303D	Joshua Oliver	58	8	1	1	1	1	1	1	1				1	
Maryland United	Maryland United A	Daniel	Yu	221E	Daniel Yu	60	8	1	1	1	1	1		1		1	1		
Lexington High School	Lexington Muztaba's Opps	William	Hua	104B	William Hua	61	8	1	1	1	1		1	1	1		1		
Multivariants	Multivariants	Nikhil	Reddy	411B	Nikhil Reddy	61	8	1	1	1	1		1	1	1		1		
PRISMS	PRISMS Falcons	Zhifei	Liu	009A	Zhifei Liu	63	8	1	1	1	1	1		1	1		1		
Lexington High School	Lexington Muztaba	Ryan	Tang	103A	Ryan Tang	63	8	1	1	1	1	1		1	1		1		
Dallas Math Circle	Dallas Math Circle	Colin	Wei	402D	Colin Wei	63	8	1	1	1	1	1		1	1		1		
Eli Gold	NDHS	Eli	Gold	047F	Eli Gold	66	8	1	1	1	1	1	1	1			1		
Green Hamsters	Green Hamsters	Amy	Ma	056A	Amy Ma	66	8	1	1	1	1	1	1	1			1		
DMV Math Circle	DMV Math Circle Sigma	Arnav	Iyengar	210B	Arnav Iyengar	66	8	1	1	1	1	1	1	1			1		
DMV Math Circle	DMV Math Circle Sigma	Adithya	Prabha	210C	Adithya Prabha	66	8	1	1	1	1	1	1	1			1		
Russian School of Mathematics	MathSchool 2	Andrew	Kalashnikov	006B	Andrew Kalashnikov	70	8	1	1	1	1	1	1	1		1			
Lexington High School	Lexington Muztaba 3rd Parties	Jonathan	Liu	031E	Jonathan Liu	70	8	1	1	1	1	1	1	1		1			
Phillips Academy	Phillips Academy	Huanqi	Zhang	004F	Huanqi Zhang	72	8	1	1	1	1	1	1	1	1				
Russian School of Mathematics	MathSchool 1	Alexander	Amrhein	005E	Alexander Amrhein	72	8	1	1	1	1	1	1	1	1				
PRISMS	PRISMS Falcons	Ziyi	Yang	009F	Ziyi Yang	72	8	1	1	1	1	1	1	1	1				
West Windsor Plainsboro High School North	Knights A	Rithik	Gumpu	016B	Rithik Gumpu	72	8	1	1	1	1	1	1	1	1				
West Windsor Plainsboro High School North	Knights A	Ethan	Wang	016E	Ethan Wang	72	8	1	1	1	1	1	1	1	1				
West Windsor Plainsboro High School South	Pirates A	Aarush	Prasad	018A	Aarush Prasad	72	8	1	1	1	1	1	1	1	1				
West Windsor Plainsboro High School South	Pirates C	Daniel	Lu	020B	Daniel Lu	72	8	1	1	1	1	1	1	1	1				
West Windsor Plainsboro High School South	Pirates C	Suhas	Kondapalli	020F	Suhas Kondapalli	72	8	1	1	1	1	1	1	1	1				
Lexington High School	Lexington Muztaba 3rd Parties	Gary	Shen	031D	Gary Shen	72	8	1	1	1	1	1	1	1	1				
Princeton High School	PHS Apricot	Maiya	Qiu	034B	Maiya Qiu	72	8	1	1	1	1	1	1	1	1				
Westfield High and UCVTS	MH Math Knights Treecko	Justin	Lee	052E	Justin Lee	72	8	1	1	1	1	1	1	1	1				
Cheshire Academy	Cheshire Cats	Jaeyun	Park	102C	Jaeyun Park	72	8	1	1	1	1	1	1	1	1				
Lexington High School	Lexington Muztaba	Jerry	Xu	103E	Jerry Xu	72	8	1	1	1	1	1	1	1	1				
Lexington High School	Lexington Muztaba	Chris	Cheng	103F	Chris Cheng	72	8	1	1	1	1	1	1	1	1				
Lexington High School	Lexington Muztaba's Opps	Jacob	Xu	104A	Jacob Xu	72	8	1	1	1	1	1	1	1	1				
Lexington High School	Lexington Muztaba's Opps	Samuel	Wang	104C	Samuel Wang	72	8	1	1	1	1	1	1	1	1				
Lexington High School	Lexington Muztaba's Opps	Rajarshi	Mandal	104F	Rajarshi Mandal	72	8	1	1	1	1	1	1	1	1				
BANT Math	BMT	Daniel	David	107E	Daniel David	72	8	1	1	1	1	1	1	1	1				
Thomas Jefferson High School for Science and Technology	the snorlaxes	Paul	Yoo	202C	Paul Yoo	72	8	1	1	1	1	1	1	1	1				
McLean High School	McLean B	Kalan	Warusa	204F	Kalan Warusa	72	8	1	1	1	1	1	1	1	1				
DMV Math Circle	DMV Math Circle Alpha	Erica	Xie	209E	Erica Xie	72	8	1	1	1	1	1	1	1	1				
Richard Montgomery High School	Moco Rockets	David	He	213D	David He	72	8	1	1	1	1	1	1	1	1				
Langley High School	Saxons	Zifan	Zhao	214B	Zifan Zhao	72	8	1	1	1	1	1	1	1	1				
Langley High School	Saxons	Ian	Liao	214C	Ian Liao	72	8	1	1	1	1	1	1	1	1				
Maryland United	Maryland United A	William	Qian	221D	William Qian	72	8	1	1	1	1	1	1	1	1				
Doral Academy High	Doral Academy Team 1: Koski's Congregation	Abhishek	Chand	301C	Abhishek Chand	72	8	1	1	1	1	1	1	1	1				
Frazer School	In Keith we Trust	George	Paret	305A	George Paret	72	8	1	1	1	1	1	1	1	1				
Dallas Math Circle	Dallas Math Circle	Devin	Li	402C	Devin Li	72	8	1	1	1	1	1	1	1	1				
Individual	Dallas Individuals 2	Bryan	Fu	412E	Bryan Fu	72	8	1	1	1	1	1	1	1	1				
Indus Center For Academic Excellence	ICAE2	Sanjana	Ramesh	602E	Sanjana Ramesh	72	8	1	1	1	1	1	1	1	1				
Indus Center For Academic Excellence	ICAE4	Meghana	Myneni	604D	Meghana Myneni	72	8	1	1	1	1	1	1	1	1				
Motown All-Stars	Motown All-Stars	Taiwen	Feng	605F	Taiwen Feng	72	8	1	1	1	1	1	1	1	1				
Huron High School	Team Tau	Siddharth	Sangi	607C	Siddharth Sangi	72	8	1	1	1	1	1	1	1	1				
Huron High School	Team Tau	Matthew	Zhang	607D	Matthew Zhang	72	8	1	1	1	1	1	1	1	1	
"""

# Infer state from school/team name when possible (contest says (name, state) is the key).
SCHOOL_TO_STATE = {
    "Motown All-Stars": "Michigan",
    "Morris Hills High School": "New Jersey",
    "West Windsor Plainsboro High School North": "New Jersey",
    "West Windsor Plainsboro High School South": "New Jersey",
    "The Pingry School": "New Jersey",
    "Thomas Jefferson High School for Science and Technology": "Virginia",
    "TJ": "Virginia",
    "DMV Math Circle": "",  # DC/MD/VA
    "Poolesville Math Team": "Maryland",
    "Dallas Math Circle": "Texas",
    "Lexington High School": "Massachusetts",
    "Westchester Area Math Circle": "New York",
    "Mass ARML": "Massachusetts",
    "Brunswick School": "Connecticut",
    "McLean High School": "Virginia",
    "Maryland United": "Maryland",
    "Maryland Pi-rates": "Maryland",
    "Langley High School": "Virginia",
    "Livingston High School": "New Jersey",
    "Plano West": "Texas",
    "PRISMS": "New Jersey",
    "Phillips Academy": "Massachusetts",
    "Princeton High School": "New Jersey",
    "River Hill High School": "Maryland",
    "Orlando Science High School": "Florida",
    "Pioneer High School": "Michigan",
    "Huron High School": "Michigan",
    "Richard Montgomery High School": "Maryland",
    "Doral Academy High": "Florida",
    "Frazer School": "Pennsylvania",
    "Cheshire Academy": "Connecticut",
    "Westfield High and UCVTS": "New Jersey",
    "Indus Center For Academic Excellence": "Texas",
    "Russian School of Mathematics": "",
    "skibidi six": "",
    "petTheSkibidi": "",
    "ABML": "",
    "AAMOC": "",
    "Individual": "",
    "Sai Chintagunta": "",
    "Green Hamsters": "",
    "Eli Gold": "",
    "Multivariants": "",
    "BANT Math": "",
}


def normalize_name(name: str) -> str:
    return " ".join(name.split()).strip().lower()


def load_students():
    """(name_lower, state) -> (student_id, canonical_name); next_id."""
    key_to_id_name: dict[tuple[str, str], tuple[int, str]] = {}
    name_only_to_id: dict[str, tuple[int, str]] = {}  # when state is blank, match by name only
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
            state = (row.get("state") or "").strip()
            if not name:
                continue

            n = normalize_name(name)
            key_to_id_name[(n, state)] = (sid, name)
            name_only_to_id.setdefault(n, (sid, name))

            for a in (row.get("alias") or "").split("|"):
                a = a.strip()
                if a:
                    na = normalize_name(a)
                    key_to_id_name[(na, state)] = (sid, name)
                    name_only_to_id.setdefault(na, (sid, name))

    return key_to_id_name, name_only_to_id, next_id


def infer_state(school: str) -> str:
    return SCHOOL_TO_STATE.get(school, "")


def main() -> None:
    key_to_id_name, name_only_to_id, next_id = load_students()

    rows: list[tuple[int, str, str, str, str, str]] = []  # sid, name, year, rank, score, team
    new_students: list[tuple[int, str, str]] = []  # sid, name, state

    for line in RAW_TSV.strip().splitlines():
        parts = line.split("\t")
        if len(parts) < 8:
            continue
        school = (parts[0] or "").strip()
        full_name = (parts[5] or "").strip()
        if not full_name:
            continue
        # Fix known typo in source: "Eric Xie" -> "Erica Xie" (first name column is Erica)
        if full_name == "Eric Xie" and (parts[2] or "").strip() == "Erica":
            full_name = "Erica Xie"
        rank_raw = (parts[6] or "").strip()
        score_raw = (parts[7] or "").strip()
        rank = rank_raw if rank_raw else ""
        score = score_raw if score_raw else ""

        state = infer_state(school)
        n = normalize_name(full_name)

        sid, canonical_name = key_to_id_name.get((n, state)) or key_to_id_name.get((n, "")) or name_only_to_id.get(n, (None, None))
        if sid is None or canonical_name is None:
            sid = next_id
            next_id += 1
            canonical_name = full_name
            new_students.append((sid, full_name, state))
            key_to_id_name[(n, state)] = (sid, canonical_name)
            name_only_to_id.setdefault(n, (sid, canonical_name))

        team = (parts[1] or "").strip() if len(parts) > 1 else ""
        rows.append((sid, canonical_name, "2024", rank, score, team))

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
            for sid, name, state in new_students:
                writer.writerow([sid, name, state, "", "", ""])

    print(f"Wrote {results_path} with {len(rows)} MMATHs 2024 individual results")
    print(f"Added {len(new_students)} new students to {STUDENTS_CSV}")


if __name__ == "__main__":
    main()
