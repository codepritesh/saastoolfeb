import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
lib_path = dir_path + '/../libs'
sys.path.append(lib_path)
sys.path.append(dir_path)
from bot_father import *
from bot_constant import *
from indicator_lib import *
from sqldata_insert import *
from exception_decor import exception_logging
from pprint import pprint


class AtrTrailingStopTool(BotFather):
    bot_alias = 'AtrTrailingStopTool'
    ATRperiod = 5
    nATRMultip = 3.5
    RED = -1
    GREEN = 1

    def __init__(self):
        super().__init__(self.bot_alias)
        self._amount = 0
        self._trade_count = 0
        self._data_info = {}
        self._trade_id = 0

    def bot_entry(self, web_input):
        try:
            super().bot_entry(web_input)
            self._log('tool_atr_trailing_stopmom---31Bot {} start'.format(self.alias))
            self._amount = float(web_input['amount'])
            self._fees = float(web_input['fees'])
            self._profit = float(web_input.get('profit', 5))
            self._base_amount = float(web_input.get('base_amount', 50))/100
            self._trailing_margin = web_input.get('trailing_margin', 5)
            self._ind_obj = Indicator(self.ex_instance)
            self._ind_obj.register_atr_trailing_stop(self._pair)
            self._price = float(self._fetch_market_price(self._pair))
            self._color = -1
        except:
            tb = traceback.format_exc()
            self._log(f'tool_atr_trailing_stopmom---43ERROR when bot entry {tb}')
    def _take_snapshot(self):
        try:
            _snapshot_data = {
                '_data_info' : self._data_info
            }
            self.take_snapshot_data(_snapshot_data)
        except:
            tb = traceback.format_exc()
            self._log(f'tool_atr_trailing_stopmom---53ERROR : {tb}')

    def print_log_realtime(self):
        try:
            while not self._terminate:
                cost_buy = Decimal(str(self._data_info.get(self._first_price, {}).get('cost_buy', 0)))
                cost_sell = Decimal(str(self._data_info.get(self._first_price, {}).get('cost_sell', 0)))
                total_lose = float(cost_sell - cost_buy - (cost_sell + cost_buy) * Decimal(str(self._fees)))
                self._log(f'tool_atr_trailing_stopmom---61CURRENT TOTAL_LOSS = {total_lose}, REVERT_COUNT = {self._revert_count}, TRADE_CLOSED = {self._trade_count}')
                time.sleep(10)
        except:
            tb = traceback.format_exc()
            self._log(f'tool_atr_trailing_stopmom---65ERROR {tb}')

    def begin_trading(self, web_input):
        try:
            self._trade_id += 1
            side = web_input.get('side', 'buy')
            input_price = float(web_input.get('price', 0))
            trade_no = str(self._trade_id)
            self._log(f'tool_atr_trailing_stopmom---73#{trade_no} Begin new trade with side={side}......')

            color = self._ind_obj.fetch_atr_ts(self._pair, self.ATRperiod, self.nATRMultip)[0]
            self._data_info.update({
                trade_no: {'open_order': {},
                           'init_color': color,
                           'base_close_order': {},
                           'trailing_order': {},
                           'is_running': True
                          }
            })

            if not input_price:
                input_price = float(self._fetch_market_price(self._pair))
                self._price = input_price

            self._log(f'tool_atr_trailing_stopmom---88#{trade_no} Place order {side}, color is {color}')
            while not self._terminate and self._data_info[trade_no]['is_running']:
                if self._order_open_position(trade_no, input_price, side, self._amount):
                    return
                time.sleep(0.3)
            self._take_snapshot()

        except:
            tb = traceback.format_exc()
            self._log(f'tool_atr_trailing_stopmom---97ERROR when bot entry {tb}')

    def set_color(self, value):
        self._color = value

    def _fetch_color(self):
        return self._color

    def _check_order_change_color(self, trade_id, side):
        # side is tp-side
        o_side = self._fetch_revert_side(side)
        order_amount = 0
        while not self._terminate and self._data_info[trade_id]['is_running']:
            # TODO: fetch color
            color = self._ind_obj.fetch_atr_ts(self._pair, self.ATRperiod, self.nATRMultip)[0]
            # color = self._fetch_color()
            current_price = float(self._fetch_market_price(self._pair))
            if color != self._data_info[trade_id]['init_color']:
                self._log(f"tool_atr_trailing_stopmom---115#{trade_id} Color change from {self._data_info[trade_id]['init_color']} to {color}")
                # TODO: check order is profit or loss
                open_order_amount = self._data_info[trade_id]['open_order'][KEY_GET_ORDER_FILLED]
                base_order_id = self._data_info[trade_id]['base_close_order'].get(KEY_GET_ORDER_ID)
                base_order_info = self._fetch_order_progress(base_order_id)
                if base_order_info[KEY_GET_ORDER_STATUS] == ORDER_OPEN:
                    self._cancel_order_with_retry(base_order_id, self._pair)
                    base_order_info = self._fetch_order_progress(base_order_id)
                    base_filled = base_order_info[KEY_GET_ORDER_FILLED]
                    order_amount = float(Decimal(str(open_order_amount)) -  Decimal(str(base_filled)))
                elif base_order_info[KEY_GET_ORDER_STATUS] == ORDER_CLOSED:
                    base_filled = base_order_info.get(KEY_GET_ORDER_FILLED, 0)
                    trailing_order_id = self._data_info[trade_id]['trailing_order'].get(KEY_GET_ORDER_ID)
                    while not self._terminate and self._data_info[trade_id]['is_running'] and not trailing_order_id:
                        time.sleep(0.2)
                        trailing_order_id = self._data_info[trade_id]['trailing_order'].get(KEY_GET_ORDER_ID)
                    trailing_order_info = self._fetch_order_progress(trailing_order_id)
                    if trailing_order_info[KEY_GET_ORDER_STATUS] in [ORDER_OPEN, ORDER_PENDING]:
                        self._cancel_order_with_retry(trailing_order_id, self._pair)
                        trailing_order_info = self._fetch_order_progress(trailing_order_id)
                        trailing_filled = trailing_order_info.get(KEY_GET_ORDER_FILLED, 0)
                        order_amount = float(Decimal(str(open_order_amount)) - Decimal(str(base_filled)) - Decimal(str(trailing_filled)))
                    elif trailing_order_info[KEY_GET_ORDER_STATUS] == ORDER_CLOSED:
                        return
                    else:
                        self._log(f'tool_atr_trailing_stopmom---140#{trade_id} STRANGE: trailing_order is cancelled')
                else:
                    self._log(f'tool_atr_trailing_stopmom---142#{trade_id} STRANGE: base_close_order is cancelled')
                if order_amount:
                    # order can got profit
                    if self._order_open_position(trade_id, current_price, side, order_amount, tp_order=True):
                        return
            time.sleep(0.3)

    def _order_open_position(self, trade_no, price, side, amount, order_history=None, tp_order=False):
        try:
            if not order_history:
                order_history = []
            if self._is_enough_balance(side, amount, price, self._pair):
                meta_data = {
                    'order_history': order_history,
                    'trade_id': trade_no
                }
                if tp_order:
                    self._log('tool_atr_trailing_stopmom---159# place {} tp-order {} @ {}....'.format(side.upper(), amount, price))
                    order_info = self.place_order(price, amount, side, self._pair, type=LIMIT,
                                                  meta_data=meta_data, callback=self._cb_signal_tp_order)
                else:
                    self._log('tool_atr_trailing_stopmom---163#{} place {} open position {} @ {}....'.format(trade_no, side.upper(), amount, price))
                    order_info = self.place_order(price, amount, side, self._pair, type=LIMIT,
                                                  meta_data=meta_data, callback=self._cb_open_position_order)
                if order_info:
                    self._waiting_order_open_position(order_info[KEY_GET_ORDER_ID])
                    return True
            self._log('tool_atr_trailing_stopmom---169#{} insufficient balance, cannot place order open position {}_{}_{}'.format(trade_no, side, amount, price))
            return False
        except:
            tb = traceback.format_exc()
            self._log('tool_atr_trailing_stopmom---173ERROR {}'.format(tb), severity='error')
            return False

    def _waiting_order_open_position(self, order_id):
        try:
            count = 0
            while order_id and not self._terminate:
                market_price = float(self._fetch_market_price(self._pair))
                self._interuptable_waiting(0.3)
                progress = self._fetch_order_progress(order_id)
                if not progress:
                    continue
                side = progress[KEY_GET_ORDER_SIDE]
                price = float(progress[KEY_GET_ORDER_PRICE])
                if progress[KEY_GET_ORDER_STATUS] != ORDER_OPEN:
                    break
                count += 1
                if count >= 6:
                    if float(progress[KEY_GET_ORDER_FILLED]) > 0 and count < 100:  # not filled after 30s -> cancel
                        continue
                    # after ~1.5s, if order open position cannot filled, should cancel and recheck
                    if market_price * STEP_WISE[side] > price * STEP_WISE[side]:
                        self._cancel_order_with_retry(order_id, self._pair)
                        self._log('tool_atr_trailing_stopmom---196# cancel {} {} open position order, follow market'.format(order_id, progress[
                            KEY_GET_ORDER_SIDE]))
                        break
        except:
            tb = traceback.format_exc()
            self._log('ERROR {}'.format(tb), severity='error')

    def _cal_info_order_follow_market(self, history_order):
        """
        history order include order info
        """
        sum_amount = Decimal('0')
        sum_cost = Decimal('0')
        for item in history_order:
            if item[KEY_GET_ORDER_FILLED] > 0:
                sum_amount += Decimal(str(item[KEY_GET_ORDER_FILLED]))
                sum_cost += Decimal(str(item[KEY_GET_ORDER_FILLED])) * Decimal(str(item[KEY_GET_ORDER_AVERAGE_PRICE]))
        avg_price = 0 if sum_amount == 0 else float(sum_cost / sum_amount)
        return {
            'avg_price': avg_price,
            'sum_amount': float(sum_amount)
        }

    def _calc_profit_price(self, trade_id, side, price, amount):
        # calc_profit order
        # side = BUY
        o_side = self._fetch_revert_side(side)

        cost_o_side = Decimal(str(self._data_info[trade_id][f'last_rv_{o_side}']['avg_price'])) *\
                        Decimal(str(self._data_info[trade_id][f'last_rv_{o_side}']['amount']))
        cost_side = Decimal(str(price)) * Decimal(str(amount))

        fees =  cost_side * Decimal(str(self._fees)) + cost_o_side * Decimal(str(self._fees))
        est_profit = float(Decimal(str(STEP_WISE[side])) * (cost_o_side - cost_side) - fees)

        return est_profit

    def _update_data_next_order(self, trade_id, data):
        try:
            side = data[KEY_GET_ORDER_SIDE]
            o_side = self._fetch_revert_side(side)
            meta_data = data.get(KEY_GET_ORDER_META_DATA, {})
            order_history = meta_data.get('order_history', [])
            # append list order history
            data_cp = data.copy()
            del data_cp[KEY_GET_ORDER_META_DATA]
            order_history.append(data_cp)
            # call function cal avg price, amount
            info_avg_order = self._cal_info_order_follow_market(order_history)
            # update avg price
            data[KEY_GET_ORDER_AVERAGE_PRICE] = info_avg_order['avg_price']
            data[KEY_GET_ORDER_FILLED] = info_avg_order['sum_amount']
            self._data_info[trade_id]['open_order'] = data
            # create base_tp_order:
            price = float(Decimal(str(data[KEY_GET_ORDER_AVERAGE_PRICE])) + Decimal(str(STEP_WISE[side])) * Decimal(
                str(self._profit)))
            amount = float(Decimal(str(data[KEY_GET_ORDER_FILLED])) * Decimal(str(self._base_amount)))
            # TODO: check balance
            while not self._terminate and not self._is_enough_balance(o_side, amount, price, self._pair):
                time.sleep(0.2)
            order_info = self.place_order(price, amount, o_side, self._pair, type=LIMIT,
                                          meta_data={'trade_id': trade_id}, callback=self._callback_take_profit_order)
            if order_info:
                self._data_info[trade_id]['base_close_order'] = order_info
                self._take_snapshot()
                self._check_order_change_color(trade_id, side)

        except:
            tb = traceback.format_exc()
            self._log('tool_atr_trailing_stopmom---265ERROR {}'.format(tb), severity='error')

    def _cb_open_position_order(self, data):
        try:
            # assume BUY filled
            if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
                trade_id = data[KEY_GET_ORDER_META_DATA]['trade_id']
                self._log(f'tool_atr_trailing_stopmom---272#{trade_id} order open position filled... {data}')
                atr_trailing_datainserted = sql_insert_atr_trailing_bot(data,trade_id,self._own_name,self._channel,self._ex_id,self._api_name,self._amount,self._price,self._profit,self._base_amount,self._trailing_margin,self._fees)
                self._log(f'tool_buysell_sellbuy_continuouslymom---open position filled data inserted to database{atr_trailing_datainserted}')

                self._take_snapshot()
                self._update_data_next_order(trade_id, data)

            elif ORDER_CANCELED == data[KEY_GET_ORDER_STATUS]:
                trade_id = data[KEY_GET_ORDER_META_DATA]['trade_id']
                self._log('tool_atr_trailing_stopmom---278# order open position cancel {}'.format(data))
                atr_trailing_datainserted = sql_insert_atr_trailing_bot(data,trade_id,self._own_name,self._channel,self._ex_id,self._api_name,self._amount,self._price,self._profit,self._base_amount,self._trailing_margin,self._fees)
                self._log(f'tool_buysell_sellbuy_continuouslymom---open position filled data inserted to database{atr_trailing_datainserted}')
                # When following market, the open position order is partial filled, continue place take-profit order for filled amount
                # payback buy market order or something like that
                price = float(self._fetch_market_price(self._pair))
                amount = Decimal(str(data[KEY_GET_ORDER_AMOUNT]))
                meta_data = data.get(KEY_GET_ORDER_META_DATA, {})
                order_history = meta_data.get('order_history', [])
                # append list order history
                data_cp = data.copy()
                del data_cp[KEY_GET_ORDER_META_DATA]

                if data[KEY_GET_ORDER_FILLED] > 0:
                    self._log(f'tool_atr_trailing_stopmom---290# order open position partial filled {data_cp}')
                    amount = amount - Decimal(str(data[KEY_GET_ORDER_FILLED]))
                if float(amount) > self._fetch_min_amount_cache(self._pair):
                    order_history.append(data_cp)
                    while not self._terminate and self._data_info[trade_id]['is_running']:
                        if self._order_open_position(trade_id, price, data[KEY_GET_ORDER_SIDE], float(amount), order_history=order_history):
                            return
                        time.sleep(0.3)
                else:
                    # amount remaining too small, next
                    self._take_snapshot()
                    self._update_data_next_order(trade_id, data)

        except:
            tb = traceback.format_exc()
            self._log('tool_atr_trailing_stopmom---305ERROR {}'.format(tb), severity='error')

    def _callback_take_profit_order(self, data):
        try:
            # order filled, begin new trade
            if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
                meta_date = data[KEY_GET_ORDER_META_DATA]
                trade_id = meta_date['trade_id']
                self._log(f'tool_atr_trailing_stopmom---313#{trade_id} Order base take profit filled.... {data}')
                new_amount = float(Decimal(str(self._amount)) - Decimal(str(data[KEY_GET_ORDER_FILLED])))
                profit_side = data[KEY_GET_ORDER_SIDE]
                close_position_order = self.place_order(0, new_amount, profit_side, self._pair,
                                                    type=LIMIT, meta_data={'trade_id': trade_id},
                                                    callback=self._cb_close_position,
                                                    trailing_stop_order_info={
                                                        TrailingOrderParams.TRAILING_MARGIN: self._trailing_margin,
                                                        'base_price': float(data[KEY_GET_ORDER_AVERAGE_PRICE]),
                                                        'follow_base_price': True}
                                                    )
                if close_position_order:
                    self._take_snapshot()
                    self._data_info[trade_id]['trailing_order'] = close_position_order

            elif ORDER_CANCELED == data[KEY_GET_ORDER_STATUS]:
                meta_date = data[KEY_GET_ORDER_META_DATA]
                trade_id = meta_date['trade_id']
                self._log(f'tool_atr_trailing_stopmom---331#{trade_id} Order base take profit cancelled.... {data}')
                self._take_snapshot()

                if data[KEY_GET_ORDER_FILLED] >= self._fetch_min_amount_cache(self._pair):
                    take_profit_side = self._fetch_revert_side(data[KEY_GET_ORDER_SIDE])
                    self._log(f'tool_atr_trailing_stopmom---336{trade_id} Place order MARKET for order partial-filled....')
                    self.place_order(None, data[KEY_GET_ORDER_FILLED], take_profit_side, self._pair, type=MARKET)
        except:
            tb = traceback.format_exc()
            self._log('tool_atr_trailing_stopmom---340ERROR {}'.format(tb), severity='error')

    def _cb_close_position(self, data):
        try:
            meta_data = data[KEY_GET_ORDER_META_DATA]
            trade_id = meta_data['trade_id']
            if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
                self._log(f'tool_atr_trailing_stopmom---347#{trade_id} Order close-position(trailing) fulfilled {data}')
                self._data_info[trade_id]['is_running'] = False
                self._take_snapshot()
            elif ORDER_CANCELED == data[KEY_GET_ORDER_STATUS]:
                self._log(f'tool_atr_trailing_stopmom---351#{trade_id} Order close-position(trailing) canceled {data}')
        except Exception as e:
            tb = traceback.format_exc()
            self._log('354ERR {}'.format(tb))

    def _cb_signal_tp_order(self, data):
        try:
            # assume BUY filled
            if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
                trade_id = data[KEY_GET_ORDER_META_DATA]['trade_id']
                self._log(f'tool_atr_trailing_stopmom---361#{trade_id} _cb_signal_tp_order  filled... {data}')
                self._data_info[trade_id]['is_running'] = False
                self._take_snapshot()

            elif ORDER_CANCELED == data[KEY_GET_ORDER_STATUS]:
                trade_id = data[KEY_GET_ORDER_META_DATA]['trade_id']
                self._log('tool_atr_trailing_stopmom---367# _cb_signal_tp_order cancel {}'.format(data))
                # When following market, the open position order is partial filled, continue place take-profit order for filled amount
                # payback buy market order or something like that
                price = float(self._fetch_market_price(self._pair))
                amount = Decimal(str(data[KEY_GET_ORDER_AMOUNT]))
                meta_data = data.get(KEY_GET_ORDER_META_DATA, {})
                order_history = meta_data.get('order_history', [])
                # append list order history
                data_cp = data.copy()
                del data_cp[KEY_GET_ORDER_META_DATA]

                if data[KEY_GET_ORDER_FILLED] > 0:
                    self._log(f'tool_atr_trailing_stopmom---379# _cb_signal_tp_order partial filled {data_cp}')
                    amount = amount - Decimal(str(data[KEY_GET_ORDER_FILLED]))
                if float(amount) > self._fetch_min_amount_cache(self._pair):
                    order_history.append(data_cp)
                    while not self._terminate and self._data_info[trade_id]['is_running']:
                        if self._order_open_position(trade_id, price, data[KEY_GET_ORDER_SIDE], float(amount), order_history=order_history, tp_order=True):
                            return
                        time.sleep(0.3)
        except:
            tb = traceback.format_exc()
            self._log('tool_atr_trailing_stopmom---389 ERROR {}'.format(tb), severity='error')

