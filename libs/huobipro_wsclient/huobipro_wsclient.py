# coding=utf-8
import os
import sys
import json
import gzip
from decimal import Decimal
from urllib import parse
import urllib.parse
import base64, hashlib, hmac
import time, uuid
import traceback
from functools import wraps
from datetime import datetime
# from huobi.impl.utils.apisignature import create_signature

this_path = os.path.dirname(os.path.realpath(__file__))
exlib_path = this_path + '/../'
sys.path.append(exlib_path)
from wsclient_common import CommonSocketManager

MARKET_DEPTH_LEVEL_0 = 'step0'
MARKET_DEPTH_LEVEL_1 = 'step1'
MARKET_DEPTH_LEVEL_2 = 'step2'
MARKET_DEPTH_LEVEL_3 = 'step3'
MARKET_DEPTH_LEVEL_4 = 'step4'
MARKET_DEPTH_LEVEL_5 = 'step5'
HUO_ORDER_BOOK_DEPTH_20 = 20
HUO_ORDER_BOOK_DEPTH_150 = 150
OHLCV_DEPTH = 100

def gunzip(compressed_data):
    return gzip.decompress(compressed_data)

def on_message_handler():
    def decorator(func):
        @wraps(func)
        def func_wrapper(self, payload, isBinary=True):
            if isBinary:
                try:
                    # Huobipro uses gzip compress
                    msg = json.loads(gunzip(payload).decode('utf-8'))
                except:
                    tb = traceback.format_exc()
                    print('{}'.format(tb))
                else:
                    func(self, msg)
        return func_wrapper
    return decorator

class UrlParamsBuilder(object):
    def __init__(self):
        self.param_map = dict()
        self.post_map = dict()

    def put_url(self, name, value):
        if value is not None:
            if isinstance(value, (list, dict)):
                self.param_map[name] = value
            else:
                self.param_map[name] = str(value)

    def put_post(self, name, value):
        if value is not None:
            if isinstance(value, (list, dict)):
                self.post_map[name] = value
            else:
                self.post_map[name] = str(value)

    def build_url(self):
        if len(self.param_map) == 0:
            return ""
        encoded_param = urllib.parse.urlencode(self.param_map)
        return "?" + encoded_param

    def build_url_to_json(self):
        return json.dumps(self.param_map, ensure_ascii=False).encode('utf8')

def utc_now():
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

