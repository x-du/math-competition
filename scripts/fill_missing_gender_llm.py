#!/usr/bin/env python3
"""
Fill missing gender in students.csv using LLM inference from student_name only.

Per prompts/fill-missing-gender.md:
- Infer gender ONLY from student_name (and alias if it clarifies).
- Do NOT infer from contest participation, school, or other fields.
- Only assign male/female when LLM confidence is >80%.
- Report students whose gender cannot be inferred for manual handling.

Requires OPENAI_API_KEY (unless --no-llm or --apply-from). Usage:
  python scripts/fill_missing_gender_llm.py [--dry-run] [--batch-size N] [--no-llm]
  python scripts/fill_missing_gender_llm.py --apply-from prompts/fill-missing-gender-inferred.json
  --no-llm       Write fill-missing-gender-input.json for external LLM; do not call API or update CSV.
  --apply-from F Apply pre-computed inferences from JSON file (e.g. from Cursor AI).
  --local        Use gender-guesser library for inference (no API); install: pip install gender-guesser
  --supplement   Second pass: apply curated names gender-guesser misses (Indian, Chinese, Korean, etc.)
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
CANNOT_INFER_TXT = ROOT / "prompts" / "fill-missing-gender-cannot-infer.txt"
INPUT_JSON = ROOT / "prompts" / "fill-missing-gender-input.json"
INFERRED_JSON = ROOT / "prompts" / "fill-missing-gender-inferred.json"

CONFIDENCE_THRESHOLD = 80

# Curated first names gender-guesser often misses (US/Indian/Chinese/Korean context, >80% confidence)
SUPPLEMENT_FEMALE = frozenset({
    "Aadhya", "Aahana", "Aanya", "Aaratrika", "Aashi", "Aayushi", "Abjini", "Adwita", "Aishwarya",
    "Amruta", "Anagha", "Ananya", "Anoushka", "Anvi", "Anvika", "Apoorva", "Arohi", "Avani",
    "Bhuvi", "Chandhana", "Dhyana", "Drishti", "Geetali", "Gaya", "Hamsini", "Ishika", "Ishita",
    "Isha", "Jayani", "Jiya", "Kavya", "Keerthana", "Khushi", "Kriti", "Kripa", "Kyvalya",
    "Leya", "Likhitha", "Mahita", "Manogna", "Medha", "Meha", "Mihika", "Mohita", "Moksha",
    "Nandana", "Nandika", "Narnia", "Niharika", "Nikhita", "Nidarshana", "Ojasya", "Parnika",
    "Poorva", "Pranavi", "Prerana", "Prisha", "Pushti", "Radea", "Rainelle", "Reya", "Riddhi",
    "Rishitha", "Rujula", "Rutvi", "Saaina", "Sahana", "Samyukta", "Sanya", "Sandarika",
    "Saranya", "Shreya", "Shreeya", "Shreshta", "Shriyadita", "Shripriya", "Shruthi", "Shveta",
    "Sowmya", "Srishti", "Sriya", "Sruthi", "Surie", "Swara", "Tanvi", "Thanishkka", "Twisha",
    "Vaishnavi", "Vaibhavee", "Varshaa", "Vedika", "Vyshnavi", "Yashika", "Yukta", "Zhilan",
    "Adithi", "Adya", "Aarushi", "Analise", "Ashleen", "Azaria", "Callia", "Cailyn", "Diya",
    "Elynna", "Haasini", "Hasini", "Inika", "Jaina", "Jiayu", "Julica", "Kanak", "Keya",
    "Laasya", "Leaya", "Lylia", "Mahika", "Matea", "Mollee", "Naaisha", "Navya", "Nethra",
    "Nishika", "Raeanne", "Rasika", "Rinnah", "Riya", "Saanvi", "Sanjana", "Sanvi", "Sejal",
    "Sharika", "Sharvaa", "Shrina", "Simay", "Sonakshi", "Srinika", "Stuti", "Suhani",
    "Summer", "Sybella", "Torsia", "Vaibhavee", "Wenjuan", "Xinyi", "Xinyue", "Yiting",
    "Aliana", "Anishka", "Anvita", "Bhavini", "Haisley", "Kaavya", "Pranamya", "Samhitha",
    "Sharanya", "Shubhi", "Siyona", "Sravya", "Snigdha", "Advika", "Sahasra", "Sheethal",
    "Aarthi", "Maanvitha", "Pranjoli", "Nirupama", "Prateeksha", "Anandita", "Srinithi",
    "Aangi", "Vishakha", "Ishaani", "Baruni", "Aneeka", "Kareena", "Akshatha", "Anaye",
    "Yamei", "Aarna", "Netra", "Smithi", "Nickita", "Anaaya", "Siddhi", "Reetisha",
    "Tannishtha", "Anouksha", "Rishika", "Ankita", "Aashritha", "Harini", "Eesha",
    "Palak", "Sukhmani", "Annicka", "Jovina", "Sophiana", "Rhushika", "Surbhi", "Ashwika",
    "Yuting", "Jianing", "Bethesda", "Sohini", "Krivi", "Syna", "Himani", "Naisha",
    "Yifei", "Qinzi", "Shuya", "Anusha", "Shriya", "Ruijia", "Yinhong", "Chenxi",
    "Leyi", "Kaiti", "Shirochka", "Jeain", "Kriste", "Linor",
})
SUPPLEMENT_MALE = frozenset({
    "Aahan", "Aarav", "Aarush", "Abhinav", "Adarsh", "Aditya", "Akshay", "Amudhan", "Anant",
    "Anirudh", "Ansh", "Anshul", "Arnav", "Arpit", "Arush", "Atharv", "Ayan", "Bhavin",
    "Chirag", "Darsh", "Dev", "Dheeraj", "Dhruv", "Ekaansh", "Eshaan", "Gautham", "Hanson",
    "Haresh", "Ishaan", "Kedaar", "Keerthan", "Krishna", "Krrish", "Manan", "Manas", "Mihir",
    "Nithin", "Paras", "Parth", "Prajit", "Praneel", "Pranav", "Prithvi", "Rachit", "Raahil",
    "Rishabh", "Rishik", "Rishit", "Ritwik", "Rushil", "Sajeev", "Sampath", "Sankarshana",
    "Shashwath", "Shlok", "Shourya", "Shreyas", "Shrihan", "Siddharth", "Soham", "Tanmay",
    "Tahmin", "Varyan", "Vatsal", "Vaibhav", "Vasu", "Vedant", "Vihaan", "Vishnu", "Vishwa",
    "Wonjun", "Yash", "Zephan", "Anjan", "Aniket", "Armaan", "Ashmit", "Bhuvan", "Cavon",
    "Daksh", "Debarghya", "Ekansh", "Harsh", "Harshil", "Jeevith", "Kannan", "Kedaar",
    "Krish", "Lohith", "Lyev", "Manvik", "Narayan", "Plato", "Prattay", "Redger", "Reyansh",
    "Rithik", "Rithvik", "Sachit", "Saharsh", "Sahil", "Samaksh", "Samarth", "Sreeram",
    "Shashwat", "Shray", "Shujun", "Siddhant", "Siddharaj", "Tanooj", "Vibhun", "Vyom",
    "Waroon", "Yuxuan", "Zakhar", "Ziang", "Aakash", "Abhiraj", "Adhvay", "Adit", "Akshaj",
    "Alakh", "Ananth", "Aniketh", "Ankur", "Anup", "Aswath", "Atharva", "Baomo", "Bhargava",
    "Brais", "Cheng", "Dharveen", "Divij", "Eldrick", "Eney", "Guanzhen", "Haokai", "Haojun",
    "Haoming", "Harsevran", "Hyunjoon", "Jiajun", "Jayvik", "Joaquin", "Kaartic", "Karn",
    "Kedar", "Kefei", "Lakshya", "Leeoz", "Lingzi", "Maulik", "Mahanth", "Nathra", "Nirvik",
    "Osvin", "Pinak", "Pragyan", "Praneeth", "Pritish", "Qinwen", "Revanth", "Rishan",
    "Ritvik", "Rounak", "Ruthvik", "Saathvik", "Sahaj", "Sanat", "Sanjith", "Sathvik",
    "Shailen", "Shishir", "Shivansh", "Shreev", "Shrey", "Srikar", "Sriaditya", "Sreedathan",
    "Srijith", "Suhas", "Tanish", "Theenash", "Vidit", "Vishal", "Vrajesh", "Vrishabh",
    "Yashnil", "Yejun", "Yelisey", "Yiran", "Yuantao", "Yuecheng", "Yujun", "Yunchan",
    "Zichang", "Zhuojia", "Ziqi", "Ziyao", "Ziyan", "Baixuan", "Tianzhuo", "Siming",
    "Venkatraman", "Aran", "Anray", "Avishi", "Jiaxin", "Ruijing", "Vidyut", "Petey",
    "Asanshay", "Roshen", "Amish", "Sirius", "Timason", "Polaris", "Bhadra", "Ryon",
    "Bodie", "Saidivyesh", "Anran", "Pulak", "Rohit", "Kyan", "Advik", "Sriyan",
    "Gentry", "Hanyu", "Ayush", "Aalok", "Yedong", "Yuehan", "Aayan", "Utshaho",
    "Haolin", "Vikrant", "Akhil", "Sohum", "Yuhan", "Minlu", "Pranay", "Adyant",
    "Jaeyeol", "Pavan", "Vishrut", "Aadi", "Anish", "Grayden", "Ruichen", "Ruikang",
    "Sashwat", "Sheehan", "Tasheen", "Ved", "Yabo", "Yiding", "Ziyan", "Matvii",
    "Sitar", "Arya", "Aayush", "Ayaan", "Prajeet", "Akshat", "Adithya", "Paraj",
    "Viveksai", "Aariv", "Abhiraj", "Ruishan", "Shoubhit", "Kairui", "Priyam",
    "Rhythm", "Vedang", "Weiwei", "Adhrit", "Swarith", "Devik", "Ojas", "Pax",
    "Winsley", "Benson", "Fox", "Saketh", "Sameehan", "Tanushi", "Aahil", "Aarnav",
    "Haoyun", "Kaiyuan", "Sayan", "Sridattha", "Zeyu", "Hao", "Wenhai", "Aayaan",
    "Stephane", "Aagam", "Bili", "Chaithanya", "Mingyi", "Shravan", "Varen", "Yufei",
    "Aryav", "Zihan", "Dang", "Medhansh", "Mowen", "Ren", "Thaman", "Yookta",
    "Aarin", "Aobin", "Shreyansh", "Kavin", "Shriram", "Tanay", "Aashrith", "Archer",
    "Virat", "Agastya", "Raghav", "Ritesh", "Divyesh", "Akhyaan", "Ashvath", "Eeshan",
    "Vybhav", "Artemii", "Nirvaan", "Hrishik", "Qixuan", "Lelin", "Shreyan", "Myren",
    "Raeyaan", "Vardaan", "Ramu", "Romir", "Nahyeon", "Sumedh", "Samanyu", "Hannak",
    "Maanav", "Shaan", "Himanish", "Mahammed", "Akshat", "Ayush", "Dhairya", "Angad",
    "Vivaan", "Harikumar", "Iverson", "Addhyan", "Savir", "Hanish", "Saketh", "Sourish",
    "Ekagra", "Jayesh", "Ashay", "Junwon", "Vihan", "Aviyan", "Yikai", "JiaJing",
    "Harshvardhan", "Pranay", "Junheng", "Kuan", "Jiaxi", "Tashan", "Brighten",
    "Sidhvin", "Yeojoon", "Nikit", "Shubham", "Kangjue", "Aiyin", "Hongkang", "Shiven",
    "YoYo", "Shaurya", "Shreyan", "Videep", "Isato", "Jinghang", "Minwei", "Uy",
    "Yixuan", "Saatvik", "Anirrudha", "Zejia", "Minglang", "Yi", "Minxing", "Jinghan",
    "Muyi", "Chunyue", "Anay", "Aahlad", "Pinmo", "Eason", "Rajit", "Advik", "Ruoqi",
    "Jiayuan", "Dashan", "Kinshuk", "Samanvay", "Raghav", "Avyank", "Riyansh",
    "Ritam", "Atishar", "Baer", "Inesh", "Aayush", "Sujay", "Sumner", "Mukundh",
    "Niral", "Aaroosh", "Haoqi", "Aryaman", "Naman", "Lakshmana", "Anirvin", "Haoyun",
    "Shihan", "Neelkanth", "Rishan", "Luoyi", "Seyth", "Aarnav", "Kalkin", "Saarang",
    "Wenbo", "Wenyuan", "Astin", "Ruiyang", "Shivan", "Vishwesh", "Srinadh", "Prashanth",
    "Harshith", "Bidith", "Shiven", "Tianran", "Yuze", "Weiyang", "Jiaheng", "Zixi",
    "Anlong", "Ruoyu", "Yingkai", "Yanxun", "Inhoo", "Pratham", "Yunfei", "Aariv",
    "Anish", "Xiaoxing", "Ziming", "Liheng", "Tymon", "Neo", "Sparsh", "Pranshu",
    "Arhaan", "Lexing", "Sarvesh", "Athithan", "Shuhan", "Kaavin", "Guhan", "Abhishek",
    "Seungheon", "Paixiao", "Vachan", "Praneet", "Jewon", "Zhaitong", "Yutong", "Dhilan",
    "Ashwin", "Revaant", "Vunal", "Xiuqi", "Kosei", "Yewon", "Zhiming", "Peilin",
    "Rishav", "Mehul", "Arav", "Ruixun", "Zenan", "Nayeon", "Zeen", "Srivibhav",
    "Akhil", "Dashiel", "Somil", "Jevin", "Hanlin", "Hanyuan", "Xizhi", "Chit",
    "Hauming", "Yanwen", "Yanlin", "Taison", "Kaustubh", "Rishi", "Saravanan",
    "Anagh", "Rohin", "Ishan", "Rithwik", "Saavir", "Videesh", "Hanwen", "Han",
    "Dhrish", "Giang", "Shengyuan", "Smaran", "Aanik", "Anushi", "Nakul",
    "Shriraman", "Stavya", "Vedavit", "Vriddhi", "Yashmit", "Lekang", "Siddh",
    "Yatharth", "Zixuan", "Min", "Shaunak", "Xuejia", "Inay", "Kyril", "Risheeth",
    "Rusheel", "Saurya", "Shreesh", "Srujan", "Thanuj", "Xianzhi", "Amahl",
    "Kaihan", "Narasimhan", "Risuning", "Sarthak", "Shivam", "Sihao", "Wentao",
    "Yevin", "Yolin", "Yuvaan", "Ahan", "Dattasai", "Hemansh", "Ubayd", "Hongyi",
    "Amane", "Arhan", "Hanbin", "Mirandasana", "Nirdvaita", "Ruyi", "Sergy",
    "Sridhar", "Suvir", "Theta", "Yundi", "Youbin", "Sri", "Kanav", "Agustya",
    "Jerrae", "Sai", "Fengyi", "Zimeng", "Xuhui", "Boyang", "Shuming", "Siddanth",
    "Ishir", "Keval", "Heerok", "Viren", "Yulong", "Payton", "Zayeed", "Canis",
    "Varun", "Apurva", "Vrishak", "Ayetra", "Stanigost", "Atticus", "Ryuya",
    "Yufan", "Ranai", "Samay", "Tianyi", "Saveer", "Shriyan", "Lokesh",
    "Shi", "Parthapratim", "Mrigank", "Sritan", "Tiancheng", "Dash", "Yuxian",
    "Agam", "Pratinav", "Podtakorn", "Aaditya", "Radley", "Satina", "Atreya",
    "Nirmit", "Keona", "Tejash", "Amlan", "Samuelson", "Rishi", "Hanlin", "Qian",
    "Jing", "Arnesh", "Exner", "Xindi", "Ryka", "Vedanth", "Karanveer", "Agrim",
    "Aaryan", "Ameya", "Sankeerth", "Nikaansh", "Ariya", "Advaith", "Daxton",
    "Rohin", "Suryan", "Ruike", "Zifei", "Derin", "Junwoo", "Pagkratios", "Rayming",
    "Ritvin", "Royden", "Sushanth", "Yihan", "Jovin", "Alexannder",
    "Zhuoqun", "Linyun", "Golden", "Xiyuan", "Aadithya", "Advait", "Anuj",
    "Asteris", "Satvik", "Andersen", "Rabhya", "Aum", "Avik", "Xiaotian",
    "Zhengyin", "Yuexin", "SaiPranav", "Tsz", "Hin", "Ji", "Yifan", "Zimou",
    "Toprak", "Junyi",
})


def load_students_missing_gender() -> List[Tuple[int, str, str]]:
    """Return [(student_id, student_name, alias), ...] for rows with empty gender."""
    rows: List[Tuple[int, str, str]] = []
    with STUDENTS_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            gender = (row.get("gender") or "").strip()
            if gender:
                continue
            try:
                sid = int((row.get("student_id") or "").strip())
            except (ValueError, TypeError):
                continue
            name = (row.get("student_name") or "").strip()
            alias = (row.get("alias") or "").strip()
            rows.append((sid, name, alias))
    return rows


def _get_openai_client():
    try:
        import openai
    except ImportError:
        print("Install openai: pip install openai", file=sys.stderr)
        raise
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is not set")
    return openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def call_llm_infer_gender_batch(
    items: List[Tuple[int, str, str]], batch_size: int = 50
) -> List[Tuple[int, str, int]]:
    """
    Call LLM to infer gender from student name (batched).
    items = [(student_id, student_name, alias), ...]
    Returns [(student_id, gender, confidence_0_100), ...].
    """
    client = _get_openai_client()
    results: List[Tuple[int, str, int]] = []

    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        numbered = []
        for j, (sid, name, alias) in enumerate(batch):
            display = name
            if alias:
                display = f"{name} (alias: {alias})"
            numbered.append(f"{j+1}. id={sid} | {display}")

        prompt = """Given these student names (from US math competition data), infer the most likely gender for each based on the name ONLY.

