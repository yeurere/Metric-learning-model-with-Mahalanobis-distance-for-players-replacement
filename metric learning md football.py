
import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import euclidean_distances, cosine_similarity

df = pd.read_csv(
    r"C:\Users\mejra\Downloads\Telegram Desktop\2022-2023 Football Player Stats.csv",
    sep=";",
    encoding="cp1251"
)
# Параметры для каждой позиции.1
# Названия должны точно совпадать с колонками твоего датасета.
POSITION_FEATURES = {
    "DF": [
        "Tkl", "Int", "Clr", "Blocks", "AerWon",
        "PasTotCmp", "Age"
    ],
    "MF": [
        "PasTotCmp%", "PasProg", "Pas3rd",
        "RecProg", "Tkl", "Assists", "Age"
    ],
    "FW": [
        "Goals", "Shots", "SoT", "Assists",
        "G/Sh", "Touches", "Age"
    ]
}

POSITION_NAMES = {
    "DF": "Защитник",
    "MF": "Полузащитник",
    "FW": "Нападающий"
}
# Названия статистических показателей и их описания
FEATURE_DESCRIPTIONS = {
    "Tkl": (
        "Tackles — количество отборов мяча."
    ),
    "Int": (
        "Interceptions — количество перехватов мяча."
    ),
    "Clr": (
        "Clearances — количество выносов мяча из опасной зоны."
    ),
    "Blocks": (
        "Blocks — количество блокировок ударов и передач."
    ),
    "AerWon": (
        "Aerial Duels Won — количество выигранных верховых единоборств."
    ),
    "PasTotCmp": (
        "Passes Completed — количество точных передач."
    ),
    "PasTotCmp%": (
        "Pass Completion % — процент точных передач."
    ),
    "PasProg": (
        "Progressive Passes — количество передач, продвигающих мяч вперёд."
    ),
    "Pas3rd": (
        "Passes into Final Third — количество передач в финальную треть поля."
    ),
    "RecProg": (
        "Progressive Passes Received — количество полученных прогрессивных передач."
    ),
    "Assists": (
        "Assists — количество голевых передач."
    ),
    "Goals": (
        "Goals — количество забитых голов."
    ),
    "Shots": (
        "Shots — общее количество ударов по воротам."
    ),
    "SoT": (
        "Shots on Target — количество ударов в створ ворот."
    ),
    "G/Sh": (
        "Goals per Shot — отношение голов к общему количеству ударов."
    ),
    "Touches": (
        "Touches — количество касаний мяча."
    )
}


def position_mask(data, position):
    return data["Pos"].fillna("").astype(str).str.contains(
        position,
        regex=False
    )


def find_candidates(df):
    print("Выбери позицию:")
    print("1 — Защитник")
    print("2 — Полузащитник")
    print("3 — Нападающий")

    choice = input("Твой выбор: ").strip()

    choices = {"1": "DF", "2": "MF", "3": "FW"}

    if choice not in choices:
        print("Неверный выбор.")
        return

    position = choices[choice]
    features = POSITION_FEATURES[position]

    print("\n=== ОПИСАНИЕ СТАТИСТИКИ ===")

    for feature in features:
        print(f"\n{feature} — {FEATURE_DESCRIPTIONS.get(feature, 'Описание отсутствует.')}")

    # Проверяем наличие необходимых колонок
    missing = [
        col for col in ["Player", "Pos"] + features
        if col not in df.columns
    ]

    if missing:
        print("В датасете отсутствуют колонки:", missing)
        return

    # Берём игроков только выбранной позиции
    players = df[position_mask(df, position)].copy()
    # Учитываем возраст молодых игроков
    players["Age"] = pd.to_numeric(
        players["Age"], errors="coerce"
    )

    max_age = int(input("Максимальный возраст игрока (например, 23): "))

    players = players[
        (players["Age"] <= max_age) &
        (players["Age"].notna())
    ].copy()
    
    1# Учитываем игровое время
    players["MP"] = pd.to_numeric(players["MP"], errors="coerce")
    players["Min"] = pd.to_numeric(players["Min"], errors="coerce")

    # Оставляем игроков, у которых есть игровое время
    players["Min"] = pd.to_numeric(
        players["Min"], errors="coerce"
    )

    players = players[players["Min"] > 0].copy()

    # Переводим статистику в числовой формат
    for col in features:
        players[col] = pd.to_numeric(
            players[col], errors="coerce"
        )

    # Убираем строки без статистики по выбранным признакам
    # Убираем строки без статистики и имени
    players = players.dropna(subset=features)
    players = players.dropna(subset=["Player"])

