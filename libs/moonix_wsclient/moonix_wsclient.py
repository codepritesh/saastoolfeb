# coding=utf-8
import os
import sys
import json
import traceback
# For getting token from rest api
import time, base64, hashlib, hmac, urllib.request
from decimal import Decimal

this_path = os.path.dirname(os.path.realpath(__file__))
lib_path = this_path + '/../'
sys.path.append(lib_path)
from common import log2
from wsclient_common import on_message_handler, \
                            CommonSocketManager


ORDER_BOOK_DEPTH = 100
OHLCV_DEPTH = 100

class MoonixWssClient(CommonSocketManager):
    """ Websocket client for MOONIX """
    #STREAM_URL = ''
    PUBLIC_URL = 'wss://socket.moonix.io'
    PRIVATE_URL = 'wss://socket.moonix.io'

    def __init__(self, key=None, secret=None):  # client
        super().__init__()
        self.__key = key
        self.__secret = secret

    def set_login_token(self, key, secret):
        self.__key = key
        self.__secret = secret

    def subscribe_public(self, pair, subscription, callback):
        id_ = "_".join([subscription['name'], pair[0]])
        data = {
            'event': 'subscribe',
            'subscription': subscription,
            'pair': pair,
        }
        self.STREAM_URL = self.PUBLIC_URL
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        return self._start_socket(id_, payload, None, callback)

    def _build_private_url(self):
        path = '/SocketHandler.ashx?Moonix_API_Key={}&Moonix_SECRET_Key={}'.format(self.__key, self.__secret)
        return self.PRIVATE_URL + path

    def subscribe_private(self, subscription, callback):
        id_ = subscription
        #data = {
        #}
        self.STREAM_URL = self._build_private_url()
        #payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        payload = None
        return self._start_socket(id_, payload, None, callback)

    def unsubscribe(self, id_):
        return self._stop_socket(id_)

