import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
lib_path = dir_path + '/../libs'
sys.path.append(lib_path)
sys.path.append(dir_path)
from bot_father import BotFather
from bot_constant import *
from exchange_lib import *
from exception_decor import  exception_logging


class FollowMarketBot(BotFather):

    def __init__(self):
        super().__init__('FollowMarketBot')
        self._amount = '0.0'
        self.str_profit = '0.0'
        self.str_free_per_one_base_curr = '0.0' # str
        self.str_opposite_market_value = '0.0' # str
        self.trigger_trade = 'BUY' # str
        self.time_fresh = 5 # float
        self.gap_n = '0.0' # str

    @exception_logging
    def bot_entry(self, web_input):
        super().bot_entry(web_input)
        self._amount = web_input['amount']
        self.str_profit = web_input['profit']
        self.str_free_per_one_base_curr = web_input['free_per_one_base_curr']
        self.str_opposite_market_value = web_input['opposite_market_value']
        self.trigger_trade = web_input['trigger_trade']
        self.time_fresh = float(web_input['time_fresh']) # float
        self.gap_n = float(web_input['gap_n']) # float
        self.begin_trading()

    @exception_logging
    def begin_trading(self):
        # begin trade
        self.executor.submit(self._catch_price_market_util_filled, self._pair, self.trigger_trade,
                             self._amount, self.time_fresh, self.gap_n, None, 1, self.cb_open_position_order)
        # const_current_price = self._fetch_market_price(self._pair)

    @exception_logging
    def cb_open_position_order(self, data):
        # callback open position order
        self._log('Cb open position order {}'.format(data))
        # place profit order
        info_r = self._cal_price_avg(data['history_order'])
        price_avg = info_r['price']
        vol = info_r['vol']
        # get data vol, price
        take_profit_side = self._fetch_revert_side(data[KEY_GET_ORDER_SIDE])
        price_profit = float(Decimal(str(price_avg)) - Decimal(str(STEP_WISE[take_profit_side])) * Decimal(self.str_profit))
        order_info = self.place_order(price_profit, self._amount, take_profit_side, self._pair, type=LIMIT, meta_data=None,
                         callback=self.cb_take_profit_and_begin_new_trade)
        # check marker
        if order_info:
            # if previous order - STEP_WISE[side] * Decimal(self._profit)
            self._tracking_price_for_next_step(price_avg, order_info)
            # cancel profit order and place again profit order

    @exception_logging
    def _tracking_price_for_next_step(self, price_open_position_order, order_take_profit):
        # fetch market price
        self._log('folllow_market_bot---67 price {} \n order profit {}'.format(price_open_position_order, order_take_profit))
        market_price = self._fetch_market_price(self._pair)
        open_position_side = self._fetch_revert_side(order_take_profit[KEY_GET_ORDER_SIDE])
        # if market price is price_open_position_order - STEP_WISE[side] * Decimal(self._profit)
        # BUY: 1 * market_price <= (price_open_position_order - STEP_WISE[BUY] * Decimal(self._profit))
        # SELL: -1 * market_price <= (price_open_position_order - STEP_WISE[SELL] * Decimal(self._profit))
        if Decimal(str(STEP_WISE[open_position_side])) * Decimal(str(market_price)) <= Decimal(str(price_open_position_order)) - Decimal(str(STEP_WISE[open_position_side])) * Decimal(self.str_opposite_market_value):
            # cancel profit order
            rs = self._cancel_order_with_retry(order_take_profit[KEY_GET_ORDER_ID], self._pair)
            # place open position order with amount 2 * self._amount
            self.executor.submit(self._catch_price_market_util_filled, self._pair, self.trigger_trade,
                                 str(Decimal('2.0') * Decimal(str(self._amount))), self.time_fresh, self.gap_n, None, 1, self.cb_open_position_order)

    @exception_logging
    def cb_take_profit_and_begin_new_trade(self, data):
        if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
            # begin new trade
            self.begin_trading()
        elif ORDER_CANCELED == data[KEY_GET_ORDER_STATUS]:
            self._log('folllow_market_botmom---86order is cancelled {}'.format_map(data))
