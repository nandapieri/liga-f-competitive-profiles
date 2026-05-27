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

POSITIVE_COLOR = "#5B9B6B"   # stable / positive
CONTROL_COLOR = "#4C78A8"    # control-oriented
WARNING_COLOR = "#E6A23C"    # reactive / unstable
NEGATIVE_COLOR = "#C96A5A"   # chaotic / fragile

# =========================================================
# 2. LOAD DATA
# =========================================================

matches = pd.read_csv(DATA_DIR / "matches.csv")
goals = pd.read_csv(DATA_DIR / "goals.csv")

# =========================================================
# 3. HELPER FUNCTIONS
# =========================================================

def get_leader(home_score, away_score, home_team, away_team):

    if home_score > away_score:
        return home_team

    if away_score > home_score:
        return away_team

    return "Draw"


def opponent_team(team, home_team, away_team):

    if team == home_team:
        return away_team

    return home_team


# =========================================================
# 4. BUILD MATCH-LEVEL VOLATILITY TABLE
# =========================================================

match_rows = []
team_rows = []

for _, match in matches.iterrows():

    match_id = match["match_id"]
    home_team = match["home_team"]
    away_team = match["away_team"]

    match_goals = (
        goals[goals["match_id"] == match_id]
        .sort_values("minute")
        .copy()
    )

    leaders_sequence = []

    equalizers = 0
    late_goals = 0

    for _, goal in match_goals.iterrows():

        home_after = goal["home_score_after"]
        away_after = goal["away_score_after"]

        new_leader = get_leader(
            home_after,
            away_after,
            home_team,
            away_team,
        )

        leaders_sequence.append(new_leader)

        if goal["is_equalizer"]:
            equalizers += 1

        if goal["is_late_goal"]:
            late_goals += 1

    # Count leader changes while ignoring draw states.
    # Example: Team A -> Draw -> Team B counts as one lead change.
    non_draw_leaders = [
        leader
        for leader in leaders_sequence
        if leader != "Draw"
    ]

    lead_changes = 0

    for i in range(1, len(non_draw_leaders)):

        if non_draw_leaders[i] != non_draw_leaders[i - 1]:
            lead_changes += 1

    final_winner = match["winner"]

    comeback_occurred = (
        lead_changes > 0
        or (
            pd.notna(match["first_goal_team"])
            and match["first_goal_team"] != final_winner
            and final_winner != "Draw"
        )
    )

    chaos_score = (
        equalizers
        + lead_changes * 2
        + late_goals
        + int(comeback_occurred)
    )

    match_rows.append(
        {
            "match_id": match_id,
            "round": match["round"],
            "date": match["date"],
            "home_team": home_team,
            "away_team": away_team,
            "winner": final_winner,
            "total_goals": len(match_goals),
            "equalizers": equalizers,
            "lead_changes": lead_changes,
            "late_goals": late_goals,
            "comeback_occurred": comeback_occurred,
            "chaos_score": chaos_score,
        }
    )

    # =====================================================
    # TEAM-LEVEL PARTICIPATION IN MATCH VOLATILITY
    # =====================================================

    for team in [home_team, away_team]:

        team_rows.append(
            {
                "match_id": match_id,
                "team": team,
                "opponent": opponent_team(team, home_team, away_team),
                "round": match["round"],
                "date": match["date"],
                "chaos_score": chaos_score,
                "match_had_equalizer": equalizers > 0,
                "match_had_lead_change": lead_changes > 0,
                "match_had_late_goal": late_goals > 0,
                "match_had_comeback": comeback_occurred,
            }
        )

# =========================================================
# 5. CREATE DATAFRAMES
# =========================================================

volatility_matches = pd.DataFrame(match_rows)
volatility_teams = pd.DataFrame(team_rows)

# =========================================================
# 6. TEAM SUMMARY
# =========================================================

team_summary = (
    volatility_teams
    .groupby("team")
    .agg(
        matches=("match_id", "count"),
        avg_chaos_score=("chaos_score", "mean"),
        total_chaos_score=("chaos_score", "sum"),
        matches_with_equalizer=("match_had_equalizer", "sum"),
        matches_with_lead_change=("match_had_lead_change", "sum"),
        matches_with_late_goal=("match_had_late_goal", "sum"),
        matches_with_comeback=("match_had_comeback", "sum"),
    )
)

team_summary["equalizer_match_rate"] = (
    team_summary["matches_with_equalizer"] / team_summary["matches"]
)

team_summary["lead_change_match_rate"] = (
    team_summary["matches_with_lead_change"] / team_summary["matches"]
)