class Moonix:
    """ High-level library MOONIX """
    CONN_NEUTRAL_KW = 'Neutral'
    CONN_EXIST_KW = 'Connection Already Exist'
    CONN_BUILD_SUCCESS_KW = 'Keys Matched & Connection Build Successfully'

    def __init__(self, key=None, secret=None, logger=None, rest_api=None):
        self._log = logger if logger else log2
        self._ws_manager = MoonixWssClient(key, secret)
        self._ws_manager.start()
        self._rest_api = rest_api
        self.websocket_data = {}
        self.websocket_data['order_progress'] = {}
        self.websocket_data['order_book'] = {}
        self.websocket_data['ohlcv'] = {}
        self.websocket_data['balances'] = {}
        self.websocket_data['ticker_info'] = {}

        # 'CONN_EXIST_KW | CONN_NEUTRAL_KW | CONN_BUILD_SUCCESS_KW'
        self.__conn_check_state = self.CONN_NEUTRAL_KW
        self.ORDER_PROGRESS_SUBS_ID = '_order_progress_{}'.format(id(self))
        print(self.ORDER_PROGRESS_SUBS_ID)

    def set_restapi(self, rest_api):
        self._rest_api = rest_api

    def set_login_token(self, key, secret):
        self._ws_manager.set_login_token(key, secret)

    @on_message_handler()
    def _order_progress_handler(self, msg):
        try:
            if not isinstance(msg, dict):
                if msg == self.CONN_EXIST_KW:
                    self._log('{}! Unsubscribe {}'.format(self.CONN_EXIST_KW, self.ORDER_PROGRESS_SUBS_ID))
                    self._ws_manager.unsubscribe(self.ORDER_PROGRESS_SUBS_ID)
                    self.__conn_check_state = self.CONN_EXIST_KW
                elif msg == self.CONN_BUILD_SUCCESS_KW:
                    self.__conn_check_state = self.CONN_BUILD_SUCCESS_KW
                #print(self.__conn_check_state)
                return
            if msg.get('EventType') != 'EXECUTIONREPORT':
                return
            order_id = msg.get('OrderId')
            amount = float(msg.get('OrderQty'))
            accu_amount = float(msg.get('QtyFilled'))
            last_filled_amount = float(msg.get('LastQtyFilled'))
            last_filled_price = float(msg.get('LastFilledPrice'))
            order_status = 'open'
            if accu_amount == amount:
                order_status = 'closed'
            print('Msg {}'.format(msg))
            # First payload: intitial order if it's new
            if not self.websocket_data['order_progress'].get(order_id):
                pair = msg.get('Pair').replace('-', '/')
                side = msg.get('Side')
                amount = float(msg.get('OrderQty'))
                price = 0
                creation_time = ''
                stored_data = {
                        'order_status': order_status,
                        'pair': pair,
                        'accu_amount': accu_amount,
                        'avg_price': last_filled_price,
                        'amount': amount,
                        'side': side,
                        'price': price,
                        'creation_time': creation_time,
                    }
                self.websocket_data['order_progress'][order_id] = stored_data

            # Update payload
            else:
                prev_avg_price = self.websocket_data['order_progress'][order_id]['avg_price']
                prev_accu_amount = self.websocket_data['order_progress'][order_id]['accu_amount']
                self.websocket_data['order_progress'][order_id]['order_status'] = order_status
                self.websocket_data['order_progress'][order_id]['accu_amount'] = accu_amount
                avg_price = Decimal(str(prev_accu_amount)) * Decimal(str(prev_avg_price)) + Decimal(str(last_filled_amount)) * Decimal(str(last_filled_price))
                if float(accu_amount) != 0:
                    avg_price = float(avg_price / Decimal(str(accu_amount)))
                self.websocket_data['order_progress'][order_id]['avg_price'] = avg_price
        except Exception as e:
            tb = traceback.format_exc()
            print(tb)
    # END _order_progress_handler


    def register_order_progress(self, pair=None):
        try:
            #self._ws_manager.subscribe_private(subscription={'name': 'openOrders'}, callback=self._order_progress_handler)
            #print('register_order_progress ')
            self._ws_manager.subscribe_private(subscription=self.ORDER_PROGRESS_SUBS_ID, callback=self._order_progress_handler)
        except Exception as e:
            tb = traceback.format_exc()
            print(tb)
            raise Exception(e)
        else:
            # Wait up to 5sec
            retry = 5
            while (retry > 0):
                if self.__conn_check_state == self.CONN_BUILD_SUCCESS_KW:
                    return True
                elif self.__conn_check_state == self.CONN_EXIST_KW:
                    raise Exception(self.CONN_EXIST_KW)
                #else: # self.CONN_NEUTRAL_KW #TODO??
                retry -= 1
                time.sleep(1)

    def fetch_order_progress(self, order_id):
        return self.websocket_data['order_progress'].get(order_id)

    def __update_order_book(self, pair, side, data, depth):
        if not data:
            return
        oneside_book = self.websocket_data['order_book'][pair][side].copy()
        for d in data:
            if isinstance(d, list):
                price_level = float(d[0])
                vol = float(d[1])
            elif isinstance(d, dict):
                price_level = float(d.get("price"))
                vol = float(d.get("size"))
            if vol > 0:
                oneside_book.update({price_level: vol})
            else:
                if price_level in oneside_book:
                    oneside_book.pop(price_level)
        oneside_book = dict(sorted(oneside_book.items(), reverse=(side == 'bids'))[:depth])
        self.websocket_data['order_book'][pair][side] = oneside_book

    @on_message_handler()
    def _order_book_handler(self, msg):
        #TODO
        pass
    # END _order_book_handler

    def register_order_book(self, pair):
        if self.websocket_data['order_book'].get(pair):
            return
        self.websocket_data['order_book'][pair] = {}
        self.websocket_data['order_book'][pair]['asks'] = {}
        self.websocket_data['order_book'][pair]['bids'] = {}
        #subscription = {"name": "book", "depth": KRA_ORDER_BOOK_DEPTH}
        #self._ws_manager.subscribe_public(pair=[pair], subscription=subscription, callback=self._order_book_handler)

    def fetch_order_book(self, pair, index=None):
        try:
            copy_of_order_book_asks = self.websocket_data['order_book'][pair].get('asks').copy()
            copy_of_order_book_bids = self.websocket_data['order_book'][pair].get('bids').copy()
            asks = sorted(copy_of_order_book_asks.items())
            bids = sorted(copy_of_order_book_bids.items(), reverse=True)
        except:
            tb = traceback.format_exc()
            self._log(f'{tb}', severity='error')
            return None, None

        if asks and bids:
            if index:
                return asks[index-1], bids[index-1]
            else:
                return asks, bids
        else:
            return None, None

    @on_message_handler()
    def _ticker_info_handler(self, msg):
        #TODO
        pass
    # END _ticker_info_handler

    def register_ticker_info(self, pair):
        if self.websocket_data['ticker_info'].get(pair):
            return
        self.websocket_data['ticker_info'][pair] = {}
        #self._ws_manager.subscribe_public(pair=[pair], subscription={"name": "ticker"}, callback=self._ticker_info_handler)

    def fetch_ticker_price(self, pair):
        return self.websocket_data['ticker_info'].get(pair)

    @on_message_handler()
    def _ohlcv_handler(self, msg):
        pair = ''
        if isinstance(msg, list):
            pair = msg[-1].replace('XBT', 'BTC')
            ohlcv_data = msg[1]
            interval = self.websocket_data['ohlcv'][pair].get('interval')
            time_event = int(float(ohlcv_data[0]) * 1000) # msec
            end_interval = int(float(ohlcv_data[1]) * 1000) # msec
            start_interval = end_interval - interval + 1 # msec
            open_price = float(ohlcv_data[2])
            highest_price = float(ohlcv_data[3])
            lowest_price = float(ohlcv_data[4])
            close_price = float(ohlcv_data[5])
        if pair:
            current_cdl = [time_event, open_price, highest_price, lowest_price, close_price, None, start_interval, end_interval]
            if self.websocket_data['ohlcv'][pair].get('running'):
                # Get newest saved running candle
                newest_running_cdl = self.websocket_data['ohlcv'][pair]['running'][-1]
                # update the running candle list
                if len(self.websocket_data['ohlcv'][pair]['running']) >= 5:
                    self.websocket_data['ohlcv'][pair]['running'].pop(0)
                self.websocket_data['ohlcv'][pair]['running'].append(current_cdl)
                # Check if the newest saved running candle becomes old.
                # We must firstly check if stored ohlcv data is just initalized by restapi or not.
                # If yes (restapi data only have 6 elements [time_event, o, h, l, v] in a rank),
                #   get saved time_event, otherwise, get saved end_interval,
                # then compare to start_interval of current_candle.
                if len(newest_running_cdl) < 7:
                    saved_time_event = newest_running_cdl[0]
                    if saved_time_event < start_interval:
                        try:
                            interval_str = self.websocket_data['ohlcv'][pair]['interval_str']
                            last_historical_candle = self._rest_api.fetch_ohlcv(pair, interval_str)[-2]
                        except:
                            tb = traceback.format_exc()
                            self._log(f'{tb}', severity='warning')
                        else:
                            # remove the oldest candle
                            self.websocket_data['ohlcv'][pair]['data'].pop(0)
                            # add a new one, the most recent candle last
                            self.websocket_data['ohlcv'][pair]['data'].append(last_historical_candle)
                else:
                    saved_end_interval = newest_running_cdl[-1]
                    # Check if the saved runtime candle becomes old
                    # WARN: somehow on Binance, time_event is out of [start_interval, end_interval].
                    #   Don't compare to time_event.
                    if saved_end_interval < start_interval:
                        if len(self.websocket_data['ohlcv'][pair]['data']) >= OHLCV_DEPTH:
                            self.websocket_data['ohlcv'][pair]['data'].pop(0)
                        # the most recent candle last
                        self.websocket_data['ohlcv'][pair]['data'].append(newest_running_cdl)
            else:
                # In case of fetch_ohlcv restapi failure
                self.websocket_data['ohlcv'][pair]['running'] = [current_cdl, ]
                self.websocket_data['ohlcv'][pair]['data'] = []
    # END _ohlcv_handler

    def _ohlcv_interval2minute(self, interval_str):
        interval_value = int(interval_str[:-1])
        if interval_str[-1] == 'm':
            factor = 1
        elif interval_str[-1] == 'h':
            factor = 60
        elif interval_str[-1] == 'd':
            factor = 1440
        elif interval_str[-1] == 'w':
            factor = 10080
        elif interval_str[-1] == 'M':
            factor = 40320 # 1 month = 4 weeks
        else:
            self._log(f'Invalid interval unit! {interval_str}', severity='error')
            return None
        return interval_value * factor

    def register_ohlcv(self, pair, interval_str='1m'):
        if self.websocket_data['ohlcv'].get(pair):
            return
        interval = self._ohlcv_interval2minute(interval_str) # minute
        self.websocket_data['ohlcv'][pair] = {}
        self.websocket_data['ohlcv'][pair]['interval_str'] = interval_str
        self.websocket_data['ohlcv'][pair]['interval'] = interval * 60 * 1000 # msec
        # intialize ohlcv data using rest api
        try:
            initial_ohlcv = self._rest_api.fetch_ohlcv(pair, interval_str)
        except:
            tb = traceback.format_exc()
            self._log(f'{tb}', severity='warning')
            initial_ohlcv = None
        if initial_ohlcv:
            self.websocket_data['ohlcv'][pair]['running'] = [initial_ohlcv[-1], ]
            self.websocket_data['ohlcv'][pair]['data'] = initial_ohlcv[-OHLCV_DEPTH-1:-1]
        subscription = {"name": "ohlc", "interval": interval}
        self._ws_manager.subscribe_public(pair=[pair], subscription=subscription, callback=self._ohlcv_handler)