Consider:
- First name(s) and any parenthetical or nickname (e.g. "Jiayu Ellie Su" → Ellie suggests female).
- Prefer US/English naming conventions when the name allows (e.g. "Alexander" → male, "Charlotte" → female).
- For names that are clearly unisex or ambiguous, or that you do not recognize well, return low confidence and do not guess.
- Output only "male" or "female"; do not use other values.

List (each line: id=student_id, then name):
%s

Reply with a JSON array. Each element must have:
- "id": the student_id number (integer)
- "gender": "male" or "female"
- "confidence": Your confidence that the inference is correct, 0 to 100 (integer). Use lower values for unisex names (e.g. Alex, Jordan, Dakota), ambiguous names, or names you do not recognize well.

Example: [{"id": 2520, "gender": "male", "confidence": 75}, {"id": 2535, "gender": "female", "confidence": 95}]
Reply with only the JSON array, no other text."""

        body = "\n".join(numbered)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt % body}],
            temperature=0,
        )
        text = (response.choices[0].message.content or "").strip()
        if "```" in text:
            text = re.sub(r"^.*?```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```.*$", "", text)
        try:
            arr = json.loads(text)
            if not isinstance(arr, list):
                arr = [arr]
            id_to_item = {sid: (sid, name, alias) for sid, name, alias in batch}
            for elem in arr:
                try:
                    sid = int(elem.get("id")) if elem.get("id") is not None else None
                except (TypeError, ValueError):
                    sid = None
                if sid is None or sid not in id_to_item:
                    continue
                g = (elem.get("gender") or "").strip().lower()
                if g not in ("male", "female"):
                    g = ""
                conf = elem.get("confidence")
                conf = max(0, min(100, int(conf))) if conf is not None else 0
                results.append((sid, g, conf))
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            print(f"Batch parse error: {e}", file=sys.stderr)
            for sid, _, _ in batch:
                results.append((sid, "", 0))

    return results


def infer_gender_local(items: List[Tuple[int, str, str]]) -> List[Tuple[int, str, int]]:
    """Use gender-guesser library for local inference (no API)."""
    try:
        import gender_guesser.detector as gender
    except ImportError:
        print("Install: pip install gender-guesser", file=sys.stderr)
        raise SystemExit(1)
    d = gender.Detector(case_sensitive=False)
    results: List[Tuple[int, str, int]] = []

    def get_first_names(name: str, alias: str) -> List[str]:
        """Extract first names from full name and alias, including parenthetical nicknames."""
        tokens = []
        for s in (name, alias):
            if not s:
                continue
            for part in s.replace(",", " ").split():
                part = part.strip()
                if "(" in part:
                    pre = part.split("(")[0].strip()
                    if pre and len(pre) > 1:
                        tokens.append(pre)
                    inner = part.split("(")[1].rstrip(")").strip()
                    if inner and len(inner) > 1:
                        tokens.append(inner)
                elif part and len(part) > 1:
                    tokens.append(part)
        return tokens

    for sid, name, alias in items:
        first_names = get_first_names(name, alias)
        if not first_names:
            results.append((sid, "", 0))
            continue
        primary = first_names[0]
        g_primary = d.get_gender(primary)
        g_best = g_primary
        for fn in first_names[1:]:
            g = d.get_gender(fn)
            if g in ("female", "mostly_female") and g_best in ("male", "mostly_male", "unknown", "andy"):
                g_best = g
                break
            if g in ("male", "mostly_male") and g_best in ("female", "mostly_female", "unknown", "andy"):
                g_best = g
                break
        if g_best in ("male", "mostly_male"):
            conf = 90 if g_best == "male" else 85
            results.append((sid, "male", conf))
        elif g_best in ("female", "mostly_female"):
            conf = 90 if g_best == "female" else 85
            results.append((sid, "female", conf))
        else:
            results.append((sid, "", 0))
    return results


def infer_gender_supplement(items: List[Tuple[int, str, str]]) -> List[Tuple[int, str, int]]:
    """Second pass: curated names gender-guesser misses (Indian, Chinese, Korean, etc.)."""
    results: List[Tuple[int, str, int]] = []

    def get_first_names(name: str, alias: str) -> List[str]:
        tokens = []
        for s in (name, alias):
            if not s:
                continue
            for part in s.replace(",", " ").split():
                part = part.strip()
                if "(" in part:
                    pre = part.split("(")[0].strip()
                    if pre and len(pre) > 1:
                        tokens.append(pre)
                    inner = part.split("(")[1].rstrip(")").strip()
                    if inner and len(inner) > 1:
                        tokens.append(inner)
                elif part and len(part) > 1:
                    tokens.append(part)
        return tokens

    for sid, name, alias in items:
        first_names = get_first_names(name, alias)
        if not first_names:
            results.append((sid, "", 0))
            continue
        found = None
        for fn in first_names:
            if fn in SUPPLEMENT_FEMALE:
                found = "female"
                break
            if fn in SUPPLEMENT_MALE:
                found = "male"
                break
        if found:
            results.append((sid, found, 85))
        else:
            results.append((sid, "", 0))
    return results


def apply_from_json(json_path: Path) -> None:
    """Apply pre-computed inferences from JSON file. Format: [{"student_id": N, "gender": "male"|"female", "confidence": 0-100}, ...]"""
    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        data = [data]
    inferred: Dict[int, str] = {}
    for elem in data:
        try:
            sid = int(elem.get("student_id"))
        except (TypeError, ValueError):
            continue
        g = (elem.get("gender") or "").strip().lower()
        conf = elem.get("confidence")
        conf = max(0, min(100, int(conf))) if conf is not None else 0
        if g in ("male", "female") and conf > CONFIDENCE_THRESHOLD:
            inferred[sid] = g
    items = load_students_missing_gender()
    id_to_name = {sid: (name, alias) for sid, name, alias in items}
    cannot_infer = [
        {"student_id": str(sid), "student_name": name, "alias": alias}
        for sid, name, alias in items
        if sid not in inferred
    ]
    print(f"Inferred with >{CONFIDENCE_THRESHOLD}% confidence: {len(inferred)}")
    print(f"Cannot infer: {len(cannot_infer)}")
    with STUDENTS_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)
    updated = 0
    for row in rows:
        try:
            sid = int((row.get("student_id") or "").strip())
        except (ValueError, TypeError):
            continue
        if sid in inferred:
            row["gender"] = inferred[sid]
            updated += 1
    with STUDENTS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Updated {updated} rows in {STUDENTS_CSV}")
    CANNOT_INFER_TXT.parent.mkdir(parents=True, exist_ok=True)
    with CANNOT_INFER_TXT.open("w", encoding="utf-8") as f:
        f.write("student_id\tstudent_name\talias\n")
        for s in cannot_infer:
            f.write(f"{s['student_id']}\t{s['student_name']}\t{s.get('alias', '')}\n")
    print(f"Wrote cannot-infer list to {CANNOT_INFER_TXT}")


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    no_llm = "--no-llm" in sys.argv
    apply_from = None
    for i, a in enumerate(sys.argv):
        if a == "--apply-from" and i + 1 < len(sys.argv):
            apply_from = sys.argv[i + 1]
            break
        if a.startswith("--apply-from="):
            apply_from = a.split("=", 1)[1]
            break
    if apply_from:
        apply_from_json(ROOT / apply_from)
        return
    batch_size = 50
    for a in sys.argv[1:]:
        if a.startswith("--batch-size="):
            batch_size = int(a.split("=")[1])

    items = load_students_missing_gender()
    print(f"Students with missing gender: {len(items)}")

    if not items:
        print("Nothing to do.")
        return

    if no_llm:
        # Write JSON for external LLM processing
        data = [
            {"student_id": sid, "student_name": name, "alias": alias}
            for sid, name, alias in items
        ]
        INPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        with INPUT_JSON.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Wrote {len(data)} students to {INPUT_JSON} for external LLM processing.")
        return

    if "--supplement" in sys.argv:
        results = infer_gender_supplement(items)
    elif "--local" in sys.argv:
        results = infer_gender_local(items)
    else:
        results = call_llm_infer_gender_batch(items, batch_size=batch_size)

    # Build id -> (gender, confidence)
    id_to_result: Dict[int, Tuple[str, int]] = {}
    for sid, gender, conf in results:
        id_to_result[sid] = (gender, conf)

    # Build inferred (confidence > 80) and cannot_infer
    inferred: Dict[int, str] = {}
    cannot_infer: List[Dict[str, str]] = []
    id_to_name_alias = {sid: (name, alias) for sid, name, alias in items}

    for sid, (gender, conf) in id_to_result.items():
        name, alias = id_to_name_alias.get(sid, ("", ""))
        if gender in ("male", "female") and conf > CONFIDENCE_THRESHOLD:
            inferred[sid] = gender
        else:
            cannot_infer.append({
                "student_id": str(sid),
                "student_name": name,
                "alias": alias,
            })

    print(f"Inferred with >{CONFIDENCE_THRESHOLD}% confidence: {len(inferred)}")
    print(f"Cannot infer (will report): {len(cannot_infer)}")

    if dry_run:
        print("\n[DRY RUN] Would update students.csv and write cannot-infer list.")
        return

    # Update students.csv
    with STUDENTS_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    updated = 0
    for row in rows:
        try:
            sid = int((row.get("student_id") or "").strip())
        except (ValueError, TypeError):
            continue
        if sid in inferred:
            row["gender"] = inferred[sid]
            updated += 1

    with STUDENTS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Updated {updated} rows in {STUDENTS_CSV}")

    # Write cannot-infer list
    CANNOT_INFER_TXT.parent.mkdir(parents=True, exist_ok=True)
    with CANNOT_INFER_TXT.open("w", encoding="utf-8") as f:
        f.write("student_id\tstudent_name\talias\n")
        for s in cannot_infer:
            f.write(f"{s['student_id']}\t{s['student_name']}\t{s.get('alias', '')}\n")
    print(f"Wrote cannot-infer list to {CANNOT_INFER_TXT}")


if __name__ == "__main__":
    main()
