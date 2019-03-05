from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter, CallbackQueryHandler

from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)

import logging, datetime, traceback

import work_materials.globals as globals

from work_materials.globals import *
from work_materials.filters.filters import *

from libs.pult import rebuild_pult
from libs.twink import Twink
from libs.report import Castle_report

from bin.pult_callback import pult, pult_callback

#   Выставляем логгироввание
console = logging.StreamHandler()
console.setLevel(logging.INFO)

log_file = logging.FileHandler(filename='error.log', mode='a')
log_file.setLevel(logging.ERROR)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO, handlers=[log_file, console])



report_by_castles = {}



def reports_clear():
    global report_by_castles
    report_by_castles.clear()
    for castle in castles:
        current = Castle_report(castle, None, None, "")
        report_by_castles.update({"{0}".format(castle) : current})
    print(report_by_castles)

"""main_twink = Twink("🦇", "attack")
test_twink = Twink("🖤", "attack")

first_twink = Twink("🖤", "attack")
second_twink = Twink("☘", "attack")
third_twink = Twink("🐢", "attack")
forth_twink = Twink("🖤", "defense")

twinks = {534572692 : test_twink, 444404089:first_twink, 536014412:second_twink, 508872919:third_twink, 412039566:forth_twink}#, 231900398 : main_twink}#"""

current_battle_stats = None



def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu




def start(bot, update, user_data):
    user_data.update(status = "start")
    button_list = [
        KeyboardButton("🍁"),
        KeyboardButton("☘"),
        KeyboardButton("🖤"),
        KeyboardButton("🐢"),
        KeyboardButton("🦇"),
        KeyboardButton("🌹"),
        KeyboardButton("🍆"),
    ]
    reply_markup = ReplyKeyboardMarkup(build_menu(button_list, n_cols=3), resize_keyboard=True, one_time_keyboard=True)
    bot.send_message(chat_id=update.message.chat_id, text="Привет! Выбери замок, которому необходимо посчитать входящий урон", reply_markup=reply_markup)


def castle(bot, update, user_data):
    user_data.update(status = "selected_castle", castle = update.message.text)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Хорошо. Теперь пришли мне форвард из @CWDigest результатов той битвы, "
                          "за которую необходимо посчитать урон, или репорт, "
                          "если необходимо посчитать урон за последнюю битву.")


def results(bot, update, user_data):
    user_data.update(status="results", results=update.message.text)
    bot.send_message(chat_id=update.message.chat_id, text="Хорошо. Теперь пришли мне форвард репорта <b> мастера(!) </b> c той битвы, за которую необходимо посчитать урон", parse_mode='HTML')


def report(bot, update, user_data):
    mes = update.message
    if mes.text.find("Твои результаты в бою:") != -1:
        report_type = 'CW3'
        user_data.update({"report_type": report_type})
    elif mes.text.find("DDG:") == 0:
        report_type = 'DDG'
        user_data.update({"report_type": report_type})
    else:
        bot.send_message(chat_id=mes.chat_id, text="Произошла ошибка, невозможно определить источник репорта (DDG / CW3 ?)")
        return
    user_data.update(status="report", report=update.message.text)
    print("castle =", user_data.get("castle"))
    print(update.message.text)
    if report_type == 'CW3':
        if update.message.text[0] == user_data.get("castle"):
            target = "defense"
        else:
            target = "attack"
    else:
        if user_data.get("castle") == '🖤':
            target = "defense"
        else:
            target = "attack"
    user_data.update(target = target)
    if target == "defense":
        if mes.text.find("🏅") != -1 or mes.text.find("🔱") != -1:
            bot.send_message(chat_id=update.message.chat_id, text="Репорт с дефа не должен содержать медальку, или GA")
            return


    bot.send_message(chat_id=update.message.chat_id, text="Хорошо. Подразумевается, что при совпадении замка с репорта и указанного ранее, то это репорт с дефа, иначе - с атаки.", parse_mode='HTML')
    calculate_damage(bot, update, user_data)

