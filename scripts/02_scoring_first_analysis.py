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

MIN_SCORED_FIRST_MATCHES = 8

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

matches["scored_first_won"] = (
    matches["first_goal_team"] == matches["winner"]
)

matches["scored_first_drew"] = (
    matches["winner"] == "Draw"
)

matches["scored_first_lost"] = (
    (~matches["scored_first_won"])
    &
    (~matches["scored_first_drew"])
)

matches["points_after_scoring_first"] = (
    matches["scored_first_won"].astype(int) * 3
    +
    matches["scored_first_drew"].astype(int)
)

# =========================================================
# 4. SUMMARY TABLE
# =========================================================

summary = (
    matches
    .groupby("first_goal_team")
    .agg(
        matches_scored_first=("match_id", "count"),
        wins=("scored_first_won", "sum"),
        draws=("scored_first_drew", "sum"),
        losses=("scored_first_lost", "sum"),
        points=("points_after_scoring_first", "sum"),
    )
)

summary["max_points"] = summary["matches_scored_first"] * 3
summary["points_dropped"] = summary["max_points"] - summary["points"]

summary["win_rate"] = summary["wins"] / summary["matches_scored_first"]
summary["draw_rate"] = summary["draws"] / summary["matches_scored_first"]
summary["loss_rate"] = summary["losses"] / summary["matches_scored_first"]
summary["points_retention"] = summary["points"] / summary["max_points"]

summary = summary.sort_values(
    "points_retention",
    ascending=False
)

summary.to_csv(
    TABLES_DIR / "scoring_first_summary.csv"
)

retention_mean = summary["points_retention"].mean()
retention_median = summary["points_retention"].median()
scored_first_mean = summary["matches_scored_first"].mean()

# =========================================================
# 5. GRAPH — CONTROL MAP
# =========================================================

plt.figure(figsize=(12, 8))

scatter_colors = []

for _, row in summary.iterrows():

    if row["points_retention"] >= retention_mean:
        scatter_colors.append(POSITIVE_COLOR)

    elif row["matches_scored_first"] >= scored_first_mean:
        scatter_colors.append(CONTROL_COLOR)

    elif row["points_retention"] >= retention_median:
        scatter_colors.append(WARNING_COLOR)

    else:
        scatter_colors.append(NEGATIVE_COLOR)

plt.scatter(
    summary["matches_scored_first"],
    summary["points_retention"],

    s=summary["matches_scored_first"] * 35,

    alpha=0.75,
    color=scatter_colors,

    edgecolor="white",
    linewidth=1.2,
)

highlight_teams = {
    "Barcelona": (0.25, 0.00),
    "Real Madrid": (0.25, 0.00),
    "Real Sociedad": (0.25, 0.00),
    "Sevilla": (0.25, 0.00),
    "Eibar": (0.25, 0.00),
    "Alhama CF": (0.25, 0.00),
}

for team, row in summary.iterrows():

    if team in highlight_teams:

        x_offset, y_offset = highlight_teams[team]

        plt.text(
            row["matches_scored_first"] + x_offset,
            row["points_retention"] + y_offset,
            team,
            fontsize=10,
            weight="bold",
            va="center",
        )

plt.axhline(
    retention_mean,
    linestyle="--",
    linewidth=1,
    alpha=0.4,
    color="black",
)

plt.axvline(
    scored_first_mean,
    linestyle="--",
    linewidth=1,
    alpha=0.4,
    color="black",
)

plt.text(
    summary["matches_scored_first"].max() - 0.5,
    1.04,
    "Frequent control\nhigh retention",
    fontsize=11,
    ha="right",
    alpha=0.7,
)

plt.text(
    10.5,
    0.58,
    "Fragile after\nscoring first",
    fontsize=11,
    alpha=0.7,
)

plt.title(
    "Liga F — Control after scoring first",
    fontsize=20,
    weight="bold",
    pad=30,
)

plt.text(
    0.5,
    1.03,
    "Frequency of opening goals vs ability to convert them into points",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11,
    alpha=0.75,
)

plt.xlabel("Matches scoring first")
plt.ylabel("Points retention after scoring first (%)")

plt.ylim(0.25, 1.08)

ax = plt.gca()
ax.yaxis.set_major_formatter(PercentFormatter(1))

plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)

plt.savefig(
    FIGURES_DIR / "01_control_map_scoring_first.png",
    dpi=300,
)

plt.close()

# =========================================================
# 6. GRAPH — OUTCOME AFTER SCORING FIRST
# =========================================================

