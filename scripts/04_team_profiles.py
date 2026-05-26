from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

from matplotlib.ticker import PercentFormatter

# =========================================================
# 1. CONFIG
# =========================================================

TABLES_DIR = Path("outputs/tables")
FIGURES_DIR = Path("outputs/figures")

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

ARCHETYPE_COLORS = {
    "Complete Competitor": "#5B9B6B",       # green
    "Front-runner": "#4C78A8",              # blue
    "Reactive Competitor": "#E6A23C",       # yellow/orange
    "Fragile Under Pressure": "#C96A5A",    # red
    "Unstable Competitor": "#8C8C8C",       # grey
}

# =========================================================
# 2. LOAD DATA
# =========================================================

scoring_first = pd.read_csv(
    TABLES_DIR / "scoring_first_summary.csv",
    index_col=0
)

comeback = pd.read_csv(
    TABLES_DIR / "comeback_summary.csv",
    index_col=0
)

# =========================================================
# 3. BUILD TEAM PROFILE TABLE
# =========================================================

profiles = pd.DataFrame(index=scoring_first.index)

profiles["scored_first_matches"] = scoring_first["matches_scored_first"]
profiles["conceded_first_matches"] = comeback["matches_conceded_first"]

profiles["control_score"] = scoring_first["points_retention"]
profiles["resilience_score"] = comeback["points_recovery_rate"]

profiles["points_dropped_after_scoring_first"] = scoring_first["points_dropped"]
profiles["points_recovered_after_conceding_first"] = comeback["points"]

profiles = profiles.fillna(0)

# =========================================================
# 4. LEAGUE AVERAGES
# =========================================================

control_avg = profiles["control_score"].mean()
resilience_avg = profiles["resilience_score"].mean()

# =========================================================
# 5. ASSIGN ARCHETYPES
# =========================================================

def assign_archetype(row):

    high_control = row["control_score"] >= control_avg
    high_resilience = row["resilience_score"] >= resilience_avg

    frequent_conceder_first = (
        row["conceded_first_matches"]
        >= profiles["conceded_first_matches"].mean()
    )

    if high_control and high_resilience:
        return "Complete Competitor"

    if high_control and not high_resilience:
        return "Front-runner"

    if not high_control and high_resilience:
        return "Reactive Competitor"

    if frequent_conceder_first and not high_resilience:
        return "Fragile Under Pressure"

    return "Unstable Competitor"

profiles["archetype"] = profiles.apply(
    assign_archetype,
    axis=1
)

profiles = profiles.sort_values(
    ["control_score", "resilience_score"],
    ascending=False
)

# =========================================================
# 6. EXPORT PROFILE TABLE
# =========================================================

profiles.to_csv(
    TABLES_DIR / "team_profiles.csv"
)

# =========================================================
# 7. STATIC GRAPH — CONTROL VS RESILIENCE
# =========================================================

plt.figure(figsize=(12, 8))

for archetype, color in ARCHETYPE_COLORS.items():

    subset = profiles[profiles["archetype"] == archetype]

    plt.scatter(
        subset["control_score"],
        subset["resilience_score"],

        s=(
            subset["scored_first_matches"]
            + subset["conceded_first_matches"]
        ) * 25,

        alpha=0.72,

        color=color,

        edgecolor="white",
        linewidth=1.2,

        label=archetype,
    )

highlight_teams = [
    "Barcelona",
    "Real Sociedad",
    "Sevilla",
    "Levante",
]

for team, row in profiles.iterrows():

    if team in highlight_teams:

        plt.text(
            row["control_score"] + 0.012,
            row["resilience_score"],
            team,
            fontsize=10,
            weight="bold",
            va="center",
        )

plt.axvline(
    control_avg,
    linestyle="--",
    linewidth=1,
    alpha=0.4,
    color="black",
)

plt.axhline(
    resilience_avg,
    linestyle="--",
    linewidth=1,
    alpha=0.4,
    color="black",
)

# =========================================================
# QUADRANT LABELS
# =========================================================

