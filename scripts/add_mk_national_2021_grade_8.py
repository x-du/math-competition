#!/usr/bin/env python3
"""
Add Math Kangaroo 2021 Grade 8 National Winners.
Source: https://mathkangaroo.org/mks/wp-content/uploads/2021/08/2021_Level-8_National-Winners.pdf
Resolves (name, state) via students.csv; adds new students as needed.
If student_id exists with missing state, fills state from MK data.
Do NOT merge students with same name in different states - match strictly on (name, state).
Note: David Zhang appears twice - CA (rank 1) and UT (rank 3) - both are valid different people.
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
OUT_DIR = ROOT / "database" / "contests" / "mk-national" / "year=2021" / "grade=8"

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

# grade, name, score, rank, state (from 2021 Level 8 National Winners PDF)
ROWS = [
    (8, "Agniv Sarkar", 120, 1, "CA"),
    (8, "David Deutsch", 120, 1, "CA"),
    (8, "David Zhang", 120, 1, "CA"),
    (8, "Kylar Cheng", 120, 1, "CA"),
    (8, "Qiao Zhang", 120, 1, "CA"),
    (8, "Samuel Ren", 120, 1, "CA"),
    (8, "Sanya Badhe", 120, 1, "CA"),
    (8, "William Chen", 120, 1, "CA"),
    (8, "Ethan Morgan", 120, 1, "GA"),
    (8, "Nikolay Silkin", 120, 1, "IA"),
    (8, "Jefferson Ji", 120, 1, "MA"),
    (8, "Rohith Raghavan", 120, 1, "MA"),
    (8, "Isaac Nobles", 120, 1, "NC"),
    (8, "Andrew Brahms", 120, 1, "NJ"),
    (8, "Daniel Gilman", 120, 1, "NJ"),
    (8, "Kevin Yao", 120, 1, "PA"),
    (8, "Ankur Dabholkar", 120, 1, "TX"),
    (8, "Gregory Roudenko", 120, 1, "VA"),
    (8, "Thomas Zheleznyak", 120, 1, "VA"),
    (8, "Victoria Rusaeva", 120, 1, "VA"),
    (8, "Vrishak Vemuri", 120, 1, "VA"),
    (8, "Joyce Huang", 120, 1, "WA"),
    (8, "Aarav Mehta", 116, 2, "CT"),
    (8, "Likhitha Selvan", 116, 2, "FL"),
    (8, "Katelyn Lu", 116, 2, "MI"),
    (8, "Akilan Paramasivam", 115, 3, "CA"),
    (8, "Anjena Raja", 115, 3, "CA"),
    (8, "Ayetra Sarkar", 115, 3, "CA"),
    (8, "Brianna Zheng", 115, 3, "CA"),
    (8, "Howard Liu", 115, 3, "CA"),
    (8, "Hugh Cheng", 115, 3, "CA"),
    (8, "Ishani Agarwal", 115, 3, "CA"),
    (8, "Kirby Fung", 115, 3, "CA"),
    (8, "Kyra Cui", 115, 3, "CA"),
    (8, "Leo Lhert", 115, 3, "CA"),
    (8, "Ritwin Narra", 115, 3, "CA"),
    (8, "Rohin Garg", 115, 3, "CA"),
    (8, "Sarthak Jain", 115, 3, "CA"),
    (8, "Yufei Chen", 115, 3, "CA"),
    (8, "Abhinav Krishna", 115, 3, "CO"),
    (8, "Eric Jin", 115, 3, "IN"),
    (8, "Bhuvan Sanga", 115, 3, "KY"),
    (8, "Aaron Huang", 115, 3, "MA"),
    (8, "Egor Lazarevich", 115, 3, "MA"),
    (8, "Ryon Das", 115, 3, "MA"),
    (8, "Thomas Xue", 115, 3, "MA"),
    (8, "Bryan Yung", 115, 3, "MD"),
    (8, "Shreyan Paliwal", 115, 3, "OR"),
    (8, "Ken Yoshida", 115, 3, "PA"),
    (8, "Ryan Wu", 115, 3, "PA"),
    (8, "Ellen Li", 115, 3, "TX"),
    (8, "David Zhang", 115, 3, "UT"),
    (8, "Eric Shen", 115, 3, "VA"),
    (8, "Ken Zhou", 115, 3, "VA"),
    (8, "Minh Nguyen", 115, 3, "VA"),
    (8, "Ray Zhang", 115, 3, "VA"),
    (8, "Rockwell Li", 115, 3, "VA"),
    (8, "Christopher Dickman", 115, 3, "WA"),
    (8, "Ethan Do", 115, 3, "WA"),
    (8, "Ethan Li", 115, 3, "WA"),
    (8, "Levi Polsky", 115, 3, "WA"),
    (8, "Stanigost Abakumov", 115, 3, "WA"),
    (8, "Sidarth Erat", 113, 4, "CA"),
    (8, "Ananya Bezbaruah", 113, 4, "WA"),
    (8, "Anthony Dokanchi", 112, 5, "CA"),
    (8, "Janice Lee", 112, 5, "CA"),
    (8, "Jonah Cha", 112, 5, "CA"),
    (8, "Shreyas Ekanathan", 112, 5, "MA"),
    (8, "Suhas Beeravelli", 112, 5, "OH"),
    (8, "Samarth Bhargav", 112, 5, "VA"),
    (8, "Pranav Kannepalli", 112, 5, "WA"),
    (8, "Allison Hung", 111, 6, "CA"),
    (8, "Anish Dara", 111, 6, "CA"),
    (8, "Arya Kunisetty", 111, 6, "CA"),
    (8, "Eldrick Fan", 111, 6, "CA"),
    (8, "Katherine Kligys", 111, 6, "CA"),
    (8, "Saidivyesh Tunguturu", 111, 6, "CA"),
    (8, "Atticus Wei", 111, 6, "CO"),
    (8, "Saketh Maddali", 111, 6, "NJ"),
    (8, "Sounak Bagchi", 111, 6, "NJ"),
    (8, "Alexander Song", 111, 6, "NY"),
    (8, "Dylan Mihovski", 111, 6, "PA"),
    (8, "Smithi Gopalakrishnan", 111, 6, "TX"),
    (8, "Marina Lin", 111, 6, "VA"),
    (8, "Nikhil Kumar", 111, 6, "VA"),
    (8, "Patrick Du", 111, 6, "VA"),
    (8, "Ashwika Sharma", 111, 6, "WA"),
    (8, "Daniel Fanaru", 111, 6, "WA"),
    (8, "Iris Tang", 111, 6, "WA"),
    (8, "Ryuya Yonekura", 111, 6, "WA"),
    (8, "Anusha Sundar", 110, 7, "CA"),
    (8, "Ava Park", 110, 7, "CA"),
    (8, "Drishti Sethia", 110, 7, "CA"),
    (8, "Eric Xiao", 110, 7, "CA"),
    (8, "Neil Krishnan", 110, 7, "CA"),
    (8, "Rose Cohen", 110, 7, "CA"),
    (8, "Sanjay Ravishankar", 110, 7, "CA"),
    (8, "Saravanan Valliappan", 110, 7, "CA"),
    (8, "Siyona Dhingra", 110, 7, "CA"),
    (8, "Yao Chen", 110, 7, "CA"),
    (8, "Yufan Wang", 110, 7, "CA"),
    (8, "Alessandra Gavriloiu", 110, 7, "CT"),
    (8, "Alex Hart", 110, 7, "GA"),
    (8, "Anshul Gokul", 110, 7, "GA"),
    (8, "Varun Gala", 110, 7, "LA"),
    (8, "Ankita Varigonda", 110, 7, "MA"),
    (8, "Ben Nir", 110, 7, "MA"),
    (8, "Isha Nagireddy", 110, 7, "MA"),
    (8, "Sampath Kalagarla", 110, 7, "MA"),
    (8, "Tzuriel Justin Yu", 110, 7, "MA"),
    (8, "Daniel Li", 110, 7, "MD"),
    (8, "Nikhita Bhatt", 110, 7, "MD"),
    (8, "Elizabeth Levinshteyn", 110, 7, "MN"),
    (8, "Kriti Nandakumar", 110, 7, "NC"),
    (8, "Agastya Batchu", 110, 7, "NJ"),
    (8, "Maxwell Gong", 110, 7, "NJ"),
    (8, "Rohan Ambastha", 110, 7, "NJ"),
    (8, "Suhas Kondapalli", 110, 7, "NJ"),
    (8, "Timothy Torubarov", 110, 7, "NJ"),
    (8, "Alexander Davi", 110, 7, "NV"),
    (8, "Celene Sahoo", 110, 7, "NY"),
    (8, "David Vaysman", 110, 7, "NY"),
    (8, "Ethan Zhang", 110, 7, "OR"),
    (8, "Alisa Bryantseva", 110, 7, "TN"),
    (8, "Audrey Perry", 110, 7, "TX"),
    (8, "Siyona Jain", 110, 7, "TX"),
    (8, "Westley Rae", 110, 7, "UT"),
    (8, "Yash Marpu", 110, 7, "VA"),
    (8, "Caleb Liu", 108, 8, "AZ"),
    (8, "Darren Su", 108, 8, "ID"),
    (8, "Aran Chakraborty", 108, 8, "MA"),
    (8, "Dashiel Lin", 108, 8, "NJ"),
    (8, "Travis Ferrin", 108, 8, "UT"),
    (8, "Rishabh Kumaran", 108, 8, "VA"),
    (8, "Michael Bower", 107, 9, "CA"),
    (8, "Daron Simmons", 107, 9, "FL"),
    (8, "Sai Palireddy", 107, 9, "GA"),
    (8, "Maksim Roman", 107, 9, "MA"),
    (8, "Owen Zhang", 107, 9, "MA"),
    (8, "Ranai Shah", 107, 9, "MA"),
    (8, "Samay Shah", 107, 9, "MA"),
    (8, "Vivek Mehta", 107, 9, "MA"),
    (8, "Elita You", 107, 9, "MI"),
    (8, "Pranav Shankar", 107, 9, "NJ"),
    (8, "Gil Yarsky", 107, 9, "NY"),
    (8, "Aidan Zhong", 107, 9, "OH"),
    (8, "Yejoon Ham", 107, 9, "TN"),
    (8, "Gabriel Xu", 107, 9, "VA"),
    (8, "Madhav Krishnaswamy", 107, 9, "VA"),
    (8, "Eva Jain", 107, 9, "WA"),
    (8, "Shrey Shah", 107, 9, "WA"),
    (8, "Anish Sarkar", 106, 10, "CA"),
    (8, "Isaac Chan", 106, 10, "CA"),
    (8, "Jonathan Ho", 106, 10, "CA"),
    (8, "Nandana Madhukara", 106, 10, "CA"),
    (8, "Satvik Sivaraman", 106, 10, "CA"),
    (8, "Tejas Ravi", 106, 10, "CA"),
    (8, "Joshua Lin", 106, 10, "IL"),
    (8, "Max Chen", 106, 10, "IL"),
    (8, "Derek Qi", 106, 10, "MA"),
    (8, "Govind Velamoor", 106, 10, "MA"),
    (8, "Lily Tjia", 106, 10, "MA"),
    (8, "Tianyi Zhou", 106, 10, "MA"),
    (8, "Ivan Zhang", 106, 10, "MD"),
    (8, "Kamila El Moselhy", 106, 10, "NY"),
    (8, "Lydia Martel", 106, 10, "NY"),
    (8, "Andrew Zhou", 106, 10, "OH"),
    (8, "Sarah Boros", 106, 10, "OH"),
    (8, "Ruideng Zhong", 106, 10, "SC"),
    (8, "Anton Chen", 106, 10, "VA"),
    (8, "Sophia Lin", 106, 10, "VA"),
    (8, "Maxim Liachenko", 105, 11, "AR"),
    (8, "Ethan Wei", 105, 11, "AZ"),
    (8, "Johnny Yu", 105, 11, "AZ"),
    (8, "Aiden Park", 105, 11, "CA"),
    (8, "Dhruv Jena", 105, 11, "CA"),
    (8, "Fateh Aliyev", 105, 11, "CA"),
    (8, "Isabelle Du", 105, 11, "CA"),
    (8, "Arnav Jain", 105, 11, "FL"),
    (8, "Nathanael Williams", 105, 11, "IL"),
    (8, "Saveer Jain", 105, 11, "KY"),
    (8, "Alexander Loo", 105, 11, "MA"),
    (8, "Armaan Priyadarshan", 105, 11, "MA"),
    (8, "Benjamin Zhu", 105, 11, "MA"),
    (8, "Julius Aarup Kulla", 105, 11, "MA"),
    (8, "Neil Nori", 105, 11, "MA"),
    (8, "Nikhil Sankaran", 105, 11, "MA"),
    (8, "Polina Kontorovich", 105, 11, "MA"),
    (8, "Sanjith Krishnan", 105, 11, "MA"),
    (8, "Vibhush Sivakumar", 105, 11, "MA"),
    (8, "Yuli Ziblat", 105, 11, "MA"),
    (8, "Azaria Hileman", 105, 11, "MD"),
    (8, "Shriyan Reyya", 105, 11, "MD"),
    (8, "Lokesh Satyasai Ramprasad Tammisetty", 105, 11, "MO"),
    (8, "Aidan Mascoli", 105, 11, "NJ"),
    (8, "Mahanth Komuravelli", 105, 11, "NJ"),
    (8, "Sreeram Sai Vuppala", 105, 11, "NJ"),
    (8, "Angela Zeng", 105, 11, "NY"),
    (8, "Simon Heiselt", 105, 11, "NY"),
    (8, "Harshita Ganga", 105, 11, "OH"),
    (8, "Tej Sampath", 105, 11, "OH"),
    (8, "Neel Jain", 105, 11, "TX"),
    (8, "Angela Zhan", 105, 11, "UT"),
    (8, "Anthony Du", 105, 11, "VA"),
    (8, "Mohith Ram Narendra Babu", 105, 11, "WA"),
    (8, "Nicholas Volfbeyn", 105, 11, "WA"),
    (8, "Isabella Hu", 104, 12, "MA"),
    (8, "Sargam Mondal", 104, 12, "NJ"),
    (8, "Anagh Gupta", 104, 12, "NY"),
    (8, "Emily Bolton", 104, 12, "WA"),
    (8, "Issac Hsiung", 103, 13, "CA"),
    (8, "Daniel Stoyanov", 103, 13, "CT"),
    (8, "Melita Dsouza", 103, 13, "FL"),
    (8, "Alexander Ung", 103, 13, "IL"),
    (8, "Haoming Zheng", 103, 13, "KY"),
    (8, "Shi Shen", 103, 13, "MI"),
    (8, "Anjan Yalamanchili", 103, 13, "NH"),
    (8, "Anastasia Lee", 103, 13, "NY"),
    (8, "David Lu", 103, 13, "VA"),
    (8, "Siddarth Kumar", 103, 13, "VA"),
    (8, "Mikhail Kolosov", 103, 13, "WA"),
    (8, "Robert Michailov", 103, 13, "WA"),
    (8, "Thiruchelvam Thirunavukkarasu", 103, 13, "WA"),
    (8, "Gabriel Dunu", 102, 14, "CA"),
    (8, "Max Ismagilov", 102, 14, "CA"),
    (8, "Nico Cruz", 102, 14, "CA"),
    (8, "Rishabh Prabhu", 102, 14, "CA"),
    (8, "Sophia Liao", 102, 14, "CA"),
    (8, "Steinunn Liorsdottir", 102, 14, "CA"),
    (8, "Haasini Yelugoti", 102, 14, "FL"),
    (8, "Parthapratim Biswas", 102, 14, "IL"),
    (8, "Aashritha Musti", 102, 14, "KS"),
    (8, "Sriram Srinivasa Kalki", 102, 14, "KS"),
    (8, "Anika Kale", 102, 14, "MA"),
    (8, "Bowen Peng", 102, 14, "MA"),
    (8, "Jagan Mranal", 102, 14, "MA"),
    (8, "Karn Chutinan", 102, 14, "MA"),
    (8, "Soham Shah", 102, 14, "MA"),
    (8, "Mrigank Malladi", 102, 14, "NC"),
    (8, "Sanjana Medapati", 102, 14, "NJ"),
    (8, "Hao Gu", 102, 14, "OR"),
    (8, "Anmol Karan", 102, 14, "VA"),
    (8, "Daniel Wu", 102, 14, "VA"),
    (8, "Elizabeth Zhang", 102, 14, "VA"),
    (8, "Ian Weatherford", 102, 14, "VA"),
    (8, "Shruthi Hebbar", 101, 15, "AR"),
    (8, "Daniel Jeon", 101, 15, "AZ"),
    (8, "Diego Agustin", 101, 15, "CA"),
    (8, "Harini Penumuchu", 101, 15, "CA"),
    (8, "Kelly Gao", 101, 15, "CA"),
    (8, "Leo Feng", 101, 15, "CA"),
    (8, "Meha Sekaran", 101, 15, "CA"),
    (8, "Natalie Kong", 101, 15, "CA"),
    (8, "Raj Pradyun Reddy Gaddam", 101, 15, "CA"),
    (8, "Rhishi Sakthivel", 101, 15, "CA"),
    (8, "Veeral Shroff", 101, 15, "CA"),
    (8, "Radea Raleva", 101, 15, "CT"),
    (8, "Rohan Bhosale", 101, 15, "IN"),
    (8, "George Durrett", 101, 15, "KS"),
    (8, "Annelise Gross", 101, 15, "MA"),
    (8, "David Katsman", 101, 15, "MA"),
    (8, "Emily Ma", 101, 15, "MA"),
    (8, "Maxwell Yu", 101, 15, "MA"),
    (8, "Maya Goldberger", 101, 15, "MA"),
    (8, "Sritan Devineni", 101, 15, "MA"),
    (8, "Thomas Li", 101, 15, "MA"),
    (8, "Christopher Wang", 101, 15, "MD"),
    (8, "Tiancheng Shao", 101, 15, "MD"),
    (8, "Dash Sukhatme", 101, 15, "NY"),
    (8, "Justin Xia", 101, 15, "OR"),
    (8, "Pranav Vijay", 101, 15, "PA"),
    (8, "Sruthi Gopalakrishnan", 101, 15, "TX"),
    (8, "Brian Wei", 101, 15, "UT"),
    (8, "Rohan Kotla", 101, 15, "VA"),
    (8, "Thomas Ye", 101, 15, "VA"),
    (8, "Yuxian Liu", 101, 15, "VA"),
    (8, "Wenjuan Zou", 101, 15, "WA"),
    (8, "Agam Randhawa", 100, 16, "CA"),
    (8, "Devin Hidayat", 100, 16, "CA"),
    (8, "Lilian Pamula", 100, 16, "CA"),
    (8, "Niharika Prachanda", 100, 16, "CA"),
    (8, "Pratinav Agrawal", 100, 16, "CA"),
    (8, "Rick Yang", 100, 16, "CA"),
    (8, "Sanat Gupta", 100, 16, "CA"),
    (8, "Podtakorn Detchprohm", 100, 16, "GA"),
    (8, "Medha Goli", 100, 16, "KS"),
    (8, "Eddy Zhao", 100, 16, "MA"),
    (8, "Eesha Gangal", 100, 16, "MA"),
    (8, "John Archibald", 100, 16, "MA"),
    (8, "Matthew Church", 100, 16, "MA"),
    (8, "Rafi Razmi", 100, 16, "MA"),
    (8, "Charlotte Li", 100, 16, "MD"),
    (8, "Mikhail Kojanov", 100, 16, "MD"),
    (8, "Aaditya Denduluri", 100, 16, "NC"),
    (8, "Aydan Ergin", 100, 16, "NY"),
    (8, "Brandon Cardamone", 100, 16, "NY"),
    (8, "Alan Zhong", 100, 16, "OR"),
    (8, "William Wang", 100, 16, "SC"),
    (8, "Callia Sun", 100, 16, "VA"),
    (8, "Noel Prince Muthuplakal", 100, 16, "WA"),
    (8, "Radley Timajo", 100, 16, "WA"),
    (8, "Collin Keopanya", 100, 16, "WI"),
    (8, "Jordan Touevsky", 99, 17, "CA"),
    (8, "Karthik Subramanian", 99, 17, "CA"),
    (8, "Satina Guo", 99, 17, "CA"),
    (8, "Atreya Mallanna", 99, 17, "MA"),
    (8, "Julia Gendin", 99, 17, "MA"),
    (8, "Nirmit Brahma", 99, 17, "MA"),
    (8, "Amani Gupta", 99, 17, "NY"),
    (8, "Darwin De Silva", 98, 18, "CA"),
    (8, "Hamed Fazel-Rezai", 98, 18, "CA"),
    (8, "Karthik Sabhanayakam", 98, 18, "CA"),
    (8, "Keona Koh", 98, 18, "CA"),
    (8, "Rainier Mayo", 98, 18, "CA"),
    (8, "Sajeev Magesh", 98, 18, "CA"),
    (8, "William Zhou", 98, 18, "CA"),
    (8, "Shourya Hooda", 98, 18, "CO"),
    (8, "Tejash Gupta", 98, 18, "GA"),
    (8, "Aadi Dash", 98, 18, "MA"),
    (8, "Irith Midha", 98, 18, "MA"),
    (8, "Omar Kannachankudy", 98, 18, "MA"),
    (8, "Jonathan Plavnik", 98, 18, "NJ"),
    (8, "Amlan Abhidarshi", 98, 18, "TX"),
    (8, "Arya Soppannavar", 98, 18, "TX"),
    (8, "Shourya Agarwal", 98, 18, "VA"),
    (8, "Andrew Kim", 98, 18, "WA"),
    (8, "Amaan Mohammad", 97, 19, "CA"),
    (8, "Appala Raju Arisetty", 97, 19, "CA"),
    (8, "Ashley Hong", 97, 19, "CA"),
    (8, "Ethan Huang", 97, 19, "CA"),
    (8, "Meghana Niranjan", 97, 19, "CA"),
    (8, "Palak Prabhakar", 97, 19, "CA"),
    (8, "Sriram Venkatesh", 97, 19, "CA"),
    (8, "Thomas Nie", 97, 19, "CA"),
    (8, "Vinay Singamsetty", 97, 19, "CA"),
    (8, "Ryan Chen", 97, 19, "IL"),
    (8, "Ranjan Dey", 97, 19, "MA"),
    (8, "Aditya Chawla", 97, 19, "MI"),
    (8, "Atharva Shinde", 97, 19, "MO"),
    (8, "Andrew Fulmer", 97, 19, "NV"),
    (8, "Leah Belostotsky", 97, 19, "NY"),
    (8, "Mark Wang", 97, 19, "OR"),
    (8, "Sarah Chung", 97, 19, "VA"),
    (8, "Eric Yee", 97, 19, "WA"),
    (8, "Aakash Gokhale", 96, 20, "CA"),
    (8, "Emmie Kao", 96, 20, "CA"),
    (8, "Franklin Yang", 96, 20, "CA"),
    (8, "Harry Christiansen", 96, 20, "CA"),
    (8, "Olivia So", 96, 20, "CA"),
    (8, "Raymond Cai", 96, 20, "CA"),
    (8, "Megan Dsouza", 96, 20, "FL"),
    (8, "Samuelson Belime", 96, 20, "FL"),
    (8, "Alexander Mitev", 96, 20, "IL"),
    (8, "Jan Lojewski", 96, 20, "IL"),
    (8, "Rishi Kanchi", 96, 20, "IL"),
    (8, "Lucia Zhang", 96, 20, "IN"),
    (8, "Mahira Hafeez", 96, 20, "IN"),
    (8, "Hanlin Zhang", 96, 20, "MA"),
    (8, "Niko Todorov", 96, 20, "MA"),
    (8, "Siddhant Ganeshwaran", 96, 20, "MA"),
    (8, "Yashwant Bolishetti", 96, 20, "MA"),
    (8, "Qian Li", 96, 20, "MI"),
    (8, "Abhay Bhaskar", 96, 20, "NJ"),
    (8, "Alexander Recce", 96, 20, "NJ"),
    (8, "Anish Mahapatra", 96, 20, "NJ"),
    (8, "Noah Lee", 96, 20, "NV"),
    (8, "Marina Li", 96, 20, "VA"),
    (8, "Ariel Khais", 96, 20, "WA"),
    (8, "Dhruv Kasarabada", 96, 20, "WA"),
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
