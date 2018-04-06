#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import dataset
import random
from functools import wraps
from telegram import *
from telegram.ext import *
from collections import defaultdict

import locale
import bot_calendar

token = os.environ['TOKEN']

updater = Updater(token=token)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s -  %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

motiveme_media = []
motiveme_custom_media = defaultdict(list)
rating_media = []

USERS = { 'xavi': 366505920, 'naum': 187158190 }

ADMINS = [USERS['xavi'], USERS['naum'], 120847148, 445765305]

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
        if len(args) == 0:
            total_links = 8

            msg = "*IME++ Links*\n"
            msg += "Mostrando últimos " + str(total_links) + " links\nUse `/links all` para mostrar todos\n\n"

            for i in range(max(-total_links, -len(links)), 0):
                msg += links[i]['name'] + ": " + links[i]['url'] + "\n"

            bot.send_message(
                chat_id = update.message.chat_id,
                text = msg,
                parse_mode = ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )

        else:
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
                bot.send_message(
                    chat_id = update.message.chat_id,
                    text="Argumentos não reconhecidos.\nUse `/links [all]` para receber os links",
                    parse_mode = ParseMode.MARKDOWN)

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


def load_media():
    motiveme_media.append(('image', 'media/AC_cf.png'))
    motiveme_media.append(('image', 'media/AC_uri.png'))
    motiveme_media.append(('image', 'media/AC_uva.png'))
    motiveme_media.append(('image', 'media/AC_yandex_open.png'))
    motiveme_media.append(('image', 'media/AC_yandex_blind.png'))
    motiveme_media.append(('image', 'media/mistermax.png'))
    motiveme_media.append(('video', 'media/dreams.mp4'))
    motiveme_media.append(('video', 'media/yes-you-can.mp4'))
    motiveme_media.append(('video', 'media/nothing-is-impossible.mp4'))

    motiveme_custom_media[USERS['xavi']].append(('image', 'media/yellow_xavi.png'))

    rating_media.append(('image', 'media/no-rating0.jpg'))
    rating_media.append(('image', 'media/no-rating1.jpg'))


def send_random_media(bot, update, media):
    t, n = random.choice(media)
    if t == 'image': bot.send_photo(chat_id=update.message.chat_id, photo=open(n, 'rb'))
    if t == 'video': bot.send_video(chat_id=update.message.chat_id, video=open(n, 'rb'))


def motiveme(bot, update):
    media = motiveme_media

    user_id = update.effective_user.id
    if user_id in motiveme_custom_media:
        media = motiveme_custom_media[user_id]

    send_random_media(bot, update, media)


def norating(bot, update):
    send_random_media(bot, update, rating_media)


def givehint(bot, update):
    bot.send_photo(chat_id=update.message.chat_id, photo=open('media/new-hobby.png', 'rb'))


def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Comando não reconhecido :(")


if __name__ == "__main__":
    print("Starting IMEppAgenda")
    locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')

    load_media()

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('links', links, pass_args=True))
    dispatcher.add_handler(CommandHandler('add_link', add_link, pass_args=True))
    dispatcher.add_handler(CommandHandler('remove_link', remove_link, pass_args=True))
    dispatcher.add_handler(CommandHandler('events', events))
    dispatcher.add_handler(CommandHandler('motiveme', motiveme))
    dispatcher.add_handler(CommandHandler('norating', norating))
    dispatcher.add_handler(CommandHandler('givehint', givehint))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    db = dataset.connect("sqlite:///bot.db");

    updater.start_polling()