# Убираем повторяющиеся имена игроков
    players = players.drop_duplicates(
        subset=["Player"],
        keep="first"
    ).reset_index(drop=True)

    if len(players) < 2:
        print("Недостаточно игроков для сравнения.")
        return

    print(f"\nПозиция: {POSITION_NAMES[position]}")
    print("Введи статистику искомого игрока:")

    target_values = []

    for feature in features:
        value = float(input(f"{feature}: "))
        target_values.append(value)

    # Матрица статистики кандидатов
    X_raw = players[features].to_numpy(dtype=float)

    # Нормализация признаков
    scaler = StandardScaler()
    X = scaler.fit_transform(X_raw)

    # Нормализуем введённую статистику тем же scaler
    target = scaler.transform(
        np.array(target_values).reshape(1, -1)
    )

    # 1. Евклидово расстояние: меньше = ближе
    euclidean = euclidean_distances(target, X)[0]

    # 2. Косинусное сходство: больше = ближе
    cosine = cosine_similarity(target, X)[0]

    # 3. Расстояние Махаланобиса: меньше = ближе
    covariance = np.cov(X, rowvar=False)
    inverse_covariance = np.linalg.pinv(covariance)

    differences = X - target
    mahalanobis = np.sqrt(
        np.maximum(
            np.einsum(
                "ij,jk,ik->i",
                differences,
                inverse_covariance,
                differences
            ),
            0
        )
    )

    # Отдельная таблица для каждой метрики
    results = players[["Player", "Squad", "Pos"]].copy()

    results["Euclidean Distance"] = euclidean
    results["Cosine Similarity"] = cosine
    results["Mahalanobis Distance"] = mahalanobis

    top_k = 5

    print("\n=== TOP 5: EUCLIDEAN DISTANCE ===")
    print(
        results.nsmallest(top_k, "Euclidean Distance")[
            ["Player", "Squad", "Euclidean Distance"]
        ].to_string(index=False)
    )

    print("\n=== TOP 5: COSINE SIMILARITY ===")
    print(
        results.nlargest(top_k, "Cosine Similarity")[
            ["Player", "Squad", "Cosine Similarity"]
        ].to_string(index=False)
    )

    print("\n=== TOP 5: MAHALANOBIS DISTANCE ===")
    print(
        results.nsmallest(top_k, "Mahalanobis Distance")[
            ["Player", "Squad", "Mahalanobis Distance"]
        ].to_string(index=False)
    )

    # Ручная оценка качества рекомендаций
    print("\n=== PRECISION@5: ОЦЕНКА РЕКОМЕНДАЦИЙ ===")
    print("Для каждого игрока введи 1, если он подходит,")
    print("или 0, если не подходит.")

    metric_columns = {
        "Euclidean": ("Euclidean Distance", "smallest"),
        "Cosine": ("Cosine Similarity", "largest"),
        "Mahalanobis": ("Mahalanobis Distance", "smallest")
    }

    for metric_name, (column, order) in metric_columns.items():
        if order == "smallest":
            top_players = results.nsmallest(top_k, column)
        else:
            top_players = results.nlargest(top_k, column)

        print(f"\nОцениваем метрику: {metric_name}")
        relevant_count = 0

        for _, player in top_players.iterrows():
            while True:
                answer = input(
                    f"Подходит ли {player['Player']}? (1/0): "
                ).strip()

                if answer in ("1", "0"):
                    relevant_count += int(answer)
                    break

                print("Введи 1 или 0.")

        actual_k = len(top_players)
        precision = relevant_count / actual_k if actual_k else 0

        print(
            f"Precision@{actual_k} для {metric_name}: "
            f"{precision:.2%} "
            f"({relevant_count}/{actual_k})"
        )


find_candidates(df)
