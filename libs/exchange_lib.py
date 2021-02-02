import os, sys, time
#import binascii
import random
import collections
import traceback
import ccxt
from copy import deepcopy
from math import log10
from hashlib import sha512
from random import randint
from threading import Thread, Lock
from datetime import datetime
from decimal import Decimal
from ccxt.base.errors import *

lib_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(lib_path)
sys.path.append(lib_path + '/../repositories')
sys.path.append(lib_path + '/../bots')
from user_repository_psql import UserRepositoryPSQL

from rest_api.moonix import moonix
from exception_decor import exception_logging
from common import log2
from bot_constant import *

from binance_wsclient.binance_wsclient import Binance
from binance_wsclient.binancef_wsclient import BinanceF
from bitkub_wsclient.bitkub_wsclient import Bitkub
from kraken_wsclient.kraken_wsclient import Kraken
from hitbtc2_wsclient.hitbtc2_wsclient import Hitbtc2
from okex3_wsclient.okex3_wsclient import Okex3
from kucoin_wsclient.kucoin_wsclient import Kucoin
from moonix_wsclient.moonix_wsclient import Moonix
from huobipro_wsclient.huobipro_wsclient import *
from sqldata_insert import *
from pprint import pprint


def makehash():
    return collections.defaultdict(makehash)

def load_api(api_file):
        cwd = os.path.dirname(os.path.realpath(__file__))
        with open(cwd + '/../api_keys/' + api_file, 'r') as f:
            key = f.readline().strip()
            secret = f.readline().strip()
            passphrase = f.readline().strip()
        return (key, secret, passphrase)

