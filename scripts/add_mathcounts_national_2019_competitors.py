#!/usr/bin/env python3
"""
Create Mathcounts National 2019 competitors.csv from PDF data.
Matches students to students.csv; creates new records for unmatched students.
"""

import csv
import re
from pathlib import Path
from typing import Optional, Tuple

REPO = Path(__file__).resolve().parent.parent
STUDENTS_CSV = REPO / "database" / "students" / "students.csv"
COMPETITORS_DIR = REPO / "database" / "contests" / "mathcounts-national" / "year=2019"

# Multi-word cities - must be checked first when splitting city/school
COMPOUND_CITIES = {
    "Baton Rouge", "Little Rock", "West Lafayette", "Silver Spring",
    "East Providence", "North Charleston", "Salt Lake City", "Falls Church",
    "Upper Tumon", "Greenwood Village", "Bloomfield Hills", "Overland Park",
    "Ellicott City", "San Jose", "Palo Alto", "San Ramon", "Scottsdale",
    "Fort Collins", "New Haven", "New York", "Saint Louis", "Saint Thomas",
    "North Oaks", "Grand Forks", "Rapid City", "Las Vegas", "Sugar Land",
    "Missouri City", "Clifton Park", "West Windsor", "East Lyme",
    "Vestavia Hills", "Colorado Springs", "Oro Valley", "Oak Brook",
    "Beverly Hills", "San Juan", "Upper Arlington", "Clay Center",
}

