import telebot
import requests
from init import BOT_TOKEN, cursor, conn
import datetime
from datetime import timedelta
from io import BytesIO
import matplotlib.pyplot as plt
import re
import json

bot = telebot.TeleBot(BOT_TOKEN)
regex_for_plot = r'^\/history\s+USD\/([A-Z]{3})\s+for\s+(\d+)\s+days$'
link_for_plt = 'https://api.exchangeratesapi.io/history?start_at={}&end_at={}&base=USD&symbols={}'
link_for_list = 'https://api.exchangeratesapi.io/latest?base=USD'


def check_exchange_message(params):
    if len(params) == 4 and params[0].isdigit() and params[2] == 'to':
        return int(params[0]), params[1], params[3]
    elif len(params) == 3 and params[0][0] == '$' and params[0][1:].isdigit() and params[1] == 'to':
        return int(params[0][1:]), 'USD', params[2]
    else:
        return None


def check_plot_message(command):
    match = re.search(regex_for_plot, command)
    if match:
        return match.group(1), match.group(2)
    return None


@bot.message_handler(commands=['list', 'lst'])
def list_message(message):
    cur_day = datetime.datetime.now()
    cursor.execute('SELECT * FROM history ORDER BY download_time DESC LIMIT 1;')
    last_download = cursor.fetchall()
    if last_download and cur_day - last_download[0][0] < timedelta(minutes=10):
        answer = '\n'.join(
            ['{}: {}'.format(key, round(value, 2)) for key, value in json.loads(last_download[0][1])['rates'].items()])
    else:
        rates = requests.get(link_for_list)
        if rates.ok:
            answer = '\n'.join(['{}: {}'.format(key, round(value, 2)) for key, value in rates.json()['rates'].items()])
            cursor.execute("INSERT INTO history VALUES ('{}', '{}');".format(
                cur_day.strftime("%Y-%m-%d %H:%M:%S"),
                json.dumps(rates.json())))
            conn.commit()
        else:
            answer = "Try later again."
    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=['exchange'])
def exchange_message(message):
    params = check_exchange_message(message.text.split()[1:])
    if params:
        cursor.execute('SELECT * FROM history ORDER BY download_time DESC LIMIT 1;')
        last_download = cursor.fetchall()
        if last_download:
            rates = json.loads(last_download[0][1])
        else:
            rates = requests.get('https://api.exchangeratesapi.io/latest?base=USD')
            if rates.ok:
                cursor.execute("INSERT INTO history VALUES ('{}', '{}');".format(
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    json.dumps(rates.json())))
                conn.commit()
                rates = rates.json()
            else:
                bot.send_message(message.chat.id, "Try later again.")
                return
        currency = rates['rates'].get(params[2])
        if currency and params[1] == 'USD':
            bot.send_message(message.chat.id, '{} {}'.format(round(currency * params[0], 2), params[2]))
            return
        currency = rates['rates'].get(params[1])
        if currency and params[2] == 'USD':
            bot.send_message(message.chat.id, '{} {}'.format(round(currency / params[0], 2), params[1]))
            return
    bot.send_message(message.chat.id, "Try again.")


@bot.message_handler(commands=['history'])
def plot_message(message):
    params = check_plot_message(message.text)
    if params:
        cur_day = datetime.datetime.now()
        rates = requests.get(link_for_plt.format((cur_day - timedelta(days=int(params[1]))).strftime("%Y-%m-%d"),
                                                 cur_day.strftime("%Y-%m-%d"),
                                                 params[0]))
        if rates.ok:
            plt.plot([i[1][params[0]] for i in (sorted(rates.json()['rates'].items()))])
            plt.title('USD/{}'.format(params[0]))
            buffer = BytesIO()
            buffer.name = 'image.jpeg'
            plt.savefig(buffer)
            buffer.seek(0)
            bot.send_photo(message.chat.id, buffer)
            plt.close()
            buffer.close()
            return
    bot.send_message(message.chat.id, "Try again.")


if __name__ == "__main__":
    bot.polling()
