import os
import sys
from decimal import Decimal
import time
from threading import Thread

cur_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(cur_path + '/../libs')
sys.path.append(cur_path + '/../repositories')
from bot_father import BotFather
from bot_constant import *
import traceback

CODE_BOT_BUY_AND_SELL_TOGETHER = 1
CODE_BOT_BUY_THEN_SELL = 2
CODE_BOT_SELL_THEN_BUY = 3


class BuySellParallelBot(BotFather):

    def __init__(self):
        super().__init__('BUY_SELL_PARALLEL')
        self._trade_count = 0
        self._do_cron_job = False
        self._base_curr = ''
        self._quote_curr = ''
        self._curr_price_trigger = []
        self._time_sleep = 10

    def bot_entry(self, web_input):
        super().bot_entry(web_input)
        # get params
        self._base_curr, self._quote_curr = self._pair.split('/')
        self._log('buy_sell_parallel_botmom---34base coin {}, quote coin {}'.format(self._base_curr, self._quote_curr))

    def cron_job_begin(self, web_input):
        self._do_cron_job = web_input['interval_place_order']
        if not self._do_cron_job:
            self._log('buy_sell_parallel_botmom---39Stop cron job place order')
            return True
        # new, reset curr price
        # self._curr_price_trigger = []
        # self._log('Curr price trigger {}'.format(self._curr_price_trigger))
        self._time_sleep = float(web_input.get('interval', 10))
        bot_type = int(web_input['bot_type'])
        # self._log('Balance current: {}'.format(self.ex_instant.fetch_balance()))
        self._log('buy_sell_parallel_botmom---47Start cron job place order, time sleep {}'.format(self._time_sleep))
        while self._do_cron_job and not self._terminate:
            try:
                #  if scenario A or B or C
                if CODE_BOT_BUY_AND_SELL_TOGETHER == bot_type:
                    # self.begin_trade(web_input)
                    Thread(target=self.begin_trade, args= (web_input, )).start()
                elif CODE_BOT_BUY_THEN_SELL == bot_type:
                    # self.begin_trade_scenario_buy_sell_sequence(web_input, BUY)
                    Thread(target=self.begin_trade_scenario_buy_sell_sequence, args=(web_input, BUY, )).start()
                elif CODE_BOT_SELL_THEN_BUY == bot_type:
                    # self.begin_trade_scenario_buy_sell_sequence(web_input, SELL)
                    Thread(target=self.begin_trade_scenario_buy_sell_sequence, args=(web_input, SELL, )).start()
                self._log('buy_sell_parallel_botmom---60Time sleep {}'.format(self._time_sleep))
                self._interuptable_waiting(self._time_sleep)
            except Exception as e:
                self._log('buy_sell_parallel_botmom---63ERROR {}'.format(e))

    def begin_trade(self, web_input):
        try:
            amount = web_input['amount']
            profit = web_input['profit']
            # get price
            # current price
            current_price = self._fetch_market_price(self._pair)
            if current_price:
                # Order buy
                buy_price = float(Decimal(str(current_price)) - Decimal(profit) / Decimal('2'))
                sell_price = float(Decimal(str(current_price)) + Decimal(profit) / Decimal('2'))
                self._log('buy_sell_parallel_botmom---76self.ex_instance.fetch_balance(self._base_curr) {}'.format(self.ex_instance.fetch_balance(coin=self._base_curr)))
                if float(self.ex_instance.fetch_balance(coin=self._base_curr)['free']) >= float(amount) \
                        and float(self.ex_instance.fetch_balance(coin=self._quote_curr)['free']) >= float(Decimal(amount) * Decimal(str(buy_price))):
                    # check current price
                    count = 3
                    while self._curr_price_trigger and current_price in self._curr_price_trigger and count > 0:
                        count -= 1
                        self._log('buy_sell_parallel_botmom---83same price {}__{}'.format(current_price, self._curr_price_trigger))
                        self._interuptable_waiting(self._time_sleep/5)
                        current_price = self._fetch_market_price(self._pair)
                        if count == 1 and current_price in self._curr_price_trigger:
                            self._log('buy_sell_parallel_botmom---87Same price, ignore round, wait next round')
                            return False
                    self._curr_price_trigger.append(current_price)
                    self._trade_count += 1
                    # profit = web_input['profit']
                    number_trader = self._trade_count
                    self._log('buy_sell_parallel_botmom---93Count number trader {}'.format(number_trader))
                    # market order and callback place profit order
                    meta_data = {
                        'trade_id': number_trader,
                        'current_price': current_price,
                    }
                    order_buy_info = self.place_order(buy_price, amount, BUY, self._pair, type=LIMIT,
                                                      meta_data=meta_data, callback=self._callback_buy_sell_parallel)
                    # Order sell
                    order_sell_info = self.place_order(sell_price, amount, SELL, self._pair, type=LIMIT,
                                                       meta_data=meta_data, callback=self._callback_buy_sell_parallel)
                    if order_sell_info and order_buy_info:
                        self._log('buy_sell_parallel_botmom---105 Trade {} create 2 order BUY_{}_{}_{} ans SELL {}__{}_{}'.format(number_trader,
                                order_buy_info[KEY_GET_ORDER_ID], amount, buy_price, order_sell_info[KEY_GET_ORDER_ID], amount, sell_price))
                    else:
                        self._log('buy_sell_parallel_botmom---108 BOT error, not fetch price market')
                else:
                    self._log('buy_sell_parallel_botmom---110 Bot not enough money')
            return True
        except Exception as e:
            tb = traceback.format_exc()
            print('ERROR {}'.format(tb))
            self._log('buy_sell_parallel_botmom---115 ERROR {}'.format(tb))

    def _callback_buy_sell_parallel(self, data):
        try:
            if not data:
                self._log('buy_sell_parallel_botmom---120 Data is None, return False')
                return False
            # order close
            if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
                previous_curr_price = data[KEY_GET_ORDER_META_DATA]['current_price']
                if previous_curr_price in self._curr_price_trigger:
                    self._curr_price_trigger.remove(previous_curr_price)
                    self._log('buy_sell_parallel_botmom---127 Remove curr price trigger {}__{}'.format(previous_curr_price, self._curr_price_trigger))
                # place profit order, return True
                self._log('buy_sell_parallel_botmom---129 Order {}__{}__{}__{}__{}'.format(data[KEY_GET_ORDER_ID], data[KEY_GET_ORDER_SIDE],
                                                            data[KEY_GET_ORDER_AMOUNT],
                                                            data[KEY_GET_ORDER_AVERAGE_PRICE],
                                                            data[KEY_GET_ORDER_STATUS]))

            elif ORDER_CANCELED == data[KEY_GET_ORDER_STATUS]:
                self._log('buy_sell_parallel_botmom---135Something wired, Order canceled .. Order {}__{}__{}__{}__{}'
                          .format(data[KEY_GET_ORDER_ID], data[KEY_GET_ORDER_SIDE], data[KEY_GET_ORDER_AMOUNT],
                                  data[KEY_GET_ORDER_PRICE], data[KEY_GET_ORDER_STATUS]))
        except Exception as e:
            tb = traceback.format_exc()
            print('ERROR {}'.format(tb))
            self._log('buy_sell_parallel_botmom---141 ERROR {}'.format(tb))

    def _callback_order_status(self, data):
        try:
            if not data:
                self._log('buy_sell_parallel_botmom---146 Data is None, return False')
                return False
            # order close
            if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
                # place profit order, return True
                self._log('buy_sell_parallel_botmom---151 Order {}__{}__{}__{}__{}'.format(data[KEY_GET_ORDER_ID], data[KEY_GET_ORDER_SIDE],
                                                            data[KEY_GET_ORDER_AMOUNT],
                                                            data[KEY_GET_ORDER_AVERAGE_PRICE],
                                                            data[KEY_GET_ORDER_STATUS]))

            elif ORDER_CANCELED == data[KEY_GET_ORDER_STATUS]:
                self._log('buy_sell_parallel_botmom---157 Something wired, Order canceled .. Order {}__{}__{}__{}__{}'
                          .format(data[KEY_GET_ORDER_ID], data[KEY_GET_ORDER_SIDE], data[KEY_GET_ORDER_AMOUNT],
                                  data[KEY_GET_ORDER_PRICE], data[KEY_GET_ORDER_STATUS]))
        except Exception as e:
            tb = traceback.format_exc()
            print('ERROR {}'.format(tb))
            self._log('buy_sell_parallel_botmom---163 ERROR {}'.format(tb))

    def begin_trade_scenario_buy_sell_sequence(self, web_input, side=BUY):
        try:
            amount = web_input['amount']
            profit = web_input['profit']
            # get price
            # current price
            count = 3
            current_price = self._fetch_market_price(self._pair)
            if current_price:
                # place order
                price = float(Decimal(str(current_price)) - Decimal(str(STEP_WISE[side])) * Decimal(profit) / Decimal('2'))
                if SELL == side:
                    is_enough_money = float(self.ex_instance.fetch_balance(coin=self._base_curr)['free']) >= float(amount)
                else:
                    is_enough_money = float(self.ex_instance.fetch_balance(coin=self._quote_curr)['free']) >= float(
                        Decimal(amount) * Decimal(str(price)))
                self._log('buy_sell_parallel_botmom---181{}__{}__{}'.format(side, is_enough_money, amount))
                if is_enough_money:
                    while self._curr_price_trigger and current_price in self._curr_price_trigger and count > 0:
                        count -= 1
                        self._log('buy_sell_parallel_botmom---185 same price {}__{}'.format(current_price, self._curr_price_trigger))
                        self._interuptable_waiting(self._time_sleep / 5)
                        current_price = self._fetch_market_price(self._pair)
                        if count == 1 and current_price in self._curr_price_trigger:
                            self._log('buy_sell_parallel_botmom---189 Same price, ignore round, wait next round')
                            return False
                    # Order buy
                    self._curr_price_trigger.append(current_price)
                    self._trade_count += 1
                    # profit = web_input['profit']
                    number_trader = self._trade_count
                    self._log('buy_sell_parallel_botmom---196 Count number trader {} __{}'.format(number_trader, side))
                    # market order and callback place profit order
                    meta_data = {
                        'trade_id': number_trader,
                        'profit': profit,
                        'current_price': current_price
                    }
                    order_info = self.place_order(price, amount, side, self._pair, type=LIMIT,
                                                      meta_data=meta_data, callback=self._callback_open_position_order_status)
                    if not order_info:
                        self._log('buy_sell_parallel_botmom---206 Trade id {} place order fail'.format(self._trade_count))
                else:
                    self._log('buy_sell_parallel_botmom---208 Bot not enough money')
            return True
        except Exception as e:
            tb = traceback.format_exc()
            print('ERROR {}'.format(tb))
            self._log('buy_sell_parallel_botmom---213 ERROR {}'.format(tb))

    def _callback_open_position_order_status(self, data):
        try:
            if not data:
                self._log('buy_sell_parallel_botmom---218Data is None, return False')
                return False
            # order close
            if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
                # place profit order, return True
                self._log('buy_sell_parallel_botmom---223_callback_open_position_order_status {}__{}__{}__{}__{}'
                          .format(data[KEY_GET_ORDER_ID], data[KEY_GET_ORDER_SIDE], data[KEY_GET_ORDER_AMOUNT],
                            data[KEY_GET_ORDER_AVERAGE_PRICE], data[KEY_GET_ORDER_STATUS]))
                # place order
                profit = data[KEY_GET_ORDER_META_DATA]['profit']
                previous_curr_price = data[KEY_GET_ORDER_META_DATA]['current_price']
                if previous_curr_price in self._curr_price_trigger:
                    self._curr_price_trigger.remove(previous_curr_price)
                    self._log('buy_sell_parallel_botmom---231 Remove curr price trigger {}__{}'.format(previous_curr_price, self._curr_price_trigger))
                meta_data = {
                    'trade_id': data[KEY_GET_ORDER_META_DATA]['trade_id'],
                    'profit': profit,
                }
                side = BUY if data[KEY_GET_ORDER_SIDE] == SELL else SELL
                price = Decimal(str(data[KEY_GET_ORDER_AVERAGE_PRICE])) - Decimal(str(STEP_WISE[side])) * Decimal(
                    profit)
                order_info = self.place_order(price, data[KEY_GET_ORDER_AMOUNT], side, self._pair, type=LIMIT,
                                              meta_data=meta_data, callback=self._callback_order_status)
                if not order_info:
                    self._log('buy_sell_parallel_botmom---242Trade id {} place order fail'.format(self._trade_count))
            elif ORDER_CANCELED == data[KEY_GET_ORDER_STATUS]:
                self._log('buy_sell_parallel_botmom---244Something wired, _callback_open_position_order_status canceled .. Order {}__{}__{}__{}__{}'
                          .format(data[KEY_GET_ORDER_ID], data[KEY_GET_ORDER_SIDE], data[KEY_GET_ORDER_AMOUNT],
                                  data[KEY_GET_ORDER_PRICE], data[KEY_GET_ORDER_STATUS]))
        except Exception as e:
            tb = traceback.format_exc()
            print('ERROR {}'.format(tb))
            self._log('buy_sell_parallel_botmom---250ERROR {}'.format(tb))


