import logging
import os
from threading import Thread
from concurrent.futures.thread import ThreadPoolExecutor

import sys
from decimal import Decimal
dir_path = os.path.dirname(os.path.realpath(__file__))
lib_path = dir_path+'/../libs'
sys.path.append(lib_path)
from exchange_lib import *
from common import log, socket_emit

class ToolBuySell:
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
        # for web
        self.socketIo = None
        self.chanel = None
        self._logger = logging.getLogger('tool_bs')
        # exchange
        self.ex = None
        self.ex_id = None
        self.own_name = None
        self.api_name = None
        # for trade
        self.__min_amount = 0.002
        self.pair = None
        # self.amount = 0
        self.profit = 0
        self.step_stop_loss = 0
        self.stop_loss_type = None
        self._terminate = False
        self._this_order_type = 'limit'
        self.executor = ThreadPoolExecutor(max_workers=20)


    def bot_entry(self, web_inputs):
        if not web_inputs:
            return False
        # assignment to self
        self.socketIo = web_inputs['socketio']
        self.chanel = web_inputs['chanel']
        if self.chanel:
            self._logger = logging.getLogger(self.chanel)
        self.__config_logger()
        self.pair = web_inputs['pair']
        self.amount = web_inputs['amount']
        self.profit = float(web_inputs['profit'])
        self.step_stop_loss = float(web_inputs['step_stop_loss'])
        self.stop_loss_type = web_inputs['stop_loss_type']
        # init exchange object
        self.ex_id = web_inputs['ex_id']
        self.own_name = web_inputs['own_name']
        self.api_name = web_inputs['api_name']
        self.ex = exchange(self.ex_id, self._logger, self.socketIo, self.chanel, api_name=self.api_name, own_username=self.own_name)
        self.ex.register_order_book(self.pair)
        self._log('tool_buy_sellmom---72TOOL BUY SELL START ^^')
        self.executor.submit(self.emit_price_table)

    def emit_price_table(self):
        while not self._terminate:
            # emit price table
            ask, bid = self._fetch_latest_price(None, get_ask_bid=True)
            price_data = {'Chain': self.pair, 'Ask': ask, 'Bid': bid}
            socket_emit(price_data, self.socketIo, self.chanel, 'log_tool_bs_price')
            time.sleep(0.2)
        self._log('tool_buy_sellmom---TOOL BUY SELL STOP, STOP LISTEN ^^')

    def _log(self, data='', severity='info'):
        log(data, self._logger, self.socketIo, self.chanel, log_severity=severity)

    def __config_logger(self):
        self._logger.setLevel(logging.DEBUG)
        script_path = os.path.dirname(os.path.realpath(__file__))
        file_name = 'tool_bs_' + datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        if self.socketIo:
            file_name = 'tool_bs_' + self.chanel
        # create file handler which logs even debug messages
        fh = logging.FileHandler(script_path + '/../web/logs/' + str(file_name) + '.log')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self._logger.addHandler(fh)

    """
    External usage method
    """
    def terminate(self):
        self._terminate = True

    def _fetch_latest_price(self, profile, get_ask_bid=False):
        ask_info, bid_info = None, None
        while ask_info is None or bid_info is None:
            ask_info, bid_info = self.ex.fetch_order_book(self.pair, 1)
        ask = float(ask_info[0])
        bid = float(bid_info[0])
        if get_ask_bid:
            return ask, bid
        # Get calculated price for each pair
        price = ask if 'sell' == profile else bid
        return price

    def start_trade_trigger(self, profile, amount, this_type, price, profit=None, step_stop_loss=None, using_stop_loss=True):
        try:
            self._log('tool_buy_sellmom---120 start_trade_trigger : {} {}  {} {}'.format(profile, amount, profit, step_stop_loss))
            trade_thread = Thread(target=self.start_trade, args=(profile, amount, this_type, price, profit,
                                                                 step_stop_loss, using_stop_loss))
            trade_thread.start()
        except Exception as e:
            tb = traceback.format_exc()
            print('TB {}'.format(tb))

    def start_trade(self, profile, amount, this_type, price, profit=None, step_stop_loss=None, using_stop_loss=True):
        side = ToolBuySell.PROFILE[profile]['side']
        profit_side = ToolBuySell.PROFILE[profile]['profit_side']
        step_wise = ToolBuySell.PROFILE[profile]['step_wise']
        stop_loss_type = 'limit' if 'market' != self.stop_loss_type else 'market'
        # fetch price
        if not price:
            price = self._fetch_latest_price(profile)
        # place order
        self._log('tool_buy_sellmom---137Start trade: {} {}  {} {}'.format(profile, amount, profit, step_stop_loss))
        self._log('tool_buy_sellmom---138Balance current: {}'.format(self.ex.fetch_balance()))
        order_id = self.ex.create_order(self.pair, this_type, side, amount, price)
        if order_id == 'invalid_cmd' or order_id == 'rate_limit':
            return None
        # wait order filled or stop loss
        self._log('tool_buy_sellmom---143Create order for side: {}, price: {}, type: {}, order_id: {}'.format(side, price, this_type, order_id))
        count = 3
        while not self.ex.fetch_order_progress(order_id) and count > 0:
            self._log('tool_buy_sellmom---146Wait info order_id: {}'.format(order_id))
            count -= 1
            time.sleep(0.2)
        self._log('tool_buy_sellmom---149+++++++ order_id: {}'.format(order_id))
        progress = self.ex.fetch_order_progress(order_id)
        order_1st_status = progress['order_status']
        filled = progress['accu_amount']
        # place profit order
        if not profit:
            profit = self.profit
        if not step_stop_loss:
            step_stop_loss = self.step_stop_loss
        profit_price = price + step_wise * profit
        stop_loss_price = price - step_wise * step_stop_loss
        sum_partial_fill = 0.0
        profit_amount_ordering = 0.0
        amount_profit_filled = 0.0
        self.order2_id = None
        while 'open' == order_1st_status and not self._terminate:
            # self._log('Wait info order_id: {}, {}'.format(order_id, filled))
            if filled >= self.__min_amount:
                # order profit
                self._log('tool_buy_sellmom---168+++++++ order_id: {} is {}, filled {}'.format(order_id, order_1st_status, filled))
                profit_amount_ordering = float(Decimal(str(profit_amount_ordering)) + Decimal(str(filled)))
                # check if order_2 is opened, cancel and re-create new order with profit_amount_ordering
                if self.order2_id:
                    if not self.ex.cancel_order(self.order2_id, self.pair):
                        self._log('tool_buy_sellmom---173Cannot cancel order id {}'.format(self.order2_id))
                    progress = self.ex.fetch_order_progress(self.order2_id)
                    status = progress['order_status']
                    o2_filled = progress['accu_amount']
                    self._log('tool_buy_sellmom---177Order id {} is {}, filled {}'.format(self.order2_id, status, o2_filled))
                    amount_profit_filled = float(Decimal(str(amount_profit_filled)) + Decimal(str(o2_filled)))
                    profit_amount_ordering = float(Decimal(str(profit_amount_ordering)) - Decimal(str(o2_filled)))
                    self._log('tool_buy_sellmom---180Create new order with amount {}'.format(profit_amount_ordering))
                    time.sleep(0.2)
                Thread(target=self.create_profit_order_and_stop_loss, args=(profit_side, float(profit_amount_ordering), profit_price,
                                                            stop_loss_type, stop_loss_price, step_wise, using_stop_loss)).start()
                # self.create_profit_order_and_stop_loss(profit_side, float(filled), profit_price,
                #                                            stop_loss_type, stop_loss_price, step_wise, using_stop_loss)
                    #return True
                    # if order_2nd_status is canceled or close --> ignore
            time.sleep(5)
            pre_amount_filled = float(sum_partial_fill)
            progress = self.ex.fetch_order_progress(order_id)
            order_1st_status = progress['order_status']
            sum_partial_fill = progress['accu_amount']
            filled = float(Decimal(str(sum_partial_fill)) - Decimal(str(pre_amount_filled)))
        # if order_1st_status is close, canceled
        if 'closed' == order_1st_status:
            self._log('tool_buy_sellmom---196+++++++ order_id: {} is {}'.format(order_id, order_1st_status))
            sum_profit_amount_ordered = float(Decimal(str(amount_profit_filled)) + Decimal(str(profit_amount_ordering)))
            if sum_profit_amount_ordered >= amount:
                return True
            profit_amount = float(Decimal(str(amount)) - Decimal(str(sum_profit_amount_ordered)))
            self.create_profit_order_and_stop_loss(profit_side, profit_amount, profit_price,
                                                   stop_loss_type, stop_loss_price, step_wise, using_stop_loss)
            return True
        if 'canceled' == order_1st_status:
            self._log('tool_buy_sellmom---205+++++++ order_id: {} is {}'.format(order_id, order_1st_status))
            self._log('tool_buy_sellmom---206Some thing weird, this side order is canceled manually. Id is {}'.format(order_id),
                      severity='error')
            return False

    def create_profit_order_and_stop_loss(self, profit_side, amount, profit_price, stop_loss_type, stop_loss_price,
                                          step_wise, using_stop_loss=True):
        self._log('tool_buy_sellmom---212+++++++ create_profit_order_and_stop_loss, profit_side {}, amount {},'
                  'profit_price {}, stop_loss_type {}, stop_loss_price {} '.format(profit_side, amount, profit_price,
                                                                                   stop_loss_type, stop_loss_price))
        # a_amount = self.amount if not amount else amount
        self.order_2nd_id = self.ex.create_order(self.pair, 'limit', profit_side, amount,
                                            profit_price)
        self.order2_id = self.order_2nd_id
        self._log('tool_buy_sellmom---219Create 2nd order for side: {}, price: {}, type: {}, amount: {},  order_id: {}.'.format(
                profit_side, profit_price, 'limit', amount, self.order_2nd_id))
        # loop check profit order

        count = 3
        while not self.ex.fetch_order_progress(self.order_2nd_id) and count > 0:
            self._log('tool_buy_sellmom---225Wait info order_id: {}'.format(self.order_2nd_id))
            count -= 1
            time.sleep(0.2)
        progress = self.ex.fetch_order_progress(self.order_2nd_id)
        order_2nd_status = progress['order_status']
        filled = progress['accu_amount']
        while 'open' == order_2nd_status and not self._terminate:
            # if price moving up stop loss price, cancel order and place stop loss order
            cur_price = self._fetch_latest_price(profit_side)
            if using_stop_loss and step_wise*cur_price <= step_wise*stop_loss_price:
                # stop loss
                self._log(
                    'tool_buy_sellmom---237Cur_price < stop_loss_price, place order stop loss, profit order id : {}'.format(self.order_2nd_id))

                if not self.ex.cancel_order(self.order_2nd_id, self.pair):
                    self._log('tool_buy_sellmom---240Cannot cancel order id {}'.format(self.order_2nd_id))

                time.sleep(0.05)
                self._log('tool_buy_sellmom---243Cancel 2nd order, order 2nd id: {}'.format(self.order_2nd_id))
                stop_loss_id = self.ex.create_order(self.pair, stop_loss_type, profit_side,
                                                    amount, stop_loss_price)
                self.order2_id = stop_loss_id
                self._log(
                    'tool_buy_sellmom---248Create stop loss order for side: {}, price: {}, type: {}, amount: {},  order_id: {}'.format(
                        profit_side, stop_loss_price, stop_loss_type, amount, stop_loss_id))
            time.sleep(0.3)
            progress = self.ex.fetch_order_progress(self.order_2nd_id)
            order_2nd_status = progress['order_status']
            filled = progress['accu_amount']
