# F1 2026 Race Prediction Model

A machine learning model that predicts Formula 1 race results before the race happens, fully updated for the 2026 regulations.

Built on top of an open-source prototype and significantly improved with 2026-specific features.

---

## Results

### Canadian GP (Round 5) — Predicted Standings
*Qualifying data plugged in after Saturday May 24*

| Position | Driver | Team | Predicted Time |
|----------|--------|------|----------------|
| P1 | TBD | TBD | TBD |
| P2 | TBD | TBD | TBD |
| P3 | TBD | TBD | TBD |

*Chart will be added after qualifying*

---

## What the model does

Takes real F1 data available before a race — qualifying times, season performance, weather — and predicts the finishing order using a machine learning ensemble model.

---

## Improvements over the prototype

| Feature | Prototype | This Model |
|---------|-----------|------------|
| Training data | 1 race (2025) | 4 races (2026) |
| Qualifying feature | Raw lap time | Gap to pole position |
| Model | Single GBR | GBR + RandomForest ensemble |
| Evaluation | Single split MAE | Cross-validation MAE |
| Teams | 10 teams | 11 teams (Audi, Cadillac added) |
| 2026 features | None | Energy management, reliability risk, overtake effectiveness |
| MAE | 3.47s | 0.595s |

---

## 2026 Regulation Changes Modelled

- **Active aerodynamics** replacing DRS — modelled via overtake effectiveness score
- **New power units** — Audi, Red Bull Ford, Honda (Aston Martin) reliability profiles added
- **Energy management** — superclipping and ERS harvesting adaptation per team
- **New teams** — Audi and Cadillac included with accurate performance profiles

---

## How to run it

**Install dependencies:**
```bash
pip install fastf1 pandas numpy scikit-learn matplotlib requests
```

**Load 2026 training data:**
```bash
cd model
python load_2026_data.py
```

**Run prediction (update qualifying times in model.py first):**
```bash
python model.py
```

---

## Project structure
f1-2026-prediction-model/
│
├── prototype/          # Original open-source prototype for reference
├── model/              # Improved 2026 model
│   ├── f1_2026_config.py       # Teams, drivers, PU info
│   ├── load_2026_data.py       # Loads real F1 data via FastF1
│   ├── feature_engineering.py  # Feature matrix builder
│   ├── model.py                # GBR + RF ensemble
│   └── visualize.py            # Results chart
└── README.md

---

## Tech stack

- **FastF1** — real F1 timing data
- **scikit-learn** — GradientBoostingRegressor + RandomForestRegressor
- **pandas / numpy** — data processing
- **matplotlib** — visualization

---

## Prototype credit

Original prototype by [mar_antaya](https://github.com/mar_antaya) — built for 2025 regulations. This project extends and updates it for the 2026 season.

---

*Predictions are updated each race weekend after qualifying. Next race: Canadian GP — May 22-24, 2026*