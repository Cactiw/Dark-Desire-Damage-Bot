from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter

from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)

import logging

import work_materials.globals as globals

from work_materials.globals import *
from work_materials.filters.filters import *


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)



report_by_castles = {}



class Twink:

    def __init__(self, castle, target):
        self.castle = castle
        self.target = target


class Castle_report:

    def __init__(self, castle, status, damage):
        self.castle = castle
        self.status = status
        self.damage = damage

    def __eq__(self, other):
        return self.castle == other.castle

def reports_clear():
    global report_by_castles
    report_by_castles.clear()
    for castle in castles:
        current = Castle_report(castle, None, None)
        report_by_castles.update({"{0}".format(castle) : current})
    print(report_by_castles)

main_twink = Twink("🍆", "attack")
test_twink = Twink("🖤", "attack")

first_twink = Twink("🖤", "attack")
second_twink = Twink("☘", "attack")
third_twink = Twink("🐢", "attack")
forth_twink = Twink("🖤", "defense")

twinks = {534572692 : test_twink, 444404089:first_twink, 536014412:second_twink, 508872919:third_twink, 412039566:forth_twink, 231900398 : main_twink}#

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
    bot.send_message(chat_id=update.message.chat_id, text="Хорошо. Теперь пришли мне форвард из @CWDigest результатов той битвы, за которую необходимо посчитать урон")


def results(bot, update, user_data):
    user_data.update(status="results", results=update.message.text)
    bot.send_message(chat_id=update.message.chat_id, text="Хорошо. Теперь пришли мне форвард репорта <b> мастера(!) </b> c той битвы, за которую необходимо посчитать урон", parse_mode='HTML')


def report(bot, update, user_data):
    mes = update.message
    user_data.update(status="report", report=update.message.text)
    print("castle =", user_data.get("castle"))
    print(update.message.text)
    if update.message.text[0] == user_data.get("castle"):
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


def calculate_damage(bot, update, user_data):
    print("Started calculating damage")
    results = user_data.get("results")
    castle = user_data.get("castle")
    report = user_data.get("report")
    target = user_data.get("target")


    string = results.partition("{0}".format(castle))[2].partition("💰")[0]
    significant_advantage = 1 if "😎" in string else 0
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
    attack = int(report.partition("⚔")[2].partition(" ")[0].partition(":")[2].partition("(")[0])
    defense = int(report.partition("🛡")[2].partition(" ")[0].partition(":")[2].partition("(")[0])
    gold_earned = int(report.partition("💰")[2].partition(":")[2][1:].partition("\n")[0])
    print("report:", report)
    print("attack =", attack)
    print("defense =", defense)
    print("gold_earned =", gold_earned)
    print("target =", target)
    if target == "attack":
        if significant_advantage:
            gold_earned /= 0.7
        total_attack = attack/gold_earned * gold_castle
    else:
        total_attack = gold_castle / (gold_earned / defense)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Деф {0} подсчитан, ориентировочно\n🛡: <b>{1:.2f}.</b>\nПодсчитать заного: /start".format(
                             castle, total_attack), parse_mode='HTML')
        return

    bot.send_message(chat_id=update.message.chat_id, text = "Вошедший урон в {0} подсчитан, ориентировочно\n⚔: <b>{1:.2f}</b>\nПодсчитать заного: /start".format(castle, total_attack), parse_mode='HTML')

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
    while string.find(" ") != -1:
        string = string.partition(" ")[2]
        #print(string)

    significant_advantage = 1 if "😎" in string else 0

    gold_castle = int(string)
    if gold_castle < 0:
        gold_castle = - gold_castle
    print(gold_castle)
    print("attack =", report.partition("⚔")[2].partition(" ")[0][1:])
    print(report.partition("⚔️")[2], report.partition("⚔")[2].partition(" "), report.partition("⚔")[2].partition(" ")[0], report.partition("⚔️")[2].partition(" ")[0][1:])
    attack = int(report.partition("⚔")[2].partition(" ")[0].partition(":")[2].partition("(")[0])
    defense = int(report.partition("🛡")[2].partition(" ")[0].partition(":")[2].partition("(")[0])
    gold_earned = int(report.partition("💰")[2].partition(":")[2][1:].partition("\n")[0])
    print("report:", report)
    print("attack =", attack)
    print("defense =", defense)
    print("gold_earned =", gold_earned)
    print("target =", target)
    if target == "attack":
        if significant_advantage:
            gold_earned /= 0.7
        try:
            total_attack = attack/gold_earned * gold_castle
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
    if send_to_mid is None or send_to_mid.enabled is False:
        send_to_mid = job.run_once(send_mid_results, 30)

    #bot.send_message(chat_id=update.message.chat_id, text = "Вошедший урон в {0} подсчитан, ориентировочно\n⚔: <b>{1}</b>\nПодсчитать заного: /start".format(castle, total_attack), parse_mode='HTML')


def send_mid_results(bot, job):
    response = "Результаты за прошедшую битву:\n"
    for castle in castles:
        current = report_by_castles.get(castle)
        response += "{0} {1} ".format(current.castle, castle_status.get(current.status))
        if current.damage is None:
            response += "???\n"
        else:
            response += "⚔: <b>{0:.2f}</b>\n".format(current.damage) if current.status == "failed" else "🛡: <b>{0:.2f}</b>\n".format(current.damage)
    bot.send_message(chat_id=admin_user_id, text = response, parse_mode='HTML')
    #bot.send_message(chat_id=stats_send_id, text = response, parse_mode='HTML')


def skip(bot, update):
    logging.info("skipped message from user @{0}, user id = {1}".format(update.message.from_user.username, update.message.from_user.id))
    return 0

def unknown_text(bot, update, user_data):
    bot.send_message(chat_id=update.message.chat_id, text="Некорректный ввод. Результаты битвы должны быть форвардом из @CWDigest, репорт - форвардом из @ChatWarsBot, замок - строго, как задано на кнопке. При ошибке попробуйте начать сначала: /start")



dispatcher.add_handler(MessageHandler(filter_is_not_allowed, skip))
dispatcher.add_handler(MessageHandler(Filters.text & filter_set_results, set_results, pass_user_data=True))
dispatcher.add_handler(MessageHandler(Filters.text & filter_instant_report, instant_report, pass_user_data=True))



dispatcher.add_handler(CommandHandler('start', start, pass_user_data=True))
dispatcher.add_handler(MessageHandler(Filters.text & filter_castle, castle, pass_user_data=True))
dispatcher.add_handler(MessageHandler(Filters.text & filter_results, results, pass_user_data=True))
dispatcher.add_handler(MessageHandler(Filters.text & filter_report, report, pass_user_data=True))

dispatcher.add_handler(CommandHandler('set_stats', enable_stats_flag, pass_user_data=True, filters=Filters.user(user_id=admin_user_id)))


# ------------------------------------------------------------------------------------------------------------------
dispatcher.add_handler(MessageHandler(Filters.text, unknown_text, pass_user_data=True))



reports_clear()
updater.start_polling(clean=False)
job = updater.job_queue

send_to_mid = None

updater.idle()