team_summary["late_goal_match_rate"] = (
    team_summary["matches_with_late_goal"] / team_summary["matches"]
)

team_summary["comeback_match_rate"] = (
    team_summary["matches_with_comeback"] / team_summary["matches"]
)

team_summary = team_summary.sort_values(
    "avg_chaos_score",
    ascending=False,
)

# =========================================================
# 7. EXPORT TABLES
# =========================================================

volatility_matches.to_csv(
    TABLES_DIR / "volatility_matches.csv",
    index=False,
)

volatility_teams.to_csv(
    TABLES_DIR / "volatility_teams.csv",
    index=False,
)

team_summary.to_csv(
    TABLES_DIR / "volatility_team_summary.csv",
)

# =========================================================
# 8. GRAPH — CHAOS SCORE BY TEAM
# =========================================================

plot_df = team_summary.sort_values("avg_chaos_score")

plt.figure(figsize=(12, 8))

q25 = plot_df["avg_chaos_score"].quantile(0.25)
q75 = plot_df["avg_chaos_score"].quantile(0.75)

colors = []

for value in plot_df["avg_chaos_score"]:

    if value <= q25:
        colors.append(POSITIVE_COLOR)

    elif value >= q75:
        colors.append(NEGATIVE_COLOR)

    else:
        colors.append(WARNING_COLOR)

plt.barh(
    plot_df.index,
    plot_df["avg_chaos_score"],
    color=colors,
)

for team, row in plot_df.iterrows():

    plt.text(
        row["avg_chaos_score"] + 0.05,
        team,
        f"{row['avg_chaos_score']:.2f}",
        va="center",
        fontsize=9,
    )

plt.title(
    "Liga F — Average match chaos by team",
    fontsize=20,
    weight="bold",
    pad=30,
)

plt.text(
    0.5,
    1.03,
    "A higher score indicates more equalizers, lead changes, late goals and comeback dynamics",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11,
    alpha=0.75,
)

plt.xlabel("Average chaos score")
plt.ylabel("Team")

plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)

plt.savefig(
    FIGURES_DIR / "19_avg_match_chaos_by_team.png",
    dpi=300,
)

plt.close()

# =========================================================
# 9. GRAPH — LEAD CHANGE MATCH RATE
# =========================================================

plot_df = team_summary.sort_values("lead_change_match_rate")

plt.figure(figsize=(12, 8))

q25 = plot_df["lead_change_match_rate"].quantile(0.25)
q75 = plot_df["lead_change_match_rate"].quantile(0.75)

colors = []

for value in plot_df["lead_change_match_rate"]:

    if value <= q25:
        colors.append(POSITIVE_COLOR)

    elif value >= q75:
        colors.append(NEGATIVE_COLOR)

    else:
        colors.append(WARNING_COLOR)

plt.barh(
    plot_df.index,
    plot_df["lead_change_match_rate"] * 100,
    color=colors,
)

for team, row in plot_df.iterrows():

    plt.text(
        row["lead_change_match_rate"] * 100 + 1,
        team,
        f"{row['lead_change_match_rate'] * 100:.0f}%",
        va="center",
        fontsize=9,
    )

plt.title(
    "Liga F — Matches with lead changes",
    fontsize=20,
    weight="bold",
    pad=30,
)

plt.text(
    0.5,
    1.03,
    "Share of matches involving a change in which team was leading",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11,
    alpha=0.75,
)

plt.xlabel("Matches with lead changes (%)")
plt.ylabel("Team")
plt.xlim(0, 60)

plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)

plt.savefig(
    FIGURES_DIR / "20_lead_change_match_rate_by_team.png",
    dpi=300,
)

plt.close()

# =========================================================
# 10. GRAPH — EQUALIZER MATCH RATE
# =========================================================

plot_df = team_summary.sort_values("equalizer_match_rate")

plt.figure(figsize=(12, 8))

q25 = plot_df["equalizer_match_rate"].quantile(0.25)
q75 = plot_df["equalizer_match_rate"].quantile(0.75)

colors = []

for value in plot_df["equalizer_match_rate"]:

    if value <= q25:
        colors.append(POSITIVE_COLOR)

    elif value >= q75:
        colors.append(NEGATIVE_COLOR)

    else:
        colors.append(WARNING_COLOR)

plt.barh(
    plot_df.index,
    plot_df["equalizer_match_rate"] * 100,
    color=colors,
)

for team, row in plot_df.iterrows():

    plt.text(
        row["equalizer_match_rate"] * 100 + 1,
        team,
        f"{row['equalizer_match_rate'] * 100:.0f}%",
        va="center",
        fontsize=9,
    )

