# coding=utf-8
import os
import sys
import json
import time
import uuid
import binascii
import traceback
from threading import Lock

this_path = os.path.dirname(os.path.realpath(__file__))
lib_path = this_path + '/../'
bots_path = this_path + '/../../bots'
sys.path.append(bots_path)
from bot_constant import *
sys.path.append(lib_path)
from common import DEFAULT_TZ, log2
from wsclient_common import on_message_handler, \
                            CommonSocketManager
from exception_decor import exception_logging
from audit_ws_data import *

HIT_ORDER_BOOK_DEPTH_5 = 5
HIT_ORDER_BOOK_DEPTH_200 = 200
OHLCV_DEPTH = 100

class Hitbtc2WssClient(CommonSocketManager):
    """ Websocket client for HITBTC2 """
    #PUBLIC_STREAM_URL = 'wss://api.hitbtc.com/api/2/ws/public'
    PUBLIC_STREAM_URL = 'wss://api.hitbtc.com/api/2/ws'
    PRIVATE_STREAM_URL = 'wss://api.hitbtc.com/api/2/ws/trading'
    STREAM_URL = ''

    def __init__(self, key=None, secret=None):  # client
        super().__init__()
        self.__key = key
        self.__secret = secret

    def set_login_token(self, key, secret):
        self.__key = key
        self.__secret = secret

    def subscribe_public(self, subscription, params, callback, use_id=False):
        id_ = '_'.join([subscription, params.get('symbol', 'None')])
        data = {
            "method": subscription,
            "params": params
        }
        if use_id:
            data.update({"id": id_})
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        self.STREAM_URL = self.PUBLIC_STREAM_URL
        return self._start_socket(id_, payload, None, callback)

    def subscribe_private(self, subscription, params, callback, use_id=False):
        id_ = '_'.join([subscription, params.get('symbol', 'None')])
        data = {
            "method": subscription,
            "params": params
        }
        if use_id:
            data.update({"id": id_})
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        credential = None
        if self.__key and self.__secret:
            data = {
                "method": "login",
                "params": {"algo": "BASIC", "pKey": self.__key, "sKey": self.__secret}
            }
            credential = json.dumps(data, ensure_ascii=False).encode('utf8')
        self.STREAM_URL = self.PRIVATE_STREAM_URL
        return self._start_socket(id_, payload, credential, callback)

    def unsubscribe(self, subscription, params):
        id_ = '_'.join([subscription, params.get('symbol', 'None')])
        self._stop_socket(id_)

