#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater
from telegram.ext import CommandHandler
import telegram
import logging
import dataset

updater = Updater(token='509175183:AAGXqkUC6V_cjNHdq4puuQwu40HT4sAECUE')
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s -  %(levelname)s - %(message)s', level=logging.INFO)

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Eu sou um bot, mas você pode me entender como uma convolução cíclica multivariável")

def links(bot, update):
    table = db["links"]
    links = table.all()

    if len(list(links)) == 0:
        bot.send_message(chat_id=update.message.chat_id, text="Não existe nenhum link =[")
    else:
        for link in links:
            bot.send_message(chat_id=update.message.chat_id,
                             text = link.name + ": " + link.url)

def add_link(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Qual o nome do seu link?")
    telegram.ForceReply()
    #bot.send_message(chat_id=update.message.chat_id, text="Qual o nome do seu link?")



start_handler = CommandHandler('start', start)
links_handler = CommandHandler('links', links)
add_link_handler = CommandHandler('add_link', add_link)
#    entry_points=[
#    )

dispatcher.add_handler(start_handler)
dispatcher.add_handler(links_handler)
dispatcher.add_handler(add_link_handler)

print("Starting IMEppAgenda")

db = dataset.connect("sqlite:///bot.db");

updater.start_polling()
