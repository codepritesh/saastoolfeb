import sys
import os
import logging
import socket
import telegram
from time import tzset
from logging.handlers import RotatingFileHandler
from concurrent.futures.thread import ThreadPoolExecutor
from ccxt.base.decimal_to_precision import decimal_to_precision, \
                                           TRUNCATE, ROUND_UP, \
                                           DECIMAL_PLACES

# Import our own packages
dir_path = os.path.dirname(os.path.realpath(__file__))
lib_path = dir_path + '/../libs'
rest_path = lib_path + '/rest_api'
bot_action_path = dir_path + '/../bot_action'
repository_path = dir_path + '/../repositories'
sys.path.append(lib_path)
sys.path.append(rest_path)
sys.path.append(bot_action_path)
sys.path.append(repository_path)
from bot_constant import *
from exchange_lib import *
from common import log,socket_emit, \
                   log2, socket_emit2, \
                   WEB_FLASK, WEB_DJANGO, \
                   DelayedRepeatTimer, \
                   RepeatTimer, datetime_now, datetime_now_raw, str_to_date, \
                   DATETIME_FMT, DEFAULT_TZ
from binance_wsclient.binancef_wsclient import BinanceF
from libdb import *
from exception_decor import exception_logging
from channels.layers import get_channel_layer
from sqldata_insert import *