def parse_cw3_report(report):
    attack = int(report.partition("⚔")[2].partition(" ")[0].partition(":")[2].partition("(")[0])
    defense = int(report.partition("🛡")[2].partition(" ")[0].partition(":")[2].partition("(")[0])
    gold_earned = int(report.partition("💰")[2].partition(":")[2][1:].partition("\n")[0])
    return_value = [attack, defense, gold_earned]
    return return_value

def parse_ddg_results(report):
    attack = int(report.partition("⚔")[2][1:].split()[0])
    defense = int(report.partition("🛡")[2].split()[0][:-1])  # Потому что там стоит ****** двоеточие без пробела
    gold_earned = int(report.partition("💰")[2].split()[0])
    return_value = [attack, defense, gold_earned]
    return return_value


def calculate_damage(bot, update, user_data):
    mes = update.message
    print("Started calculating damage")
    results = user_data.get("results")
    if results is None:
        results = current_battle_stats
    castle = user_data.get("castle")
    report = user_data.get("report")
    target = user_data.get("target")
    report_type = user_data.get("report_type")


    string = results.partition("{0}".format(castle))[2].partition("💰")[0]
    #significant_advantage = 1 if "😎" in string else 0          #   Временно отключено
    significant_advantage = 0
    string = string.split(" ")
    string = string[len(string) - 1]
    print(string)
    print("significant_advantage =", significant_advantage)

    gold_castle = int(string)
    if gold_castle < 0:
        gold_castle = - gold_castle
    print(gold_castle)
    print("attack =", report.partition("⚔")[2].partition(" ")[0][1:])
    #print(report.partition("⚔")[2], report.partition("⚔️")[2].partition(" "), report.partition("⚔️")[2].partition(" ")[0], report.partition("⚔")[2].partition(" ")[0][1:])
    if report_type == 'CW3':
        parsed = parse_cw3_report(report)
    elif report_type == 'DDG':
        parsed = parse_ddg_results(report)
    else:
        dispatcher.bot.send_message(chat_id=mes.chat_id, text="Произошла ошибка, попробуйте нажать /start")
        return
    attack = parsed[0]
    defense = parsed[1]
    gold_earned = parsed[2]
    print("report:", report)
    print("attack =", attack)
    print("defense =", defense)
    print("gold_earned =", gold_earned)
    print("target =", target)
    if target == "attack":
        total_attack = attack/gold_earned * gold_castle * (0.95 if significant_advantage else 1)
    else:
        total_attack = gold_castle / (gold_earned / defense)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Деф {0} подсчитан, ориентировочно\n🛡: <b>{1:.2f}</b> k.\nПодсчитать заного: /start".format(
                             castle, total_attack/1000), parse_mode='HTML')
        return

    bot.send_message(chat_id=update.message.chat_id, text = "Вошедший урон в {0} подсчитан, ориентировочно\n⚔: <b>{1:.2f}</b> k.\nПодсчитать заного: /start".format(castle, total_attack/1000), parse_mode='HTML')
    pop_list = ["results", "castle", "report", "target", "report_type"]
    for item in pop_list:
        if item in user_data:
            user_data.pop(item)

def disable_stats_flag(bot, job):
    globals.set_stats_flag = 0
    print("flag =", globals.set_stats_flag)


def enable_stats_flag(bot, update, user_data):
    globals.set_stats_flag = 1
    print("flag =", globals.set_stats_flag)
    job.run_once(disable_stats_flag, 30)


def set_results(bot, update, user_data):
    mes = update.message
    global current_battle_stats
    current_battle_stats = mes.text
    for castle in castles:
        current = report_by_castles.get(castle)
        current.status = "failed" if "⚔" in mes.text.partition(castle)[2].partition("💰")[0] else "defended"
        report_by_castles.update({"{0}".format(castle): current})

    print("stats updated")
    bot.send_message(chat_id=admin_user_id, text = "Статистика по битве обновлена. Хорошего дня!")


