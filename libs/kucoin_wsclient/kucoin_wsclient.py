import os
import sys
import time, urllib.request, json
#import asyncio
import traceback
from decimal import Decimal
import uuid

this_path = os.path.dirname(os.path.realpath(__file__))
lib_path = this_path + '/../'
kucoin3pp_path = this_path + '/kucoin_3pp/'
sys.path.append(lib_path)
sys.path.append(kucoin3pp_path)
from client import Client
from common import log2
from wsclient_common import on_message_handler, \
                            CommonSocketManager

KC_ORDER_BOOK_DEPTH = 200
OHLCV_DEPTH = 100

class KucoinWssClient(CommonSocketManager):
    PUBLIC_URL = 'wss://push-private.kucoin.com/endpoint?token='
    PRIVATE_URL = ''
    API_URL = "https://api.kucoin.com/api/v1/bullet-public"

    def __init__(self, key=None, secret=None, passphrase=None):  # client
        super().__init__()
        self.__key = key
        self.__secret = secret
        self.__passphrase = passphrase

    def set_login_token(self, key, secret, passphrase):
        self.__key = key
        self.__secret = secret
        self.__passphrase = passphrase

    # Getting token from rest api
    def _get_token(self):
        api_nonce = bytes(str(int(time.time()*1000)), 'utf-8')
        api_request = urllib.request.Request(self.API_URL, b'nonce=%s' % api_nonce)
        return json.loads(urllib.request.urlopen(api_request).read().decode('utf-8')).get('data', {}).get('token', '')

    def subscribe_public(self, subscription, callback):
        id_ = str(uuid.uuid4())[::5]
        data = {
            "id": id_ ,
            "type": "subscribe",
            "topic": subscription,
            "response": True
        }
        endpoint = self._get_token()
        self.STREAM_URL = self.PUBLIC_URL + endpoint
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        return self._start_socket(id_, payload, None, callback)


