import pandas as pd
import numpy as np
from visualize import plot_results
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

from feature_engineering import build_features, apply_reliability_penalty
from f1_2026_config import DRIVER_TO_TEAM

# ── Features the model will use ────────────────────────────────────────────
FEATURE_COLS = [
    "QualiGap_s",
    "EffectiveQualiTime_s",
    "TeamScore",
    "ReliabilityRisk",
    "EnergyMgmt",
    "OvertakeEff",
    "RainProb",
    "Temperature",
    "AvgLapTime_s",
]

def build_pipeline(estimator):
    """Wraps any model in imputer + scaler + model pipeline."""
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
        ("model",   estimator),
    ])

def train_model(X: pd.DataFrame, y: pd.Series):
    """
    Train GBR + RandomForest ensemble and report CV MAE.
    Returns both trained pipelines.
    """
    print("\nTraining models...")

    # ── Model 1: Gradient Boosting ─────────────────────────────────────────
    gbr = build_pipeline(GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        subsample=0.8,
        random_state=42
    ))

    # ── Model 2: Random Forest ─────────────────────────────────────────────
    rf = build_pipeline(RandomForestRegressor(
        n_estimators=200,
        max_depth=4,
        random_state=42
    ))

    # ── Cross validation MAE ───────────────────────────────────────────────
    cv = min(5, len(X))  # use 5 folds or less if not enough data
    gbr_scores = cross_val_score(gbr, X, y, cv=cv, scoring="neg_mean_absolute_error")
    rf_scores  = cross_val_score(rf,  X, y, cv=cv, scoring="neg_mean_absolute_error")

    gbr_mae = -gbr_scores.mean()
    rf_mae  = -rf_scores.mean()

    print(f"  GBR CV MAE: {gbr_mae:.3f}s")
    print(f"  RF  CV MAE: {rf_mae:.3f}s")
    print(f"  Ensemble MAE (avg): {(gbr_mae + rf_mae) / 2:.3f}s")

    # ── Train on full dataset ──────────────────────────────────────────────
    gbr.fit(X, y)
    rf.fit(X, y)

    return gbr, rf, gbr_mae, rf_mae

def predict(gbr, rf, X: pd.DataFrame) -> np.ndarray:
    """60/40 weighted ensemble prediction."""
    p_gbr = gbr.predict(X)
    p_rf  = rf.predict(X)
    return 0.6 * p_gbr + 0.4 * p_rf

# ── Main — Canadian GP prediction ─────────────────────────────────────────
if __name__ == "__main__":

    # Step 11: Load 2026 training data
    print("Loading 2026 training data...")
    driver_averages = pd.read_csv("2026_driver_averages.csv")

    # Step 12: 2026 Canadian GP qualifying data
    # Replace these with real qualifying times after Saturday
    qualifying_2026 = pd.DataFrame({
        "Driver": [
            "ANT", "RUS", "NOR", "LEC", "VER",
            "HAM", "PIA", "SAI", "ALB", "GAS",
            "COL", "LAW", "BEA", "HAD", "ALO",
            "STR", "HUL", "BOR", "PER", "BOT",
            "OCO", "LIN"
        ],
        "QualifyingTime_s": [
            73.1, 73.3, 73.4, 73.6, 73.8,
            74.0, 74.1, 74.3, 74.5, 74.6,
            74.7, 74.9, 75.0, 75.2, 75.4,
            75.5, 75.7, 75.8, 76.0, 76.2,
            76.3, 76.5
        ]
    })

    # Race conditions
    RAIN_PROB   = 0.20   # update before race
    TEMPERATURE = 22.0   # update before race

    # Step 13: Build features
    print("Building features...")
    features = build_features(
        qualifying_2026=qualifying_2026,
        driver_averages=driver_averages,
        rain_prob=RAIN_PROB,
        temperature=TEMPERATURE
    )

    # Prepare training data — use 2026 avg lap time as target
    mask = features["AvgLapTime_s"].notna()
    X_train = features.loc[mask, FEATURE_COLS]
    y_train = features.loc[mask, "AvgLapTime_s"]

    # Train
    gbr, rf, gbr_mae, rf_mae = train_model(X_train, y_train)

    # Predict for all drivers
    X_all = features[FEATURE_COLS]
    features["PredictedTime_s"] = predict(gbr, rf, X_all)

    # Apply reliability penalty
    results = apply_reliability_penalty(features)

    # Sort by adjusted time
    results = results.sort_values("AdjustedTime_s").reset_index(drop=True)
    results["Position"] = range(1, len(results) + 1)

    # ── Print results ──────────────────────────────────────────────────────
    print("\n" + "═"*45)
    print("  *** 2026 CANADIAN GP — PREDICTED STANDINGS ***")
    print("═"*45)
    medals = {0: "P1", 1: "P2", 2: "P3"}
    for i, row in results.iterrows():
        medal = medals.get(i, f"P{i+1}")
        gap = "" if i == 0 else f"+{row['AdjustedTime_s'] - results['AdjustedTime_s'].iloc[0]:.3f}s"
        print(f"  {medal}  {row['Driver']:<4}  {row['AdjustedTime_s']:.3f}s  {gap}")
    print("═"*45)
    print(f"\n  Model MAE: ~{(gbr_mae + rf_mae) / 2:.3f}s per lap")
    # ── Generate chart ─────────────────────────────────────────────────────
    plot_results(results, gbr, FEATURE_COLS, "Canadian GP")