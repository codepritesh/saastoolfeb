import os
import sys
from decimal import Decimal

cur_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(cur_path + '/../libs')
sys.path.append(cur_path + '/../repositories')
from bot_father import BotFather
from bot_constant import *
import traceback


class SupportBot(BotFather):

    def __init__(self):
        super().__init__('EthBtcSupportBot')
        self.best_price_only = False
        self._trade_count = 0

    def bot_entry(self, web_input):
        super().bot_entry(web_input)
        # get params

    def begin_trade(self, web_input):
        trade_id = self._trade_count
        # buy or sell
        side = web_input['side']
        # profit = web_input['profit']
        amount = web_input['amount']
        type = web_input['type_order']
        # boolean place order profit, stop loss
        # is_take_stop_loss = web_input['take_stop_loss']
        is_take_profit = web_input['take_profit']
        is_take_price_manual = web_input['take_price_manual']
        self._log('support_botmom---35begin trade .. side {}'.format(side))
        # market order and callback place profit order
        meta_data = {
            'trade_id': trade_id,
            # 'side': side,
            # 'amount': amount,
            # 'profit': profit,
            # 'is_take_profit': is_take_profit,
            # 'is_take_stop_loss': is_take_stop_loss,
            'web_input': web_input
        }
        # get price
        if type == MARKET:
            self._process_place_order(is_take_profit, None, amount, side, type, meta_data)
            return True
        if is_take_price_manual:
            price = web_input['price']
        else:
            # fetch order book
            rank = int(web_input['rank'])
            type_price_order_book = web_input['type_price_order_book']
            if LIMIT == type_price_order_book:
                side_fetch_price_side = side
            else:
                # market
                side_fetch_price_side = BUY if side == SELL else SELL
            price = self._fetch_best_price(self._pair, side_fetch_price_side, index=rank)
        self._process_place_order(is_take_profit, price, amount, side, type, meta_data)
        return True

    def _process_place_order(self, is_take_profit, price, amount, side, type, meta_data):
        if is_take_profit:
            # type, side
            order_info = self.place_order(price, amount, side, self._pair, type=type,
                                          meta_data=meta_data, callback=self._callback_order_status)
        else:
            order_info = self.place_order(price, amount, side, self._pair, type=type,
                                          meta_data=meta_data, callback=None)

    def _callback_order_status(self, data):
        try:
            if not data:
                self._log('support_botmom---77Data is None, return False')
                return False
            # order close
            if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
                # place profit order, return True
                self._log('support_botmom---82_callback_order_status with previous data {}'.format(data))
                meta_data = data[KEY_GET_ORDER_META_DATA]
                web_input = meta_data['web_input']
                profit = web_input['profit']
                side = BUY if data[KEY_GET_ORDER_SIDE] == SELL else SELL
                price_profit = float(Decimal(data[KEY_GET_ORDER_AVERAGE_PRICE]) \
                                     - Decimal(str(STEP_WISE[side])) * Decimal(profit))
                order_info = self.place_order(price_profit, data[KEY_GET_ORDER_AMOUNT], side, self._pair, type=LIMIT,
                                 callback=self.__callback_order_profit)

                is_take_stop_loss = web_input.get('take_stop_loss', False)
                if is_take_stop_loss and order_info:
                    s_stop_loss_value = web_input['stop_loss']
                    type_stop_loss = web_input['type_stop_loss']
                    price_stop_loss = float(Decimal(data[KEY_GET_ORDER_AVERAGE_PRICE]) \
                                     + Decimal(str(STEP_WISE[side])) * Decimal(s_stop_loss_value))
                    self.place_stop_loss_order_helper(price_stop_loss, data[KEY_GET_ORDER_FILLED], side, self._pair,
                                                      type_stop_loss, cb_when_order_open=self._callback_when_stop_loss_open,
                                                      order_profit_id=order_info[KEY_GET_ORDER_ID])
            elif ORDER_CANCELED == data[KEY_GET_ORDER_STATUS]:
                self._log('Something wired, Order canceled')
        except Exception as e:
            tb = traceback.format_exc()
            print('ERROR {}'.format(tb))
            self._log('support_botmom---106ERROR {}'.format(tb))

    def _callback_when_stop_loss_open(self, data):
        self._log('Stop loss order open {}'.format(data))

    def __callback_order_profit(self, data):
        if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
            self._log("support_botmom---113 Order profit callback {}".format(data))
