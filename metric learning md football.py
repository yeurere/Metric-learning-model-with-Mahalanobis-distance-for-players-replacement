
# ============================================================
# FOOTBALL PLAYER SIMILARITY & REPLACEMENT SYSTEM
# Kazakhstan: Premier League / First League / Second League
#
# Methods:
# 1. Euclidean Distance
# 2. Cosine Similarity
# 3. Mahalanobis Distance
#
# Target player statistics are entered manually as season totals.
# The program automatically converts count statistics to per 90.
# ============================================================

import pandas as pd
import numpy as np
import warnings

from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.covariance import LedoitWolf
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import cdist

warnings.filterwarnings("ignore")


# ============================================================
# 1. CSV FILE PATHS
# ============================================================

PREMIER_CSV = r"C:\Users\...\players_merged.csv"
FIRST_CSV   = r"C:\Users\...\firstleague_players_merged.csv"
SECOND_CSV  = r"C:\Users\...\secondleague_players_merged.csv"

# Измени названия файлов выше на свои реальные пути.


# ============================================================
# 2. LEAGUE SELECTION
# ============================================================

print("=" * 60)
print("SELECT KAZAKHSTAN LEAGUE")
print("=" * 60)

print("1 — Kazakhstan Premier League")
print("2 — Kazakhstan First League")
print("3 — Kazakhstan Second League")

league_choice = input("\nChoose league: ").strip()

league_files = {
    "1": (PREMIER_CSV, "Premier League"),
    "2": (FIRST_CSV, "First League"),
    "3": (SECOND_CSV, "Second League")
}

if league_choice not in league_files:
    raise ValueError("Invalid league selection!")

file_path, league_name = league_files[league_choice]

df = pd.read_csv(file_path)

print(f"\nSelected league: {league_name}")
print("Players loaded:", len(df))


# ============================================================
# 3. DATA PREPARATION
# ============================================================

required = [
    "player_id",
    "first_name",
    "last_name",
    "age",
    "position_code",
    "stats.time_on_field_total",
    "stats.games_played"
]

missing = [c for c in required if c not in df.columns]

if missing:
    raise ValueError(f"Missing required columns: {missing}")

df["Player"] = (
    df["first_name"].fillna("").astype(str)
    + " "
    + df["last_name"].fillna("").astype(str)
).str.strip()

df["age"] = pd.to_numeric(df["age"], errors="coerce")
df["Minutes"] = pd.to_numeric(
    df["stats.time_on_field_total"], errors="coerce"
)
df["Matches"] = pd.to_numeric(
    df["stats.games_played"], errors="coerce"
)

for col in df.columns:
    if col.startswith("stats."):
        df[col] = pd.to_numeric(df[col], errors="coerce")


# ============================================================
# 4. POSITION SELECTION
# ============================================================

print("\n" + "=" * 60)
print("SELECT PLAYER POSITION")
print("=" * 60)

print("1 — Defender")
print("2 — Midfielder")
print("3 — Forward")

position_choice = input("\nChoose position: ").strip()

position_map = {
    "1": ("DEF", "Defender"),
    "2": ("MID", "Midfielder"),
    "3": ("FWD", "Forward")
}

if position_choice not in position_map:
    raise ValueError("Invalid position!")

position_code, position_name = position_map[position_choice]

players = df[df["position_code"] == position_code].copy()

print("\nSelected position:", position_name)
print("Players:", len(players))


# ============================================================
# 5. AGE LIMIT AND PLAYING TIME FILTERS
# ============================================================

print("\n" + "=" * 60)
print("CANDIDATE FILTERS")
print("=" * 60)

max_age = float(input("Maximum candidate age (e.g. 23): "))

minutes_input = input(
    "Minimum candidate minutes [450 by default]: "
).strip()

min_minutes = float(minutes_input) if minutes_input else 450

players = players[
    (players["age"] <= max_age)
    & (players["age"].notna())
    & (players["Minutes"] >= min_minutes)
    & (players["Minutes"] > 0)
].copy()

