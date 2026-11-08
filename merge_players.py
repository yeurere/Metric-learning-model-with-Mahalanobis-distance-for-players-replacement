import json

with open("kff_players.json", encoding="utf-8") as f:
    stats = json.load(f)          

with open("kff_players_names.json", encoding="utf-8") as f:
    enriched = json.load(f)       

enriched_by_id = {p["id"]: p for p in enriched}

merged = []
missing = []
for item in stats:
    pid = item["player_id"]
    info = enriched_by_id.get(pid)
    if info is None:
        missing.append(pid)
        merged.append(item)      
        continue
    extra = {k: v for k, v in info.items() if k != "id"}  
    merged.append({**item, **extra})

with open("players_merged.json", "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"Merged: {len(merged) - len(missing)} из {len(stats)}")
if missing:
    print("No any data on second file player_id:", missing)
