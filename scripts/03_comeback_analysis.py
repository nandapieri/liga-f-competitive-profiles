from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

# =========================================================
# 1. CONFIG
# =========================================================

DATA_DIR = Path("data/processed")

FIGURES_DIR = Path("outputs/figures")
TABLES_DIR = Path("outputs/tables")

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

MIN_CONCEDED_FIRST_MATCHES = 8

POSITIVE_COLOR = "#5B9B6B"   # green
CONTROL_COLOR = "#4C78A8"    # blue
WARNING_COLOR = "#E6A23C"    # yellow/orange
NEGATIVE_COLOR = "#C96A5A"   # red
NEUTRAL_COLOR = "#8C8C8C"    # grey

OUTCOME_COLORS = {
    "Win": POSITIVE_COLOR,
    "Draw": WARNING_COLOR,
    "Loss": NEGATIVE_COLOR,
}

# =========================================================
# 2. LOAD DATA
# =========================================================

matches = pd.read_csv(DATA_DIR / "matches.csv")

# =========================================================
# 3. PREPARE DATA
# =========================================================

matches = matches.dropna(subset=["first_goal_team"]).copy()

matches["conceded_first_team"] = matches.apply(
    lambda row:
    row["away_team"]
    if row["first_goal_team"] == row["home_team"]
    else row["home_team"],
    axis=1,
)

matches["conceded_first_won"] = (
    matches["conceded_first_team"] == matches["winner"]
)

matches["conceded_first_drew"] = (
    matches["winner"] == "Draw"
)

matches["conceded_first_lost"] = (
    (~matches["conceded_first_won"])
    &
    (~matches["conceded_first_drew"])
)

matches["points_after_conceding_first"] = (
    matches["conceded_first_won"].astype(int) * 3
    +
    matches["conceded_first_drew"].astype(int)
)

# =========================================================
# 4. SUMMARY TABLE
# =========================================================

summary = (
    matches
    .groupby("conceded_first_team")
    .agg(
        matches_conceded_first=("match_id", "count"),
        wins=("conceded_first_won", "sum"),
        draws=("conceded_first_drew", "sum"),
        losses=("conceded_first_lost", "sum"),
        points=("points_after_conceding_first", "sum"),
    )
)

summary["max_points"] = summary["matches_conceded_first"] * 3
summary["points_lost"] = summary["max_points"] - summary["points"]

summary["win_rate"] = summary["wins"] / summary["matches_conceded_first"]
summary["draw_rate"] = summary["draws"] / summary["matches_conceded_first"]
summary["loss_rate"] = summary["losses"] / summary["matches_conceded_first"]

summary["points_recovery_rate"] = (
    summary["points"] / summary["max_points"]
)

summary["points_per_match_after_conceding_first"] = (
    summary["points"] / summary["matches_conceded_first"]
)

summary = summary.sort_values(
    "points_recovery_rate",
    ascending=False,
)

summary.to_csv(
    TABLES_DIR / "comeback_summary.csv"
)

recovery_mean = summary["points_recovery_rate"].mean()
recovery_median = summary["points_recovery_rate"].median()
conceded_mean = summary["matches_conceded_first"].mean()

# =========================================================
# 5. GRAPH — RESILIENCE MAP
# =========================================================

plt.figure(figsize=(12, 8))

scatter_colors = []

for _, row in summary.iterrows():

    if row["points_recovery_rate"] >= recovery_mean:
        scatter_colors.append(POSITIVE_COLOR)

    elif row["matches_conceded_first"] <= conceded_mean:
        scatter_colors.append(CONTROL_COLOR)

    elif row["points_recovery_rate"] >= recovery_median:
        scatter_colors.append(WARNING_COLOR)

    else:
        scatter_colors.append(NEGATIVE_COLOR)

plt.scatter(
    summary["matches_conceded_first"],
    summary["points_recovery_rate"],

    s=summary["matches_conceded_first"] * 35,

    alpha=0.75,
    color=scatter_colors,

    edgecolor="white",
    linewidth=1.2,
)

highlight_teams = {
    "Barcelona": (0.25, 0.00),
    "Real Sociedad": (0.25, 0.00),
    "Deportivo La Coruna": (0.25, 0.00),
    "Levante": (0.25, 0.00),
    "Alhama CF": (0.25, 0.015),
}

for team, row in summary.iterrows():

    if team in highlight_teams:

        x_offset, y_offset = highlight_teams[team]

        plt.text(
            row["matches_conceded_first"] + x_offset,
            row["points_recovery_rate"] + y_offset,
            team,
            fontsize=10,
            weight="bold",
            va="center",
        )

