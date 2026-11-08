import json
import time
import requests

# 1. Ваши уникальные ID игроков, которые вы собрали из статистики
player_ids = [1366 ,1883, 146]  # замените на ваш реальный список ID
season_id = 200  # актуальный ID сезона из вашей ссылки

complete_players_data = []

for pid in player_ids:
  # Формируем ссылку на официальный API игрока
  api_url = f'https://kffleague.kz/api/v1/players/{pid}?season_id=203&lang=ru'

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

      # Вытаскиваем только те поля, которые понадобятся для модельки
      player_info = {
          'id': data.get('id'),
          'first_name': data.get('first_name'),
          'last_name': data.get('last_name'),
          'birthday': data.get('birthday'),
          'age': data.get('age'),
          'position_code': data.get('position_code'),  # например, 'GK', 'DEF'
          'top_role': data.get('top_role'),  # 'ВР (вратарь)'
          'height': data.get('height'),
          'weight': data.get('weight'),
          'jersey_number': data.get('jersey_number'),
          'teams': data.get('teams'),
      }

      complete_players_data.append(player_info)
      print(
          f"Успешно собрано: ID {pid} ->"
          f" {player_info['first_name']} {player_info['last_name']}"
      )
    else:
      print(f'Ошибка API для ID {pid}: статус {response.status_code}')

    # Небольшая пауза, чтобы не перегружать сервер и избежать блокировки
    time.sleep(0.5)

  except Exception as e:
    print(f'Ошибка при запросе для ID {pid}: {e}')

# 2. Сохраняем готовую базу данных игроков в JSON
with open('target_players_names.json', 'w', encoding='utf-8') as f:
  json.dump(complete_players_data, f, ensure_ascii=False, indent=4)

print('\nВсе данные игроков успешно сохранены в файл target_players_names.json!')