class BotFather:
    # default web/logs for legacy flask
    LOG_BASEPATH = dir_path + '/../web/logs/'
    CSV_BASEPATH = dir_path + '/../web/reports/'
    
    def __init__(self, alias):
        # name of bot
        self.alias = alias
        # bot name will be collection name
        self.DB_RP_COLL = alias
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        self.task_list = []
        # attribute must have
        self._pair_mix_type = None
        self._pair = None
        self._pair_list = []
        self.ex_instance = None
        self._own_name = None
        self._api_name = None
        # stop scanning and terminate
        self._terminate = False
        self._stop_scanning = False
        # web version
        self._channel = None
        # define a log&socket_emit callback
        self._log = None
        self._socket_emit = None
        # if one pair, list have one
        # if pair not register, fetch new min amount
        # save to dict to reduce call api fetch min amount
        self._min_amount_dict = {}
        # report object
        self._report = None
        self._db = None
        self._balance_check_timer = None
        # Timer clean ws data
        self._clean_ws_data_timer = None
        self._influx_pnl_timer = None
        self._ws_check_timer = None
        self._start_time = datetime_now()
        self._log_csv_filename = '{}_'.format(self.alias) + self._start_time
        self._instance_id = self._start_time
        # bookkeeper thread loop
        self._bookkeeper_thread_observer = {}
        # dict save precision of pairs
        self._price_precision_dict = {}
        self.lock = Lock()
        # list object exchange
        self.ex_instances = {}
        self.best_price_only = True
        # default target_coin is USDT
        self._target_coin = "USDT"
        self._ws_data_check = {
                    WS_DATA.ORDER_BOOK: {}
                }
        self.finish_pnl = False
        self.pnl_info = {}
        self.start_time = None
        

    def delete_done_task(self):
        try:
            # delete finished task
            for task_name, task in self.task_list.copy():
                if task.done():
                    self.task_list.remove((task_name, task))
                    del task
        except:
            tb = traceback.format_exc()
            self._log(f'bot_fathermom---105WARN: delete_done_task \n {tb}')

    def submit_task(self, * args):
        self.delete_done_task()
        # self._log(f'task_list len: {len(self.task_list)}')
        f = self.executor.submit(* args)
        task_info = [args[0].__name__]
        # Get order id for subscribe-order task
        if len(args) > 1:
            task_info.append(args[1])
        self.task_list.append((task_info, f))

    def get_task_list(self):
        return str(self.task_list)

    def clear_task_list(self):
        self.task_list = []

    def __config_logger(self, file_path):
        # Reset TZ to 'Asia/Ho_Chi_Minh'
        os.environ['TZ'] = DEFAULT_TZ
        tzset()

        if self._channel:
            self._logger = logging.getLogger(self._channel)
        else:
            self._logger = logging.getLogger(self.alias)

        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False
        # create file handler which logs event debug messages
        #fh = logging.FileHandler(file_path)
        fh = RotatingFileHandler(file_path, mode='a', maxBytes=LoggerConfig.LOG_MAX_SIZE, backupCount=LoggerConfig.LOG_MAX_FILE)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self._logger.addHandler(fh)

    def _setup_log_socket_emit(self):
        """
        Support only django
        """
        # config log
        if self._channel:
            self._log_csv_filename = '{}_'.format(self.alias) + self._channel
        self.LOG_BASEPATH = dir_path + '/../django/logs/'
        self.CSV_BASEPATH = dir_path + '/../django/reports/'
        file_path = self.LOG_BASEPATH + self._log_csv_filename + '.log'
        self.__config_logger(file_path)
        self._channel_layer = get_channel_layer()
        return self._log_new, self._socket_emit_new

    # For Django
    @exception_logging
    def _log_new(self, data, severity='info'):
        log2(data, self._logger, self._channel_layer, self._channel, Chanel.LOG, severity=severity)

    @exception_logging
    def _socket_emit_new(self, data, channel_mux,):
        socket_emit2(data, self._channel_layer, self._channel, channel_mux,self._own_name)

    def _wait_order_until_enough(self, params, key_exchange=None):
        try:
            count_time = 0
            except_orders = 0
            ex_instance = self.get_ex_instance(key_exchange)
            ex_name = ex_instance.get_exchange_name()
            while not self._terminate:
                max_orders = ex_instance.fetch_number_of_opening_orders()
                if ex_name in [EXCHANGE.KRAKEN, EXCHANGE.HITBTC]:
                    except_orders = MAX_ORDER_KRA
                elif ex_name == EXCHANGE.BINANCE:
                    except_orders = MAX_ORDER_BIN
                # check
                if max_orders < except_orders:
                    return True
                elif count_time == 0 or count_time >= 3:  # 30s
                    self._log(f'bot_fathermom---182## {ex_instance.get_exchange_id()} ORDER REACH MAX_ORDER ON EXCHANGE!!!.....')
                    # if open-position order for zelda return
                    if params and params.get(PlaceOrderParams.IS_NOT_WAITING_ORDER):
                        return False
                    count_time = 1
                self._interuptable_waiting(10)
                count_time += 1
        except:
            tb = traceback.format_exc()
            self._log(f'bot_fathermom---191WARN: _wait_order_until_enough \n {tb}')

    def place_order(self, price, amount, side, pair, type=LIMIT, behavior_order_stop_loss='no', params={}, meta_data={},
                    callback=None, trailing_stop_order_info=None, key_exchange=None):
        # check is reach MAX order in account
        if not self._wait_order_until_enough(params, key_exchange=key_exchange):
            return
        # Decimal price
        if price:
            if not isinstance(price, Decimal):
                price = Decimal(str(price))
            # round up or down price
            price_round = self._round_price_helper(price, side, pair)
        else:
            price_round = None
        if params is None:
            params = {}
        if trailing_stop_order_info:
            """
            trailing_stop_order_info = {'trailing_margin', profit_threshold}                    
            """
            return self.__place_trailing_stop_order(amount, side, pair, type, params, callback, meta_data,
                                             trailing_stop_order_info, key_exchange)
        if 'no' == behavior_order_stop_loss:
            return self.__place_order_normal(price_round, amount, side, pair, type, params, callback, meta_data=meta_data,
                                             key_exchange=key_exchange)
        if ORDER_STOP_LOSS == behavior_order_stop_loss:
            return self.__place_order_stop_loss(price_round, amount, side, pair, type, params, callback, meta_data=meta_data)
        return None

    def __place_trailing_stop_order(self, amount, side, pair, type, params, callback, meta_data,
                                    trailing_stop_order_info, key_exchange=None):
        """
        Place trailing stop order
        """
        ex_instance = self.get_ex_instance(key_exchange)
        if not trailing_stop_order_info:
            raise Exception('trailing_stop_order_info must not None')
        if TrailingOrderParams.TRAILING_MARGIN not in trailing_stop_order_info.keys():
            raise Exception('TRAILING_MARGIN must had value')
        follow_base_price = trailing_stop_order_info.get(TrailingOrderParams.FOLLOW_BASE_PRICE, False)
        gap = trailing_stop_order_info.get(TrailingOrderParams.GAP, 0)
        postOnly = trailing_stop_order_info.get(TrailingOrderParams.POST_ONLY, False)
        order_id = ex_instance.create_trailing_stop_order(pair, type, side, amount,
                                                          trailing_stop_order_info[TrailingOrderParams.TRAILING_MARGIN],
                                                          trailing_stop_order_info[TrailingOrderParams.BASE_PRICE],
                                                          self._fetch_min_amount_cache(pair),
                                                          follow_base_price=follow_base_price,
                                                          gap=gap, post_only=postOnly)
        trailing_stop_order_info_cp = trailing_stop_order_info.copy()
        trailing_stop_order_info.update({
            KEY_GET_ORDER_ID: order_id
        })
        # self.update_callback_follow_order_id(order_id, callback)
        self._bookkeeper_thread_observer.update({
            order_id: {
                PlaceOrderParams.CALLBACK: callback,
                KEY_GET_ORDER_META_DATA: meta_data
            }
        })
        self.submit_task(self.subscribe_order_status, order_id, side, params, callback, meta_data,
                         trailing_stop_order_info_cp, key_exchange)
        data_order = {
            KEY_GET_ORDER_ID: order_id,
            KEY_GET_ORDER_PAIR: pair,
            KEY_GET_ORDER_AMOUNT: amount,
            KEY_GET_ORDER_SIDE: side,
            KEY_GET_ORDER_PRICE: trailing_stop_order_info[TrailingOrderParams.BASE_PRICE],
            KEY_GET_ORDER_STATUS: ORDER_PENDING,
            KEY_GET_ORDER_FILLED: 0.0,
            KEY_GET_ORDER_AVERAGE_PRICE: 0.0,
            FEES: 0.0,
            KEY_GET_ORDER_META_DATA: meta_data,
            TrailingOrderParams.TRAILING_MARGIN: trailing_stop_order_info_cp
        }
        order_info = data_order.copy()
        order_info.update({KEY_GET_ORDER_STATUS: ORDER_OPEN})
        return data_order

    def place_stop_loss_order_helper(self, price, amount, side, pair, type,
                                     cb_when_order_open=None, order_profit_id=None, meta_data={}, callback=None):
        params = {
            CB_WHEN_STOP_LOSS_ORDER_OPEN: cb_when_order_open,
            PARAMS_PROFIT_ORDER_ID: order_profit_id
        }
        stop_loss_order_info = self.place_order(price, amount, side, pair,
                                                type=type, behavior_order_stop_loss=ORDER_STOP_LOSS, params=params,
                                                meta_data=meta_data, callback=callback)
        if not stop_loss_order_info:
            self._log('bot_fathermom---280ERROR create stop loss order origin fail, please check log to fix')
        else:
            self.update_callback_follow_order_id(stop_loss_order_info[KEY_GET_ORDER_ID], callback)
        return stop_loss_order_info

    @exception_logging
    def __place_order_normal(self, price, amount, side, pair, type, params, callback, meta_data={}, key_exchange=None):
        ex_instance = self.get_ex_instance(key_exchange)
        order_id = ex_instance.create_order(pair, type, side, amount, price)
        if order_id == ErrorConstant.RESTAPI_INVALID_CMD or order_id == ErrorConstant.RESTAPI_RATE_LIMIT:
            self._log(f'bot_fathermom---290{self.alias} create order {order_id}')
            return None
        elif order_id == ErrorConstant.RESTAPI_POSTONLY_ORDER_FAILED:
            # Invoke cb right away with status as expired
            data = {
                KEY_GET_ORDER_ID: 0,
                KEY_GET_ORDER_STATUS: ORDER_EXPIRED,
                KEY_GET_ORDER_PAIR: pair,
                KEY_GET_ORDER_FILLED: 0,
                KEY_GET_ORDER_AVERAGE_PRICE: 0,
                KEY_GET_ORDER_SIDE: side,
                KEY_GET_ORDER_AMOUNT: amount,
                KEY_GET_ORDER_PRICE: price,
                KEY_GET_ORDER_META_DATA: meta_data,
            }
            if callback:
                self.submit_task(callback, data)
            return data
        # self.update_callback_follow_order_id(order_id, callback)
        self._bookkeeper_thread_observer.update({
            order_id: {
                PlaceOrderParams.CALLBACK: callback,
                KEY_GET_ORDER_META_DATA: meta_data,
                KEY_GET_PARAMS: params}})
        self.submit_task(self.subscribe_order_status, order_id, side, params, callback, meta_data, None, key_exchange)
        order_info = self._fetch_order_progress(order_id, key_exchange)
        if order_info:
            order_info.update({KEY_GET_ORDER_META_DATA: meta_data})
        return order_info

    @exception_logging
    def update_callback_follow_order_id(self, order_id, callback):
        """
        change callback
        :param order_id:
        :param callback:
        :return:
        """
        if self._bookkeeper_thread_observer.get(order_id):
            self._bookkeeper_thread_observer[order_id].update({
                PlaceOrderParams.CALLBACK: callback
            })
            return True
        else:
            self._log(f'bot_fathermom---334Update callback, order not found {order_id}')
            return False

    def __place_order_stop_loss(self, price, amount, side, pair, type, params,
                                callback, meta_data={}, key_exchange=None):
        """
        Place order stop loss
        """
        ex_instance = self.get_ex_instance(key_exchange)
        self._log(f'bot_fathermom---343Create stop loss order with params {params}, '
                  f'bot_fathermom---344amount {amount}, side {side}, pair {pair}, type {type}, meta_data {meta_data}')
        profit_order_id = params[PARAMS_PROFIT_ORDER_ID]
        stop_loss_type = 'own_stoploss_{}'.format(type)
        self._log(f'bot_fathermom---347{self.alias}. Place order: '
                  f'{pair}__{side}__{price}__{amount}__{type}__profit_order_id_{profit_order_id}')
        stop_loss_order_id = ex_instance.create_order(pair, stop_loss_type, side, amount, price,
                                                      params={'stopPrice': price,
                                                              'profit-order-id': profit_order_id,
                                                              'bot_type': self.alias})
        if not stop_loss_order_id:
            self._log(f'bot_fathermom---354Create stop loss order is fail with params {params}, amount {amount}, side {side}, '
                      f'bot_fathermom---355pair {pair}, type {type}, meta_data {meta_data}')
            return False
        # Thread(target=self.__subscribe_stop_loss_order_is_open,
        #        args=(stop_loss_order_id, price, amount, side, params, callback, meta_data)).start()
        self.update_callback_follow_order_id(stop_loss_order_id, callback)
        self.submit_task(self.subscribe_order_status, stop_loss_order_id, price, amount, side, params, callback, meta_data)
        # two order, profit and stop loss order
        data_order = {
            KEY_GET_ORDER_ID: stop_loss_order_id,
            STOP_LOSS_ORDER_ID: stop_loss_order_id,
            KEY_GET_ORDER_AMOUNT: amount,
            KEY_GET_ORDER_SIDE: side,
            KEY_GET_ORDER_PRICE: price,
            KEY_GET_ORDER_STATUS: ORDER_PENDING,
            KEY_GET_ORDER_FILLED: 0.0,
            KEY_GET_ORDER_AVERAGE_PRICE: 0.0,
            FEES: 0.0,
            KEY_GET_ORDER_META_DATA: meta_data
        }
        return data_order

    def __subscribe_stop_loss_order_is_open(self, stop_loss_order_id, price, amount, side, params, callback, meta_data,
                                            key_exchange=None):
        """
        Callback when stop loss order has status open
        """
        ex_instance = self.get_ex_instance(key_exchange)
        if not ex_instance.fetch_order_progress(stop_loss_order_id):
            self._log('bot_fathermom---383Not fetch data stop loss, return true')
            return False
        while ORDER_PENDING == ex_instance.fetch_order_progress(stop_loss_order_id):
            time.sleep(BOT_TIMER.DEFAULT_TIME_SLEEP)
        callback_when_top_loss_order_open = params[CB_WHEN_STOP_LOSS_ORDER_OPEN]
        if ORDER_OPEN == ex_instance.fetch_order_progress(stop_loss_order_id) and callback_when_top_loss_order_open:
            data_order = {
                KEY_GET_ORDER_ID: None,
                STOP_LOSS_ORDER_ID: stop_loss_order_id,
                KEY_GET_ORDER_AMOUNT: amount,
                KEY_GET_ORDER_SIDE: side,
                KEY_GET_ORDER_PRICE: price,
                KEY_GET_ORDER_STATUS: ORDER_OPEN,
                KEY_GET_ORDER_FILLED: 0.0,
                KEY_GET_ORDER_AVERAGE_PRICE: 0.0,
                FEES: 0.0,
                KEY_GET_ORDER_META_DATA: meta_data
            }
            callback_when_top_loss_order_open(data_order)
        # invoke subscribe order
        self.subscribe_order_status(stop_loss_order_id, side, params, callback,
                                    meta_data=meta_data, key_exchange=key_exchange)

    def cleanup_order_data(self, order_id):
        #TODO update to deal with multi-exchange
        self.ex_instance.remove_order_ws_data(order_id, force_remove=True)
        # For sure, in case order still not closed/canceled
        if self._bookkeeper_thread_observer.get(order_id):
            del self._bookkeeper_thread_observer[order_id]
        self._log(f'bot_fathermom---412bot_father: cleanup order {order_id} data')

    # fetch best price
    def _fetch_best_price(self, pair, side='', index=1, key_exchange=None):
        ex_instance = self.get_ex_instance(key_exchange)
        ask_info, bid_info = ex_instance.fetch_order_book(pair, index)
        while not self._terminate:
            ask_info, bid_info = ex_instance.fetch_order_book(pair, index)
            if ask_info and bid_info and ask_info[0] and bid_info[0]:
                break
            self._interuptable_waiting(BOT_TIMER.DEFAULT_TIME_SLEEP)
        ask = float(ask_info[0])
        bid = float(bid_info[0])
        if not side:
            return ask, bid
        return ask if side == SELL else bid

    def _interuptable_waiting(self, waiting_time):
        if waiting_time > 3:
            while not self._terminate and waiting_time > 0:
                time.sleep(1)
                waiting_time -= 1
        else:
            time.sleep(waiting_time)

    # callback when order is close or canceled
    def subscribe_order_status(self, order_id, side, params, callback, meta_data={},
                               trailing_order_info=None, key_exchange=None):
        try:
            self._log(f'bot_fathermom---441subscribe_order_status {key_exchange} {order_id}')
            ex_instance = self.get_ex_instance(key_exchange)
            callback_from_bookkeeper = self._bookkeeper_thread_observer.get(order_id, {}).get(PlaceOrderParams.CALLBACK) \
                if self._bookkeeper_thread_observer.get(order_id, {}).get(PlaceOrderParams.CALLBACK) else callback
            if not callback_from_bookkeeper:
                self._log('bot_fathermom---446Callback not define, return False')
                return False
            cb_event_when_order_open = True if trailing_order_info else False
            amount_filled = 0
            while not self._terminate:
                while not ex_instance.fetch_order_progress(order_id) and not self._terminate:
                    self._log(f'bot_fathermom---452wait for data of order id {order_id}')
                    self._interuptable_waiting(BOT_TIMER.DEFAULT_TIME_SLEEP)
                # Runtime changing cb
                callback_from_bookkeeper = self._bookkeeper_thread_observer.get(order_id, {}).get(PlaceOrderParams.CALLBACK) \
                    if self._bookkeeper_thread_observer.get(order_id, {}).get(PlaceOrderParams.CALLBACK) else callback
                progress = ex_instance.fetch_order_progress(order_id)
                data = {
                    KEY_GET_ORDER_ID: order_id,  # str
                    KEY_GET_ORDER_STATUS: progress[WS_ORDER_PROGRESS.STATUS],  # str
                    KEY_GET_ORDER_PAIR: progress[WS_ORDER_PROGRESS.PAIR],  # pair
                    KEY_GET_ORDER_FILLED: progress[WS_ORDER_PROGRESS.FILLED],  # float
                    KEY_GET_ORDER_AVERAGE_PRICE: progress[WS_ORDER_PROGRESS.AVG_PRICE] if progress[WS_ORDER_PROGRESS.AVG_PRICE] else progress[WS_ORDER_PROGRESS.PRICE],  # float
                    KEY_GET_ORDER_SIDE: progress[WS_ORDER_PROGRESS.SIDE],  # str
                    KEY_GET_ORDER_AMOUNT: progress[WS_ORDER_PROGRESS.AMOUNT],  # float
                    KEY_GET_PARAMS: params,
                    KEY_GET_ORDER_PRICE: progress[WS_ORDER_PROGRESS.PRICE],  # float
                    KEY_GET_ORDER_META_DATA: meta_data,
                    TrailingOrderParams.TRAILING_MARGIN: trailing_order_info
                }
                if data[KEY_GET_ORDER_STATUS] in [ORDER_EXPIRED, ORDER_CANCELED, ORDER_CLOSED]:
                    if callback_from_bookkeeper:
                        callback_from_bookkeeper(data)
                    else:
                        self._log('bot_fathermom---475while order status but callback None')
                    # delete when order close or canceled
                    if self._bookkeeper_thread_observer.get(order_id):
                        del self._bookkeeper_thread_observer[order_id]
                    # update time for ws_data
                    ex_instance.append_update_time_ws_data(order_id)
                    # log order history
                    return True
                elif float(data[KEY_GET_ORDER_FILLED]) > amount_filled:
                    amount_filled = data[KEY_GET_ORDER_FILLED]
                    if callback_from_bookkeeper:
                        callback_from_bookkeeper(data)
                    else:
                        self._log('bot_fathermom---488while order status but callback None')
                elif cb_event_when_order_open and ORDER_OPEN == data[KEY_GET_ORDER_STATUS]:
                    cb_event_when_order_open = False
                    if callback_from_bookkeeper:
                        callback_from_bookkeeper(data)
                    else:
                        self._log('bot_fathermom---494while order status but callback None')
                self._interuptable_waiting(BOT_TIMER.DEFAULT_TIME_SLEEP)
            # end while
        except:
            tb = traceback.format_exc()
            print(f'WARN subscribe_order_status {order_id} {tb}')

    def stop_scanning(self):
        """
        External usage method
        """
        self._stop_scanning = True
        self._log(f'bot_fathermom---506BOT {self.alias} STOP SCANNING^^')

    def terminate(self, key_exchange=None):
        """
        External usage method
        """
        self._terminate = True
        self.stop_clean_ws_data()
        self._stop_ws_connection_check()
        self._log(f'bot_fathermom---515BOT {self.alias} TERMINATE ^^')

        if self.ex_instances:
            for ex_instance in self.ex_instances.values():
                self._log(f'bot_fathermom---519Balance STOP {ex_instance.fetch_balance()}')
                # close websocket
                ex_instance.unsubscribe_ws()
                # close all thread of bot
                ex_instance.terminated = True

    def _update_profit(self, balance_account, order, attr_vol, price):
        """
        Update profit
        """
        if BUY == order[KEY_GET_ORDER_SIDE]:
            value_transaction = float(order[attr_vol]) * price
            balance_account['sum_buy'] += value_transaction
        else:
            value_transaction = float(order[attr_vol]) * price
            balance_account['sum_sell'] += value_transaction
        # fees
        balance_account['sum_fees'] += balance_account['fees'] * value_transaction
        return balance_account

    def tracking_time_out(self, time_str):
        """
        Tracking time out
        """
        self._log(f'bot_fathermom---543Bot tracking time out {time_str}')
        h, m, s = time_str.split(':')
        timer = int(h) * 3600 + int(m) * 60 + int(s)
        while not self._terminate and not self._stop_scanning and timer >= 0:
            timer -= 1
            time.sleep(1)
        if not self._stop_scanning:
            self._log(f'bot_fathermom---550BOT {self.alias} STOP IS REACH TIMER {time_str} ^^')
            self._stop_scanning = True
            self._process_balance_back()

    def _process_balance_back(self):
        pass


    def stop_clean_ws_data(self):
        if self._clean_ws_data_timer:
            self._clean_ws_data_timer.cancel()
            self._log('bot_fathermom---561Stop clean ws data timer')

    def _start_clean_ws_data(self):
        # Trigger a repeat timer. It will take balance snapshot every 30min
        self._clean_ws_data_timer = RepeatTimer(BOT_TIMER.CLEAN_WS_DATA_INTERVAL_BF, self._clean_ws_data)
        self._clean_ws_data_timer.setDaemon(True)
        self._clean_ws_data_timer.start()

    def _clean_ws_data(self):
        self._log('bot_fathermom---570# BOT FATHER: Clean ws_data is begin')
        self._init_min_amount()
        for exchange_obj in self.ex_instances.values():
            exchange_obj.clear_order_ws_when_not_using()

    def _start_ws_connection_check(self):
        if self._ws_check_timer:
            return
        self._log(f'bot_fathermom---578Start ws_connection checking for order_book, interval={BOT_TIMER.WS_CHECK_INTERVAL}s')
        self._order_book_ws_check()
        self._ws_check_timer = RepeatTimer(BOT_TIMER.WS_CHECK_INTERVAL, self._order_book_ws_check)
        self._ws_check_timer.setDaemon(True)
        self._ws_check_timer.start()

    def _stop_ws_connection_check(self):
        if self._ws_check_timer:
            self._ws_check_timer.cancel()

    def _order_book_ws_check(self):
        def order_book_checker(pair):
            order_book_ws = self._ws_data_check[WS_DATA.ORDER_BOOK]
            for ex_key, ex in self.ex_instances.items():
                book_key = '_'.join([ex_key, pair])
                asks, bids = ex.fetch_order_book(pair, 1)
                if book_key not in order_book_ws:
                    order_book_ws[book_key] = {}
                    order_book_ws[book_key]['asks'] = asks
                    order_book_ws[book_key]['bids'] = bids
                    continue
                if order_book_ws[book_key]['asks'] == asks and \
                   order_book_ws[book_key]['bids'] == bids:
                    self._log(f'bot_fathermom---601Order book {book_key} is not updated after {BOT_TIMER.WS_CHECK_INTERVAL}s!! '
                              f'{asks} {bids}. Restart order_book!', severity='warning')
                    ex.register_order_book(pair, self.best_price_only, refresh=True)
                    self._interuptable_waiting(1)
                    asks, bids = ex.fetch_order_book(pair, 1)
                order_book_ws[book_key]['asks'] = asks
                order_book_ws[book_key]['bids'] = bids
        # END def checker(pair)
        for pair in self._pair_list:
            order_book_checker(pair)

    def bot_entry(self, web_input):
        #print("init------------------------------------------------------------615---webinput")
        try:
            self._pair_mix_type = web_input.get('pair')
            if isinstance(self._pair_mix_type, str):
                self._pair = self._pair_mix_type
                self._pair_list = [self._pair]
            else:
                self._pair_list = self._pair_mix_type
                # Avoid duplicate pairs
                self._pair_list = list(set(self._pair_list))

            # Initialize insufficient status for buy/sell of all pair

            self._framework = web_input.get('framework', WEB_DJANGO)
            self._socketio = web_input.get('socket')
            self._channel = web_input.get('uuid')
            self._own_name = web_input.get('own_name')
            self._api_name = web_input.get('api_name')
            self._amount= web_input.get('amount')


            self._log, self._socket_emit = self._setup_log_socket_emit()

            # Initialize exchange

            # for get list
            # {dev_api1: Object}
            list_ex = web_input.get('list_ex')
            if not list_ex:
                list_ex = self.define_list_ex(web_input)
            for item in list_ex:
                """
                [{'ex_id': BIN, 'api_name': api_name}, {'ex_id': BIN, 'api_name': api_name}]
                """
                kwargs = {AggregateExchange.FILE_LOGGER_KW: self._logger}
                ex_id = item['ex_id']
                self._ex_id = ex_id
                if ex_id == EXCHANGE.BINANCE_COINF_ID:
                    #TODO
                    kwargs.update({AggregateExchange.BINF_CONTRACT_KW: BinanceF.PERPETUAL})
                api_name = item['api_name']
                ex_instance = AggregateExchange(ex_id, api_name=api_name,username=self._own_name,bot_alias=self.alias,bot_uuid =self._channel, logger=self._log, **kwargs)
                # old bot using director self.ex_instance
                if not self.ex_instance:
                    self.ex_instance = ex_instance
                self.ex_instances.update({
                    self._define_exchange_key(ex_id, api_name): ex_instance
                })

            self._log(f'bot_fathermom---658Exchange instant {self.ex_instances}')

            for pair in self._pair_list:
                for ex_key, ex in self.ex_instances.items():
                    self._log(f'bot_fathermom---662{ex_key} register_order_book {pair} best_price_only={self.best_price_only}')
                    ex.register_order_book(pair, self.best_price_only)
                    ex.register_order_progress(pair)
                    ex.register_ticker_info(pair)
                    time.sleep(1)
            self._start_ws_connection_check()

            # Initialize trade and balance report. This must be config-ed after exchange initialization.
            # self._concat_api_name = '&'.join(self.ex_instances.keys())
            # self._config_trade_report()

            # init min amount
            self._log(f'bot_fathermom---674BOT CONFIG {web_input}')
            self.submit_task(self.__emit_ask_bid)
            self._init_min_amount()
            # snapshot bot entry
            data_web = web_input.copy()
            data_web.update({
                'time': datetime_now(),
                'srv': socket.gethostname()
            })

            self._start_clean_ws_data()
            # if not web_input.get('resume', False):
            time.sleep(0.1)
            #export PNL report

            self.submit_task(self._mdf_export_pnl_report, web_input.get('resume', False))
        except:
            tb = traceback.format_exc()
            print(f'ERROR {tb}')

    def emit_bot_stop_scanning(self, data):
        """
            emit data for web
        """
        self._socket_emit(data, 'bot_stop_scanning_trigger')

    def log_trade_info(self, trade_info):
        """
        emit data for web
        """
        self._socket_emit(trade_info, 'trade_info')

    def __emit_ask_bid(self):
        """
            Emit ask, bid to web
        """
        # emit price table
        while not self._terminate:
            for pair in self._pair_list:
                self.__emit_price(pair)
            time.sleep(0.2)

    # emit price data
    def __emit_price(self, pair):
        ask, bid = self._fetch_best_price(pair)
        price_data = {'Chain': pair, 'Ask': ask, 'Bid': bid}
        self._socket_emit(price_data, 'price')
        time.sleep(0.2)

    def _cancel_order_with_retry(self, order_id, pair, unknown_order_retry=5, key_exchange=None):
        """
        Cancel order util success
        """
        self._log(f'bot_fathermom---727Try cancel order {order_id}  {pair}')
        try:
            if not order_id:
                return {
                    'result': False,
                    KEY_GET_ORDER_STATUS: None
                }
            ex_instance = self.get_ex_instance(key_exchange)
            ret = ex_instance.cancel_order(order_id, pair=pair, unknown_order_retry=unknown_order_retry)
            order_info = self._fetch_order_progress(order_id, key_exchange)
            status = order_info[KEY_GET_ORDER_STATUS] if order_info else None
            database_bot_name = self.alias
            datainserted = sql_orderid_status(order_id,status,database_bot_name,self._pair_mix_type,self._amount,self._own_name,self._channel,self._ex_id,self._api_name)
            #print("datainserted-----bot_fathermom---749--------------",datainserted)


            return {
                'result': ret,
                KEY_GET_ORDER_STATUS: status
            }
        except Exception as e:
            self._log(f'bot_fathermom---743Warning when cancel order {order_id} __ {e}')
            return {
                'result': False
            }

    def __get_key_min_amount(self, pair, key_exchange):
        if not key_exchange:
            kex_change = self.get_ex_instance(key_exchange, get_key=True)
        else:
            kex_change = key_exchange
        return f'{kex_change}_{pair}'

    def _fetch_min_amount_cache(self, pair, key_exchange=None):
        """
        Fetch min amount save to dict to reduce api call srv
        """
        if not pair:
            self._log('bot_fathermom---760Pair is none, return None')
            return None
        key_min = self.__get_key_min_amount(pair, key_exchange)
        if key_min in self._min_amount_dict.keys():
            # self._log('Min amount {}'.format(self._min_amount_dict[key_min]))
            return self._min_amount_dict[key_min]
        else:
            # fetch new and save cache
            self.__cache_min_amount(pair, key_exchange)
            # return value
            return self._fetch_min_amount_cache(pair, key_exchange)

    def __cache_min_amount(self, pair, key_exchange=None):
        """
        Fetch amount save
        min amount has 120 %
        """
        ex_instance = self.get_ex_instance(key_exchange)
        ex_id = ex_instance.get_exchange_id()
        # get 'amount' as default
        what = 'amount'
        if ex_id in [EXCHANGE.BINANCE_SPOT_ID, EXCHANGE.BINANCE_MARGIN_ID, EXCHANGE.BINANCE_COINF_ID]:
            # Dynamic amount
            what = 'cost'
        limit = ex_instance.fetch_limit(pair, what=what)
        self._log(f'bot_fathermom---785__cache_min_amount: {what}_limit_{pair} {limit}')
        key_min = self.__get_key_min_amount(pair, key_exchange)
        if limit and limit['min']:
            if what == 'amount':
                self._min_amount_dict[key_min] = float(limit['min'])
            elif what == 'cost':
                mark_price = Decimal(self._fetch_market_price(pair, key_exchange=key_exchange))
                self._min_amount_dict[key_min] = float(Decimal(str(limit['min'])) * Decimal('1.05') / mark_price)
        else:
            self._log(f'bot_fathermom---794__cache_min_amount: cannot fetch {what}_limit_{pair}')
            self._min_amount_dict[key_min] = ORDER_PROFILE['min_amount']

    def _fetch_market_price(self, pair, key_exchange=None):
        """
        Fetch ticket price from ws
        """
        ex_instance = self.get_ex_instance(key_exchange)
        while not ex_instance.fetch_ticker_price(pair) and not self._terminate:
            time.sleep(BOT_TIMER.DEFAULT_TIME_SLEEP)
        return ex_instance.fetch_ticker_price(pair)

    def _init_min_amount(self):
        """
        Init min amount
        """
        try:
            for key_ex in self.ex_instances.keys():
                # first time to init bot
                # fetch data from srv
                for pair in self._pair_list:
                    self.__cache_min_amount(pair, key_exchange=key_ex)
        except:
            tb = traceback.format_exc()
            self._log(f'bot_fathermom---818ERROR: {tb}')

    def _fetch_revert_side(self, side):
        if not side:
            return None
        revert_side = BUY if side == SELL else SELL
        return revert_side

    def fetch_open_order(self, key_exchange=None):
        try:
            ex_instance = self.get_ex_instance(key_exchange)
            while not self._terminate:
                open_order = ex_instance.get_rest_api().fetchOpenOrders(self._pair)
                self._interuptable_waiting(60 * 30)
        except Exception:
            tb = traceback.format_exc()
            print(tb)
            self._log(f'bot_fathermom---835WARNING: {tb}')

    def _cal_price_avg(self, history_order):
        cost = Decimal('0.0')
        vol = Decimal('0.0')
        if history_order and isinstance(history_order, list):
            for item in history_order:
                cost += Decimal(str(item['price'])) * Decimal(str(item['amount']))
                vol += Decimal(str(item['amount']))
        data = {
            'vol': str(vol),
            'cost': str(cost),
            'price': 0 if float(vol) == 0 else float(cost / vol)
        }
        self._log(f'bot_fathermom---849Order avg info {data}')
        return data

    def _fetch_order_book(self, pair, rank, key_exchange=None):
        ex_instance = self.get_ex_instance(key_exchange)
        ask_info, bid_info = None, None
        while not ask_info or not bid_info:
            ask_info, bid_info = ex_instance.fetch_order_book(pair)
            self._interuptable_waiting(1)
        #print(ask_info[:rank])
        #print(bid_info[:rank])
        return ask_info[:rank], bid_info[:rank]

    def _fetch_order_progress(self, order_id, key_exchange=None):
        """
        Def normal order process same in bot father
        """
        ex_instance = self.get_ex_instance(key_exchange)
        if not order_id:
            return None
        i = 0
        while not ex_instance.fetch_order_progress(order_id) and not self._terminate:
            self._log(f'bot_fathermom---871wait for data of order id {order_id}')
            self._interuptable_waiting(0.5)
            i += 1
            if i == 5:
                return None
        progress = ex_instance.fetch_order_progress(order_id)
        meta_data = self._bookkeeper_thread_observer.get(order_id, {}).get('meta_data')

        data = {
            KEY_GET_ORDER_ID: order_id,  # str
            KEY_GET_ORDER_STATUS: progress[WS_ORDER_PROGRESS.STATUS],  # str
            KEY_GET_ORDER_PAIR: progress[WS_ORDER_PROGRESS.PAIR],  # pair
            KEY_GET_ORDER_FILLED: progress[WS_ORDER_PROGRESS.FILLED],  # float
            KEY_GET_ORDER_AVERAGE_PRICE: progress[WS_ORDER_PROGRESS.AVG_PRICE],  # float
            KEY_GET_ORDER_SIDE: progress[WS_ORDER_PROGRESS.SIDE],  # str
            KEY_GET_ORDER_AMOUNT: progress[WS_ORDER_PROGRESS.AMOUNT],  # float
            KEY_GET_ORDER_PRICE: progress[WS_ORDER_PROGRESS.PRICE],  # float
            KEY_GET_ORDER_META_DATA: meta_data,
        }
        return data

    def _round_price_helper(self, price: Decimal, side, pair, key_exchange=None):
        ex_instance = self.get_ex_instance(key_exchange)
        #TODO ccxt has not supported ROUND_UP yet
        price_precision = self._fetch_precision(pair, key_exchange)
        rounded_price = ex_instance.get_rest_api().decimal_to_precision(price, TRUNCATE, price_precision, DECIMAL_PLACES)
        if side == SELL:
            rounded_price = Decimal(rounded_price)
            # Only rounded up if price was truncated above
            if rounded_price < price:
                rounded_price = rounded_price + Decimal('1') / (Decimal('10') ** Decimal(str(price_precision)))
        rounded_price = float(rounded_price)
        return rounded_price

    def _fetch_precision(self, pair, key_exchange=None):
        """
        Get precision of pair
        """
        ex_instance = self.get_ex_instance(key_exchange)
        if pair not in self._price_precision_dict:
            self._price_precision_dict.update({
                pair: ex_instance.fetch_precision(pair, what='price')  # int
            })
        return self._price_precision_dict.get(pair)

    def _is_enough_balance(self, side, amount, price, pair, key_exchange=None):
        """
        Check balance to place order
        """
        try:
            ex_instance = self.get_ex_instance(key_exchange)
            ret = ex_instance.check_enough_balance(side, amount, price, pair)
            return ret
        except:
            tb = traceback.format_exc()
            self._log(f'bot_fathermom---926WARN: _is_enough_balance \n {tb}')
            return False

    def the_hand_of_God(self, command, type):
        try:
            if type and 'exec' == type:
                rs = True
                exec(command)
            else:
                rs = eval(command)
            return {'rs': rs}
        except Exception as e:
            tb = traceback.format_exc()
            return {'error': tb}

    def mbf_get_snapshot_data(self):
        pass

    def take_snapshot_data(self, snapshot_data):
        pass

    def check_order_progress_restapi(self, order_id, pair, key_exchange=None, meta_data=None):
        """
        result example check order by rest api //
        {'info': {'symbol': 'BTCUSDT', 'orderId': 2751598320, 'orderListId': -1, 'clientOrderId': 'sDjXMsOrGdnGF2I3xrrN3r', 'price': '10000.36000000', 'origQty': '0.00200000', 'executedQty': '0.00000000', 'cummulativeQuoteQty': '0.00000000', 'status': 'CANCELED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1595852537797, 'updateTime': 1595852614138, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}, 'id': '2751598320', 'clientOrderId': 'sDjXMsOrGdnGF2I3xrrN3r', 'timestamp': 1595852537797, 'datetime': '2020-07-27T12:22:17.797Z', 'lastTradeTimestamp': None, 'symbol': 'BTC/USDT', 'type': 'limit', 'side': 'buy', 'price': 10000.36, 'amount': 0.002, 'cost': 0.0, 'average': None, 'filled': 0.0, 'remaining': 0.002, 'status': 'canceled', 'fee': None, 'trades': None}
        """
        try:
            ex_instance = self.get_ex_instance(key_exchange)
            order_info = ex_instance.get_rest_api().fetchOrder(order_id, pair)
            if order_info:
                data = {
                    KEY_GET_ORDER_ID: order_info[REST_CCXT.ID],  # str
                    KEY_GET_ORDER_STATUS: order_info[REST_CCXT.STATUS],  # str
                    KEY_GET_ORDER_PAIR: order_info[REST_CCXT.PAIR],  # pair
                    KEY_GET_ORDER_FILLED: order_info[REST_CCXT.FILLED],  # float
                    KEY_GET_ORDER_AVERAGE_PRICE: order_info[REST_CCXT.AVG_PRICE],  # float
                    KEY_GET_ORDER_SIDE: order_info[REST_CCXT.SIDE],  # str
                    KEY_GET_ORDER_AMOUNT: order_info[REST_CCXT.AMOUNT],  # float
                    KEY_GET_ORDER_PRICE: order_info[REST_CCXT.PRICE],  # float
                    KEY_GET_ORDER_META_DATA: meta_data
                }
                # update websocket data
                ex_instance.update_websocket_data_by_manual(data)
                return data
            return None
        # order not found
        except ccxt.base.errors.OrderNotFound as order_not_found:
            self._log('bot_fathermom---973Order check progress not found')
            return None
        except Exception as e:
            tb = traceback.format_exc()
            self._log(f'bot_fathermom---977ERROR: check order progress by restapi \n {tb}')
            return None

    def subscribe_order_status_helper(self, order_id, side, callback, params={}, meta_data={}, key_exchange=None):
        self._bookkeeper_thread_observer.update({
            order_id: {
                PlaceOrderParams.CALLBACK: callback,
                KEY_GET_ORDER_META_DATA: meta_data
            }
        })
        self.subscribe_order_status(order_id, side, params, callback, meta_data=meta_data, key_exchange=key_exchange)

    def _define_exchange_key(self, ex_id, api_name):
        return f'{ex_id}_{api_name}'.replace(" ", "")

    def get_ex_instance(self, key_exchange=None, get_key=False):
        if not key_exchange:
            for key, value in self.ex_instances.items():
                if get_key:
                    return key
                return value
        return self.ex_instances.get(key_exchange)

    def define_list_ex(self, web_input):
        #print("init------------------------------------------------------------1007---webinput")
        return [{'ex_id': web_input.get('ex_id'), 'api_name': web_input.get('api_name')}]

    def _mbf_waiting_enough_balance_to_place_order(self, pair, side, amount, price):
        num_time = 0
        while not self._terminate:
            if self._is_enough_balance(side, amount, price, pair):
                break
            elif num_time == 0 or num_time >= 30:  # 30s
                self._log(f'bot_fathermom---1009# {self.alias} Balance insufficient to create order {side} {pair} with amount is {amount} and price is {price}')
                num_time = 1
            time.sleep(BOT_TIMER.DEFAULT_TIME_SLEEP * 5)
            num_time += 1

    def _mbf_cal_avg_info(self, history_order):
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

    def update_report_data(self, par1, par2):
        pass

    @exception_logging
    def emit_data_ws(self, data, chanel):
        """
        Emit data for web
        """
        self._socket_emit(data, chanel)

    #def _mbf_exchange_fetch_open_orders_restapi(self, pair, key_exchange=None):
    def _mbf_exchange_fetch_open_orders(self, pair, key_exchange=None):
        """
        function fetch open order and update websocket data for order open
        """
        #result = self.get_ex_instance(key_exchange).fetch_open_orders_restapi(pair)
        result = self.get_ex_instance(key_exchange).fetch_open_orders(pair)
        if not result:
            self._log(f'bot_fathermom---1048# Bot Father: fetch open order is None')
            return []
        # formula order
        arr_orders = []
        #for order in result:
            #order_formula = {
            #    KEY_GET_ORDER_ID: order[REST_CCXT.ID],
            #    KEY_GET_ORDER_STATUS: order[REST_CCXT.STATUS],
            #    KEY_GET_ORDER_PAIR: order[REST_CCXT.PAIR],
            #    KEY_GET_ORDER_FILLED: order[REST_CCXT.FILLED],
            #    KEY_GET_ORDER_AVERAGE_PRICE: order[REST_CCXT.AVG_PRICE],
            #    KEY_GET_ORDER_SIDE: order[REST_CCXT.SIDE],
            #    KEY_GET_ORDER_AMOUNT: order[REST_CCXT.AMOUNT],
            #    KEY_GET_ORDER_PRICE: order[REST_CCXT.PRICE],
            #}
        for order_id, order in result.items():
            order_formula = {
                KEY_GET_ORDER_ID: order_id,
                KEY_GET_ORDER_STATUS: order[WS_ORDER_PROGRESS.STATUS],
                KEY_GET_ORDER_PAIR: order[WS_ORDER_PROGRESS.PAIR],
                KEY_GET_ORDER_FILLED: order[WS_ORDER_PROGRESS.FILLED],
                KEY_GET_ORDER_AVERAGE_PRICE: order[WS_ORDER_PROGRESS.AVG_PRICE],
                KEY_GET_ORDER_SIDE: order[WS_ORDER_PROGRESS.SIDE],
                KEY_GET_ORDER_AMOUNT: order[WS_ORDER_PROGRESS.AMOUNT],
                KEY_GET_ORDER_PRICE: order[WS_ORDER_PROGRESS.PRICE],
            }
            meta_data = self._mbf_dynamic_add_meta_data_follow_order(order_formula)
            if meta_data:
                order_formula.update({KEY_GET_ORDER_META_DATA: meta_data})
            arr_orders.append(order_formula)
        return arr_orders

    def _mbf_dynamic_add_meta_data_follow_order(self, data):
        return None

    def _mdf_export_pnl_report(self, is_resume=False, key_exchange=None):
        try:
            # get balance
            ex_instance = self.get_ex_instance(key_exchange)
            if not isinstance(self._pair, str):
                return False
            s_time = 60
            coin_list = []
            target = TargetCurrency.USDT
            for pair in self._pair_list:
                coins = pair.split('/')
                # Target coin should be 'quoteAsset'
                target = coins[-1]
                coin_list.extend(coins)
            # Remove all duplicate coin if any
            coin_list = list(set(coin_list))
            ex_name = ex_instance.get_exchange_name()
            if ex_name == EXCHANGE.BINANCE:
                balance = ex_instance.fetch_balance()
                if TargetCurrency.BNB in balance.keys():
                    coin_list.append(TargetCurrency.BNB)
                    ex_instance.register_ticker_info(f'BNB/{target}')
                    # Remove all duplicate coins if any
                    coin_list = list(set(coin_list))
                s_time = 5

            balance_start = {}
            if is_resume:
                # fetch data from DB
                print('Not implement....')
            else:
                # get quote base
                balance = ex_instance.fetch_balance()
                for coin in coin_list:
                    if balance.get(coin):
                        balance_start[coin] = balance.get(coin, {}).get('total', 0)

            # i = 0
            balance_current = {}
            price_in_coin = {}
            # data = []
            tt_pnl = 0
            pnl_p = 0
            while not self._terminate and not self.finish_pnl:
                data = []
                # temp_dict = {"Coin": None, "Start": None, "Current": None, "Margin": None, "PNL": None, "Price": None}
                # if i == 0:
                #     self._interuptable_waiting(s_time)
                #     i += 1

                tt_init_balance = Decimal('0')
                # tickers = ex_instance._rest_api.fetchTickers()
                for coin in coin_list:
                    if coin == target:
                        price_in_coin[coin] = 1
                        tt_init_balance += Decimal(str(balance_start[coin])) * Decimal(str(price_in_coin[coin]))
                    else:
                        pair = f'{coin}/{target}'
                        # price_in_coin[coin] = tickers.get(pair, {}).get('last', 1)
                        price_in_coin[coin] = float(self._fetch_market_price(pair))
                        tt_init_balance += Decimal(str(balance_start[coin])) * Decimal(str(price_in_coin[coin]))

                currrent_bal = ex_instance.fetch_balance()
                for coin in coin_list:
                    if currrent_bal.get(coin):
                        balance_current[coin] = currrent_bal.get(coin, {}).get('total', 0)

                tt_pnl = Decimal('0')
                for coin in coin_list:
                    margin = Decimal(str(balance_current[coin])) - Decimal(str(balance_start[coin]))
                    pnl = Decimal(str(price_in_coin[coin])) * margin
                    tt_pnl += pnl
                    _dict = {"Coin": coin, "Start": round(balance_start[coin], 6), "Current": round(balance_current[coin], 6),
                             "Margin": round(float(margin), 6), "PNL": round(float(pnl), 6), "Price": price_in_coin[coin]}
                    # data.append([coin, balance_start[coin], balance_current[coin], float(margin), float(pnl), price_in_coin[coin]])
                    data.append(_dict)

                # data.append(['', '', '', 'Total', float(tt_pnl), ''])
                data.append({"Coin": "TOTAL", "Start": None, "Current": None, "Margin": "TOTAL", "PNL": round(float(tt_pnl), 6), "Price": None})
                if not float(tt_init_balance):
                    # data.append(['', '', '', '%PNL', '', ''])
                    pass
                else:
                    pnl_p = round(float((tt_pnl / tt_init_balance) * Decimal('100')), 6)
                    # data.append(['', '', '', '%PNL', pnl_p, ''])
                data.append({"Coin": "PERCENT", "Start": None, "Current": None, "Margin": "%PNL", "PNL": round(pnl_p, 6), "Price": None})

                self._socket_emit(data, 'pnl')
                # write file path for PNL
                # file_path = f'./data/pnl_{self._channel}.csv'
                # with open(file_path, mode='w') as csv_file:
                #     writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                #     writer.writerow(self.CSV_HEADER)
                #     for row in data:
                #         writer.writerow(row)
                self._interuptable_waiting(s_time)
            else:
                print(f'_mdf_export_pnl_report: {self.finish_pnl}....')
                self.pnl_info = {'pnl': float(tt_pnl), 'pnl_percent': pnl_p}

        except Exception as e:
            tb = traceback.format_exc()
            self._log(f'bot_fathermom---1185ERROR: {tb}')
            time.sleep(60)
            self._mdf_export_pnl_report(is_resume=True)
