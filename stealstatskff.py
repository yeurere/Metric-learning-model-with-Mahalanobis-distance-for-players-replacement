import json
import time
import requests

player_ids = [] # players' IDs, that taken from https://kffleague.kz cite's code
season_id = 200 # id of 2026 Premier League season, for first league id - 204, for second league - 203

all_players_stats = []

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
}

for player_id in player_ids:
  url = f"https://kffleague.kz/api/v2/players/{player_id}/stats?season_id={season_id}&lang=ru"

  try:
    response = requests.get(url, headers=headers, timeout=1000)
    if response.status_code == 200:
      data = response.json()
      all_players_stats.append({"player_id": player_id, "stats": data})
      print(f"Игрок с ID {player_id} успешно загружен.")
    else:
      print(f"Игрок с ID {player_id} не найден (статус: {response.status_code})")
  except Exception as e:
    print(f"Ошибка при запросе игрока {player_id}: {e}")

  time.sleep(0.2)

filename = r"C:\Users\....\kff_players.json"

with open(filename, "w", encoding="utf-8") as f:
  json.dump(all_players_stats, f, ensure_ascii=False, indent=4)

print(
    f"\nReady! Statistics saved in: {filename}"
)  