# 2019 PDF data - STATE, FIRST, LAST, S/C, GRADE, CITY, SCHOOL
# Format: state name_parts S/C grade city school
PDF_LINES = """
Alabama Justin Pan S 8 Madison Discovery Middle School
Alabama Siddharth Doppalapudi S 8 Birmingham Altamont School
Alabama Ruoge Li S 7 Vestavia Hills Louis Pizitz Middle School
Alabama Daniel Zhao S 8 Birmingham Alabama School of Fine Arts
Alaska Alex Loomis S 8 Anchorage Romig Middle School
Alaska Camden Armstrong S 8 Anchorage Romig Middle School
Alaska Sean Raften S 8 Kenai Kenai Middle School
Alaska Elias Bailey S 8 Anchorage Romig Middle School
Arizona Marcus Giorza S 8 Phoenix Madison #1 Middle School
Arizona Sai Konkimalla S 8 Oro Valley BASIS Oro Valley
Arizona Shaan Keole S 7 Phoenix BASIS Phoenix
Arizona Yoobin Cha S 6 Chandler Arizona College Prep-Oakland
Arkansas Soren Schmidt S 8 Bentonville Thaden School
Arkansas Aaron Liu S 8 Little Rock LISA Academy
Arkansas Dinesh Vasireddy S 8 Bentonville Fulbright Junior High School
Arkansas Ellie Feng S 7 Conway Ruth Doyle Middle School
California Eric Shen S 8 San Jose Miller Middle School
California Alan Lee S 8 Palo Alto Ellen Fletcher Middle School
California William Chen S 8 Fremont William Hopkins Junior High
California Andrew Wen S 8 Fremont William Hopkins Junior High
Colorado Ari Wang S 8 Colorado Springs Mountain Ridge Middle School
Colorado Srinivas Arun S 7 Greenwood Village Campus Middle School
Colorado Jackson Dryg S 7 Fort Collins Preston Middle School
Colorado Rishi Rai S 7 Denver Challenge School
Connecticut Adeethyia Shankar S 8 Brookfield Whisconier Middle School
Connecticut Mingwen Duan S 7 Niantic East Lyme Middle School
Connecticut Yunrui Yang S 8 New Haven The Foote School
Connecticut Alan Wang S 8 Farmington Irving A. Robbins Middle School
Delaware Perryn Chang S 8 Wilmington PS DuPont Middle School
Delaware Jonathan Pei S 8 Wilmington PS DuPont Middle School
Delaware Mia Lu S 8 Newark The Independence School
Delaware Anand John S 8 Wilmington PS DuPont Middle School
Department of Defense Faisal Ramzi Al Sewaidi S 8 Bahrain Bahrain Middle/High School
Department of Defense Mason Parker S 8 Germany Ramstein Middle School
Department of Defense Brian Song S 8 Korea Humphreys Middle School
Department of Defense Seth Robles S 8 Germany Hohenfels Middle High School
District of Columbia Robert Foster S 7 Washington Sidwell Friends School
District of Columbia Jonathan Nixon S 8 Washington Sidwell Friends School
District of Columbia Matthew Weitzner S 6 Washington Alice Deal Middle School
District of Columbia Sherlock Grigsby II S 6 Washington Georgetown Day School
Florida Wesley Chen S 8 Tallahassee Deerlake Middle School
Florida Karthik Vedula S 8 Tallahassee Fairview Middle School
Florida Razzi Masroor S 7 Miami Doral Academy Charter Middle School
Florida Aaron Hu S 7 Tallahassee Deerlake Middle School
Georgia Ethan Gao S 8 Alpharetta Fulton Science Academy
Georgia Richard Yu S 8 Alpharetta Fulton Science Academy
Georgia Andy Zhang S 8 Cumming South Forsyth Middle School
Georgia Kevin Yuan S 8 Alpharetta Fulton Science Academy
Guam Seungryeol Tae S 8 Upper Tumon St. John's School
Guam Kevin Choi S 7 Upper Tumon St. John's School
Guam Kangsan Yoon S 7 Barrigada Harvest Christian Academy
Guam Elizabeth Mamczarz S 7 Barrigada Harvest Christian Academy
Hawaii Adam Yoshiaki Inamasu S 8 Honolulu Washington Middle School
Hawaii Felicity Zhou S 8 Honolulu Washington Middle School
Hawaii Allison Eto S 8 Honolulu Iolani School
Hawaii Zachary Tyrrell S 8 Honolulu Washington Middle School
Idaho Zihongbo Wang S 8 Boise East Junior High School
Idaho Kevin Xu S 8 Boise East Junior High School
Idaho Srikar Surapaneni S 8 Rathdrum North Idaho STEM Charter Academy
Idaho Jieming Mei S 8 Boise East Junior High School
Illinois Krishna Pothapragada S 7 Lisle Kennedy Junior High School
Illinois Nate Maydanchik S 6 Oak Brook Butler Junior High School
Illinois Jeffrey Chen S 8 Chicago University of Chicago Laboratory Schools
Illinois Nathan Ma S 8 Lincolnshire Daniel Wright Junior High School
Indiana Ray Li S 8 West Lafayette West Lafayette Junior Senior High School
Indiana Harry Zheng S 8 Carmel Clay Middle School
Indiana Minnie Liang S 8 West Lafayette West Lafayette Junior Senior High School
Indiana Grace Yang S 8 Indianapolis Sycamore School
Iowa Joe Su S 8 Clive Indian Hills Junior High School
Iowa Anish Lodh S 8 Coralville Northwest Junior High
Iowa Ashley Seo S 8 Coralville Northwest Junior High
Iowa SangHyuk Im S 8 Coralville Northwest Junior High
Kansas Naveen Kannan S 8 Overland Park Pleasant Ridge Middle School
Kansas Rebecca Xue S 7 Overland Park Lakewood Middle School
Kansas Nathan Zhang S 8 Olathe California Trail Middle School
Kansas David Han S 8 Overland Park Lakewood Middle School
Kentucky Luke Mo S 8 Louisville Meyzeek Middle School
Kentucky Joseph Vulakh S 7 Lexington Tates Creek Middle School
Kentucky Krishna Bhatraju S 8 Lexington Winburn Middle School
Kentucky Shaurya Jadhav S 8 Henderson Holy Name School
Louisiana Alex Wu S 8 Baton Rouge LSU Lab School
Louisiana Julian Vertigan S 7 Baton Rouge Vertigan Family Homeschool
Louisiana Ryan Ding S 8 Baton Rouge Glasgow Middle School
Louisiana Ethan Guo S 8 Baton Rouge Glasgow Middle School
Maine Albert Bai S 7 Hermon Hermon Middle School
Maine Noah Manning S 8 Kennebunk Middle School of the Kennebunks
Maine Eamon Flint McGlashan S 8 Kennebunk Middle School of the Kennebunks
Maine Karl Hokkanen S 7 Camden Camden-Rockport Middle School
Maryland Joshua Hsieh S 8 Silver Spring Takoma Park Middle School
Maryland Andrew Yuan S 8 Germantown Roberto Clemente Middle School
Maryland Nathan Shan S 8 Silver Spring Takoma Park Middle School
Maryland David Li S 8 Ellicott City Burleigh Manor Middle School
Massachusetts Max Xu S 8 Westford Stony Brook Middle School
Massachusetts Daniel Mai S 8 Acton RJ Grey Junior High School
Massachusetts Huaye Lin S 8 Lexington Jonas Clarke Middle School
Massachusetts Kaylee Ji S 8 Andover Doherty Middle School
Michigan Vikram Goddla S 7 Beverly Hills Detroit Country Day Middle School
Michigan Jason Zhang S 7 Plymouth East Middle School
Michigan Michael Lu S 6 Bloomfield Hills Bloomfield Hills Middle School
Michigan Henry Jiang S 6 Beverly Hills Detroit Country Day Middle School
Minnesota Andrew Zhang S 8 Plymouth Wayzata Central Middle School
Minnesota Linden Li S 8 North Oaks Chippewa Middle School
Minnesota Aurora Wang S 8 North Oaks Chippewa Middle School
Minnesota Henry Zheng S 7 Edina Valley View Middle School
Mississippi Kenichiro Suzuki S 8 Madison Madison Middle School
Mississippi Leo Mei S 8 Madison Madison Middle School
Mississippi Dhanush Kondabathini S 8 Madison Germantown Middle School
Mississippi Landon Tu S 7 Madison Madison Middle School
Missouri Nicole Li S 8 Saint Louis Ladue Middle School
Missouri Alex Chen S 8 Ellisville Crestview Middle School
Missouri Wilson Gao S 8 Chesterfield Parkway West Middle School
Missouri Yuvan Chali S 8 Saint Louis Ladue Middle School
Montana Edward Guthrie S 8 Bozeman Gallatin Valley Homeschool
Montana Yuan Du S 7 Missoula Washington Middle School
Montana Cadien Archer S 7 Billings Lewis & Clark Middle School
Montana Jonas Zeiler S 7 Billings Lewis & Clark Middle School
Nebraska Cole Welstead S 8 Lincoln Lux Middle School
Nebraska Jason Jiang S 7 Lincoln Hazel G. Scott Middle School
Nebraska Nixon Hanna S 7 Lincoln Lux Middle School
Nebraska Kaleb Whitmore S 7 Clay Center Sandy Creek Middle School
Nevada Frank Abbeduto S 8 Henderson Bob Miller Middle School
Nevada Audrey Lim S 8 Reno Davidson Academy
Nevada Megan Davi S 8 Reno Davidson Academy
Nevada Christopher Bao S 6 Las Vegas The Adelson Educational Campus School
New Hampshire Garima Rastogi S 7 Concord Rastogi Homeschool
New Hampshire Anshul Rastogi S 8 Concord Rastogi Homeschool
New Hampshire Roxane Park S 6 Lyme Crossroads Academy
New Hampshire Deetya Nagri S 7 Nashua Academy for Science and Design
New Jersey Kishan Bava S 8 Livingston Heritage Middle School
New Jersey Qirui Cai S 8 West Windsor Thomas Grover Middle School
New Jersey George Cao S 8 Skillman Montgomery Middle School
New Jersey Bryan Zhang S 8 Green Brook Green Brook Middle School
New Mexico Charles Cai S 8 Los Alamos Los Alamos Middle School
New Mexico Alexander Livescu S 8 Los Alamos Los Alamos Middle School
New Mexico Grant Staten S 8 Albuquerque Desert Ridge Middle School
New Mexico Harmony Guan S 7 Albuquerque Desert Ridge Middle School
New York Matthew Zhao S 8 Scarsdale Scarsdale Middle School
New York Forrest Gao S 8 Clifton Park Acadia Middle School
New York Davis Zong Jr. S 7 New York Hunter College High School
New York Brandon Lou S 8 New York Hunter College High School
North Carolina Minseok Park S 8 Raleigh Carnage Middle School
North Carolina Brian Zhang S 7 Raleigh Carnage Middle School
North Carolina Sukrith Velmineti S 8 Raleigh Carnage Middle School
North Carolina Eric Wu S 7 Cary Triangle Math And Science Academy
North Dakota Nolan Severance S 8 Hunter Northern Cass Public School
North Dakota Dylan Raaum S 8 Grand Forks Schroeder Middle School
North Dakota Rick Peng S 7 Fargo Discovery Middle School
North Dakota Patrick Shen S 7 Fargo Discovery Middle School
Ohio Edward Kong S 8 Mason Mason Middle School
Ohio Tanishq Pauskar S 7 Massillon Jackson Memorial Middle School
Ohio Michael Zuo S 8 Mason Mason Middle School
Ohio Riddhi Gupta S 8 Upper Arlington Jones Middle School
Oklahoma Daniel Wang S 8 Jenks Jenks Middle School
Oklahoma Timothy Stroup S 8 Jenks Jenks Middle School
Oklahoma Raymond Jiang S 8 Jenks Jenks Middle School
Oklahoma Nathaniel Willcox S 8 Tulsa University School
Oregon Ram Goel S 8 Portland Krishna Homeschool
Oregon Suyash Pandit S 8 Portland Cedar Park Middle School
Oregon Alan Kappler S 8 Hillsboro Davidson Academy
Oregon Nividh Singh S 8 Portland Stoller Middle School
Pennsylvania Vivian Loh S 7 Pittsburgh Winchester Thurston School
Pennsylvania Ethan Liu S 8 Wayne Valley Forge Middle School
Pennsylvania Thrisha Kalpatthi S 7 Wexford Marshall Middle School
Pennsylvania Skyler Le S 8 Wayne Radnor Middle School
Puerto Rico Jessica Wan S 7 San Juan Saint John's School
Puerto Rico Gustavo Carrion Rodriguez S 8 Caguas Cimatec School
Puerto Rico Fernando Mediavilla S 8 San Juan Colegio San Ignaciode Loyola
Puerto Rico Jerry Chen S 7 San Juan Saint John's School
Rhode Island Andrew Song S 7 East Providence Gordon School
Rhode Island William Bruno S 6 Providence The Wheeler School
Rhode Island Louise Marie Choi Schattle S 8 Barrington Barrington Middle School
Rhode Island Kamran Pahlavi S 8 Barrington Barrington Middle School
South Carolina Kaylee Chen S 8 Irmo Dutch Fork Middle School
South Carolina Ahan Shi S 7 Central R.C. Edwards Middle School
South Carolina Scott Fowler S 8 Lyman DR Hill Middle School
South Carolina Angela Mei S 8 North Charleston Charleston County School of the Arts
South Dakota Megan Zhu S 8 Rapid City Southwest Middle School
South Dakota Sampada Nepal S 7 Brookings George S. Mickelson Middle School
South Dakota Vanessa An S 7 Brookings George S. Mickelson Middle School
South Dakota Gianna Stangeland S 8 Pierre George S. Mickelson Middle School
State Department Owen Lalis S 8 Japan Nagoya International School
State Department Avi Kabra S 8 Singapore Singapore American School
State Department Josh Shin S 6 Singapore Singapore American School
State Department Jaeha Hwang S 8 India American Embassy School
Tennessee George Hu S 7 Knoxville Farragut Middle School
Tennessee Alexander Wang S 8 Nashville Montgomery Bell Academy
Tennessee Bryan Ding S 7 Memphis Memphis University School
Tennessee Henry Pitt S 8 Nashville Montgomery Bell Academy
Texas Aaron Guo S 8 Plano Rice Middle School
Texas Rich Wang S 8 Missouri City Quail Valley Middle School
Texas Ray Tang S 8 Missouri City Quail Valley Middle School
Texas Amy Chang S 8 Sugar Land Fort Settlement Middle School
Utah Zachary Klein S 8 Salt Lake City Rowland Hall
Utah Marianne Liu S 8 Salt Lake City West High School
Utah Brian Wei S 6 Salt Lake City Wasatch Junior High School
Utah Kiran Reddy S 6 Sandy Waterford School
Vermont Kirk Smith S 7 Rutland Rutland Town School
Vermont Keaton St. Martin S 8 Vergennes Vergennes Union Middle School
Vermont Saksham Bhardwaj S 8 South Burlington F.H. Tuttle Middle School
Vermont Jacob Graham S 6 Middlebury Middlebury Union Middle School
Virgin Islands Ronit Totwani S 8 Saint Thomas Antilles School
Virgin Islands Julien Loewenstein S 7 Saint Thomas Antilles School
Virgin Islands Ariel Paul S 8 Saint Thomas Antilles School
Virgin Islands Aisha Khemani S 8 Saint Thomas Antilles School
Virginia Samuel Wang S 8 McLean BASIS Independent McLean
Virginia Ethan Zhou S 8 McLean BASIS Independent McLean
Virginia Alan Vladimiroff S 8 Falls Church Longfellow Middle School
Virginia Aiden Feyerherm S 6 Vienna Westbriar Elementary School
Washington Joy An S 8 Bellevue Odle Middle School
Washington Gene Yang S 8 Bellevue Odle Middle School
Washington Albert Weng S 8 Issaquah Beaver Lake Middle School
Washington Wilson Liu S 8 Redmond Evergreen Middle School
West Virginia Amy Lu S 8 Morgantown Suncrest Middle School
West Virginia Lauren Shen S 7 Morgantown Suncrest Middle School
West Virginia Austin Luo S 6 Morgantown Suncrest Middle School
West Virginia Grace Yan S 7 Morgantown Suncrest Middle School
Wisconsin Jacob Rottier S 8 De Pere West De Pere Middle School
Wisconsin Kevin Song S 8 Madison Velma Hamilton Middle School
Wisconsin Kartik Ramachandrula S 6 Brookfield Wisconsin Hills Middle School
Wisconsin Alexis Hu S 8 Shorewood Shorewood Intermediate School
Wyoming Dane Lauritzen S 8 Powell Powell Middle School
Wyoming Felicity Olsson S 7 Lander Lander Middle School
Wyoming Cooper Kaligis S 8 Laramie Laramie Middle School
Wyoming Jack Weiss S 7 Gillette Sage Valley Junior High School
""".strip().split("\n")


