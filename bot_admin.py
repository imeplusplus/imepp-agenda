#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
from telegram import *
from telegram.ext import *
from bot_restricted import restricted
from bot_db import db
import bot as app # This avoids cyclic imports


ADD_ADMIN_0, ADD_ADMIN_1, REM_ADMIN, BROADCAST = range(4)


@restricted
def add_admin_step0(bot, update, user_data):
    admins_db = db['admins']
    user_id = int(update.message.text)

    if admins_db.count(id=user_id) != 0:
        update.message.reply_text('Usuário já é admin!')
        return ConversationHandler.END

    user_data['id'] = user_id
    update.message.reply_text('Envie nome do usuário:')
    return ADD_ADMIN_1


@restricted
def add_admin_step1(bot, update, user_data):
    admins_db = db['admins']

    name = update.message.text
    user_id = user_data['id']
    del user_data['id']

    admins_db.upsert(dict(name=name, id=user_id), ['id'])

    update.message.reply_text('Admin adicionado com sucesso!')

    return ConversationHandler.END


@restricted
def rem_admin(bot, update):
    admins_db = db['admins']
    admins_db.delete(id=int(update.message.text))

    update.message.reply_text("Admin removido com sucesso. (Ou não)")

    return ConversationHandler.END


@restricted
def list_admins(bot, update):
    admins_db = db['admins']
    admins = list(admins_db.all())

    if len(admins) == 0:
        update.effective_message.reply_text("Não existem admins =[")
    else:
        msg = "*Admins*:\n"

        for admin in admins:
            msg += admin['name'] + " - " + str(admin['id']) + "\n"

        update.effective_message.reply_text(
            msg,
            parse_mode = ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )


@restricted
def admins_menu(bot, update):
    custom_keyboard = [
        [
            InlineKeyboardButton("Add admin", callback_data="admin add_admin"),
            InlineKeyboardButton("Remove admin", callback_data="admin rem_admin"),
        ],
        [
            InlineKeyboardButton("List admins", callback_data="admin list_admins"),
            InlineKeyboardButton("« Back", callback_data="admin back"),
        ],
        #[
        #    InlineKeyboardButton("Broadcast", callback_data="admin broadcast"),
        #]
    ]

    bot.edit_message_text(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        text='*Config* / *admins*',
        reply_markup=InlineKeyboardMarkup(custom_keyboard),
        parse_mode=ParseMode.MARKDOWN
    )


@restricted
def admins_menu_query_result(bot, update):
    query = update.callback_query
    data = query.data.split(' ')[1]

    bot.answer_callback_query(query.id)

    if data == 'add_admin':
        update.effective_message.reply_text("Envie o id do usuário (/cancel para cancelar):")
        return ADD_ADMIN_0
    elif data == 'rem_admin':
        update.effective_message.reply_text("Envie o id do usuário (/cancel para cancelar):")
        return REM_ADMIN
    elif data == 'list_admins': list_admins(bot, update)
    elif data == 'broadcast': to_be_implemented(bot, query.message.chat_id)
    elif data == 'back': app.config_menu(bot, update)
    else: something_wrong(bot, query.message.chat_id)

    return ConversationHandler.END


def cancel(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Operation cancelled!"
    )
    return ConversationHandler.END


def to_be_implemented(bot, chat_id):
    bot.send_message(
        chat_id=chat_id,
        text="To be implemented!"
    )


def something_wrong(bot, chat_id):
    bot.send_message(
        chat_id=chat_id,
        text="Houston, we have a problem!"
    )
    return ConversationHandler.END


admins_handler = ConversationHandler(
    entry_points = [CallbackQueryHandler(admins_menu_query_result, pattern=r'^\badmin\b')],
    states = {
        ADD_ADMIN_0: [MessageHandler(Filters.text, add_admin_step0, pass_user_data=True)],
        ADD_ADMIN_1: [MessageHandler(Filters.text, add_admin_step1, pass_user_data=True)],
        REM_ADMIN: [MessageHandler(Filters.text, rem_admin)],
    },
    fallbacks = [CommandHandler('cancel', cancel)],
    allow_reentry = True
)
