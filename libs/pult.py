from work_materials.globals import twinks, build_menu
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def build_pult():
    __pult_buttons = []
    for id in list(twinks):
        twink = twinks.get(id)
        __pult_buttons.append(InlineKeyboardButton(twink.username, callback_data='tn {0}'.format(id)))
    reply_markup = InlineKeyboardMarkup(build_menu(__pult_buttons, 3))
    return reply_markup