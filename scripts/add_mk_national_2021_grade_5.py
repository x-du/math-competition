#!/usr/bin/env python3
"""
Add Math Kangaroo 2021 Grade 5 National Winners.
Source: https://mathkangaroo.org/mks/wp-content/uploads/2021/08/2021_Level-5_National-Winners.pdf
Resolves (name, state) via students.csv; adds new students as needed.
If student_id exists with missing state, fills state from MK data.
Do NOT merge students with same name in different states - match strictly on (name, state).
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2021" / "grade=5"

STATE_ABBREV_TO_FULL = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut",
    "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida",
    "GA": "Georgia", "GU": "Guam", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
    "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
    "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
    "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}

# grade, name, score, rank, state (from 2021 Level 5 National Winners PDF)
# Excluded: Nikita Nazarov, Alikhan Nurlybay (Eastern Province, S. A. - Saudi Arabia)
ROWS = [
    (5, "Alicia Fei", 120, 1, "CA"),
    (5, "Anandita Mukherjee", 120, 1, "CA"),
    (5, "Junwon Jahng", 120, 1, "CA"),
    (5, "Oscar Varodayan", 120, 1, "CA"),
    (5, "Vihaan Gupta", 120, 1, "CA"),
    (5, "William Sun", 120, 1, "CA"),
    (5, "Xiaoran Han", 120, 1, "CA"),
    (5, "Zion Qu", 120, 1, "CA"),
    (5, "Nicholas Tong", 120, 1, "CT"),
    (5, "Sheehan Banka", 120, 1, "GA"),
    (5, "Christopher Sakaliyski", 120, 1, "IL"),
    (5, "Julia Shtiliyanova", 120, 1, "MA"),
    (5, "Rajarshi Mandal", 120, 1, "MA"),
    (5, "Ryan Li", 120, 1, "MA"),
    (5, "Selena Ge", 120, 1, "MA"),
    (5, "Eric Ding", 120, 1, "MN"),
    (5, "Victor Li", 120, 1, "MO"),
    (5, "Leeoz Nebat", 120, 1, "NV"),
    (5, "Ethan Greenblatt", 120, 1, "NY"),
    (5, "Thomas Wu", 120, 1, "TX"),
    (5, "Erin Bian", 120, 1, "WA"),
    (5, "Shuyin Liu", 120, 1, "WA"),
    (5, "Ashleen Pathri", 117, 2, "CA"),
    (5, "Itai Firstenberg", 117, 2, "CA"),
    (5, "Jaden Huang", 117, 2, "MA"),
    (5, "Jacob Levinshteyn", 117, 2, "MN"),
    (5, "Rohan Musti", 116, 3, "AZ"),
    (5, "Aiden Lee", 116, 3, "CA"),
    (5, "Tanish Parida", 116, 3, "MA"),
    (5, "Andrew Li", 116, 3, "MO"),
    (5, "Abhiraj Sarkar", 115, 4, "AL"),
    (5, "Adeline Chen", 115, 4, "CA"),
    (5, "Ayaan Aggarwal", 115, 4, "CA"),
    (5, "Isabella Wu", 115, 4, "CA"),
    (5, "Matthew Lau", 115, 4, "CA"),
    (5, "Minghao Guo", 115, 4, "CA"),
    (5, "Petey Bunsongsikul", 115, 4, "CA"),
    (5, "Rohan Nayak Mallick", 115, 4, "CA"),
    (5, "Tejo Madhavarapu", 115, 4, "CA"),
    (5, "Vishnudev Hari", 115, 4, "CA"),
    (5, "William Lv", 115, 4, "CA"),
    (5, "Ruichen Han", 115, 4, "IN"),
    (5, "Hanna Zamana", 115, 4, "KY"),
    (5, "Roger Gao", 115, 4, "MA"),
    (5, "Vidyut Kartik", 115, 4, "MA"),
    (5, "Arda Eroz", 115, 4, "MD"),
    (5, "Vihan Netra", 115, 4, "MD"),
    (5, "Hillel Ziskind", 115, 4, "NJ"),
    (5, "Rebecca Jihyo Kim", 115, 4, "NJ"),
    (5, "Siddharth Mirchandani", 115, 4, "NJ"),
    (5, "Aviyan Panday", 115, 4, "NY"),
    (5, "Evander Protopapas", 115, 4, "NY"),
    (5, "Michael Shakhnovich", 115, 4, "NY"),
    (5, "Yunong Wu", 115, 4, "NY"),
    (5, "Evgenii Matros", 115, 4, "PA"),
    (5, "Bryan Kuang", 115, 4, "TX"),
    (5, "Lauren Chen", 115, 4, "TX"),
    (5, "Yikai Wang", 115, 4, "VA"),
    (5, "Ella Qiu", 115, 4, "WA"),
    (5, "Iveta Zhovtobriukh", 115, 4, "WA"),
    (5, "Olivia Wang", 115, 4, "WA"),
    (5, "Xinyue Liu", 115, 4, "WA"),
    (5, "Katherine Su", 114, 5, "TX"),
    (5, "Brett Chang", 113, 6, "CA"),
    (5, "Lylia Zheng", 113, 6, "CA"),
    (5, "Advait Ajay", 113, 6, "OR"),
    (5, "Aarav Mann", 112, 7, "CA"),
    (5, "Adyant Bhavsar", 112, 7, "CA"),
    (5, "Gareth Lee", 112, 7, "CA"),
    (5, "Uday Shankar", 112, 7, "CA"),
    (5, "Satya Kokonda", 112, 7, "DE"),
    (5, "Grant Liu", 112, 7, "IL"),
    (5, "Alexander Gao", 112, 7, "IN"),
    (5, "Anika Malyavanatham", 112, 7, "OR"),
    (5, "Timothy Wu", 112, 7, "WA"),
    (5, "Anish Varada", 111, 8, "CA"),
    (5, "Atticus Stewart", 111, 8, "CA"),
    (5, "Michael Tang", 111, 8, "CA"),
    (5, "Olivia Zhu", 111, 8, "CA"),
    (5, "Sohum Vajaria", 111, 8, "CA"),
    (5, "Girish Prasad", 111, 8, "CT"),
    (5, "Trisha Dutta", 111, 8, "MA"),
    (5, "Ayden Huang", 111, 8, "MO"),
    (5, "Rohit Barua", 111, 8, "NJ"),
    (5, "Siddarth Sankar", 111, 8, "PA"),
    (5, "Alakh Gajjar", 111, 8, "TX"),
    (5, "Anvita Gandhari", 111, 8, "VA"),
    (5, "Violet Yan", 111, 8, "VA"),
    (5, "Yixuan Wang", 111, 8, "VA"),
    (5, "Anshul Arul", 111, 8, "WA"),
    (5, "Eva Akulova", 111, 8, "WA"),
    (5, "Gordon Bu", 111, 8, "WA"),
    (5, "Pia Gupta", 111, 8, "WA"),
    (5, "William Shan", 110, 9, "AZ"),
    (5, "Aidan Shin", 110, 9, "CA"),
    (5, "Alyssa Liu", 110, 9, "CA"),
    (5, "Bhuvi Tawari", 110, 9, "CA"),
    (5, "Brandon Lowenstein", 110, 9, "CA"),
    (5, "Daniel Farcas", 110, 9, "CA"),
    (5, "Ishaan Mittal", 110, 9, "CA"),
    (5, "Luca Busracamwongs", 110, 9, "CA"),
    (5, "Markel Zeng", 110, 9, "CA"),
    (5, "Matthew Wang", 110, 9, "CA"),
    (5, "Michael Jin", 110, 9, "CA"),
    (5, "Raman Ravikumar", 110, 9, "CA"),
    (5, "Yifan Liu", 110, 9, "CA"),
    (5, "Zhengyin Zhu", 110, 9, "CA"),
    (5, "Hayden Hughes", 110, 9, "CT"),
    (5, "Charles Parslow", 110, 9, "IL"),
    (5, "Jovin Alenghat", 110, 9, "IL"),
    (5, "Ziang Zhuang", 110, 9, "LA"),
    (5, "Ayaka Hatabu", 110, 9, "MA"),
    (5, "Diya Koul", 110, 9, "MA"),
    (5, "Ian Liu", 110, 9, "MA"),
    (5, "Ian Wang", 110, 9, "MA"),
    (5, "Vivek Varanasi", 110, 9, "MA"),
    (5, "William Wu", 110, 9, "MA"),
    (5, "Matthew Zhang", 110, 9, "MD"),
    (5, "Ethan Liu", 110, 9, "MI"),
    (5, "Anirudh Pulugurtha", 110, 9, "NH"),
    (5, "David Rivilis", 110, 9, "NH"),
    (5, "Aarav Kumar", 110, 9, "NJ"),
    (5, "Shiraz Naser", 110, 9, "NJ"),
    (5, "Kai Tsuboyama", 110, 9, "NY"),
    (5, "Ryan Chen", 110, 9, "NY"),
    (5, "Claire Ding", 110, 9, "PA"),
    (5, "Harry Liu", 110, 9, "TX"),
    (5, "Stephan Lugovoy", 110, 9, "VA"),
    (5, "Antony Missine", 110, 9, "WA"),
    (5, "Anusha Arora", 110, 9, "WA"),
    (5, "Keane Qu", 110, 9, "WA"),
    (5, "Ruien Chen", 110, 9, "WA"),
    (5, "Xiaoyan Yan", 110, 9, "WA"),
    (5, "Elliot Seo", 109, 10, "CA"),
    (5, "JiaJing Liang", 109, 10, "CA"),
    (5, "Srinithi Peripydi", 109, 10, "CA"),
    (5, "Leo Hong", 109, 10, "NC"),
    (5, "Aditya Mondal", 108, 11, "CA"),
    (5, "Ronak Bose", 108, 11, "CA"),
    (5, "Sean Huang", 108, 11, "CA"),
    (5, "Sophia Fan", 108, 11, "CA"),
    (5, "Vibha Santhanakrishnan", 108, 11, "CA"),
    (5, "Evan Li", 108, 11, "GA"),
    (5, "Grady Schroeder", 108, 11, "IL"),
    (5, "Gabriel Panaitescu", 108, 11, "MA"),
    (5, "Michelle Zheng", 108, 11, "MA"),
    (5, "Stephen Wang", 108, 11, "MA"),
    (5, "Reyansh Khubani", 108, 11, "NJ"),
    (5, "Harshvardhan Bhangale", 108, 11, "OH"),
    (5, "Eddy Zhang", 108, 11, "PA"),
    (5, "Prajit Saravanan", 108, 11, "TX"),
    (5, "Aayush Gupta", 108, 11, "WA"),
    (5, "Jason Tae", 107, 12, "AZ"),
    (5, "Aarav Vignesh", 107, 12, "CA"),
    (5, "Andersen Edmonds", 107, 12, "CA"),
    (5, "Boyan Manolov", 107, 12, "CA"),
    (5, "Jason Yang", 107, 12, "CA"),
    (5, "Kevin Li", 107, 12, "CA"),
    (5, "Kevin Mathew", 107, 12, "CA"),
    (5, "Konstantin Edunov", 107, 12, "CA"),
    (5, "Lucas Chen", 107, 12, "CA"),
    (5, "Maksim Begar", 107, 12, "CA"),
    (5, "Nathan Chen", 107, 12, "CA"),
    (5, "Vedant Maheshwari", 107, 12, "CA"),
    (5, "Waroon Thapanangkun", 107, 12, "CA"),
    (5, "David Lei", 107, 12, "CT"),
    (5, "Jason Eum", 107, 12, "DE"),
    (5, "Antony Wang", 107, 12, "GA"),
    (5, "Jakub Angelow", 107, 12, "IL"),
    (5, "Adelle Freink", 107, 12, "MA"),
    (5, "Isaac Goodman", 107, 12, "MA"),
    (5, "Priyam Ajwaliya", 107, 12, "MA"),
    (5, "Samuel Minow", 107, 12, "MA"),
    (5, "Yuecheng Wu", 107, 12, "MA"),
    (5, "Walter Isard", 107, 12, "NC"),
    (5, "David Yu", 107, 12, "NJ"),
    (5, "Olivia Markesic", 107, 12, "NY"),
    (5, "Joseph Liang", 107, 12, "OR"),
    (5, "Jerry Huang", 107, 12, "PA"),
    (5, "Pranay Gudladona", 107, 12, "TX"),
    (5, "Richard Zhang", 107, 12, "TX"),
    (5, "Ekansh Arora", 107, 12, "VA"),
    (5, "Nathan Park", 107, 12, "VA"),
    (5, "Junheng Wang", 107, 12, "WA"),
    (5, "Kuan Dai", 107, 12, "WA"),
    (5, "Alec Timothy Nudo", 106, 13, "CA"),
    (5, "Arnav Gokhale", 106, 13, "CA"),
    (5, "Bryan Ge", 106, 13, "CA"),
    (5, "Douglas Nottage", 106, 13, "CA"),
    (5, "Emily Qian", 106, 13, "CA"),
    (5, "Felix Zhang", 106, 13, "CA"),
    (5, "Karina Quach", 106, 13, "CA"),
    (5, "Max Zhang", 106, 13, "CA"),
    (5, "Michelle Li", 106, 13, "CA"),
    (5, "Nikhil Sangani", 106, 13, "CA"),
    (5, "Niyati Ramanathan", 106, 13, "CA"),
    (5, "Sophie Sun", 106, 13, "CA"),
    (5, "Vanshikaa Anand", 106, 13, "CA"),
    (5, "Warren Zhong", 106, 13, "CA"),
    (5, "Yanlin Huang", 106, 13, "CA"),
    (5, "Pavan Kapoor", 106, 13, "CT"),
    (5, "Jiaxi Ji", 106, 13, "IL"),
    (5, "Daniel Ramakrishna", 106, 13, "MA"),
    (5, "Elif Uygun", 106, 13, "MA"),
    (5, "Krish Nath", 106, 13, "MA"),
    (5, "Tashan Behara", 106, 13, "MA"),
    (5, "Anabelle Krom-Hernandez", 106, 13, "NJ"),
    (5, "Bobby Qian", 106, 13, "NJ"),
    (5, "Vaibhav Sitaraman", 106, 13, "NJ"),
    (5, "Brighten Sun", 106, 13, "NY"),
    (5, "Shiva Marti", 106, 13, "NY"),
    (5, "Hudson Fong", 106, 13, "OK"),
    (5, "Audrey Hou", 106, 13, "OR"),
    (5, "John Kong", 106, 13, "OR"),
    (5, "Michael Moshchuk", 106, 13, "WA"),
    (5, "Natalie Gan", 106, 13, "WA"),
    (5, "Aaron Anghel", 105, 14, "CA"),
    (5, "Andrea Wang", 105, 14, "CA"),
    (5, "Dylan Huang", 105, 14, "CA"),
    (5, "Eva Lin", 105, 14, "CA"),
    (5, "Hanyu Zhang", 105, 14, "CA"),
    (5, "Netra Khot", 105, 14, "CA"),
    (5, "Peter Parra", 105, 14, "CA"),
    (5, "Vyom Saxena", 105, 14, "CA"),
    (5, "Henry Buczkiewicz", 105, 14, "CT"),
    (5, "Evan Yang", 105, 14, "FL"),
    (5, "Kaustubh Bukkapatnam", 105, 14, "IL"),
    (5, "YuHan ChenHe", 105, 14, "IL"),
    (5, "Zimou Z", 105, 14, "IL"),
    (5, "Haniya Hussain", 105, 14, "MA"),
    (5, "Khwaja Hussain", 105, 14, "MA"),
    (5, "Aryaveer Shishodia", 105, 14, "NJ"),
    (5, "Emre Dogan", 105, 14, "NJ"),
    (5, "Surya Raghavan", 105, 14, "NJ"),
    (5, "Vishnu Srikant", 105, 14, "NJ"),
    (5, "Athena Grinsai", 105, 14, "NY"),
    (5, "Julien Okenczyc", 105, 14, "PA"),
    (5, "Andrew Lu", 105, 14, "TX"),
    (5, "Gaya Kulatilaka", 105, 14, "TX"),
    (5, "Mikaela Tereshkov", 105, 14, "VA"),
    (5, "Daniel Shendure", 105, 14, "WA"),
    (5, "Ella Sun", 105, 14, "WA"),
    (5, "Manan Ghosh", 105, 14, "WA"),
    (5, "Yan Levin", 105, 14, "WA"),
    (5, "Ali Zaman", 104, 15, "CA"),
    (5, "Arpit Panda", 104, 15, "CA"),
    (5, "Henry Deng", 104, 15, "CA"),
    (5, "Sidhvin Palaniappan", 104, 15, "CA"),
    (5, "Yeojoon Yoon", 104, 15, "MA"),
    (5, "Asya Chen", 104, 15, "TX"),
    (5, "Siddharth Surapaneni", 104, 15, "VA"),
    (5, "Leonardo Zhou", 104, 15, "WA"),
    (5, "Wesley Wu", 104, 15, "WA"),
    (5, "Alivia Cui", 103, 16, "CA"),
    (5, "Aria Sanil", 103, 16, "CA"),
    (5, "Daniel Wang", 103, 16, "CA"),
    (5, "Ishita Gaikwad", 103, 16, "CA"),
    (5, "Jinxian Cao", 103, 16, "CA"),
    (5, "Jonathan Yu", 103, 16, "CA"),
    (5, "Joseph Baek", 103, 16, "CA"),
    (5, "Steven Shu", 103, 16, "CA"),
    (5, "Sudhir Venkatraman", 103, 16, "CA"),
    (5, "Tanisha Bhugra", 103, 16, "CA"),
    (5, "Jacob Weng", 103, 16, "GA"),
    (5, "Thanishkka Vijayabaskar", 103, 16, "GA"),
    (5, "Ananya Iyer", 103, 16, "IL"),
    (5, "Ethan Li", 103, 16, "MA"),
    (5, "Jeffrey Yin", 103, 16, "MA"),
    (5, "Ruben Lee", 103, 16, "MA"),
    (5, "Taiwen Feng", 103, 16, "MI"),
    (5, "Nikit Chitteti", 103, 16, "NJ"),
    (5, "Aneesh Jakkamsetti", 103, 16, "NY"),
    (5, "Dheeraj Garg", 103, 16, "PA"),
    (5, "Surya Charan Garimella", 103, 16, "PA"),
    (5, "Dayana Veys", 103, 16, "WA"),
    (5, "Kairui Dai", 102, 17, "AZ"),
    (5, "Aangi Mehta", 102, 17, "CA"),
    (5, "Alvin Siamwalla", 102, 17, "CA"),
    (5, "Andrew Eroshin", 102, 17, "CA"),
    (5, "Annie Jin", 102, 17, "CA"),
    (5, "Clara Lee", 102, 17, "CA"),
    (5, "Eli Chen", 102, 17, "CA"),
    (5, "Ethan Ge", 102, 17, "CA"),
    (5, "Julia Matveyev", 102, 17, "CA"),
    (5, "Leonardo Lin", 102, 17, "CA"),
    (5, "Lucas Della Vigna", 102, 17, "CA"),
    (5, "Matea Gebala", 102, 17, "CA"),
    (5, "Ojasya Machiraju", 102, 17, "CA"),
    (5, "Ryan Lu", 102, 17, "CA"),
    (5, "Sameer Rajdev", 102, 17, "CA"),
    (5, "Vishakha Shastri", 102, 17, "CA"),
    (5, "Arnav Patel", 102, 17, "GA"),
    (5, "Sanjay Magesh", 102, 17, "IL"),
    (5, "Tiger Kumar", 102, 17, "IN"),
    (5, "Arnav Sreeram", 102, 17, "MA"),
    (5, "Gauri Bhakta", 102, 17, "MA"),
    (5, "Justina Sun", 102, 17, "MA"),
    (5, "Mia Zhao", 102, 17, "MA"),
    (5, "Shubham Kulkarni", 102, 17, "MA"),
    (5, "Jeffrey Wu", 102, 17, "MI"),
    (5, "Alen Sahakyan", 102, 17, "MO"),
    (5, "Daniel Mun", 102, 17, "NY"),
    (5, "Jonathan Safro", 102, 17, "SC"),
    (5, "Kangjue Wang", 102, 17, "TX"),
    (5, "Shaarda Krishna", 102, 17, "TX"),
    (5, "Alexander Liu", 102, 17, "VA"),
    (5, "Aiyin Gou", 102, 17, "WA"),
    (5, "Olivia Sun", 102, 17, "WA"),
    (5, "Siddhant Lodha", 102, 17, "WA"),
    (5, "Stephan Yang", 102, 17, "WA"),
    (5, "Alex Shi", 101, 18, "CA"),
    (5, "Alexander Shi", 101, 18, "CA"),
    (5, "Amy Chen", 101, 18, "CA"),
    (5, "Andrew Ho", 101, 18, "CA"),
    (5, "Dennis Bi", 101, 18, "CA"),
    (5, "Elaine Saum", 101, 18, "CA"),
    (5, "Elaine Wen", 101, 18, "CA"),
    (5, "Emma Wang", 101, 18, "CA"),
    (5, "Hongkang Zhao", 101, 18, "CA"),
    (5, "Jaeho Lee", 101, 18, "CA"),
    (5, "Jeremy Lee", 101, 18, "CA"),
    (5, "Kerim Lahmar", 101, 18, "CA"),
    (5, "Kevin Yang", 101, 18, "CA"),
    (5, "Luke Tang", 101, 18, "CA"),
    (5, "Natalie Dong", 101, 18, "CA"),
    (5, "Rohan Singh", 101, 18, "CA"),
    (5, "Shravan Sundar", 101, 18, "CA"),
    (5, "Maadhav Subramanian", 101, 18, "CT"),
    (5, "Olivia Wang", 101, 18, "CT"),
    (5, "Shiven Brahmkshatriya", 101, 18, "CT"),
    (5, "Megha Sandrapaty", 101, 18, "FL"),
    (5, "YoYo Qu", 101, 18, "FL"),
    (5, "Debarghya Das", 101, 18, "IL"),
    (5, "Michael Chen", 101, 18, "IL"),
    (5, "Tanisha Lalwani", 101, 18, "IL"),
    (5, "David Wang", 101, 18, "MA"),
    (5, "Shaurya Bedre", 101, 18, "MA"),
    (5, "Shreyan Mazumder", 101, 18, "MA"),
    (5, "Jolee Xian", 101, 18, "MD"),
    (5, "Aditya Joshi", 101, 18, "NY"),
    (5, "Christoffer Lamtan", 101, 18, "NY"),
    (5, "Ethan Ding", 101, 18, "NY"),
    (5, "Frederik Bultje", 101, 18, "NY"),
    (5, "Justin Koo", 101, 18, "NY"),
    (5, "Vivienne Ding", 101, 18, "NY"),
    (5, "Yuxuan Jiang", 101, 18, "OR"),
    (5, "Allison Guan", 101, 18, "PA"),
    (5, "Derek Su", 101, 18, "PA"),
    (5, "Yuantao Tang", 101, 18, "PA"),
    (5, "Tanish Shetty", 101, 18, "UT"),
    (5, "Ajay Balusu", 101, 18, "VA"),
    (5, "Mayukh Krishna Aduru", 101, 18, "VA"),
    (5, "Michelle Lin", 101, 18, "VA"),
    (5, "Andrew Chen", 101, 18, "WA"),
    (5, "Kevin Wu", 101, 18, "WA"),
    (5, "William Han", 101, 18, "WA"),
    (5, "Vivian Pinto", 100, 19, "AZ"),
    (5, "Aaron Lei", 100, 19, "CA"),
    (5, "Aaryan Samanta", 100, 19, "CA"),
    (5, "Alice Shao", 100, 19, "CA"),
    (5, "Angela Wang", 100, 19, "CA"),
    (5, "Armaan Syed", 100, 19, "CA"),
    (5, "Charlene Li", 100, 19, "CA"),
    (5, "Claire Mao", 100, 19, "CA"),
    (5, "Crystal Gu", 100, 19, "CA"),
    (5, "Jeffery Wang", 100, 19, "CA"),
    (5, "Jessica Jin", 100, 19, "CA"),
    (5, "Jonathan Li", 100, 19, "CA"),
    (5, "Katherine Yang", 100, 19, "CA"),
    (5, "Katie Xie", 100, 19, "CA"),
    (5, "Liesel Park", 100, 19, "CA"),
    (5, "Sebastian Liang", 100, 19, "CA"),
    (5, "Arya Ravikumar", 100, 19, "IA"),
    (5, "Alexandra Ryskin", 100, 19, "IL"),
    (5, "Edward Jiang", 100, 19, "IL"),
    (5, "Melanie Ma", 100, 19, "IL"),
    (5, "Emma Wei", 100, 19, "IN"),
    (5, "Kiran Oliver", 100, 19, "MD"),
    (5, "Chandhana Lingam Muhilan", 100, 19, "NJ"),
    (5, "Jianing Liu", 100, 19, "NJ"),
    (5, "Pranav Naveen", 100, 19, "NJ"),
    (5, "Esther Lee", 100, 19, "NY"),
    (5, "Isha Patil", 100, 19, "NY"),
    (5, "Konstantine Okon", 100, 19, "NY"),
    (5, "Max Chang", 100, 19, "NY"),
    (5, "Keerthana Visveish", 100, 19, "PA"),
    (5, "Sophia Wang", 100, 19, "TX"),
    (5, "Jacob Lu", 100, 19, "WA"),
    (5, "Owen T Zhang", 100, 19, "WA"),
    (5, "Shujun Liu", 100, 19, "WA"),
    (5, "Sophy Xu", 100, 19, "WA"),
    (5, "Videep Mannava", 100, 19, "WA"),
    (5, "Aarav Agarwal", 99, 20, "CA"),
    (5, "Angela Baykshtite", 99, 20, "CA"),
    (5, "Arohi Sharma", 99, 20, "CA"),
    (5, "Boyan Han", 99, 20, "CA"),
    (5, "Christopher Jiang", 99, 20, "CA"),
    (5, "Ella Wang", 99, 20, "CA"),
    (5, "Hank Sun", 99, 20, "CA"),
    (5, "Hyunhoo Bae", 99, 20, "CA"),
    (5, "Isato Otaki", 99, 20, "CA"),
    (5, "Lucas Lee", 99, 20, "CA"),
    (5, "Rishika Nanda", 99, 20, "CA"),
    (5, "Ryan Li", 99, 20, "CA"),
    (5, "Sruthi Manoj", 99, 20, "CA"),
    (5, "Vyom Shukla", 99, 20, "CA"),
    (5, "Ishaani Molugu", 99, 20, "FL"),
    (5, "Baruni Soni", 99, 20, "IL"),
    (5, "Eric Liu", 99, 20, "MA"),
    (5, "Leila Alencar", 99, 20, "MA"),
    (5, "Lucas Shang", 99, 20, "MA"),
    (5, "Vivan Netra", 99, 20, "MD"),
    (5, "Vihaan Limaye", 99, 20, "MI"),
    (5, "Megan Wang", 99, 20, "MN"),
    (5, "Vinay Parekunnel", 99, 20, "MO"),
    (5, "Daniel Dimitrov", 99, 20, "NC"),
    (5, "Ashwin Kannan", 99, 20, "NJ"),
    (5, "Anna Vasylenko", 99, 20, "NY"),
    (5, "Daniel Obreja", 99, 20, "WA"),
    (5, "Jaeyeol Oh", 99, 20, "WA"),
    (5, "Jinghang Chen", 99, 20, "WA"),
]


def load_students():
    key_to_row = {}
    name_to_blank_state_rows = {}
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
                if not state:
                    nl = name.lower()
                    if nl not in name_to_blank_state_rows:
                        name_to_blank_state_rows[nl] = []
                    name_to_blank_state_rows[nl].append(r)
            for a in (row.get("alias") or "").split("|"):
                a = a.strip()
                if a:
                    key = (a.lower(), state)
                    if key not in key_to_row:
                        key_to_row[key] = r
    return key_to_row, name_to_blank_state_rows, next_id


def main():
    key_to_row, name_to_blank_state_rows, next_id = load_students()
    new_students = []
    out_rows = []
    state_updates = {}

    for grade, name, score, rank, state_abbrev in ROWS:
        state = STATE_ABBREV_TO_FULL.get(state_abbrev.strip().upper(), state_abbrev.strip())
        name_clean = name.strip()
        key = (name_clean.lower(), state)
        row = key_to_row.get(key)
        if row:
            out_rows.append((row["student_id"], row["student_name"], state, grade, score, rank, ""))
            continue

        blank_rows = name_to_blank_state_rows.get(name_clean.lower(), [])
        if len(blank_rows) == 1:
            row = blank_rows[0]
            state_updates[row["student_id"]] = state
            key_to_row[key] = row
            row["state"] = state
            out_rows.append((row["student_id"], row["student_name"], state, grade, score, rank, ""))
            continue

        sid = next_id
        next_id += 1
        key_to_row[key] = {"student_id": sid, "student_name": name_clean, "state": state}
        new_students.append({
            "student_id": sid, "student_name": name_clean, "state": state,
            "team_ids": "", "alias": "", "gender": "", "grade_in_2026": ""
        })
        out_rows.append((sid, name_clean, state, grade, score, rank, ""))

    if new_students:
        with open(STUDENTS_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["student_id", "student_name", "state", "team_ids", "alias", "gender", "grade_in_2026"], extrasaction="ignore")
            for r in new_students:
                w.writerow(r)
        print(f"Added {len(new_students)} new students")

    if state_updates:
        with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = list(reader.fieldnames or [])
        for row in rows:
            sid_s = (row.get("student_id") or "").strip()
            try:
                sid = int(sid_s)
            except ValueError:
                continue
            if sid in state_updates:
                row["state"] = state_updates[sid]
        tmp_path = STUDENTS_CSV.with_suffix(".csv.tmp")
        with tmp_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        tmp_path.replace(STUDENTS_CSV)
        print(f"Filled missing state for {len(state_updates)} students: {state_updates}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "results.csv"
    rank_counts = {}
    for _, _, _, _, _, r, _ in out_rows:
        rank_counts[r] = rank_counts.get(r, 0) + 1
    rank_to_mcp = {}
    r = 1
    for rank_val in sorted(rank_counts.keys()):
        n = rank_counts[rank_val]
        rank_to_mcp[rank_val] = (r + r + n - 1) / 2
        r += n

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["student_id", "student_name", "state", "grade", "score", "rank", "national_percentile", "mcp_rank"])
        for sid, name, state, grade, score, rank, pct in out_rows:
            w.writerow([sid, name, state, grade, score, rank, pct, rank_to_mcp[rank]])
    print(f"Wrote {out_path} ({len(out_rows)} rows)")


if __name__ == "__main__":
    main()
