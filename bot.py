#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import dataset
from functools import wraps
from telegram import *
from telegram.ext import *

import locale
import bot_calendar

token = os.environ['TOKEN']

updater = Updater(token=token)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s -  %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

ADMINS = [366505920, 187158190, 120847148, 445765305]

def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ADMINS:
            bot.send_message(
                char_id = update.message.chat_id,
                text = "*Acesso negado.*",
                parse_mode = ParseMode.MARKDOWN
            )
            return
        return func(bot, update, *args, **kwargs)
    return wrapped

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Eu sou um bot, mas você pode me entender como uma convolução cíclica multivariável")

def links(bot, update, args):
    table = db["links"]
    links = list(table.all())

    if len(links) == 0:
        bot.send_message(
            chat_id = update.message.chat_id,
            text="Não existe nenhum link =[")
    else:
        if len(args) == 1:
            if args[0] == "all":
                msg = "*IME++ Links*\n"

                for link in links:
                    msg += link['name'] + ": " + link['url'] + "\n"

                bot.send_message(
                    chat_id = update.message.chat_id,
                    text = msg,
                    parse_mode = ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
        else:
            msg = "*IME++ Links*\n"
            msg += "Mostrando últimos 5 links\nUse `/links all` para mostrar todos\n\n"

            for i in range(max(-5, -len(links)), 0):
                msg += links[i]['name'] + ": " + links[i]['url'] + "\n"

            bot.send_message(
                chat_id = update.message.chat_id,
                text = msg,
                parse_mode = ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )

def events(bot, update):
    msg = bot_calendar.get_events(6)
    bot.send_message(
        chat_id = update.message.chat_id,
        text = msg,
        parse_mode = ParseMode.HTML,
        disable_web_page_preview=True
    )


@restricted
def add_link(bot, update, args):
    if len(args) < 2:
        bot.send_message(
            chat_id = update.message.chat_id,
            text = "Comando incorreto.\nUso: /add_link <link> <nome do link>"
        )
    else:
        links_db = db['links']

        link = args[0]
        name = ' '.join(args[1:])

        links_db.insert(dict(name=name, url=link))

        msg  = "*Link adicionado com sucesso!*\n"
        msg += "Nome do link: " + name + "\n"
        msg += "Link: " + link

        bot.send_message(
            chat_id = update.message.chat_id,
            text = msg,
            parse_mode = ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )


@restricted
def remove_link(bot, update, args):
    if len(args) < 1:
        bot.send_message(
            chat_id = update.message.chat_id,
            text = "Comando incorreto.\nUso: /remove_link <link> [links extra]"
        )
    else:
        links_db = db['links']

        for url in args:
            links_db.delete(url=url)

        bot.send_message(
            chat_id = update.message.chat_id,
            text = "Links removidos com sucesso. (Ou nao)"
        )


if __name__ == "__main__":
    print("Starting IMEppAgenda")
    locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('links', links, pass_args=True))
    dispatcher.add_handler(CommandHandler('add_link', add_link, pass_args=True))
    dispatcher.add_handler(CommandHandler('remove_link', remove_link, pass_args=True))
    dispatcher.add_handler(CommandHandler('events', events))

    db = dataset.connect("sqlite:///bot.db");

    updater.start_polling()
