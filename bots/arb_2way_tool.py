import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
lib_path = dir_path + '/../libs'
bot_ac_path = dir_path + '/../bot_action'
sys.path.append(lib_path)
sys.path.append(dir_path)
sys.path.append(bot_ac_path)
from bot_father import *
from bot_constant import *
from exchange_lib import *
from sqldata_insert import *
from support_order_follow_market import SupportOrderFollowMarket
from pprint import pprint


class Arb2WayBot(SupportOrderFollowMarket, BotFather):

    bot_alias = 'Arb2WayBot'
    key_exchange_1 = 'ex_1'
    key_exchange_2 = 'ex_2'
    profit_exchange = 'profit_exchange'
    min_profit = 'min_profit'
    follow_market = 'follow_market'


    def __init__(self):
        super().__init__(self.bot_alias)
        self._stake_exchange = {}
        self._amount = '0.0'
        self._profit = '0.0'

    def bot_entry(self, web_input):
        try:
            # create list exchange
            self._ex_id1 = web_input['ex_id1']
            self._api_name1 = web_input['api_name1']
            min_profit = float(web_input["min_profit"])
            self._min_profit = min_profit
            self.min_profit = min_profit

            self._ex_id2 = web_input['ex_id2']
            self._api_name2 = web_input['api_name2']

            self._stake_exchange = {
                self.key_exchange_1: self._define_exchange_key(self._ex_id1, self._api_name1),
                self.key_exchange_2: self._define_exchange_key(self._ex_id2, self._api_name2),
            }
            web_input.update({
                'list_ex': [{'ex_id': self._ex_id1, 'api_name': self._api_name1},
                 {'ex_id': self._ex_id2, 'api_name': self._api_name2}]
            })

            super().bot_entry(web_input)
            # exchange_profit
            self._exchange_profit = web_input['exchange_profit']
            self._amount = float(web_input['amount'])
            self._profit = float(web_input['profit'])
            # self._fees = float(web_input['fees'])
            self._log('arb_2way_toolmom---55Bot {} start'.format(self.alias))
        except:
            tb = traceback.format_exc()
            self._log(f'arb_2way_toolmom---58ERROR bot entry {tb}')
    def begin_trading(self, web_input):
        try:
            price = float(web_input['price'])
            self._price = price

            exchange_profit = web_input['exchange_profit']
            side = web_input['side']
            amount = float(web_input["amount"])
            profit = float(web_input["profit"])
            follow_market = web_input["follow_market"]
            self._follow_market = follow_market
            is_parallel = web_input["is_parallel"]
            self._is_parallel = is_parallel
            gap = float(web_input.get('gap', 0))
            self._gap = gap

            follow_gap = float(web_input.get('follow_gap', 0))
            self._follow_gap = follow_gap
            postOnly = web_input.get('postOnly', False)
            self._postOnly = postOnly
            open_key_exchange = self._fetch_revert_exchange(exchange_profit)
            profit_key_exchange = self._stake_exchange[exchange_profit]
            self._log(
                f'arb_2way_toolmom---76Begin trade with exchange profit {exchange_profit} {side} with amount {amount} and profit {profit} and price {price}')
            if is_parallel:
                self.submit_task(self.msf_place_order_follow_market_helper, self._pair, side, amount, None,
                                                                       self._callback_of_profit_order, None, open_key_exchange, False, {}, None, gap, follow_gap, postOnly)
                self._log(f'arb_2way_toolmom---80Place order {side.upper()} on-exchange {open_key_exchange}')
                self.submit_task(self.msf_place_order_follow_market_helper, self._pair, self._fetch_revert_side(side), amount, None,
                                                                       self._callback_of_profit_order, None, profit_key_exchange, False, {}, None, gap, follow_gap, postOnly)
                self._log(f'arb_2way_toolmom---83Place tp-order {side.upper()} on-exchange {profit_key_exchange}')
            else:
                if not price:
                    price = 0
                    self._log(f'arb_2way_toolmom---87Market price is {price} on-exchange {open_key_exchange}')
                # place open order
                meta_data = {
                    self.profit_exchange: profit_key_exchange,
                    'profit': profit,
                    self.min_profit: min_profit,
                    self.follow_market: follow_market,
                    'gap': gap,
                    'follow_gap': follow_gap,
                    'postOnly': postOnly,
                }
                order_info = self.msf_place_order_follow_market_helper(self._pair, side, amount, price, self._callback_open_pos_order,
                                                          meta_data=meta_data, key_exchange=open_key_exchange, gap=gap, follow_gap=follow_gap, postOnly=postOnly)
                if order_info:
                    self._log(f'arb_2way_toolmom---101begin trade with order info {order_info} on-exchange {open_key_exchange}')
        except:
            tb = traceback.format_exc()
            self._log(f'arb_2way_toolmom---104ERROR begin_trading {tb}')

    def _callback_open_pos_order(self, data):
        try:
            if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
                self._log(f'arb_2way_toolmom---109# Open order is filled {data}')
                sql_insertedarb_2way = sql_insert_arb_2way_toolbot(data,self._own_name,self._channel,self._ex_id1,self._api_name1,self._ex_id2,self._api_name2,self._profit,self._min_profit,self._price,self._follow_market,self._is_parallel,self._postOnly,self._gap,self._follow_gap)
                self._log(f'arb_2way_toolmom---114open order is filled {sql_insertedarb_2way}')
                meta_data = data[KEY_GET_ORDER_META_DATA]
                ex_change_profit = meta_data[self.profit_exchange]
                profit = meta_data['profit']
                follow_market = meta_data[self.follow_market]
                gap = meta_data['gap']
                follow_gap = meta_data['follow_gap']
                postOnly = meta_data['postOnly']

                min_profit = meta_data[self.min_profit]
                profit_side = self._fetch_revert_side(data[KEY_GET_ORDER_SIDE])
                price_profit = float(Decimal(str(data[KEY_GET_ORDER_AVERAGE_PRICE])) - Decimal(str(STEP_WISE[profit_side])) * Decimal(str(profit)))
                if not min_profit:
                    min_price_profit = None
                else:
                    min_price_profit = float(Decimal(str(data[KEY_GET_ORDER_AVERAGE_PRICE])) - Decimal(str(STEP_WISE[profit_side])) * Decimal(str(min_profit)))
                self._log(f'arb_2way_toolmom---125Place order profit {profit_side} {data[KEY_GET_ORDER_FILLED]} with threshold price is {min_price_profit} on-ex {ex_change_profit}')
                # min price follow market
                if follow_market:
                    self.msf_place_order_follow_market_helper(self._pair, profit_side, data[KEY_GET_ORDER_FILLED], None, callback=self._callback_of_profit_order,
                                 key_exchange=ex_change_profit, base_threshold_price=min_price_profit, gap=gap, follow_gap=follow_gap, postOnly=postOnly)
                else:
                    self.place_order(price_profit, data[KEY_GET_ORDER_FILLED], profit_side, self._pair, type=LIMIT,
                                     callback=self._callback_of_profit_order, key_exchange=ex_change_profit)
        except:
            tb = traceback.format_exc()
            self._log(f'arb_2way_toolmom---135ERROR callback tp: {tb}')

    def _callback_of_profit_order(self, data):
        if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
            self._log(f'arb_2way_toolmom---139Order profit filled {data}')
            sql_insertedarb_2way = sql_insert_arb_2way_toolbot(data,self._own_name,self._channel,self._ex_id1,self._api_name1,self._ex_id2,self._api_name2,self._profit,self._min_profit,self._price,self._follow_market,self._is_parallel,self._postOnly,self._gap,self._follow_gap)
            self._log(f'arb_2way_toolmom---146Order profit filled {sql_insertedarb_2way}')


        elif ORDER_CANCELED == data[KEY_GET_ORDER_STATUS]:
            self._log(f'arb_2way_toolmom---141Order profit cancelled {data}')

    def _fetch_revert_exchange(self, exchange_key):
        if self.key_exchange_1 == exchange_key:
            return self._stake_exchange[self.key_exchange_2]
        # else
        return self._stake_exchange[self.key_exchange_1]

