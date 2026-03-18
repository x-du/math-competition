#!/usr/bin/env python3
"""
Apply fill-missing-gender prompt: update students.csv with inferred gender
only where inference from name has >80% confidence; list the rest as cannot-infer.
"""
import csv
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
STUDENTS_CSV = os.path.join(REPO_ROOT, "database", "students", "students.csv")

# student_id -> gender for names where LLM inference is >80% confident (male/female only).
# At 80% we also include: Donghyeon (male, Korean), Theo, Jayden, Brenon, Sunay, Joey,
# Junu, Karn, Sai, Zhifei, Eli, Zifan, Elliot, Vinci (male). Still exclude: unisex
# (Alex, Chris, Robin), ambiguous (Cris, Guiqing), unfamiliar (Time, Xei, Phuong, Seojin, Jaeyun).
INFERRED_GENDER = {
    2350: "male",   # Donghyeon Kim (Korean, typically male)
    2351: "male",   # Theo Wolens
    2352: "male",   # Jayden Gong
    2354: "male",   # Brenon Wang
    2355: "male",   # Sunay Miduthuri (Indian, typically male)
    2357: "male",   # Alexander Braun
    2359: "male",   # Vihaan Dev
    2360: "male",   # Joey Guo
    2361: "male",   # Vincent Huang
    2362: "male",   # Lionel Ip
    2363: "male",   # Dash Keffer
    2364: "male",   # Maxim Kolosov
    2365: "male",   # Matthew Kostikov
    2366: "female", # Annabelle Lee
    2367: "female", # Liana Lee
    2368: "male",   # Ronchen Luo
    2369: "male",   # Sidharth Midhun
    2370: "male",   # Junu Pae (Korean, typically male)
    2371: "male",   # Max Pham
    2378: "male",   # Karn Chutnian (Thai, typically male)
    2372: "male",   # Rohan Rajaram
    2373: "female", # Ritisha Srivastava
    2374: "male",   # Aiden Yan
    2375: "male",   # Simon Yang
    2376: "male",   # Tiancheng Zheng
    2377: "female", # Madelyn Zhu
    2379: "male",   # Rishi Shah
    2380: "male",   # Dekan Chen
    2381: "male",   # Mark Yutong Zhao
    2382: "male",   # Divit Mehra
    2383: "male",   # Owen Tang
    2384: "male",   # Patrick Deng
    2385: "male",   # Sai Chintagunta (Indian, often male)
    2386: "male",   # Spencer Wang
    2387: "male",   # Joshua Oliver
    2388: "male",   # Nikhil Reddy
    2389: "male",   # Zhifei Liu (志飞, typically male)
    2390: "male",   # Eli Gold (predominantly male)
    2391: "female", # Amy Ma
    2392: "male",   # Adithya Prabha
    2393: "male",   # Alexander Amrhein
    2394: "male",   # Gary Shen
    2399: "male",   # Zifan Zhao (子凡, often male)
    2397: "female", # Erica Xie
    2398: "male",   # David He
    2400: "male",   # Ian Liao
    2401: "male",   # Abhishek Chand
    2402: "female", # Sanjana Ramesh
    2403: "female", # Meghana Myneni
    2404: "male",   # Siddharth Sangi
    2405: "male",   # Matthew Zhang
    2407: "male",   # Cooper Salts
    2408: "male",   # Owen Xu
    2409: "male",   # Oscar Varodayan
    2410: "male",   # Ayan Sharma
    2411: "male",   # Alan Verbitsky
    2412: "male",   # Ethan Yin
    2413: "male",   # Kieran Callahan
    2415: "male",   # Minghao Guo
    2416: "male",   # Jayson Quah
    2417: "male",   # Nathan Song
    2418: "female", # Alice Wang
    2419: "male",   # Sohum Tavisala
    2420: "male",   # Aiden Shan
    2422: "male",   # Daniel Luo
    2423: "female", # Ava Berenji
    2424: "female", # Tiffany Meng
    2425: "male",   # Vedanth Chakravarthi
    2427: "male",   # Brandon Muliadi
    2428: "male",   # Spencer Hill
    2429: "female", # Lily Shi
    2430: "male",   # Prince Rohatgi
    2431: "female", # Daphne Chen
    2432: "female", # Nupur Krishnan
    2433: "male",   # Nathan Chen
    2434: "male",   # Satyaki Sen
    2435: "male",   # Anshuman Arun
    2436: "female", # Manalee Chowdhury
    2437: "male",   # Alexey Chub
    2438: "male",   # Anshul Dandekar
    2439: "male",   # Kaiyuan Ding
    2440: "male",   # Itai Firstenberg
    2441: "male",   # Aiden Fong
    2442: "female", # Allison Guan
    2444: "male",   # Kevin Lu
    2445: "male",   # Elliot Maa (Elliot skews male)
    2446: "male",   # Henry Meier
    2447: "female", # Bridget Procter
    2448: "male",   # Vsevolod Titov
    2449: "male",   # Kyle Wan
    2450: "male",   # Derek Wu
    2451: "male",   # Graham Zhang
    2452: "male",   # Randy Zhong
    2456: "male",   # Julian Xiao
    2457: "male",   # August Deer
    2458: "female", # Natalie Deering
    2459: "female", # Ella Gal-on
    2460: "male",   # Jackson Gish
    2461: "female", # Anna Johnston
    2462: "male",   # Peter Matsakis
    2463: "male",   # Emmett Mighdoll
    2464: "male",   # Rohan Ramkumar
    2465: "male",   # Arnav Ratna
    2466: "male",   # Ganesh Sankar
    2467: "male",   # Peter Vandervelde
    2468: "male",   # Taras Abakumov
    2469: "male",   # Vinci Ho (often short for Vincent)
    2470: "male",   # Ryan Lee
    2471: "female", # Anju Aoi
    2472: "male",   # Kaison Fong
    2473: "male",   # Justin Fu
    2474: "male",   # Rithwik Gupta
    2475: "male",   # Connor Huh
    2476: "female", # Helen Law
    2477: "male",   # Alexander Maresov
    2478: "male",   # Ibrahim Piri
    2479: "male",   # Axel Szolusha
    2480: "male",   # Bryant Wang
    2482: "male",   # Sebastian Weinberger
    2483: "male",   # Fateh Aliyev
    2484: "female", # Jacqueline Wang
    2485: "male",   # Sanjay Kaushik
}


