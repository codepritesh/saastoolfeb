import os
import sys
from decimal import Decimal

cur_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(cur_path + '/../libs')
sys.path.append(cur_path + '/../repositories')
from bot_father import BotFather
from bot_constant import *


class EthBtcSupportBot(BotFather):

    def __init__(self):
        super().__init__('EthBtcSupportBot')
        self._profit = Decimal('0.0')
        self._trade_count = 0

    def bot_entry(self, web_input):
        super().bot_entry(web_input)
        # get params
        self._profit = Decimal(web_input['profit'])

    def begin_trade(self, web_input):
        trade_id = self._trade_count
        # buy or sell
        side = web_input['side']
        profit = web_input['profit']
        amount = web_input['amount']
        self._log('eth_btc_support_botmom---30begin trade .. side {}'.format(side))
        # market order and callback place profit order
        meta_data = {
            'trade_id': trade_id,
            'side': side,
            'amount': amount,
            'profit': profit
        }
        self.place_order(None, amount, side, self._pair, type=MARKET,
                         meta_data=meta_data, callback=self._callback_order_status)

    def _callback_order_status(self, data):
        if not data:
            self._log('eth_btc_support_bot---43Data is None, return False')
            return False
        # order close
        if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
            # place profit order, return True
            self._log('eth_btc_support_botmom---48Create profit order with previous data {}'.format(data))
            meta_data = data[KEY_GET_ORDER_META_DATA]
            profit = meta_data['profit']
            side = BUY if data[KEY_GET_ORDER_SIDE] == SELL else SELL
            price_profit = float(Decimal(data[KEY_GET_ORDER_AVERAGE_PRICE]) \
                                 - Decimal(str(STEP_WISE[side])) * Decimal(profit))
            self.place_order(price_profit, data[KEY_GET_ORDER_AMOUNT], side, self._pair, type=LIMIT,
                             callback=self.__callback_order_profit)
        elif ORDER_CANCELED == data[KEY_GET_ORDER_STATUS]:
            self._log('eth_btc_support_botmom---57Something wired, Order cancled')

    def __callback_order_profit(self, data):
        if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
            self._log("eth_btc_support_botmom---61 Order profit callback {}".format(data))