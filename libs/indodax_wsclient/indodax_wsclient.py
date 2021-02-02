# coding=utf-8
import os
import sys
import json
import zlib
import time
import traceback
from functools import wraps

this_path = os.path.dirname(os.path.realpath(__file__))
exlib_path = this_path + '/../'
sys.path.append(exlib_path)
from wsclient_common import CommonSocketManager

def on_message_handler():
    def decorator(func):
        @wraps(func)
        def func_wrapper(self, payload, isBinary):
            if not isBinary:
                try:
                    msg = json.loads(payload.decode('utf-8'))
                except ValueError:
                    pass
                else:
                    func(self, msg)
        return func_wrapper
    return decorator

class IndodaxWssClient(CommonSocketManager):
    """ Websocket client for INDODAX """
    #FIXME
    STREAM_URL = 'wss://kline.indodax.com/ws/'

    def __init__(self, key=None, secret=None):  # client
        super().__init__()
        self.__key = key
        self.__secret = secret

    def set_login_token(self, key, secret):
        self.__key = key
        self.__secret = secret

    def subscribe_public(self, subscription, callback):
        id_ = subscription
        data = {'sub': subscription, 'id': '1'}
        payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
        return self._start_socket(id_, payload, None, callback)

    def subscribe_private(self, subscription, callback):
        #TODO
        pass

    def unsubscribe(self):
        pass

class Indodax:
    """ High-level library INDODAX """
    def __init__(self, key=None, secret=None, passphrase=None, logger=None, rest_api=None):
        self._logger = logger if logger else print
        self._ws_manager = IndodaxWssClient(key, secret)
        self._ws_manager.start()
        self._rest_api = rest_api
        self.websocket_data = {}
        self.websocket_data['ohlcv'] = {}

    def set_restapi(self, rest_api):
        self._rest_api = rest_api

    def set_login_token(self, key, secret, passphrase):
        self._ws_manager.set_login_token(key, secret, passphrase)

    @on_message_handler()
    def _order_progress_handler(self, msg):
        #TODO
        pass
    # END _order_progress_handler

    def register_order_progress(self, pair):
        self._logger('Not supported yet')
        #TODO
        return

    def fetch_order_progress(self, order_id):
        self._logger('Not supported yet')
        #TODO
        return

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
        self._logger('Not supported yet')
        #TODO
        return

    def fetch_order_book(self, pair, index=None):
        self._logger('Not supported yet')
        #TODO
        return
        try:
            copy_of_order_book_asks = self.websocket_data['order_book'][pair].get('asks').copy()
            copy_of_order_book_bids = self.websocket_data['order_book'][pair].get('bids').copy()
            asks = sorted(copy_of_order_book_asks.items())
            bids = sorted(copy_of_order_book_bids.items(), reverse=True)
        except:
            tb = traceback.format_exc()
            self._logger('{}'.format(tb))
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
        self._logger('Not supported yet')
        #TODO
        return

    def fetch_ticker_price(self, pair):
        self._logger('Not supported yet')
        #TODO
        return

    @on_message_handler()
    def _ohlcv_handler(self, msg):
        print(msg)
        return
        if not isinstance(msg, dict):
            return
        ohlcv_data = msg.get('tick')
        if not ohlcv_data:
            return
        ws_pair = ohlcv_data.get('pair')
        ws_ohlcv_data = self.websocket_data['ohlcv'].copy()
        pair = ''
        for p in ws_ohlcv_data.keys():
            if ws_ohlcv_data[p].get('ws_pair') == ws_pair:
                pair = p
                break
        if not pair:
            # Only cache data for registered pair
            return

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
                    # remove the oldest candle
                    self.websocket_data['ohlcv'][pair]['data'].pop(0)
                    interval_str = self.websocket_data['ohlcv'][pair]['interval_str']
                    last_historical_candle = self.api.fetch_ohlcv(pair, interval_str)[-2]
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

    def register_ohlcv(self, pair, interval_str='1m'):
        if self.websocket_data['ohlcv'].get(pair):
            return
        self.websocket_data['ohlcv'][pair] = {}
        self.websocket_data['ohlcv'][pair]['ws_pair'] = pair.replace('/', '').lower()
        self.websocket_data['ohlcv'][pair]['interval_str'] = interval_str
        # intialize ohlcv data using rest api
        #try:
        #    initial_ohlcv = self._rest_api.fetch_ohlcv(pair, interval_str)
        #except:
        #    tb = traceback.format_exc()
        #    self._logger('{}'.format(tb))
        #    initial_ohlcv = None
        #if initial_ohlcv:
        #    self.websocket_data['ohlcv'][pair]['running'] = [initial_ohlcv[-1], ]
        #    self.websocket_data['ohlcv'][pair]['data'] = initial_ohlcv[-OHLCV_DEPTH-1:-1]
        stream_name = '{}.kline.{}'.format(pair.replace('/', '').lower(), interval_str)
        print(stream_name)
        self._ws_manager.subscribe_public(subscription=stream_name, callback=self._ohlcv_handler)

    def fetch_ohlcv(self, pair, tf_index=1):
        pass