plt.axhline(
    recovery_mean,
    linestyle="--",
    linewidth=1,
    alpha=0.4,
    color="black",
)

plt.axvline(
    conceded_mean,
    linestyle="--",
    linewidth=1,
    alpha=0.4,
    color="black",
)

plt.text(
    summary["matches_conceded_first"].max() - 0.5,
    0.58,
    "High recovery",
    fontsize=11,
    ha="right",
    alpha=0.7,
)

plt.text(
    22.5,
    0.085,
    "Frequent setbacks\nlow recovery",
    fontsize=11,
    ha="center",
    alpha=0.7,
)

plt.title(
    "Liga F — Resilience after conceding first",
    fontsize=20,
    weight="bold",
    pad=30,
)

plt.text(
    0.5,
    1.03,
    "How often teams concede first vs their ability to recover points",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11,
    alpha=0.75,
)

plt.xlabel("Matches conceding first")
plt.ylabel("Points recovery rate (%)")

plt.ylim(-0.02, 0.65)

ax = plt.gca()
ax.yaxis.set_major_formatter(PercentFormatter(1))

plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)

plt.savefig(
    FIGURES_DIR / "09_resilience_map_conceding_first.png",
    dpi=300,
)

plt.close()

# =========================================================
# 6. GRAPH — OUTCOME AFTER CONCEDING FIRST
# =========================================================

plot_df = summary.sort_values("points_recovery_rate")

plt.figure(figsize=(13, 8))

plt.barh(
    plot_df.index,
    plot_df["win_rate"],
    label="Win",
    color=OUTCOME_COLORS["Win"],
)

plt.barh(
    plot_df.index,
    plot_df["draw_rate"],
    left=plot_df["win_rate"],
    label="Draw",
    color=OUTCOME_COLORS["Draw"],
)

plt.barh(
    plot_df.index,
    plot_df["loss_rate"],
    left=plot_df["win_rate"] + plot_df["draw_rate"],
    label="Loss",
    color=OUTCOME_COLORS["Loss"],
)

plt.title(
    "Liga F — Result after conceding first",
    fontsize=20,
    weight="bold",
    pad=30,
)

plt.text(
    0.5,
    1.03,
    "Who can recover after the first setback?",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11,
    alpha=0.75,
)

plt.xlabel("Share of matches after conceding first (%)")
plt.ylabel("Team")

ax = plt.gca()
ax.xaxis.set_major_formatter(PercentFormatter(1))

plt.legend(
    title="Outcome",
    loc="center left",
    bbox_to_anchor=(1.02, 0.5),
    frameon=False,
)

plt.tight_layout(
    rect=[0, 0, 0.86, 0.94]
)

plt.savefig(
    FIGURES_DIR / "10_outcome_after_conceding_first.png",
    dpi=300,
)

plt.close()

# =========================================================
# 7. GRAPH — POINTS RECOVERED
# =========================================================

recovered_df = summary.sort_values("points")

plt.figure(figsize=(12, 8))

colors = []

for _, row in recovered_df.iterrows():

    if row["points"] >= recovered_df["points"].quantile(0.75):
        colors.append(POSITIVE_COLOR)

    elif row["points"] >= recovered_df["points"].median():
        colors.append(WARNING_COLOR)

    else:
        colors.append(NEGATIVE_COLOR)

plt.barh(
    recovered_df.index,
    recovered_df["points"],
    color=colors,
)

for team, row in recovered_df.iterrows():
    plt.text(
        row["points"] + 0.2,
        team,
        f"{int(row['points'])} pts",
        va="center",
        fontsize=9,
    )

plt.title(
    "Liga F — Points recovered after conceding first",
    fontsize=20,
    weight="bold",
    pad=30,
)

plt.text(
    0.5,
    1.03,
    "A simple view of comeback capacity",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11,
    alpha=0.75,
)

plt.xlabel("Points recovered")
plt.ylabel("Team")

plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)

plt.savefig(
    FIGURES_DIR / "11_points_recovered_after_conceding_first.png",
    dpi=300,
)

plt.close()

# =========================================================
# 8. GRAPH — RECOVERY RANKING
# =========================================================

ranking_df = summary.sort_values("points_recovery_rate")

plt.figure(figsize=(12, 8))

colors = [
    POSITIVE_COLOR if value >= recovery_mean
    else NEGATIVE_COLOR
    for value in ranking_df["points_recovery_rate"]
]

