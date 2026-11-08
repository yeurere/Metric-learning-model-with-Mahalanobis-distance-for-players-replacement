import json
import time
import requests

player_ids = []  # players' IDs, that taken from https://kffleague.kz cite's code 
season_id = 200  # id of premier league 2026 season, for first league - 204, for second - 203 

complete_players_data = []

for pid in player_ids:
  api_url = f'https://kffleague.kz/api/v1/players/{pid}?season_id={season_id}&lang=ru'

  headers = {
      'User-Agent': (
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      ),
      'Accept': 'application/json',
  }

  try:
    response = requests.get(api_url, headers=headers, timeout=1000)
    if response.status_code == 200:
      data = response.json()

      player_info = {
          'id': data.get('id'),
          'first_name': data.get('first_name'),
          'last_name': data.get('last_name'),
          'birthday': data.get('birthday'),
          'age': data.get('age'),
          'position_code': data.get('position_code'),  
          'top_role': data.get('top_role'),  
          'height': data.get('height'),
          'weight': data.get('weight'),
          'jersey_number': data.get('jersey_number'),
          'teams': data.get('teams'),
      }

      complete_players_data.append(player_info)
      print(
          f"Success: ID {pid} ->"
          f" {player_info['first_name']} {player_info['last_name']}"
      )
    else:
      print(f'Error of API for ID {pid}: status {response.status_code}')

    time.sleep(0.5)

  except Exception as e:
    print(f'Error while ID request {pid}: {e}')

with open('target_players_names.json', 'w', encoding='utf-8') as f:
  json.dump(complete_players_data, f, ensure_ascii=False, indent=4)

print('\nВсе данные игроков успешно сохранены в файл target_players_names.json!')