plt.text(
    0.97,
    0.525,
    "Elite control\n+ recovery",
    fontsize=11,
    ha="right",
    va="center",
    alpha=0.7,
)

plt.text(
    0.94,
    0.075,
    "Control-dependent",
    fontsize=11,
    ha="right",
    va="center",
    alpha=0.7,
)

plt.text(
    0.39,
    0.075,
    "Low control\n+ low recovery",
    fontsize=11,
    va="center",
    alpha=0.7,
)

plt.text(
    0.60,
    0.22,
    "Reactive profile",
    fontsize=11,
    alpha=0.7,
)

plt.title(
    "Liga F — Team competitive profiles",
    fontsize=20,
    weight="bold",
    pad=30,
)

plt.text(
    0.5,
    1.03,
    "Game-state control vs comeback resilience",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11,
    alpha=0.75,
)

plt.xlabel("Control after scoring first (%)")
plt.ylabel("Recovery after conceding first (%)")

plt.xlim(0.35, 1.05)
plt.ylim(-0.02, 0.57)

ax = plt.gca()

ax.xaxis.set_major_formatter(
    PercentFormatter(1)
)

ax.yaxis.set_major_formatter(
    PercentFormatter(1)
)

plt.legend(
    title="Archetype",
    loc="upper left",
    frameon=False,
    fontsize=10,
    title_fontsize=11,
)

plt.tight_layout(
    rect=[0, 0, 1, 0.94]
)

plt.savefig(
    FIGURES_DIR / "15_team_profiles_control_vs_resilience.png",
    dpi=300,
)

plt.close()

# =========================================================
# 8. STATIC GRAPH — ARCHETYPE COUNTS
# =========================================================

archetype_counts = (
    profiles["archetype"]
    .value_counts()
    .sort_values()
)

plt.figure(figsize=(10, 6))

bar_colors = [
    ARCHETYPE_COLORS.get(archetype, "#8C8C8C")
    for archetype in archetype_counts.index
]

plt.barh(
    archetype_counts.index,
    archetype_counts.values,
    color=bar_colors,
)

for archetype, value in archetype_counts.items():
    plt.text(
        value + 0.05,
        archetype,
        str(value),
        va="center",
        fontsize=10,
    )

plt.title(
    "Liga F — Competitive Archetypes",
    fontsize=16,
    weight="bold",
)

plt.xlabel("Number of teams")
plt.ylabel("Archetype")

plt.xlim(0, archetype_counts.max() + 1)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "16_competitive_archetypes_count.png",
    dpi=300,
)

plt.close()

# =========================================================
# 9. STATIC GRAPH — CONTROL SCORE BY ARCHETYPE
# =========================================================

profiles_sorted = profiles.sort_values(
    ["archetype", "control_score"],
    ascending=[True, False]
)

plt.figure(figsize=(12, 8))

bar_colors = [
    ARCHETYPE_COLORS.get(archetype, "#8C8C8C")
    for archetype in profiles_sorted["archetype"]
]

plt.barh(
    profiles_sorted.index,
    profiles_sorted["control_score"] * 100,
    color=bar_colors,
)

for team, row in profiles_sorted.iterrows():

    label = (
        f"{row['control_score'] * 100:.0f}%"
        f" | {row['archetype']}"
    )

    plt.text(
        row["control_score"] * 100 + 1,
        team,
        label,
        va="center",
        fontsize=8,
    )

plt.title(
    "Liga F — Control Score by Competitive Archetype",
    fontsize=16,
    weight="bold",
)

plt.xlabel("Control score (%)")
plt.ylabel("Team")

plt.xlim(0, 115)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "17_control_score_by_archetype.png",
    dpi=300,
)

plt.close()

# =========================================================
# 10. INTERACTIVE DATASET
# =========================================================

interactive_df = profiles.copy().reset_index()

interactive_df = interactive_df.rename(
    columns={
        "first_goal_team": "team",
        "index": "team",
        "control_score": "Control Score",
        "resilience_score": "Recovery Score",
        "scored_first_matches": "Scored First",
        "conceded_first_matches": "Conceded First",
        "points_dropped_after_scoring_first": "Points Dropped After Scoring First",
        "points_recovered_after_conceding_first": "Points Recovered After Conceding First",
        "archetype": "Archetype",
    }
)

