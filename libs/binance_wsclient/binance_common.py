# coding=utf-8
import os
import sys
import json
import time
import traceback
import hashlib, hmac, requests
from urllib.parse import urljoin, urlencode

this_path = os.path.dirname(os.path.realpath(__file__))
lib_path = this_path + '/../'
sys.path.append(lib_path)
bots_path = lib_path + '/../bots/'
sys.path.append(bots_path)
from common import RepeatTimer, log2
from bot_constant import *
from wsclient_common import on_message_handler, \
                            CommonSocketManager

def get_listen_key(user_stream_api_url, api_key, secret_key=None, signed=False):
    params = {}
    if signed:
        if not secret_key:
            return None
        query_str = urlencode(params)
        params['signature'] = hmac.new(secret_key.encode('utf-8'), query_str.encode('utf-8'), hashlib.sha256).hexdigest()
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'X-MBX-APIKEY': api_key}
    res = requests.post(user_stream_api_url, headers=headers, params=params)
    if res.status_code == 200:
        return res.json().get('listenKey', None)
    return None

def get_exchange_info(ex_info_api_url):
    res = requests.get(ex_info_api_url)
    if res.status_code == 200:
        symbols = res.json().get('symbols')
        pair_dict = {}
        for symbol_info in symbols:
            pair = '/'.join([symbol_info['baseAsset'], symbol_info['quoteAsset']])
            ws_pair = ''.join([symbol_info['baseAsset'], symbol_info['quoteAsset']])
            ws_pair = ws_pair.lower()
            if not pair_dict.get(ws_pair):
                pair_dict[ws_pair] = {}
            pair_dict[ws_pair]['pair'] = pair.upper()
            # For Futures
            if symbol_info.get('contractType'):
                ct = symbol_info['contractType']
                # symbol: "BTCUSD_200925"
                _, pair_dict[ws_pair][ct] = symbol_info['symbol'].split('_')
        return pair_dict
    return None


class BinanceWssClientFactory(CommonSocketManager):
    """ Websocket client factory for BINANCE """
    #== TO BE OVERWRITEN ==#
    # Uses raw stream only
    BASE_RAW_STREAM_URL = ''
    # API to fetch exchange info
    EX_INFO_API_URL = ''
    # API to get listen key
    USER_STREAM_API_URL = ''
    #== TO BE OVERWRITEN ==#

    LISTEN_KEY_PING_INT = 30 * 60 # 30min in sec

    def __init__(self, key=None, secret=None, logger=None):  # client
        super().__init__()
        self._log = logger if logger else log2
        self._key = key
        #FIXME currently, we don't touch to the account (i.e. transfer),
        # so don't need to use secret api. Comment it for secure.
        #self._secret = secret
        self._usr_stream_timer = None
        self._usr_stream_listen_key = None
        self._usr_stream_callback = None

    def set_login_token(self, key, secret):
        self._key = key
        #self._secret = secret

    def subscribe_public(self, subscription, callback):
        id_ = subscription
        self.STREAM_URL = urljoin(self.BASE_RAW_STREAM_URL, subscription)
        return self._start_socket(id_, None, None, callback)

    def __user_stream_keepalive(self):
        listen_key = get_listen_key(self.USER_STREAM_API_URL, self._key)
        count = 0
        while not listen_key:
            # avoid rate-limit
            time.sleep(60)
            count += 1
            if count % 2 == 0:
                self._log(f'Keep-alive: cannot get_listen_key after {count}mins', severity='warning')
            listen_key = get_listen_key(self.USER_STREAM_API_URL, self._key)
        print('__user_stream_keepalive', listen_key)
        if listen_key != self._usr_stream_listen_key:
            self._log(f'new listenKey {listen_key}, restart user_stream socket', severity='debug')
            self._start_user_stream_socket(listen_key, self._usr_stream_callback)
            msg = json.dumps({'e': 'update_order_progress'}).encode('utf8')
            self._usr_stream_callback(msg)

    def __start_ustream_keepalive_timer(self):
        self._usr_stream_timer = RepeatTimer(self.LISTEN_KEY_PING_INT, self.__user_stream_keepalive)
        self._usr_stream_timer.setDaemon(True)
        self._usr_stream_timer.start()

    def __stop_ustream_keepalive_timer(self):
        if self._usr_stream_timer:
            self._usr_stream_timer.cancel()
            self._usr_stream_timer = None

    def __stop_user_stream_socket(self, listen_key):
        if listen_key in self._conns:
            self._stop_socket(listen_key)
        self._usr_stream_listen_key = None
        self.__stop_ustream_keepalive_timer()

    def _start_user_stream_socket(self, listen_key, callback):
        # stop previous listenkey connection
        self.__stop_user_stream_socket(self._usr_stream_listen_key)
        self._usr_stream_listen_key = listen_key
        self._usr_stream_callback = callback
        self.STREAM_URL = urljoin(self.BASE_RAW_STREAM_URL, listen_key)
        id_ = listen_key
        conn_key = self._start_socket(id_, None, None, callback)
        if conn_key:
            # start timer to keep socket alive
            self.__start_ustream_keepalive_timer()
        return conn_key

    def subscribe_private(self, subscription=None, callback=None):
        listen_key = get_listen_key(self.USER_STREAM_API_URL, self._key)
        # Dont waste time to register an existing socket
        if listen_key in self._conns:
            return
        return self._start_user_stream_socket(listen_key, callback)

    def unsubscribe(self, subscription=None):
        if not subscription:
            self.__stop_user_stream_socket(self._usr_stream_listen_key)
        else:
            self._stop_socket(subscription)