def parse_line(line: str) -> Optional[Tuple[str, str, int, str, str]]:
    """Parse a line into (state, student_name, grade, city, school). Returns None for invalid lines."""
    line = line.strip()
    if not line:
        return None
    # Match: STATE ... S <grade> CITY SCHOOL
    m = re.search(r"\s+S\s+([678])\s+(.+)$", line)
    if not m:
        return None
    grade = int(m.group(1))
    rest = m.group(2)  # city and school
    before_s = line[: m.start()].strip()
    # before_s is "STATE FirstName LastName" - need to split state from name
    state = None
    for s in [
        "Department of Defense", "District of Columbia", "State Department",
        "Virgin Islands", "Puerto Rico", "Rhode Island", "New Hampshire",
        "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota",
        "South Carolina", "South Dakota", "West Virginia",
    ]:
        if before_s.startswith(s + " "):
            state = s
            break
    if not state:
        # Single-word state
        parts = before_s.split()
        if len(parts) >= 3:
            state = parts[0]
        else:
            return None
    name = before_s[len(state) :].strip()
    if not name:
        return None
    # Parse city and school from rest
    tokens = rest.split()
    city = ""
    school = ""
    if len(tokens) >= 2:
        # Check for 2-word city (must be in COMPOUND_CITIES)
        two_word = " ".join(tokens[:2])
        if two_word in COMPOUND_CITIES:
            city = two_word
            school = " ".join(tokens[2:])
        else:
            city = tokens[0]
            school = " ".join(tokens[1:])
    elif len(tokens) == 1:
        city = tokens[0]
        school = ""
    return (state, name, grade, city, school)


