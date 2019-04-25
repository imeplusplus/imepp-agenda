#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import random
import locale
from functools import wraps
from telegram import *
from telegram.ext import *
from collections import defaultdict

import bot_calendar
from bot_admin import *
from bot_db import db

token = os.environ['TOKEN']

updater = Updater(token=token)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s -  %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

motiveme_media = []
motiveme_custom_media = defaultdict(list)
rating_media = []

USERS = { 'xavi': 366505920, 'naum': 187158190 }

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Eu sou um bot, mas você pode me entender como uma convolução cíclica multivariável")

def show(bot, update, links, isAll):
    if len(links) == 0:
        bot.send_message(
            chat_id = update.message.chat_id,
            text="Não existe nenhum link =[")
    else:
        if not isAll:
            msg = "*IME++ Links*\n"

            total_links = 8
            if len(links) > total_links:
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
            msg = "*IME++ Links*\n"

            for link in links:
                msg += link['name'] + ": " + link['url'] + "\n"

            bot.send_message(
                chat_id = update.message.chat_id,
                text = msg,
                parse_mode = ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )



def permanent_links(bot, update, args):
    table = db["links"]
    links = list(table.find(isPermanent=1))
    if len(args) == 0 or args[0] != 'all' : show(bot, update, links, 0)
    else: show(bot, update, links, 1)

def links(bot, update, args):
    table = db["links"]
    #links = list(table.find(isPermanent=0))
    links = list(table.all())
    if len(args) == 0 or args[0] != 'all' : show(bot, update, links, 0)
    else: show(bot, update, links, 1)

def add_link_internal(update, name, link, isPermanent):
    links_db = db['links']
   # links_db.upsert(dict(name=name, url=link, isPermanent=isPermanent), ['url'])

    links_db.upsert(dict(name=name, url=link), ['url'])
    msg  = "*Link adicionado ou atualizado com sucesso!*\n"
    msg += "Link: " + link + "\n"
    msg += "Descrição: " + name

    update.message.reply_text(
        msg,
        parse_mode = ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )


def rem_link_internal(update, link):
    links_db = db['links']
    links_db.delete(url=link)
    update.message.reply_text("Link removido com sucesso. (Ou não)")

def verify(update, link):
    if "http" not in link:
        update.effective_message.reply_text(
            "Comando incorreto.\nIsso não é um link"
        )
        return 0
    return 1

@restricted
def add_link_permanent(bot, update, args):
    if len(args) < 2:
        update.effective_message.reply_text(
        "Comando incorreto.\nUso: /add_link_permanent <nome do link> <link>"
        )
        return

    link = args[-1]
    if not verify(update, link): return

    name = ' '.join(args[:-1])
    add_link_internal(update, name, link, 1)

@restricted
def add_link_right(bot, update, args): 
    if len(args) < 2:
        update.effective_message.reply_text(
            "Comando incorreto.\nUso: /real_add_link <nome do link> <link>"
        )
        return

    link = args[-1]
    if not verify(update, link): return

    name = ' '.join(args[:-1])
    add_link_internal(update, name, link, 0)


@restricted
def add_link(bot, update, args):
    if len(args) < 2:
        update.effective_message.reply_text(
            "Comando incorreto.\nUso: /add_link <link> <nome do link>"
        )
        return

    link = args[0]
    if not verify(update, link): return
    
    name = ' '.join(args[1:])
    add_link_internal(update, name, link, 0)


@restricted
def rem_link(bot, update, args):
    if len(args) < 1:
        update.effective_message.reply_text(
            "Comando incorreto.\nUso: /remove_link <link>"
        )
        return

    link = args[0]
    if not verify(update, link): return

    links_db = db['links']
    if not links_db.find_one(url=link):
        update.effective_message.reply_text(
            "Este link não está na lista"
        )
        return
    
    rem_link_internal(update, link)


def events(bot, update):
    msg = bot_calendar.get_events(6)
    bot.send_message(
        chat_id = update.message.chat_id,
        text = msg,
        parse_mode = ParseMode.HTML,
        disable_web_page_preview=True
    )


def load_media():
    motiveme_media.append(('image', 'media/AC_cf.png'))
    motiveme_media.append(('image', 'media/AC_uri.png'))
    motiveme_media.append(('image', 'media/AC_uva.png'))
    motiveme_media.append(('image', 'media/AC_yandex_open.png'))
    motiveme_media.append(('image', 'media/AC_yandex_blind.png'))
    motiveme_media.append(('image', 'media/mistermax.png'))
    motiveme_media.append(('image', 'media/last-min.jpg'))
    motiveme_media.append(('video', 'media/dreams.mp4'))
    motiveme_media.append(('video', 'media/yes-you-can.mp4'))
    motiveme_media.append(('video', 'media/nothing-is-impossible.mp4'))

    motiveme_custom_media[USERS['xavi']].append(('image', 'media/yellow_xavi.png'))

    rating_media.append(('image', 'media/no-rating0.jpg'))
    rating_media.append(('image', 'media/no-rating1.jpg'))
    rating_media.append(('image', 'media/no-rating2.jpg'))


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

def my_id(bot, update):
    bot.send_message(chat_id=update.message.from_user.id,
                     text="User ID: " + str(update.message.from_user.id))

def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Comando não reconhecido :(")


if __name__ == "__main__":
    print("Starting IMEppAgenda")
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF8')

    load_media()

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('links', links, pass_args=True))
    dispatcher.add_handler(CommandHandler('permanent_links', permanent_links, pass_args=True))
    dispatcher.add_handler(CommandHandler('events', events))
    dispatcher.add_handler(CommandHandler('motiveme', motiveme))
    dispatcher.add_handler(CommandHandler('norating', norating))
    dispatcher.add_handler(CommandHandler('givehint', givehint))
    dispatcher.add_handler(CommandHandler('my_id', my_id))

    dispatcher.add_handler(CommandHandler('add_link', add_link, pass_args=True))
    dispatcher.add_handler(CommandHandler('real_add_link', add_link_right, pass_args=True))
    dispatcher.add_handler(CommandHandler('add_link_permanent', add_link_permanent, pass_args=True)) 
    dispatcher.add_handler(CommandHandler('rem_link', rem_link, pass_args=True))
    dispatcher.add_handler(CommandHandler('admin', admin))

    query_result_handler = CallbackQueryHandler(query_result)
    dispatcher.add_handler(
        ConversationHandler(
            entry_points = [CallbackQueryHandler(query_result)],
            states = {
                ADD_ADMIN_0: [MessageHandler(Filters.text, add_admin_step0, pass_user_data=True)],
                ADD_ADMIN_1: [MessageHandler(Filters.text, add_admin_step1, pass_user_data=True)],
                REM_ADMIN: [MessageHandler(Filters.text, rem_admin)],
            },
            fallbacks = [CommandHandler('cancel', cancel)],
            allow_reentry = True
        )
    )

    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()
