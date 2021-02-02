import os, sys
cur_path = os.path.dirname(os.path.realpath(__file__))
root_app_path = cur_path + '/../d_trading_bots/'
bot_path = cur_path + '/../../bots/'
lib_path = cur_path + '/../../libs/'
sys.path.append(cur_path + '/../services/')
sys.path.append(cur_path)
sys.path.append(lib_path)
sys.path.append(bot_path)
sys.path.append(root_app_path)
from common import WEB_DJANGO
from consumer import BaseConsumer
from base_service import BaseService
import requests
import traceback
from support_big_amount_strategy_bot import *
from threading import Thread
import json

class SupportBigAmountConsumer(BaseConsumer):
    BOT_ALIAS = SupportBigAmountBot.bot_alias
    base_srv = BaseService()

    def receive(self, text_data):
        print('support_big_amount--consumersmom---25text data {}'.format(text_data))
        if self.channel_mux != 'control':
            return
        text_data_json = json.loads(text_data)
        web_input = text_data_json
        web_input.update({'framework': WEB_DJANGO})
        signal = text_data_json.get('signal')

        if signal == 'start':
            try:
                return self.start_bot(web_input)
            except:
                tb = traceback.format_exc()
                print('support_big_amount--consumersmom---38ERROR: SupportBigAmountConsumer: {}'.format(tb))
                return False
        if signal == 'stop':
            try:
                return self.stop_bot(web_input)
            except:
                tb = traceback.format_exc()
                print('support_big_amount--consumersmom---45ERROR: SupportBigAmountConsumer: {}'.format(tb))
                return False
        elif 'buy_trigger' == signal or 'sell_trigger' == signal:
            self.invoke_place_order(web_input)

    def start_bot(self, web_input):
        data = web_input.copy()
        a_bot = SupportBigAmountBot()
        t = Thread(target=a_bot.bot_entry, args=(data, ))
        t.start()
        self.base_srv.add_bot_running(self.BOT_ALIAS, web_input['uuid'], a_bot, t, web_input, data)
        return True

    def stop_bot(self, web_input):
        try:
            self.base_srv.stop_bot(self.BOT_ALIAS, web_input)
        except:
            tb = traceback.format_exc()
            print("support_big_amount--consumersmom---63SupportBigAmountConsumer: ", tb)
        return True

    def invoke_place_order(self, web_input):
        bot = self.base_srv.fetch_bot(bot_alias=self.BOT_ALIAS, uuid=web_input['uuid'])
        if bot:
            Thread(target=bot.begin_trading, args=(web_input, )).start()
            return True
        return False
