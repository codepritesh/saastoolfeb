import os
import sys
import argparse
import logging
import uuid
import time
from datetime import datetime
from threading import Thread
from queue import Queue

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../libs')
from common import log, socket_emit, RepeatTimer
from exchange_lib import *

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from multi_ways_bot import multi_ways_bot

ohlc_dryrun = [[None, 7191.8, 7195.2, 7173.6, 7180.5], [None, 7183.5, 7184.7, 7150.2, 7150.2], [None, 7150.8, 7156.3, 7130, 7145.1], [None, 7140.1, 7163.6, 7130.1, 7153.9], [None, 7155.8, 7178.7, 7144.3, 7169.1], [None, 7166.2, 7190, 7158.6, 7181.8], [None, 7189.9, 7228.9, 7189.9, 7221.8], [None, 7240.4, 7244, 7206.6, 7210.8], [None, 7207.5, 7219.4, 7190.0, 7217.0], [None, 7227.5, 7232.1, 7190.0, 7190.0]]

def arg_parser(web_inputs=None):
    args_dict = web_inputs
    if not web_inputs:
        parser = argparse.ArgumentParser(description='Candle bot')
        parser.add_argument('ex_and_pair', type=str, help='Exchange and pair')
        parser.add_argument('-a', '--amount_unit', type=str, default='0-', help='Amount in base/quote currency for order (default: 0-)')
        parser.add_argument('-i', '--ohlc_interval', type=str, default='1m', help='Candle interval')
        parser.add_argument('-t', '--threshold', type=str, default='0.08-0.03-0.03-0.08-0.08-0.1', help='List of hyphen-seperated percentage thresholds. Default: 0.08-0.03-0.03-0.08-0.08-0.1')
        parser.add_argument('-p', '--threshold_percent', type=float, default=0, help='Percentage of incr/decr price of opposite order. Default: 0')
        parser.add_argument('-c', '--cutloss_chain', type=str, default='t-c', help='Cutloss chain for first and opposite orders. Default: t-c')
        parser.add_argument('-to', '--order_timeout', type=float, default=0, help='Timeout for order cutloss timeout. Default: 0')
        parser.add_argument('-H', '--historical_candle', type=bool, nargs='?', const=True, default=False, help='Examine historical candle instead of running cdl')
        parser.add_argument("-P", '--parallel_order', type=bool, nargs='?', const=True, default=False, help="Placing orders parallelly")
        parser.add_argument('-D', '--dry_run', type=bool, nargs='?', const=True, default=False, help='Dry run')
        parser.add_argument('-L', '--limit_filled_timeout_and_retry', type=str, help='limit cutloss: threshold-timeout(in minute)-retry(example: 2-10-3). This is required for cutloss_mechanism "c". Mutex with -M')
        parser.add_argument('-X', '--multiplied_amount_cutloss', type=str, help='multiplied amount cutloss: incr/decr_price_percentage-sell/buy_threshold-amount_times (example: 1-0.07-2). This is required for cutloss_mechanism "d"')
        parser.add_argument('--pseudo', type=bool, nargs='?', const=True, default=False, help='Dry run with a given list of ohlcv data. Valid only with -D')

        args = parser.parse_args()
        args_dict = vars(args)

    # end if
    ex_id = args_dict.get('ex_and_pair')[:3]
    pair = args_dict.get('ex_and_pair')[3:]

    if args_dict.get('limit_filled_timeout_and_retry'):
        w_threshold, w_timeout, w_retry = args_dict.get('limit_filled_timeout_and_retry').split('-')
        w_threshold = float(w_threshold) / 100
        # w_timeout in second
        w_timeout = float(w_timeout) * 60
        w_retry = int(float(w_retry))
    else:
        w_threshold = 0
        w_timeout = 0
        w_retry = 0

    if args_dict.get('multiplied_amount_cutloss'):
        delta_price_percentage, price_threshold, amount_times = args_dict.get('multiplied_amount_cutloss').split('-')
        delta_price_percentage = float(delta_price_percentage) / 100
        price_threshold = float(price_threshold) / 100
        amount_times = float(amount_times)
    else:
        delta_price_percentage = 0
        price_threshold = 0
        amount_times = 0

    # Main bot args
    args_dict.update({'ex_id': ex_id, 'pair': pair})
    args_dict.update({'order_timeout': float(args_dict.get('order_timeout')) * 60})
    args_dict.update({'w_threshold': w_threshold, 'w_timeout': w_timeout, 'w_retry': w_retry})
    args_dict.update({'delta_price_percentage': delta_price_percentage, 'price_threshold': price_threshold, 'amount_times': amount_times})
    return args_dict