plot_df = summary.sort_values("points_retention")

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
    "Liga F — Result after scoring first",
    fontsize=20,
    weight="bold",
    pad=30,
)

plt.text(
    0.5,
    1.03,
    "Some teams turn the first goal into control; others leave the match open",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11,
    alpha=0.75,
)

plt.xlabel("Share of matches after scoring first (%)")
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
    FIGURES_DIR / "02_outcome_after_scoring_first.png",
    dpi=300,
)

plt.close()

# =========================================================
# 7. GRAPH — POINTS DROPPED
# =========================================================

dropped_df = summary.sort_values("points_dropped")

plt.figure(figsize=(12, 8))

q25 = dropped_df["points_dropped"].quantile(0.25)
q75 = dropped_df["points_dropped"].quantile(0.75)

colors = []

for value in dropped_df["points_dropped"]:

    if value <= q25:
        colors.append(POSITIVE_COLOR)

    elif value >= q75:
        colors.append(NEGATIVE_COLOR)

    else:
        colors.append(WARNING_COLOR)

plt.barh(
    dropped_df.index,
    dropped_df["points_dropped"],
    color=colors,
)

for team, row in dropped_df.iterrows():
    plt.text(
        row["points_dropped"] + 0.2,
        team,
        f"{int(row['points_dropped'])} pts",
        va="center",
        fontsize=9,
    )

plt.title(
    "Liga F — Points dropped after scoring first",
    fontsize=20,
    weight="bold",
    pad=30,
)

plt.text(
    0.5,
    1.03,
    "A simple view of fragility after taking the lead",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11,
    alpha=0.75,
)

plt.xlabel("Points dropped")
plt.ylabel("Team")

plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)

plt.savefig(
    FIGURES_DIR / "03_points_dropped_after_scoring_first.png",
    dpi=300,
)

plt.close()

# =========================================================
# 8. GRAPH — STABILITY RANKING
# =========================================================

ranking_df = summary.sort_values("points_retention")

plt.figure(figsize=(12, 8))

colors = [
    POSITIVE_COLOR if value >= retention_mean
    else NEGATIVE_COLOR
    for value in ranking_df["points_retention"]
]

plt.barh(
    ranking_df.index,
    ranking_df["points_retention"] * 100,
    color=colors,
)

for team, row in ranking_df.iterrows():
    label = (
        f"{row['points_retention'] * 100:.0f}%"
        f"  ({int(row['matches_scored_first'])}x)"
    )

    plt.text(
        row["points_retention"] * 100 + 1,
        team,
        label,
        va="center",
        fontsize=9,
    )

plt.title(
    "Liga F — Stability after scoring first",
    fontsize=20,
    weight="bold",
    pad=30,
)

plt.text(
    0.5,
    1.03,
    "Points retained from the maximum possible after opening the score",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11,
    alpha=0.75,
)

plt.xlabel("Points retention (%)")
plt.ylabel("Team")
plt.xlim(0, 110)

plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)

plt.savefig(
    FIGURES_DIR / "04_stability_ranking_after_scoring_first.png",
    dpi=300,
)

plt.close()

# =========================================================
# 9. GRAPH — OPENING GOALS BY TEAM
# =========================================================

opening_goals = (
    summary["matches_scored_first"]
    .sort_values()
)

plt.figure(figsize=(12, 8))

q25 = opening_goals.quantile(0.25)
q75 = opening_goals.quantile(0.75)

colors = []

for value in opening_goals.values:

    if value >= q75:
        colors.append(POSITIVE_COLOR)

    elif value <= q25:
        colors.append(NEGATIVE_COLOR)

    else:
        colors.append(WARNING_COLOR)

plt.barh(
    opening_goals.index,
    opening_goals.values,
    color=colors,
)

for team, value in opening_goals.items():
    plt.text(
        value + 0.2,
        team,
        str(int(value)),
        va="center",
        fontsize=9,
    )

plt.title(
    "Liga F — Opening goals by team",
    fontsize=20,
    weight="bold",
    pad=30,
)

plt.text(
    0.5,
    1.03,
    "Frequency of starting matches from a positive game state",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11,
    alpha=0.75,
)

plt.xlabel("Matches scoring first")
plt.ylabel("Team")

plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)

plt.savefig(
    FIGURES_DIR / "05_opening_goals_by_team.png",
    dpi=300,
)

plt.close()

# =========================================================
# 10. GRAPH — WIN RATE AFTER SCORING FIRST
# =========================================================

