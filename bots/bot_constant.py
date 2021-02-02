from decimal import Decimal
import time
import traceback

# logger
class LoggerConfig:
    LOG_MAX_SIZE = 31457280  # bytes = 30MiB
    LOG_MAX_FILE = 9  # max rotated files


ORDER_PROFILE = {
    'buy': {
        'step_wise': 1
    },
    'sell': {
        'step_wise': -1
    },
    'time_sleep': 0.1,
    'status': {
        'open': 'open',
        'closed': 'closed',
        'canceled': 'canceled',
        'pending': 'pending'
    },
    'min_amount': 0.002
}
# handel stop loss order in bot father and key use in some where
ORDER_STOP_LOSS = 'stop_loss'
STOP_LOSS_FLOW_PRICE_MARKET = 'trade_market'
CB_WHEN_STOP_LOSS_ORDER_OPEN = 'cb_stop_loss_order_open'
STOP_LOSS_ORDER_ID = 'stop_loss_order_id'
FEES = 'fees'
PARAMS_PROFIT_ORDER_ID = 'profit_order_id'
# end key stop loss order
# order_id in order data info
KEY_GET_ORDER_ID = 'order_id'
KEY_GET_ORDER_SIDE = 'position'
KEY_GET_ORDER_PRICE = 'price'
KEY_GET_ORDER_PAIR = 'symbol'
KEY_GET_ORDER_META_DATA = 'meta_data'
KEY_GET_ORDER_AVERAGE_PRICE = 'average'
KEY_GET_ORDER_STATUS = 'status'
KEY_GET_ORDER_AMOUNT = 'amount'
KEY_GET_ORDER_FILLED = 'filled'
KEY_GET_ST_ORDER_ID = 'stop_loss_order_id'
KEY_GET_PARAMS = 'params'
KEY_EXCHANGE = 'key_exchange'
# for back test
ORDER_FILLED = 'filled'
ORDER_INSUFFICIENT_BAL = 'insufficient balance'
ORDER_HAD_STOP_LOSS = 'OPEN-STOP-LOSS'

# exchange lib
EXCHANGE_WS_ORDER_STATUS = 'order_status'
ORDER_CLOSED = 'closed'
ORDER_OPEN = 'open'
ORDER_CANCELED = 'canceled'
ORDER_PENDING = 'pending'
ORDER_EXPIRED = 'expired'


# Order info
LIMIT = 'limit'
MARKET = 'market'
LIMIT_MAKER = 'limit_maker'
BUY = 'buy'
SELL = 'sell'

STEP_WISE = {
    BUY: 1,
    SELL: -1
}
DECIMAL_STEP_WISE = {
    BUY: Decimal('1'),
    SELL: Decimal('-1')

}

"""
BOT FATHER
"""
MAX_WORKERS = 1000
MAX_ORDER_BIN = 200
MAX_ORDER_KRA = 200

"""
BLACK lIST FOR MONITOR LINK
"""


MON_BLACK_LIST = ['ToolBayonetta', 'SupportMultiBoxBot', 'SupportBigAmountBot']


class LogClassification:
    """
    LOG
    """
    MAIN_FLOW = 'MAIN_FLOW'


class LogClassification:
    """
    LOG
    """
    MAIN_FLOW = 'MAIN_FLOW'

"""
EXCHANGE LIB
"""


class OWN_STOPLOSS:
    LIMIT_TYPE = 'own_stoploss_limit'
    MARKET_TYPE = 'own_stoploss_market'
    TRADE_MARKET_TYPE = 'own_stoploss_trade_market'


class ErrorConstant:
    KRA_RL_KEYWORD = 'EOrder:Rate limit exceeded'
    KRA_OL_KEYWORD = 'EOrder:Orders limit exceeded'
    KRA_RL_PENALTY = 5 * 60  # 5 minutes
    INVALID_NONCE = 'Invalid nonce'
    BIN_POSTONLY_ORDER_FAILED = 'Order would immediately match and take'
    BIN_INVALID_TIMESTAMP = 'Timestamp for this request is outside of the recvWindow'

    RESTAPI_POSTONLY_ORDER_FAILED = 'postonly_failed'
    RESTAPI_INVALID_CMD = 'invalid_cmd'
    RESTAPI_RATE_LIMIT = 'rate_limit'
    UNKNOWN_ORDER_SENT = 'Unknown order sent'


