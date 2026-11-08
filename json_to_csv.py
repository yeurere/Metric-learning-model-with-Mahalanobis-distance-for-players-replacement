import json
import pandas as pd

with open("players_merged.json", encoding="utf-8") as f:
    data = json.load(f)

df = pd.json_normalize(data, sep=".")

df["teams"] = df["teams"].apply(lambda t: ";".join(map(str, t)) if isinstance(t, list) else t)

df = df.drop(columns=["stats.player_id", "stats"], errors="ignore")

df.to_csv("players_merged.csv", index=False, encoding="utf-8-sig")

print(df.shape)
