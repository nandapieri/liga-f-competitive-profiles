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
└── 04_team_profiles.py
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

# Author

Fernanda Pieri  
Football analytics & performance analysis portfolio project.