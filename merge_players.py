import json

# 1. Загружаем оба файла
with open("all_players_stats.json", encoding="utf-8") as f:
    stats = json.load(f)          # список: [{"player_id": ..., "stats": {...}}, ...]

with open("players_enriched_data.json", encoding="utf-8") as f:
    enriched = json.load(f)       # список: [{"id": ..., "first_name": ..., ...}, ...]

# 2. Словарь {id: данные игрока} из второго файла для быстрого поиска
enriched_by_id = {p["id"]: p for p in enriched}

# 3. Добавляем данные из второго файла в каждую запись первого
merged = []
missing = []
for item in stats:
    pid = item["player_id"]
    info = enriched_by_id.get(pid)
    if info is None:
        missing.append(pid)
        merged.append(item)       # оставляем как есть, без доп. данных
        continue
    extra = {k: v for k, v in info.items() if k != "id"}  # дубль id не нужен
    merged.append({**item, **extra})

# 4. Сохраняем результат
with open("players_merged.json", "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"Объединено: {len(merged) - len(missing)} из {len(stats)}")
if missing:
    print("Нет данных во втором файле для player_id:", missing)
