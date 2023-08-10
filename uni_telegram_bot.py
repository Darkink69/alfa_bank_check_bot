import requests
import json

TOKEN = "6488210431:AAEu7Gl8xYs_IXZo56IXeqeSYd7HrGAGB9o"
URL = 'https://api.telegram.org/bot'


def send_message(chat_id, message):
    requests.get(f'{URL}{TOKEN}/sendMessage?chat_id={chat_id}&text={message}')


def send_photo_file(chat_id, img):
    files = {'photo': open(img, 'rb')}
    requests.post(f'{URL}{TOKEN}/sendPhoto?chat_id={chat_id}', files=files)


def send_document(chat_id, doc):
    with open(doc, 'rb') as f:
        files = {'document': f}
        requests.post(f'{URL}{TOKEN}/sendDocument?chat_id={chat_id}', files=files)


def send_photo_url(chat_id, img_url):
    requests.get(f'{URL}{TOKEN}/sendPhoto?chat_id={chat_id}&photo={img_url}')


def send_video_file(chat_id, video):
    files = {'video': open(video, 'rb')}
    requests.post(f'{URL}{TOKEN}/sendVideo?chat_id={chat_id}', files=files)





