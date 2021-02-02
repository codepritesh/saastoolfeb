# coding=utf-8
import os
import sys
import json
import traceback
# For getting token from rest api
import time, base64, hashlib, hmac, urllib.request

this_path = os.path.dirname(os.path.realpath(__file__))
lib_path = this_path + '/../'
sys.path.append(lib_path)
from common import log2
from wsclient_common import on_message_handler, \
                            CommonSocketManager
from exception_decor import exception_logging
from audit_ws_data import *

KRA_ORDER_BOOK_DEPTH_10 = 10
KRA_ORDER_BOOK_DEPTH_25 = 25
KRA_ORDER_BOOK_DEPTH_100 = 100
KRA_ORDER_BOOK_DEPTH_500 = 500
KRA_ORDER_BOOK_DEPTH_1000 = 1000
OHLCV_DEPTH = 100

class KrakenWssClient(CommonSocketManager):
    """ Websocket client for KRAKEN """
    #STREAM_URL = ''
    PUBLIC_URL = 'wss://ws.kraken.com'
    PRIVATE_URL = 'wss://ws-auth.kraken.com'
    API_URL = 'https://api.kraken.com'

    def __init__(self, key=None, secret=None):  # client
        super().__init__()
        self.__key = key
        self.__secret = secret

    def set_login_token(self, key, secret):
        self.__key = key
        self.__secret = secret

    def subscribe_public(self, subscription, pair, callback):
        id_ = "_".join([subscription['name'], pair[0]])
        data = {
            'event': 'subscribe',
            'subscription': subscription,
            'pair': pair,
        }
        self.STREAM_URL = self.PUBLIC_URL
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        return self._start_socket(id_, payload, None, callback)

    # Getting token from rest api
    def _get_token(self, key, secret):
        api_nonce = bytes(str(int(time.time()*1000)), 'utf-8')
        api_request = urllib.request.Request(self.API_URL + '/0/private/GetWebSocketsToken', b'nonce=%s' % api_nonce)
        api_request.add_header('API-Key', key)
        api_request.add_header('API-Sign', base64.b64encode(hmac.new(base64.b64decode(secret), b'/0/private/GetWebSocketsToken' + hashlib.sha256(api_nonce + b'nonce=%s' % api_nonce).digest(), hashlib.sha512).digest()))
        return json.loads(urllib.request.urlopen(api_request).read().decode('utf-8')).get('result', {}).get('token', '')

    def subscribe_private(self, subscription, callback):
        id_ = "_".join([subscription['name']])
        token = self._get_token(self.__key, self.__secret)
        if token:
            subscription.update({"token": token})
        data = {
            'event': 'subscribe',
            'subscription': subscription,
        }
        self.STREAM_URL = self.PRIVATE_URL
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        return self._start_socket(id_, payload, None, callback)

    # Actually, we dont un-subscribe, just disconnect the stream
    def unsubscribe(self, subscription, pair=[]):
        if pair:
            id_ = "_".join([subscription['name'], pair[0]])
        else:
            id_ = "_".join([subscription['name']])
        self._stop_socket(id_)