interactive_df["Context Volume"] = (
    interactive_df["Scored First"]
    +
    interactive_df["Conceded First"]
)

interactive_df["Control %"] = (
    interactive_df["Control Score"] * 100
).round(1)

interactive_df["Recovery %"] = (
    interactive_df["Recovery Score"] * 100
).round(1)

# =========================================================
# 11. INTERACTIVE GRAPH — TEAM PROFILE MAP
# =========================================================

fig = px.scatter(
    interactive_df,

    x="Control Score",
    y="Recovery Score",

    color="Archetype",

    size="Context Volume",
    size_max=40,

    hover_name="team",

    hover_data={
        "Archetype": True,
        "Control %": True,
        "Recovery %": True,
        "Scored First": True,
        "Conceded First": True,
        "Points Dropped After Scoring First": True,
        "Points Recovered After Conceding First": True,
        "Control Score": False,
        "Recovery Score": False,
        "Context Volume": False,
    },

    color_discrete_map=ARCHETYPE_COLORS,

    title="Liga F competitive profiles: control vs recovery",

    labels={
        "Control Score": "Control after scoring first",
        "Recovery Score": "Recovery after conceding first",
    },

    opacity=0.78,
)

# =========================================================
# 12. INTERACTIVE GRAPH — REFERENCE LINES
# =========================================================

fig.add_hline(
    y=resilience_avg,
    line_dash="dash",
    line_color="black",
    opacity=0.30,
)

fig.add_vline(
    x=control_avg,
    line_dash="dash",
    line_color="black",
    opacity=0.30,
)

# =========================================================
# 13. INTERACTIVE GRAPH — STORYTELLING ANNOTATIONS
# =========================================================

fig.add_annotation(
    x=0.98,
    y=0.51,
    text="Elite control + recovery",
    showarrow=False,
    font=dict(size=11),
)

fig.add_annotation(
    x=0.94,
    y=0.035,
    text="Control-dependent",
    showarrow=False,
    font=dict(size=11),
)

fig.add_annotation(
    x=0.69,
    y=0.20,
    text="Reactive profile",
    showarrow=False,
    font=dict(size=11),
)

fig.add_annotation(
    x=0.45,
    y=0.035,
    text="Low control + low recovery",
    showarrow=False,
    font=dict(size=11),
)

# =========================================================
# 14. INTERACTIVE GRAPH — LAYOUT
# =========================================================

fig.update_traces(
    marker=dict(
        line=dict(
            width=1,
            color="white"
        )
    )
)

fig.update_layout(
    template="simple_white",
    width=1000,
    height=650,

    title=dict(
        x=0.03,
        y=0.96,
        font=dict(size=22)
    ),

    legend_title_text="Competitive archetype",

    xaxis=dict(
        range=[0.35, 1.05],
        tickformat=".0%",
        title="Control after scoring first",
    ),

    yaxis=dict(
        range=[-0.02, 0.55],
        tickformat=".0%",
        title="Recovery after conceding first",
    ),

    hoverlabel=dict(
        bgcolor="white",
        font_size=12,
    ),
)

# =========================================================
# 15. EXPORT INTERACTIVE GRAPH
# =========================================================

fig.write_html(
    FIGURES_DIR / "18_interactive_team_profile_map.html"
)

# =========================================================
# 16. PRINT OUTPUTS
# =========================================================

print("\nTEAM PROFILES")
print("-------------")
print(profiles)

print("\nSaved figures:")
print("outputs/figures/15_team_profiles_control_vs_resilience.png")
print("outputs/figures/16_competitive_archetypes_count.png")
print("outputs/figures/17_control_score_by_archetype.png")
print("outputs/figures/18_interactive_team_profile_map.html")

print("\nSaved table:")
print("outputs/tables/team_profiles.csv")

print("\nDONE")