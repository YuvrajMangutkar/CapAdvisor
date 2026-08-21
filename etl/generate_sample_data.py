"""
generate_sample_data.py
-----------------------
Generates realistic synthetic MHT-CET CAP round cutoff data for Maharashtra
engineering colleges (2022–2024). Outputs structured CSVs to data/processed/.

Run: python etl/generate_sample_data.py
"""

import os
import csv
import random

random.seed(42)

# ---------------------------------------------------------------------------
# Reference Data
# ---------------------------------------------------------------------------

COLLEGES = [
    # id, name, district, type, nirf_proxy (1=best, 20=lowest)
    (1,  "College of Engineering Pune (COEP)",             "Pune",        "Autonomous", 1),
    (2,  "Veermata Jijabai Technological Institute (VJTI)", "Mumbai",      "Autonomous", 2),
    (3,  "Institute of Chemical Technology (ICT)",          "Mumbai",      "Autonomous", 3),
    (4,  "Pune Institute of Computer Technology (PICT)",    "Pune",        "Unaided",    4),
    (5,  "Vishwakarma Institute of Technology (VIT Pune)",  "Pune",        "Unaided",    5),
    (6,  "DJ Sanghvi College of Engineering",               "Mumbai",      "Unaided",    6),
    (7,  "KJ Somaiya College of Engineering",               "Mumbai",      "Unaided",    7),
    (8,  "Sardar Patel College of Engineering (SPCE)",      "Mumbai",      "Aided",      8),
    (9,  "MIT College of Engineering Pune",                 "Pune",        "Unaided",    9),
    (10, "Ramrao Adik Institute of Technology",             "Navi Mumbai", "Unaided",   10),
    (11, "Fr. Conceicao Rodrigues College of Engineering",  "Mumbai",      "Aided",     11),
    (12, "Thadomal Shahani Engineering College",            "Mumbai",      "Unaided",   12),
    (13, "Army Institute of Technology",                    "Pune",        "Aided",     13),
    (14, "Walchand College of Engineering Sangli",          "Sangli",      "Aided",     14),
    (15, "Government College of Engineering Aurangabad",    "Aurangabad",  "Government",15),
    (16, "Yashwantrao Chavan College of Engineering",       "Nagpur",      "Aided",     16),
    (17, "Government College of Engineering Amravati",      "Amravati",    "Government",17),
    (18, "Lokmanya Tilak College of Engineering",           "Navi Mumbai", "Unaided",   18),
    (19, "Sinhgad College of Engineering",                  "Pune",        "Unaided",   19),
    (20, "DY Patil College of Engineering",                 "Pune",        "Unaided",   20),
]

BRANCHES = [
    # id, name, code, demand_factor (higher = more competitive, AI/CS trending up)
    (1,  "Computer Engineering",                    "CE",    1.00),
    (2,  "Information Technology",                  "IT",    0.97),
    (3,  "Artificial Intelligence & Data Science",  "AIDS",  0.98),
    (4,  "Electronics & Telecommunication Engg",    "ETE",   0.88),
    (5,  "Mechanical Engineering",                  "MECH",  0.75),
    (6,  "Civil Engineering",                       "CIVIL", 0.65),
    (7,  "Electrical Engineering",                  "EE",    0.78),
]

# Not all colleges offer all branches
COLLEGE_BRANCH_MAP = {
    1:  [1, 2, 3, 4, 5, 6, 7],   # COEP: all
    2:  [1, 2, 3, 4, 5, 6, 7],   # VJTI: all
    3:  [4, 5, 6, 7],             # ICT: non-CS heavy
    4:  [1, 2, 3, 4],             # PICT: CS focused
    5:  [1, 2, 3, 4, 5, 7],       # VIT Pune
    6:  [1, 2, 3, 4, 5, 7],       # DJ Sanghvi
    7:  [1, 2, 3, 4, 5, 7],       # KJ Somaiya
    8:  [1, 2, 4, 5, 6, 7],       # SPCE
    9:  [1, 2, 3, 4, 5, 6, 7],    # MIT Pune: all
    10: [1, 2, 3, 4, 5, 7],       # RAIT
    11: [1, 2, 4, 5, 7],          # FRCRCE
    12: [1, 2, 3, 4, 5],          # Thadomal
    13: [1, 2, 4, 5, 7],          # AIT
    14: [1, 2, 4, 5, 6, 7],       # Walchand
    15: [1, 2, 4, 5, 6, 7],       # GCE Aurangabad
    16: [1, 2, 4, 5, 6, 7],       # YCCE Nagpur
    17: [1, 2, 4, 5, 6, 7],       # GCE Amravati
    18: [1, 2, 3, 4, 5],          # LTCE
    19: [1, 2, 3, 4, 5, 6, 7],    # Sinhgad: all
    20: [1, 2, 3, 4, 5, 6, 7],    # DY Patil: all
}

