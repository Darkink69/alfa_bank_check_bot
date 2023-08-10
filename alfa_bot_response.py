import requests
import json
import time
import datetime as dt
from datetime import datetime
import uni_telegram_bot

TOKEN = "6488210431:AAEu7Gl8xYs_IXZo56IXeqeSYd7HrGAGB9o"
URL = 'https://api.telegram.org/bot'


def time_now():
    return dt.datetime.now().strftime("%D %H:%M:%S")


def timestamp_to_date(tmstmp):
    objectdate = datetime.fromtimestamp(tmstmp)
    return objectdate


def get_updates(offset=0):
    messages = requests.get(f'{URL}{TOKEN}/getUpdates?offset={offset}').json()
    return messages


def reply_keyboard(chat_id, text):
    reply_markup = {"keyboard": [["Условия «Альфа-Вклад»"], ["Условия «Альфа-Счет»"], ["Пригласительные с бонусом"]], "resize_keyboard": True, "one_time_keyboard": True}
    data = {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}
    requests.post(f'{URL}{TOKEN}/sendMessage', data=data)


def add_to_json(messages):
    for message in messages['result']:
        chat_id = message['message']['chat']['id']
        first_name = message['message']['chat']['first_name']
        try:
            username = message['message']['chat']['username']
        except BaseException:
            username = ''
        date = str(timestamp_to_date(message['message']['date']))
        text = message['message']['text']

        data = json.load(open("db_users.json", "r", encoding='utf-8'))
        # print(str(data[0]['id']) + " VS " + str(chat_id))

        all_ids = []
        for id in data:
            all_ids.append(id['id'])

        if chat_id not in all_ids:
            print(f'{time_now()} | Боту написал новый пользователь {first_name}, {username}, id {chat_id}.')
            json_data = {
                "id": chat_id,
                "first_name": first_name,
                "username": username,
                "premium": True,
                "subscript": True,
                "requests": [
                    [
                        {"date": date},
                        {"text": text}
                    ]
                ]
            }
            data.append(json_data)
            with open("db_users.json", "w", encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
        # print(all_ids, 'all ids')

        # last_date = data[0]['requests'][-1][0]['date']
        # if last_date != date:
        #     json_data = [{"date": date}, {"text": text}]
        #     data[0]['requests'].append(json_data)
        #
        #     with open("db_users.json", "w", encoding='utf-8') as file:
        #         json.dump(data, file, indent=2, ensure_ascii=False)


def check_message(chat_id, message, date):
    print(f'{time_now()} | Пользователь с id {chat_id} написал боту: "{message}".')
    if message.lower() in ['условия «альфа-вклад»', 'подробные условия альфа-вклад', 'альфа-вклад', 'вклад']:
        data = json.load(open("db_alfa.json", "r", encoding='utf-8'))
        last_date = data[0]['alfa_rate'][-1]['last_date']
        rate = data[0]['alfa_rate'][-1]['rate']
        url_pdf = data[0]['alfa_rate'][-1]['url_pdf']
        message = f'Последняя редакция условий по Альфа-вкладу от {last_date}\n' \
                  f'Ставки:\n' \
                  f'в рублях - до {rate[0]}%\n' \
                  f'в долларах - {rate[1]}%\n' \
                  f'в евро - {rate[2]}%\n' \
                  f'в юанях - до {rate[3]}%\n\n' \
                  f'Альфа-вклад. Редакция от {last_date} (Полная версия):\n{url_pdf}'
        uni_telegram_bot.send_message(chat_id, message)

    elif message.lower() in ['условия «альфа-счет»', 'подробные условия альфа-счет', 'альфа-счет', 'счет']:
        data = json.load(open("db_alfa.json", "r", encoding='utf-8'))
        last_date = data[1]['alfa_savings_account'][-1]['last_date']
        rate = data[1]['alfa_savings_account'][-1]['rate']
        url_pdf = data[1]['alfa_savings_account'][-1]['url_pdf']
        message = f'Последняя редакция условий по Альфа-счету от {last_date}\n' \
                  f'Ставки в рублях:\n' \
                  f'в период 1-2 месяца - {rate[1]}%\n' \
                  f'в период 3 месяца и более - до {rate[3]}%\n\n' \
                  f'Альфа-счёт. Редакция от {last_date} (Полная версия):\n{url_pdf}'
        uni_telegram_bot.send_message(chat_id, message)

    elif message.lower() in ['пригласительные с бонусом']:
        message = f'Продукты Альфа-Банка с пригласительным бонусом ❤️ \n' \
                  f'(сердечко это 4-й из набора https://t.me/addemoji/AAAAAAAMOJI)\n' \
                  f'Альфа-карта с кешбэком [бесплатное обслуживание, кешбэк до 5+%] +500₽ вам → https://alfa.me/PPLAcU\n' \
                  f'Наша лучшая кредитка [кешбэк, бесплатное обслуживание, год без %] +500₽ вам → https://alfa.me/gDZHMa\n' \
                  f'Счёт для бизнеса [переводы 0 ₽ юрлицам и ИП, минимальная комиссия за эквайринг и кэшбэк до 5%] +2000₽ вам → https://alfa.me/hoMBO4\n' \
                  f'Альфа-Премиум [кешбэк до 7+% и другие премиальные бонусы] +5000₽ вам → https://alfa.me/iG7P_Y'
        uni_telegram_bot.send_message(chat_id, message)

    elif message.lower() in ['отключить рассылку', 'отключить', 'откл', 'рассылку']:
        data_users = json.load(open("db_users.json", "r", encoding='utf-8'))
        for i, user in enumerate(data_users):
            # print(type(user['id']), type(chat_id))
            if user['id'] == chat_id:
                data_users[i]["subscript"] = False
                with open("db_users.json", "w", encoding='utf-8') as file:
                    json.dump(data_users, file, indent=2, ensure_ascii=False)
                uni_telegram_bot.send_message(chat_id, 'Автоматическая рассылка отключена.')

    elif message.lower() in ['включить рассылку', 'включить', 'вкл']:
        data_users = json.load(open("db_users.json", "r", encoding='utf-8'))
        for i, user in enumerate(data_users):
            if user['id'] == chat_id:
                data_users[i]["subscript"] = True
                with open("db_users.json", "w", encoding='utf-8') as file:
                    json.dump(data_users, file, indent=2, ensure_ascii=False)
                uni_telegram_bot.send_message(chat_id, 'Автоматическая рассылка включена.')

    elif message.lower() in ['/start']:
        info = f'Приветствую вас!\n' \
               f'Я бот, который знает все о различных вкладах Альфа банка.\n' \
               f'Я круглосуточно слежу за всеми изменениями на сайте банка и в течении нескольких минут проинформирую вас, если условия вкладов изменились.\n' \
               f'Так же для вас всегда актуальные пригласительные с дополнительным бонусом на оформление карт и РКО.'
        uni_telegram_bot.send_message(chat_id, info)
        reply_keyboard(chat_id, 'Узнайте о условиях вкладов банков.')

    else:
        reply_keyboard(chat_id, 'Узнайте о условиях вкладов банков.')


def run():
    print(f'{time_now()} | Сервер бота запущен.')
    update_id = get_updates()['result'][-1]['update_id']  # Присваиваем ID последнего отправленного сообщения боту
    # update_id = 951251229
    while True:
        time.sleep(15)
        messages = get_updates(update_id)  # Получаем обновления
        for message in messages['result']:
            # Если в обновлении есть ID больше чем ID последнего сообщения, значит пришло новое сообщение
            if update_id < message['update_id']:
                update_id = message['update_id']  # Присваиваем ID последнего отправленного сообщения боту
                # Отвечаем тому кто прислал сообщение боту
                check_message(message['message']['chat']['id'], message['message']['text'], message['message']['date'])
                add_to_json(messages)


if __name__ == '__main__':
    run()






# https://api.telegram.org/bot6082546372:AAHM33fkvArJpe8wU5IQeg0L4jOGNpHJe2Q/getUpdates