#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
from telegram import *
from telegram.ext import *
from bot_db import db

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
