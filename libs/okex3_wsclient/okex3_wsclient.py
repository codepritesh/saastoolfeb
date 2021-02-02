# coding=utf-8
import os
import sys
import json
import zlib
import time
import traceback

this_path = os.path.dirname(os.path.realpath(__file__))
lib_path = this_path + '/../'
sys.path.append(lib_path)
from common import log2
from wsclient_common import on_message_handler, \
                            CommonSocketManager

def inflate(compressed_data):
    decompress = zlib.decompressobj(-zlib.MAX_WBITS)
    inflated = decompress.decompress(compressed_data)
    inflated += decompress.flush()
    inflated_dict = json.loads(inflated.decode('utf-8'))
    return inflated_dict

class Okex3WssClient(CommonSocketManager):
    """ Websocket client for OKEX3 """
    STREAM_URL = 'wss://real.okex.com:8443/ws/v3'

    def __init__(self, key=None, secret=None, passphrase=None):  # client
        super().__init__()
        self.__key = key
        self.__secret = secret
        self.__passphrase = passphrase

    def set_login_token(self, key, secret, passphrase):
        self.__key = key
        self.__secret = secret
        self.__passphrase = passphrase

    def subscribe(self, subscription, callback):
        id_ = ''
        for channel in subscription:
            id_ += channel
        data = {
            "op": "subscribe",
            "args": subscription,
        }
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        credential = None
        if self.__key and self.__secret and self.__passphrase:
            login_token = [self.__key, self.__passphrase, time.time(), self.__secret]
            data = {
                "op": "login",
                "args": login_token,
            }
            credential = json.dumps(data, ensure_ascii=False).encode('utf8')
        return self._start_socket(id_, payload, credential, callback)

    def unsubscribe(self, subscription):
        pass

class Okex3:
    """ High-level library OKEX3 """
    def __init__(self, key=None, secret=None, passphrase=None, logger=None, rest_api=None):
        self._log = logger if logger else log2
        self._ws_manager = Okex3WssClient(key, secret, passphrase)
        self._ws_manager.start()
        self._rest_api = rest_api
        self.websocket_data = {}
        self.websocket_data['order_progress'] = {}
        self.websocket_data['order_book'] = {}
        self.websocket_data['ohlcv'] = {}
        self.websocket_data['balances'] = {}

    def set_restapi(self, rest_api):
        self._rest_api = rest_api

    def set_login_token(self, key, secret, passphrase):
        self._ws_manager.set_login_token(key, secret, passphrase)

    @on_message_handler(decoder=inflate)
    def _order_progress_handler(self, msg):
        #TODO
        pass
    # END _order_progress_handler

    def register_order_progress(self, pair):
        if self.websocket_data['order_progress'].get(pair):
            return
        self.websocket_data['order_progress'][pair] = {}
        args = "spot/order:" + pair.replace('/', '-')
        self._ws_manager.subscribe(subscription=[args], callback=self._order_progress_handler)

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

    @on_message_handler(decoder=inflate)
    def _order_book_handler(self, msg):
        # Okex3 msg is a dict
        # Partital msg (200):
        # {'data': [{'bids': [['7224.1', '0.05691715', '4'], ['7224', '2.59', '1']], 'checksum': 2063881655, 'asks': [['7224.2', '4.54320917', '9'], ['7224.5', '0.00230285', '1']] 'instrument_id': 'BTC-USDT', 'timestamp': '2019-12-25T07:05:35.651Z'}], 'action': 'partial', 'table': 'spot/depth'}
        # Update msg (possible num of asks != num of bids):
        # {'data': [{'bids': [['7221.5', '0.50781827', '4'], ['7221.3', '0.12062618', '1'], ['7220.7', '0.53442152', '2']], 'checksum': 1151199021, 'asks': [['7229.4', '0.20764094', '1'], ['7240.3', '0', '0']], 'instrument_id': 'BTC-USDT', 'timestamp': '2019-12-25T07:05:35.794Z'}], 'action': 'update', 'table': 'spot/depth'}
        if not isinstance(msg, dict):
            return
        if msg.get('table') != 'spot/depth':
            return
        data_list = msg.get('data')
        for data in data_list:
            pair = data.get('instrument_id')
            pair = pair.replace('-', '/')
            if msg.get('action') == 'partial':
                self.websocket_data['order_book'][pair]['asks'] = {}
                self.websocket_data['order_book'][pair]['bids'] = {}
            self.__update_order_book(pair, 'asks', data.get('asks'), KEX_ORDER_BOOK_DEPTH)
            self.__update_order_book(pair, 'bids', data.get('bids'), KEX_ORDER_BOOK_DEPTH)
    # END _order_book_handler

    def register_order_book(self, pair):
        if self.websocket_data['order_book'].get(pair):
            return
        self.websocket_data['order_book'][pair] = {}
        self.websocket_data['order_book'][pair]['asks'] = {}
        self.websocket_data['order_book'][pair]['bids'] = {}
        args = "spot/depth:" + pair.replace('/', '-')
        self._ws_manager.subscribe(subscription=[args], callback=self._order_book_handler)

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

    @on_message_handler(decoder=inflate)
    def _ticker_info_handler(self, msg):
        if not isinstance(msg, dict):
            return
        if msg.get('table') == 'spot/ticker':
            data_list = msg.get('data')
            for data in data_list:
                pair = data.get('instrument_id')
                pair = pair.replace('-', '/')
                price = float(data.get('last'))
                self.websocket_data['ticker_info'][pair] = price
    # END _ticker_info_handler

    def register_ticker_info(self, pair):
        if self.websocket_data['ticker_info'].get(pair):
            return
        self.websocket_data['ticker_info'][pair] = {}
        args = "spot/ticker:" + pair.replace('/', '-')
        self._ws_manager.subscribe(subscription=[args], callback=self._ticker_info_handler)

    def fetch_ticker_price(self, pair):
        return self.websocket_data['ticker_info'].get(pair)

    def register_ohlcv(self, pair, interval_str='1m'):
        self._log('Not implemented yet')
        #TODO
        return
