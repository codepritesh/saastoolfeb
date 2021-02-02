import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
lib_path = dir_path + '/../libs'
bot_path = dir_path + '/../bots'
sys.path.append(lib_path)
sys.path.append(dir_path)
sys.path.append(bot_path)
from bot_father import *
from bot_constant import *


class SupportOrderFollowMarket(BotFather):
    TIME_SLEEP = 0.1
    ORDER_HISTORY = 'order_history'
    CALLBACK = 'callback'
    DATA = 'data'
    GAP = 'gap'
    IS_QUOTE_AMOUNT = 'is_quote_coin_amount'
    CANCEL_INTERVAL = 'cancel_interval'
    INIT_AMOUNT = 'initial_amount'
    MIN_PROFIT = 'minimal_profit'
    MIN_PRICE = 'minimal_price'
    POST_ONLY = 'postOnly'
    VERBOSE = 'verbose'
    BASE_TP_PRICE = 'base_tp_price'
    CANCEL_INTERVAL_DEFAULT = 1.5 #s
    CANCEL_AFTER_TIME = 30 #s

    def __init__(self, alias):
        super().__init__(alias)

    def msf_place_order_follow_market_helper(self, pair, side, amount, price, callback, meta_data=None, key_exchange=None,
                                             is_quote_coin_amount=False, min_profit={}, base_threshold_price=None, gap=0, follow_gap=0, postOnly=False, verbose=True, base_tp_price=None):
        try:
            # Issues Pass by ref
            # issues:
            #
            # objA: call this func with meta_data = {}, at line 88: when meta_data update, it's will be = {'ori_price': priceA, 'ori_amount': amountA},
            #       and still in-progress
            # objB: also call this func but don't pass meta_data, line 88: also update = {'ori_price': priceB, 'ori_amount': amountB}
            #
            # Now, objA will change meta_data = {'ori_price': priceB, 'ori_amount': amountB} same with objB.
            # Killed by: Handle this value as local variable of obj, then the pass by value/ref won't affect to another obj

            if not meta_data:
                meta_data = {}
            if not price: # price is 0
                if not postOnly:
                    price = float(Decimal(str(self._fetch_market_price(pair, key_exchange=key_exchange))) - Decimal(
                        str(STEP_WISE[side])) * Decimal(str(gap)))
                else:
                    price = float(self._fetch_best_price(pair, side, key_exchange=key_exchange))
            min_price = None
            order_type = LIMIT_MAKER if postOnly else LIMIT
            if is_quote_coin_amount:
                quote_quatity = amount
                amount = float(Decimal(str(amount)) / Decimal(str(price)))
                if min_profit:
                    min_amount = float(Decimal(str(min_profit[self.INIT_AMOUNT])) + Decimal(str(STEP_WISE[side]))*Decimal(str(min_profit[self.MIN_PROFIT])))
                    min_price = float(Decimal(str(quote_quatity)) / Decimal(str(min_amount)))
                    if STEP_WISE[side] * min_amount > STEP_WISE[side] * amount:
                        # calc price for minimal profit
                        amount = min_amount
                        price = min_price
                        verbose and self._log(f'support_order_follow_marketMOM---67Follow-market order reach min profit at begin, only place normal limit order')
                        self.place_order(price, amount, side, pair, type=order_type, callback=callback, key_exchange=key_exchange)
                        return
            elif base_tp_price:
                pass
                # else not is quote
            else:
                if base_threshold_price:
                    # Buy
                    # if stepwise * market price  > stepwise * base_threshold_price
                    if STEP_WISE[side] * price > STEP_WISE[side] * base_threshold_price:
                        # place on base threshold price
                        verbose and self._log(f'support_order_follow_marketMOM---79Follow-market order reach base_threshold_price at begin, only place normal limit order')
                        self.place_order(base_threshold_price, amount, side, pair, type=order_type, callback=callback, key_exchange=key_exchange)
                        return
                    # else
                    else:
                        min_price = base_threshold_price

            if follow_gap == 0:
                follow_gap = gap
            meta_data.update({'ori_price': price, 'ori_amount': amount})
            self.submit_task(self.__msf_retry_place_order, pair, side, amount, price, meta_data, None, callback, key_exchange, is_quote_coin_amount, follow_gap, min_price, postOnly, verbose, base_tp_price)
        except:
            tb = traceback.format_exc()
            self._log(f'support_order_follow_marketMOM---92ERROR {tb}')

    def __msf_retry_place_order(self, pair, side, amount, price, data=None, order_history=None,
                                callback=None, key_exchange=None, is_quote_coin_amount=False, follow_gap=0, min_price=None, postOnly=False, verbose=True, base_tp_price=None):
        try:
            # check enough money
            if min_price and is_quote_coin_amount and STEP_WISE[side] * min_price <= STEP_WISE[side] * price:
                quote_quality = Decimal(str(amount)) * Decimal(str(price))
                price = min_price
                amount = float(quote_quality/Decimal(str(min_price)))
            verbose and self._log(f'support_order_follow_marketMOM---102{self.__class__.__name__} __msf_retry_place_order {pair, side, amount, price}')
            self._mbf_waiting_enough_balance_to_place_order(pair, side, amount, price)
            # enough money
            if not order_history:
                order_history = []
            if data and data.get(self.CANCEL_INTERVAL):
                cancel_interval = data[self.CANCEL_INTERVAL]
            else:
                cancel_interval = self.CANCEL_INTERVAL_DEFAULT
            meta_data = {
                self.ORDER_HISTORY: order_history,
                self.CALLBACK: callback,
                self.DATA: data,
                self.GAP: follow_gap,
                KEY_EXCHANGE: key_exchange,
                self.CANCEL_INTERVAL: cancel_interval,
                self.IS_QUOTE_AMOUNT: is_quote_coin_amount,
                self.MIN_PRICE: min_price,
                self.POST_ONLY: postOnly,
                self.VERBOSE: verbose,
                self.BASE_TP_PRICE: base_tp_price,
            }
            rs = self.__msf_place_follow_market(pair, side, amount, price, meta_data, key_exchange=key_exchange, min_price=min_price, postOnly=postOnly, base_tp_price=base_tp_price)
            if not rs:
                verbose and self._log(f'support_order_follow_marketMOM---126 __msf_retry_place_order Retry place order with args: {pair} {side} {amount} {price} {data} {order_history}')
        except:
            tb = traceback.format_exc()
            self._log(f'support_order_follow_marketMOM---129ERROR {tb}')

    def __msf_place_follow_market(self, pair, side, amount, price, meta_data, key_exchange=None, min_price=None, postOnly=False, base_tp_price=None):
        try:
            gap = meta_data.get(self.GAP)
            order_type = LIMIT_MAKER if postOnly else LIMIT
            order_info = self.place_order(price, amount, side, pair, type=order_type,
                                          meta_data=meta_data, callback=self.__cb_open_position_order,
                                          key_exchange=key_exchange)
            if order_info:
                self._waiting_order_open_position(pair, order_info[KEY_GET_ORDER_ID], gap=gap, cancel_interval=meta_data[self.CANCEL_INTERVAL], min_price=min_price,
                                                  key_exchange=key_exchange, postOnly=postOnly, base_tp_price=base_tp_price)
                return True
            return False
        except:
            tb = traceback.format_exc()
            self._log('support_order_follow_marketMOM---145ERROR {}'.format(tb), severity='error')
            return False

    def _waiting_order_open_position(self, pair, order_id, gap=0, cancel_interval=CANCEL_INTERVAL_DEFAULT,
                                                            max_time_wait=CANCEL_AFTER_TIME, min_price=None, key_exchange=None, postOnly=False, verbose=True, base_tp_price=None):
        try:
            cancel_max_cnt = int(cancel_interval / self.TIME_SLEEP)
            wait_max_cnt = int(max_time_wait / self.TIME_SLEEP)
            count = 0
            while order_id and not self._terminate:
                time.sleep(self.TIME_SLEEP)
                progress = self._fetch_order_progress(order_id, key_exchange=key_exchange)
                if not progress:
                    continue
                side = progress[KEY_GET_ORDER_SIDE]
                price = float(progress[KEY_GET_ORDER_PRICE])
                if progress[KEY_GET_ORDER_STATUS] != ORDER_OPEN:
                    break
                if base_tp_price:
                    current_price = self._fetch_market_price(pair, key_exchange)
                    if Decimal(str(current_price)) * DECIMAL_STEP_WISE[side] >= Decimal(str(base_tp_price)) * \
                            DECIMAL_STEP_WISE[side]:
                        self.update_callback_follow_order_id(order_id, self.__cb_do_something)
                        self._cancel_order_with_retry(order_id, pair, key_exchange=key_exchange)
                        verbose and self._log('support_order_follow_marketMOM---169# cancel {} {} open position order, reach base_price'.format(order_id, progress[KEY_GET_ORDER_SIDE]))
                        return
                count += 1
                if count >= cancel_max_cnt:
                    if float(progress[KEY_GET_ORDER_FILLED]) > 0 and count < wait_max_cnt:  # not fulfilled after 30s -> cancel
                        continue
                    # after ~1.5s, if order open position is not partially filled, should cancel and recheck
                    market_price = self.__cal_price_follow_market(pair, side, gap, key_exchange=None, postOnly=postOnly)
                    if market_price * STEP_WISE[side] > price * STEP_WISE[side]:
                        if min_price and market_price * STEP_WISE[side] >= float(min_price) * STEP_WISE[side]:
                            verbose and self._log('support_order_follow_marketMOM---179# follow market order reach min profit, dont cancel anymore'.format(order_id))
                            break

                        verbose and self._log('support_order_follow_marketMOM---182# cancel {} {} open position order, follow market'.format(order_id,
                                                                        progress[ KEY_GET_ORDER_SIDE]))
                        self._cancel_order_with_retry(order_id, pair,key_exchange=key_exchange)
                        break
        except:
            tb = traceback.format_exc()
            self._log('support_order_follow_marketMOM---188ERROR {}'.format(tb), severity='error')

    def __cb_do_something(self, data):
        try:
            if data[KEY_GET_ORDER_STATUS] in [ORDER_CLOSED, ORDER_CANCELED]:
                self._log(f'support_order_follow_marketMOM---193# Invoke callback do nothing when I like...')
                self.__next_action_when_place_order_success(data)
        except:
            tb = traceback.format_exc()
            self._log('support_order_follow_marketMOM---197ERROR {}'.format(tb), severity='error')

    def __cb_open_position_order(self, data):
        try:
            # assume BUY filled
            meta_data = data.get(KEY_GET_ORDER_META_DATA, {})
            verbose = meta_data.get(self.VERBOSE, True)
            if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
                verbose and self._log(f'support_order_follow_marketMOM---205# {self.__class__.__name__} follow-market order filled... {data}')
                self.__next_action_when_place_order_success(data)
            elif ORDER_CANCELED == data[KEY_GET_ORDER_STATUS]:
                verbose and self._log(f'support_order_follow_marketMOM---208# {self.__class__.__name__} follow-market order {ORDER_CANCELED}... {data}')
                # When following market, the open position order is partial filled, continue place take-profit order for filled amount
                # payback buy market order or something like that
                pair = data[KEY_GET_ORDER_PAIR]
                side = data[KEY_GET_ORDER_SIDE]
                amount = Decimal(str(data[KEY_GET_ORDER_AMOUNT]))
                key_exchange = meta_data.get(KEY_EXCHANGE)
                is_quote_coin_amount = meta_data.get(self.IS_QUOTE_AMOUNT)
                base_tp_price = meta_data.get(self.BASE_TP_PRICE)
                if base_tp_price:
                    current_price = self._fetch_market_price(pair, key_exchange)
                    if Decimal(str(current_price)) * DECIMAL_STEP_WISE[side] >= Decimal(str(base_tp_price)) * \
                            DECIMAL_STEP_WISE[side]:
                        self._log(f'support_order_follow_marketMOM---221# return {data[KEY_GET_ORDER_ID]} open position order, reach base_price={base_tp_price}')
                        self.__next_action_when_place_order_success(data)
                        return
                # price = float(self._fetch_market_price(pair, key_exchange=key_exchange))
                gap = meta_data.get(self.GAP)
                postOnly = meta_data.get(self.POST_ONLY)
                price = self.__cal_price_follow_market(pair, side, gap, key_exchange=None, postOnly=postOnly)
                # parameter save
                order_history = meta_data[self.ORDER_HISTORY]
                callback = meta_data[self.CALLBACK]
                info = meta_data[self.DATA]
                # end parameter save

                # append list order history
                data_cp = data.copy()
                del data_cp[KEY_GET_ORDER_META_DATA]
                # end delete meta_data, only add history order info, excluded meta_data
                amount = self.__calc_quote_coin_amount(data, price)

                if data[KEY_GET_ORDER_FILLED] > 0:
                    verbose and self._log(f'support_order_follow_marketMOM---241# follow-market order partial filled {data_cp}')
                if float(amount) > self._fetch_min_amount_cache(pair):
                    if data[KEY_GET_ORDER_FILLED] > 0:
                        order_history.append(data_cp)
                    while not self._is_enough_balance(side, amount, price, pair):
                        time.sleep(BOT_TIMER.DEFAULT_TIME_SLEEP * 3)
                        price = self.__cal_price_follow_market(pair, side, gap, key_exchange=None, postOnly=postOnly)
                        amount = self.__calc_quote_coin_amount(data, price)
                    verbose and self._log(f'support_order_follow_marketMOM---249#{self.__class__.__name__} call follow market')
                    min_price = meta_data[self.MIN_PRICE]
                    self.__msf_retry_place_order(pair, side, float(amount), price, callback=callback, data=info,
                                                 order_history=order_history, key_exchange=key_exchange,
                                                 is_quote_coin_amount=is_quote_coin_amount, follow_gap=gap, min_price=min_price, postOnly=postOnly, verbose=verbose, base_tp_price=base_tp_price)
                else:
                    # amount remaining too small, next
                    verbose and self._log(f'support_order_follow_marketMOM---256# Invoke callback when min amount')
                    data[KEY_GET_ORDER_STATUS] = ORDER_CLOSED
                    self.__next_action_when_place_order_success(data)
            elif ORDER_EXPIRED == data[KEY_GET_ORDER_STATUS]:
                verbose and self._log(f'support_order_follow_marketMOM---260# {self.__class__.__name__} follow-market order {ORDER_EXPIRED}... {data}')
                pair = data[KEY_GET_ORDER_PAIR]
                side = data[KEY_GET_ORDER_SIDE]
                meta_data = data.get(KEY_GET_ORDER_META_DATA, {})
                key_exchange = meta_data.get(KEY_EXCHANGE)
                is_quote_coin_amount = meta_data.get(self.IS_QUOTE_AMOUNT)
                gap = meta_data.get(self.GAP)
                postOnly = meta_data.get(self.POST_ONLY)
                base_tp_price = meta_data.get(self.BASE_TP_PRICE)
                if base_tp_price:
                    current_price = self._fetch_market_price(pair, key_exchange)
                    if Decimal(str(current_price)) * DECIMAL_STEP_WISE[side] >= Decimal(str(base_tp_price)) * \
                            DECIMAL_STEP_WISE[side]:
                        self._log(f'support_order_follow_marketMOM---273# return {data[KEY_GET_ORDER_ID]} open position order, reach base_price={base_tp_price}')
                        self.__next_action_when_place_order_success(data)
                        return
                price = self.__cal_price_follow_market(pair, side, gap, key_exchange=None, postOnly=postOnly)
                # parameter save
                order_history = meta_data[self.ORDER_HISTORY]
                callback = meta_data[self.CALLBACK]
                info = meta_data[self.DATA]
                amount = self.__calc_quote_coin_amount(data, price)
                while not self._is_enough_balance(side, amount, price, pair):
                    time.sleep(BOT_TIMER.DEFAULT_TIME_SLEEP * 3)
                    price = self.__cal_price_follow_market(pair, side, gap, key_exchange=None,postOnly=postOnly)
                    amount = self.__calc_quote_coin_amount(data, price)
                verbose and self._log(f'support_order_follow_marketMOM---286#{self.__class__.__name__} call follow market')
                min_price = meta_data[self.MIN_PRICE]
                self.__msf_retry_place_order(pair, side, float(amount), price, callback=callback, data=info,
                                             order_history=order_history, key_exchange=key_exchange,
                                             is_quote_coin_amount=is_quote_coin_amount, follow_gap=gap, min_price=min_price, postOnly=postOnly, verbose=verbose, base_tp_price=base_tp_price)
        except:
            tb = traceback.format_exc()
            self._log('support_order_follow_marketMOM---293ERROR {}'.format(tb), severity='error')

    def __next_action_when_place_order_success(self, data):
        try:
            # callback
            meta_data = data.get(KEY_GET_ORDER_META_DATA, {})
            # parameter save
            order_history = meta_data[self.ORDER_HISTORY]
            callback = meta_data[self.CALLBACK]
            info = meta_data[self.DATA]
            # end parameter save
            # append list order history
            data_cp = data.copy()
            del data_cp[KEY_GET_ORDER_META_DATA]
            order_history.append(data_cp)
            # cal avg price, sum amount -> then update in data, order info
            avg_info = self._mbf_cal_avg_info(order_history)
            # begin update data order info
            data.update({
                KEY_GET_ORDER_AVERAGE_PRICE: avg_info['avg_price'],
                KEY_GET_ORDER_PRICE: float(info.get('ori_price', 0)),
                KEY_GET_ORDER_AMOUNT: float(info.get('ori_amount', 0)),
                KEY_GET_ORDER_FILLED: avg_info['sum_amount'],
                # always return status close
                KEY_GET_ORDER_STATUS: data[KEY_GET_ORDER_STATUS]
            })
            # meta_data
            data[KEY_GET_ORDER_META_DATA] = info
            # end update data
            if callback:
                callback(data)
            else:
                self._log(f'support_order_follow_marketMOM---325{self.__class__.__name__} no had callback, data: {data}')
        except:
            tb = traceback.format_exc()
            self._log('support_order_follow_marketMOM---328ERROR {}'.format(tb), severity='error')

    def __cal_price_follow_market(self, pair, side, gap, key_exchange=None, postOnly=False):
        try:
            if not postOnly:
                price = float(Decimal(str(self._fetch_market_price(pair, key_exchange=key_exchange))) - Decimal(str(STEP_WISE[side])) * Decimal(str(gap)))
            else:
                price = float(self._fetch_best_price(pair, side, key_exchange=key_exchange))
            return price
        except:
            tb = traceback.format_exc()
            self._log('support_order_follow_marketMOM---339ERROR {}'.format(tb), severity='error')

    def __calc_quote_coin_amount(self, data, price):
        try:
            meta_data = data.get(KEY_GET_ORDER_META_DATA, {})
            is_quote_coin_amount = meta_data.get(self.IS_QUOTE_AMOUNT)
            if is_quote_coin_amount:
                origin_quote_amount = Decimal(str(data[KEY_GET_ORDER_PRICE])) * Decimal(str(data[KEY_GET_ORDER_AMOUNT]))
                filled_quote_amount = Decimal(str(data[KEY_GET_ORDER_AVERAGE_PRICE])) * Decimal(
                    str(data[KEY_GET_ORDER_FILLED]))
                quote_amount = origin_quote_amount - filled_quote_amount
                amount = float(quote_amount / Decimal(str(price)))
            else:
                amount = float(Decimal(str(data[KEY_GET_ORDER_AMOUNT])) - Decimal(str(data[KEY_GET_ORDER_FILLED])))
            return amount
        except:
            tb = traceback.format_exc()
            self._log('support_order_follow_marketMOM---356ERROR {}'.format(tb), severity='error')