class Kucoin:
    def __init__(self, key=None, secret=None, passphrase=None, logger=None, rest_api=None):
        self._log = logger if logger else log2
        self._rest_api = rest_api
        self._ws_manager = KucoinWssClient(key, secret, passphrase)
        self._ws_manager.start()
        self.websocket_data = {}
        self.websocket_data['order_progress'] = {}
        self.websocket_data['order_book'] = {}
        self.websocket_data['balances'] = {}
        self.websocket_data['ohlcv'] = {}
        self.websocket_data['ticker_info'] = {}
        self._client = Client(key, secret, passphrase)
        self.list_order_id = []

    def set_restapi(self, rest_api):
        self._rest_api = rest_api

    def set_login_token(self, key, secret, passphrase):
        self._ws_manager.set_login_token(key, secret, passphrase)

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
        # data: { "changes":{"asks":[["6","1","1545896669105"]],
        #                    "bids":[["4","1","1545896669106"]]},
        #         "symbol":"BTC-USDT",...}
        if not isinstance(msg, dict) or not msg.get('data'):
            return
        pair =  msg['data'].get('symbol').replace('-', '/')
        asks = msg['data']['changes'].get('asks')
        bids = msg['data']['changes'].get('bids')
        if len(asks) > 0:
            self.__update_order_book(pair, 'asks', asks, KC_ORDER_BOOK_DEPTH)
        if len(bids) > 0:
            self.__update_order_book(pair, 'bids', bids, KC_ORDER_BOOK_DEPTH)

    def register_order_book(self, pair):
        # new_loop = asyncio.new_event_loop()
        # options = {}
        # options['pair'] = pair
        if self.websocket_data['order_book'].get(pair):
            return
        self.websocket_data['order_book'][pair] = {}
        self.websocket_data['order_book'][pair]['asks'] = {}
        self.websocket_data['order_book'][pair]['bids'] = {}
        stream_name = "/market/level2:" + pair.replace('/','-')
        #print(stream_name)
        self._ws_manager.subscribe_public(subscription=stream_name, callback=self._order_book_handler)

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
                return asks[index], bids[index]
            else:
                return asks, bids
        else:
            return None, None
    # END _order_book process

    # START _ticker_info process
    @on_message_handler()
    def _ticker_info_handler(self, msg):
        if not isinstance(msg, dict) or not msg.get('data'):
            return
        pair = msg.get('topic')
        pair = pair.split(':')[-1].replace('-', '/')
        price = msg['data'].get('price')
        self.websocket_data['ticker_info'][pair] = price

    def register_ticker_info(self, pair):
        if self.websocket_data['ticker_info'].get(pair):
            return
        self.websocket_data['ticker_info'][pair] = {}
        stream_name = "/market/ticker:" + pair.replace('/','-')
        self._ws_manager.subscribe_public(subscription=stream_name, callback=self._ticker_info_handler)

    def fetch_ticker_price(self, pair):
        return self.websocket_data['ticker_info'].get(pair)
    # END _ticker_info process

    # START _order_progress process
    @on_message_handler()
    def _order_progress_handler(self, msg):
        print(msg)
        if not isinstance(msg, dict) or not msg.get('data'):
            return
        data = msg.get("data")
        # new order
        # if data.get('type') == 'done' and data.get('orderId') in self.list_order_id:
            # order_id = data.get('orderId')
            # order_status = data.get('reason')
            # pair = data.get('symbol').replace('-', '/')
            # side = data.get('side')
            # creation_time = data.get('time')
            # if order_status == 'filled':
            #     order_status = 'closed'
            # elif order_status == 'canceled':
            #     amount = float(data.get('size'))
        if data.get('type') == 'match' and data.get('tradeId') in self.list_order_id:
            order_id = data.get('tradeId') #FIXME
            order_status = 'open'
            pair = data.get('symbol').replace('-', '/')
            side = data.get('side')
            creation_time = int(data.get('time'))/1000 #ms
            price = float(data.get('price'))
            amount = float(data.get('size'))

            stored_data = {
                    'order_status': order_status,
                    'pair': pair,
                    'accu_amount': amount,
                    'avg_price': price,
                    'amount': amount,
                    'side': side,
                    'price': price,
                    'creation_time': creation_time,
                }
            # missing order_id
            self.websocket_data['order_progress'][order_id] = stored_data
        # update order_progress
        elif data.get('type') == 'change' and data.get('orderId') in self.list_order_id:
            pair = data.get('symbol').replace('-', '/')
            order_id = data.get('orderId')
            order_status = 'open'
            side = data.get('side')
            amount= data.get('amount')
            price = float(data.get('price'))
            creation_time = data.get('time')
            #FIXME
            accu_amount = float(Decimal(str(data.get('oldSize'))) - Decimal(str(data.get('newSize'))))
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
            # missing amount 
            self.websocket_data['order_progress'][order_id] = stored_data

    def register_order_progress(self, pair=None):
        if self.websocket_data['order_progress'].get(pair):
            return
        stream_name = "/market/level3:" + pair.replace('/','-')
        self._ws_manager.subscribe_public(subscription=stream_name, callback=self._order_progress_handler)

    def fetch_order_progress(self, order_id):
        return self.websocket_data['order_progress'].get(order_id)
    # END _order_progress process

    # START _ohclv_progress process
    @on_message_handler()
    def _ohlcv_handler(self, msg):
        if not isinstance(msg, dict) or not msg.get('data'):
            return
        # new msg is new trade
        data = msg.get('data')
        pair = data.get('symbol').replace('-','/')
        _time = int(int(data.get('time'))/1000000000)
        _price = float(data.get('price'))
        _vol = float(data.get('size'))

        last_running_ohlcv = self.websocket_data['ohlcv'][pair]['running'][-1]
        last_ohlcv = self.websocket_data['ohlcv'][pair]['data'][-1]
        open_price = last_running_ohlcv[1]
        high_price = max(float(last_running_ohlcv[2]), _price)
        low_price = min(float(last_running_ohlcv[3]), _price)
        close_price = _price
        volume = float(Decimal(str(last_running_ohlcv[5])) + Decimal(str(_vol)))
        time_next = int(int(last_ohlcv[0]) + self.ohlcv_inv*60) # next candle
        running_ohlcv = [time_next, open_price, high_price, low_price, close_price, volume]

        if _time > time_next:
            print(_time, running_ohlcv)
            self.websocket_data['ohlcv'][pair]['data'].pop(0)
            self.websocket_data['ohlcv'][pair]['data'].append(last_running_ohlcv)
            running_ohlcv = [(int(last_ohlcv[0]) + self.ohlcv_inv*60*2), _price, _price, _price, _price, _vol]
        if len(self.websocket_data['ohlcv'][pair]['running']) >= 2:
            self.websocket_data['ohlcv'][pair]['running'].pop(0)

        self.websocket_data['ohlcv'][pair]['running'].append(running_ohlcv)

    def register_ohlcv(self, pair, interval_str='1m', real_time=False):
        symbol = pair.replace('/','-')
        if 'm' in interval_str:
            interval = interval_str.replace('m','min')
            # self.ohlcv_inv is num of minute
            self.ohlcv_inv = int(interval_str.replace('m',''))
        elif 'h' in interval_str:
            interval = interval_str.replace('h','hour')
            self.ohlcv_inv = int(interval_str.replace('h',''))*60
        elif 'w' in interval_str:
            interval = interval_str.replace('w','week')
            self.ohlcv_inv = int(interval_str.replace('w',''))*60*24*7
        print("self.ohlcv_inv: ", self.ohlcv_inv)

        if self.websocket_data['ohlcv'].get(pair):
            return
        self.websocket_data['ohlcv'][pair] = {}
        self.websocket_data['ohlcv'][pair]['interval_str'] = interval_str
        self.websocket_data['ohlcv'][pair]['is_real_time'] = real_time
        # intialize ohlcv data using rest api
        try:
            # initial_ohlcv = self._rest_api.fetch_ohlcv(pair, interval_str)
            _ohlcv = self._client.get_kline_data(symbol, kline_type=interval)
            initial_ohlcv = []
            # fetch api have [0] is latest value
            for item in reversed(_ohlcv):
                tmp_array = [item[0], item[1], item[3], item[4], item[2], item[5]]
                initial_ohlcv.append(tmp_array)
            self.websocket_data['ohlcv'][pair]['running'] = [initial_ohlcv[-1],]
            self.websocket_data['ohlcv'][pair]['data'] = initial_ohlcv[-OHLCV_DEPTH-1:-1]
            print(self.websocket_data['ohlcv'][pair]['data'][0])
            print(self.websocket_data['ohlcv'][pair]['data'][-1])
            print(self.websocket_data['ohlcv'][pair]['running'])

        except:
            self.websocket_data['ohlcv'][pair]['data'] = []
            self.websocket_data['ohlcv'][pair]['running'] = []
            tb = traceback.format_exc()
            self._log(f'{tb}', severity='warning')
        stream_name = "/market/match:" + pair.replace('/','-')
        self._ws_manager.subscribe_public(subscription=stream_name, callback=self._ohlcv_handler)
    # END _ohclv_progress process

if __name__ == "__main__":
    a = Kucoin()
    a.register_order_book('ETH/BTC')
    # a.register_order_book('BTC/USDT')
    a.register_ticker_info('ETH/BTC')
    a.register_ohlcv('ETH/BTC')
    # a.register_order_progress('BTC/USDT')
    # a.register_ohlcv('BTC/USDT', '3m')
    time.sleep(10)
    print(a.fetch_ohlcv('ETH/BTC'))
    print(a.fetch_ticker_price('ETH/BTC'))
    print(a.fetch_order_book('ETH/BTC'))
    # print(a.fetch_order_book('ETH/BTC', index=-1))
    os._exit(0)
