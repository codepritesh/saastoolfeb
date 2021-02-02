import sys
import os
import collections
from decimal import Decimal
import ta
import numpy as np
import pandas as pd

lib_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(lib_path)
sys.path.append(lib_path + '/../repositories')
from ohlcv_repository import OhlcvRepository

def makehash():
    return collections.defaultdict(makehash)


class Indicator:
    def __init__(self, ex_api, logger=None, socketio=None, channel_uuid=''):
        self._logger = logger
        self._socketlog = [socketio, channel_uuid]
        self._ex_api = ex_api
        self._ohlcv_repository = OhlcvRepository()
        self.indicator_data = makehash()
        self.indicator_data['supp_resist'] = {}
        self.indicator_data['moving_average'] = {}
        self.indicator_data['rsi'] = {}

    def __calc_support_resistance(self, pair, supp_resist='support', initial=False, time_query=None, input_cdl_list=None):
        interval = self.indicator_data['supp_resist'][pair]['interval']
        swing_len = self.indicator_data['supp_resist'][pair]['swing_len']
        # get data from db
        # get 60 record for calculate SR
        if input_cdl_list:
            candle_list = input_cdl_list
        elif time_query:
            time_start = time_query - (2 * swing_len + 1) * 60 * 1000
            candle_list = self._ohlcv_repository.fetch_cdl_list(pair, interval, time_start, to_time=time_query)
        elif self._ex_api:
            candle_list = self._ex_api.fetch_ohlcv(pair, interval, tf_index=0)
        else:
            return
        pivot_idx = swing_len
        left_bar = 2 * swing_len - 1
        right_bar = 1
        #print('candle_list ', candle_list)
        if initial:
            num_candles = len(candle_list)
            for _ in range(num_candles-swing_len*2):
                if not self.indicator_data['supp_resist'][pair]['last_resistance']:
                    if right_bar == 1:
                        high_price_list = [c[2] for c in candle_list[-left_bar:]]
                    else:
                        high_price_list = [c[2] for c in candle_list[-left_bar:-right_bar+1]]
                    high_pivot = high_price_list[-pivot_idx]
                    highest_high = max(high_price_list)
                    if high_pivot == highest_high:
                        self.indicator_data['supp_resist'][pair]['last_resistance'] = high_pivot
                if not self.indicator_data['supp_resist'][pair]['last_support']:
                    if right_bar == 1:
                        low_price_list = [c[3] for c in candle_list[-left_bar:]]
                    else:
                        low_price_list = [c[3] for c in candle_list[-left_bar:-right_bar+1]]
                    low_pivot = low_price_list[-pivot_idx]
                    lowest_low = min(low_price_list)
                    if low_pivot == lowest_low:
                        self.indicator_data['supp_resist'][pair]['last_support'] = low_pivot
                if self.indicator_data['supp_resist'][pair]['last_resistance'] and self.indicator_data['supp_resist'][pair]['last_support']:
                    return
                left_bar += 1
                right_bar += 1
        else:
            period_candle_list = candle_list[-left_bar:]
            if supp_resist == 'resistance':
                high_price_list = [c[2] for c in period_candle_list]
                high_pivot = high_price_list[-pivot_idx]
                highest_high = max(high_price_list)
                if high_pivot == highest_high:
                    self.indicator_data['supp_resist'][pair]['last_resistance'] = high_pivot

            if supp_resist == 'support':
                low_price_list = [c[3] for c in period_candle_list]
                low_pivot = low_price_list[-pivot_idx]
                lowest_low = min(low_price_list)
                if low_pivot == lowest_low:
                    self.indicator_data['supp_resist'][pair]['last_support'] = low_pivot

    def register_support_resistance(self, pair, swing_len, interval='1m', time_query=None):
        if self.indicator_data['supp_resist'].get(pair):
            return
        if self._ex_api:
            self._ex_api.register_ohlcv(pair, interval)
        self.indicator_data['supp_resist'][pair] = {}
        self.indicator_data['supp_resist'][pair]['swing_len'] = swing_len
        self.indicator_data['supp_resist'][pair]['interval'] = interval
        self.indicator_data['supp_resist'][pair]['last_support'] = None
        self.indicator_data['supp_resist'][pair]['last_resistance'] = None
        self.__calc_support_resistance(pair, initial=True, time_query=time_query)

    def fetch_support(self, pair, time_query=None, input_cdl_list=None):
        if self.indicator_data['supp_resist'].get(pair):
            self.__calc_support_resistance(pair, 'support', time_query=time_query, input_cdl_list=input_cdl_list)
            return self.indicator_data['supp_resist'][pair]['last_support']
        return None

    def fetch_resistance(self, pair, time_query=None, input_cdl_list=None):
        if self.indicator_data['supp_resist'].get(pair):
            self.__calc_support_resistance(pair, 'resistance', time_query=time_query, input_cdl_list=input_cdl_list)
            return self.indicator_data['supp_resist'][pair]['last_resistance']
        return None

    def register_moving_average(self, pair, interval='1m'):
        if self.indicator_data['moving_average'].get(pair):
            return
        if self._ex_api:
            self._ex_api.register_ohlcv(pair, interval, real_time=True)
        self.indicator_data['moving_average'][pair] = {}
        self.indicator_data['moving_average'][pair]['interval'] = interval

    def fetch_moving_average(self, pair, period: int, candle_index=1, ma_type='simple', source='close', time_query=None, input_cdl_list=None):
        if not self.indicator_data['moving_average'].get(pair):
            return None
        interval = self.indicator_data['moving_average'][pair]['interval']
        # Fetch candle list
        if input_cdl_list:
            candle_list = input_cdl_list
        elif time_query:
            time_start = time_query - period * 60 * 1000
            candle_list = self._ohlcv_repository.fetch_cdl_list(pair, interval, time_start, to_time=time_query)
        elif self._ex_api:
            candle_list = self._ex_api.fetch_ohlcv(pair, interval, tf_index=0)
        else:
            return None
        # Calc moving_average
        if ma_type == 'simple':
            first_cdl_period = -(candle_index + period - 1)
            last_cdl_period = -candle_index + 1
            if last_cdl_period == 0:
                candle_in_period = candle_list[first_cdl_period:]
            else:
                candle_in_period = candle_list[first_cdl_period:last_cdl_period]
            #print(first_cdl_period, last_cdl_period, candle_in_period)
            if source == 'close':
                source_in_period = [Decimal(str(cdl[4])) for cdl in candle_in_period]
            elif source == 'open':
                if input_cdl_list:
                    source_in_period = [Decimal(str(cdl[1])) for cdl in candle_in_period]
                else:
                    running_cdl = self._ex_api.fetch_running_ohlcv(pair, interval)
                    candle_in_period = candle_in_period[1:] + [running_cdl]
                    source_in_period = [Decimal(str(cdl[1])) for cdl in candle_in_period]
            elif source == 'volume':
                source_in_period = [Decimal(str(cdl[5])) for cdl in candle_in_period]
            else:
                #TODO
                return None
            #print(source_in_period, period)
            moving_average = float(sum(source_in_period)/Decimal(str(period)))
            return moving_average
        else:
            print('{} not supported'.format(ma_type))
            return None
            
    def register_rsi(self, pair, interval='1m'):
        if self.indicator_data['rsi'].get(pair):
            return
        if self._ex_api:
            self._ex_api.register_ohlcv(pair, interval)
        self.indicator_data['rsi'][pair] = {}
        self.indicator_data['rsi'][pair]['interval'] = interval

    def fetch_rsi(self, pair, period: int, candle_index=1, source='close', time_query=None, input_cdl_list=None):
        if not self.indicator_data['rsi'].get(pair):
            return None
        interval = self.indicator_data['rsi'][pair]['interval']
        # Fetch candle list
        if input_cdl_list:
            candle_list = input_cdl_list
        elif time_query:
            time_start = time_query - period * 60 * 1000
            candle_list = self._ohlcv_repository.fetch_cdl_list(pair, interval, time_start, to_time=time_query)
        elif self._ex_api:
            candle_list = self._ex_api.fetch_ohlcv(pair, interval, tf_index=0)
        else:
            return None
        # Calc rsi
        last_cdl_period = -candle_index + 1
        if last_cdl_period == 0:
            candle_in_period = candle_list
        else:
            candle_in_period = candle_list[:last_cdl_period]
        if source == 'close':
            source_in_period = [Decimal(str(cdl[4])) for cdl in candle_in_period]
        elif source == 'open':
            running_cdl = self._ex_api.fetch_running_ohlcv(pair, interval)
            candle_in_period = candle_in_period[1:] + [running_cdl]
            source_in_period = [Decimal(str(cdl[1])) for cdl in candle_in_period]
        else:
            #TODO
            return None
        change = [j-i for i, j in zip(source_in_period[:-1], source_in_period[1:])]
        gain = [i if i >= 0 else 0 for i in change]
        loss = [-1*i if i < 0 else 0 for i in change]
        def rma(input_list, alpha):
            alpha = Decimal(str(alpha))
            rma = Decimal(str(input_list[0]))
            for element in input_list:
                rma = (element + (alpha - Decimal(1)) * rma) / alpha
            return rma
        avgGain = rma(gain, period)
        avgLoss = rma(loss, period)
        rs = avgGain / avgLoss
        rsi = Decimal(100) - (Decimal(100) / (Decimal(1) + rs))
        return float(rsi)

    def register_macd(self, pair, interval='1m'):
        if self.indicator_data['macd'].get(pair):
            return
        if self._ex_api:
            self._ex_api.register_ohlcv(pair, interval)
        self.indicator_data['macd'][pair] = {}
        self.indicator_data['macd'][pair]['interval'] = interval

    def fetch_macd(self, pair, candle_index=1, flen=12, slen=26, signal_sm=9, source='close', runtime=False, time_query=None, input_cdl_list=None):
        if not self.indicator_data['macd'].get(pair):
            return None
        interval = self.indicator_data['macd'][pair]['interval']
        # Fetch candle list
        if input_cdl_list:
            candle_list = input_cdl_list
        elif time_query:
            time_start = time_query - period * 60 * 1000
            candle_list = self._ohlcv_repository.fetch_cdl_list(pair, interval, time_start, to_time=time_query)
        elif self._ex_api:
            candle_list = self._ex_api.fetch_ohlcv(pair, interval, tf_index=0)
        else:
            return None

        #print(first_cdl_period, last_cdl_period, candle_in_period)
        if source == 'close':
            source_index = 4
        elif source == 'open':
            source_index = 1

        if runtime:
            running_cdl = self._ex_api.fetch_running_ohlcv(pair, interval)
            candle_in_period = candle_list + [running_cdl]
            source_in_period = [cdl[source_index] for cdl in candle_in_period]
        else:
            source_in_period = [cdl[source_index] for cdl in candle_list]

        def ema(input_list, alpha):
            alpha = Decimal(str(2/(alpha + 1)))
            ema = Decimal(str(input_list[0]))
            for element in input_list:
                ema = alpha * Decimal(str(element)) + (Decimal(1) - alpha) * ema
            return float(ema)

        # Fast length
        macd_line = []
        for i in range(slen, len(source_in_period)+1):
            emaslow = ema(source_in_period[:i], slen)
            emafast = ema(source_in_period[:i], flen)
            macd = emafast - emaslow
            macd_line.append(macd)
        signal_latest = ema(macd_line, signal_sm)
        macd_latest = macd_line[-1]
        return macd_latest - signal_latest, macd_latest, signal_latest

    def register_atr_trailing_stop(self, pair, interval='1m'):
        if self.indicator_data['atr_ts'].get(pair):
            return
        if self._ex_api:
            self._ex_api.register_ohlcv(pair, interval)
        self.indicator_data['atr_ts'][pair] = {}
        self.indicator_data['atr_ts'][pair]['interval'] = interval

    def generate_atr_tailing(self, df, ATRperiod, nATRMultip):
        df['ATR'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], ATRperiod)
        nLoss = nATRMultip * df['ATR']
        xATRTrailingStop = np.zeros(len(nLoss))
        pos = np.zeros(len(nLoss))
        for i in range(ATRperiod - 1, len(xATRTrailingStop)):
            if df['close'][i] > xATRTrailingStop[i - 1] and df['close'][i - 1] > xATRTrailingStop[i - 1]:
                xATRTrailingStop[i] = max(xATRTrailingStop[i - 1], df['close'][i] - nLoss[i])
            elif df['close'][i] < xATRTrailingStop[i - 1] and df['close'][i - 1] < xATRTrailingStop[i - 1]:
                xATRTrailingStop[i] = min(xATRTrailingStop[i - 1], df['close'][i] + nLoss[i])
            elif df['close'][i] > xATRTrailingStop[i - 1]:
                xATRTrailingStop[i] = df['close'][i] - nLoss[i]
            else:
                xATRTrailingStop[i] = df['close'][i] + nLoss[i]

            if df['close'][i - 1] < xATRTrailingStop[i - 1] and df['close'][i] > xATRTrailingStop[i - 1]:
                # Green
                pos[i] = 1
            elif df['close'][i - 1] > xATRTrailingStop[i - 1] and df['close'][i] < xATRTrailingStop[i - 1]:
                # Red
                pos[i] = -1
            else:
                pos[i] = pos[i - 1]
        df['atr_ts'] = xATRTrailingStop
        df['color'] = pos
        # First 1hour data isn't accuracy because of rma
        # Return data from cdl 60
        return df[60:]

    def fetch_atr_ts(self, pair, ATRperiod, nATRMultip):
        if not self.indicator_data['atr_ts'].get(pair):
            return None
        interval = self.indicator_data['atr_ts'][pair]['interval']
        candle_list = self._ex_api.fetch_ohlcv(pair, interval, tf_index=0)
        candle_list = [i[:6] for i in candle_list]
        df = pd.DataFrame(candle_list, columns=['Time', 'open', 'high', 'low', 'close', 'volume'])
        gen_df = self.generate_atr_tailing(df, ATRperiod, nATRMultip)
        last_item_index = df.shape[0] - 1
        return (int(gen_df['color'][last_item_index]), gen_df['atr_ts'][last_item_index])
