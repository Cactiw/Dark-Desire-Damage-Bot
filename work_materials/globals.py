from telegram.ext import Updater
from config import ProductionToken, request_kwargs


updater = Updater(token=ProductionToken, request_kwargs=request_kwargs)
dispatcher = updater.dispatcher

castles = ['🍁', '☘', '🖤', '🐢', '🦇', '🌹', '🍆']
castle_status = { "failed" : '⚔', "defended" : '🛡'}


admin_user_id = 231900398
stats_send_id = 105907720

instant_report_list = [534572692, 444404089, 536014412, 508872919, 412039566, 231900398]#

admin_ids = [231900398, 105907720]

set_stats_flag = 0
