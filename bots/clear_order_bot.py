import sys
import os
from collections import defaultdict
from decimal import Decimal

dir_path = os.path.dirname(os.path.realpath(__file__))
lib_path = dir_path + '/../libs'
sys.path.append(lib_path)
sys.path.append(dir_path)
from bot_father import BotFather
from bot_constant import *
from sqldata_insert import *
from pprint import pprint


class ClearOrderBot(BotFather):
    alias = 'ClearOrderBot'

    def __init__(self):
        super().__init__(self.alias)
        self._pair = None

    def bot_entry(self, web_input):
        if not web_input:
            web_input.update({
                'ex_id': 'BIN',
                'pair': 'BTC/USDT',
                'own_name': 'dev',
                'api_name': 'ngocngoc.hh1',
                'amount': 0.002
            })
        super().bot_entry(web_input)
        self._log('clear_order_botmom---31CLEAR AND AVERAGE ORDER BOT START ^^')
        self._side =  web_input["side"]
        

    """
    Cancel order sell/buy with pair
    """

    def cancel_order(self, web_input):
        if not web_input:
            web_input.update({
                'ex_id': 'BIN',
                'pair': 'BTC/USDT',
                'own_name': 'dev',
                'api_name': 'ngocngoc.hh1',
                'side': 'buy'
            })
        self._cancel_side = web_input['side']
        self._price_type = web_input['price_type']
        self._signal = web_input['signal']
        self._uuid = web_input['uuid']
        

        # fetch order and cancel
        self._log('clear_order_botmom---48Start cancelling {} orders'.format(self._pair))
        self.ex_instance.cancel_all_open_orders(None, [self._pair], self._cancel_side, switch2restapi=True)
        self._log('clear_order_botmom---50End cancel {} orders'.format(self._pair))
        

    """
    Clear order sell/buy with pair and price market/limit
    """

    def clear_order(self, web_input):
        if not web_input:
            web_input.update({
                'ex_id': 'BIN',
                'pair': 'BTC/USDT',
                'own_name': 'dev',
                'api_name': 'ngocngoc.hh1',
                'side': 'buy',
                'price_side': 'limit'
            })
        self._clear_side = web_input['side']
        self._clear_price_side = web_input['price_type']

        # fetch order and clear
        self._log('clear_order_botmom--70Start clear {} orders'.format(self._pair))
        # TODO: call restapi to get orders open based on order_progress
        open_orders = self.ex_instance.fetch_open_orders_restapi(self._pair)
        # order_dict = self.ex_instance.fetch_open_orders(self._pair)
        # for order_id, data in order_dict.items():
        #     if data['side'] != self._clear_side:
        for order in open_orders:
            if self._clear_side != order.get('side'):
                continue
            self.ex_instance.cancel_order(order.get('id'), self._pair)
            # partial-fill, create new order with remaining amount and best price(limit/market)
            filled = float(order.get('filled'))  # data['accu_amount']
            amount = float(order.get('amount'))  # data['amount']
            self._amount = amount
            if float(filled) > 0.002:
                self._log('clear_order_botmom---85Partial filled {} with Pair {}'.format(filled, self._pair))
                self._amount = float(amount) - float(filled)
            self.create_trade_order(self._clear_side)

            self._log('clear_order_botmom---89Clear Order ID  {} with Pair {}'.format(order.get('id'), self._pair))

        self._log('clear_order_botmom---91End clear {} orders'.format(self._pair))
        

    def create_trade_order(self, side):
        if self._clear_price_side == 'limit':
            price = self._fetch_best_price(self._pair, side)
        else:  # price_side = market(sell = bid, buy = ask)
            ask, bid = self._fetch_best_price(self._pair)
            price = ask if side == 'buy' else bid
        self.place_order(price, self._amount, side, self._pair, type='limit', callback=self.callback_order_status)

    def callback_order_status(self, data):
        if ORDER_PROFILE['status']['closed'] == data['status']:
            self._log('clear_order_botmom---103Order {} is {}'.format(data['order_id'], data['status']))
        if ORDER_PROFILE['clear_order_botmom---104status']['canceled'] == data['status']:
            self._log('clear_order_botmom---105Order cancel')

    """
    AVG order
    """
    def avg_order(self, web_input):
        side = web_input['side']
        self._log('clear_order_botmom---112Start average {} orders'.format(self._pair))
        open_orders = self.ex_instance.fetch_open_orders_restapi(self._pair)
        if open_orders is None:
            self._log('clear_order_botmom---115No has open order')
            return True
        vol = Decimal('0.0')
        sum_cost = Decimal('0.0')
        for order in open_orders:
            order_id = order.get('id')
            if side != order.get('side'):
                continue
            self._cancel_order_with_retry(order.get('id'), self._pair)
            # partial-fill, create new order with remaining amount and best price(limit/market)
            # fetch order
            order_info = self.ex_instance.fetch_order_progress(order_id)
            self._log('clear_order_botmom---127{}'.format(order_info))
            avg_start="start"
            avg_limit="price_limit"
            clear_order_inserted = sql_clear_order_bot(order_info,self._own_name,self._ex_id,self._api_name,self._pair,self._side,self._price_type,self._signal,self._uuid,order_id)
            self._log(f'clear_order_botmom-------------clear_order_botdatabase{clear_order_inserted}')

            # amount = Decimal(str(order_info[KEY_GET_ORDER_AMOUNT]))
            amount = Decimal(str(order_info['amount']))
            # filled = Decimal(str(order_info[KEY_GET_ORDER_FILLED]))
            filled = Decimal(str(order_info['accu_amount']))
            # price = Decimal(str(order_info[KEY_GET_ORDER_PRICE]))
            price = Decimal(str(order_info['price']))
            vol += amount - filled
            sum_cost += price * (amount - filled)
        self._log('clear_order_botmom---136Sum vol open order {} orders on {}, cost {}'.format(float(vol), self._pair, float(sum_cost)))
        if float(vol) > 0:
            price = float(sum_cost/vol)
            self.place_order(price, float(vol), side, self._pair, type=LIMIT, callback=None)