def main():
    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    cannot_infer = []
    updated = 0
    for row in rows:
        sid = row.get("student_id", "")
        try:
            student_id = int(sid)
        except (ValueError, TypeError):
            continue
        gender = (row.get("gender") or "").strip()
        if gender:
            continue
        if student_id in INFERRED_GENDER:
            row["gender"] = INFERRED_GENDER[student_id]
            updated += 1
        else:
            cannot_infer.append({
                "student_id": sid,
                "student_name": row.get("student_name", ""),
                "alias": row.get("alias", ""),
            })

    with open(STUDENTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Updated {updated} rows with inferred gender.")
    print(f"Cannot infer ({len(cannot_infer)} students):")
    for s in cannot_infer:
        alias = f" (alias: {s['alias']})" if s.get("alias") else ""
        print(f"  {s['student_id']} | {s['student_name']}{alias}")

    # Write cannot-infer list to file for manual follow-up
    out_path = os.path.join(REPO_ROOT, "prompts", "fill-missing-gender-cannot-infer.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("student_id\tstudent_name\talias\n")
        for s in cannot_infer:
            f.write(f"{s['student_id']}\t{s['student_name']}\t{s.get('alias', '')}\n")
    print(f"\nWrote cannot-infer list to {out_path}")


if __name__ == "__main__":
    main()