class CandleBot(multi_ways_bot):
    NOISE_FILTER = Decimal('0.0001') #%
    def __init__(self):
        multi_ways_bot.__init__(self)
        # for web version
        self._stop_scanning = False
        self._terminate = False
        self._socketio = None
        self._channel_uuid = ''
        # bot field
        self._args = None
        self._pair = None
        self._ex_id = None
        self._initial_amount = None
        self._amount = 0.0
        self._timer = None
        self._logger = logging.getLogger('candle_bot')
        self._trade_threads = []
        # Exchange field
        self._api_file_key = '_candle_bot'
        self._ex_api = None
        self._ohlc_interval = ''
        self._interval_in_sec = 0
        # save status
        self._prev_timestamp = 0
        self._prev_ha_open = Decimal('0')
        self._prev_ha_close = Decimal('0')
        # prediction thresholds
        self._red_low_tail_thres = Decimal('0.08')
        self._red_high_tail_thres = Decimal('0.03')
        self._green_low_tail_thres = Decimal('0.03')
        self._green_high_tail_thres = Decimal('0.08')
        self._ha_body_width_thres = Decimal('0.08')
        self._low_high_thres = Decimal('0.1')

    def __config_logger(self):
        self._logger.setLevel(logging.DEBUG)
        script_path = os.path.dirname(os.path.realpath(__file__))
        file_name = 'candle_bot_cmd' + datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        if self._socketio:
            file_name = 'candle_bot_web_' + self._channel_uuid
        # create file handler which logs even debug messages
        fh = logging.FileHandler(script_path + '/../web/logs/' + str(file_name) + '.log')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self._logger.addHandler(fh)

    def _interruptible_waiting(self, waiting_time):
        if waiting_time > 3:
            while not self._terminate and waiting_time > 0:
                time.sleep(1)
                waiting_time -= 1
        else:
            time.sleep(waiting_time)

    def _predict(self, open, high, low, close, initialize=False):
        open = Decimal(str(open))
        high = Decimal(str(high))
        low = Decimal(str(low))
        close = Decimal(str(close))

        # body_width
        if close > open:
            # green candle
            body_width = 1 - open / close
        else:
            body_width = 1 - close / open
        body_width *= 100 #%

        # ha open
        if initialize:
            ha_open = (open + close) / 2
        else:
            ha_open = (self._prev_ha_open + self._prev_ha_close) / 2

        # ha close
        ha_close = (open + high + low + close) / 4

        # ha high
        ha_high = max(high, ha_open, ha_close)

        # ha low
        ha_low = min(low, ha_open, ha_close)

        # high tail & low tail & ha_body_width
        if ha_close > ha_open: # HA color: GREEN
            high_tail = 1 - ha_close / ha_high
            low_tail = 1 - ha_low / ha_open
            ha_body_width = 1 - ha_open / ha_close
        else: # HA color: RED
            high_tail = 1 - ha_open / ha_high
            low_tail = 1 - ha_low / ha_close
            ha_body_width = 1 - ha_close / ha_open
        high_tail *= 100 #%
        low_tail *= 100 #%
        ha_body_width *= 100 #%

        # low_high
        if high_tail - low_tail > self.NOISE_FILTER:
            low_high = high_tail - low_tail
        else:
            low_high = low_tail - high_tail

        # P-O??? #FIXME is it needed?
        if low_high - ha_body_width > self.NOISE_FILTER:
            p_o = low_high - ha_body_width
        else:
            p_o = ha_body_width - low_high

        # prediction
        prediction = None
        if ha_close > ha_open: # HA color: GREEN
            self._log('HA Color: GREEN', severity='debug')
            if high_tail > self._green_high_tail_thres and \
               low_tail < self._green_low_tail_thres and \
               ha_body_width > self._ha_body_width_thres and \
               low_high > self._low_high_thres:
                prediction = 'UP'
        elif ha_close < ha_open: # HA color: RED
            self._log('HA Color: RED', severity='debug')
            if low_tail > self._red_low_tail_thres and \
               high_tail < self._red_high_tail_thres and \
               ha_body_width > self._ha_body_width_thres and \
               low_high > self._low_high_thres:
                prediction = 'DOWN'

        data = {'body_width': body_width, 'ha_close': ha_close, 'ha_open': ha_open, 'ha_high': ha_high, 'ha_low': ha_low, 'high_tail': high_tail, 'low_tail': low_tail, 'ha_body_width': ha_body_width, 'low_high': low_high, 'P-O': p_o, 'prediction': prediction}
        self._log(data, severity='debug')

        return prediction, ha_open, ha_close

    def _fetch_latest_price(self, side='sell', get_ask_bid=False):
        ask_volume, bid_volume = None, None
        while ask_volume == None or bid_volume == None:
            ask_volume, bid_volume = self._ex_api.fetch_order_book(self._pair, 1)
        ask = float(ask_volume[0])
        bid = float(bid_volume[0])
        if get_ask_bid:
            return (ask, bid)
        # Get calculated price for each pair
        price = ask if side == 'sell' else bid
        return price

    def _place_order_and_cutloss_check(self, trade_id, trade_info, amount, side, price, price_type, cutloss_check_type, ret_queue=None):
        self._log('_place_order_and_cutloss_check: amount={}, side={}, price={}, price_type={}, cutloss_check_type={}'.format(amount, side, price, price_type, cutloss_check_type), severity='debug')
        if self._args.get('dry_run'):
            retval = ('Success', 0, 0)
            if ret_queue:
                ret_queue.put(retval)
            return retval

        order_info_list = []
        an_order_info = {}
        order_id = self._ex_api.create_order(self._pair, 'limit', side, amount, price)
        if 'invalid_cmd' == order_id or 'rate_limit' == order_id:
            self._log('TRADE {}, place {} order failed, {}'.format(trade_id, side, order_id), severity='error')
            retval = ('Canceled', 0, 0)
            if ret_queue:
                ret_queue.put(retval)
            return retval
        else:
            self._log('TRADE {}, place {} order: {}, amount={}, price={}'.format(trade_id, side, order_id, amount, price))

        num_orders = int(trade_info.get('NumOrders')) + 1
        order_info = eval("{{'Order{i}': {{'OrderID': order_id, 'Side': side, 'Cutloss': cutloss_check_type, 'Amount': amount, 'Price': price, 'Status': 'open'}}}}".format(i=num_orders))
        trade_info.update({'NumOrders': num_orders})
        trade_info.update(order_info)
        socket_emit(trade_info, self._socketio, self._channel_uuid, 'trade_order_info')

        old_order_id = order_id
        order_id, filled_amount, avg_price = self._cutloss_check(cutloss_check_type, self._ex_api, order_id, self._pair, 'limit', side, price_type, amount, price, 1)
        retval = ('Canceled', filled_amount, avg_price)
        progress = self._ex_api.fetch_order_progress(order_id)
        order_status = progress['order_status']
        if order_status == 'canceled':
            self._log('TRADE {}, {} order {} is canceled'.format(trade_id, side, order_id), severity='error')
        elif cutloss_check_type != 't' and order_status == 'open':
            self._log('TRADE {}, {} order {} still "open" after cutloss "c/d"!?!'.format(trade_id, side, order_id), severity='error')
        else: # Success/Cutloss
            TradeStatus = 'Success'
            if old_order_id != order_id:
                TradeStatus = 'Cutloss'
            retval = (TradeStatus, filled_amount, avg_price)

        # return
        if ret_queue:
            ret_queue.put(retval)
        return retval

    def _amount_calc(self, price):
        ordering_unit = self._pair[:self._pair.find('/')]
        second_coin = self._pair[self._pair.find('/')+1:]
        if self._unit == ordering_unit:
            return float(self._initial_amount)
        elif self._unit == second_coin:
            ordering_pre_amount = Decimal(str(self._initial_amount))
            price = Decimal(str(price))
            return float(ordering_pre_amount / price)
        else:
            self._log("The unit {} not in pair {}".format(self._unit, self._pair), severity='error')
            return None

    def _place_trade(self, prediction):
        args = self._args
        parallel = args.get('parallel_order')
        oppo_price_percent = Decimal(str(args.get('threshold_percent'))) / 100
        cutloss_check_type, oppo_cutloss_check_type = args.get('cutloss_chain').split('-')

        trade_id = str(uuid.uuid4())[::5]
        trade_time = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
        trade_info = {'_id': trade_id, 'TradeTime': trade_time, 'Prediction': prediction, 'TradeStatus': 'Pending', 'NumOrders': 0}

        side = 'buy' if prediction == 'UP' else 'sell'
        price_type, oppo_side, oppo_price_type, oppo_price_delta_wise = ('ask', 'buy', 'bid', -1) if side == 'sell' else ('bid', 'sell', 'ask', 1)

        self._log('START {} TRADE {}, PREDICTION: {}'.format('PARALLEL' if parallel else 'SERIAL', trade_id, prediction))

        propagate_price = False
        # First order
        cur_price = self._fetch_latest_price(side)
        if not self._amount:
            self._amount = self._amount_calc(cur_price)
            self._log('amount {} calculated at {} price {}'.format(self._amount, price_type, cur_price))
        threads = []
        inputs = [trade_id, trade_info, self._amount, side, cur_price, price_type, cutloss_check_type]
        if parallel:
            first_queue = Queue(maxsize=1)
            inputs.append(first_queue)
            first_thread = Thread(target=self._place_order_and_cutloss_check, args=(inputs))
            threads.append((first_thread, first_queue))
        else:
            # Only propagate price to the 2nd one if serial and not timeout cutloss
            if cutloss_check_type != 't':
                propagate_price = True
            trade_status, filled_amount, avg_price = self._place_order_and_cutloss_check(*inputs)
            if trade_status == 'Canceled':
                self._log('STOP SERIAL TRADE {}, CUTLOSS FIRST ORDER ({}) FAILED\n'.format(trade_id, side), severity='error')
                return False

        # Second order
        if not propagate_price:
            # Get current ask or bid price
            cur_price = self._fetch_latest_price(oppo_side)
            cur_price = Decimal(str(cur_price))
        else:
            # Propagate price
            cur_price = Decimal(str(avg_price))
        cur_price = float(cur_price + oppo_price_delta_wise * (cur_price * oppo_price_percent))
        inputs = [trade_id, trade_info, self._amount, oppo_side, cur_price, oppo_price_type, oppo_cutloss_check_type]
        if parallel:
            second_queue = Queue(maxsize=1)
            inputs.append(second_queue)
            second_thread = Thread(target=self._place_order_and_cutloss_check, args=(inputs))
            threads.append((second_thread, second_queue))
        else:
            trade_status, _, _ = self._place_order_and_cutloss_check(*inputs)
            if trade_status == 'Canceled':
                self._log('STOP SERIAL TRADE {}, CUTLOSS SECOND ORDER ({}) FAILED\n'.format(trade_id, oppo_side), severity='error')
                return False

        if parallel:
            for t, _ in threads:
                t.start()
            trade_ok = True
            for t, q in threads:
                t.join()
                trade_status, _, _ = q.get()
                q.task_done()
                if trade_status == 'Canceled':
                    self._log('PARALLEL TRADE {}, {} ORDER {} FAILED'.format(trade_id, side, order_id), severity='error')
                    trade_ok = False
            if not trade_ok:
                self._log('STOP PARALLEL TRADE {}, at least an order failed\n'.format(trade_id))
                return False

        self._log('STOP {} TRADE {}, SUCCESSFUL\n'.format('PARALLEL' if parallel else 'SERIAL', trade_id))
        return True

    def _init_ha_open_close(self, history_cdl_num=5):
        self._log('_init_ha_open_close: initializing', severity='debug')
        ohlc_list = self._ex_api.fetch_ohlcv(self._pair, self._ohlc_interval, tf_index=0)[-history_cdl_num:]
        _, self._prev_ha_open, self._prev_ha_close = self._predict(*(ohlc_list[0])[1:5], initialize=True)
        for i in range(history_cdl_num - 1):
            _, self._prev_ha_open, self._prev_ha_close = self._predict(*(ohlc_list[i+1])[1:5])
        self._log('_init_ha_open_close: finish! ha_open={}, ha_close={}\n'.format(self._prev_ha_open, self._prev_ha_close), severity='debug')
        return ohlc_list[-1][0]

    def _predict_and_place_trade(self, ohlc=None):
        if not ohlc:
            ohlc = self._ex_api.fetch_running_ohlcv(self._pair, self._ohlc_interval)
        self._log('_predict_and_place_trade: candle: {}'.format(ohlc))
        prediction, self._prev_ha_open, self._prev_ha_close = self._predict(*ohlc[1:5])
        if prediction:
            if not float(self._initial_amount):
                return
            trade_thread = Thread(target=self._place_trade, args=(prediction, ))
            trade_thread.start()
            #self._trade_threads.append(trade_thread)
        else:
            self._log('Prediction: None\n')

    def _check_signal_from_candle(self):
        self._log('_check_signal_from_candle: Starting\n')
        self._prev_timestamp = self._init_ha_open_close()
        self._log('_check_signal_from_candle: Checking next candle\n\n')
        after_init_ha_open_close = True
        candle_cnt = 0
        while not self._terminate and not self._stop_scanning:
            if self._args.get('dry_run') and self._args.get('pseudo'):
                if candle_cnt >= len(ohlc_dryrun):
                    return
                ohlc = ohlc_dryrun[candle_cnt]
                candle_cnt += 1
                self._predict_and_place_trade(ohlc)
            else:
                # Uses historical candle to calculate prediction
                if self._args.get('historical_candle'):
                    ohlc = self._ex_api.fetch_ohlcv(self._pair, self._ohlc_interval)
                    timestamp = ohlc[0]
                    if timestamp == self._prev_timestamp:
                        self._interruptible_waiting(5)
                        continue
                    # Record new candle using timestamp
                    self._prev_timestamp = timestamp
                    self._predict_and_place_trade(ohlc)
                # Uses running candle to calculate prediction
                else:
                    if after_init_ha_open_close:
                        ohlc = self._ex_api.fetch_ohlcv(self._pair, self._ohlc_interval)
                        timestamp = ohlc[0]
                        if timestamp > self._prev_timestamp:
                            self._log('Specical case! The running candle after HA_open initialization became historical one', severity='warn')
                            self._prev_timestamp = timestamp
                        else:
                            after_init_ha_open_close = False
                            ohlc = self._ex_api.fetch_running_ohlcv(self._pair, self._ohlc_interval)
                            self._timer = RepeatTimer(self._interval_in_sec, self._predict_and_place_trade)
                            self._timer.setDaemon(True)
                            self._timer.start()
                        self._predict_and_place_trade(ohlc)
                    else:
                        # At this time, this method will do nothing
                        self._interruptible_waiting(5)
        else:
            if self._timer:
                self._timer.cancel()
            if self._stop_scanning:
                self._log('STOP SCANNING & PLACING TRADE')
                while len(self._cutlossing) > 0 and not self._terminate:
                    self._log('{} remaining orders'.format(len(self._cutlossing)))
                    time.sleep(2)
            return

    def stop_scanning(self):
        self._stop_scanning = True

    def terminate(self):
        self._terminate = True

    def bot_entry(self, web_inputs=None):
        if web_inputs:
            self._socketio = web_inputs.get('socketio')
            self._channel_uuid = web_inputs.get('uuid')
            self._logger = logging.getLogger(self._channel_uuid)
        args = arg_parser(web_inputs)
        self._args = args

        # Config logger
        self.__config_logger()

        self._log('START THE CANDLE BOT, INITIALIZING...')

        self._ex_id = args.get('ex_id')
        self._pair = args.get('pair')
        self._initial_amount, self._unit = args.get('amount_unit').split('-')
        if self._unit not in self._pair:
            self._log('unit is not in pair {}'.format(self._pair), severity='error')
            return
        self._ohlc_interval = args.get('ohlc_interval')
        thresholds = args.get('threshold').split('-')
        self._red_low_tail_thres = Decimal(thresholds[0]) #%
        self._red_high_tail_thres = Decimal(thresholds[1]) #%
        self._green_low_tail_thres = Decimal(thresholds[2]) #%
        self._green_high_tail_thres = Decimal(thresholds[3]) #%
        self._ha_body_width_thres = Decimal(thresholds[4]) #%
        self._low_high_thres = Decimal(thresholds[5]) #%

        self._log(args, severity='debug')

        if args.get('dry_run'):
            self._log('================================ DRY RUN ================================\n')

        # init exchange instance
        self._ex_api = exchange(self._ex_id, self._logger, self._socketio, self._channel_uuid, api_file_no=self._api_file_key)
        self._ex_api.register_order_book(self._pair)
        self._ex_api.register_ohlcv(self._pair, self._ohlc_interval)
        self._interval_in_sec = self._ex_api.ohlcv_interval2minute(self._ohlc_interval)
        self._interval_in_sec *= 60

        # Main loop
        self._check_signal_from_candle()

        # Exit bot
        self._log('THE CANDLE BOT EXIT!!')


if __name__ == '__main__':
    a_bot = CandleBot()
    a_bot.bot_entry()
    os._exit(0)
