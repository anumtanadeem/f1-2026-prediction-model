# f1_2026_config.py
# Single source of truth for all 2026 F1 team and driver info
# Update constructor points before each race

# ── Power unit suppliers ───────────────────────────────────────────────────
POWER_UNITS = {
    "Mercedes":     ["Mercedes", "Alpine"],
    "Ferrari":      ["Ferrari", "Haas", "Cadillac"],
    "Red Bull Ford":["Red Bull", "Racing Bulls"],
    "Honda":        ["Aston Martin"],
    "Audi":         ["Audi"],
}

# ── Driver to team mapping ─────────────────────────────────────────────────
DRIVER_TO_TEAM = {
    # Mercedes
    "ANT": "Mercedes",
    "RUS": "Mercedes",
    # McLaren
    "NOR": "McLaren",
    "PIA": "McLaren",
    # Ferrari
    "LEC": "Ferrari",
    "HAM": "Ferrari",
    # Red Bull
    "VER": "Red Bull",
    "HAD": "Red Bull",
    # Aston Martin (Honda PU)
    "ALO": "Aston Martin",
    "STR": "Aston Martin",
    # Alpine (Mercedes PU)
    "GAS": "Alpine",
    "COL": "Alpine",
    # Williams
    "ALB": "Williams",
    "SAI": "Williams",
    # Racing Bulls (Red Bull Ford PU)
    "LAW": "Racing Bulls",
    "BEA": "Racing Bulls",
    # Audi (new constructor)
    "HUL": "Audi",
    "BOR": "Audi",
    # Cadillac (new constructor, Ferrari PU)
    "PER": "Cadillac",
    "BOT": "Cadillac",
    # Haas (Ferrari PU)
    "OCO": "Haas",
    "LIN": "Haas",
}

# ── Driver to power unit mapping ───────────────────────────────────────────
DRIVER_TO_PU = {d: pu for pu, teams in POWER_UNITS.items() for t in teams for d, team in DRIVER_TO_TEAM.items() if team == t}

# ── Constructor points after Miami (Round 4) ───────────────────────────────
# Update this before each race
TEAM_POINTS = {
    "Mercedes":     149,
    "Ferrari":      107,
    "McLaren":      104,
    "Red Bull":      47,
    "Williams":      44,
    "Alpine":        32,
    "Racing Bulls":  21,
    "Haas":          14,
    "Audi":          10,
    "Aston Martin":   6,
    "Cadillac":       4,
}

# ── Reliability risk per power unit (DNF rate so far in 2026) ─────────────
# 0.0 = perfectly reliable, 1.0 = DNF every race
# Based on real 2026 early season DNF data
PU_RELIABILITY = {
    "Mercedes":      0.10,
    "Ferrari":       0.15,
    "Red Bull Ford": 0.25,   # VER DNF already this season
    "Honda":         0.20,   # ALO DNF already this season
    "Audi":          0.30,   # New PU, least proven
}

# ── Wet performance factors ────────────────────────────────────────────────
# Below 1.0 = better in wet, above 1.0 = worse in wet
WET_FACTORS = {
    "ANT": 0.972,
    "RUS": 0.969,
    "NOR": 0.978,
    "PIA": 0.980,
    "LEC": 0.976,
    "HAM": 0.976,
    "VER": 0.975,
    "HAD": 0.990,
    "ALO": 0.973,
    "STR": 0.980,
    "GAS": 0.979,
    "COL": 0.982,
    "ALB": 0.981,
    "SAI": 0.979,
    "LAW": 0.985,
    "BEA": 0.988,
    "HUL": 0.985,
    "BOR": 0.988,
    "PER": 0.983,
    "BOT": 0.987,
    "OCO": 0.982,
    "LIN": 0.990,
}