def generate_order_id(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return str(randint(range_start, range_end))


class AggregateExchange:
    CCXT_VERBOSE_KW = 'ccxt_verbose'
    FILE_LOGGER_KW = 'file_logger'

    # Exchange-specific params
    BINF_CONTRACT_KW = 'binancef_contract_type'

    @exception_logging
    def __init__(self, exchange_id, api_name='', username='',bot_alias='',bot_uuid ='', api_from_file='', logger=None, *iter_opts, **kw_opts):
        self.terminated = False
        self._exchange_id = exchange_id
        self._exchange_name = EXCHANGE.ID_2_EXCHANGE.get(exchange_id)
        self._api_name = api_name
        self._own_name = username
        self._bot_alias = bot_alias
        self._bot_uuid = bot_uuid
        self._log = logger if logger else log2
        # This logger will be used by ws instead of above self._log()
        self._file_logger = kw_opts.get(self.FILE_LOGGER_KW)

        if not self._exchange_name:
            self._log("exchange_libmom---73Exchange {} not found".format(exchange_id), severity='error')
            return

        # Fetch apikey & apisecret and passphrase (if any)
        if username and api_name:
            # Support Django by default
            user_repository = UserRepositoryPSQL()
            self._log("exchange_libmom---80libs-exchange_lib-80User {} using api {}".format(username, api_name))
            key, secret, passphrase = user_repository.get_api_4_exchange(username, api_name)
        else:
            if api_from_file:
                apifile = api_from_file
            else:
                apifile = self._exchange_name + '.api'
            self._log("exchange_libmom---87Using apifile: {}".format(apifile))
            key, secret, passphrase = load_api(apifile)

        self._exchange_uuid = ''
        if key and secret:
            combined_ks = '_'.join([key, secret])
            hash_obj = sha512(bytes(combined_ks, encoding='utf8'))
            hash_hex = hash_obj.hexdigest()
            self._exchange_uuid = hash_hex[:8] + hash_hex[-8:]

        # Setup RESTAPI part for exchange
        if exchange_id in EXCHANGE.OWN_REST_API_EXCHANGE:
            exec(f'self._rest_api = {self._exchange_name}({key}, {secret})')
        else:
            ccxt_init = {}
            if key and secret:
                ccxt_init = {'apiKey': key, 'secret': secret}
                if passphrase:
                    ccxt_init.update({'password': passphrase})
                if kw_opts.get(self.CCXT_VERBOSE_KW):
                    ccxt_init.update({'verbose': True})
            exec(f'self._rest_api = self._retry_rest_api(ccxt.{self._exchange_name}, (ccxt_init, ))')

        # Setup WS part of exchange
        self._ws_api = None
        if self._exchange_name == EXCHANGE.BINANCE:
            self._rest_api.options['adjustForTimeDifference'] = True
            if exchange_id == EXCHANGE.BINANCE_SPOT_ID:
                kwargs = {Binance.ACCOUNT_TYPE_KW: Binance.SPOT}
                self._ws_api = Binance(key, secret, logger=self._ws_log, rest_api=self._rest_api, **kwargs)
            elif exchange_id == EXCHANGE.BINANCE_MARGIN_ID:
                kwargs = {Binance.ACCOUNT_TYPE_KW: Binance.MARGIN}
                self._ws_api = Binance(key, secret, logger=self._ws_log, rest_api=self._rest_api, **kwargs)
            elif exchange_id == EXCHANGE.BINANCE_USDTF_ID:
                self._rest_api.options['defaultType'] = 'future'
                kwargs = {BinanceF.FUTURE_TYPE_KW: BinanceF.USDT_FUTURES}
                self._ws_api = BinanceF(key, secret, logger=self._ws_log, rest_api=self._rest_api, **kwargs)
            elif exchange_id == EXCHANGE.BINANCE_COINF_ID:
                self._rest_api.options['defaultType'] = 'delivery'
                kwargs = {BinanceF.FUTURE_TYPE_KW: BinanceF.COIN_FUTURES}
                self._ws_api = BinanceF(key, secret, logger=self._ws_log, rest_api=self._rest_api, **kwargs)
                if kw_opts.get(self.BINF_CONTRACT_KW):
                    self._ws_api.set_contract_type(kw_opts.get(self.BINF_CONTRACT_KW))
            #self._ws_api.register_order_progress()
        elif self._exchange_name == EXCHANGE.BITKUB:
            self._ws_api = Bitkub(key, secret, logger=self._ws_log, rest_api=self._rest_api)
        elif self._exchange_name == EXCHANGE.KRAKEN:
            self._ws_api = Kraken(key, secret, logger=self._ws_log, rest_api=self._rest_api)
            #self._ws_api.register_order_progress()
        elif self._exchange_name == EXCHANGE.HITBTC:
            self._ws_api = Hitbtc2(key, secret, logger=self._ws_log, rest_api=self._rest_api)
        elif self._exchange_name == EXCHANGE.OKEX3:
            self._ws_api = Okex3(key, secret, passphrase, logger=self._ws_log, rest_api=self._rest_api)
        elif self._exchange_name == EXCHANGE.HUOBIPRO:
            self._ws_api = Huobipro(key, secret, logger=self._ws_log, rest_api=self._rest_api)
        elif self._exchange_name == EXCHANGE.KUCOIN:
            self._ws_api = Kucoin(key, secret, passphrase, logger=self._ws_log, rest_api=self._rest_api)
        elif self._exchange_name == EXCHANGE.MOONIX:
            self._ws_api = Moonix(key, secret, logger=self._ws_log, rest_api=self._rest_api)

        # Dont use this var directly. Call fetch_markets instead.
        self.__markets = {}

        # Dont need to use makehash anymore
        self.websocket_data = {}
        # Same data (status only: pending, open, closed, canceled)
        # WS_DATA.ORDER_PROGRESS: {'975630827': [ORDER_OPEN, 'BTC/USDT', 0.0, 0.0, 0.002, 'buy', 6000.0]}
        self.websocket_data[WS_DATA.ORDER_PROGRESS] = {}
        # Order id map between our own order_id for stoploss order and real exchange order
        self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP] = {}
        # Sample data
        # 'order_book': {'BTC/USDT': {'asks': {11179.41: 0.001, 7510.0: 0.00017}, 'bids': {7438.76: 1.5732, 7421.4: 0.43}}}
        self.websocket_data[WS_DATA.ORDER_BOOK] = {}
        self.websocket_data[WS_DATA.OHLCV] = {}

        # Reference to lower ws data
        if self._ws_api:
            self.websocket_data[WS_DATA.ORDER_PROGRESS] = self._ws_api.websocket_data[WS_DATA.ORDER_PROGRESS]
            self.websocket_data[WS_DATA.OHLCV] = self._ws_api.websocket_data[WS_DATA.OHLCV]

    def get_exchange_id(self):
        return self._exchange_id

    def get_exchange_name(self):
        return self._exchange_name

    def get_exchange_uuid(self):
        return self._exchange_uuid

    def get_api_name(self):
        return self._api_name

    def get_ws_api(self):
        return self._ws_api

    def get_rest_api(self):
        return self._rest_api

    def set_logger(self, log_callback):
        self._log = log_callback

    def _ws_log(self, data, severity='info'):
        log2(data, logger=self._file_logger, severity=severity)

    def _retry_rest_api(self, rest_api_func, input_args):
        ret = None
        for _ in range(100):
            try:
                #TODO DBG
                # if rest_api_func.__name__ != self._exchange_name and rest_api_func == self._rest_api.create_order:
                #     self._log('create_order: input_args={}'.format(input_args))
                # END DBG
                ret = rest_api_func(*input_args)
            except ccxt.NetworkError as e:
                tb = traceback.format_exc()
                random_sleep = random.randrange(300, 500)/91
                self._log('{}'.format(tb), severity='warning')
                self._log('{}: NetworkError, retry after {}s!'.format(rest_api_func.__name__, random_sleep), severity='warning')
                time.sleep(random_sleep)
                continue
            except ccxt.OrderNotFound as e:
                self._log('{}: Unknown order sent'.format(rest_api_func.__name__), severity='warning')
                return ErrorConstant.UNKNOWN_ORDER_SENT
            except Exception as e:
                tb = traceback.format_exc()
                if ErrorConstant.KRA_RL_KEYWORD in str(e) or ErrorConstant.KRA_OL_KEYWORD in str(e):
                    self._log('{}'.format(tb), severity='error')
                    self._log('{}: DDoSProtection!! rate_limit!'.format(rest_api_func.__name__), severity='error')
                    return ErrorConstant.RESTAPI_RATE_LIMIT
                elif ErrorConstant.INVALID_NONCE in str(e):
                    random_sleep = random.randrange(300,500)/91
                    self._log('{}'.format(tb), severity='error')
                    self._log('{}: InvalidNonce!! retry after {}s!'.format(rest_api_func.__name__, random_sleep), severity='warning')
                    time.sleep(random_sleep)
                    continue
                elif ErrorConstant.BIN_POSTONLY_ORDER_FAILED in str(e):
                    self._log('{}: postOnly failed!!'.format(rest_api_func.__name__), severity='warning')
                    return ErrorConstant.RESTAPI_POSTONLY_ORDER_FAILED
                else:
                    self._log('{}'.format(tb), severity='error')
                    self._log('{}: invalid_cmd!!'.format(rest_api_func.__name__), severity='error')
                    self._log('create_order: input_args={}'.format(input_args))
                    return ErrorConstant.RESTAPI_INVALID_CMD
            else:
                return ret
        return ret

    def register_trade_stream(self, pair, refresh=False):
        if refresh:
            self._ws_api.unregister_trade_stream(pair=pair)
        self._ws_api.register_trade_stream(pair=pair)

    def fetch_trade_stream(self, pair, _reset_counter=False, index=None):
        return self._ws_api.fetch_trade_stream(pair, _reset_counter, index)

    def fetch_trade_volume(self, pair, _reset_counter=None):
        return self._ws_api.fetch_trade_volume(pair, _reset_counter)

    def register_order_book(self, pair, best_price_only=False, refresh=False):
        if best_price_only and self._exchange_name == EXCHANGE.BINANCE:
            if refresh:
                self._ws_api.unregister_book_ticker(pair=pair)
            self._ws_api.register_book_ticker(pair=pair)
        else:
            if refresh:
                self._ws_api.unregister_order_book(pair=pair)
            self._ws_api.register_order_book(pair=pair)

    def fetch_order_book(self, pair, index=None):
        if self._exchange_name != EXCHANGE.INDODAX:
            return self._ws_api.fetch_order_book(pair, index)
        else:
            # already sorted
            asks, bids = self.fetch_order_book_restapi(pair, WS_DATA.DAX_ORDER_BOOK_DEPTH)
            if asks and bids:
                if index:
                    return asks[index-1], bids[index-1]
                else:
                    return asks, bids
            else:
                return None, None

    @exception_logging
    def register_ticker_info(self, pair, refresh=False):
        if self._exchange_name == EXCHANGE.HITBTC:
            pair = pair.replace('USDT', 'USD')
        if refresh:
            self._ws_api.unregister_ticker_info(pair)
        self._ws_api.register_ticker_info(pair)

    @exception_logging
    def fetch_ticker_price(self, pair):
        return self._ws_api.fetch_ticker_price(pair)

    def register_order_progress(self, pair=None, refresh=False):
        if self._exchange_name == EXCHANGE.INDODAX:
            return
        # Okex3 needs symbol to register user order
        if self._exchange_name == EXCHANGE.OKEX3 and not pair:
            return
        # Huobipro needs symbol to register user order
        if self._exchange_name == EXCHANGE.HUOBIPRO and not pair:
            return
        # Propagate Exception from lower ws lib
        try:
            if refresh:
                self._ws_api.unregister_order_progress(pair=pair)
            self._ws_api.register_order_progress(pair=pair)
        except Exception as e:
            self._log(e)
            raise Exception(e)

    def fetch_order_progress(self, order_id):
        # Check if it's our own stoploss order
        if not isinstance(order_id, str) and self._exchange_id != EXCHANGE.MOONIX_ID:
            order_id = str(order_id)
        if order_id in self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP]:
            ex_order_id = self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP][order_id]
            if ex_order_id:
                return self.fetch_order_progress(ex_order_id)

        if self._exchange_name == EXCHANGE.INDODAX:
            p = self.fetch_order_restapi(order_id)
            # Plz read order response of Indodax restapi
            if p:
                stored_data = {
                        WS_ORDER_PROGRESS.STATUS: p.get(REST_CCXT.STATUS),
                        WS_ORDER_PROGRESS.PAIR: p.get(REST_CCXT.PAIR),
                        WS_ORDER_PROGRESS.FILLED: p.get(REST_CCXT.FILLED),
                        WS_ORDER_PROGRESS.AVG_PRICE: p.get(REST_CCXT.AVG_PRICE),
                        WS_ORDER_PROGRESS.AMOUNT: p.get(REST_CCXT.AMOUNT),
                        WS_ORDER_PROGRESS.SIDE: p.get(REST_CCXT.SIDE),
                        WS_ORDER_PROGRESS.PRICE: p.get(REST_CCXT.PRICE),
                        WS_ORDER_PROGRESS.CREATION_TIME: p.get(REST_CCXT.CREATION_TIME),
                    }
                return stored_data
            return {}
        return self.websocket_data[WS_DATA.ORDER_PROGRESS].get(order_id)

    def remove_order_ws_data(self, order_id, force_remove=False):
        if not self.websocket_data[WS_DATA.ORDER_PROGRESS].get(order_id):
            return
        status = self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id].get(WS_ORDER_PROGRESS.STATUS)
        if force_remove:
            if status == ORDER_OPEN:
                self._log(f'exchange_libmom---332Order {order_id} still OPEN. Force remove!', severity='warning')
            del self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id]
        elif status != ORDER_OPEN:
            del self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id]
        else:
            self._log(f'exchange_libmom---337Order {order_id} still OPEN. Dont remove!', severity='warning')

    def fetch_open_orders(self, input_pair='', sorted_creation_time_list=False):
        order_dict = {}
        order_progress_data = deepcopy(self.websocket_data[WS_DATA.ORDER_PROGRESS])
        for order_id, data in order_progress_data.items():
            order_status = data.get(WS_ORDER_PROGRESS.STATUS)
            pair = data.get(WS_ORDER_PROGRESS.PAIR)
            if order_id in self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP]:
                continue
            if order_status != ORDER_OPEN:
                continue
            if input_pair and input_pair != pair:
                continue
            order_dict.update({order_id: data})
        if sorted_creation_time_list:
            # newest order, latest order in the list
            return [{k: v} for k, v in sorted(order_dict.items(), key=lambda item: item[1].get(WS_ORDER_PROGRESS.CREATION_TIME))]
        return order_dict

    def fetch_number_of_opening_orders(self):
        counter = 0
        for order_id, order_info in self.websocket_data[WS_DATA.ORDER_PROGRESS].copy().items():
            if order_info[WS_ORDER_PROGRESS.STATUS] == ORDER_OPEN and \
                    order_id not in self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP].keys():
                counter += 1
        return counter

    def ohlcv_interval2minute(self, interval_str='1m'):
        interval_value = int(interval_str[:-1])
        if interval_str[-1] == OHLCV.MINUTE:
            factor = 1
        elif interval_str[-1] == OHLCV.HOUR:
            factor = 60
        elif interval_str[-1] == OHLCV.DAY:
            factor = 1440
        elif interval_str[-1] == OHLCV.WEEK:
            factor = 10080
        elif interval_str[-1] == OHLCV.MONTH:
            factor = 40320 # 1 month = 4 weeks
        else:
            self._log('exchange_libmom---378Invalid interval unit! {}'.format(interval_str), severity='error')
            return None
        return interval_value * factor

    def register_ohlcv(self, pair, interval_str='1m', real_time=False, refresh=False):
        if self._exchange_name == EXCHANGE.BINANCE:
            if refresh:
                self._ws_api.unregister_ohlcv(pair, interval_str, real_time)
            self._ws_api.register_ohlcv(pair, interval_str, real_time)
            return True

        if refresh:
            self._ws_api.unregister_ohlcv(pair, interval_str)
        self._ws_api.register_ohlcv(pair, interval_str)

    def fetch_ohlcv(self, pair, time_frame='1m', tf_index=1):
        if self._exchange_name == EXCHANGE.INDODAX:
            if tf_index >= 1:
                return self.fetch_ohlcv_restapi(pair, time_frame)[-int(tf_index)-1]
            else:
                return self.fetch_ohlcv_restapi(pair, time_frame)[:-1]

        if self.websocket_data[WS_DATA.OHLCV][pair].get(OHLCV.DATA):
            if tf_index >= 1:
                return self.websocket_data[WS_DATA.OHLCV][pair].get(OHLCV.DATA)[-int(tf_index)]
            else:
                return self.websocket_data[WS_DATA.OHLCV][pair].get(OHLCV.DATA)
        return None

    def fetch_running_ohlcv(self, pair, time_frame='1m'):
        if self._exchange_name == EXCHANGE.INDODAX:
            return self.fetch_ohlcv_restapi(pair, time_frame)[-1]

        if self.websocket_data[WS_DATA.OHLCV][pair].get(OHLCV.RUNNING):
            return self.websocket_data[WS_DATA.OHLCV][pair].get(OHLCV.RUNNING)[-1]
        return None

    def fetch_ticker_restapi(self, pair):
        return self._retry_rest_api(self._rest_api.fetchTicker, (pair, ))

    def fetch_order_restapi(self, order_id):
        return self._retry_rest_api(self._rest_api.fetchOrder, (order_id, ))

    def fetch_order_status_restapi(self, order_id, pair):
        ret = self._retry_rest_api(self._rest_api.fetchOrder, (order_id, pair))
        if ret and isinstance(ret, dict):
            return ret.get(REST_CCXT.STATUS)
        return None

    def fetch_open_orders_restapi(self, pair=''):
        try:
            # Fetch open orders from restapi
            if self._exchange_id == EXCHANGE.INDODAX_ID:
                # In case exchange supports fetch all open orders. e.g Indodax
                # Otherwise, this will return 'invalid cmd'
                return self._rest_api.fetchOpenOrders()
            symbol = None
            if self._exchange_id == EXCHANGE.BINANCE_COINF_ID:
                symbol = self._ws_api.get_symbol_from_pair(pair, False)
            return self._rest_api.fetchOpenOrders(symbol if symbol else pair)
        except:
            tb = traceback.format_exc()
            self._log(f'exchange_libmom---440ERROR {tb}')

    def update_ws_order_progress(self, pair):
        symbol = None
        if self._exchange_id == EXCHANGE.BINANCE_COINF_ID:
            symbol = self._ws_api.get_symbol_from_pair(pair, False)
        return update_ws_order_progress_helper(self._rest_api, symbol, pair, self._ws_api.websocket_data[WS_DATA.ORDER_PROGRESS])

    def fetch_order_book_restapi(self, pair, depth=10):
        order_books = self._retry_rest_api(self._rest_api.fetch_order_book, (pair, depth))
        return (order_books.get(REST_CCXT.ASKS)[:depth], order_books.get(REST_CCXT.BIDS)[:depth])

    def fetch_ohlcv_restapi(self, pair, time_frame='1m', depth=OHLCV_DEPTH):
        ohlcv = self._retry_rest_api(self._rest_api.fetch_ohlcv, (pair, time_frame))
        return ohlcv[-depth:]

    def fetch_markets(self, refresh=False):
        def _rebuild_precision(markets: list):
            for mk in markets:
                for k, v in mk['precision'].items():
                    v = float(v)
                    if 0.0 < v < 1.0:
                        new_prec = -log10(v)
                        new_prec = int(new_prec)
                        mk['precision'].update({k: new_prec})

        def _BID_rebuild_markets(markets: list):
            for mk in markets:
                mk[REST_CCXT.PAIR] = '/'.join([mk.get('base'), mk.get('quote')])
                mk['limits']['cost']['min'] = mk.get('info', {}).get('contractSize')

        if self._exchange_id in EXCHANGE.OWN_REST_API_EXCHANGE:
            return self._rest_api.fetch_markets()
        elif not self.__markets or refresh:
            markets = self._retry_rest_api(self._rest_api.fetch_markets, ())
            if self._exchange_id == EXCHANGE.BINANCE_COINF_ID:
                _BID_rebuild_markets(markets)
            _rebuild_precision(markets)
            self.__markets = {m.get(REST_CCXT.PAIR):{'limits': m.get('limits'), 'precision': m.get('precision')} for m in markets}
        # else: Assume that there's no change of markets in the running time
        return self.__markets

    def fetch_symbols(self, refresh=False):
        return list(self.fetch_markets(refresh))

    def fetch_precision(self, pair, what='', refresh=False):
        """
        Params:
            what: 'price', 'amount', BIN['base', 'quote']
        """
        markets = self.fetch_markets(refresh)
        if pair in list(markets):
            if not what:
                return markets[pair].get('precision')
            else:
                return markets[pair].get('precision').get(what)
        return None

    def fetch_limit(self, pair, what='', refresh=False):
        """
        Params:
            what: 'cost', 'price', 'amount'
        Returns: {'min': ..., 'max': ...} or None
        """
        markets = self.fetch_markets(refresh)
        if pair in list(markets):
            if not what:
                return markets[pair].get('limits')
            else:
                return markets[pair].get('limits').get(what)
        return {}

    def fetch_latest_price(self, pair):
        ask_volume, bid_volume = None, None
        while not self.terminated and ask_volume == None or bid_volume == None:
            time.sleep(0.1)
            ask_volume, bid_volume = self.fetch_order_book(pair, 1)
        ask = float(ask_volume[0])
        bid = float(bid_volume[0])
        return ask, bid

    # fetch best price
    def fetch_best_price(self, pair, side=SELL, index=1):
        ask_info, bid_info = None, None
        while not self.terminated and not ask_info or not bid_info:
            ask_info, bid_info = self.fetch_order_book(pair, index)
            time.sleep(0.1)
        ask = float(ask_info[0])
        bid = float(bid_info[0])
        # Get calculated price for each pair
        price = ask if side == 'sell' else bid
        return price

    def _stoploss_checking(self, order_id, pair, type, side, amount, price, params):
        # Get stopPrice
        stop_price = params.get("stopPrice")
        profit_order_id = params.get("profit-order-id")
        bot_type = params.get("bot_type")

        if not stop_price:
            del self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP][order_id]
            del self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id]
            return

        if pair not in self.websocket_data[WS_DATA.ORDER_BOOK]:
            self.register_order_book(pair)

        step_wise = STEP_WISE[side]
        # Create an exchange order
        cutloss_market = False
        cutloss_trade = False
        if type == OWN_STOPLOSS.LIMIT_TYPE:
            type = LIMIT
        elif type == OWN_STOPLOSS.MARKET_TYPE:
            type = MARKET
            cutloss_market = True
        elif type == OWN_STOPLOSS.TRADE_MARKET_TYPE:
            type = MARKET
            cutloss_trade = True

        while not self.terminated and order_id in self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP]:
            ask, bid = self.fetch_latest_price(pair)
            if cutloss_trade:
                price_market = self.fetch_ticker_price(pair)
                if step_wise * float(price_market) >= step_wise * stop_price:
                    break
            elif cutloss_market:
                if (side == BUY and ask >= float(stop_price)) or (side == SELL and bid <= float(stop_price)):
                    # Stop price is reached, break while loop to create exchange order
                    break
            elif not cutloss_market:
                if (side == BUY and bid >= float(stop_price)) or (side == SELL and ask <= float(stop_price)):
                    # Stop price is reached, break while loop to create exchange order
                    break
            time.sleep(0.2)
            
        if order_id not in self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP]:
            # The stoploss order is canceled so it'll be removed from stoploss_order_id_map
            self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id][WS_ORDER_PROGRESS.STATUS] = ORDER_CANCELED
            return
            
        self._log('{} Stoploss order {}: reach stopPrice {}, canceling take-profit order {} then create exchange order... '.format(bot_type, order_id, stop_price, profit_order_id))
        if profit_order_id:
            # Check filled amount of profit order
            filled = self.fetch_order_progress(profit_order_id).get(WS_ORDER_PROGRESS.FILLED)
            remaining_amount = float(Decimal(str(amount)) - Decimal(str(filled)))
            self._log('{} Stoploss order {}: take-profit order {} filled={}, remaining amount for stoploss order {}'.format(bot_type, order_id, profit_order_id, filled, remaining_amount))
            if remaining_amount <= 0:
                return
            # if cancel order failed, still create stop loss order
            try:
                self.cancel_order(profit_order_id, pair)
            except Exception as e:
                tb = traceback.format_exc()
                self._log('exchange_libmom---594Cancel profit order {} failed\n{}'.format(profit_order_id, tb), severity='warning')
            # Check filled amount of profit order
            filled = self.fetch_order_progress(profit_order_id).get(WS_ORDER_PROGRESS.FILLED)
            remaining_amount = float(Decimal(str(amount)) - Decimal(str(filled)))
            self._log('{} Stoploss order {}: take-profit order {} filled={} when cancling, remaining amount for stoploss order {}'.format(bot_type, order_id, profit_order_id, filled, remaining_amount))
            if remaining_amount <= 0:
                return
        ex_order_id = self.create_order(pair, type, side, remaining_amount, price)
        self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id].update({
            WS_ORDER_PROGRESS.STATUS: ORDER_OPEN
        })
        if ex_order_id == ErrorConstant.RESTAPI_INVALID_CMD or not ex_order_id:
            del self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP][order_id]
            self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id].update({
                WS_ORDER_PROGRESS.STATUS: ORDER_CANCELED
            })
            return
            
        # Update stoploss_order_id_map with new ex order id
        self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP].update({order_id: ex_order_id})
        self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id] = None
        return
        
    def create_own_stoploss_order(self, pair, type, side, amount, price, params={}):
        # Generate own order_id has 9 digits
        order_id = generate_order_id(9)
        while not self.terminated and order_id in self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP]:
            # Regenerate if order_id exists
            order_id = generate_order_id(9)
        self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP][order_id] = ''
        stored_data = {
                WS_ORDER_PROGRESS.STATUS: ORDER_PENDING,
                WS_ORDER_PROGRESS.PAIR: pair,
                WS_ORDER_PROGRESS.FILLED: 0.0,
                WS_ORDER_PROGRESS.AVG_PRICE: 0.0,
                WS_ORDER_PROGRESS.AMOUNT: amount,
                WS_ORDER_PROGRESS.SIDE: side,
                WS_ORDER_PROGRESS.PRICE: price,
                WS_ORDER_PROGRESS.CREATION_TIME: int(time.time() * 1000),
                WS_ORDER_PROGRESS.IS_USING: True,
                WS_ORDER_PROGRESS.UPDATE_TIME: [time.time()]
            }
        self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id] = stored_data
        # Checking price if the stopPrice in params is reached then open an exchange order
        Thread(target=self._stoploss_checking, args=(order_id, pair, type, side, amount, price, params)).start()
        return order_id

    def check_enough_balance(self, side, amount, price, pair):
        try:
            # COIN-Futures: dont need to check balance on BUY side
            # USDT-Futures: dont need to check balance on SELL side
            if (self._exchange_id == EXCHANGE.BINANCE_COINF_ID and BUY == side) or \
               (self._exchange_id == EXCHANGE.BINANCE_USDTF_ID and SELL == side):
                return True
            if not pair:
                self._log('exchange_libmom---649check enough balance must have pair, return True')
                return True
            _base_curr, _quote_curr = pair.split('/')
            curr, pr = (_quote_curr, Decimal(str(price))) if BUY == side else (_base_curr, Decimal(1))
            curr_balance = self.fetch_balance(curr)
            # if balance not fetch, return True
            if not curr_balance:
                self._log(f'exchange_libmom---656curr_balance for {curr} None, return True')
                return True
            if not curr_balance.get('total'):
                self._log(f'exchange_libmom---659Balance {curr} does not have "total" attr, return False __ {curr_balance}')
                return False
            if curr_balance.get('free'):
                balance = Decimal(str(curr_balance['free']))
            elif curr_balance.get('used'):
                balance = Decimal(str(curr_balance['total'])) - Decimal(str(curr_balance['used']))
            else:
                balance = Decimal(str(curr_balance['total']))
            amount_dec = Decimal(str(amount))
            #FIXME need to recalc amount for COIN-Futures.
            # The amount unit is 'contract' which has a fixed size (contractSize) in USD.
            if self._exchange_id == EXCHANGE.BINANCE_COINF_ID:
                cont_size = self.fetch_limit(pair, what='cost').get('min')
                amount_dec = Decimal(str(cont_size)) / Decimal(str(price))
            return balance >= (amount_dec * pr)
        except:
            tb = traceback.format_exc()
            self._log(f'exchange_libmom---676check_enough_balance: {tb}', severity='warning')
            return False

    def _check_break_trailing(self, order_id):
        if self.terminated:
            self._log(f'exchange_libmom---681{order_id} terminated when check_break_trailing')
            return True
        elif str(order_id) not in self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP]:
            # The stoploss order is canceled so it'll be removed from stoploss_order_id_map
            self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id].update({
                WS_ORDER_PROGRESS.STATUS: ORDER_CANCELED
            })
            self._log(f'exchange_libmom---688{order_id} deleted from order_map when check_break_trailing')
            return True
        return False

    def _checking_trailing_stop_order(self, order_id, pair, type, side, amount, trailing_margin, base_price, min_amount, follow_base_price=False, gap=0, post_only=False):
        step_wise = Decimal(str(STEP_WISE[side]))
        trailing_margin = Decimal(str(trailing_margin))
        orig_base_price = base_price
        base_price = float(base_price)
        trailing_stop_price = float(Decimal(str(base_price)) + step_wise * trailing_margin)
        is_reach_base = False
        while not self.terminated and str(order_id) in self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP]:
            price_market = float(self.fetch_ticker_price(pair))
            if float(step_wise) * price_market <= float(step_wise) * base_price:
                base_price = price_market
                trailing_stop_price = float(Decimal(str(price_market)) + step_wise * trailing_margin)
                # print(trailing_stop_price)
            elif float(step_wise) * price_market > float(step_wise) * trailing_stop_price:
                if follow_base_price and float(step_wise) * trailing_stop_price <= float(step_wise) * orig_base_price:
                    self._log(f'exchange_libmom---707{order_id} reach trailing stop price={trailing_stop_price} origin_base={orig_base_price} cur_price={price_market}, place {type} {side} order')
                    is_reach_base = True
                    break
                elif not follow_base_price:
                    self._log(f'exchange_libmom---711{order_id} reach trailing stop price {trailing_stop_price} cur_price={price_market}, place {type} {side} order')
                    break
            time.sleep(0.2)

        if self._check_break_trailing(order_id):
            return

        order_price = float(Decimal(str(self.fetch_best_price(pair, side))) - step_wise * Decimal(str(gap)))
        if is_reach_base:
            order_price = orig_base_price
        type_order = LIMIT_MAKER if post_only else LIMIT
        # check balance before create order
        num_time = 0
        while not self.terminated and str(order_id) in self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP]:
            if self.check_enough_balance(side, amount, order_price, pair):
                break
            elif num_time == 0 or num_time >= 50:  # 10s
                self._log(f'exchange_libmom---728# ex_lib: Balance insufficient to create order {side} {pair} with amount is {amount} and price is {order_price}')
                num_time = 1
            time.sleep(0.2)
            num_time += 1

        if self._check_break_trailing(order_id):
            return

        ex_order_id = self.create_order(pair, type_order, side, amount, order_price)
        while not self.terminated and str(order_id) in self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP] and \
                ex_order_id in [ErrorConstant.RESTAPI_POSTONLY_ORDER_FAILED, ErrorConstant.RESTAPI_INVALID_CMD] \
                or self.fetch_order_progress(ex_order_id).get(WS_ORDER_PROGRESS.STATUS) == ORDER_EXPIRED:
            order_price = float(self.fetch_best_price(pair, side))
            if is_reach_base:
                # Follow market but has base price
                if float(Decimal(str(orig_base_price)) * step_wise) <= float(Decimal(str(order_price)) * step_wise):
                    order_price = orig_base_price
            if self.check_enough_balance(side, amount, order_price, pair):
                ex_order_id = self.create_order(pair, type_order, side, amount, order_price)
            time.sleep(0.2)

        if self._check_break_trailing(order_id):
            return

        self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id].update({
            WS_ORDER_PROGRESS.STATUS: ORDER_OPEN
        })
        if ex_order_id:
            if is_reach_base:
                orig_base_price = order_price
            self._follow_market_order(ex_order_id, order_id, pair, side, amount, type_order, min_amount, gap, base_price=orig_base_price)
            return

    def _follow_market_order(self, ex_order_id, order_id, pair, side, amount, type_order, min_amount, gap, base_price=None):
        count = 0
        s_amount = 0
        step_wise = Decimal(str(STEP_WISE[side]))
        still_follow_mk = True
        while not self.terminated and self.fetch_order_progress(ex_order_id).get(WS_ORDER_PROGRESS.STATUS) == ORDER_OPEN and\
                str(order_id) in self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP]:
            count += 1
            order_progress = self.fetch_order_progress(ex_order_id)
            if base_price == order_progress.get(WS_ORDER_PROGRESS.PRICE) and still_follow_mk:
                still_follow_mk = False
                self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP][order_id] = ex_order_id

            if count > 18 and order_progress.get(WS_ORDER_PROGRESS.STATUS) == ORDER_OPEN and still_follow_mk:
                if float(order_progress.get(WS_ORDER_PROGRESS.FILLED)) > 0 and count < 100: #not filled after 30s -> cancel
                    time.sleep(0.3)
                    continue
                new_amount_order = amount - s_amount - float(order_progress.get(WS_ORDER_PROGRESS.FILLED))
                if new_amount_order <= min_amount:
                    time.sleep(0.3)
                    continue
                # after ~1.5s, if order open position cannot filled, should cancel and recheck
                price_cmp = float(Decimal(str(self.fetch_best_price(pair, side))) * step_wise)
                this_price = float(Decimal(str(order_progress.get(WS_ORDER_PROGRESS.PRICE))) * step_wise)

                if price_cmp > this_price:
                    cancel_rs = self.cancel_order(ex_order_id, pair)
                    self._log('exchange_libmom---788{} Cancel rs, follow market {}'.format(order_id, cancel_rs))
                    order_progress = self.fetch_order_progress(ex_order_id)
                    mk_price = float(Decimal(str(self.fetch_best_price(pair, side))) - step_wise * Decimal(str(gap)))
                    if order_progress.get(WS_ORDER_PROGRESS.STATUS) == ORDER_CANCELED:
                        if float(order_progress.get(WS_ORDER_PROGRESS.FILLED)) > 0:
                            self._log(f'exchange_libmom---793{order_id} partial filled {order_progress.get(WS_ORDER_PROGRESS.FILLED)}')
                        s_amount = float(Decimal(str(s_amount)) + Decimal(str(order_progress.get(WS_ORDER_PROGRESS.FILLED))))
                        remain_amount = float(Decimal(str(amount)) - Decimal(str(s_amount)))
                        price = mk_price
                        if base_price and (step_wise * Decimal(str(mk_price)) > step_wise * Decimal(str(base_price))):
                            still_follow_mk = False
                            price = base_price
                            # ex_order_id = self.create_order(pair, LIMIT, side, remain_amount, price)
                            # self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP][order_id] = ex_order_id
                            # return
                            # check balance before create order
                        num_time = 0
                        while not self.terminated:
                            if self.check_enough_balance(side, remain_amount, price, pair):
                                break
                            elif num_time == 0 or num_time >= 50:  # 10s
                                self._log(
                                    f'exchange_libmom---810# ex_lib: Balance insufficient to create order {side} {pair} with amount is {remain_amount} and price is {price}')
                                num_time = 1
                            time.sleep(0.2)
                            num_time += 1
                        ex_order_id = self.create_order(pair, type_order, side, remain_amount, price)
                        while not self.terminated and ex_order_id in [ErrorConstant.RESTAPI_POSTONLY_ORDER_FAILED, ErrorConstant.RESTAPI_INVALID_CMD] \
                                or self.fetch_order_progress(ex_order_id).get(WS_ORDER_PROGRESS.STATUS) == ORDER_EXPIRED:
                            order_price = float(self.fetch_best_price(pair, side))
                            if self.check_enough_balance(side, amount, order_price, pair):
                                ex_order_id = self.create_order(pair, type_order, side, remain_amount, order_price)
                            time.sleep(0.2)
                        if not still_follow_mk:
                            # Reach base, link fake order id with exchange order id
                            self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP][order_id] = ex_order_id
                        count = 0
            time.sleep(0.3)

        order_progress = self.fetch_order_progress(ex_order_id)
        # Sample data (status only: pending, open, closed, canceled)
        if order_progress.get(WS_ORDER_PROGRESS.STATUS) == ORDER_CLOSED:
            self._log(f'exchange_libmom---830{order_id} fulfilled')
            # return data for order_id
            data = {
                     WS_ORDER_PROGRESS.STATUS: ORDER_CLOSED,
                     WS_ORDER_PROGRESS.PAIR: pair,
                     WS_ORDER_PROGRESS.FILLED: amount,
                     WS_ORDER_PROGRESS.AVG_PRICE: order_progress.get(WS_ORDER_PROGRESS.AVG_PRICE),
                     WS_ORDER_PROGRESS.AMOUNT: amount,
                     WS_ORDER_PROGRESS.SIDE: side,
                     WS_ORDER_PROGRESS.PRICE: order_progress.get(REST_CCXT.PRICE),
                     WS_ORDER_PROGRESS.CREATION_TIME: order_progress.get(REST_CCXT.CREATION_TIME),
                     WS_ORDER_PROGRESS.IS_USING: True,
                     WS_ORDER_PROGRESS.UPDATE_TIME: [time.time()]
                    }
            if str(order_id) in self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP]:
                del self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP][order_id]
            self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id] = data


    def create_trailing_stop_order(self, pair, type, side, amount, trailing_margin, base_price, min_amount, follow_base_price=False, gap=0, post_only=False):
        order_id = str(generate_order_id(9))
        while not self.terminated and order_id in self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP]:
            # Regenerate if order_id exists
            order_id = str(generate_order_id(9))
        self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP][order_id] = ''
        stored_data = {
            WS_ORDER_PROGRESS.STATUS: ORDER_PENDING,
            WS_ORDER_PROGRESS.PAIR: pair,
            WS_ORDER_PROGRESS.FILLED: 0.0,
            WS_ORDER_PROGRESS.AVG_PRICE: 0.0,
            WS_ORDER_PROGRESS.AMOUNT: amount,
            WS_ORDER_PROGRESS.SIDE: side,
            WS_ORDER_PROGRESS.PRICE: base_price,
            WS_ORDER_PROGRESS.CREATION_TIME: int(time.time() * 1000),
            WS_ORDER_PROGRESS.IS_USING: True,
            WS_ORDER_PROGRESS.UPDATE_TIME: [time.time()]
        }
        self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id] = stored_data
        if pair not in self.websocket_data[WS_DATA.ORDER_BOOK]:
            self.register_order_book(pair)
        if not self.fetch_ticker_price(pair):
            self.register_ticker_info(pair)

        # Checking price if the stopPrice in params is reached then open an exchange order
        Thread(target=self._checking_trailing_stop_order, args=(order_id, pair, type, side, amount, trailing_margin, base_price, min_amount, follow_base_price, gap, post_only)).start()
        return order_id


    def create_order(self, pair, type, side, amount, price, params={}):
        if self._exchange_name == EXCHANGE.HUOBIPRO:
            pair = self.normalize_pair_huobipro(pair)
        else: # binance futures
            if self._exchange_id in [EXCHANGE.BINANCE_USDTF_ID, EXCHANGE.BINANCE_COINF_ID]:
                if type == 'stop_loss_limit':
                    type = 'stop'
        try:
            # Our own stoploss order mechanism
            if type in [OWN_STOPLOSS.LIMIT_TYPE, OWN_STOPLOSS.MARKET_TYPE, OWN_STOPLOSS.TRADE_MARKET_TYPE]:
                return self.create_own_stoploss_order(pair, type, side, amount, price, params)
            if type == MARKET:
                price = None
            if self._exchange_id == EXCHANGE.BINANCE_MARGIN_ID:
                # sapiPostMarginOrder
                format_pair = pair.replace('/', '')
                order = self._rest_api.sapi_post_margin_order({'symbol': format_pair, 'side': side.upper(), 'type': type.upper(),'recvWindow': 5000,
                                                        'timeInForce': 'GTC', 'quantity': amount, 'price': price,
                                                         'timestamp': int(time.time() * 1000)})
                self._log('exchange_libmom---897order {}'.format(order))
            else:
                # PostOnly order
                if type == LIMIT_MAKER:
                    if self._exchange_id == EXCHANGE.HITBTC_ID:
                        type = LIMIT
                        params = {"postOnly": True}
                    elif self._exchange_id == EXCHANGE.KRAKEN_ID:
                        type = LIMIT
                        params = {'oflags': 'post'}
                symbol = pair
                if self._exchange_id == EXCHANGE.BINANCE_COINF_ID:
                    symbol = self._ws_api.get_symbol_from_pair(pair, False)
                order = self._retry_rest_api(self._rest_api.create_order, (symbol, type, side, amount, price, params))

            if order in [ErrorConstant.RESTAPI_INVALID_CMD, ErrorConstant.RESTAPI_RATE_LIMIT, ErrorConstant.RESTAPI_POSTONLY_ORDER_FAILED]:
                return order

            order_id = ''
            if order.get(REST_CCXT.ID):
                # Get order id on Kraken, hitbtc
                order_id = order.get(REST_CCXT.ID)
                # Hack to update ws data for binance only
                if self._exchange_id in [EXCHANGE.BINANCE_SPOT_ID, EXCHANGE.HITBTC_ID]:
                    if isinstance(order, dict):
                        stored_data = {
                            WS_ORDER_PROGRESS.STATUS: order.get(REST_CCXT.STATUS),
                            WS_ORDER_PROGRESS.PAIR: pair,
                            WS_ORDER_PROGRESS.FILLED: order.get(REST_CCXT.FILLED),
                            WS_ORDER_PROGRESS.AVG_PRICE: order.get(REST_CCXT.AVG_PRICE) if order.get(REST_CCXT.AVG_PRICE) else price,
                            WS_ORDER_PROGRESS.AMOUNT: amount,
                            WS_ORDER_PROGRESS.SIDE: side,
                            WS_ORDER_PROGRESS.PRICE: price,
                            WS_ORDER_PROGRESS.CREATION_TIME: order.get(REST_CCXT.CREATION_TIME),
                            WS_ORDER_PROGRESS.IS_USING: True,
                            WS_ORDER_PROGRESS.UPDATE_TIME: [time.time()],
                        }
                        if not self.websocket_data[WS_DATA.ORDER_PROGRESS].get(order_id) or \
                            (self.websocket_data[WS_DATA.ORDER_PROGRESS].get(order_id) and \
                             self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id][WS_ORDER_PROGRESS.STATUS] == ORDER_OPEN and order.get(REST_CCXT.STATUS) != ORDER_OPEN):
                            self.websocket_data[WS_DATA.ORDER_PROGRESS].update({order_id: stored_data})
            elif order.get('orderId'):
                # Get order id on Indodax,...
                order_id = order.get('orderId')
            self._log('exchange_libmom---941{} __ {} {} {} {} {} with order id {}'.format(self._exchange_name,pair,type,side,amount,price,order_id))
            sql_order_detail_inserted = sql_exchange_lib_order_details(pair,type,side,amount,price,order_id,self._own_name,self._bot_alias,self._bot_uuid,self._api_name,self._exchange_id)
            self._log('exchange_libmom---943---{}'.format(sql_order_detail_inserted))


            return order_id
        except Exception as e:
            tb = traceback.format_exc()
            self._log('exchange_libmom---945ERROR {}'.format(tb), severity='error')
            return None

    def cancel_order(self, order_id, pair=None, unknown_order_retry=5):
        try:
            unknown_order_sleep_time = 0.5

            if self._exchange_id == EXCHANGE.BINANCE_MARGIN_ID:
                format_pair = pair.replace('/', '')
                order_delete = self._rest_api.sapi_delete_margin_order(
                    {'symbol': format_pair, 'orderId': str(order_id), 'recvWindow': 5000, 'timestamp': int(time.time() * 1000)})
                self._log('exchange_libmom---956delete order {}'.format(order_delete))
                return True
            # Check if the canceled order is our own stoploss order
            if str(order_id) in self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP]:
                order_id = str(order_id)
                ex_order_id = self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP].get(order_id)
                ret = True
                if ex_order_id:
                    ret = self.cancel_order(ex_order_id, pair)
                del self.websocket_data[WS_DATA.STOPLOSS_ORDER_MAP][order_id]
                self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id].update({
                    WS_ORDER_PROGRESS.STATUS: ORDER_CANCELED,
                })
                self._log('exchange_libmom---969Canceled stoploss order {}'.format(order_id))
                return ret

            symbol = None
            if self._exchange_id == EXCHANGE.BINANCE_COINF_ID:
                symbol = self._ws_api.get_symbol_from_pair(pair, False)
            # if not have order progress in ws_data, return False
            # because order had been remove by clean ws_data
            if not self.fetch_order_progress(order_id):
                return False
            order_status = self.fetch_order_progress(order_id).get(WS_ORDER_PROGRESS.STATUS)
            while not self.terminated and order_status != ORDER_CANCELED and order_status != ORDER_CLOSED:
                if self._exchange_name in [EXCHANGE.KRAKEN, EXCHANGE.HITBTC]:
                    ret = self._retry_rest_api(self._rest_api.cancel_order, (order_id, ))
                else:  # Valid for Binance and Indodax
                    ret = self._retry_rest_api(self._rest_api.cancel_order, (order_id, symbol if symbol else pair))
                    if isinstance(ret, dict):
                        ret_order_status = ret.get(REST_CCXT.STATUS)
                        if ret_order_status:
                            self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id].update(
                                                {
                                                    WS_ORDER_PROGRESS.STATUS: ret_order_status,
                                                    WS_ORDER_PROGRESS.FILLED: ret.get(REST_CCXT.FILLED),
                                                    WS_ORDER_PROGRESS.AVG_PRICE: 0 if not ret.get(REST_CCXT.AVG_PRICE) else float(ret.get(REST_CCXT.AVG_PRICE)),
                                                })
                if ret in [ErrorConstant.RESTAPI_INVALID_CMD, ErrorConstant.RESTAPI_RATE_LIMIT,
                           ErrorConstant.UNKNOWN_ORDER_SENT]:
                    if ret == ErrorConstant.UNKNOWN_ORDER_SENT:
                        # loop for fetching order_status in case getting UNKNOWN_ORDER_SENT while cancel an order
                        order_status = self.fetch_order_progress(order_id).get(WS_ORDER_PROGRESS.STATUS)
                        while not self.terminated and order_status == ORDER_OPEN and unknown_order_retry >= 0:
                            time.sleep(unknown_order_sleep_time)
                            order_status = self.fetch_order_progress(order_id).get(WS_ORDER_PROGRESS.STATUS)
                            if order_status == ORDER_CANCELED:
                                return True
                            elif order_status in [ORDER_CLOSED, ORDER_EXPIRED]:
                                return False
                            unknown_order_retry -= 1
                    order_status = self.fetch_order_progress(order_id).get(WS_ORDER_PROGRESS.STATUS)
                    if order_status == ORDER_CANCELED:
                        self._log('exchange_libmom---1009Canceled {}'.format(order_id))
                        order_status_inserted = exchange_lib_cancled_order(order_id,order_status,self._own_name,self._bot_alias,self._bot_uuid)
                        #print("exchange_libmom---1024order cancled",order_status_inserted)
                        return True
                    else:
                        self._log('exchange_libmom---1012{} status: {}'.format(order_id, order_status))
                        order_status_inserted = exchange_lib_cancled_order(order_id,order_status,self._own_name,self._bot_alias,self._bot_uuid)
                        #print("exchange_libmom---1021order cancled",order_status_inserted)
                        return False
                time.sleep(0.2)
                order_status = self.fetch_order_progress(order_id).get(WS_ORDER_PROGRESS.STATUS)
            if order_status == ORDER_CANCELED:
                self._log('exchange_libmom---1026Canceled {}'.format(order_id))
                order_status_inserted = exchange_lib_cancled_order(order_id,order_status,self._own_name,self._bot_alias,self._bot_uuid)
                #print("exchange_libmom---1024order cancled",order_status_inserted)
                return True
            else:
                self._log('exchange_libmom---1020{} status: {}'.format(order_id, order_status))
                order_status_inserted = exchange_lib_cancled_order(order_id,order_status,self._own_name,self._bot_alias,self._bot_uuid)
                #print("exchange_libmom---1029order cancled",order_status_inserted)
                return False
        except Exception as e:
            tb = traceback.format_exc()
            self._log('exchange_libmom---1024Cancel {} failed with err: {}'.format(order_id, str(tb).replace('ERROR', 'WARNING')))
            return False

    def cancel_all_open_orders(self, coin_list=[], pair_list=[], side='buy', switch2restapi=False):
        try:
            if self._exchange_name == EXCHANGE.KRAKEN:
                order_progress_data = self.websocket_data[WS_DATA.ORDER_PROGRESS].copy()
            elif self._exchange_name == EXCHANGE.BINANCE:
                if not switch2restapi:
                    # In case we dont care about open orders before register_order_progress
                    order_progress_data = self.websocket_data[WS_DATA.ORDER_PROGRESS].copy()
                else:
                    if not pair_list:
                        self._log('exchange_libmom---1037Only supports cancel orders from a pair list on Binance', severity='error')
                        return False
                    # TODO fetch open orders by pairs
                    for pair in pair_list:
                        open_orders = self.fetch_open_orders_restapi(pair)
                        for order in open_orders:
                            if side == order.get(REST_CCXT.SIDE):
                                self.cancel_order(order.get(REST_CCXT.ID), pair)
                            # Avoid InvalidNonce
                            time.sleep(0.2)
                    return True
            elif self._exchange_name == EXCHANGE.INDODAX:
                # TODO fetch all open orders
                open_orders = self.fetch_open_orders_restapi()
                for order in open_orders:
                    if pair_list:
                        for pair in pair_list:
                            if order.get(REST_CCXT.PAIR) == pair:
                                self.cancel_order(order.get(REST_CCXT.ID), pair=pair)
                                break
                    elif coin_list:
                        for coin in coin_list:
                            if order.get(REST_CCXT.PAIR).find(coin) != -1:
                                self.cancel_order(order.get(REST_CCXT.ID), pair=order.get(REST_CCXT.PAIR))
                                break
                    else:
                        self.cancel_order(order.get(REST_CCXT.ID), pair=order.get(REST_CCXT.PAIR))
                return True

            # Below segment is only for exchange supporting websocket
            for order_id, order_progress in order_progress_data.items():
                if order_progress[WS_ORDER_PROGRESS.STATUS] == ORDER_CLOSED or order_progress[WS_ORDER_PROGRESS.STATUS] == ORDER_CANCELED:
                    continue
                if pair_list:
                    for pair in pair_list:
                        if order_progress[WS_ORDER_PROGRESS.PAIR] == pair:
                            self.cancel_order(order_id, pair=order_progress[WS_ORDER_PROGRESS.PAIR])
                            break
                elif coin_list:
                    for coin in coin_list:
                        if order_progress[WS_ORDER_PROGRESS.PAIR].find(coin) != -1:
                            self.cancel_order(order_id, pair=order_progress[WS_ORDER_PROGRESS.PAIR])
                            break
                else: # cancel all orders
                    self.cancel_order(order_id, pair=order_progress[WS_ORDER_PROGRESS.PAIR])
            return True
        except Exception as e:
            return False

    def fetch_balance(self, coin=''):
        if self._exchange_name == EXCHANGE.MOONIX:
            return self._rest_api.fetch_balance(coin)
        elif self._exchange_name == EXCHANGE.BINANCE:
            balance = self._ws_api.fetch_balance(coin)
            if balance:
                return balance

        balance = self._retry_rest_api(self._rest_api.fetch_balance, ())
        if not coin:
            return balance
        return balance.get(coin)

    def fetch_balance_rest_api(self, coin=''):
        balance = self._retry_rest_api(self._rest_api.fetch_balance, ())
        if not coin:
            return balance
        return balance.get(coin)

    def get_all_valid_pairs_from_coin(self, coin):
        symbols = self.fetch_symbols()
        return [i for i in symbols if coin == i[:i.find('/')] or coin == i[i.find('/')+1:]]

    def get_all_valid_pairs_from_coin_list(self, coin_list):
        all_pairs = []
        for c in coin_list:
            pairs = self.get_all_valid_pairs_from_coin(c)
            all_pairs = all_pairs + list(set(pairs) - set(all_pairs))
        return all_pairs

    def get_pairs(self):
        symbols = self.fetch_symbols()
        dic = {}
        for i in symbols:
            dic.update({i.replace('/', ''): i})
        return dic

    def get_valid_pair_from_2coins(self, coin1, coin2):
        symbols = self.fetch_symbols()
        pair1 = '{}/{}'.format(coin1, coin2)
        pair2 = '{}/{}'.format(coin2, coin1)
        if pair1 in symbols:
            return pair1
        if pair2 in symbols:
            return pair2
        return ''

    def normalize_pair_huobipro(self, pair):
        pair = pair.replace('/', '')
        pair = pair.lower()
        return pair

    def fetch_order(self, order_id):
        return self._rest_api.fetch_order(order_id)

    def unsubscribe_ws(self):
        try:
            self._log('exchange_libmom---1143Close web socket')
            self._ws_api._ws_manager.close()
        except Exception as e:
            tb = traceback.format_exc()
            self._log(f'exchange_libmom---1147ERROR when close websocket {tb}')

    def register_balance_account(self, refresh=False):
        """
        Register balance account websocket
        """
        # binance alredy registered
        if self._exchange_name == EXCHANGE.BINANCE:
            return True
        try:
            self._ws_api.register_balance_account()
        except Exception as e:
            self._log('exchange_libmom---1159Method not found')

    def update_websocket_data_by_manual(self, data):
        """
        self.ex_instance.websocket_data['order_progress']['825276072'].update({'order_status':'closed', WS_ORDER_PROGRESS.FILLED: 200.0})
        """
        try:
            if not data:
                self._log('exchange_libmom---1167update websocket data, but data None, return False')
                return False
            order_info = self.websocket_data[WS_DATA.ORDER_PROGRESS].get(data.get(KEY_GET_ORDER_ID))
            if order_info:
                self.websocket_data[WS_DATA.ORDER_PROGRESS].get(data.get(KEY_GET_ORDER_ID)).update({
                    WS_ORDER_PROGRESS.STATUS: data.get(KEY_GET_ORDER_STATUS),
                    WS_ORDER_PROGRESS.FILLED: data.get(KEY_GET_ORDER_FILLED),
                    WS_ORDER_PROGRESS.AVG_PRICE: data.get(KEY_GET_ORDER_AVERAGE_PRICE),
                })
            else:
                self.websocket_data[WS_DATA.ORDER_PROGRESS].update({data.get(KEY_GET_ORDER_ID): {
                    WS_ORDER_PROGRESS.STATUS: data.get(KEY_GET_ORDER_STATUS),
                    WS_ORDER_PROGRESS.FILLED: data.get(KEY_GET_ORDER_FILLED),
                    WS_ORDER_PROGRESS.AVG_PRICE: data.get(KEY_GET_ORDER_AVERAGE_PRICE),
                    WS_ORDER_PROGRESS.SIDE: data.get(KEY_GET_ORDER_SIDE),
                    WS_ORDER_PROGRESS.AMOUNT: data.get(KEY_GET_ORDER_AMOUNT),
                    WS_ORDER_PROGRESS.PRICE: data.get(KEY_GET_ORDER_PRICE),
                    WS_ORDER_PROGRESS.PAIR: data.get(KEY_GET_ORDER_PAIR),
                }})
            self.append_update_time_ws_data(data.get(KEY_GET_ORDER_ID))
        except Exception as e:
            tb = traceback.format_exc()
            self._log(f'exchange_libmom---1189Traceback error: \n {tb}')

    def clear_order_ws_when_not_using(self, force_remove=False):
        try:
            """
            2 case clear: 1. Order canceled or filled by last day
                          2. Order have flag: IS_USING is False
            """
            self._log(f'exchange_libmom---1197EXCHANGE_LIB: {self._exchange_id} clear_order_ws_when_not_using begin')
            order_progress_cp = self.websocket_data[WS_DATA.ORDER_PROGRESS].copy()
            time_now = time.time()  # example: 1599535540.955784
            for order_id, order_info in order_progress_cp.items():
                time_updates = order_info.get(WS_ORDER_PROGRESS.UPDATE_TIME)
                if time_updates:
                    # select last time update
                    last_time_update = time_updates[-1]
                    # gap_time = 24*60*60 # 1 day
                    # demo 5 minutes
                    gap_time = BOT_TIMER.CLEAN_WS_DATA_INTERVAL_EXCHANGE_LIB
                    if ORDER_OPEN != order_info[WS_ORDER_PROGRESS.STATUS] and ORDER_PENDING != order_info[WS_ORDER_PROGRESS.STATUS] \
                            and ((gap_time < time_now - last_time_update) or force_remove):
                        if order_id in self.websocket_data[WS_DATA.ORDER_PROGRESS].keys():
                            del self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id]
                time.sleep(0.01)
            self._log(f'exchange_libmom---1213#EXCHANGE_LIB: {self._exchange_id} clear order ws when not using done')
        except:
            tb = traceback.format_exc()
            self._log(f'exchange_libmom---1216Traceback error: \n {tb}')

    def append_update_time_ws_data(self, order_id):
        try:
            # if order_id not in ws_data progress
            if order_id not in self.websocket_data[WS_DATA.ORDER_PROGRESS].keys():
                # if order had status cancel closed
                self._log(f'exchange_libmom---1223Cant update time of  order id {order_id} in ws data')
            else:
                order_infos = self.websocket_data[WS_DATA.ORDER_PROGRESS].get(order_id)
                if not order_infos:
                    self._log(f'exchange_libmom---1227STRANGE: Order id: {order_id} had no content in ws data')
                    return
                arr_update_time = order_infos.get(WS_ORDER_PROGRESS.UPDATE_TIME)
                if ORDER_OPEN != order_infos[WS_ORDER_PROGRESS.STATUS]:
                    if not arr_update_time:
                        self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id].update({
                            WS_ORDER_PROGRESS.UPDATE_TIME: [time.time()]
                        })
                    else:
                        self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id][WS_ORDER_PROGRESS.UPDATE_TIME].append(time.time())
                    # self._log(f'Update update_time when order status diff open')
        except:
            tb = traceback.format_exc()
            self._log(f'exchange_libmom---1240ERROR {tb}')


