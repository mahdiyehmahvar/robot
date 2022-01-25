from flask import Response
from flask import request
from flask import Flask
import json
import requests
import os

from bs4 import BeautifulSoup
import requests

# esmfilm = input()
page = requests.get(
    'https://www.imdb.com/search/title/?groups=top_1000&sort=user_rating,desc&count=200&ref_=adv_prv')
moviename = []
imdbrate = []
genere = []
movieyeardict = {}
ratedict = {}
genredict = {}
sumarrydict = {}


soup = BeautifulSoup(page.content, 'html.parser')

data = soup.find_all('div', class_='lister-item mode-advanced')

for i in data:
    name = i.h3.a.text
    moviename.append(name)

    rate = i.find(
        'div', class_='inline-block ratings-imdb-rating').text.replace('\n', '')
    imdbrate.append(rate)
    ratedict.update({name: rate})
    moviegenre = i.p.find('span', class_='genre').text.replace(
        '\n', '').replace(' ', '')
    genere.append(moviegenre)
    genredict.update({name: moviegenre})
    year = i.h3.find('span', class_='lister-item-year text-muted unbold').text
    movieyeardict.update({name: year})
    summary = i.find_all('p', class_='text-muted')
    Summ = summary[1].text
    sumarrydict.update({name: Summ})

# print(movieyeardict.get(esmfilm),ratedict.get(esmfilm),genredict.get(esmfilm),sep=' | ')

url = "https://api.telegram.org/bot5164303840:AAFinWpqK_Nk3_6ZJscImsaL31zoCE0dsyo/"
app = Flask(__name__)


def get_all_updates():
    response = requests.get(url + 'getUpdates')
    return response.json()


def get_last_update(allUpdates):
    return allUpdates['result'][-1]


def get_chat_id(update):
    return update['message']['chat']['id']


def sendmessage(chat_id, text):
    sendData = {'chat_id': chat_id, 'text': text}
    response = requests.post(url + 'sendMessage', sendData)
    return response


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        msg = request.get_json()
        chat_id = get_chat_id(msg)
        text = msg['message'].get('text', '')
        if text == '/start':
            sendmessage(chat_id, 'Enter Movie Name')
        elif 'search' in text:
            esmfilm = text.split(maxsplit=1)[1]
            sendmessage(chat_id, (movieyeardict.get(esmfilm)))
            sendmessage(chat_id, (ratedict.get(esmfilm)))
            sendmessage(chat_id, (genredict.get(esmfilm)))

        elif 'summary' in text:
            esmfilm = text.split(maxsplit=1)[1]
            sendmessage(chat_id, (sumarrydict.get(esmfilm)))
        elif 'add' in text:

            esmfilm = text.split(maxsplit=1)[1]
            list = read_json()
            username = msg['message']['from']['username']
            sendmessage(chat_id, 'Added Successfully')
            if username not in list.keys():
                list[username] = []
            list[username].append(esmfilm)
            write_json(list)
        elif text == 'favoritelist':
            list = read_json()
            username = msg['message']['from']['username']
            if username not in list.keys():
                sendmessage(chat_id, 'Favorite List is Empty')
            else:
                for j in list[username]:
                    sendmessage(chat_id, j)

        else:
            sendmessage(chat_id, 'INVALID REQUEST')
        return Response('ok', status=200)
    else:
        return ''


def write_json(data, filename='favoritelist.json'):
    with open(filename, 'w') as target:
        json.dump(data, target, indent=4, ensure_ascii=False)


def read_json(filename='favoritelist.json'):
    with open(filename, 'r') as target:
        data = json.load(target)
    return data


write_json({})
app.run(debug=True)
#app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
