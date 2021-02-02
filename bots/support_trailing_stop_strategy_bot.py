import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
lib_path = dir_path + '/../libs'
bot_ac_path = dir_path + '/../bot_action'
sys.path.append(lib_path)
sys.path.append(dir_path)
sys.path.append(bot_ac_path)
from bot_father import *
from support_order_follow_market import SupportOrderFollowMarket
from bot_constant import *
from sqldata_insert import *
from pprint import pprint


class SupportTrailingStopBot(SupportOrderFollowMarket, BotFather):

    bot_alias = 'SupportTrailingStopBot'
    entry_side = 'entry_side'
    entry_price = 'entry_price'
    amount = 'amount'
    trailing_margin = 'trailing_margin'
    open_position_order = 'open_position_order'
    trailing_amount = 'trailing_amount'
    finished_amount = 'finished_amount'
    min_profit = 'min_profit'
    gap = 'gap'
    postOnly = 'postOnly'
    cancel_threshold = 'cancel_threshold'

    def __init__(self):
        super().__init__(self.bot_alias)
        self._amount = '0.0'
        self._profit = '0.0'
        self._trade_num = 0

    def bot_entry(self, web_input):
       
        try:
            super().bot_entry(web_input)
            self._base_curr, self._quote_curr = self._pair.split('/')
            if web_input.get('resume'):
                snapshot_data = self.snapshot_db.fetch_data(SupportTrailingStopBot.bot_alias, self._channel)
                if not snapshot_data:
                    self._log(f'support_trailing_stop_strategy_botmom---43Snapshot {self._channel} not found')
                    return
                else:
                    snapshot_data = snapshot_data.get('snapshot_data')
                # Resume running variables
                self._trade_info = snapshot_data.get('_trade_info', {})
                self._cost = snapshot_data.get('_cost')
                if not self._cost:
                    self._cost = 0
                self._order_num = snapshot_data.get('_order_num')
                if not self._order_num:
                    self._order_num = 0
                self._trade_num = snapshot_data.get('_trade_num')
                if not self._trade_num:
                    self._trade_num = 0
                # resume
                # self.start_instance_report()
                self._resume()
            else:
                # Otherwises start new bot
                # self.start_instance_report()
                self._trade_info = {}
                self._trade_num = 0
                self._order_num = 0
                self._cost = 0
        except Exception as e:
            tb = traceback.format_exc()
            self._log(f'support_trailing_stop_strategy_botmom---70ERROR {tb}')
    def _take_snapshot(self, trade_id):
        try:
            if self._trade_info.get(trade_id):
                self._trade_info[trade_id].update({
                    'timestamp': datetime_now()
                })
            snapshot = {'snapshot_data': {
                '_trade_info': self._trade_info,
                '_cost': self._cost,
                '_order_num': self._order_num,
                '_trade_num': self._trade_num,
            }
            }
            self.snapshot_db.update_document(SupportTrailingStopBot.bot_alias, {'_id': self._channel}, snapshot)
        except Exception as e:
            tb = traceback.format_exc()
            self._log('support_trailing_stop_strategy_botmom---88_take_snapshot traceback {}'.format(tb))

    def _resume(self):
        try:
            pass
        except Exception as e:
            tb = traceback.format_exc()
            self._log(f'support_trailing_stop_strategy_botmom---95ERROR {tb}')

    def begin_trading(self, web_input):
        try:
            self._trade_num += 1
            trade_id = str(self._trade_num)
            entry_side = web_input.get('side')
            entry_price = float(web_input.get('entry_price'))
            if entry_price == 0:
                entry_price = float(self._fetch_market_price(self._pair))
            trailing_margin = float(web_input.get('trailing_margin'))
            self._trailing_margin = trailing_margin
            amount = float(web_input.get('amount'))
            min_profit = float(web_input.get('min_profit', 0.1))
            self._min_profit = min_profit
            cancel_threshold = float(web_input.get('cancel_threshold', 1))
            self._cancel_threshold = cancel_threshold
            gap = float(web_input.get('gap', 0))
            self._gap = gap
            postOnly = web_input.get('postOnly', False)
            self._postOnly = postOnly
            follow_gap = float(web_input.get('follow_gap', 0))
            self._follow_gap = follow_gap
            self._entry_price = entry_price
            trade_info = {
                self.entry_side: entry_side,
                self.entry_price: entry_price,
                self.amount: amount,
                self.trailing_margin: trailing_margin,
                self.open_position_order: None,
                self.trailing_amount: 0,
                self.finished_amount: 0,
                self.min_profit: min_profit,
                self.cancel_threshold: cancel_threshold,
                self.gap: gap,
                self.postOnly: postOnly,
            }
            self._trade_info.update({trade_id: trade_info})
            self._log(f'support_trailing_stop_strategy_botmom---126#{trade_id} start trade {trade_info}')
            # Place open-position order
            meta_data = {'trade_id': trade_id}
            self.msf_place_order_follow_market_helper(self._pair, entry_side, amount, entry_price, self._cb_open_position,
                                                      meta_data=meta_data, gap=gap, follow_gap=follow_gap, postOnly=postOnly)
            self._take_snapshot(trade_id)

        except Exception as e:
            tb = traceback.format_exc()
            self._log(f'support_trailing_stop_strategy_botmom---135ERROR {tb}')

    def _cb_open_position(self, data):
        try:
            meta_data = data[KEY_GET_ORDER_META_DATA]
            trade_id = meta_data['trade_id']
            if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
                self._trade_info[trade_id][self.open_position_order] = data
                min_profit = self._trade_info[trade_id][self.min_profit]
                gap = self._trade_info[trade_id][self.gap]
                postOnly = self._trade_info[trade_id][self.postOnly]
                new_amount = float(Decimal(str(data[KEY_GET_ORDER_FILLED])) - \
                                   Decimal(str(self._trade_info[trade_id][self.trailing_amount])))
                if new_amount >= self._fetch_min_amount_cache(self._pair):
                    self._log('support_trailing_stop_strategy_botmom---149#{} order open-position filled {} {}'.format(trade_id, data[KEY_GET_ORDER_FILLED], data))
                    data_inserted = sql_support_trailing_stop_bot(data,trade_id,self._own_name,self._channel,self._ex_id,self._api_name,self._amount,self._pair,self._entry_price,self._trailing_margin,self._cancel_threshold,self._postOnly,self._gap,self._follow_gap,self._min_profit)
                    self._log('support_trailing_stop_strategy_botmom---153-----------------data_inserted149 {}'.format(data_inserted))
                    profit_side = self._fetch_revert_side(data[KEY_GET_ORDER_SIDE])
                    base_price = float(Decimal(str(data[KEY_GET_ORDER_AVERAGE_PRICE])) + \
                                       Decimal(str(STEP_WISE[data[KEY_GET_ORDER_SIDE]])) * Decimal(str(min_profit)))
                    close_position_order = self.place_order(0, new_amount, profit_side, self._pair,
                                                type=LIMIT, meta_data={'trade_id': trade_id}, callback=self._cb_close_position,
                                                trailing_stop_order_info={TrailingOrderParams.TRAILING_MARGIN: self._trade_info[trade_id][self.trailing_margin],
                                                                          'base_price': base_price, 'follow_base_price': True, 'gap': gap, 'postOnly': postOnly}
                                                )
                    if close_position_order:
                        self._log(f'support_trailing_stop_strategy_botmom---159#{trade_id} placed trailing stop {self._trade_info[trade_id][self.trailing_margin]} {close_position_order}')
                        data_inserted = sql_support_trailing_stop_bot(close_position_order,trade_id,self._own_name,self._channel,self._ex_id,self._api_name,self._amount,self._pair,self._entry_price,self._trailing_margin,self._cancel_threshold,self._postOnly,self._gap,self._follow_gap,self._min_profit)
                        self._log('support_trailing_stop_strategy_botmom---165-----------------data_inserted159 {}'.format(data_inserted))
                        self._trade_info[trade_id][self.trailing_amount] = float(Decimal(str(self._trade_info[trade_id][self.trailing_amount])) + \
                                                                                 Decimal(str(new_amount)))

                    if self._trade_info[trade_id][self.trailing_amount] == self._trade_info[trade_id][self.amount]:
                        # Fulfilled
                        self._log('support_trailing_stop_strategy_botmom---165#{} order open-position fulfilled {}'.format(trade_id, data))
                        data_inserted = sql_support_trailing_stop_bot(data,trade_id,self._own_name,self._channel,self._ex_id,self._api_name,self._amount,self._pair,self._entry_price,self._trailing_margin,self._cancel_threshold,self._postOnly,self._gap,self._follow_gap,self._min_profit)
                        self._log('support_trailing_stop_strategy_botmom---173-----------------data_inserted165 {}'.format(data_inserted))
                        self._order_num += 1
                        self._trade_info[trade_id][self.open_position_order] = None
                    # Log cost and order_num
                    self._cost += float(Decimal(str(data[KEY_GET_ORDER_AVERAGE_PRICE])) * Decimal(str(data[KEY_GET_ORDER_FILLED])))
                    self._log(f'support_trailing_stop_strategy_botmom---170#{trade_id} ORDER CLOSED: {self._order_num}, VOLUME: {self._cost}')
                    self.checking_cutloss(trade_id, close_position_order[KEY_GET_ORDER_ID], data[KEY_GET_ORDER_AVERAGE_PRICE], data[KEY_GET_ORDER_SIDE])
                else:
                    self._log('support_trailing_stop_strategy_botmom---173#{} order open-position filled amount to small to place order'.format(trade_id, data))
                    self._trade_info[trade_id][self.open_position_order] = None
            elif ORDER_CANCELED == data[KEY_GET_ORDER_STATUS]:
                # Order canceled
                self._log('support_trailing_stop_strategy_botmom---177#{} order open-position cancel {}'.format(trade_id, data))
                new_amount = float(Decimal(str(data[KEY_GET_ORDER_FILLED])) - Decimal(str(self._trade_info[trade_id][self.trailing_amount])))
                if new_amount >= self._fetch_min_amount_cache(self._pair):
                    min_profit = self._trade_info[trade_id][self.min_profit]
                    gap = self._trade_info[trade_id][self.gap]
                    postOnly = self._trade_info[trade_id][self.postOnly]
                    profit_side = self._fetch_revert_side(data[KEY_GET_ORDER_SIDE])
                    self._cost += float(
                        Decimal(str(data[KEY_GET_ORDER_AVERAGE_PRICE])) * Decimal(str(data[KEY_GET_ORDER_FILLED])))
                    self._log(f'support_trailing_stop_strategy_botmom---186#{trade_id} ORDER CLOSED: {self._order_num}, VOLUME: {self._cost}')
                    base_price = float(Decimal(str(data[KEY_GET_ORDER_AVERAGE_PRICE])) + \
                                       Decimal(str(STEP_WISE[data[KEY_GET_ORDER_SIDE]])) * Decimal(str(min_profit)))
                    close_position_order = self.place_order(0, new_amount, profit_side, self._pair,
                                                            type=LIMIT, meta_data={'trade_id': trade_id},
                                                            callback=self._cb_close_position,
                                                            trailing_stop_order_info={
                                                                TrailingOrderParams.TRAILING_MARGIN: self._trade_info[trade_id][
                                                                    self.trailing_margin],
                                                                'base_price': base_price,
                                                                'follow_base_price': True,
                                                                'gap': gap, 'postOnly': postOnly}
                                                            )
                    if close_position_order:
                        self._log(
                            f'support_trailing_stop_strategy_botmom---201#{trade_id} placed trailing stop {self._trade_info[trade_id][self.trailing_margin]} {close_position_order}')
                        self._trade_info[trade_id][self.trailing_amount] = float(
                            Decimal(str(self._trade_info[trade_id][self.trailing_amount])) + \
                            Decimal(str(new_amount)))
                    # Log cost and order_num
                    self._cost += float(Decimal(str(data[KEY_GET_ORDER_AVERAGE_PRICE])) * Decimal(str(data[KEY_GET_ORDER_FILLED])))
                    self._log(f'support_trailing_stop_strategy_botmom---207#{trade_id} ORDER CLOSED: {self._order_num}, VOLUME: {self._cost}')
                    self.checking_cutloss(trade_id, close_position_order[KEY_GET_ORDER_ID],
                                          data[KEY_GET_ORDER_AVERAGE_PRICE], data[KEY_GET_ORDER_SIDE])

                else:
                    self._log('support_trailing_stop_strategy_botmom---212#{} order open-position filled amount to small to place order'.format(trade_id, data))
                    data_inserted = sql_support_trailing_stop_bot(data,trade_id,self._own_name,self._channel,self._ex_id,self._api_name,self._amount,self._pair,self._entry_price,self._trailing_margin,self._cancel_threshold,self._postOnly,self._gap,self._follow_gap,self._min_profit)
                    self._log('support_trailing_stop_strategy_botmom---222-----------------data_inserted212 {}'.format(data_inserted))
                    self._trade_info[trade_id][self.open_position_order] = None
            # Take snapshot end of cb
            self._take_snapshot(trade_id)
        except Exception as e:
            tb = traceback.format_exc()
            self._log('support_trailing_stop_strategy_botmom---218ERR {}'.format(tb))

    def checking_cutloss(self, trade_id, order_id, open_position_price, open_position_side):
        try:
            info = self._fetch_order_progress(order_id)
            cancel_threshold = self._trade_info[trade_id][self.cancel_threshold]
            while not self._terminate and info.get(KEY_GET_ORDER_STATUS) == ORDER_PENDING:
                cur_price = float(self._fetch_market_price(self._pair))
                if 100 * STEP_WISE[open_position_side] * (open_position_price - cur_price) / cur_price >= cancel_threshold:
                    self._log(f'support_trailing_stop_strategy_botmom---227#{trade_id} {order_id} {open_position_price} reached cancel-threshold, cur_price={cur_price}')
                    self._cancel_order_with_retry(order_id, self._pair)
                time.sleep(BOT_TIMER.DEFAULT_TIME_SLEEP)
                info = self._fetch_order_progress(order_id)
        except:
            tb = traceback.format_exc()
            self._log('support_trailing_stop_strategy_botmom---233 ERROR {}'.format(tb), severity='error')

    def _cb_close_position(self, data):
        try:
            meta_data = data[KEY_GET_ORDER_META_DATA]
            trade_id = meta_data['trade_id']
            if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
                self._log('support_trailing_stop_strategy_botmom---240#{} order close-position fulfilled {}'.format(trade_id, data))
                self._order_num += 1
                self._cost += float(
                    Decimal(str(data[KEY_GET_ORDER_AVERAGE_PRICE])) * Decimal(str(data[KEY_GET_ORDER_FILLED])))
                self._log(f'support_trailing_stop_strategy_botmom---244#{trade_id}  ORDER CLOSED: {self._order_num}, VOLUME: {self._cost}')
                filled_amount = data[KEY_GET_ORDER_FILLED]
                self._trade_info[trade_id][self.finished_amount] = float(Decimal(str(self._trade_info[trade_id][self.finished_amount])) + \
                                                                         Decimal(str(filled_amount)))
                if self._trade_info[trade_id][self.finished_amount] == self._trade_info[trade_id][self.trailing_amount]:
                    self._log(f'support_trailing_stop_strategy_botmom---249#{trade_id} finished {self._trade_info[trade_id][self.finished_amount]}')
            elif ORDER_CANCELED == data[KEY_GET_ORDER_STATUS]:
                self._log('support_trailing_stop_strategy_botmom---251#{} order close-position canceled {}'.format(trade_id, data))
                data_inserted = sql_support_trailing_stop_bot(data,trade_id,self._own_name,self._channel,self._ex_id,self._api_name,self._amount,self._pair,self._entry_price,self._trailing_margin,self._cancel_threshold,self._postOnly,self._gap,self._follow_gap,self._min_profit)
                self._log('support_trailing_stop_strategy_botmom---263-----------------data_inserted251 {}'.format(data_inserted))
            self._take_snapshot(trade_id)
        except Exception as e:
            tb = traceback.format_exc()
            self._log('support_trailing_stop_strategy_botmom---255ERR {}'.format(tb))

