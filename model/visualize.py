# visualize.py
# Generates the predicted standings chart

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

TEAM_COLORS = {
    "Mercedes":      "#00d2be",
    "McLaren":       "#FF8000",
    "Ferrari":       "#E8002D",
    "Red Bull":      "#3671C6",
    "Aston Martin":  "#229971",
    "Alpine":        "#FF87BC",
    "Williams":      "#64C4FF",
    "Racing Bulls":  "#6692FF",
    "Audi":          "#ffffff",
    "Cadillac":      "#c8a4dc",
    "Haas":          "#B6BABD",
}

def plot_results(results, gbr, feature_cols, race_name):

    fig = plt.figure(figsize=(16, 10), facecolor="#0f0f13")
    gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

    ax1 = fig.add_subplot(gs[0, :])   # standings — full width
    ax2 = fig.add_subplot(gs[1, 0])   # feature importance
    ax3 = fig.add_subplot(gs[1, 1])   # quali gap vs predicted

    TEXT = "#e8e8e8"
    GRID = "#2a2a3a"

    for ax in (ax1, ax2, ax3):
        ax.set_facecolor("#16161e")
        ax.tick_params(colors=TEXT, labelsize=8)
        ax.xaxis.label.set_color(TEXT)
        ax.yaxis.label.set_color(TEXT)
        ax.title.set_color(TEXT)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID)

    # ── Chart 1: Predicted standings ──────────────────────────────────────
    from f1_2026_config import DRIVER_TO_TEAM
    colors = [
        TEAM_COLORS.get(DRIVER_TO_TEAM.get(d, ""), "#888888")
        for d in results["Driver"]
    ]

    bars = ax1.barh(
        results["Driver"][::-1],
        results["AdjustedTime_s"][::-1],
        color=colors[::-1],
        edgecolor="#000000",
        linewidth=0.5,
        height=0.65,
    )

    ax1.set_xlabel("Predicted Adjusted Lap Time (s)", color=TEXT)
    ax1.set_title(f"🏁 2026 {race_name} — Predicted Race Standings", color=TEXT, fontsize=12, pad=10)

    min_t = results["AdjustedTime_s"].min()
    ax1.set_xlim(min_t - 2, results["AdjustedTime_s"].max() + 2)

    medals = {0: "🥇", 1: "🥈", 2: "🥉"}
    for i, (bar, row) in enumerate(zip(bars, results[::-1].itertuples())):
        # Time label on bar
        ax1.text(
            bar.get_x() + bar.get_width() + 0.1,
            bar.get_y() + bar.get_height() / 2,
            f"{row.AdjustedTime_s:.3f}s",
            va="center", ha="left", color=TEXT, fontsize=7.5
        )
        # Medal/position label
        rev_idx = len(results) - 1 - list(results.itertuples()).index(
            list(results.itertuples())[len(results) - 1 - i]
        )
        label = medals.get(len(results) - 1 - i, f"P{len(results) - i}")
        ax1.text(min_t - 1.9, i, label, va="center", ha="left", color=TEXT, fontsize=8)

    ax1.grid(axis="x", color=GRID, linewidth=0.5)

    # ── Chart 2: Feature importance ───────────────────────────────────────
    imps = gbr.named_steps["model"].feature_importances_
    sorted_idx = np.argsort(imps)
    ax2.barh(
        [feature_cols[i] for i in sorted_idx],
        imps[sorted_idx],
        color="#4f8cff",
        edgecolor="#000",
        linewidth=0.4,
    )
    ax2.set_title("Feature Importance (GBR)", color=TEXT, fontsize=9)
    ax2.set_xlabel("Importance", color=TEXT)
    ax2.grid(axis="x", color=GRID, linewidth=0.4)

    # ── Chart 3: Quali gap vs predicted time ──────────────────────────────
    ax3.scatter(
        results["QualiGap_s"],
        results["AdjustedTime_s"],
        c=[TEAM_COLORS.get(DRIVER_TO_TEAM.get(d, ""), "#888") for d in results["Driver"]],
        s=100, edgecolors="#000", linewidths=0.5, zorder=3
    )
    for _, row in results.iterrows():
        ax3.annotate(
            row["Driver"],
            (row["QualiGap_s"], row["AdjustedTime_s"]),
            xytext=(4, 4), textcoords="offset points",
            fontsize=7, color=TEXT
        )
    ax3.set_xlabel("Qualifying Gap to Pole (s)", color=TEXT)
    ax3.set_ylabel("Predicted Adjusted Time (s)", color=TEXT)
    ax3.set_title("Quali Gap vs Predicted Race Pace", color=TEXT, fontsize=9)
    ax3.grid(color=GRID, linewidth=0.4)

    fig.suptitle(
        f"F1 2026 {race_name} Predictions  |  GBR + RF Ensemble  |  MAE ~0.595s",
        color=TEXT, fontsize=13, y=0.98, fontweight="bold"
    )

    filename = f"2026_{race_name.replace(' ', '_')}_prediction.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"\n  ✓ Chart saved → {filename}")