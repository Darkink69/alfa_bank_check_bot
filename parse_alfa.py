from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import datetime as dt
import json
import requests
import uni_telegram_bot

# chat_ids = ["813012401", "861583531"]
# chat_ids = ["813012401"]
chat_ids = []


def load_users():
    data_users = json.load(open("db_users.json", "r", encoding='utf-8'))
    for user in data_users:
        if user['subscript']:
            chat_ids.append(user['id'])
    return chat_ids


def time_now():
    return dt.datetime.now().strftime("%D %H:%M:%S")


def add_to_json(data_index, data_key, last_date, rate, url_pdf, message):
    data = json.load(open("db_alfa.json", "r", encoding='utf-8'))
    if data[data_index][data_key][-1]['last_date'] != last_date:
        print(f'{time_now()} | В Н И М А Н И Е ! Обнаружены изменения в условиях на сайте банка на странице {data_key}')
        send_telegram_message('Внимание! Опубликованы новые условия!')
        send_telegram_message(message)
        print(f'{time_now()} | Сообщения о изменении условий отправлены в телеграмм')

        json_data = {
            "last_date": last_date,
            "rate": rate,
            "url_pdf": url_pdf
        }
        data[data_index][data_key].append(json_data)

        with open("db_alfa.json", "w", encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        print(f'{time_now()} | Запись о новых условиях внесена в базу данных')

        save_pdf(url_pdf)

    else:
        print(f'{time_now()} | Нет изменений условий на сайте банка на странице {data_key}')


def parse_deposits():
    link = 'https://alfabank.ru/make-money/deposits/alfa/'
    driver = webdriver.Chrome()
    driver.get(link)

    data_index = 0
    data_key = 'alfa_rate'

    try:
        elements = driver.find_elements(By.LINK_TEXT, 'Подробные условия по Альфа-Вкладу')
        for element in elements:
            url_pdf = element.get_attribute("outerHTML").split('"')[3]
        # print(url_pdf)

        last_date = (url_pdf[-12:-4])[:2] + '.' + (url_pdf[-12:-4])[2:4] + '.' + (url_pdf[-12:-4])[4:]
        # print(last_date)

        elements = driver.find_elements(By.CLASS_NAME, 'd2lIQ')
        rate = []
        for element in elements:
            rate.append(element.get_attribute("outerHTML").split('">')[16][:4])
        # print(rate)
    except BaseException:
        print(f'{time_now()} | О Ш И Б К А ! Не удалось получить информацию со страницы «Альфа-Вклад»')

        last_date, rate, url_pdf = load_last_json(data_index, data_key)

        message = 'Ошибка парсинга страницы «Альфа-Вклад»'
        chat_ids = ["813012401", "861583531"]
        for chat_id in chat_ids:
            uni_telegram_bot.send_message(chat_id, message)


    message = f'Последняя редакция условий по Альфа-вкладу от {last_date}\n' \
              f'Ставки:\n' \
              f'в рублях - до {rate[0]}%\n' \
              f'в долларах - {rate[1]}%\n' \
              f'в евро - {rate[2]}%\n' \
              f'в юанях - до {rate[3]}%\n\n' \
              f'Альфа-вклад. Редакция от {last_date} (Полная версия):\n{url_pdf}\n\n' \
              f'Чтобы отключить автоматическую рассылку изменений условий банка в реальном времени, напишите боту:\n' \
              f'Отключить рассылку.'

    return data_index, data_key, last_date, rate, url_pdf, message


def parse_savings_account():
    link = 'https://alfabank.ru/make-money/savings-account/alfa/'
    driver = webdriver.Chrome()
    driver.get(link)

    data_index = 1
    data_key = 'alfa_savings_account'

    try:
        elements = driver.find_elements(By.LINK_TEXT, 'Подробные условия')
        for element in elements:
            url_pdf = element.get_attribute("outerHTML").split('"')[9]
        # print(url_pdf)

        last_date = (url_pdf[-12:-4])[:2] + '.' + (url_pdf[-12:-4])[2:4] + '.' + (url_pdf[-12:-4])[4:]
        # print(last_date)

        elements = driver.find_elements(By.CLASS_NAME, 'g1Hrp')
        rate = []
        for element in elements:
            x = element.get_attribute("outerHTML").split('">')[-1]
            if '%' in x:
                rate.append(x.split('<!')[0])
        # print(rate)
    except BaseException:
        print(f'{time_now()} | О Ш И Б К А ! Не удалось получить информацию со страницы «Альфа-Счет»')

        last_date, rate, url_pdf = load_last_json(data_index, data_key)

        message = 'Ошибка парсинга страницы «Альфа-Счет»'
        chat_ids = ["813012401", "861583531"]
        for chat_id in chat_ids:
            uni_telegram_bot.send_message(chat_id, message)


    message = f'Последняя редакция условий по Альфа-счету от {last_date}\n' \
              f'Ставки в рублях:\n' \
              f'в период 1-2 месяца - {rate[1]}%\n' \
              f'в период 3 месяца и более - до {rate[3]}%\n\n' \
              f'Альфа-счёт. Редакция от {last_date} (Полная версия):\n{url_pdf}\n\n'\
              f'Чтобы отключить автоматическую рассылку изменений условий банка в реальном времени, напишите боту:\n'\
              f'Отключить рассылку.'

    return data_index, data_key, last_date, rate, url_pdf, message


def send_telegram_message(message):
    for chat_id in chat_ids:
        uni_telegram_bot.send_message(chat_id, message)


def save_pdf(url_pdf):
    try:
        r = requests.get(url_pdf)
        name_pdf = url_pdf.split('/')[-1]

        with open(f'pdf/{name_pdf}', 'wb') as f:
            f.write(r.content)
        print(f'{time_now()} | Файл pdf сохранен в папку')
    except BaseException:
        print(f'{time_now()} | Не удалось скачать pdf-файл')


def load_last_json(data_index, data_key):
    data = json.load(open("db_alfa.json", "r", encoding='utf-8'))
    last_date = data[data_index][data_key][-1]['last_date']
    rate = data[data_index][data_key][-1]['rate']
    url_pdf = data[data_index][data_key][-1]['url_pdf']

    return last_date, rate, url_pdf


print(f'{time_now()} | Сервер запущен')
print(f'{time_now()} | Автоматическая рассылка включена у {len(load_users())} пользователей(ля).')


for i in range(100000):
    chat_ids = load_users()
    data_index, data_key, last_date, rate, url_pdf, message = parse_deposits()
    add_to_json(data_index, data_key, last_date, rate, url_pdf, message)

    data_index, data_key, last_date, rate, url_pdf, message = parse_savings_account()
    add_to_json(data_index, data_key, last_date, rate, url_pdf, message)

    time.sleep(3600)




