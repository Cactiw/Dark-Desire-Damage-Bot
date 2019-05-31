from work_materials.globals import twinks as twinks_const, build_menu, castles as castles_const, status_default
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from libs.twink import Twink

castles = ['🍁', '☘', '🖤', '🐢', '🦇', '🌹', '🍆']


class Pult:
    pults = {}

    def __init__(self, chat_id, message_id, real_account=False):
        self.chat_id = chat_id
        self.message_id = message_id
        self.real_account = real_account

        self.status = status_default.copy()
        self.castles = castles_const.copy()
        self.twinks = {}
        for key in list(twinks_const):
            twink = twinks_const.get(key)
            new_twink = Twink(twink.castle, twink.target, twink.username, twink.telegram_id, twink.current_castle,
                              twink.real_account)
            self.twinks.update({key: new_twink})
        print("self.twinks =", self.twinks)

        Pult.pults.update({self.chat_id: self})

    @staticmethod
    def get_pult(chat_id):
        return Pult.pults.get(chat_id)


def build_pult(pult):
    castles = pult.castles
    twinks = pult.twinks
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
    print(pult.real_account)
    print(twinks)
    if not pult.real_account:
        for id in list(twinks):
            twink = twinks.get(id)
            if twink.real_account:
                continue
            print(twink.current_castle)
            __pult_buttons.append(InlineKeyboardButton(twink.current_castle + twink.username, callback_data='ptn {0}'.format(id)))
        menu = build_menu(__pult_buttons, 3)
        for castle_row in __castle_buttons:
            menu.append(castle_row)
    else:
        menu = __castle_buttons
    reply_markup = InlineKeyboardMarkup(menu)
    return reply_markup


def rebuild_pult(action, context, pult):
    twinks = pult.twinks
    castles = pult.castles
    if action == "change_twink":
        for id in list(twinks):
            twink = twinks.get(id)
            twink_const = twinks_const.get(id)
            twink.username = twink_const.username
            twinks.update({id: twink})
        twink = twinks.get(context)
        twink.username = '✅' + twink.username
        new_markup = build_pult(pult)
        return new_markup
    if action == "change_target":
        for i in range (0, len(castles)):
            castles[i] = castles_const[i]
        castles[context] = '✅' + castles[context]
        new_markup = build_pult(pult)
        return new_markup

    if action == "default":
        temp_pult = Pult(0, 0)
        return build_pult(temp_pult)
    if action == "current":
        return build_pult(pult)