class EXCHANGE:
    BINANCE = 'binance'
    BINANCE_SPOT_ID = 'BIN'
    BINANCE_MARGIN_ID = 'BIM'
    BINANCE_USDTF_ID = 'BIF' # Backward-compat
    BINANCE_COINF_ID = 'BID'

    BITKUB = 'bitkub'
    BITKUB_ID = 'BIT'

    KRAKEN = 'kraken'
    KRAKEN_ID = 'KRA'

    HITBTC = 'hitbtc'
    HITBTC_ID = 'HIT'

    INDODAX = 'indodax'
    INDODAX_ID = 'DAX'

    OKEX3 = 'okex3'
    OKEX3_ID = 'KEX'

    HUOBIPRO = 'huobipro'
    HUOBIPRO_ID = 'HUO'

    KUCOIN = 'kucoin'
    KUCOIN_ID = 'KUC'

    MOONIX = 'moonix'
    MOONIX_ID = 'MOX'

    # own implement exchange
    OWN_REST_API_EXCHANGE = ['MOX']

    ID_2_EXCHANGE = {
        BINANCE_SPOT_ID: BINANCE,
        BINANCE_MARGIN_ID: BINANCE,
        BINANCE_USDTF_ID: BINANCE,
        BINANCE_COINF_ID: BINANCE,
        BITKUB_ID: BITKUB,
        KRAKEN_ID: KRAKEN,
        HITBTC_ID: HITBTC,
        INDODAX_ID: INDODAX,
        OKEX3_ID: OKEX3,
        HUOBIPRO_ID: HUOBIPRO,
        KUCOIN_ID: KUCOIN,
        MOONIX_ID: MOONIX,
    }


class WS_DATA:
    ORDER_BOOK = 'order_book'
    OHLCV = 'ohlcv'
    ORDER_PROGRESS = 'order_progress'
    TICKER_INFO = 'ticker_info'
    STOPLOSS_ORDER_MAP = 'stoploss_order_id_map'
    DAX_ORDER_BOOK_DEPTH = 100
    OHLCV_DEPTH = 100


class WS_ORDER_PROGRESS:
    STATUS = 'order_status'
    PAIR = 'pair'
    FILLED = 'accu_amount'
    AMOUNT = 'amount'
    AVG_PRICE = 'avg_price'
    PRICE = 'price'
    SIDE = 'side'
    CREATION_TIME = 'creation_time'
    UPDATE_TIME = 'update_time'
    IS_USING = 'is_using'


class OHLCV:
    MINUTE = 'm'
    HOUR = 'h'
    DAY = 'd'
    WEEK = 'w'
    MONTH = 'M'

    DATA = 'data'
    RUNNING = 'running'


class REST_CCXT:
    # ORDER
    STATUS = 'status'
    ID = 'id'
    PAIR = 'symbol'
    FILLED = 'filled'
    AVG_PRICE = 'average'
    AMOUNT = 'amount'
    SIDE = 'side'
    PRICE = 'price'
    CREATION_TIME = 'timestamp'
    TYPE = 'type'
    # ORDER BOOk
    ASKS = 'asks'
    BIDS = 'bids'


class REPORT_DATA:
    OPEN_ORDER = 'open_order'
    CLOSE_ORDER = 'close_order'
    VOLUME = 'volume'
    TRADE_CLOSE = 'trade_close'
    TERMINATED = 'terminated'
    ELAPSED_TIME = 'elapsed_bot_time'


class BOT_TIMER:
    """
    Const for bot_father
    """
    DEFAULT_TIME_SLEEP = 0.1  # secs
    CLEAN_WS_DATA_INTERVAL_BF = 60 * 30  # mins
    CLEAN_WS_DATA_INTERVAL_EXCHANGE_LIB = 60 * 25  # mins
    BALANCE_CHECK_INTERVAL = 60 * 5  # mins
    WS_CHECK_INTERVAL = 60 * 5  # mins
    INFLUX_BALANCE_CHECK_INTERVAL = 30  # 0.5 min


