#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
from telegram import *
from telegram.ext import *
from bot_restricted import restricted
from bot_db import db
import bot as app # This avoids cyclic imports


ADD_LINK_0, ADD_LINK_1, REM_LINK = range(3)


def add_link_internal(update, name, link, is_permanent):
    links_db = db['links']
    links_db.upsert(dict(name=name, url=link, isPermanent=is_permanent), ['url'])

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


@restricted
def add_link_step0(bot, update, user_data):
    links_db = db['links']

    msg = ''

    link = update.message.text
    if links_db.count(url=link) != 0:
        msg = 'Link já existente. Envie a nova descrição do link:'
    else:
        msg = 'Envie a descrição do link:'

    user_data['link'] = link
    update.message.reply_text(msg)
    return ADD_LINK_1


@restricted
def add_link_step1(bot, update, user_data):
    name = update.message.text
    add_link_internal(update, name, user_data['link'], False)
    return ConversationHandler.END


@restricted
def rem_link(bot, update):
    rem_link_internal(update, update.message.text)
    return ConversationHandler.END


@restricted
def links_menu(bot, update):
    custom_keyboard = [
        [
            InlineKeyboardButton("Add link", callback_data="link add_link"),
            InlineKeyboardButton("Remove link", callback_data="link rem_link"),
        ],
        [
            InlineKeyboardButton("« Back", callback_data="link back"),
        ]
    ]

    bot.edit_message_text(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        text='*Config* / *links*',
        reply_markup=InlineKeyboardMarkup(custom_keyboard),
        parse_mode=ParseMode.MARKDOWN
    )


def cancel(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Operation cancelled!"
    )
    return ConversationHandler.END


def something_wrong(bot, chat_id):
    bot.send_message(
        chat_id=chat_id,
        text="Houston, we have a problem!"
    )
    return ConversationHandler.END


@restricted
def links_menu_query_result(bot, update):
    query = update.callback_query
    data = query.data.split(' ')[1]

    bot.answer_callback_query(query.id)

    if data == 'add_link':
        update.effective_message.reply_text("Envie o link (/cancel para cancelar):")
        return ADD_LINK_0
    elif data == 'rem_link':
        update.effective_message.reply_text("Envie o link (/cancel para cancelar)")
        return REM_LINK
    elif data == 'back': app.config_menu(bot, update)
    else: something_wrong(bot, query.message.chat_id)

    return ConversationHandler.END


links_handler = ConversationHandler(
    entry_points = [CallbackQueryHandler(links_menu_query_result, pattern=r'^\blink\b')],
    states = {
        ADD_LINK_0: [MessageHandler(Filters.text, add_link_step0, pass_user_data=True)],
        ADD_LINK_1: [MessageHandler(Filters.text, add_link_step1, pass_user_data=True)],
        REM_LINK: [MessageHandler(Filters.text, rem_link)],
    },
    fallbacks = [CommandHandler('cancel', cancel)],
    allow_reentry = True
)