#TODO need to check Binance docs regularly
# for further API URL changes.
# https://binance-docs.github.io/apidocs/spot/en/#change-log
class BinanceUrls:
    # SPOT
    SPOT_BASE_RAW_STREAM_URL = 'wss://stream.binance.com:9443/ws/'
    SPOT_API_URL = 'https://api.binance.com/'
    SPOT_EX_INFO_API_URL = urljoin(SPOT_API_URL, '/api/v3/exchangeInfo')
    SPOT_USER_STREAM_API_URL = urljoin(SPOT_API_URL, '/api/v3/userDataStream')
    # MARGIN
    MARGIN_BASE_RAW_STREAM_URL = SPOT_BASE_RAW_STREAM_URL
    MARGIN_API_URL = SPOT_API_URL
    MARGIN_EX_INFO_API_URL = SPOT_EX_INFO_API_URL
    MARGIN_USER_STREAM_API_URL = urljoin(MARGIN_API_URL, '/sapi/v1/userDataStream')
    # USDT-Futures
    FUTURES_BASE_RAW_STREAM_URL = 'wss://fstream.binance.com/ws/'
    FUTURES_API_URL = 'https://fapi.binance.com/'
    FUTURES_EX_INFO_API_URL = urljoin(FUTURES_API_URL, '/fapi/v1/exchangeInfo')
    FUTURES_USER_STREAM_API_URL = urljoin(FUTURES_API_URL, '/fapi/v1/listenKey')
    # COIN-Futures
    DELIVERY_BASE_RAW_STREAM_URL = 'wss://dstream.binance.com/ws/'
    DELIVERY_API_URL = 'https://dapi.binance.com/'
    DELIVERY_EX_INFO_API_URL = urljoin(DELIVERY_API_URL, '/dapi/v1/exchangeInfo')
    DELIVERY_USER_STREAM_API_URL = urljoin(DELIVERY_API_URL, '/dapi/v1/listenKey')

class BinanceSpotWssClient(BinanceWssClientFactory):
    """ Websocket client for BINANCE SPOT """
    BASE_RAW_STREAM_URL = BinanceUrls.SPOT_BASE_RAW_STREAM_URL
    EX_INFO_API_URL = BinanceUrls.SPOT_EX_INFO_API_URL
    USER_STREAM_API_URL = BinanceUrls.SPOT_USER_STREAM_API_URL

class BinanceMarginWssClient(BinanceWssClientFactory):
    """ Websocket client for BINANCE MARGIN """
    BASE_RAW_STREAM_URL = BinanceUrls.MARGIN_BASE_RAW_STREAM_URL
    EX_INFO_API_URL = BinanceUrls.MARGIN_EX_INFO_API_URL
    USER_STREAM_API_URL = BinanceUrls.MARGIN_USER_STREAM_API_URL

class BinanceUsdtFuturesWssClient(BinanceWssClientFactory):
    """ Websocket client for BINANCE USDT-Futures """
    BASE_RAW_STREAM_URL = BinanceUrls.FUTURES_BASE_RAW_STREAM_URL
    EX_INFO_API_URL = BinanceUrls.FUTURES_EX_INFO_API_URL
    USER_STREAM_API_URL = BinanceUrls.FUTURES_USER_STREAM_API_URL