def normalize_name(name: str) -> str:
    """Normalize name for matching (lowercase, collapse spaces)."""
    return " ".join(name.lower().split())


def main():
    # Load existing students
    name_to_id: dict[str, int] = {}
    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = int(row["student_id"])
            name_to_id[normalize_name(row["student_name"])] = sid
            if row.get("alias"):
                name_to_id[normalize_name(row["alias"])] = sid

    # Parse PDF lines and collect competitors
    competitors = []
    new_students: list[tuple[str, str]] = []  # (student_name, state)
    next_id = max(name_to_id.values()) + 1 if name_to_id else 1

    for line in PDF_LINES:
        parsed = parse_line(line)
        if not parsed:
            continue
        state, student_name, grade, city, school = parsed
        norm = normalize_name(student_name)
        if norm in name_to_id:
            student_id = name_to_id[norm]
        else:
            student_id = next_id
            next_id += 1
            new_students.append((student_name, state))
            name_to_id[norm] = student_id

        competitors.append({
            "student_id": student_id,
            "state": state,
            "student_name": student_name,
            "grade": grade,
            "city": city,
            "school": school,
        })

    # Create year=2019 directory
    COMPETITORS_DIR.mkdir(parents=True, exist_ok=True)

    # Write competitors.csv
    competitors_path = COMPETITORS_DIR / "competitors.csv"
    with open(competitors_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["student_id", "state", "student_name", "grade", "city", "school"],
        )
        writer.writeheader()
        writer.writerows(competitors)

    print(f"Wrote {competitors_path} with {len(competitors)} competitors")

    # Append new students to students.csv
    if new_students:
        with open(STUDENTS_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for student_name, state in new_students:
                writer.writerow([name_to_id[normalize_name(student_name)], student_name, state, "", "", ""])
        print(f"Added {len(new_students)} new students to {STUDENTS_CSV}")
        for name, state in new_students:
            print(f"  + {name} ({state})")
    else:
        print("All competitors already existed in students.csv")


if __name__ == "__main__":
    main()
