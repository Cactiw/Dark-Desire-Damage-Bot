from telegram.ext import BaseFilter
from work_materials.globals import *

import work_materials.globals as globals

LILPIN_ID = -1001293422180

class FilterIsNotAllowed(BaseFilter):
    def filter(self, message):
        return not(message.from_user.id in admin_ids or message.from_user.id in instant_report_list)

class Filter_Set_Results(BaseFilter):
    def filter(self, message):
        if message.text:
            if message.forward_from_chat is not None:
                print(globals.set_stats_flag)
                return message.forward_from_chat.id == -1001391784649 and globals.set_stats_flag and message.from_user.id == admin_user_id
            return 0


class Filter_Instant_Report(BaseFilter):
    def filter(self, message):
        if message.text:
            if message.forward_from is not None:
                return "Твои результаты в бою:" in message.text and message.from_user.id in instant_report_list
            return 0


class Filter_Instant_Real_Report(BaseFilter):
    def filter(self, message):
        if message.text:
            if message.forward_from is not None:
                return "Твои результаты в бою:" in message.text and message.from_user.id in list(twinks)
            return 0


class Filter_Castle(BaseFilter):
    def filter(self, message):
        if message.text:
            user_data = dispatcher.user_data.get(message.from_user.id)
            return message.text in castles and user_data  # and user_data.get("status") == "start"


class Filter_Results(BaseFilter):
    def filter(self, message):
        if message.text:
            if message.forward_from_chat is not None:
                print(message.forward_from)
                user_data = dispatcher.user_data.get(message.from_user.id)
                return message.forward_from_chat.id == -1001391784649 and user_data and user_data.get("status") == "selected_castle"
            return 0


class Filter_Report(BaseFilter):
    def filter(self, message):
        if message.text:
            user_data = dispatcher.user_data.get(message.from_user.id)
            if user_data is None:
                dispatcher.bot.send_message(chat_id=message.from_user.id, text="Произошла ошибка, попробуйте нажать /start")
                return False
            return user_data.get("status") in ["results", "selected_castle"] and "Твои результаты в бою:" in message.text


class FilterDDGReport(BaseFilter):
    def filter(self, message):
        if message.text:
            user_data = dispatcher.user_data.get(message.from_user.id)
            if user_data is None:
                print("User_data is None, id =", message.from_user.id)
                print(message.text)
                dispatcher.bot.send_message(chat_id=message.from_user.id, text="Произошла ошибка, попробуйте нажать /start")
                return False
            return user_data.get("status") == "results" and message.text.find("DDG:") == 0


class FilterLilpin(BaseFilter):
    def filter(self, message):
        if message.text:
            return message.forward_from_chat and message.forward_from_chat.id == LILPIN_ID

filter_lilpin = FilterLilpin()



filter_is_not_allowed = FilterIsNotAllowed()

filter_castle = Filter_Castle()
filter_results = Filter_Results()
filter_report = Filter_Report()
filter_ddg_report = FilterDDGReport()

filter_set_results = Filter_Set_Results()
filter_instant_report = Filter_Instant_Report()
filter_instant_real_report = Filter_Instant_Real_Report()
