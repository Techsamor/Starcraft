import concurrent.futures
import requests
import os
import csv

# URL для API запроса
api_url = "http://aligulac.com/api/v1/player/?current_rating__isnull=false&current_rating__decay__lt=4&order_by=-current_rating__rating&limit=10&apikey=neVwP5vwrq0OOdwDzQOP"

# Параметры API запроса
params = {
    'appid': 'neVwP5vwrq0OOdwDzQOP'
}


# Функция для загрузки флага
def download_flag(row):
    country_code = row['country']
    if country_code is not None:
        country_code = country_code.lower()
        flag_url = f"http://img.aligulac.com/flags/{country_code}.png"
        response = requests.get(flag_url)
        response.raise_for_status()
        file_path = f"Flags/{row['tag']}.png"  # Путь для сохранения флага
        with open(file_path, 'wb') as file:
            file.write(response.content)

        return file_path
    else:
        return None


# Функция для обработки данных
def processing(row):
    team_name = [team['team']['name'] for team in row['current_teams']]
    writer.writerow(
        [row['tag'], row['name'], row['birthday'], row['race'], ', '.join(team_name), row['total_earnings']])

    flag_image = download_flag(row)
    if flag_image is not None:
        return row, flag_image
    else:
        return row, None


# Отправляем GET запрос к API
res = requests.get(api_url, params=params)
print(res.status_code)
print(res.headers["Content-Type"])
print(res.json())

# Получаем данные из ответа
data = res.json()
flags_directory = "Flags"
stats_directory = "Stats"

# Создаем директории для сохранения флагов и статистики
if not os.path.exists(flags_directory):
    os.makedirs(flags_directory)
if not os.path.exists(stats_directory):
    os.makedirs(stats_directory)
# Путь для сохранения CSV файла
csv_path = os.path.join(stats_directory, 'output.csv')

# Создаем CSV файл и записываем заголовки столбцов
with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Ник', 'Имя', 'Дата', 'Раса', 'Команда', 'Призовые'])

    # Используем ThreadPoolExecutor для параллельной обработки данных
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for row in data['objects']:
            future = executor.submit(processing, row)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            row, flag_image = future.result()
