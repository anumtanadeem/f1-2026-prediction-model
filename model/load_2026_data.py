import fastf1
import pandas as pd
import os

os.makedirs("f1_cache", exist_ok=True)
fastf1.Cache.enable_cache("f1_cache")

def load_race(year, round_number, race_name):
    print(f"Loading {race_name}...")
    try:
        session = fastf1.get_session(year, round_number, "R")
        session.load(
            laps=True,
            telemetry=False,
            weather=False,
            messages=False,
            livedata=None
        )
        laps = session.laps[["Driver", "LapTime", "Sector1Time", "Sector2Time", "Sector3Time"]].copy()

        # Convert to seconds first
        laps["LapTime_s"] = laps["LapTime"].dt.total_seconds()
        laps["S1_s"]      = laps["Sector1Time"].dt.total_seconds()
        laps["S2_s"]      = laps["Sector2Time"].dt.total_seconds()
        laps["S3_s"]      = laps["Sector3Time"].dt.total_seconds()

        # Only drop rows where LapTime itself is missing
        # Keep rows even if sector times are missing
        laps = laps.dropna(subset=["LapTime_s"])

        # Filter per driver individually
        def filter_driver(group):
            if len(group) < 5:
                return group  # too few laps to filter, keep all
            q_low  = group["LapTime_s"].quantile(0.10)
            q_high = group["LapTime_s"].quantile(0.90)
            return group[(group["LapTime_s"] >= q_low) & (group["LapTime_s"] <= q_high)]

        laps = laps.groupby("Driver", group_keys=False).apply(filter_driver)

        laps["Race"] = race_name
        print(f"  ✓ {len(laps)} clean laps | {laps['Driver'].nunique()} drivers")
        return laps

    except Exception as e:
        print(f"  ✗ Failed to load {race_name}: {e}")
        return pd.DataFrame()

# Load all four 2026 races
races = [
    (2026, 1, "Australia"),
    (2026, 2, "China"),
    (2026, 3, "Japan"),
    (2026, 4, "Miami"),
]

frames = []
for year, round_num, name in races:
    df = load_race(year, round_num, name)
    if not df.empty:
        frames.append(df)

# Combine into one dataset
all_laps = pd.concat(frames, ignore_index=True)

# Calculate average lap time per driver across all 2026 races
driver_averages = all_laps.groupby("Driver").agg(
    AvgLapTime_s = ("LapTime_s", "mean"),
    AvgS1_s      = ("S1_s", "mean"),
    AvgS2_s      = ("S2_s", "mean"),
    AvgS3_s      = ("S3_s", "mean"),
    TotalLaps    = ("LapTime_s", "count")
).reset_index()

print("\n--- 2026 Driver Averages (fastest to slowest) ---")
print(driver_averages.sort_values("AvgLapTime_s").to_string(index=False))

# Save for use in our model later
driver_averages.to_csv("2026_driver_averages.csv", index=False)
print("\n✓ Saved to 2026_driver_averages.csv")