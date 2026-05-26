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

POSITIVE_COLOR = "#5B9B6B"
CONTROL_COLOR = "#4C78A8"
WARNING_COLOR = "#E6A23C"
NEGATIVE_COLOR = "#C96A5A"

GAME_STATE_COLORS = {
    "winning": POSITIVE_COLOR,
    "drawing": WARNING_COLOR,
    "losing": NEGATIVE_COLOR,
}

# =========================================================
# 2. LOAD DATA
# =========================================================

matches = pd.read_csv(DATA_DIR / "matches.csv")
goals = pd.read_csv(DATA_DIR / "goals.csv")

# =========================================================
# 3. DATASET OVERVIEW
# =========================================================

print("\nDATASET OVERVIEW")
print("----------------")

print(f"Matches: {matches.shape[0]}")
print(f"Goals: {goals.shape[0]}")
print(f"Teams: {len(set(matches['home_team']) | set(matches['away_team']))}")

print("\nMatches sample:")
print(matches.head())

print("\nGoals sample:")
print(goals.head())

# =========================================================
# 4. BASIC LEAGUE SUMMARY
# =========================================================

print("\nBASIC LEAGUE SUMMARY")
print("--------------------")

total_matches = matches.shape[0]
total_goals = goals.shape[0]
goals_per_match = total_goals / total_matches

draw_rate = (matches["winner"] == "Draw").mean()

print(f"Goals per match: {goals_per_match:.2f}")
print(f"Draw rate: {draw_rate:.2%}")

# =========================================================
# 5. GRAPH — GOALS BY MINUTE
# =========================================================

goals_by_minute = (
    goals["minute"]
    .value_counts()
    .sort_index()
)

plt.figure(figsize=(14, 5))

plt.plot(
    goals_by_minute.index,
    goals_by_minute.values,
    marker="o",
    linewidth=1.8,
    color=CONTROL_COLOR,
)

plt.title(
    "Liga F — Goals by minute",
    fontsize=20,
    weight="bold",
    pad=24,
)

plt.text(
    0.5,
    1.03,
    "Distribution of goals across match time",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11,
    alpha=0.75,
)

plt.xlabel("Minute")
plt.ylabel("Goals")

plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)

plt.savefig(
    FIGURES_DIR / "00_goals_by_minute.png",
    dpi=300,
)

plt.close()

print("Saved: outputs/figures/00_goals_by_minute.png")

# =========================================================
# 6. GRAPH — GOALS BY GAME STATE BEFORE
# =========================================================

game_state_counts = (
    goals["game_state_before"]
    .value_counts()
    .reindex(["drawing", "winning", "losing"])
)

print("\nGOALS BY GAME STATE BEFORE")
print("--------------------------")
print(game_state_counts)

plt.figure(figsize=(8, 5))

colors = [
    GAME_STATE_COLORS[state]
    for state in game_state_counts.index
]

plt.bar(
    game_state_counts.index,
    game_state_counts.values,
    color=colors,
)

for state, value in game_state_counts.items():
    plt.text(
        state,
        value + 3,
        str(int(value)),
        ha="center",
        fontsize=10,
    )

plt.title(
    "Liga F — Goals by game state before",
    fontsize=20,
    weight="bold",
    pad=24,
)

plt.text(
    0.5,
    1.04,
    "Whether teams were drawing, winning or losing before scoring",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11,
    alpha=0.75,
)

plt.xlabel("Game state before goal")
plt.ylabel("Goals")

plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)

plt.savefig(
    FIGURES_DIR / "00_goals_by_game_state_before.png",
    dpi=300,
)

plt.close()

print("Saved: outputs/figures/00_goals_by_game_state_before.png")

# =========================================================
# 7. GRAPH — LATE GOALS BY TEAM
# =========================================================

late_goal_rate = goals["is_late_goal"].mean()

late_goals_by_team = (
    goals[goals["is_late_goal"]]
    .groupby("scoring_team")
    .size()
    .sort_values()
)

print("\nLATE GOALS")
print("----------")

print(f"Late goal rate: {late_goal_rate:.2%}")

print("\nLate goals by team:")
print(late_goals_by_team.sort_values(ascending=False))

plt.figure(figsize=(12, 8))

q25 = late_goals_by_team.quantile(0.25)
q75 = late_goals_by_team.quantile(0.75)

colors = []

for value in late_goals_by_team.values:

    if value >= q75:
        colors.append(POSITIVE_COLOR)

    elif value <= q25:
        colors.append(NEGATIVE_COLOR)

    else:
        colors.append(WARNING_COLOR)

plt.barh(
    late_goals_by_team.index,
    late_goals_by_team.values,
    color=colors,
)

for team, value in late_goals_by_team.items():
    plt.text(
        value + 0.2,
        team,
        str(int(value)),
        va="center",
        fontsize=9,
    )

plt.title(
    "Liga F — Late goals by team",
    fontsize=20,
    weight="bold",
    pad=28,
)

plt.text(
    0.5,
    1.015,
    f"Late goals represent {late_goal_rate:.1%} of all goals in the dataset",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11,
    alpha=0.75,
)

plt.xlabel("Late goals")
plt.ylabel("Team")

plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)

plt.savefig(
    FIGURES_DIR / "00_late_goals_by_team.png",
    dpi=300,
)

plt.close()

print("Saved: outputs/figures/00_late_goals_by_team.png")


# =========================================================
# 8. EXPORT SUMMARY TABLES
# =========================================================

matches_with_first_goal = matches.dropna(
    subset=["first_goal_team"]
).copy()

opening_goal_counts = (
    matches_with_first_goal["first_goal_team"]
    .value_counts()
    .sort_values()
)

matches_with_first_goal["scored_first_won"] = (
    matches_with_first_goal["first_goal_team"]
    == matches_with_first_goal["winner"]
)

scoring_first_summary = (
    matches_with_first_goal
    .groupby("first_goal_team")
    .agg(
        matches_scored_first=("match_id", "count"),
        wins_after_scoring_first=("scored_first_won", "sum"),
    )
)

scoring_first_summary["win_rate_after_scoring_first"] = (
    scoring_first_summary["wins_after_scoring_first"]
    / scoring_first_summary["matches_scored_first"]
)

scoring_first_summary = scoring_first_summary.sort_values(
    "win_rate_after_scoring_first"
)

scoring_first_summary.to_csv(
    TABLES_DIR / "basic_scoring_first_summary.csv"
)

late_goals_by_team.to_csv(
    TABLES_DIR / "late_goals_by_team.csv",
    header=["late_goals"]
)

print("\nSaved summary tables in outputs/tables/")

# =========================================================
# 11. PRINT OUTPUTS
# =========================================================

print("\nSaved figures:")
print("outputs/figures/00_goals_by_minute.png")
print("outputs/figures/00_goals_by_game_state_before.png")
print("outputs/figures/00_late_goals_by_team.png")

print("\nDONE")