win_rate_df = summary.sort_values("win_rate")

plt.figure(figsize=(12, 8))

colors = [
    POSITIVE_COLOR if value >= summary["win_rate"].mean()
    else NEGATIVE_COLOR
    for value in win_rate_df["win_rate"]
]

plt.barh(
    win_rate_df.index,
    win_rate_df["win_rate"] * 100,
    color=colors,
)

for team, row in win_rate_df.iterrows():
    label = (
        f"{row['win_rate'] * 100:.0f}%"
        f"  ({int(row['matches_scored_first'])}x)"
    )

    plt.text(
        row["win_rate"] * 100 + 1,
        team,
        label,
        va="center",
        fontsize=9,
    )

plt.title(
    "Liga F — Win rate after scoring first",
    fontsize=20,
    weight="bold",
    pad=30,
)

plt.text(
    0.5,
    1.03,
    "How often teams convert the first goal into a win",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11,
    alpha=0.75,
)

plt.xlabel("Win rate after scoring first (%)")
plt.ylabel("Team")
plt.xlim(0, 110)

plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)

plt.savefig(
    FIGURES_DIR / "06_win_rate_after_scoring_first.png",
    dpi=300,
)

plt.close()

# =========================================================
# 11. GRAPH — FILTERED STABILITY RANKING
# =========================================================

filtered = summary[
    summary["matches_scored_first"] >= MIN_SCORED_FIRST_MATCHES
].copy()

filtered = filtered.sort_values("points_retention")

plt.figure(figsize=(12, 8))

colors = [
    POSITIVE_COLOR if value >= retention_mean
    else NEGATIVE_COLOR
    for value in filtered["points_retention"]
]

plt.barh(
    filtered.index,
    filtered["points_retention"] * 100,
    color=colors,
)

for team, row in filtered.iterrows():
    label = (
        f"{row['points_retention'] * 100:.0f}%"
        f"  ({int(row['matches_scored_first'])}x)"
    )

    plt.text(
        row["points_retention"] * 100 + 1,
        team,
        label,
        va="center",
        fontsize=9,
    )

plt.title(
    f"Liga F — Stability after scoring first "
    f"(min. {MIN_SCORED_FIRST_MATCHES} matches)",
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

plt.xlabel("Points retention (%)")
plt.ylabel("Team")
plt.xlim(0, 110)

plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)

plt.savefig(
    FIGURES_DIR / "07_scoring_first_filtered_ranking.png",
    dpi=300,
)

plt.close()

# =========================================================
# 12. GRAPH — LOSSES AFTER SCORING FIRST
# =========================================================

losses_df = summary.sort_values("losses")

plt.figure(figsize=(12, 8))

q25 = losses_df["losses"].quantile(0.25)
q75 = losses_df["losses"].quantile(0.75)

colors = []

for value in losses_df["losses"]:

    if value <= q25:
        colors.append(POSITIVE_COLOR)

    elif value >= q75:
        colors.append(NEGATIVE_COLOR)

    else:
        colors.append(WARNING_COLOR)

plt.barh(
    losses_df.index,
    losses_df["losses"],
    color=colors,
)

for team, row in losses_df.iterrows():
    plt.text(
        row["losses"] + 0.08,
        team,
        str(int(row["losses"])),
        va="center",
        fontsize=9,
    )

plt.title(
    "Liga F — Matches lost after scoring first",
    fontsize=20,
    weight="bold",
    pad=30,
)

plt.text(
    0.5,
    1.03,
    "How often teams lose after opening the score",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11,
    alpha=0.75,
)

plt.xlabel("Losses after scoring first")
plt.ylabel("Team")

plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)

plt.savefig(
    FIGURES_DIR / "08_losses_after_scoring_first.png",
    dpi=300,
)

plt.close()

# =========================================================
# 13. PRINT OUTPUTS
# =========================================================

print("\nSaved figures:")
print("outputs/figures/01_control_map_scoring_first.png")
print("outputs/figures/02_outcome_after_scoring_first.png")
print("outputs/figures/03_points_dropped_after_scoring_first.png")
print("outputs/figures/04_stability_ranking_after_scoring_first.png")
print("outputs/figures/05_opening_goals_by_team.png")
print("outputs/figures/06_win_rate_after_scoring_first.png")
print("outputs/figures/07_scoring_first_filtered_ranking.png")
print("outputs/figures/08_losses_after_scoring_first.png")

print("\nSaved table:")
print("outputs/tables/scoring_first_summary.csv")

print("\nDONE")