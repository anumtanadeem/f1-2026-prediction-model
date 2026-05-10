# feature_engineering.py
# Builds the feature matrix that the model will train on

import pandas as pd
import numpy as np
from f1_2026_config import DRIVER_TO_TEAM, TEAM_POINTS, PU_RELIABILITY, WET_FACTORS

def quali_gap(times: pd.Series) -> pd.Series:
    """
    Gap to pole position in seconds.
    Example: pole=88.0s, driver=88.5s → gap=0.5s
    This works across all circuits — Monaco or Monza, the gap is always meaningful.
    Raw time is not — Monaco pole is ~72s, Monza is ~59s.
    """
    return times - times.min()

def build_features(qualifying_2026: pd.DataFrame,
                   driver_averages: pd.DataFrame,
                   rain_prob: float,
                   temperature: float) -> pd.DataFrame:
    """
    Merges all features into one DataFrame ready for the model.
    """
    df = qualifying_2026.copy()

    # ── Feature 1: Qualifying gap to pole (circuit-agnostic) ──────────────
    df["QualiGap_s"] = quali_gap(df["QualifyingTime_s"])

    # ── Feature 2: Wet-adjusted qualifying time ───────────────────────────
    df["WetFactor"] = df["Driver"].map(WET_FACTORS).fillna(1.0)
    if rain_prob >= 0.75:
        df["EffectiveQualiTime_s"] = df["QualifyingTime_s"] * df["WetFactor"]
    else:
        df["EffectiveQualiTime_s"] = df["QualifyingTime_s"]

    # ── Feature 3: Team constructor score (normalised 0-1) ────────────────
    max_pts = max(TEAM_POINTS.values())
    df["Team"] = df["Driver"].map(DRIVER_TO_TEAM)
    df["TeamScore"] = df["Team"].map(
        {t: p / max_pts for t, p in TEAM_POINTS.items()}
    ).fillna(0.0)

    # ── Feature 4: Reliability risk per power unit ────────────────────────
    # Maps each driver to their PU manufacturer's reliability score
    pu_map = {
        "ANT": "Mercedes", "RUS": "Mercedes",
        "NOR": "Mercedes", "PIA": "Mercedes",   # McLaren uses Mercedes PU
        "LEC": "Ferrari",  "HAM": "Ferrari",
        "OCO": "Ferrari",  "LIN": "Ferrari",    # Haas uses Ferrari PU
        "PER": "Ferrari",  "BOT": "Ferrari",    # Cadillac uses Ferrari PU
        "VER": "Red Bull Ford", "HAD": "Red Bull Ford",
        "LAW": "Red Bull Ford", "BEA": "Red Bull Ford",
        "ALO": "Honda",    "STR": "Honda",
        "HUL": "Audi",     "BOR": "Audi",
        "GAS": "Mercedes", "COL": "Mercedes",   # Alpine uses Mercedes PU
        "ALB": "Mercedes", "SAI": "Mercedes",   # Williams uses Mercedes PU
    }
    df["ReliabilityRisk"] = df["Driver"].map(
        {d: PU_RELIABILITY[pu] for d, pu in pu_map.items()}
    ).fillna(0.20)

    # ── Feature 5: Weather ────────────────────────────────────────────────
    df["RainProb"]    = rain_prob
    df["Temperature"] = temperature

    # ── Feature 6: 2026 average lap time from training data ───────────────
    df = df.merge(
        driver_averages[["Driver", "AvgLapTime_s", "AvgS1_s", "AvgS2_s", "AvgS3_s"]],
        on="Driver",
        how="left"
    )

    return df

def apply_reliability_penalty(results: pd.DataFrame) -> pd.DataFrame:
    """
    Adjusts predicted lap time upward based on power unit reliability risk.
    
    Logic: a driver with 25% DNF risk effectively "loses" 25% of races.
    We translate that into a lap time penalty so unreliable cars
    rank lower in the predicted standings — reflecting real expected points.
    
    Example: VER predicted at 92.0s with 0.25 risk → 92.0 * (1 + 0.25*0.05)
    = 92.0 * 1.0125 = 93.15s — drops him down the order slightly.
    """
    results = results.copy()
    results["AdjustedTime_s"] = results["PredictedTime_s"] * (
        1 + results["ReliabilityRisk"] * 0.05
    )
    return results

# ── Test it works ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import pandas as pd

    test_quali = pd.DataFrame({
        "Driver": ["ANT", "NOR", "RUS", "LEC", "HAM", "VER"],
        "QualifyingTime_s": [88.0, 88.2, 88.4, 88.6, 88.8, 89.0]
    })

    driver_averages = pd.read_csv("2026_driver_averages.csv")

    features = build_features(
        qualifying_2026=test_quali,
        driver_averages=driver_averages,
        rain_prob=0.10,
        temperature=22.0
    )

    # Simulate predicted times (we'll replace this with real model output later)
    features["PredictedTime_s"] = features["QualifyingTime_s"] + features["QualiGap_s"] * 0.3

    # Apply reliability penalty
    results = apply_reliability_penalty(features)

    print("\n--- Before reliability penalty ---")
    print(results[["Driver", "PredictedTime_s"]].sort_values("PredictedTime_s").to_string(index=False))

    print("\n--- After reliability penalty ---")
    print(results[["Driver", "AdjustedTime_s", "ReliabilityRisk"]].sort_values("AdjustedTime_s").to_string(index=False))