class BinanceCoinFuturesWssClient(BinanceWssClientFactory):
    """ Websocket client for BINANCE COIN-Futures """
    BASE_RAW_STREAM_URL = BinanceUrls.DELIVERY_BASE_RAW_STREAM_URL
    EX_INFO_API_URL = BinanceUrls.DELIVERY_EX_INFO_API_URL
    USER_STREAM_API_URL = BinanceUrls.DELIVERY_USER_STREAM_API_URL


class BinanceCommon:
    """ Common high-level library for BINANCE """
    ORDER_BOOK_DEPTH_5 = 5
    ORDER_BOOK_DEPTH_10 = 10
    ORDER_BOOK_DEPTH_20 = 20
    ORDER_BOOK_DEPTH_50 = 50
    ORDER_BOOK_DEPTH_100 = 100
    ORDER_BOOK_DEPTH_500 = 500
    ORDER_BOOK_DEPTH_1000 = 1000
    ORDER_BOOK_DEPTH_5000 = 5000
    OHLCV_DEPTH = 100

    def __init__(self, rest_api, ws_manager, logger, *args, **kwargs):
        self._log = logger if logger else log2
        self._rest_api = rest_api

        self._ws_manager = ws_manager
        self._ws_manager.start()

        self._pair_dict = get_exchange_info(self._ws_manager.EX_INFO_API_URL)
        self.websocket_data = {}
        self.websocket_data['order_progress'] = {}
        self.websocket_data['order_book'] = {}
        self.websocket_data['book_ticker'] = {}
        self.websocket_data['ohlcv'] = {}
        self.websocket_data['balances'] = {}
        self.websocket_data['ticker_info'] = {}
        self.websocket_data['trade'] = {}
        self.vol_ask_count = 0
        self.vol_bid_count = 0
        self.order_progress_pairs = []

    def set_restapi(self, rest_api):
        self._rest_api = rest_api

    def set_login_token(self, key, secret):
        self._ws_manager.set_login_token(key, secret)

    def get_symbol_from_pair(self, pair, stream_symbol=True):
        #TODO overrided by a specific implementation
        pass

    def get_pair_from_symbol(self, symbol):
        ws_pair = symbol.split('_')[0].lower()
        return self._pair_dict.get(ws_pair, {}).get('pair', '')

    def _restapi_call_on_pair(self, restapi_func, pair, *args, **kwargs):
        symbol = self.get_symbol_from_pair(pair, stream_symbol=False)
        return restapi_func(symbol, *args, **kwargs)

    @on_message_handler()
    def _user_stream_handler(self, msg):
        #TODO overrided by a specific implementation
        pass
    # END _user_stream_handler

    # Binance only uses one user_stream for spot/margin acount and order update
    def register_order_progress(self, pair=None):
        # Initial balances
        balances = self._rest_api.fetch_balance()
        for coin in balances:
            if balances[coin].get('total'):
                self.websocket_data['balances'][coin] = balances[coin]
        if pair:
            if pair not in self.order_progress_pairs:
                self.order_progress_pairs.append(pair)
            self.update_order_progress(pair)
        self._ws_manager.subscribe_private(subscription=None, callback=self._user_stream_handler)

    def unregister_order_progress(self, pair=None):
        self._ws_manager.unsubscribe(subscription=None)

    def update_order_progress(self, pair):
        symbol = self.get_symbol_from_pair(pair, stream_symbol=False)
        update_ws_order_progress_helper(self._rest_api, symbol, pair, self.websocket_data[WS_DATA.ORDER_PROGRESS])

    def fetch_balance(self, coin=''):
        if coin:
            return self.websocket_data['balances'].get(coin)
        else:
            return self.websocket_data['balances']

    def _update_order_book(self, pair, side, data, depth):
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
        #TODO overrided by a specific implementation
        pass
    # END _order_book_handler

    def _init_order_book(self, pair):
        depth = self.websocket_data['order_book'][pair]['depth']
        order_books = self._restapi_call_on_pair(self._rest_api.fetch_order_book, pair, depth)
        self.websocket_data['order_book'][pair]['lastUpdateId'] = int(order_books.get('nonce'))
        self.websocket_data['order_book'][pair]['nonce'] = 0
        self.websocket_data['order_book'][pair]['asks'] = {}
        self._update_order_book(pair, 'asks', order_books.get('asks'), depth)
        self.websocket_data['order_book'][pair]['bids'] = {}
        self._update_order_book(pair, 'bids', order_books.get('bids'), depth)

    def register_order_book(self, pair, depth=ORDER_BOOK_DEPTH_5):
        if pair not in self.websocket_data['order_book']:
            self.websocket_data['order_book'][pair] = {}
            self.websocket_data['order_book'][pair]['depth'] = depth

        # For trade volume
        self.vol_ask_count = 0
        self.vol_bid_count = 0

        # Initialize order_book using rest api
        self._init_order_book(pair)

        symbol = self.get_symbol_from_pair(pair)
        stream_name = f'{symbol}@depth@100ms'
        self._ws_manager.subscribe_public(subscription=stream_name, callback=self._order_book_handler)

    def unregister_order_book(self, pair):
        symbol = self.get_symbol_from_pair(pair)
        stream_name = f'{symbol}@depth@100ms'
        self._ws_manager.unsubscribe(subscription=stream_name)

    def fetch_trade_volume(self, pair, _reset_counter=False):
        vol_ask = self.vol_ask_count
        vol_bid = self.vol_bid_count
        if _reset_counter:
            self.vol_ask_count = 0
            self.vol_bid_count = 0
        return vol_ask, vol_bid

    def fetch_order_book(self, pair, index=None):
        try:
            if index == 1 and pair in self.websocket_data['book_ticker']:
                return self._fetch_best_ask_bid(pair)
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
        if not isinstance(msg, dict):
            return
        if msg.get('c'):
            ws_pair = msg.get('s').lower()
            pair = self.get_pair_from_symbol(ws_pair)
            self.websocket_data['ticker_info'][pair] = float(msg.get('c'))
    # END _ticker_info_handler

    def register_ticker_info(self, pair):
        if pair not in self.websocket_data['ticker_info']:
            self.websocket_data['ticker_info'][pair] = 0.0
        symbol = self.get_symbol_from_pair(pair)
        stream_name = f'{symbol}@ticker'
        self._ws_manager.subscribe_public(subscription=stream_name, callback=self._ticker_info_handler)

    def unregister_ticker_info(self, pair):
        symbol = self.get_symbol_from_pair(pair)
        stream_name = f'{symbol}@ticker'
        self._ws_manager.unsubscribe(subscription=stream_name)

    def fetch_ticker_price(self, pair):
        return self.websocket_data['ticker_info'].get(pair)

    @on_message_handler()
    def _ohlcv_handler(self, msg):
        pair = ''
        if not isinstance(msg, dict):
            return
        if msg.get('e') != 'kline':
            return
        ws_pair = msg.get('s').lower()
        pair = self.get_pair_from_symbol(ws_pair)
        if not pair:
            return
        ohlcv_data = msg.get('k')
        time_event = int(float(msg.get('E')))
        start_interval = int(float(ohlcv_data.get('t'))) # msec
        end_interval = int(float(ohlcv_data.get('T'))) # msec
        open_price = float(ohlcv_data.get('o'))
        highest_price = float(ohlcv_data.get('h'))
        lowest_price = float(ohlcv_data.get('l'))
        close_price = float(ohlcv_data.get('c'))
        volume = float(ohlcv_data.get('v'))
        #print('\n', time_event, end_interval, time_event > end_interval)

        current_cdl = [time_event, open_price, highest_price, lowest_price, close_price, volume, start_interval, end_interval]
        if self.websocket_data['ohlcv'][pair].get('running'):
            # Get newest saved running candle
            newest_running_cdl = self.websocket_data['ohlcv'][pair]['running'][-1]
            # update the running candle list
            if len(self.websocket_data['ohlcv'][pair]['running']) >= 5:
                self.websocket_data['ohlcv'][pair]['running'].pop(0)
            # In Binance, final running candle has 'time_event' greater than its end_interval
            # If we receive that final event, we can fetch the next running candle from trade stream
            if time_event >= end_interval and self.websocket_data['ohlcv'][pair]['is_real_time']:
                #print('last hcdl', self.websocket_data['ohlcv'][pair]['data'][-1])
                #print(current_cdl)
                next_start_interval = end_interval + 1
                next_start_interval = int(next_start_interval / 1000)
                # FIXME Workaround:
                # Somehow we can miss new trade event (for new running candle), check it several times
                retry = 3
                while not self.websocket_data['trade'][pair].get(next_start_interval) and retry > 0:
                    time.sleep(0.2)
                    retry -= 1
                    #if retry == 0:
                    #    print(self.websocket_data['trade'][pair])
                if self.websocket_data['trade'][pair].get(next_start_interval):
                    rt_cdl = self.websocket_data['trade'][pair].get(next_start_interval)
                    price = rt_cdl['price']
                    # FIXME TRICK build a running cdl with length=6 like cdl from rest_api
                    rt_current_cdl = [rt_cdl['time_event'], price, price, price, price, rt_cdl['vol']]
                    if len(newest_running_cdl) < 7:
                        # remove the oldest candle
                        self.websocket_data['ohlcv'][pair]['data'].pop(0)
                        interval_str = self.websocket_data['ohlcv'][pair]['interval_str']
                        symbol = self.get_symbol_from_pair(pair, False)
                        last_historical_candle = self._restapi_call_on_pair(self._rest_api.fetch_ohlcv, pair, interval_str)[-2]
                        # add a new one, the most recent candle last
                        self.websocket_data['ohlcv'][pair]['data'].append(last_historical_candle)
                    else:
                        if len(self.websocket_data['ohlcv'][pair]['data']) >= self.OHLCV_DEPTH:
                            self.websocket_data['ohlcv'][pair]['data'].pop(0)
                        # the most recent candle last
                        self.websocket_data['ohlcv'][pair]['data'].append(current_cdl)
                    #print('realtime', self.websocket_data['ohlcv'][pair]['data'][-1])
                    self.websocket_data['ohlcv'][pair]['running'].append(rt_current_cdl)
                    #print(self.websocket_data['ohlcv'][pair]['running'][-1])
                    return
            self.websocket_data['ohlcv'][pair]['running'].append(current_cdl)
            # Check if the newest saved running candle becomes old.
            # We must firstly check if stored ohlcv data is just initalized by restapi or not.
            # If yes (restapi data only have 6 elements [time_event, o, h, l, v] in a rank),
            #   get saved time_event, otherwise, get saved end_interval,
            # then compare to start_interval of current_candle.
            if len(newest_running_cdl) < 7:
                saved_time_event = newest_running_cdl[0]
                if saved_time_event < start_interval:
                    # remove the oldest candle
                    self.websocket_data['ohlcv'][pair]['data'].pop(0)
                    interval_str = self.websocket_data['ohlcv'][pair]['interval_str']
                    last_historical_candle = self._restapi_call_on_pair(self._rest_api.fetch_ohlcv, pair, interval_str)[-2]
                    # add a new one, the most recent candle last
                    self.websocket_data['ohlcv'][pair]['data'].append(last_historical_candle)
                    #print('rcdl', current_cdl)
                    #print('normal1', self.websocket_data['ohlcv'][pair]['data'][-1])
            else:
                saved_end_interval = newest_running_cdl[-1]
                # Check if the saved runtime candle becomes old
                # WARN: somehow on Binance, time_event is out of [start_interval, end_interval].
                #   Don't compare to time_event.
                if saved_end_interval < start_interval:
                    if len(self.websocket_data['ohlcv'][pair]['data']) >= self.OHLCV_DEPTH:
                        self.websocket_data['ohlcv'][pair]['data'].pop(0)
                    # the most recent candle last
                    self.websocket_data['ohlcv'][pair]['data'].append(newest_running_cdl)
                    #print('rcdl', current_cdl)
                    #print('normal2', self.websocket_data['ohlcv'][pair]['data'][-1])
        else:
            # In case of fetch_ohlcv restapi failure
            self.websocket_data['ohlcv'][pair]['running'] = [current_cdl, ]
            self.websocket_data['ohlcv'][pair]['data'] = []
    # END _ohlcv_handler

    def register_ohlcv(self, pair, interval_str='1m', real_time=False):
        if pair not in self.websocket_data['ohlcv']:
            self.websocket_data['ohlcv'][pair] = {}
        self.websocket_data['ohlcv'][pair]['interval_str'] = interval_str
        self.websocket_data['ohlcv'][pair]['is_real_time'] = real_time
        # intialize ohlcv data using rest api
        try:
            initial_ohlcv = self._restapi_call_on_pair(self._rest_api.fetch_ohlcv, pair, interval_str)
        except:
            tb = traceback.format_exc()
            self._log(f'{tb}', severity='warning')
            initial_ohlcv = None
        if initial_ohlcv:
            self.websocket_data['ohlcv'][pair]['running'] = [initial_ohlcv[-1], ]
            self.websocket_data['ohlcv'][pair]['data'] = initial_ohlcv[-self.OHLCV_DEPTH-1:-1]

        if real_time:
            self.register_trade_stream(pair)

        symbol = self.get_symbol_from_pair(pair)
        stream_name = f'{symbol}@kline_{interval_str}'
        self._ws_manager.subscribe_public(subscription=stream_name, callback=self._ohlcv_handler)

    def unregister_ohlcv(self, pair, interval_str='1m', real_time=False):
        symbol = self.get_symbol_from_pair(pair)
        stream_name = f'{symbol}@kline_{interval_str}'
        self._ws_manager.unsubscribe(subscription=stream_name)

    #FIXME keep this func for register_ohlcv realtime=True
    def register_trade_stream(self, pair):
        #TODO overrided by SPOT/MARGIN
        pass

    def fetch_trade_stream(self, pair, _reset_counter=False, index=None):
        try:
            buys = self.websocket_data['trade'][pair].get('buy').copy()
            sells = self.websocket_data['trade'][pair].get('sell').copy()
            buy = sorted(buys.items())
            sell = sorted(sells.items())
        except:
            tb = traceback.format_exc()
            self._log(f'{tb}', severity='warning')
            return None, None
        if _reset_counter:
            self.websocket_data['trade'][pair]['buy'] = {}
            self.websocket_data['trade'][pair]['sell'] = {}
        if buy and sell:
            if index:
                return buy[index], sell[index]
            else:
                return buy, sell
        else:
            return None, None

    @on_message_handler()
    def _individual_book_ticker_handler(self, msg):
        if not isinstance(msg, dict):
            return
        if not msg.get('u'):
            return
        ws_pair = msg.get('s').lower()
        pair = self.get_pair_from_symbol(ws_pair)
        if pair not in self.websocket_data['book_ticker']:
            return
        if msg.get('a'):
            self.websocket_data['book_ticker'][pair]['ask'] = float(msg.get('a'))
        if msg.get('A'):
            self.websocket_data['book_ticker'][pair]['ask_volume'] = float(msg.get('A'))
        if msg.get('b'):
            self.websocket_data['book_ticker'][pair]['bid'] = float(msg.get('b'))
        if msg.get('B'):
            self.websocket_data['book_ticker'][pair]['bid_volume'] = float(msg.get('B'))

    def register_book_ticker(self, pair):
        if pair not in self.websocket_data['book_ticker']:
            self.websocket_data['book_ticker'][pair] = {}
            self.websocket_data['book_ticker'][pair]['ask'] = 0.0
            self.websocket_data['book_ticker'][pair]['ask_volume'] = 0.0
            self.websocket_data['book_ticker'][pair]['bid'] = 0.0
            self.websocket_data['book_ticker'][pair]['bid_volume'] = 0.0
        symbol = self.get_symbol_from_pair(pair)
        stream_name = f'{symbol}@bookTicker'
        self._ws_manager.subscribe_public(subscription=stream_name, callback=self._individual_book_ticker_handler)

    def unregister_book_ticker(self, pair):
        symbol = self.get_symbol_from_pair(pair)
        stream_name = f'{symbol}@bookTicker'
        self._ws_manager.unsubscribe(subscription=stream_name)

    def _fetch_best_ask_bid(self, pair):
        if pair not in self.websocket_data['book_ticker']:
            return None, None
        ask = self.websocket_data['book_ticker'][pair]['ask']
        ask_volume = self.websocket_data['book_ticker'][pair]['ask_volume']
        bid = self.websocket_data['book_ticker'][pair]['bid']
        bid_volume = self.websocket_data['book_ticker'][pair]['bid_volume']
        return (ask, ask_volume), (bid, bid_volume)

    @on_message_handler()
    def _aggre_trade_stream_handler(self, msg):
        print(msg)

    def register_aggregate_trade_stream(self, pair):
        if pair not in self.websocket_data['trade']:
            self.websocket_data['trade'][pair] = {}
        symbol = self.get_symbol_from_pair(pair)
        stream_name = f'{symbol}@aggTrade'
        self._ws_manager.subscribe_public(subscription=stream_name, callback=self._aggre_trade_stream_handler)

    def unregister_aggregate_trade_stream(self, pair):
        symbol = self.get_symbol_from_pair(pair)
        stream_name = f'{symbol}@aggTrade'
        self._ws_manager.unsubscribe(subscription=stream_name)