plt.barh(
    ranking_df.index,
    ranking_df["points_recovery_rate"] * 100,
    color=colors,
)

for team, row in ranking_df.iterrows():
    label = (
        f"{row['points_recovery_rate'] * 100:.0f}%"
        f"  ({int(row['matches_conceded_first'])}x)"
    )

    plt.text(
        row["points_recovery_rate"] * 100 + 1,
        team,
        label,
        va="center",
        fontsize=9,
    )

plt.title(
    "Liga F — Recovery after conceding first",
    fontsize=20,
    weight="bold",
    pad=30,
)

plt.text(
    0.5,
    1.03,
    "Points recovered from the maximum possible after conceding first",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11,
    alpha=0.75,
)

plt.xlabel("Points recovery (%)")
plt.ylabel("Team")
plt.xlim(0, 70)

plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)

plt.savefig(
    FIGURES_DIR / "12_recovery_ranking_after_conceding_first.png",
    dpi=300,
)

plt.close()

# =========================================================
# 9. GRAPH — FILTERED RECOVERY RANKING
# =========================================================

filtered = summary[
    summary["matches_conceded_first"] >= MIN_CONCEDED_FIRST_MATCHES
].copy()

filtered = filtered.sort_values("points_recovery_rate")

plt.figure(figsize=(12, 8))

colors = [
    POSITIVE_COLOR if value >= recovery_mean
    else NEGATIVE_COLOR
    for value in filtered["points_recovery_rate"]
]

plt.barh(
    filtered.index,
    filtered["points_recovery_rate"] * 100,
    color=colors,
)

for team, row in filtered.iterrows():
    label = (
        f"{row['points_recovery_rate'] * 100:.0f}%"
        f"  ({int(row['matches_conceded_first'])}x)"
    )

    plt.text(
        row["points_recovery_rate"] * 100 + 1,
        team,
        label,
        va="center",
        fontsize=9,
    )

plt.title(
    f"Liga F — Recovery after conceding first "
    f"(min. {MIN_CONCEDED_FIRST_MATCHES} matches)",
    fontsize=20,
    weight="bold",
    pad=30,
)

plt.text(
    0.5,
    1.03,
    "Filtered view to reduce small-sample distortion",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11,
    alpha=0.75,
)

plt.xlabel("Points recovery (%)")
plt.ylabel("Team")
plt.xlim(0, 70)

plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)

plt.savefig(
    FIGURES_DIR / "13_conceding_first_filtered_ranking.png",
    dpi=300,
)

plt.close()

# =========================================================
# 10. GRAPH — MATCHES CONCEDED FIRST
# =========================================================

conceded_first = (
    summary["matches_conceded_first"]
    .sort_values()
)

plt.figure(figsize=(12, 8))

q25 = conceded_first.quantile(0.25)
q75 = conceded_first.quantile(0.75)

colors = []

for value in conceded_first.values:

    if value <= q25:
        colors.append(POSITIVE_COLOR)

    elif value >= q75:
        colors.append(NEGATIVE_COLOR)

    else:
        colors.append(WARNING_COLOR)

plt.barh(
    conceded_first.index,
    conceded_first.values,
    color=colors,
)

for team, value in conceded_first.items():
    plt.text(
        value + 0.2,
        team,
        str(int(value)),
        va="center",
        fontsize=9,
    )

plt.title(
    "Liga F — Matches conceding first by team",
    fontsize=20,
    weight="bold",
    pad=30,
)

plt.text(
    0.5,
    1.03,
    "Frequency of starting matches from a negative game state",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11,
    alpha=0.75,
)

plt.xlabel("Matches conceding first")
plt.ylabel("Team")

plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)

plt.savefig(
    FIGURES_DIR / "14_matches_conceding_first_by_team.png",
    dpi=300,
)

plt.close()

# =========================================================
# 11. PRINT OUTPUTS
# =========================================================

print("\nSaved figures:")
print("outputs/figures/09_resilience_map_conceding_first.png")
print("outputs/figures/10_outcome_after_conceding_first.png")
print("outputs/figures/11_points_recovered_after_conceding_first.png")
print("outputs/figures/12_recovery_ranking_after_conceding_first.png")
print("outputs/figures/13_conceding_first_filtered_ranking.png")
print("outputs/figures/14_matches_conceding_first_by_team.png")

print("\nSaved table:")
print("outputs/tables/comeback_summary.csv")

print("\nDONE")