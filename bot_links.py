
'''
# BACKUP
ADD_LINK_0, ADD_LINK_1, REM_LINK, ADD_ADMIN_0, ADD_ADMIN_1, REM_ADMIN, BROADCAST = range(7)

#ADD_LINK_0: [MessageHandler(Filters.text, add_link_step0, pass_user_data=True)],
#ADD_LINK_1: [MessageHandler(Filters.text, add_link_step1, pass_user_data=True)],
#REM_LINK: [MessageHandler(Filters.text, rem_link)],

@restricted
def add_link_step0(bot, update, user_data):
    links_db = db['links']

    msg = ''

    link = update.message.text
    if links_db.count(url=link) != 0:
        msg = 'Link já existente.\nEnvie a nova descrição do link:'
    else:
        msg = 'Envie a descrição do link:'

    user_data['link'] = link
    update.message.reply_text(msg)
    return ADD_LINK_1


@restricted
def add_link_step1(bot, update, user_data):
    add_link_internal(update, name, link)
    return ConversationHandler.END


@restricted
def rem_link(bot, update):
    rem_link_internal(update, update.message.text)
    return ConversationHandler.END


def config(bot, update):
    custom_keyboard = [
        [
            InlineKeyboardButton("Add link", callback_data="admin add_link"),
            InlineKeyboardButton("Remove link", callback_data="admin rem_link"),
        ],
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
        text='Configuração:',
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
        if result_data == 'add_link':
            update.effective_message.reply_text("Envie o link (/cancel para cancelar):")
            return ADD_LINK_0
        elif result_data == 'rem_link':
            update.effective_message.reply_text("Envie o link (/cancel para cancelar)")
            return REM_LINK
        elif result_data == 'add_admin':
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
'''