class Hitbtc2(AuditData):
    """ High-level library HITBTC2 """
    PAIR_MAPPER = {
            'BTC/USDT': 'BTC/USD',
        }

    def __init__(self, key=None, secret=None, logger=None, rest_api=None):
        self._log = logger if logger else log2
        self._rest_api = rest_api
        self._ws_manager = Hitbtc2WssClient(key, secret)
        self._ws_manager.start()
        self._create_order_lock = Lock()
        self._create_order_error = ''
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

    @on_message_handler()
    def _order_progress_handler(self, msg):
        # print('_order_progress_handler {}'.format(msg))
        if not isinstance(msg, dict):
            return
        if msg.get("method") != 'activeOrders' and msg.get("method") != "report":
            return
        data = msg.get("params")
        # First payload, all open orders
        if isinstance(data, list):
            for order in data:
                order_id = order.get("clientOrderId")
                ex_pair = order.get("symbol")
                coin2 = ex_pair[3:]
                if coin2 == 'USD':
                    coin2 = 'USDT'
                pair = ex_pair[:3] + '/' + coin2
                order_status = order.get("status")
                # Convert binanace order status to align with kraken
                if order_status == 'new' or order_status == 'partiallyFilled':
                    order_status = 'open'
                elif order_status == 'filled':
                    order_status = 'closed'
                accu_amount = float(order.get("cumQuantity"))
                price = float(order.get("price", 0))
                amount = float(order.get("quantity"))
                try:
                    creation_time = int(float(order.get("createdAt"))) # msec
                except Exception as e:
                    #self._log('DBG1: TZ change to UTC!!', severity='debug')
                    # createdAt is string
                    os.environ['TZ'] = 'UTC'
                    time.tzset()
                    p = '%Y-%m-%dT%H:%M:%S.%fZ'
                    d = order.get("createdAt")
                    creation_time = int(time.mktime(time.strptime(d, p)))
                    # Reset TZ to 'Asia/Ho_Chi_Minh'
                    os.environ['TZ'] = DEFAULT_TZ
                    time.tzset()
                side = order.get("side")
                #self.websocket_data['order_progress'][order_id] = [order_status, pair, accu_amount, price, amount, side, price, creation_time]
                stored_data = {
                        'order_status': order_status,
                        'pair': pair,
                        'accu_amount': accu_amount,
                        'avg_price': price,
                        'amount': amount,
                        'side': side,
                        'price': price,
                        'creation_time': creation_time,
                    }
                self.websocket_data['order_progress'][order_id] = stored_data
                self.append_update_time_ws_data(order_id)
                #self._log(f'Create new ws data, order id {order_id} : f{stored_data}')
        # Update payload
        elif isinstance(data, dict):
            order_id = data.get("clientOrderId")
            order_status = data.get("status")
            accu_amount = float(data.get("cumQuantity"))
            # Convert binanace order status to align with kraken
            if order_status == 'new' or order_status == 'partiallyFilled':
                order_status = 'open'
            elif order_status == 'filled':
                order_status = 'closed'
            # Order already exists
            if self.websocket_data['order_progress'].get(order_id):
                old_status = self.websocket_data['order_progress'].get(order_id).get('order_status')
                if ORDER_CLOSED == old_status or ORDER_CANCELED == old_status:
                    #self._log(f'Order {order_id} has old status {old_status}, ignore update status from ws, new status {order_status.lower()}')
                    return
                else:
                    self.websocket_data['order_progress'][order_id].update({
                        'order_status': order_status.lower()
                    })
                self.append_update_time_ws_data(order_id)
                self.websocket_data['order_progress'][order_id].update({
                    'accu_amount': float(accu_amount)})
            else:
                # New order
                ex_pair = data.get("symbol")
                coin2 = ex_pair[3:]
                if coin2 == 'USD':
                    coin2 = 'USDT'
                pair = ex_pair[:3] + '/' + coin2
                price = float(data.get("price", 0))
                amount = float(data.get("quantity"))
                try:
                    creation_time = float(data.get("createdAt"))
                except Exception as e:
                    #self._log('DBG2: TZ change to UTC!!', severity='debug')
                    # createdAt is string
                    os.environ['TZ'] = 'UTC'
                    time.tzset()
                    p = '%Y-%m-%dT%H:%M:%S.%fZ'
                    d = data.get("createdAt")
                    creation_time = int(time.mktime(time.strptime(d, p)))
                    # Reset TZ to 'Asia/Ho_Chi_Minh'
                    os.environ['TZ'] = DEFAULT_TZ
                    time.tzset()
                side = data.get("side")
                stored_data = {
                        'order_status': order_status,
                        'pair': pair,
                        'accu_amount': accu_amount,
                        'avg_price': price,
                        'amount': amount,
                        'side': side,
                        'price': price,
                        'creation_time': creation_time,
                    }
                self.websocket_data['order_progress'][order_id] = stored_data
                self.append_update_time_ws_data(order_id)
                #self._log(f'Create new ws data, order id {order_id} : f{stored_data}')
    # END _order_progress_handler

    def register_order_progress(self, pair=None):
        self._ws_manager.subscribe_private(subscription="subscribeReports", params={}, callback=self._order_progress_handler)

    def unregister_order_progress(self, pair=None):
        self._ws_manager.unsubscribe(subscription="subscribeReports", params={})

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
        # payload msg is a dict ref at https://api.hitbtc.com/#subscribe-to-order-book
        # print('msg {}'.format(msg))
        if not isinstance(msg, dict):
            return
        if msg.get("method") != "snapshotOrderbook" and msg.get("method") != "updateOrderbook":
            return
        data = msg.get("params")
        ex_pair = data.get("symbol")
        if not data or not ex_pair:
            return
        coin2 = ex_pair[3:]
        if coin2 == 'USD':
            coin2 = 'USDT'
        pair = ex_pair[:3] + '/' + coin2
        self.__update_order_book(pair, 'asks', data.get('ask'), HIT_ORDER_BOOK_DEPTH_5)
        self.__update_order_book(pair, 'bids', data.get('bid'), HIT_ORDER_BOOK_DEPTH_5)
    # END _order_book_handler

    def _init_order_book(self, pair):
        order_books = self._rest_api.fetch_order_book(pair, HIT_ORDER_BOOK_DEPTH_5)
        if not order_books:
            return
        self.__update_order_book(pair, 'asks', order_books.get('asks'), HIT_ORDER_BOOK_DEPTH_5)
        self.__update_order_book(pair, 'bids', order_books.get('bids'), HIT_ORDER_BOOK_DEPTH_5)

    def register_order_book(self, pair):
        if pair not in self.websocket_data['order_book']:
            self.websocket_data['order_book'][pair] = {}
            self.websocket_data['order_book'][pair]['asks'] = {}
            self.websocket_data['order_book'][pair]['bids'] = {}
        self._init_order_book(pair)
        pair = pair.replace('USDT', 'USD')
        pair = pair.replace('/', '')
        params = {"symbol": pair}
        self._ws_manager.subscribe_public(subscription="subscribeOrderbook", params=params, callback=self._order_book_handler)

    def unregister_order_book(self, pair):
        pair = pair.replace('USDT', 'USD')
        pair = pair.replace('/', '')
        params = {"symbol": pair}
        self._ws_manager.unsubscribe(subscription="subscribeOrderbook", params=params)

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

    @exception_logging
    @on_message_handler()
    def _ticker_info_handler(self, msg):
        # print(msg)
        if not isinstance(msg, dict) or not msg.get("params"):
            return
        data = msg.get("params")
        ex_pair = data.get("symbol")
        if not data or not ex_pair:
            return
        coin2 = ex_pair[3:]
        if coin2 == 'USD':
            coin2 = 'USDT'
        pair = ex_pair[:3] + '/' + coin2
        self.websocket_data['ticker_info'][pair] = float(data.get('last'))
        # print(self.websocket_data['ticker_info'][pair])
    # END _ticker_info_handler

    @exception_logging
    def register_ticker_info(self, pair):
        if pair not in self.websocket_data['ticker_info']:
            self.websocket_data['ticker_info'][pair] = {}
        if pair == 'BTC/USDT':
            pair = pair.replace('BTC/USDT', 'BTC/USD')
        pair = pair.replace('/', '')
        params = {"symbol": pair}
        self._ws_manager.subscribe_public(subscription="subscribeTicker", params=params, callback=self._ticker_info_handler)

    def unregister_ticker_info(self, pair):
        if pair == 'BTC/USDT':
            pair = pair.replace('BTC/USDT', 'BTC/USD')
        pair = pair.replace('/', '')
        params = {"symbol": pair}
        self._ws_manager.unsubscribe(subscription="subscribeTicker", params=params)

    @exception_logging
    def fetch_ticker_price(self, pair):
        # print('fetch_ticker_price {} '.format(self.websocket_data['ticker_info']))
        return self.websocket_data['ticker_info'].get(pair)

    def __ohlcv_snapshot(self, pair, data):
        fm = '%Y-%m-%dT%H:%M:%S.%fZ'
        his_ohlcv = []
        runing_ohlcv = []
        for cdl in data:
            timestamp = cdl.get('timestamp')
            ts = int(time.mktime(time.strptime(timestamp, fm)) * 1000)
            ohlcv = [ts, float(cdl['open']), float(cdl['max']), float(cdl['min']), float(cdl['close']), float(cdl['volume'])]
            if cdl != data[-1]:
                his_ohlcv.append(ohlcv)
            else:
                runing_ohlcv.append(ohlcv)
        self.websocket_data['ohlcv'][pair]['data'] = his_ohlcv
        self.websocket_data['ohlcv'][pair]['running'] = runing_ohlcv

    @on_message_handler()
    def _ohlcv_handler(self, msg):
        if not isinstance(msg, dict):
            return
        if msg.get('method') not in ['snapshotCandles', 'updateCandles']:
            return
        ws_pair = msg.get('params', None).get('symbol')
        pair = self.websocket_data['ohlcv'][ws_pair]
        data = msg.get('params', None).get('data')
        if msg.get('method') == 'snapshotCandles':
            self.__ohlcv_snapshot(pair, data)
            return
        # Update payload
        cdl = data[-1]
        fm = '%Y-%m-%dT%H:%M:%S.%fZ'
        timestamp = cdl.get('timestamp')
        ts = int(time.mktime(time.strptime(timestamp, fm)) * 1000)
        running_ohlcv = [ts, float(cdl['open']), float(cdl['max']), float(cdl['min']), float(cdl['close']), float(cdl['volume'])]
        last_running_ohlcv = self.websocket_data['ohlcv'][pair]['running'][-1]
        if ts > last_running_ohlcv[0]:
            self.websocket_data['ohlcv'][pair]['data'].pop(0)
            self.websocket_data['ohlcv'][pair]['data'].append(last_running_ohlcv)
        if len(self.websocket_data['ohlcv'][pair]['running']) >= 2:
            self.websocket_data['ohlcv'][pair]['running'].pop(0)
        self.websocket_data['ohlcv'][pair]['running'].append(running_ohlcv)

    # See: https://github.com/hitbtc-com/hitbtc-api/blob/master/APIv2.md#candles
    def _cdl_interval_translate(self, interval_str='1m'):
        if interval_str == '1m':
            return 'M1'
        if interval_str == '3m':
            return 'M3'
        if interval_str == '5m':
            return 'M5'
        if interval_str == '15m':
            return 'M15'
        if interval_str == '30m':
            return 'M30'
        if interval_str == '1h':
            return 'H1'
        if interval_str == '4h':
            return 'H4'
        if interval_str == '1d':
            return 'D1'
        if interval_str == '1w':
            return 'D7'
        if interval_str == '1M':
            return '1M'
        return None

    def register_ohlcv(self, pair, interval_str='1m'):
        if pair not in self.websocket_data['ohlcv']:
            self.websocket_data['ohlcv'][pair] = {}
        self.websocket_data['ohlcv'][pair]['interval_str'] = interval_str
        ws_pair = pair.replace('BTC/USDT', 'BTC/USD')
        ws_pair = ws_pair.replace('/', '').upper()
        self.websocket_data['ohlcv'][ws_pair] = pair
        # intialize ohlcv data using rest api
        #try:
        #    initial_ohlcv = self._rest_api.fetch_ohlcv(pair, interval_str)
        #    self.websocket_data['ohlcv'][pair]['running'] = [initial_ohlcv[-1], ]
        #    self.websocket_data['ohlcv'][pair]['data'] = initial_ohlcv[-OHLCV_DEPTH-1:-1]
        #    print(self.websocket_data['ohlcv'][pair]['data'])
        #except:
        #    self.websocket_data['ohlcv'][pair]['data'] = []
        #    self.websocket_data['ohlcv'][pair]['running'] = []
        #    tb = traceback.format_exc()
        #    self._log(f'{tb}', severity='warning')
        interval = self._cdl_interval_translate(interval_str)
        params = {"symbol": ws_pair, "period": interval, "limit": OHLCV_DEPTH}
        self._ws_manager.subscribe_public(subscription="subscribeCandles", params=params, callback=self._ohlcv_handler)

    def unregister_ohlcv(self, pair, interval_str='1m'):
        ws_pair = pair.replace('BTC/USDT', 'BTC/USD')
        ws_pair = ws_pair.replace('/', '').upper()
        params = {"symbol": ws_pair}
        self._ws_manager.unsubscribe(subscription="subscribeCandles", params=params)

    @on_message_handler()
    def _create_order_handler(self, msg):
        if msg.get("result") == False:
            self._create_order_error = "WS ERROR"
            if self._create_order_lock.locked():
                self._create_order_lock.release()
        elif msg.get("error"):
            self._create_order_error = str(msg.get("error"))
            if self._create_order_lock.locked():
                self._create_order_lock.release()

        if isinstance(msg.get("result"), dict):
            # Created order successfully
            if self._create_order_lock.locked():
                self._create_order_lock.release()
    # END _create_order_handler

    def create_order(self, pair, type, side, amount, price, stopPrice=None):
        if pair in Hitbtc2.PAIR_MAPPER:
            pair = Hitbtc2.PAIR_MAPPER.get(pair)
        pair = pair.replace('/', '')
        if type == "stop_loss_limit":
            type = "stopLimit"
        order_id = binascii.b2a_hex(os.urandom(15)).decode('ascii')
        order_data = {
            "clientOrderId": order_id,
            "symbol": pair,
            "side": side,
            "type": type,
            "price": str(price),
            "quantity": str(amount),
            "postOnly": True,
        }
        if stopPrice:
            order_data.update({"stopPrice": stopPrice})
        # Lock self._creating_order_lock then waiting for create_order ws payload
        self._create_order_lock.acquire()
        self._create_order_info = {"id": order_id}
        self._ws_manager.subscribe_private(subscription="newOrder", params=order_data, callback=self._create_order_handler)
        # When ws payload is processed get error msg if any
        while self._create_order_lock.locked():
            time.sleep(0.2)

        if self._create_order_error:
            self._log(f'create order error: {self._create_order_error}', severity='error')
            self._create_order_error = ''
            return None
        else:
            return order_id
