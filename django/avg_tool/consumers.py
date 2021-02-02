import os, sys
import json
from threading import Thread
import traceback
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
from exception_decor import exception_logging
from consumer import BaseConsumer
from base_service import BaseService
from clear_order_bot import *


class AvgToolConsumer(BaseConsumer):
    BOT_ALIAS = ClearOrderBot.alias
    base_srv = BaseService()

    def receive(self, text_data):
        if self.channel_mux != 'control':
            return

        text_data_json = json.loads(text_data)
        web_input = text_data_json
        web_input.update({'framework': WEB_DJANGO})
        signal = text_data_json.get('signal')
        try:
            if signal == 'start':
                return self.start_bot(web_input)
            if signal == 'stop':
                return self.stop_bot(web_input)
            if signal == 'clear':
                return self.invoke_clear_order(web_input)
            if signal == 'cancel':
                return self.invoke_cancel_order(web_input)
            if signal == 'average':
                return self.invoke_average_order(web_input)
        except:
            tb = traceback.format_exc()
            print('ERROR: DenverConsumer: {}'.format(tb))
            return False

    def start_bot(self, web_input):
        data = web_input.copy()
        a_bot = ClearOrderBot()
        t = Thread(target=a_bot.bot_entry, args=(data, ))
        t.start()
        self.base_srv.add_bot_running(self.BOT_ALIAS, web_input['uuid'], a_bot, t, web_input, data)
        return True

    def stop_bot(self, web_input):
        try:
            self.base_srv.stop_bot(self.BOT_ALIAS, web_input)
        except:
            tb = traceback.format_exc()
            print("DenverService: ", tb)
        return True

    """
    Clear order
    """
    @exception_logging
    def invoke_clear_order(self, web_input):
        bot = self.base_srv.fetch_bot(bot_alias=self.BOT_ALIAS, uuid=web_input['uuid'])
        if bot:
            bot.clear_order(web_input)
            return True
        return False

    """
    Cancel Order
    """
    @exception_logging
    def invoke_cancel_order(self, web_input):
        bot = self.base_srv.fetch_bot(bot_alias=self.BOT_ALIAS, uuid=web_input['uuid'])
        if bot:
            bot.cancel_order(web_input)
            return True
        return False

    """
    Cancel Order
    """
    @exception_logging
    def invoke_average_order(self, web_input):
        bot = self.base_srv.fetch_bot(bot_alias=self.BOT_ALIAS, uuid=web_input['uuid'])
        if bot:
            bot.avg_order(web_input)
            return True
        return False
