import json
from pathlib import Path

import pandas as pd

# =========================================================
# 1. CONFIGURAÇÃO
# =========================================================

RAW_DIR = Path("data/raw/matches")

OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

match_rows = []
goal_rows = []

# =========================================================
# 2. FUNÇÃO DE GAME STATE
# =========================================================

def game_state(home_score, away_score, is_home_team):

    if home_score == away_score:
        return "drawing"

    if is_home_team:
        return "winning" if home_score > away_score else "losing"

    return "winning" if away_score > home_score else "losing"

# =========================================================
# 3. LOOP DOS JSONS
# =========================================================

for file in sorted(RAW_DIR.glob("*.json")):

    print(f"processing {file.name}")

    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # =====================================================
    # 4. DADOS GERAIS DA PARTIDA
    # =====================================================

    general = data["general"]
    header = data["header"]

    match_id = general["matchId"]

    home_team = general["homeTeam"]["name"]
    away_team = general["awayTeam"]["name"]

    home_goals = header["teams"][0]["score"]
    away_goals = header["teams"][1]["score"]

    # =====================================================
    # 5. EVENTOS DA PARTIDA
    # =====================================================

    events = data["content"]["matchFacts"]["events"]["events"]

    goals = [
        e for e in events
        if e["type"] == "Goal"
    ]

    # =====================================================
    # 6. PRIMEIRO GOL
    # =====================================================

    first_goal_team = None
    first_goal_minute = None

    if goals:

        first_goal = sorted(
            goals,
            key=lambda e: e["time"]
        )[0]

        first_goal_team = (
            home_team
            if first_goal["isHome"]
            else away_team
        )

        first_goal_minute = first_goal["time"]

    # =====================================================
    # 7. RESULTADO FINAL
    # =====================================================

    winner = (
        home_team if home_goals > away_goals
        else away_team if away_goals > home_goals
        else "Draw"
    )

    # =====================================================
    # 8. MATCH TABLE
    # =====================================================

    match_rows.append({

        "match_id": match_id,

        "round": general.get("matchRound"),

        "date": general.get("matchTimeUTCDate"),

        "home_team": home_team,
        "away_team": away_team,

        "home_goals": home_goals,
        "away_goals": away_goals,

        "winner": winner,

        "first_goal_team": first_goal_team,
        "first_goal_minute": first_goal_minute,

    })

    # =====================================================
    # 9. GOALS TABLE
    # =====================================================

    for e in goals:

        home_before = e["homeScore"]
        away_before = e["awayScore"]

        home_after, away_after = e["newScore"]

        scoring_team = (
            home_team
            if e["isHome"]
            else away_team
        )

        goal_rows.append({

            "match_id": match_id,

            "minute": e["time"],

            "scoring_team": scoring_team,

            "scorer": e.get("nameStr"),

            "is_home_goal": e["isHome"],

            "home_score_before": home_before,
            "away_score_before": away_before,

            "home_score_after": home_after,
            "away_score_after": away_after,

            # =============================================
            # GAME STATE
            # =============================================

            "game_state_before": game_state(
                home_before,
                away_before,
                e["isHome"]
            ),

            "game_state_after": game_state(
                home_after,
                away_after,
                e["isHome"]
            ),

            # =============================================
            # CONTEXT FLAGS
            # =============================================

            "is_equalizer": (
                home_after == away_after
            ),

            "is_go_ahead_goal": (
                home_before == away_before
                and home_after != away_after
            ),

            "is_late_goal": (
                e["time"] >= 75
            ),

        })

# =========================================================
# 10. DATAFRAMES
# =========================================================

matches_df = pd.DataFrame(match_rows)

goals_df = pd.DataFrame(goal_rows)

# =========================================================
# 11. EXPORTAR CSV
# =========================================================

matches_df.to_csv(
    OUT_DIR / "matches.csv",
    index=False
)

goals_df.to_csv(
    OUT_DIR / "goals.csv",
    index=False
)

# =========================================================
# 12. RESUMO
# =========================================================

print("\nMATCHES")
print(matches_df.shape)

print("\nGOALS")
print(goals_df.shape)

print("\nDONE")