import json
import time
import requests

# Пример списка ID игроков (сюда можно собрать все ID игроков лиги)
player_ids = [1366 ,1883, 146]

all_players_stats = []

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
}

for player_id in player_ids:
  # Подставляем ID игрока в эндпоинт
  url = f"https://kffleague.kz/api/v2/players/{player_id}/stats?season_id=204&lang=ru"

  try:
    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code == 200:
      data = response.json()
      # Сохраняем данные игрока
      all_players_stats.append({"player_id": player_id, "stats": data})
      print(f"Игрок с ID {player_id} успешно загружен.")
    else:
      print(f"Игрок с ID {player_id} не найден (статус: {response.status_code})")
  except Exception as e:
    print(f"Ошибка при запросе игрока {player_id}: {e}")

  # Небольшая пауза, чтобы сайт не заблокировал за слишком частые запросы
  time.sleep(0.2)

# --- СОХРАНЕНИЕ В JSON-ФАЙЛ НА КОМПЬТЕРЕ ---
filename = r"C:\Users\mejra\Desktop\target_players.json"

with open(filename, "w", encoding="utf-8") as f:
  json.dump(all_players_stats, f, ensure_ascii=False, indent=4)

print(
    f"\nГотово! Статистика всех игроков сохранена в файл: {filename}"
)  #[cite: 4]