CATEGORIES = [
    # code, label, percentile_discount (subtracted from Open cutoff)
    ("GOPENH",  "Open (Home University)",          0.0),
    ("GOBCNH",  "OBC-NCL (Home University)",       6.0),
    ("GSCNH",   "SC (Home University)",           18.0),
    ("GSTNH",   "ST (Home University)",           28.0),
    ("GEWSNH",  "EWS (Home University)",           3.5),
    ("LOPENS",  "Open (Other than Home Univ.)",    2.5),
]

YEARS  = [2022, 2023, 2024]
ROUNDS = [1, 2, 3]

# Base closing percentile for Open/CE per college (approximates real MHT-CET data)
BASE_CLOSING_PCT = {
    1:  99.10,  # COEP
    2:  98.80,  # VJTI
    3:  95.00,  # ICT (different profile)
    4:  97.20,  # PICT
    5:  96.50,  # VIT Pune
    6:  96.80,  # DJ Sanghvi
    7:  96.20,  # KJ Somaiya
    8:  95.60,  # SPCE
    9:  94.80,  # MIT Pune
    10: 94.50,  # RAIT
    11: 94.00,  # FRCRCE
    12: 93.50,  # Thadomal
    13: 93.00,  # AIT
    14: 91.00,  # Walchand Sangli
    15: 89.00,  # GCE Aurangabad
    16: 87.00,  # YCCE Nagpur
    17: 85.00,  # GCE Amravati
    18: 91.50,  # LTCE
    19: 88.00,  # Sinhgad
    20: 86.00,  # DY Patil
}

# Yearly trend: MHT-CET gets slightly more competitive each year
YEARLY_TREND = {2022: -0.4, 2023: 0.0, 2024: +0.4}

# Round effect: Round 1 has the widest spread (many seats), later rounds tighten
ROUND_CLOSING_ADJUST = {1: +0.0, 2: -0.8, 3: -1.5}  # closing rises in R2/R3 (harder to get)
# (In reality: R1 cutoff is 'relaxed', R2 tightens as seats fill, R3 is the last chance)
# Actually in MHT-CET CAP, successive rounds may have lower cutoffs as good students
# already got seats. Let's model it more accurately:
# R1: highest cutoffs (most competition), R2/R3: slightly lower
ROUND_CLOSING_ADJUST = {1: 0.0, 2: -0.5, 3: -1.2}

SEATS = {
    1:  {"CE": 60, "IT": 60, "AIDS": 30, "ETE": 60, "MECH": 60, "CIVIL": 60, "EE": 60},
    2:  {"CE": 60, "IT": 60, "AIDS": 30, "ETE": 60, "MECH": 60, "CIVIL": 60, "EE": 60},
    3:  {"CE": 30, "IT": 30, "AIDS": 30, "ETE": 30, "MECH": 30, "CIVIL": 30, "EE": 30},
    4:  {"CE": 120,"IT": 120,"AIDS": 60, "ETE": 60},
    5:  {"CE": 60, "IT": 60, "AIDS": 60, "ETE": 60, "MECH": 60, "EE": 60},
    6:  {"CE": 60, "IT": 60, "AIDS": 60, "ETE": 60, "MECH": 60, "EE": 60},
    7:  {"CE": 60, "IT": 60, "AIDS": 60, "ETE": 60, "MECH": 60, "EE": 60},
    8:  {"CE": 60, "IT": 60, "ETE": 60, "MECH": 60, "CIVIL": 60, "EE": 60},
    9:  {"CE": 120,"IT": 120,"AIDS": 60, "ETE": 60, "MECH": 60, "CIVIL": 60, "EE": 60},
    10: {"CE": 60, "IT": 60, "AIDS": 60, "ETE": 60, "MECH": 60, "EE": 60},
    11: {"CE": 60, "IT": 60, "ETE": 60, "MECH": 60, "EE": 60},
    12: {"CE": 60, "IT": 60, "AIDS": 60, "ETE": 60, "MECH": 60},
    13: {"CE": 60, "IT": 60, "ETE": 60, "MECH": 60, "EE": 60},
    14: {"CE": 60, "IT": 60, "ETE": 60, "MECH": 60, "CIVIL": 60, "EE": 60},
    15: {"CE": 60, "IT": 60, "ETE": 60, "MECH": 60, "CIVIL": 60, "EE": 60},
    16: {"CE": 60, "IT": 60, "ETE": 60, "MECH": 60, "CIVIL": 60, "EE": 60},
    17: {"CE": 60, "IT": 60, "ETE": 60, "MECH": 60, "CIVIL": 60, "EE": 60},
    18: {"CE": 60, "IT": 60, "AIDS": 60, "ETE": 60, "MECH": 60},
    19: {"CE": 120,"IT": 120,"AIDS": 60, "ETE": 60, "MECH": 60, "CIVIL": 60, "EE": 60},
    20: {"CE": 120,"IT": 120,"AIDS": 60, "ETE": 60, "MECH": 60, "CIVIL": 60, "EE": 60},
}