class POSTGRESS_CONFIG:
    MIN_CONN = 5
    MAX_CONN = 50
    USER_NAME = 'postgres'
    PASSWORD = ''
    HOST_FAN = ''
    PORT = '5432'
    DATABASE_ORDER_HISTORY = ''


class PlaceOrderParams:
    IS_NOT_WAITING_ORDER = 'is_not_waiting_order'
    CALLBACK = 'callback'


class TrailingOrderParams:
    TRAILING_MARGIN = 'trailing_margin'
    FOLLOW_BASE_PRICE = 'follow_base_price'
    GAP = 'gap'
    POST_ONLY = 'postOnly'
    BASE_PRICE = 'base_price'


class Chanel:
    LOG = 'log'


class TargetCurrency:
    BNB = 'BNB'
    USDT = 'USDT'


"""
This should be used by BINANCE or HITBTC
  rest_api: ccxt object
  pair: must be not None
  symbol: is only used by BID
  ws_order_progress_refdata: must be passed by reference
"""
def update_ws_order_progress_helper(rest_api, symbol, pair, ws_order_progress_refdata):
    try:
        # Build ws order id list before fetching open orders restapi
        ws_order_ids = [oid for oid in ws_order_progress_refdata.copy()]
        # Update ws data with all open orders of pair
        open_orders = rest_api.fetchOpenOrders(symbol if symbol else pair)
        if not open_orders:
            return None
        open_order_ids = []
        for order in open_orders:
            order_id = order.get(REST_CCXT.ID)
            open_order_ids.append(order_id)
            if order_id in ws_order_progress_refdata:
                continue
            accu_amount = order.get(REST_CCXT.FILLED)
            avg_price = order.get(REST_CCXT.AVG_PRICE)
            amount = order.get(REST_CCXT.AMOUNT)
            side = order.get(REST_CCXT.SIDE)
            price = order.get(REST_CCXT.PRICE)
            creation_time = order.get(REST_CCXT.CREATION_TIME)
            stored_data = {
                    WS_ORDER_PROGRESS.STATUS: ORDER_OPEN,
                    WS_ORDER_PROGRESS.PAIR: pair,
                    WS_ORDER_PROGRESS.FILLED: accu_amount,
                    WS_ORDER_PROGRESS.AVG_PRICE: avg_price,
                    WS_ORDER_PROGRESS.AMOUNT: amount,
                    WS_ORDER_PROGRESS.SIDE: side,
                    WS_ORDER_PROGRESS.PRICE: price,
                    WS_ORDER_PROGRESS.CREATION_TIME: creation_time,
                    WS_ORDER_PROGRESS.IS_USING: True,
                    WS_ORDER_PROGRESS.UPDATE_TIME: [time.time()]
                }
            ws_order_progress_refdata[order_id] = stored_data
        # Update ws tracked open orders
        for order_id in ws_order_ids:
            if ws_order_progress_refdata.get(order_id, {}).get(WS_ORDER_PROGRESS.STATUS) != ORDER_OPEN:
                continue
            # Update if ws data is outdated
            if order_id not in open_order_ids:
                order_info = rest_api.fetchOrder(order_id, symbol if symbol else pair)
                if not isinstance(order_info, dict):
                    continue
                stored_data = {
                        WS_ORDER_PROGRESS.STATUS: order_info.get(REST_CCXT.STATUS),
                        WS_ORDER_PROGRESS.FILLED: order_info.get(REST_CCXT.FILLED),
                        WS_ORDER_PROGRESS.AVG_PRICE: order_info.get(REST_CCXT.AVG_PRICE),
                    }
                update_time = ws_order_progress_refdata[order_id].get(WS_ORDER_PROGRESS.UPDATE_TIME, [])
                if update_time:
                    update_time.append(time.time())
                else:
                    update_time = [time.time()]
                stored_data.update({WS_ORDER_PROGRESS.UPDATE_TIME: update_time})
                ws_order_progress_refdata[order_id].update(stored_data)

        return open_orders
    except:
        tb = traceback.format_exc()
        print(f'bot_constantmom---351ERR: update_ws_order_progress_helper {tb} ')
