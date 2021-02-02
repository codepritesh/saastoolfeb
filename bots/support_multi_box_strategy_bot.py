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
from sqldata_insert import *
from support_order_follow_market import SupportOrderFollowMarket
from pprint import pprint


class SupportMultiBoxBot(SupportOrderFollowMarket, BotFather):

    bot_alias = 'SupportMultiBoxBot'

    def __init__(self):
        super().__init__(self.bot_alias)
        self._amount = '0.0'
        self._profit = '0.0'


    def bot_entry(self, web_input):
        self._inti_box_buy_price = web_input.get('inti_box_buy_price', '0')
        self._inti_box_sell_price = web_input.get('inti_box_sell_price', '0')
        self._follow_track_box_postOnly = web_input.get('follow_track_box_postOnly', False)
        self._follow_track_box_gap = web_input.get('follow_track_box_gap', '0')
        self._follow_track_box_follow_gap = web_input.get('follow_track_box_follow_gap', '0')
        self._follow_track_box_amount = web_input.get('follow_track_box_amount', '0')
        self._balance_box_amount = web_input.get('balance_box_amount', '0')
        self._balance_box_count = web_input.get('balance_box_count', '0')
        self._follow_balance_box_postOnly = web_input.get('follow_balance_box_postOnly', False)
        self._follow_balance_box_gap = web_input.get('follow_balance_box_gap', '0')
        self._follow_balance_box_follow_gap = web_input.get('follow_balance_box_follow_gap', '0')
        self._follow_balance_box_time = web_input.get('follow_balance_box_time', '1.5')
        self._follow_balance_box_amount = web_input.get('follow_balance_box_amount', '0')
        self._follow_balance_box_count = web_input.get('follow_balance_box_count', '0')
        self._follow_balance_box_profit = web_input.get('follow_balance_box_profit', '0')
        self._follow_balance_box_step = web_input.get('follow_balance_box_step', '0')
        try:
            super(SupportOrderFollowMarket, self).bot_entry(web_input)
            # Fetch open order of this account
            #self.ex_instance.fetch_open_orders_restapi(self._pair)
            self.farthest_buy = self.farthest_sell = self.mid = 0
            self.calc_mid_and_emit()
        except:
            tb = traceback.format_exc()
            self._log('support_multi_box_strategy_botmom---33ERROR {}'.format(tb), severity='error')


    def begin_box1(self, web_input):
        try:
            buy_price, sell_price, amount = self.__parse_agr_initialization_box(web_input)
            self._log(f'support_multi_box_strategy_botmom---38BOX 1 INITIALIZATION web_input amount={amount} buy_price={buy_price} sell_price={sell_price}')
            if self._is_enough_balance(BUY, amount, buy_price, self._pair) and \
                    self._is_enough_balance(SELL, amount, sell_price, self._pair):
                for side, price in (BUY, buy_price), (SELL, sell_price):
                    order_info = self.place_order(price, amount, side, self._pair, type='limit')

                    multi_box_data = sql_support_multi_box(order_info,self._own_name,self._channel,self._ex_id,self._api_name,self._pair,self._inti_box_buy_price,self._inti_box_sell_price,self._follow_track_box_postOnly,self._follow_track_box_gap,self._follow_track_box_follow_gap,self._follow_track_box_amount,self._balance_box_amount,self._balance_box_count,self._follow_balance_box_postOnly,self._follow_balance_box_gap,self._follow_balance_box_follow_gap,self._follow_balance_box_time,self._follow_balance_box_amount,self._follow_balance_box_count,self._follow_balance_box_profit,self._follow_balance_box_step)
                    print("datainserted---------------",multi_box_data)
                    self._log(f'support_multi_box_strategy_botmom---43BOX 1 INITIALIZATION place order {order_info}')
            else:
                self._log('support_multi_box_strategy_botmom---45## Balance insufficient to create order for BOX1')
        except:
            tb = traceback.format_exc()
            self._log('support_multi_box_strategy_botmom---48ERROR {}'.format(tb), severity='error')

    def begin_box2(self, web_input):
        try:
            gap, follow_gap, postOnly, amount, entry_side = self.__parse_agr_follow_track_box(web_input)
            self._log(f'support_multi_box_strategy_botmom---53BOX 2 FOLLOW TRADE web_input {entry_side} amount={amount} gap={gap}')
            self.msf_place_order_follow_market_helper(self._pair, entry_side, amount, 0,
                                                      self._callback_of_fm_order, gap=gap, follow_gap=follow_gap, postOnly=postOnly)
        except:
            tb = traceback.format_exc()
            self._log('support_multi_box_strategy_botmom---58ERROR {}'.format(tb), severity='error')

    def calc_mid_and_emit(self):
        counter = 0
        while not self._terminate:
            time.sleep(0.2)
            counter += 1
            if counter >= 5*1800:
                # fetch open order from rest api every 30mins to make sure it's updated
                #self.ex_instance.fetch_open_orders_restapi(self._pair)
                self.ex_instance.update_ws_order_progress(self._pair)
                counter = 0

            ws_open_orders = self.ex_instance.fetch_open_orders(self._pair)
            buy_price_list = [v[KEY_GET_ORDER_PRICE] for v in ws_open_orders.values() if v[WS_ORDER_PROGRESS.SIDE] == BUY]
            buy_price_list.sort()
            farthest_buy = buy_price_list[0] if buy_price_list else 0
            sell_price_list = [v[KEY_GET_ORDER_PRICE] for v in ws_open_orders.values() if v[WS_ORDER_PROGRESS.SIDE] == SELL]
            sell_price_list.sort()
            farthest_sell = sell_price_list[-1] if sell_price_list else 0
            # Dont update web if there's no change
            if farthest_buy == self.farthest_buy and farthest_sell == self.farthest_sell:
                continue
            if farthest_sell and farthest_buy:
                mid = float((Decimal(str(farthest_buy)) + Decimal(str(farthest_sell))) / Decimal('2'))
            else:
                mid = 0
            self.farthest_buy = farthest_buy
            self.farthest_sell = farthest_sell
            self.mid = mid
            data = {
                'farthest_buy': self.farthest_buy,
                'farthest_sell': self.farthest_sell,
                'mid': self.mid
            }
            self.emit_data_ws(data, 'update')

    def begin_box3(self, web_input):
        try:
            entry_side, entry_amount, count = self.__parse_agr_follow_balance_box(web_input)
            self._log(f'support_multi_box_strategy_botmom---98BOX 3 BALANCING ORDERS web_input amount={entry_amount} count={count}')
            farthest_price = self.farthest_sell if entry_side == SELL else self.farthest_buy

            margin = abs(Decimal(str(farthest_price)) - Decimal(str(self.mid))) / (Decimal(str(count)) + Decimal('1'))
            amount = float(Decimal(str(entry_amount))/Decimal(str(count)))
            for i in range(1, count+1):
                price = float(Decimal(str(self.mid)) - Decimal(str(STEP_WISE[entry_side])) * Decimal(str(i)) * margin)
                if self._is_enough_balance(entry_side, amount, price, self._pair):
                    order_info = self.place_order(price, amount, entry_side, self._pair, type='limit')
                    self._log(f'support_multi_box_strategy_botmom---107BOX 3 BALANCING ORDERS place order {order_info}')
                else:
                    self._log(f'support_multi_box_strategy_botmom---109## Balance insufficient to create order for BOX3 {entry_side} {amount}@{price}')
        except:
            tb = traceback.format_exc()
            self._log('support_multi_box_strategy_botmom---112ERROR {}'.format(tb), severity='error')

    def begin_box4(self, web_input):
        try:
            gap, follow_gap, postOnly, amount, entry_side, *order_md  = self.__parse_agr_follow_balance_box(web_input)
            self._log(f'support_multi_box_strategy_botmom---117BOX 4 FOLLOW BALANCE web_input: {entry_side} amount={amount} gap={gap} \
                  time_delay={order_md[0]} pf_count={order_md[1]} 1st_profit={order_md[2]} step={order_md[-1]}')
            md = {}
            md[self.CANCEL_INTERVAL] = order_md[0]
            md['count'] = order_md[1]
            md['first_profit'] = order_md[2]
            md['profit_step'] = order_md[-1]
            self.msf_place_order_follow_market_helper(self._pair, entry_side, amount, 0,
                               self._callback_of_fm_balance_order, meta_data=md, gap=gap, follow_gap=follow_gap, postOnly=postOnly)
        except:
            tb = traceback.format_exc()
            self._log('support_multi_box_strategy_botmom---128ERROR {}'.format(tb), severity='error')


    def _callback_of_fm_order(self, data):
        if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
            self._log(f'support_multi_box_strategy_botmom---133BOX 2: Follow market order is filled: {data}')

    def _callback_of_fm_balance_order(self, data):
        if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
            self._log(f'support_multi_box_strategy_botmom---137BOX 4: Follow market order is filled: {data}')
            multi_box_data = sql_support_multi_box(data,self._own_name,self._channel,self._ex_id,self._api_name,self._pair,self._inti_box_buy_price,self._inti_box_sell_price,self._follow_track_box_postOnly,self._follow_track_box_gap,self._follow_track_box_follow_gap,self._follow_track_box_amount,self._balance_box_amount,self._balance_box_count,self._follow_balance_box_postOnly,self._follow_balance_box_gap,self._follow_balance_box_follow_gap,self._follow_balance_box_time,self._follow_balance_box_amount,self._follow_balance_box_count,self._follow_balance_box_profit,self._follow_balance_box_step)
            print("datainserted---------------",multi_box_data)
            meta_data = data['meta_data']
            count = meta_data['count']
            first_profit = Decimal(str(meta_data['first_profit']))
            profit_step = Decimal(str(meta_data['profit_step']))
            open_avg_price = Decimal(str(data[KEY_GET_ORDER_AVERAGE_PRICE]))
            open_side = data[KEY_GET_ORDER_SIDE]

            amount = data[KEY_GET_ORDER_AMOUNT]
            amount = float(Decimal(str(amount)) / Decimal(str(count)))
            profit_side = self._fetch_revert_side(open_side)
            profit_price = open_avg_price + Decimal(str(STEP_WISE[open_side])) * first_profit
            for i in range(0, count):
                step_price = float(profit_price - Decimal(str(STEP_WISE[profit_side])) * Decimal(str(i)) * profit_step)
                if self._is_enough_balance(profit_side, amount, step_price, self._pair):
                    order_info = self.place_order(step_price, amount, profit_side, self._pair, type='limit',
                                                            callback=self._callback_of_fm_balance_profit_order)
                    self._log(f'support_multi_box_strategy_botmom---154BOX 4 BALANCING ORDERS place order {i+1}: {order_info}')
                    multi_box_data=sql_support_multi_box(order_info,self._own_name,self._channel,self._ex_id,self._api_name,self._pair,self._inti_box_buy_price,self._inti_box_sell_price,self._follow_track_box_postOnly,self._follow_track_box_gap,self._follow_track_box_follow_gap,self._follow_track_box_amount,self._balance_box_amount,self._balance_box_count,self._follow_balance_box_postOnly,self._follow_balance_box_gap,self._follow_balance_box_follow_gap,self._follow_balance_box_time,self._follow_balance_box_amount,self._follow_balance_box_count,self._follow_balance_box_profit,self._follow_balance_box_step)
                    print("datainserted---------------",multi_box_data)
                else:
                    self._log(f'support_multi_box_strategy_botmom---156## Balance insufficient to create order {i} for BOX4 {profit_side} {amount}@{step_price}')

    def _callback_of_fm_balance_profit_order(self, data):
        if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
            self._log(f'support_multi_box_strategy_botmom---160BOX 4: Profit order is filled: {data}')
            multi_box_data=sql_support_multi_box(data,self._own_name,self._channel,self._ex_id,self._api_name,self._pair,self._inti_box_buy_price,self._inti_box_sell_price,self._follow_track_box_postOnly,self._follow_track_box_gap,self._follow_track_box_follow_gap,self._follow_track_box_amount,self._balance_box_amount,self._balance_box_count,self._follow_balance_box_postOnly,self._follow_balance_box_gap,self._follow_balance_box_follow_gap,self._follow_balance_box_time,self._follow_balance_box_amount,self._follow_balance_box_count,self._follow_balance_box_profit,self._follow_balance_box_step)
            print("datainserted---------------",multi_box_data)

    @exception_logging
    def __parse_agr_initialization_box(self, web_input):
        buy_price = float(web_input.get('inti_box_buy_price', 0))
        self._inti_box_buy_price = buy_price
        sell_price = float(web_input.get('inti_box_sell_price', 0))
        self._inti_box_sell_price = sell_price
        amount = float(web_input.get('inti_box_amount', 0))
        return buy_price, sell_price, amount

    @exception_logging
    def __parse_agr_follow_track_box(self, web_input):
        gap = float(web_input.get('follow_track_box_gap', 0))
        self._follow_track_box_gap = gap
        follow_gap = float(web_input.get('follow_track_box_follow_gap', 0))
        self._follow_track_box_follow_gap = follow_gap
        postOnly = web_input.get('follow_track_box_postOnly', False)
        self._follow_track_box_postOnly = postOnly
        amount = float(web_input.get('follow_track_box_amount', 0))
        self._follow_track_box_amount = amount
        side = web_input.get('side', BUY)
        return gap, follow_gap, postOnly, amount, side


    @exception_logging
    def __parse_agr_follow_balance_box(self, web_input):
        side = web_input.get('side', BUY)
        count = int(web_input.get('balance_box_count', 0))
        self._balance_box_count = count
        amount = float(web_input.get('balance_box_amount', 0))
        self._balance_box_amount = amount
        return side, amount, count

    @exception_logging
    def __parse_agr_follow_balance_box(self, web_input):
        gap = float(web_input.get('follow_balance_box_gap', 0))
        self._follow_balance_box_gap = gap
        follow_gap = float(web_input.get('follow_balance_box_follow_gap', 0))
        self._follow_balance_box_follow_gap = follow_gap
        postOnly = web_input.get('follow_balance_box_postOnly', False)
        self._follow_balance_box_postOnly = postOnly
        amount = float(web_input.get('follow_balance_box_amount', 0))
        self._follow_balance_box_amount = amount
        side = web_input.get('side', BUY)
        cancel_time_delay = float(web_input.get('follow_balance_box_time', 1.5))
        if cancel_time_delay <= 0.0:
            cancel_time_delay = 1.5
        self._follow_balance_box_time = cancel_time_delay
        count = int(float(web_input.get('follow_balance_box_count', 0)))
        self._follow_balance_box_count = count
        first_profit = float(web_input.get('follow_balance_box_profit', 0))
        self._follow_balance_box_profit = first_profit
        profit_step = float(web_input.get('follow_balance_box_step', 0))
        self._follow_balance_box_step = profit_step
        return gap, follow_gap, postOnly, amount, side, cancel_time_delay, count, first_profit, profit_step

