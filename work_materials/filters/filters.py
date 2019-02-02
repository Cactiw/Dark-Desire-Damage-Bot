from telegram.ext import BaseFilter
from work_materials.globals import *

import work_materials.globals as globals

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
                return message.text.find("Твои результаты в бою:") != -1 and message.from_user.id in instant_report_list
            return 0




class Filter_Castle(BaseFilter):
    def filter(self, message):
        if message.text:
            return message.text in castles and dispatcher.user_data.get(message.from_user.id).get("status") == "start"

class Filter_Results(BaseFilter):
    def filter(self, message):
        if message.text:
            if message.forward_from_chat is not None:
                print(message.forward_from)
                return message.forward_from_chat.id == -1001391784649 and dispatcher.user_data.get(message.from_user.id).get("status") == "selected_castle"
            return 0

class Filter_Report(BaseFilter):
    def filter(self, message):
        if message.text:
            if dispatcher.user_data.get(message.from_user.id) is None:
                print("User_data is None, id =", message.from_user.id)
                print(message.text)
                dispatcher.bot.send_message(chat_id=message.from_user.id, text="Произошла ошибка, попробуйте нажать /start")
            return dispatcher.user_data.get(message.from_user.id).get("status") == "results" and message.text.find("Твои результаты в бою:") != -1

class FilterDDGReport(BaseFilter):
    def filter(self, message):
        if message.text:
            if dispatcher.user_data.get(message.from_user.id) is None:
                print("User_data is None, id =", message.from_user.id)
                print(message.text)
                dispatcher.bot.send_message(chat_id=message.from_user.id, text="Произошла ошибка, попробуйте нажать /start")
            return dispatcher.user_data.get(message.from_user.id).get("status") == "results" and message.text.find("DDG:") == 0




filter_is_not_allowed = FilterIsNotAllowed()

filter_castle = Filter_Castle()
filter_results = Filter_Results()
filter_report = Filter_Report()
filter_ddg_report = FilterDDGReport()

filter_set_results = Filter_Set_Results()
filter_instant_report = Filter_Instant_Report()