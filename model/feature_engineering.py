# feature_engineering.py
import pandas as pd
import numpy as np
from f1_2026_config import DRIVER_TO_TEAM, TEAM_POINTS, PU_RELIABILITY, WET_FACTORS, ENERGY_MANAGEMENT

def quali_gap(times: pd.Series) -> pd.Series:
    return times - times.min()

def build_features(qualifying_2026: pd.DataFrame,
                   driver_averages: pd.DataFrame,
                   rain_prob: float,
                   temperature: float) -> pd.DataFrame:

    df = qualifying_2026.copy()

    # Feature 1: Qualifying gap to pole
    df["QualiGap_s"] = quali_gap(df["QualifyingTime_s"])

    # Feature 2: Wet adjusted qualifying time
    df["WetFactor"] = df["Driver"].map(WET_FACTORS).fillna(1.0)
    if rain_prob >= 0.75:
        df["EffectiveQualiTime_s"] = df["QualifyingTime_s"] * df["WetFactor"]
    else:
        df["EffectiveQualiTime_s"] = df["QualifyingTime_s"]

    # Feature 3: Team constructor score
    max_pts = max(TEAM_POINTS.values())
    df["Team"] = df["Driver"].map(DRIVER_TO_TEAM)
    df["TeamScore"] = df["Team"].map(
        {t: p / max_pts for t, p in TEAM_POINTS.items()}
    ).fillna(0.0)

    # Feature 4: Reliability risk
    pu_map = {
        "ANT": "Mercedes", "RUS": "Mercedes",
        "NOR": "Mercedes", "PIA": "Mercedes",
        "LEC": "Ferrari",  "HAM": "Ferrari",
        "OCO": "Ferrari",  "LIN": "Ferrari",
        "PER": "Ferrari",  "BOT": "Ferrari",
        "VER": "Red Bull Ford", "HAD": "Red Bull Ford",
        "LAW": "Red Bull Ford", "BEA": "Red Bull Ford",
        "ALO": "Honda",    "STR": "Honda",
        "HUL": "Audi",     "BOR": "Audi",
        "GAS": "Mercedes", "COL": "Mercedes",
        "ALB": "Mercedes", "SAI": "Mercedes",
    }
    df["ReliabilityRisk"] = df["Driver"].map(
        {d: PU_RELIABILITY[pu] for d, pu in pu_map.items()}
    ).fillna(0.20)

    # Feature 5: Energy management score
    df["EnergyMgmt"] = df["Team"].map(ENERGY_MANAGEMENT).fillna(0.60)

    # Feature 6: Overtake mode effectiveness
    from f1_2026_config import OVERTAKE_EFFECTIVENESS
    df["OvertakeEff"] = df["Driver"].map(OVERTAKE_EFFECTIVENESS).fillna(0.0)
    
    # Feature 7: Weather
    df["RainProb"]    = rain_prob
    df["Temperature"] = temperature

    # Feature 8: 2026 average lap time from training data
    df = df.merge(
        driver_averages[["Driver", "AvgLapTime_s", "AvgS1_s", "AvgS2_s", "AvgS3_s"]],
        on="Driver",
        how="left"
    )

    return df

def apply_reliability_penalty(results: pd.DataFrame) -> pd.DataFrame:
    results = results.copy()
    results["AdjustedTime_s"] = results["PredictedTime_s"] * (
        1 + results["ReliabilityRisk"] * 0.05
    )
    return results

# ── Test ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":

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

    features["PredictedTime_s"] = features["QualifyingTime_s"] + features["QualiGap_s"] * 0.3
    results = apply_reliability_penalty(features)

    print("\n--- Feature matrix ---")
    print(results[[
        "Driver", "QualiGap_s", "TeamScore",
        "ReliabilityRisk", "EnergyMgmt", "OvertakeEff"
    ]].to_string(index=False))