class Kraken(AuditData):
    """ High-level library KRAKEN """
    def __init__(self, key=None, secret=None, logger=None, rest_api=None):
        self._log = logger if logger else log2
        self._rest_api = rest_api
        self._ws_manager = KrakenWssClient(key, secret)
        self._ws_manager.start()
        self.websocket_data = {}
        self.websocket_data['order_progress'] = {}
        self.websocket_data['order_book'] = {}
        self.websocket_data['ohlcv'] = {}
        self.websocket_data['balances'] = {}
        self.websocket_data['ticker_info'] = {}

    def set_restapi(self, rest_api):
        self._rest_api = rest_api

    def set_login_token(self, key, secret):
        self._ws_manager.set_login_token(key, secret)

    @exception_logging
    @on_message_handler()
    def _order_progress_handler(self, msg):
        if isinstance(msg, dict):
            # {"errorMessage":"Private subscriptions are currently unavailable",
            #  "event":"subscriptionStatus","status":"error","subscription":{"name":"openOrders","token":"QHEf"}}
            if msg.get('errorMessage'):
                self._log(f'Failed to fetch order info. {msg}', severity='error')
            return
        # Kraken msg is a list has 2 elements
        # Example payload:
        # [[{"OXVPYF-7LHD4-EL5FNZ":{"status":"canceled"}}],"openOrders"]
        if not isinstance(msg, list):
            return
        if msg[-1] != 'openOrders':
            return
        for order in msg[0]:
            order_id = list(order.keys())[0]
            order_data = order.get(order_id)
            order_status = order_data.get('status')
            accu_amount = order_data.get('vol_exec')
            avg_price = order_data.get('avg_price')
            cancel_reason = order_data.get('cancel_reason')

            # First payload: intitial order if it's new
            if not self.websocket_data['order_progress'].get(order_id):
                pair = ''
                side = ''
                amount = 0.0
                price = 0.0
                accu_amount = float(accu_amount)
                avg_price = float(avg_price)
                if order_data.get('vol'):
                    amount = float(order_data.get('vol'))
                if order_data.get('opentm'):
                    creation_time = int(float(order_data.get('opentm'))) #TODO check it be msec
                if order_data.get('descr'):
                    if order_data.get('descr').get('pair'):
                        pair = order_data.get('descr').get('pair').replace('XBT', 'BTC')
                    if order_data.get('descr').get('type'):
                        side = order_data.get('descr').get('type').lower()
                    if order_data.get('descr').get('price'):
                        price = float(order_data.get('descr').get('price'))
                else:
                    return

                if cancel_reason and cancel_reason =='Post only order':
                    order_status = 'expired'
                
                #self.websocket_data['order_progress'][order_id] = [order_status, pair, accu_amount, avg_price, amount, side, price, creation_time]
                stored_data = {
                        'order_status': order_status,
                        'pair': pair,
                        'accu_amount': accu_amount,
                        'avg_price': avg_price,
                        'amount': amount,
                        'side': side,
                        'price': price,
                        'creation_time': creation_time,
                    }
                self.websocket_data['order_progress'][order_id] = stored_data
                self.append_update_time_ws_data(order_id)
            # Update payload
            else:
                if order_status:
                    self.websocket_data['order_progress'][order_id]['order_status'] = order_status.lower()
                    self.append_update_time_ws_data(order_id)
                if accu_amount:
                    self.websocket_data['order_progress'][order_id]['accu_amount'] = float(accu_amount)
                if avg_price:
                    self.websocket_data['order_progress'][order_id]['avg_price'] = float(avg_price)
                if cancel_reason and cancel_reason =='Post only order':
                    self.websocket_data['order_progress'][order_id]['order_status'] = 'expired'
                    # emit signal to onnext function
    # END _order_progress_handler

    def register_order_progress(self, pair=None):
        subscription = {'name': 'openOrders'}
        self._ws_manager.subscribe_private(subscription=subscription, callback=self._order_progress_handler)

    def unregister_order_progress(self, pair=None):
        subscription = {'name': 'openOrders'}
        self._ws_manager.unsubscribe(subscription=subscription)

    @exception_logging
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
        # Kraken msg is a list has 4 elements
        # Example payload:
        # [0, {'a': [['8072.90000', '0.00000000', '1570285133.002971'], ['8076.70000', '2.65890000', '1570285129.903176', 'r']]}, 'book-10', 'XBT/USD']
        # [0, {'b': [['8067.30000', '0.00000000', '1570285132.501565'], ['8063.60000', '0.21800000', '1570285105.875617', 'r']]}, 'book-10', 'XBT/USD']
        # First msg: snapshot of all order book
        if not isinstance(msg, list):
            return
        if 'as' in msg[1]:
            pair = msg[-1].replace('XBT', 'BTC')
            depth = self.websocket_data['order_book'][pair]['depth']
            self.websocket_data['order_book'][pair]['asks'] = {}
            self.__update_order_book(pair, 'asks', msg[1]['as'], depth)
            self.websocket_data['order_book'][pair]['bids'] = {}
            self.__update_order_book(pair, 'bids', msg[1]['bs'], depth)
        # Updated msg
        elif 'a' in msg[1] or 'b' in msg[1]:
            pair = msg[-1].replace('XBT', 'BTC')
            depth = self.websocket_data['order_book'][pair]['depth']
            for x in msg[1:len(msg[1:])-1]:
                if 'a' in x:
                    self.__update_order_book(pair, 'asks', x['a'], depth)
                if 'b' in x:
                    self.__update_order_book(pair, 'bids', x['b'], depth)
    # END _order_book_handler

    def register_order_book(self, pair, depth=KRA_ORDER_BOOK_DEPTH_10):
        if pair not in self.websocket_data['order_book']:
            self.websocket_data['order_book'][pair] = {}
            self.websocket_data['order_book'][pair]['asks'] = {}
            self.websocket_data['order_book'][pair]['bids'] = {}
        self.websocket_data['order_book'][pair]['depth'] = depth
        subscription = {'name': 'book', 'depth': depth}
        self._ws_manager.subscribe_public(subscription=subscription, pair=[pair], callback=self._order_book_handler)

    def unregister_order_book(self, pair, depth=KRA_ORDER_BOOK_DEPTH_10):
        subscription = {'name': 'book', 'depth': depth}
        self._ws_manager.unsubscribe(subscription=subscription, pair=[pair])

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
        if not isinstance(msg, list):
            return
        if msg[-2] == 'ticker':
            pair = msg[-1].replace('XBT', 'BTC')
            data = msg[1]
            self.websocket_data['ticker_info'][pair] = float(data.get('c')[0])
    # END _ticker_info_handler

    def register_ticker_info(self, pair):
        if pair not in self.websocket_data['ticker_info']:
            self.websocket_data['ticker_info'][pair] = {}
        subscription = {'name': 'ticker'}
        self._ws_manager.subscribe_public(subscription=subscription, pair=[pair], callback=self._ticker_info_handler)

    def unregister_ticker_info(self, pair):
        subscription = {'name': 'ticker'}
        self._ws_manager.unsubscribe(subscription=subscription, pair=[pair])

    def fetch_ticker_price(self, pair):
        return self.websocket_data['ticker_info'].get(pair)

    @on_message_handler()
    def _ohlcv_handler(self, msg):
        if not isinstance(msg, list):
            return
        pair = msg[-1].replace('XBT', 'BTC')
        if not pair:
            return
        ohlcv_data = msg[1]
        interval = self.websocket_data['ohlcv'][pair].get('interval')
        time_event = int(float(ohlcv_data[0]) * 1000) # msec
        end_interval = int(float(ohlcv_data[1]) * 1000) # msec
        start_interval = end_interval - interval + 1 # msec
        open_price = float(ohlcv_data[2])
        highest_price = float(ohlcv_data[3])
        lowest_price = float(ohlcv_data[4])
        close_price = float(ohlcv_data[5])

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
                        self._log(f'{tb}', severity='error')
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
        if pair not in self.websocket_data['ohlcv']:
            self.websocket_data['ohlcv'][pair] = {}
        interval = self._ohlcv_interval2minute(interval_str) # minute
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
        subscription = {'name': 'ohlc', 'interval': interval}
        self._ws_manager.subscribe_public(subscription=subscription, pair=[pair], callback=self._ohlcv_handler)

    def unregister_ohlcv(self, pair, interval_str='1m'):
        interval = self._ohlcv_interval2minute(interval_str)
        subscription = {'name': 'ohlc', 'interval': interval}
        self._ws_manager.unsubscribe(subscription=subscription, pair=[pair])

    @exception_logging
    def __handler_subscribe_data_balance(self, data):
        """
        Handler subscribe data balance
        """
        print(f'{data}')

    @exception_logging
    def register_balance_account(self):
        """
        Handler balance websocket
        """
        subscription = {'name': 'accountBalancesAndMargins'}
        self._ws_manager.subscribe_private(subscription=subscription, callback=self.__handler_subscribe_data_balance)

    def unregister_balance_account(self):
        subscription = {'name': 'accountBalancesAndMargins'}
        self._ws_manager.unsubscribe(subscription=subscription)
