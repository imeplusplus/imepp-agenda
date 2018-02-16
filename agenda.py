#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater
from telegram.ext import CommandHandler
import logging

updater = Updater(token='TOKEN')
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s -  %(levelname)s - %(message)s', level=logging.INFO)

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Eu sou um bot, mas você pode me entender como uma convolução cíclica multivariável")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()
