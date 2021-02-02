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

BIT_ORDER_BOOK_DEPTH_30 = 30
BIT_OHLCV_DEPTH = 100

class BitkubWssClient(CommonSocketManager):
    """ Websocket client for BITKUB """
    BASE_STREAM_URL = 'wss://api.bitkub.com/websocket-api/'
    BASE_API_URL = 'https://api.bitkub.com'
    TOKEN_PATH = '/api/market/wstoken'

    def __init__(self, key=None, secret=None):  # client
        super().__init__()
        self.__key = key
        #self.__secret = secret

    def set_login_token(self, key, secret):
        self.__key = key
        #self.__secret = secret

    def subscribe_public(self, subscription, callback):
        id_ = subscription
        self.STREAM_URL = self.BASE_STREAM_URL + subscription
        return self._start_socket(id_, None, None, callback)

    # Getting token from rest api
    def _get_token(self, key, secret=None, signed=False):
        api_request = urllib.request.Request(self.BASE_API_URL + self.TOKEN_PATH)
        api_request.add_header('accept', 'application/json')
        api_request.add_header('content-type', 'application/json')
        api_request.add_header('API-Key', key)
        res = json.loads(urllib.request.urlopen(api_request).read().decode('utf-8'))
        return res.get('result', '')

    def subscribe_private(self, subscription, callback):
        id_ = subscription
        token = self._get_token(self.__key)
        cred = {'auth': token}
        cred = json.dumps(cred, ensure_ascii=False).encode('utf8')
        self.STREAM_URL = self.BASE_STREAM_URL + subscription
        return self._start_socket(id_, None, cred, callback)

    # Actually, we dont un-subscribe, just disconnect the stream
    def unsubscribe(self, subscription):
        pass

class Bitkub(AuditData):
    """ High-level library BITKUB """
    def __init__(self, key=None, secret=None, logger=None, rest_api=None):
        self._log = logger if logger else log2
        self._rest_api = rest_api
        self._symbol_ids = self.__fetch_symbol_id()
        self._ws_manager = BitkubWssClient(key, secret)
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

    def __fetch_symbol_id(self):
        markets = self._rest_api.fetchMarkets()
        symbol_ids = {}
        for mk in markets:
            pair = mk.get('symbol')
            sid = mk.get('info', {}).get('id')
            # 2-way dict
            symbol_ids.update({pair: str(sid)})
            symbol_ids.update({str(sid): pair})
        return symbol_ids

    def _symbol2pair(self, symbol):
        return symbol.replace('_', '/').upper()

    def _pair2symbol(self, pair):
        return pair.replace('/', '_').lower()

    def _pair2symbol_id(self, pair):
        return self._symbol_ids.get(pair)

    def _symbol_id2pair(self, sid: str):
        return self._symbol_ids.get(str(sid))

    @on_message_handler()
    def _order_progress_handler(self, msg):
        #TODO
        pass
    # END _order_progress_handler

    def register_order_progress(self, pair=None):
        #TODO
        pass

    def unregister_order_progress(self, pair=None):
        #TODO
        pass

    def fetch_order_progress(self, order_id):
        return self.websocket_data['order_progress'].get(order_id)

    @on_message_handler()
    def _order_book_handler(self, msg):
        if not isinstance(msg, dict):
            return
        if ('data' and 'event') not in msg:
            return
        if msg['event'] == 'askschanged':
            side = 'asks'
        elif msg['event'] == 'bidschanged':
            side = 'bids'
        else: #tradeschanged
            #TODO
            return
        sid = msg['pairing_id']
        pair = self._symbol_id2pair(sid)
        data = msg['data']
        # idx: quoteVol=0, rate=1 (price), baseVol=2
        book_updates = [[d[1], d[2]] for d in data]
        self.websocket_data['order_book'][pair][side] = book_updates
    # END _order_book_handler

    def _init_order_book(self, pair):
        order_books = self._rest_api.fetchOrderBook(pair, BIT_ORDER_BOOK_DEPTH_30)
        self.websocket_data['order_book'][pair]['asks'] = order_books.get('asks')
        self.websocket_data['order_book'][pair]['bids'] = order_books.get('bids')

    def register_order_book(self, pair):
        if pair not in self.websocket_data['order_book']:
            self.websocket_data['order_book'][pair] = {}
            self.websocket_data['order_book'][pair]['asks'] = {}
            self.websocket_data['order_book'][pair]['bids'] = {}
        self._init_order_book(pair)
        sid = self._pair2symbol_id(pair)
        self._ws_manager.subscribe_public(subscription=sid, callback=self._order_book_handler)

    def unregister_order_book(self, pair):
        sid = self._pair2symbol_id(pair)
        self._ws_manager.unsubscribe(subscription=sid)

    def fetch_order_book(self, pair, index=None):
        try:
            asks = self.websocket_data['order_book'][pair].get('asks').copy()
            bids = self.websocket_data['order_book'][pair].get('bids').copy()
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
        if not isinstance(msg, dict):
            return
        if not msg.get('stream'):
            return
        stream_name = msg.get('stream')
        service_name, service_type, symbol = stream_name.split('.')
        if service_type != 'ticker':
            return
        pair = symbol.replace('_', '/').upper()
        self.websocket_data['ticker_info'][pair] = float(msg.get('last'))
    # END _ticker_info_handler

    def register_ticker_info(self, pair):
        if pair not in self.websocket_data['ticker_info']:
            self.websocket_data['ticker_info'][pair] = 0.0
        ws_pair = pair.replace('/', '_').lower()
        subscription = f'market.ticker.{ws_pair}'
        self._ws_manager.subscribe_public(subscription=subscription, callback=self._ticker_info_handler)

    def unregister_ticker_info(self, pair):
        ws_pair = pair.replace('/', '_').lower()
        subscription = f'market.ticker.{ws_pair}'
        self._ws_manager.unsubscribe(subscription=subscription)

    def fetch_ticker_price(self, pair):
        return self.websocket_data['ticker_info'].get(pair)

    @on_message_handler()
    def _ohlcv_handler(self, msg):
        #TODO
        pass
    # END _ohlcv_handler

    def register_ohlcv(self, pair, interval_str='1m'):
        #TODO
        self._log('OHLCV ws not supported!!')

    def unregister_ohlcv(self, pair, interval_str='1m'):
        #TODO
        self._log('OHLCV ws not supported!!')