def instant_report(bot, update, user_data):
    global send_to_mid

    results = current_battle_stats
    castle = twinks.get(update.message.from_user.id).castle
    report = update.message.text
    target = twinks.get(update.message.from_user.id).target

    current_castle = report_by_castles.get(castle)
    if (current_castle.status == "failed" and target == "defense") or (current_castle.status == "defended" and target == "attack"):
        print("report ignored")
        return

    string = results.partition("{0}".format(castle))[2].partition("💰")[0]
    #significant_advantage = 1 if "😎" in string else 0          #   Временно отключено
    significant_advantage = 0
    string = string.split(" ")
    string = string[len(string) - 1]


    gold_castle = int(string)
    if gold_castle < 0:
        gold_castle = - gold_castle
    print(gold_castle)
    print("attack =", report.partition("⚔")[2].partition(" ")[0][1:])
    print(report.partition("⚔️")[2], report.partition("⚔")[2].partition(" "), report.partition("⚔")[2].partition(" ")[0], report.partition("⚔️")[2].partition(" ")[0][1:])
    parsed = parse_cw3_report(report)
    attack = parsed[0]
    defense = parsed[1]
    gold_earned = parsed[2]
    print("report:", report)
    print("attack =", attack)
    print("defense =", defense)
    print("gold_earned =", gold_earned)
    print("target =", target)
    if target == "attack":
        try:
            total_attack = attack/gold_earned * gold_castle * (0.95 if significant_advantage else 1)
        except ZeroDivisionError:
            total_attack = 0
    else:
        try:
            total_attack = gold_castle / (gold_earned / defense)
        except ZeroDivisionError:
            total_attack = 0
        """bot.send_message(chat_id=update.message.chat_id,
                         text="Деф {0} подсчитан, ориентировочно\n🛡: <b>{1}</b>\nПодсчитать заного: /start".format(
                             castle, total_attack), parse_mode='HTML')"""

    current_castle.damage = total_attack
    if "Enraged" in report:
        current_castle.warning += "🏅"
    if "You were outplayed" in report:
        current_castle.warning += "🔽"
    if "You were poisoned" in report:
        current_castle.warning += "💉"
    if gold_earned < 10:
        current_castle.warning += "⚠️"

    if send_to_mid is None or send_to_mid.enabled is False:
        send_to_mid = job.run_once(send_mid_results, 30)

    #bot.send_message(chat_id=update.message.chat_id, text = "Вошедший урон в {0} подсчитан, ориентировочно\n⚔: <b>{1}</b>\nПодсчитать заного: /start".format(castle, total_attack), parse_mode='HTML')


def send_mid_results(bot, job):
    global send_to_mid
    message_datetime = datetime.datetime.now(tz=moscow_tz).replace(tzinfo=None)
    time = message_datetime - message_datetime.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
    if time < datetime.timedelta(hours=1):  #   Дневная битва прошлого дня
        message_datetime -= datetime.timedelta(days=1)
        battle_time = message_datetime.replace(hour = 17, minute = 0, second = 0, microsecond = 0)
    else:
        battle_time = datetime.datetime.combine(message_datetime.date(), datetime.time(hour=1))
        while message_datetime - battle_time >= datetime.timedelta(hours=8):
            battle_time += datetime.timedelta(hours = 8)
    response = "Результаты битвы {0}:\n".format(battle_time.strftime("%D %H:%M"))
    castles.sort(key = lambda curr:report_by_castles.get(curr).damage if report_by_castles.get(curr).damage is not None else 0, reverse=True)
    for castle in castles:
        current = report_by_castles.get(castle)
        response += "{0} {1} ".format(current.castle, castle_status.get(current.status))
        if current.damage is None:
            response += "???\n"
        else:
            response += "{0}: <b>{1:.2f}</b> k  {2}\n".format("⚔" if current.status == "failed" else "🛡", current.damage/1000, current.warning)
    bot.send_message(chat_id=admin_user_id, text = response, parse_mode='HTML')
    bot.send_message(chat_id=stats_send_id, text = response, parse_mode='HTML')
    reports_clear()
    send_to_mid = None


