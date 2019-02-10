from work_materials.globals import twinks as twinks_const, build_menu, castles as castles_const
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from libs.twink import Twink

twinks = {}
castles = ['🍁', '☘', '🖤', '🐢', '🦇', '🌹', '🍆']

def build_pult(twinks, castles):
    __pult_buttons = []
    __castle_buttons = [
        [
            InlineKeyboardButton(castles[0], callback_data="pc0"),
            InlineKeyboardButton(castles[1], callback_data="pc1"),
            InlineKeyboardButton(castles[2], callback_data="pc2"),
        ],
        [
            InlineKeyboardButton(castles[3], callback_data="pc3"),
            InlineKeyboardButton(castles[4], callback_data="pc4"),
            InlineKeyboardButton(castles[5], callback_data="pc5"),
        ],
        [
            InlineKeyboardButton(castles[6], callback_data="pc6"),
        ],
        [
            InlineKeyboardButton("🆗 Подтвердить", callback_data="pok"),
        ]
    ]
    for id in list(twinks):
        twink = twinks.get(id)
        __pult_buttons.append(InlineKeyboardButton(twink.username, callback_data='ptn {0}'.format(id)))
    menu = build_menu(__pult_buttons, 3)
    for castle_row in __castle_buttons:
        menu.append(castle_row)
    reply_markup = InlineKeyboardMarkup(menu)
    return reply_markup

def rebuild_pult(action, context):
    if action == "change_twink":
        for id in list(twinks):
            twink = twinks.get(id)
            twink_const = twinks_const.get(id)
            twink.username = twink_const.username
            twinks.update({id : twink})
        twink = twinks.get(context)
        twink.username = '✅' + twink.username
        new_markup = build_pult(twinks, castles)
        return new_markup
    if action == "change_target":
        for i in range (0, len(castles)):
            castles[i] = castles_const[i]
        castles[context] = '✅' + castles[context]
        new_markup = build_pult(twinks, castles)
        return new_markup

    if action == "default":
        twinks.clear()
        for key in list(twinks_const):
            twink = twinks_const.get(key)
            new_twink = Twink(twink.castle, twink.target, twink.username)
            twinks.update({key : new_twink})
        for i in range(0, len(castles)):
            castles[i] = castles_const[i]
        return build_pult(twinks, castles)
    if action == "current":
        return build_pult(twinks, castles)
