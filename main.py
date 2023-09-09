import concurrent.futures
import requests
import csv

api_url = "http://aligulac.com/api/v1/player/?current_rating__isnull=false&current_rating__decay__lt=4&order_by=-current_rating__rating&limit=500&apikey=neVwP5vwrq0OOdwDzQOP"

params = {
    'appid': 'neVwP5vwrq0OOdwDzQOP'
}


def download_flag(row):
    country_code = row['country']
    if country_code is not None:
        country_code = country_code.lower()
        flag_url = f"http://img.aligulac.com/flags/{country_code}.png"
        response = requests.get(flag_url)
        response.raise_for_status()
        file_path = f"flags/{row['tag']}.png"  # Путь для сохранения флага
        with open(file_path, 'wb') as file:
            file.write(response.content)

        return file_path
    else:
        return None


def processing(row):
    team_name = [team['team']['name'] for team in row['current_teams']]
    writer.writerow(
        [row['tag'], row['name'], row['birthday'], row['race'], ', '.join(team_name), row['total_earnings']])

    flag_image = download_flag(row)
    if flag_image is not None:
        return row, flag_image
    else:
        return row, None


res = requests.get(api_url, params=params)
print(res.status_code)
print(res.headers["Content-Type"])
print(res.json())

data = res.json()
flags_directory = "flags"

with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Ник', 'Имя', 'Дата', 'Раса', 'Команда', 'Призовые'])

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for row in data['objects']:
            future = executor.submit(processing, row)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            row, flag_image = future.result()
