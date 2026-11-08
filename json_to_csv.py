import json
import pandas as pd

with open("players_merged.json", encoding="utf-8") as f:
    data = json.load(f)

# Разворачиваем вложенные словари: stats.goal, stats.ranks.goal, ...
df = pd.json_normalize(data, sep=".")

# teams — это список, например [92]; превращаем в строку "92" или "92;105"
df["teams"] = df["teams"].apply(lambda t: ";".join(map(str, t)) if isinstance(t, list) else t)

# stats.player_id дублирует player_id — убираем
df = df.drop(columns=["stats.player_id", "stats"], errors="ignore")

# utf-8-sig, чтобы Excel правильно показал кириллицу
df.to_csv("players_merged.csv", index=False, encoding="utf-8-sig")

print(df.shape)
