import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
lib_path = dir_path + '/../libs'
bot_path = dir_path + '/../bots'
sys.path.append(lib_path)
sys.path.append(bot_path)
sys.path.append(dir_path)
from support_order_follow_market import SupportOrderFollowMarket
from support_order_stop_loss import SupportOrderStopLoss
from bot_constant import *

class ExampleUseActionLib(SupportOrderFollowMarket, SupportOrderStopLoss):

    def __init__(self):
        print('ExampleUseActionLib init')

    def bot_entry(self, web_input):
        super(SupportOrderFollowMarket, self).bot_entry(web_input)

    def begin_trading(self, web_input):
        self._log(f'example_use_action_libmom---23 Begin trading with data {web_input}')
        side = web_input['side']
        amount = float(web_input['amount'])
        price = float(web_input['price'])
        meta_data = {
            'info': 'Kaka'
        }
        # place order follow market and invoke callback
        self.msf_place_order_follow_market_helper(self._pair, side, amount, price, self._callback_of_open_order,  meta_data=meta_data)

    def _callback_of_open_order(self, data):
        if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
            self.print_metheod_stoploss(data)
            self._log(f'example_use_action_libmom---36 Open order is filled: {data}')
        if ORDER_OPEN == data[KEY_GET_ORDER_STATUS]:
            self.print_metheod_stoploss(data)
            self._log(f'example_use_action_libmom---39 Open order cancelled, {data}')
