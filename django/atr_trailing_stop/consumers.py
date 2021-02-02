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
from atr_trailing_stop_strategy_bot import *
from threading import Thread
import json

class AtrTrailingStopConsumer(BaseConsumer):
    BOT_ALIAS = AtrTrailingStopBot.bot_alias
    base_srv = BaseService()

    def receive(self, text_data):
        print('text data {}'.format(text_data))
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
                print('ERROR: AtrTrailingStopConsumer: {}'.format(tb))
                return False
        if signal == 'stop':
            try:
                return self.stop_bot(web_input)
            except:
                tb = traceback.format_exc()
                print('ERROR: AtrTrailingStopConsumer: {}'.format(tb))
                return False

    def start_bot(self, web_input):
        data = web_input.copy()
        a_bot = AtrTrailingStopBot()
        t = Thread(target=a_bot.bot_entry, args=(data, ))
        t.start()
        self.base_srv.add_bot_running(self.BOT_ALIAS, web_input['uuid'], a_bot, t, web_input, data)
        return True

    def stop_bot(self, web_input):
        try:
            self.base_srv.stop_bot(self.BOT_ALIAS, web_input)
        except:
            tb = traceback.format_exc()
            print("AtrTrailingStopConsumer: ", tb)
        return True