if len(players) < 3:
    raise ValueError(
        "Not enough players after filtering. "
        "Increase the age limit or reduce minimum minutes."
    )

print("\nCandidates after filtering:", len(players))


# ============================================================
# 6. FEATURE DEFINITIONS
#
# count = season total, automatically converted to per 90
# ratio = percentage, entered directly
# ============================================================

common_features = [
    ("Goals", "stats.goal", "count"),
    ("Assists", "stats.goal_pass", "count"),
    ("Shots", "stats.shot", "count"),
    ("Shots on target", "stats.shots_on_goal", "count"),
    ("Passes", "stats.passes", "count"),
    ("Pass accuracy (%)", "stats.pass_ratio", "ratio"),
    ("Accurate passes", "stats.pass_acc", "count"),
    ("Forward passes", "stats.pass_forward", "count"),
    ("Progressive passes", "stats.pass_progressive", "count"),
    ("Crosses", "stats.pass_cross", "count"),
    ("Passes into penalty area", "stats.pass_to_box", "count"),
    ("Successful dribbles", "stats.dribble_success", "count"),
    ("Corners", "stats.corner", "count"),
    ("Offsides", "stats.offside", "count"),
    ("Tackles", "stats.tackle", "count"),
    ("Interceptions", "stats.interception", "count"),
    ("Recoveries", "stats.recovery", "count"),
    ("Aerial duels", "stats.aerial_duel", "count"),
    ("Aerial duels won", "stats.aerial_duel_success", "count"),
    ("Ground duels", "stats.ground_duel", "count"),
    ("Ground duels won", "stats.ground_duel_success", "count"),
    ("Fouls", "stats.foul", "count"),
    ("Fouls suffered", "stats.foul_taken", "count"),
    ("Yellow cards", "stats.yellow_cards", "count"),
    ("Red cards", "stats.red_cards", "count"),
    ("Penalties scored", "stats.penalty_success", "count"),
    ("Own goals", "stats.owngoal", "count"),
    ("Goals outside the box", "stats.goal_out_box", "count"),
    ("Blocked shots", "stats.shots_blocked_opponent", "count"),
]

position_features = {
    "DEF": [
        "Goals", "Assists", "Shots", "Shots on target",
        "Passes", "Pass accuracy (%)", "Accurate passes",
        "Forward passes", "Progressive passes", "Crosses",
        "Passes into penalty area",
        "Tackles", "Interceptions", "Recoveries",
        "Aerial duels", "Aerial duels won",
        "Ground duels", "Ground duels won",
        "Fouls", "Fouls suffered",
        "Yellow cards", "Red cards"
    ],

    "MID": [
        "Goals", "Assists", "Shots", "Shots on target",
        "Passes", "Pass accuracy (%)", "Accurate passes",
        "Forward passes", "Progressive passes", "Crosses",
        "Passes into penalty area",
        "Successful dribbles", "Corners",
        "Tackles", "Interceptions", "Recoveries",
        "Aerial duels", "Aerial duels won",
        "Ground duels", "Ground duels won",
        "Fouls", "Fouls suffered",
        "Yellow cards", "Red cards"
    ],

    "FWD": [
        "Goals", "Assists", "Shots", "Shots on target",
        "Passes", "Pass accuracy (%)", "Accurate passes",
        "Forward passes", "Progressive passes",
        "Passes into penalty area",
        "Successful dribbles", "Offsides",
        "Aerial duels", "Aerial duels won",
        "Ground duels", "Ground duels won",
        "Fouls suffered",
        "Yellow cards", "Red cards"
    ]
}

feature_lookup = {
    label: (column, kind)
    for label, column, kind in common_features
}

selected_labels = position_features[position_code]

# Используем только столбцы, существующие в выбранном CSV.
# Также исключаем показатели, у которых слишком мало данных.

features = []

for label in selected_labels:
    column, kind = feature_lookup[label]

    if column not in players.columns:
        continue

    coverage = players[column].notna().mean()

    if coverage >= 0.40:
        features.append((label, column, kind))

