#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
from telegram import *
from telegram.ext import *
from bot_restricted import restricted
from bot_db import db
from bot_menu_common import *


ADD_LINK_0, ADD_LINK_1, ADD_PERM_LINK_0, ADD_PERM_LINK_1 = range(4)


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


# TODO(naum): use in list_links
def get_links(count, is_permanent):
    table = db["links"]

    if count == 0: count = table.count()
    links = list(table.find(isPermanent=is_permanent))[-count:]

    return links


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
    user_data['perm'] = False;
    update.message.reply_text(msg)
    return ADD_LINK_1


@restricted
def add_perm_link_step0(bot, update, user_data):
    links_db = db['links']

    msg = ''

    link = update.message.text
    if links_db.count(url=link) != 0:
        msg = 'Link já existente. Envie a nova descrição do link:'
    else:
        msg = 'Envie a descrição do link:'

    user_data['link'] = link
    user_data['perm'] = True;
    update.message.reply_text(msg)
    return ADD_LINK_1


@restricted
def add_link_step1(bot, update, user_data):
    name = update.message.text
    add_link_internal(update, name, user_data['link'], user_data['perm'])
    return ConversationHandler.END


@restricted
def links_menu(bot, update):
    custom_keyboard = [
        [
            InlineKeyboardButton("Add permanent link", callback_data="link add_perm_link"),
            InlineKeyboardButton("Remove permanent link", callback_data="link rem_perm_link_menu"),
        ],
        [
            InlineKeyboardButton("Add link", callback_data="link add_link"),
            InlineKeyboardButton("Remove link", callback_data="link rem_link_menu"),
        ],
        [
            InlineKeyboardButton("« Back", callback_data="config main"),
        ]
    ]

    bot.edit_message_text(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        text='*Config* / *links*',
        reply_markup=InlineKeyboardMarkup(custom_keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

@restricted
def rem_link_list(bot, update, is_permanent):
    links = get_links(0, is_permanent)

    custom_keyboard = []

    for link in links:
        custom_keyboard.append([
            InlineKeyboardButton(
                link['name'] + ": " + link['url'],
                callback_data="link rem_" + ("perm_" if is_permanent else "") + "link " + link['url']
            )
        ])

    custom_keyboard.append([InlineKeyboardButton("« Back", callback_data="config links")])

    header = '*Config* / *links* / '
    if is_permanent: header += "*rem permanent link*"
    else: header += "*rem link*"

    bot.edit_message_text(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        text=header,
        reply_markup=InlineKeyboardMarkup(custom_keyboard),
        parse_mode=ParseMode.MARKDOWN
    )


@restricted
def links_menu_query_result(bot, update):
    query = update.callback_query
    data = query.data.split(' ')

    bot.answer_callback_query(query.id)

    if data[1] == 'add_perm_link':
        update.effective_message.reply_text("Envie o link permanente (/cancel para cancelar):")
        return ADD_PERM_LINK_0

    elif data[1] == 'rem_perm_link_menu':
        rem_link_list(bot, update, True)

    elif data[1] == 'rem_perm_link':
        rem_link_internal(update, data[2])
        rem_link_list(bot, update, True)

    elif data[1] == 'add_link':
        update.effective_message.reply_text("Envie o link (/cancel para cancelar):")
        return ADD_LINK_0

    elif data[1] == 'rem_link_menu':
        rem_link_list(bot, update, False)

    elif data[1] == 'rem_link':
        rem_link_internal(update, data[2])
        rem_link_list(bot, update, False)

    else:
        something_wrong(bot, query.message.chat_id)

    return ConversationHandler.END


links_handler = ConversationHandler(
    entry_points = [CallbackQueryHandler(links_menu_query_result, pattern=r'^\blink\b')],
    states = {
        ADD_LINK_0: [MessageHandler(Filters.text, add_link_step0, pass_user_data=True)],
        ADD_PERM_LINK_0: [MessageHandler(Filters.text, add_perm_link_step0, pass_user_data=True)],
        ADD_LINK_1: [MessageHandler(Filters.text, add_link_step1, pass_user_data=True)]
    },
    fallbacks = [CommandHandler('cancel', cancel)],
    allow_reentry = True
)