BRANCH_CODE_MAP = {b[2]: b for b in BRANCHES}


def clamp(val: float, lo: float = 10.0, hi: float = 99.99) -> float:
    return round(max(lo, min(hi, val)), 2)


def generate_cutoff_row(college_id, branch_id, cat_code, cat_discount, year, round_no):
    branch = next(b for b in BRANCHES if b[0] == branch_id)
    branch_code = branch[2]
    branch_demand = branch[3]

    base = BASE_CLOSING_PCT[college_id]
    # Apply branch demand (CS close to base, others lower)
    branch_adj = (branch_demand - 1.0) * 12   # CE: 0, ETE: -1.44, MECH: -3.0, CIVIL: -4.2
    # Apply category discount
    cat_adj = -cat_discount
    # Apply year trend
    year_adj = YEARLY_TREND[year]
    # Apply round effect
    round_adj = ROUND_CLOSING_ADJUST[round_no]
    # Small noise
    noise = random.gauss(0, 0.3)

    closing_pct = clamp(base + branch_adj + cat_adj + year_adj + round_adj + noise)
    # Opening percentile: the first (highest percentile) student admitted — 0.5-2 pts above closing
    opening_adj = random.uniform(0.5, 2.5)
    opening_pct = clamp(closing_pct + opening_adj)

    seats = SEATS.get(college_id, {}).get(branch_code, 60)

    return {
        "college_id": college_id,
        "branch_id": branch_id,
        "category_code": cat_code,
        "year": year,
        "round": round_no,
        "opening_percentile": opening_pct,
        "closing_percentile": closing_pct,
        "total_seats": seats,
        "filled_seats": int(seats * random.uniform(0.80, 1.0)),
    }


def main():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
    os.makedirs(out_dir, exist_ok=True)

    # ── colleges.csv ────────────────────────────────────────────────────────
    colleges_path = os.path.join(out_dir, "colleges.csv")
    with open(colleges_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["college_id", "college_name", "district", "college_type", "nirf_rank_proxy"])
        for c in COLLEGES:
            w.writerow(c)
    print(f"[OK] Written {colleges_path}")

    # ── branches.csv ─────────────────────────────────────────────────────────
    branches_path = os.path.join(out_dir, "branches.csv")
    with open(branches_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["branch_id", "branch_name", "branch_code", "demand_factor"])
        for b in BRANCHES:
            w.writerow(b)
    print(f"[OK] Written {branches_path}")

    # ── categories.csv ────────────────────────────────────────────────────────
    categories_path = os.path.join(out_dir, "categories.csv")
    with open(categories_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["category_code", "category_label", "percentile_discount"])
        for cat in CATEGORIES:
            w.writerow(cat)
    print(f"[OK] Written {categories_path}")

    # ── cutoffs.csv ───────────────────────────────────────────────────────────
    cutoffs_path = os.path.join(out_dir, "cutoffs.csv")
    rows = []
    row_id = 1
    for college in COLLEGES:
        c_id = college[0]
        for b_id in COLLEGE_BRANCH_MAP[c_id]:
            for cat_code, _, cat_discount in CATEGORIES:
                for year in YEARS:
                    for round_no in ROUNDS:
                        row = generate_cutoff_row(c_id, b_id, cat_code, cat_discount, year, round_no)
                        row["id"] = row_id
                        rows.append(row)
                        row_id += 1

    fieldnames = ["id", "college_id", "branch_id", "category_code", "year", "round",
                  "opening_percentile", "closing_percentile", "total_seats", "filled_seats"]
    with open(cutoffs_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"[OK] Written {cutoffs_path} ({len(rows)} rows)")
    print(f"\nSample data generation complete. Total cutoff records: {len(rows)}")


if __name__ == "__main__":
    main()