if len(features) < 3:
    raise ValueError("Not enough available statistical features.")

print("\nFeatures used by the model:")
for label, column, kind in features:
    print("-", label)


# ============================================================
# 7. TARGET PLAYER INPUT
# ============================================================

print("\n" + "=" * 60)
print("TARGET PLAYER INFORMATION")
print("=" * 60)

target_age = float(input("Target player age: "))

target_matches = float(input("Matches played during season: "))
target_minutes = float(input("Minutes played during season: "))

if target_minutes <= 0:
    raise ValueError("Minutes must be greater than zero.")

print("\nEnter season statistics.")
print("Enter TOTAL season values, not per 90 values.")
print("For unknown statistics, press Enter.")

target_raw = {}

for label, column, kind in features:
    value = input(f"{label}: ").strip()

    if value == "":
        target_raw[column] = np.nan
    else:
        target_raw[column] = float(value)


# ============================================================
# 8. AUTOMATIC PER-90 CONVERSION
# ============================================================

# Count statistics are converted to per 90 automatically.
# Percentage statistics remain unchanged.

model_columns = []
model_labels = []

X_data = pd.DataFrame(index=players.index)
target_data = {}

for label, column, kind in features:

    if kind == "count":
        new_column = label + "_per90"

        X_data[new_column] = (
            players[column] / players["Minutes"] * 90
        )

        if pd.isna(target_raw[column]):
            target_data[new_column] = np.nan
        else:
            target_data[new_column] = (
                target_raw[column] / target_minutes * 90
            )

    else:
        new_column = label

        X_data[new_column] = players[column]
        target_data[new_column] = target_raw[column]

    model_columns.append(new_column)
    model_labels.append(label)


# Add duel success percentages.
# These are calculated from total and won duels.

def safe_percentage(won, total):
    return np.where(
        total > 0,
        won / total * 100,
        np.nan
    )

if (
    "stats.aerial_duel" in players.columns
    and "stats.aerial_duel_success" in players.columns
    and "Aerial duels" in selected_labels
):
    col = "Aerial duel success (%)"

    X_data[col] = safe_percentage(
        players["stats.aerial_duel_success"],
        players["stats.aerial_duel"]
    )

    total = target_raw.get("stats.aerial_duel", np.nan)
    won = target_raw.get("stats.aerial_duel_success", np.nan)

    target_data[col] = (
        won / total * 100
        if pd.notna(total) and pd.notna(won) and total > 0
        else np.nan
    )

    model_columns.append(col)

if (
    "stats.ground_duel" in players.columns
    and "stats.ground_duel_success" in players.columns
    and "Ground duels" in selected_labels
):
    col = "Ground duel success (%)"

    X_data[col] = safe_percentage(
        players["stats.ground_duel_success"],
        players["stats.ground_duel"]
    )

    total = target_raw.get("stats.ground_duel", np.nan)
    won = target_raw.get("stats.ground_duel_success", np.nan)

    target_data[col] = (
        won / total * 100
        if pd.notna(total) and pd.notna(won) and total > 0
        else np.nan
    )

    model_columns.append(col)


# ============================================================
# 9. REMOVE UNAVAILABLE FEATURES
# ============================================================

# Drop columns with no values or only one unique value.
valid_columns = []

for col in model_columns:
    if col not in X_data.columns:
        continue

    if X_data[col].notna().sum() < 3:
        continue

    if X_data[col].nunique(dropna=True) <= 1:
        continue

    valid_columns.append(col)

X_data = X_data[valid_columns]

target_data = {
    col: target_data.get(col, np.nan)
    for col in valid_columns
}

if len(valid_columns) < 3:
    raise ValueError("Too few usable features for similarity search.")

# Impute missing values using candidate medians.
imputer = SimpleImputer(strategy="median")

X_imputed = imputer.fit_transform(X_data)

target_frame = pd.DataFrame(
    [target_data],
    columns=valid_columns
)

target_imputed = imputer.transform(target_frame)


# ============================================================
# 10. STANDARDIZATION
# ============================================================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X_imputed)
target_scaled = scaler.transform(target_imputed)