def credential_builder(private_url, apikey, secret, time=None):
    host = urllib.parse.urlparse(private_url).hostname
    path = urllib.parse.urlparse(private_url).path

    builder = UrlParamsBuilder()
    builder.put_url('AccessKeyId', apikey)
    builder.put_url('SignatureVersion', '2')
    builder.put_url('SignatureMethod', 'HmacSHA256')
    if time:
        timestamp = time
    else:
        timestamp = utc_now()
    builder.put_url('Timestamp', timestamp)

    param_keys = sorted(builder.param_map.keys())
    qs = '&'.join(['{}={}'.format(k, parse.quote(builder.param_map[k], safe='')) for k in param_keys])
    payload = '{}\n{}\n{}\n{}'.format('GET', host, path, qs)
    dig = hmac.new(secret.encode('utf-8'), msg=payload.encode('utf-8'), digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(dig).decode('utf-8')
    print(signature)

    builder.put_url('Signature', signature)
    builder.put_url('op', 'auth')
    builder1 = UrlParamsBuilder()
    create_signature(apikey, secret, 'GET', private_url, builder1)#, timestamp)
    builder1.put_url('op', 'auth')
    return builder.build_url_to_json()

class HuobiproWssClient(CommonSocketManager):
    """ Websocket client for HUOBIPRO """
    PUBLIC_STREAM_URL = 'wss://api.huobi.pro/ws'
    PRIVATE_V1_STREAM_URL = 'wss://api.huobi.pro/ws/v1'

    def __init__(self, key=None, secret=None, passphrase=None):  # client
        super().__init__()
        self.__key = key
        self.__secret = secret

    def set_login_token(self, key, secret, passphrase=None):
        self.__key = key
        self.__secret = secret

    def subscribe_public(self, subscription, callback):
        id_ = subscription
        # id_ = str(uuid.uuid4())[::5]
        data = {
            "sub": subscription,
            "id": id_,
        }
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        self.STREAM_URL = self.PUBLIC_STREAM_URL
        return self._start_socket(id_, payload, None, callback)

    def subscribe_private(self, subscription, callback):
        if not self.__key and not self.__secret:
            return False
        id_ = subscription
        data = {
            "op": "sub",
            "cid": id_,
            "topic": subscription,
        }
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        self.STREAM_URL = self.PRIVATE_V1_STREAM_URL
        credential = credential_builder(self.STREAM_URL, self.__key, self.__secret)
        print(credential)
        return self._start_socket(id_, payload, credential, callback)

    def unsubscribe(self):
        pass

class Huobipro:
    """ High-level library HUOBIPRO """
    def __init__(self, key=None, secret=None, passphrase=None, logger=None, rest_api=None):
        self._logger = logger if logger else print
        self._ws_manager = HuobiproWssClient(key, secret, passphrase)
        self._ws_manager.start()
        self._rest_api = rest_api
        self.websocket_data = {}
        self.websocket_data['order_progress'] = {}
        self.websocket_data['order_book'] = {}
        self.websocket_data['ohlcv'] = {}
        self.websocket_data['balances'] = {}
        self.websocket_data['ticker_info'] = {}
        self._order_book_depth = HUO_ORDER_BOOK_DEPTH_150

    def set_restapi(self, rest_api):
        self._rest_api = rest_api

    def set_login_token(self, key, secret, passphrase=None):
        self._ws_manager.set_login_token(key, secret, passphrase)

    @on_message_handler()
    def _order_progress_handler(self, msg):
        print(msg)
        if not isinstance(msg, dict) or not msg.get('data'):
            return
        ws_pair = msg['data'].get('symbol')
        order_data = self.websocket_data['order_progress'].copy()
        pair = ''
        for p in order_data.keys():
            if order_data[p].get('ws_pair') == ws_pair:
                pair = p
                break
        if not pair:
            return
        order_data = msg.get('data')
        order_id = order_data.get('order-id')
        order_status = order_data.get('order-state')
        if order_status:
            order_status = order_status.lower()
            if order_status == 'submitted' or order_status == 'partial-filled':
                order_status = 'open'
            elif order_status == 'filled':
                order_status = 'closed'
        accu_amount = float(order_data.get('filled-amount'))
        unfill = order_data.get('unfilled-amount')
        amount = float(Decimal(str(accu_amount)) + Decimal(str(unfill)))
        avg_price = float(order_data.get('price'))
        side = order_data.get('order-type').split('-')
        stored_data = {
                        'order_status': order_status,
                        'pair': pair,
                        'accu_amount': accu_amount,
                        'avg_price': avg_price,
                        'amount': amount,
                        'side': side,
                        'price': avg_price,
                        'creation_time': None,
                    }
        self.websocket_data['order_progress'][order_id] = stored_data
    # END _order_progress_handler

    def register_order_progress(self, pair=None):
        if pair:
            ws_pair = pair.replace('/', '').lower()
        else:
            ws_pair = '*'
        self.websocket_data['order_progress'][pair]['ws_pair'] = ws_pair
        subscription = 'orders.{}.update'.format(ws_pair)
        print(subscription)
        self._ws_manager.subscribe_private(subscription=subscription, callback=self._order_progress_handler)

    def fetch_order_status(self, order_id):
        if self.websocket_data['order_progress'].get(order_id):
            return self.websocket_data['order_progress'].get(order_id)
        return None

    def fetch_order_progress(self, order_id):
        if self.websocket_data['order_progress'].get(order_id):
            return self.websocket_data['order_progress'].get(order_id)
        return None

    # START order_book
    @on_message_handler()
    def _order_book_handler(self, msg):
        if not isinstance(msg, dict) or not msg.get('ch') or not msg.get('tick'):
            return
        ws_pair = msg.get('ch').split('.')[1]
        order_book_data = self.websocket_data['order_book'].copy()
        pair = ''
        for p in order_book_data.keys():
            if order_book_data[p].get('ws_pair') == ws_pair:
                pair = p
                break
        if not pair:
            # Only cache data for registered pair
            return
        asks_bids = msg.get('tick')
        self.websocket_data['order_book'][pair]['asks'] = asks_bids.get('asks')
        self.websocket_data['order_book'][pair]['bids'] = asks_bids.get('bids')
        # print(self.websocket_data['order_book'][pair]['asks'])
    # END _order_book_handler

    def register_order_book(self, pair, aggr_level=MARKET_DEPTH_LEVEL_0):
        if self.websocket_data['order_book'].get(pair):
            return
        self.websocket_data['order_book'][pair] = {}
        ws_pair = pair.replace('/', '').lower()
        self.websocket_data['order_book'][pair]['ws_pair'] = ws_pair
        self.websocket_data['order_book'][pair]['asks'] = []
        self.websocket_data['order_book'][pair]['bids'] = []
        if aggr_level == MARKET_DEPTH_LEVEL_0:
            self._order_book_depth = HUO_ORDER_BOOK_DEPTH_150
        else:
            self._order_book_depth = HUO_ORDER_BOOK_DEPTH_20
        subscription = 'market.{}.depth.{}'.format(ws_pair, aggr_level)
        self._ws_manager.subscribe_public(subscription=subscription, callback=self._order_book_handler)

    def fetch_order_book(self, pair, index=None):
        asks = self.websocket_data['order_book'].get(pair, None).get('asks')
        bids = self.websocket_data['order_book'].get(pair, None).get('bids')

        if asks and bids:
            if index:
                return asks[index], bids[index]
            else:
                return asks, bids
        else:
            return None, None

    # Ticker info
    @on_message_handler()
    def _ticker_info_handler(self, msg):
        if not isinstance(msg, dict) or not msg.get('ch') or not msg.get('tick'):
            return
        ws_pair = msg.get('ch').split('.')[1]
        ticker_data = self.websocket_data['ticker_info'].copy()
        pair = ''
        for p in ticker_data.keys():
            if ticker_data[p].get('ws_pair') == ws_pair:
                pair = p
                break
        if not pair:
            # Only cache data for registered pair
            return
        tick = msg.get('tick')
        for index in tick.get('data'):
            self.websocket_data['ticker_info'][pair]['price'] = index.get('price')

    def register_ticker_info(self, pair):
        if self.websocket_data['ticker_info'].get(pair):
            return
        self.websocket_data['ticker_info'][pair] = {}
        ws_pair = pair.replace('/', '').lower()
        self.websocket_data['ticker_info'][pair]['ws_pair'] = ws_pair
        stream_name = "market.{}.trade.detail".format(ws_pair)
        self._ws_manager.subscribe_public(subscription=stream_name, callback=self._ticker_info_handler)

    def fetch_ticker_price(self, pair):
        return self.websocket_data['ticker_info'].get(pair).get('price', None)

    # OHLCV impl
    @on_message_handler()
    def _ohlcv_handler(self, msg):
        if not isinstance(msg, dict) or not msg.get('ch') or not msg.get('tick'):
            return
        ws_pair = msg.get('ch').split('.')[1]
        ohlcv_data = self.websocket_data['ohlcv'].copy()
        pair = ''
        for p in ohlcv_data.keys():
            if ohlcv_data[p].get('ws_pair') == ws_pair:
                pair = p
                break
        if not pair:
            # Only cache data for registered pair
            return
        data = msg.get('tick')
        _time = int(data.get('id'))
        _open = float(data.get('open'))
        _high = float(data.get('high'))
        _low = float(data.get('low'))
        _close = float(data.get('close'))
        _vol = float(data.get('amount'))
        running_ohlcv = [_time, _open, _high, _low, _close, _vol]
        # print(running_ohlcv)
        if len(self.websocket_data['ohlcv'][pair]['running']) > 0:
            last_running_ohlcv = self.websocket_data['ohlcv'][pair]['running'][-1]
        else:
            last_running_ohlcv = running_ohlcv

        if _time != last_running_ohlcv[0]:
            if len(self.websocket_data['ohlcv'][pair]['data']) >= OHLCV_DEPTH:
                self.websocket_data['ohlcv'][pair]['data'].pop(0)
            self.websocket_data['ohlcv'][pair]['data'].append(last_running_ohlcv)
            # print(self.websocket_data['ohlcv'][pair]['data'])
        if len(self.websocket_data['ohlcv'][pair]['running']) >= 2:
            self.websocket_data['ohlcv'][pair]['running'].pop(0)

        self.websocket_data['ohlcv'][pair]['running'].append(running_ohlcv)

    # END _ohlcv_handler

    def register_ohlcv(self, pair, interval_str='1m'):
        if self.websocket_data['ohlcv'].get(pair):
            return
        if interval_str[-1] == 'm':
            period = interval_str[:-1] + 'min'
        elif interval_str[-1] == 'd':
            period = interval_str[:-1] + 'day'
        elif interval_str[-1] == 'h':
            period = interval_str[:-1] + 'hour'
        elif interval_str[-1] == 'M':
            period = interval_str[:-1] + 'mon'
        elif interval_str[-1] == 'w':
            period = interval_str[:-1] + 'week'
        elif interval_str[-1] == 'y':
            period = interval_str[:-1] + 'year'
        else:
            return
        self.websocket_data['ohlcv'][pair] = {}
        self.websocket_data['ohlcv'][pair]['interval_str'] = interval_str
        try:
            initial_ohlcv = self._rest_api.fetch_ohlcv(pair, interval_str)
            self.websocket_data['ohlcv'][pair]['running'] = [initial_ohlcv[-1], ]
            self.websocket_data['ohlcv'][pair]['data'] = initial_ohlcv[-OHLCV_DEPTH-1:-1]
        except:
            self.websocket_data['ohlcv'][pair]['data'] = []
            self.websocket_data['ohlcv'][pair]['running'] = []
            tb = traceback.format_exc()
            self._logger('{}'.format(tb))
        ws_pair = pair.replace('/', '').lower()
        self.websocket_data['ohlcv'][pair]['ws_pair'] = ws_pair
        subscription = 'market.{}.kline.{}'.format(ws_pair, period)
        self._ws_manager.subscribe_public(subscription=subscription, callback=self._ohlcv_handler)

    def fetch_ohlcv(self, pair, tf_index=1):
        if self.websocket_data['ohlcv'][pair].get('data'):
            if tf_index >= 1:
                return self.websocket_data['ohlcv'][pair].get('data')[-int(tf_index)]
            else:
                return self.websocket_data['ohlcv'][pair].get('data')
        return None

if __name__ == '__main__':
    a = Huobipro()
    # a.register_order_book('BTC/USDT')
    # a.register_ticker_info('BTC/USDT')
    # a.register_ohlcv('BTC/USDT', '1m')
    a.register_order_progress('BTC/USDT')
    time.sleep(10)
    # print(a.fetch_ticker_price('BTC/USDT'))
    # print(a.fetch_order_book('BTC/USDT'))
    # print(a.fetch_order_book('BTC/USDT', -1))
    # print(a.fetch_ohlcv('BTC/USDT'))
    os._exit(0)
