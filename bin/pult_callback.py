from telegram.error import BadRequest, Unauthorized, TelegramError
from work_materials.globals import twinks, cursor, local_tz, moscow_tz, castles
from libs.pult import Pult, rebuild_pult
import logging, traceback, datetime


def get_pult_text(user_id=None):
    if user_id is None:
        # Запрос на пульт для управления твинками
        response = "Текущие цели:\n"
        for key in twinks:
            twink = twinks.get(key)
            if twink.real_account:
                continue
            response += "{3}<code>{0:<12}</code> {1:>10} - {2}\n".format(twink.username, twink.castle, twink.target,
                                                                         twink.current_castle)
    else:
        # Запрос на пульт для сообщения боту текущей цели атаки конкретного аккаунта
        response = "Выбранная цель:\n"
        twink = twinks.get(user_id)
        response += "{3}<b>{0:<12}</b> {1:>10} - {2}\n".format(twink.username, twink.castle, twink.target,
                                                               twink.current_castle)
    return response


def pult(bot, update):
    pult = Pult(update.message.chat_id, update.message.message_id)
    pult.status.update({"twink": -1, "target": -1})
    response = get_pult_text(user_id=None)
    bot.send_message(chat_id=update.message.chat_id, text = response + "\n{0}".format(datetime.datetime.now(tz=moscow_tz)),
                     reply_markup=rebuild_pult("default", None, pult), parse_mode='HTML')


# Функция, которая присылает реальному игроку пульт для указания цели атаки одновременно с битвой или раньше по запросу
def target_set(bot, update):
    if isinstance(update, int):
        user_id = update
    else:
        user_id = update.message.from_user.id
    twink = twinks.get(user_id)
    if twink is None:
        bot.send_message(chat_id=user_id, text="Ошибка. Вы зарегистрированы?")
        return
    pult = Pult(update.message.chat_id, update.message.message_id, real_account=True)
    bot.send_message(chat_id=user_id, text=get_pult_text(user_id=user_id),
                     reply_markup=rebuild_pult("default", None, pult), parse_mode='HTML')


def pult_twink_callback(bot, update):
    mes = update.callback_query.message
    id = int(update.callback_query.data.split()[1])
    pult = Pult.get_pult(mes.chat_id)
    new_markup = rebuild_pult("change_twink", id, pult)
    pult.status.update({"twink": id})
    edit_pult(bot=bot, chat_id=mes.chat_id, message_id=mes.message_id, reply_markup=new_markup,
              callback_query_id=update.callback_query.id)


def pult_castles_callback(bot, update):
    mes = update.callback_query.message
    new_target = int(update.callback_query.data[2:])
    pult = Pult.get_pult(mes.chat_id)
    new_markup = rebuild_pult("change_target", new_target, pult)
    pult.status.update({ "target" : new_target })
    edit_pult(bot=bot, chat_id=mes.chat_id, message_id=mes.message_id, reply_markup=new_markup, callback_query_id=update.callback_query.id)


def pult_ok_callback(bot, update):
    mes = update.callback_query.message
    pult = Pult.get_pult(mes.chat_id)
    twink_id = pult.status.get("twink")
    twink_target = pult.status.get("target")
    real_account = pult.real_account
    if twink_id == -1 and not real_account:
        bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text="Необходимо выбрать аккаунт!")
        return
    if twink_target == -1:
        bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text="Необходимо выбрать замок!")
        return
    if real_account:
        twink = twinks.get(pult.chat_id)
    else:
        try:
            twink = twinks.get(twink_id)
        except IndexError:
            bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text="Ошибка при выборе аккаунта")
            return
    request = "select current_castle from twinks where telegram_id = %s"
    cursor.execute(request, (twink.telegram_id,))
    row = cursor.fetchone()
    if row is None:
        bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text="Ошибка при поиске аккаунта")
        return
    if row[0] == castles[twink_target]:
        new_target = "defense"
    else:
        new_target = "attack"
    new_castle_target = castles[twink_target]
    request = "update twinks set target = %s, castle_target = %s where telegram_id = %s"
    cursor.execute(request, (new_target, new_castle_target, twink.telegram_id))
    twink.target = new_target
    twink.castle = new_castle_target
    response = get_pult_text(user_id=pult.chat_id if pult.real_account else None)
    reply_markup = rebuild_pult("current", None, pult)
    bot.editMessageText(chat_id=mes.chat_id, message_id=mes.message_id,
                        text=response, parse_mode='HTML', reply_markup=reply_markup)
    bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text="Успешно выполнено")


def pult_callback(bot, update):
    data = update.callback_query.data
    if data.find("pt") == 0:
        pult_twink_callback(bot, update)
        return
    if data.find("pc") == 0:
        pult_castles_callback(bot, update)
        return
    if data.find("pok") == 0:
        pult_ok_callback(bot, update)
        return


def edit_pult(bot, chat_id, message_id, reply_markup, callback_query_id):
    try:
        bot.editMessageReplyMarkup(chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)
    except BadRequest:
        pass
    except TelegramError:
        logging.error(traceback.format_exc)
    finally:
        bot.answerCallbackQuery(callback_query_id=callback_query_id)