# ============================================================
# 11. EUCLIDEAN DISTANCE
# ============================================================

euclidean = cdist(
    target_scaled,
    X_scaled,
    metric="euclidean"
)[0]

players["Euclidean_Distance"] = euclidean


# ============================================================
# 12. COSINE SIMILARITY
# ============================================================

cosine = cosine_similarity(
    target_scaled,
    X_scaled
)[0]

players["Cosine_Similarity"] = cosine


# ============================================================
# 13. MAHALANOBIS DISTANCE
# ============================================================

# Ledoit-Wolf covariance shrinkage makes the covariance
# estimation more stable with correlated football statistics.

covariance_model = LedoitWolf()
covariance_model.fit(X_scaled)

precision = covariance_model.precision_

difference = X_scaled - target_scaled

mahalanobis = np.sqrt(
    np.maximum(
        np.einsum(
            "ij,jk,ik->i",
            difference,
            precision,
            difference
        ),
        0
    )
)

players["Mahalanobis_Distance"] = mahalanobis


# ============================================================
# 14. REPLACEMENT SCORE
# ============================================================

def distance_similarity(values):
    ranks = pd.Series(values).rank(
        ascending=True,
        method="average",
        pct=True
    )

    return (1 - ranks + 1 / len(ranks)) * 100


players["Euclidean_Similarity"] = distance_similarity(
    players["Euclidean_Distance"]
)

players["Mahalanobis_Similarity"] = distance_similarity(
    players["Mahalanobis_Distance"]
)

players["Cosine_Similarity_pct"] = (
    (players["Cosine_Similarity"] + 1) / 2 * 100
).clip(0, 100)

# Age score: closer age to the target player gives a higher score.
# Candidates above max_age have already been filtered out.

age_difference = abs(players["age"] - target_age)

players["Age_Score"] = (
    1 - age_difference / max(max_age, 1)
).clip(0, 1) * 100

# 80% statistical similarity + 20% age suitability

players["Replacement_Euclidean"] = (
    0.8 * players["Euclidean_Similarity"]
    + 0.2 * players["Age_Score"]
)

players["Replacement_Cosine"] = (
    0.8 * players["Cosine_Similarity_pct"]
    + 0.2 * players["Age_Score"]
)

players["Replacement_Mahalanobis"] = (
    0.8 * players["Mahalanobis_Similarity"]
    + 0.2 * players["Age_Score"]
)


# ============================================================
# 15. TOP-5 RESULTS
# ============================================================

display_columns = [
    "player_id",
    "Player",
    "age",
    "Matches",
    "Minutes"
]

def show_top5(title, sort_column, ascending, replacement_column):

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    result = players.sort_values(
        sort_column,
        ascending=ascending
    ).head(5).copy()

    columns = display_columns + [
        sort_column,
        "Age_Score",
        replacement_column
    ]

    print(result[columns].round(2).to_string(index=False))

    return result

top_euclidean = show_top5(
    "TOP-5 — EUCLIDEAN DISTANCE",
    "Euclidean_Distance",
    True,
    "Replacement_Euclidean"
)

top_cosine = show_top5(
    "TOP-5 — COSINE SIMILARITY",
    "Cosine_Similarity",
    False,
    "Replacement_Cosine"
)

top_mahalanobis = show_top5(
    "TOP-5 — MAHALANOBIS DISTANCE",
    "Mahalanobis_Distance",
    True,
    "Replacement_Mahalanobis"
)


# ============================================================
# 16. EXPORT RESULTS
# ============================================================

output_file = "player_similarity_results.xlsx"

with pd.ExcelWriter(output_file) as writer:

    top_euclidean.to_excel(
        writer,
        sheet_name="Euclidean",
        index=False
    )

    top_cosine.to_excel(
        writer,
        sheet_name="Cosine",
        index=False
    )

    top_mahalanobis.to_excel(
        writer,
        sheet_name="Mahalanobis",
        index=False
    )

print("\nResults saved:", output_file)

