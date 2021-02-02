import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
lib_path = dir_path + '/../libs'
sys.path.append(lib_path)
sys.path.append(dir_path)
from bot_father import BotFather
from bot_constant import *
from exchange_lib import *

class SidewinderBot(BotFather):
    BUY_PROFILE = 'buy'
    SELL_PROFILE = 'sell'
    PROFILE = {
        BUY_PROFILE: {
            'side': 'buy',
            'profit_side': 'sell',
            'step_wise': 1
        },
        SELL_PROFILE: {
            'side': 'sell',
            'profit_side': 'buy',
            'step_wise': -1
        }
    }

    def __init__(self):
        super().__init__('SidewinerBot')
        self.__min_amount = 0.002
        self.profit = 0
        self.step_stop_loss = 0
        self.stop_loss_type = None
        self._pair = None

    def bot_entry(self, web_input):
        if not web_input:
            print('No INPUT, RETURN FALSE')
            return False
        super().bot_entry(web_input)
        # params for bot
        self.profit = float(web_input['profit'])
        self.step_stop_loss = float(web_input['step_stop_loss'])
        self.stop_loss_type = web_input['stop_loss_type']

    def start_trade_trigger(self, profile, amount, this_type, price, profit=None, step_stop_loss=None, using_stop_loss=True):
        trade_thread = Thread(target=self.start_trade, args=(profile, amount, this_type, price, profit, step_stop_loss, using_stop_loss))
        self._log('side_winder_botmom---48Start trade: {} {}  {} {}'.format(profile, amount, profit, step_stop_loss))
        trade_thread.start()

    def start_trade(self, profile, amount, this_type, price, profit=None, step_stop_loss=None, using_stop_loss=True):
        side = self.PROFILE[profile]['side']
        profit = self.profit if not profit else profit
        profit_side = self.PROFILE[profile]['profit_side']
        step_wise = self.PROFILE[profile]['step_wise']
        stop_loss_type = 'market' if 'market' == self.stop_loss_type else 'limit'
        # fetch price
        if 'limit' == this_type and not price:
            price = self._fetch_best_price(profile)
        # place order
        meta_data = {'type': 'init_order',
                     'profit': profit,
                     'stop_loss_type': stop_loss_type,
                     'profit_side': profit_side,
                     'profit_type': 'limit',
                     'step_wise': step_wise}
        data = self.place_order(price, amount, side, self._pair, type=this_type, meta_data=meta_data,
                                callback=self.callback_order_status_change)
        if not data:
            self._log('side_winder_botmom---70Place order is error, please report when check balance')

    def callback_order_status_change(self, data):
        meta_data = data['meta_data']
        if not meta_data:
            self._log('side_winder_botmom---75 Oder {} return not have meta_data'.format(data['order_id']))
            return True
        if ORDER_PROFILE['status']['closed'] == data['status']:
            self._log('side_winder_botmom---78Order {} is close'.format(data['order_id']))
            if 'init_order' == meta_data['type']:
                # place profit order and stop loss order
                price = float(data['average']) + meta_data['step_wise'] * meta_data['profit']
                cb_data = {
                    'type': 'profit_order',

                }
                self.place_order(price, float(data['filled']), meta_data['profit_side'], self._pair,
                                 type=meta_data['profit_type'], behavior_order_stop_loss='stop_loss',
                                 params={})
