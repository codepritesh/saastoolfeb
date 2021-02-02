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
from arb_2way_tool import *
from threading import Thread
import json

class Arb2WayConsumer(BaseConsumer):
    BOT_ALIAS = Arb2WayBot.bot_alias
    base_srv = BaseService()

    def receive(self, text_data):
        print('text data {}'.format(text_data))
        text_data_json = json.loads(text_data)
        web_input = text_data_json
        web_input.update({'framework': WEB_DJANGO})
        if 'action' == self.channel_mux:
            self._begin_trade(web_input)
            return

        if self.channel_mux != 'control':
            return
        signal = text_data_json.get('signal')

        if signal == 'start':
            try:
                return self.start_bot(web_input)
            except:
                tb = traceback.format_exc()
                print('ERROR: Arb2WayConsumer: {}'.format(tb))
                return False
        if signal == 'stop':
            try:
                return self.stop_bot(web_input)
            except:
                tb = traceback.format_exc()
                print('ERROR: Arb2WayConsumer: {}'.format(tb))
                return False

    def start_bot(self, web_input):
        data = web_input.copy()
        a_bot = Arb2WayBot()
        t = Thread(target=a_bot.bot_entry, args=(data, ))
        t.start()
        self.base_srv.add_bot_running(self.BOT_ALIAS, web_input['uuid'], a_bot, t, web_input, data)
        return True

    def stop_bot(self, web_input):
        try:
            self.base_srv.stop_bot(self.BOT_ALIAS, web_input)
        except:
            tb = traceback.format_exc()
            print("Arb2WayConsumer: ", tb)
        return True

    def _begin_trade(self, web_input):
        bot = self.base_srv.fetch_bot(bot_alias=self.BOT_ALIAS, uuid=web_input['uuid'])
        if bot:
            Thread(target=bot.begin_trading, args=(web_input, )).start()
            return True
        return False