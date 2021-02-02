import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
lib_path = dir_path + '/../libs'
bot_ac_path = dir_path + '/../bot_action'
sys.path.append(lib_path)
sys.path.append(dir_path)
sys.path.append(bot_ac_path)
from bot_father import BotFather
from bot_constant import *
from exchange_lib import *
from sqldata_insert import *
from support_order_follow_market import SupportOrderFollowMarket
from pprint import pprint


class SupportBigAmountBot(SupportOrderFollowMarket, BotFather):

    bot_alias = 'SupportBigAmountBot'

    def __init__(self):
        super().__init__(self.bot_alias)
        self._remain_amount = 0.0
        self._stop_loss = '0.00003'
        self._stop_loss_type = MARKET
        self._profit = '1'
        self._stop_loss_status = False
        self._n_gap = 0.000001
        self._place_profit_order = False
        self._place_stop_order = False

    def bot_entry(self, web_input):
        super().bot_entry(web_input)

    def begin_trading(self, web_input):
        try:
            print('support_big_amount_strategy_botmom---36web input {}'.format(web_input))
            input_price = float(web_input['price'])
            gap = float(web_input['gap'])
            self._gap = gap
            follow_gap = float(web_input['follow_gap'])
            self._place_order_stop_loss = web_input['place_order_stop_loss']
            self._place_order_profit =  web_input['place_order_profit']
            self._follow_gap = follow_gap
            side = web_input['side']
            amount = web_input['amount']
            postOnly = web_input['postOnly']
            self._postOnly = postOnly
            if not input_price:
                self.executor.submit(self.msf_place_order_follow_market_helper, self._pair, side, amount, 0, self._open_position_cb, web_input, None,
                                             False, {}, None, gap, follow_gap, postOnly)
            else:
                self._log(f'support_big_amount_strategy_botmom---47Place limit order {side} {input_price}')
                self.place_order(input_price, amount, side, self._pair, type=LIMIT, meta_data=web_input,
                                 callback=self._open_position_cb)
        except:
            tb = traceback.format_exc()
            self._log('support_big_amount_strategy_botmom---52ERROR {}'.format(tb))
    def _open_position_cb(self, data):
        try:
            if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
                self._log(f'support_big_amount_strategy_botmom---57Open position filled {data}')
                datainserted_support_big_amount = sql_support_big_amount_strategy_bot(data,self._own_name,self._channel,self._ex_id,self._api_name,self._pair,self._stop_loss,self._profit,self._postOnly,self._gap,self._follow_gap,self._place_order_stop_loss,self._place_order_profit)
                self._log('support_big_amount_strategy_botmom---59-----------------data_inserted149 {}'.format(datainserted_support_big_amount))
                meta_data = data[KEY_GET_ORDER_META_DATA]
                place_profit_order = meta_data['place_order_profit']
                place_cutloss_order = meta_data['place_order_stop_loss']
                stop_loss = float(meta_data['stop_loss'])
                profit = float(meta_data['profit'])
                gap = float(meta_data['gap'])
                postOnly = meta_data['postOnly']
                follow_gap = float(meta_data['follow_gap'])

                take_profit_side = self._fetch_revert_side(data[KEY_GET_ORDER_SIDE])
                self._log('support_big_amount_strategy_botmom---68Place_profit_order {}'.format(place_profit_order))
                if place_profit_order:
                    # price profit
                    price_profit_order = float(
                        Decimal(str(data[KEY_GET_ORDER_AVERAGE_PRICE])) - Decimal(str(STEP_WISE[take_profit_side])) * Decimal(str(profit)))
                    order_info = self.place_order(price_profit_order, data[KEY_GET_ORDER_FILLED], take_profit_side, self._pair, type=LIMIT,
                                                  meta_data=None,
                                                  callback=self._callback_take_profit_order)
                    if order_info and order_info[KEY_GET_ORDER_STATUS] == ORDER_OPEN:
                        order_profit_id = order_info[KEY_GET_ORDER_ID]
                        # stop loss
                        if place_cutloss_order:
                            price_stop_loss = float(
                                Decimal(str(data[KEY_GET_ORDER_AVERAGE_PRICE])) + Decimal(str(STEP_WISE[take_profit_side])) * Decimal(str(stop_loss)))
                            # stop loss order
                            self._log('support_big_amount_strategy_botmom---83Begin check stop loss on price {}'.format(price_stop_loss))
                            self._place_stop_loss_order(price_stop_loss, take_profit_side, data[KEY_GET_ORDER_FILLED], order_profit_id, gap, follow_gap, postOnly)
        except:
            tb = traceback.format_exc()
            self._log('support_big_amount_strategy_botmom---87ERROR {}'.format(tb))


    def _place_stop_loss_order(self, price, side, amount, order_profit_id, gap, follow_gap, postOnly):
        # while open position status is open
        if not order_profit_id:
            self._log('support_big_amount_strategy_botmom---93Not order id, return False')
            return False
        # while not self._terminate and self._stop_loss_status:
        while not self._terminate:
            self._interuptable_waiting(BOT_TIMER.DEFAULT_TIME_SLEEP)
            # reach price, cancel order
            market_price = self._fetch_market_price(self._pair)
            profit_order_info = self._fetch_order_progress(order_profit_id)
            if not profit_order_info:
                continue

            if profit_order_info[KEY_GET_ORDER_STATUS] == ORDER_CLOSED:
                break
            elif STEP_WISE[side] * float(market_price) >= STEP_WISE[side] * price \
                    and profit_order_info[KEY_GET_ORDER_STATUS] == ORDER_OPEN:
                self._cancel_order_with_retry(order_profit_id, self._pair)
                # create stop loss
                profit_order_info = self._fetch_order_progress(order_profit_id)
                cutloss_amount = float(Decimal(str(amount)) -Decimal(str(profit_order_info[KEY_GET_ORDER_FILLED])))
                self._log('Place stop loss order {}__{}__{}'.format(side, side, cutloss_amount))
                self._log('support_big_amount_strategy_botmom---117-----------------data fetched {}'.format(profit_order_info))

                #here you can insert if youget data from self_log-- cutlessamount and profit_order_info 
                self.msf_place_order_follow_market_helper(self._pair, side, cutloss_amount, 0, self._callback_stop_loss_order, gap=gap,
                                                          follow_gap=follow_gap, postOnly=postOnly)
                break
        self._log('support_big_amount_strategy_botmom---116End wait create order stop loss for order side {}'.format(side))

    """
    cb when take profit order filled
    """
    def _callback_take_profit_order(self, data):
        # order filled, begin new trade
        if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
            self._log('support_big_amount_strategy_botmom---124Order take profit filled... {}'.format(data))
            datainserted_support_big_amount = sql_support_big_amount_strategy_bot(data,self._own_name,self._channel,self._ex_id,self._api_name,self._pair,self._stop_loss,self._profit,self._postOnly,self._gap,self._follow_gap,self._place_order_stop_loss,self._place_order_profit)
            self._log('support_big_amount_strategy_botmom---59-----------------data_inserted149 {}'.format(datainserted_support_big_amount))
        elif ORDER_CANCELED == data[KEY_GET_ORDER_STATUS]:
            self._log(' support_big_amount_strategy_botmom---126Order cancel {}'.format(data))
            datainserted_support_big_amount = sql_support_big_amount_strategy_bot(data,self._own_name,self._channel,self._ex_id,self._api_name,self._pair,self._stop_loss,self._profit,self._postOnly,self._gap,self._follow_gap,self._place_order_stop_loss,self._place_order_profit)
            self._log('support_big_amount_strategy_botmom---59-----------------data_inserted149 {}'.format(datainserted_support_big_amount))

    """
        cb when stop loss filled
    """
    def _callback_stop_loss_order(self, data):
        # order filled, begin new trade
        if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
            self._log('support_big_amount_strategy_botmom---134Order stop loss filled... {}. Begin new trade'.format(data))
            datainserted_support_big_amount = sql_support_big_amount_strategy_bot(data,self._own_name,self._channel,self._ex_id,self._api_name,self._pair,self._stop_loss,self._profit,self._postOnly,self._gap,self._follow_gap,self._place_order_stop_loss,self._place_order_profit)
            self._log('support_big_amount_strategy_botmom---59-----------------data_inserted149 {}'.format(datainserted_support_big_amount))
        elif ORDER_CANCELED == data[KEY_GET_ORDER_STATUS]:
            self._log('support_big_amount_strategy_botmom---136 Order stop loss cancel {}'.format(data))
            datainserted_support_big_amount = sql_support_big_amount_strategy_bot(data,self._own_name,self._channel,self._ex_id,self._api_name,self._pair,self._stop_loss,self._profit,self._postOnly,self._gap,self._follow_gap,self._place_order_stop_loss,self._place_order_profit)
            self._log('support_big_amount_strategy_botmom---59-----------------data_inserted149 {}'.format(datainserted_support_big_amount))