def lilpin(bot, update):
    mes = update.message
    response = "Распределение целей:\n"
    castles_will_be_attacked = []
    for castle in castles:
        if castle in mes.text:
            castles_will_be_attacked.append(castle)
    twinks_list = list(twinks.values())
    for twink in twinks_list:
        if twink.target == "attack":
            for attack_castle in castles_will_be_attacked:
                if twink.current_castle != attack_castle:
                    new_castle_target = attack_castle
                    request = "update twinks set castle_target = %s where telegram_id = %s"
                    cursor.execute(request, (new_castle_target, twink.telegram_id))
                    twink.castle = attack_castle
                    response += "Цель <b>{}{}</b> изменена на {}\n".format(twink.current_castle, twink.username, attack_castle)
                    castles_will_be_attacked.remove(attack_castle)
                    break
    response += "\nПолные результаты смотри в /pult"
    bot.send_message(chat_id = mes.chat_id, text = response, parse_mode = 'HTML')


def inline_callback(bot, update):
    if update.callback_query.data.find("p") == 0:
        pult_callback(bot, update)
        return

def twinks_load():
    logging.info("Loading twinks...")
    request = "select telegram_id, username, target, castle_target, current_castle from twinks"
    cursor.execute(request)
    row = cursor.fetchone()
    while row:
        telegram_id = row[0]
        username = row[1]
        target = row[2]
        castle_target = row[3]
        current_castle = row[4]
        current = Twink(castle_target, target, username, telegram_id, current_castle)
        twinks.update({telegram_id : current})
        row = cursor.fetchone()
    logging.info("Complete")


def skip(bot, update):
    logging.info("skipped message from user @{0}, user id = {1}".format(update.message.from_user.username, update.message.from_user.id))
    bot.send_message(chat_id=admin_user_id, text = "skipped message from user @{0}, "
                                                   "user id = {1}".format(update.message.from_user.username,
                                                                          update.message.from_user.id))
    return 0

def unknown_text(bot, update, user_data):
    bot.send_message(chat_id=update.message.chat_id, text="Некорректный ввод. Результаты битвы должны быть форвардом из @CWDigest, репорт - форвардом из @ChatWarsBot, замок - строго, как задано на кнопке. При ошибке попробуйте начать сначала: /start")



dispatcher.add_handler(MessageHandler(filter_is_not_allowed, skip))
dispatcher.add_handler(MessageHandler(Filters.text & filter_set_results, set_results, pass_user_data=True))
dispatcher.add_handler(MessageHandler(Filters.text & filter_instant_report, instant_report, pass_user_data=True))



dispatcher.add_handler(CommandHandler('start', start, pass_user_data=True))
dispatcher.add_handler(CommandHandler('pult', pult, pass_user_data=False))
dispatcher.add_handler(MessageHandler(Filters.text & filter_lilpin, lilpin, pass_user_data=False))
dispatcher.add_handler(MessageHandler(Filters.text & filter_castle, castle, pass_user_data=True))
dispatcher.add_handler(MessageHandler(Filters.text & filter_results, results, pass_user_data=True))
dispatcher.add_handler(MessageHandler(Filters.text & (filter_report | filter_ddg_report), report, pass_user_data=True))


dispatcher.add_handler(CommandHandler('set_stats', enable_stats_flag, pass_user_data=True, filters=Filters.user(user_id=admin_user_id)))

dispatcher.add_handler(CallbackQueryHandler(inline_callback, pass_update_queue=False, pass_user_data=False))

# ------------------------------------------------------------------------------------------------------------------
dispatcher.add_handler(MessageHandler(Filters.text, unknown_text, pass_user_data=True))



reports_clear()
twinks_load()
updater.start_polling(clean=False)
job = updater.job_queue

send_to_mid = None

updater.idle()