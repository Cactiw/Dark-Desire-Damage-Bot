from telegram.ext import Updater
from config import ProductionToken, request_kwargs, psql_creditals
import pytz, tzlocal, psycopg2


updater = Updater(token=ProductionToken, request_kwargs=request_kwargs)
dispatcher = updater.dispatcher

castles = ['🍁', '☘', '🖤', '🐢', '🦇', '🌹', '🍆']
castles_unicode = {'🍁' : '\uD83C\uDF41', '☘' : '\u2618', '🖤' : '\uD83D\uDDA4', '🐢' : '\uD83D\uDC22',
                   '🦇' : '\uD83E\uDD87', '🌹' : '\uD83C\uDF39', '🍆' : '\uD83C\uDF46'}

status_default = {}
castle_status = { "failed" : '⚔', "defended" : '🛡'}

conn = psycopg2.connect("dbname={0} user={1} password={2}".format(psql_creditals['dbname'], psql_creditals['user'], psql_creditals['pass']))
conn.set_session(autocommit = True)
cursor = conn.cursor()

admin_user_id = 231900398
stats_send_id = 105907720

twinks = {}

instant_report_list = [534572692, 444404089, 536014412, 508872919, 412039566, 546634100]#, 231900398]#

admin_ids = [231900398, 105907720]

set_stats_flag = 0

moscow_tz = pytz.timezone('Europe/Moscow')
try:
    local_tz = tzlocal.get_localzone()
except pytz.UnknownTimeZoneError:
    local_tz = pytz.timezone('Europe/Andorra')

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
