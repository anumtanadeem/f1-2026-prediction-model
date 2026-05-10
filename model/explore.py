import fastf1
import os

os.makedirs("f1_cache", exist_ok=True)
fastf1.Cache.enable_cache("f1_cache")

print("Loading 2026 Australian GP...")
session = fastf1.get_session(2026, 1, "R")

# Only load what we need — skips timing app, telemetry, weather
session.load(
    laps=True,
    telemetry=False,
    weather=False,
    messages=False,
    livedata=None
)

laps = session.laps
print("\nDrivers in this race:")
print(laps["Driver"].unique())

print("\nSample of lap data:")
print(laps[["Driver", "LapTime", "Sector1Time", "Sector2Time", "Sector3Time"]].head(10))