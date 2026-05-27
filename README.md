# Liga F — Game State & Competitive Profiles Analysis

Exploratory football analytics project focused on how Liga F teams behave after scoring or conceding first.

The project combines match event data, game-state analysis and competitive profiling to better understand:
- which teams control matches after scoring first,
- which teams can recover after conceding first,
- and how different competitive archetypes emerge across the league.

---

# Main Questions

- Which teams are strongest at protecting leads?
- Which teams show the best comeback resilience?
- How often do teams score first or concede first?
- Are some teams heavily dependent on controlling the game state?
- Can we identify consistent competitive profiles across the league?

---

# Project Structure

```bash
scripts/
│
├── 01_game_state_exploration.py
├── 02_scoring_first_analysis.py
├── 03_comeback_analysis.py
├── 04_team_profiles.py
└── 05_volatility_analysis.py
```

---

# Key Outputs

## 1. Game State Exploration

Initial exploratory analysis of:
- goals by minute,
- goals by game state,
- late goals,
- opening goals,
- win rates after scoring first.

### Example Insights

- Late goals represent an important share of total league scoring.
- Teams that score first generally have a strong advantage.
- Some teams consistently start matches from positive game states.

---

## 2. Scoring First Analysis

Analysis of what happens after teams score first.

### Metrics

- Win rate after scoring first
- Points dropped after scoring first
- Match outcome distribution after scoring first
- Control score

### Competitive Interpretation

This section highlights:
- elite controllers,
- unstable leaders,
- and teams that struggle to protect advantages.

---

## 3. Conceding First Analysis

Analysis of team behavior after conceding the opening goal.

### Metrics

- Recovery rate
- Points recovered after conceding first
- Result distribution after conceding first
- Resilience score

### Competitive Interpretation

This section identifies:
- resilient teams,
- reactive teams,
- and fragile profiles under pressure.

---

## 4. Competitive Team Profiles

Combined view of:
- control after scoring first,
- resilience after conceding first.

This creates league-wide competitive archetypes such as:
- Complete Competitor
- Front-runner
- Reactive Competitor
- Fragile Under Pressure

---

## 5. Volatility & Match Chaos Analysis

Analysis focused on competitive instability, contextual turbulence and match-state volatility across Liga F.

Metrics:
- Match chaos score
- Lead-change frequency
- Equalizer frequency
- Late-game involvement
- Volatility mapping
- Competitive Interpretation

This section explores:
- emotionally unstable matches,
- chaotic competitive environments,
- controlled dominance,
- and how different teams sustain or lose contextual control during matches.

The analysis introduces volatility archetypes such as:
- Stable profiles
- Controlled volatility
- High-chaos competitors
- Reactive environments

---

# Visual Design Philosophy

The project uses a consistent visual language inspired by a “competitive traffic-light system”:

- 🟢 Green → strong / resilient / positive profile
- 🔵 Blue → control-oriented / front-runner profile
- 🟡 Yellow → reactive / unstable profile
- 🔴 Red → fragile / negative profile

The goal is to improve readability and storytelling instead of producing purely descriptive charts.

---

# Tools Used

- Python
- Pandas
- Matplotlib
- Plotly

---

---

# Next Phases

The current version of the project focuses on competitive control, resilience and contextual stability using match-level game-state analysis.

Future phases aim to deepen the interpretation of competitive behavior across the season.

## 1. Temporal Volatility Dynamics

Potential additions:
- rolling chaos scores,
- volatility evolution across the season,
- momentum swings,
- instability streaks,
- contextual collapse periods.

Goal:
understand how competitive instability changes throughout the season instead of using only season-wide aggregates.

---

## 2. Temporal Dynamics

Potential additions:
- rolling control scores,
- rolling resilience scores,
- momentum shifts across the season,
- collapse or recovery periods,
- form evolution by round.

Goal:
analyze how competitive behavior changes over time instead of treating the season as a static dataset.

---

## 3. Home vs Away Competitive Identity

Potential additions:
- contextual stability at home vs away,
- resilience differences by venue,
- dependence on home advantage,
- emotional stability outside home matches.

Goal:
explore how competitive identity changes depending on match context.

---

## 4. Match Flow Modeling

Potential additions:
- game-state transition models,
- comeback probabilities,
- collapse probabilities,
- state transition matrices.

Goal:
move from descriptive analysis toward contextual match-flow modeling.

---

## 5. Football Interpretation Layer

Main focus:
connecting the metrics to football meaning.

Key questions:
- What does “control” actually mean in Liga F?
- Which teams sustain competitive dominance most consistently?
- Which teams depend heavily on game state?
- Which teams perform better under adversity or chaos?
- Which patterns help explain long-term competitive stability?

The long-term objective is to build a football-oriented framework for interpreting competitive behavior beyond traditional standings and isolated match statistics.

---

# Author

Fernanda Pieri  
Football analytics & performance analysis portfolio project.