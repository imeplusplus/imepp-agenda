#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
from telegram import *
from telegram.ext import *


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