plt.title(
    "Liga F — Matches with equalizers",
    fontsize=20,
    weight="bold",
    pad=30,
)

plt.text(
    0.5,
    1.03,
    "Share of matches where the scoreline returned to level after the opening goal",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11,
    alpha=0.75,
)

plt.xlabel("Matches with equalizers (%)")
plt.ylabel("Team")
plt.xlim(0, 80)

plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)

plt.savefig(
    FIGURES_DIR / "21_equalizer_match_rate_by_team.png",
    dpi=300,
)

plt.close()

# =========================================================
# 11. GRAPH — VOLATILITY MAP
# =========================================================

plot_df = team_summary.copy()

plt.figure(figsize=(12, 8))

chaos_median = plot_df["avg_chaos_score"].median()
late_goal_median = plot_df["late_goal_match_rate"].median()

scatter_colors = []

for _, row in plot_df.iterrows():

    chaos = row["avg_chaos_score"]
    late = row["late_goal_match_rate"]

    if (
        chaos < chaos_median
        and late < late_goal_median
    ):
        scatter_colors.append(POSITIVE_COLOR)

    elif (
        chaos >= chaos_median
        and late < late_goal_median
    ):
        scatter_colors.append(CONTROL_COLOR)

    elif (
        chaos < chaos_median
        and late >= late_goal_median
    ):
        scatter_colors.append(WARNING_COLOR)

    else:
        scatter_colors.append(NEGATIVE_COLOR)

plt.scatter(
    plot_df["avg_chaos_score"],
    plot_df["late_goal_match_rate"],

    s=plot_df["matches"] * 25,

    color=scatter_colors,
    alpha=0.75,

    edgecolor="white",
    linewidth=1.2,
)

highlight_offsets = {
    "Barcelona": (0.04, 0.00),
    "Real Madrid": (0.04, 0.00),
    "Real Sociedad": (0.04, 0.00),
    "Eibar": (0.04, 0.00),
    "Levante": (0.04, 0.00),
    "Alhama CF": (0.04, 0.00),
}

for team, row in plot_df.iterrows():

    if team in highlight_offsets:

        x_offset, y_offset = highlight_offsets[team]

        plt.text(
            row["avg_chaos_score"] + x_offset,
            row["late_goal_match_rate"] + y_offset,
            team,
            fontsize=10,
            weight="bold",
            va="center",
        )

plt.axvline(
    chaos_median,
    linestyle="--",
    linewidth=1,
    alpha=0.4,
    color="black",
)

plt.axhline(
    late_goal_median,
    linestyle="--",
    linewidth=1,
    alpha=0.4,
    color="black",
)

plt.text(
    0.78,
    0.635,
    "Lower chaos\nlate involvement",
    fontsize=10,
    ha="center",
    va="top",
    alpha=0.7,
)

plt.text(
    1.58,
    0.635,
    "High chaos\nlate involvement",
    fontsize=10,
    ha="center",
    va="top",
    alpha=0.7,
)

plt.text(
    0.78,
    0.305,
    "Stable profile",
    fontsize=10,
    ha="center",
    va="bottom",
    alpha=0.7,
)

plt.text(
    1.58,
    0.305,
    "Controlled volatility",
    fontsize=10,
    ha="center",
    va="bottom",
    alpha=0.7,
)

plt.title(
    "Liga F — Volatility map",
    fontsize=20,
    weight="bold",
    pad=30,
)

plt.text(
    0.5,
    1.03,
    "Average match chaos vs late-game involvement",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11,
    alpha=0.75,
)

plt.xlabel("Average chaos score")
plt.ylabel("Matches with late goals (%)")

ax = plt.gca()

ax.yaxis.set_major_formatter(
    PercentFormatter(1)
)

plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)

plt.savefig(
    FIGURES_DIR / "22_volatility_map.png",
    dpi=300,
)

plt.close()

# =========================================================
# 12. PRINT OUTPUTS
# =========================================================

print("\nVOLATILITY TEAM SUMMARY")
print("-----------------------")
print(team_summary)

print("\nSaved figures:")
print("outputs/figures/19_avg_match_chaos_by_team.png")
print("outputs/figures/20_lead_change_match_rate_by_team.png")
print("outputs/figures/21_equalizer_match_rate_by_team.png")
print("outputs/figures/22_volatility_map.png")

print("\nSaved tables:")
print("outputs/tables/volatility_matches.csv")
print("outputs/tables/volatility_teams.csv")
print("outputs/tables/volatility_team_summary.csv")

print("\nDONE")