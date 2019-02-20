#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
from telegram import *
from telegram.ext import *
from bot_db import db


ADD_ADMIN_0, ADD_ADMIN_1, REM_ADMIN, BROADCAST = range(4)


def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        table = db['admins']

        if table.count() != 0:
            user_id = update.effective_user.id
            if not table.find_one(id=user_id):
                bot.send_message(
                    chat_id=update.effective_user.id,
                    text='Acesso negado :('
                )

                if update.callback_query:
                    bot.answer_callback_query(update.callback_query.id)

                return

        return func(bot, update, *args, **kwargs)
    return wrapped


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
def admin(bot, update):
    custom_keyboard = [
        [
            InlineKeyboardButton("Add admin", callback_data="admin add_admin"),
            InlineKeyboardButton("Remove admin", callback_data="admin rem_admin"),
        ],
        [
            InlineKeyboardButton("List admins", callback_data="admin list_admins"),
        ],
        #[
        #    InlineKeyboardButton("Broadcast", callback_data="admin broadcast"),
        #]
    ]

    update.effective_user.send_message(
        text='Admin menu:',
        reply_markup=InlineKeyboardMarkup(custom_keyboard)
    )


@restricted
def query_result(bot, update):
    query = update.callback_query
    data = query.data.split(' ')
    result_type = data[0]
    result_data = data[1]

    bot.answer_callback_query(query.id)

    if result_type == 'admin':
        if result_data == 'add_admin':
            update.effective_message.reply_text("Envie o id do usuário (/cancel para cancelar):")
            return ADD_ADMIN_0
        elif result_data == 'rem_admin':
            update.effective_message.reply_text("Envie o id do usuário (/cancel para cancelar):")
            return REM_ADMIN
        elif result_data == 'list_admins':
            list_admins(bot, update)
            return ConversationHandler.END
        elif result_data == 'broadcast': to_be_implemented(bot, query.message.chat_id)
        else: something_wrong(bot, query.message.chat_id)
    else:
        something_wrong(bot, query.message.chat_id)

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
