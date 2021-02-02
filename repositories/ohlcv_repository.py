import sys
import os
from datetime import datetime

from zope.interface import named

dir_path = os.path.dirname(os.path.realpath(__file__))
lib_path = dir_path + '/../libs'
sys.path.append(lib_path)
sys.path.append(dir_path)
from libdb import DB
from config_db import *
import csv
from binance.client import Client

class OhlcvRepository:
    def __init__(self):
        self._database_name = 'binance_data'
        self._db = DB(server=FANSIPAN_DB, port=FANSIPAN_DB_PORT,
                      username=FANSIPAN_DB_USERNAME, passwd=FANSIPAN_DB_PASSWD)
        self._db.create_database(self._database_name)
        self.client = Client()

    def insert_document(self, collection, data={}):
        self._db.insert_document(collection, data)
        return True

    def query_document(self, collection, query, find_one=False):
        return self._db.query_document(collection, query, find_one)

    def update_document(self, collection, query, new_value):
        return self._db.update_document(collection, query, new_value)

    def delete_document(self, collection, query):
        return self._db.delete_document(collection, query)

    def query_count(self, collection, query):
        coll = self._db.get_collection(collection)
        return coll.count_documents(query)

    """
    Fetch list candelstick data from DB
    interval: interval of cdl (minute unit, e.g. 1, 3, 5, 10, 60)
    Fetch data from from_time to to_time (epoch timestamp)
    """
    def fetch_cdl_list(self, pair, interval, from_time, to_time=None):
        # Get actual start time which is appropriate with interval
        # For example cdl 5m, from_time must be devisible by 5
        if 'm' in str(interval):
            interval = str(interval).replace('m', '')
        interval = int(interval)
        div = int((int(from_time) / 60000) % interval)
        if div == 0:
            from_time = from_time
        else:
            from_time = (int(int(from_time) / 60000) + interval - div) * 60000
        # Get 1m_cdl list
        if not to_time:
            cdl_1m_list = list(self.query_document(pair, {'_id': {"$gte": from_time}}))
        else:
            cdl_1m_list = list(self.query_document(pair, {'_id': {"$gte": from_time, '$lt': to_time}}))

        # Build cdl_list of inputed interval from 1m_cdl
        cdl_list_group = []
        if interval == 1:  # case cdl-1m
            cdl_list_group = [[cdl_1m_list[i]] for i in range(0, len(cdl_1m_list))]
        else:  # case cdl > 1m, cannot use 'if' condition for 1m.
            ref_time = 0
            _data = []
            for index, cdl in enumerate(cdl_1m_list, start=1):
                _time = int(cdl.get('_id'))
                if not ref_time:
                    ref_time = _time
                if _time > (ref_time + interval * 60000):
                    cdl_list_group.append(_data)
                    ref_time = ref_time + interval * 60000
                    _data = []
                _data.append(cdl)
                if index >= len(cdl_1m_list):
                    cdl_list_group.append(_data)
        data = []
        for group in cdl_list_group:
            if 0 < len(group) <= interval:
                item = []
                # First item _Id is _id of group
                item.append(group[0]['_id'])
                item.append(group[0]['open'])
                total_vol = 0
                high = group[0]['high']
                low = group[0]['low']
                for cdl in group:
                    total_vol += cdl['vol']
                    if cdl['high'] > high:
                        high = cdl['high']
                    if cdl['low'] < low:
                        low = cdl['low']
                item.append(high)
                item.append(low)
                item.append(group[-1]['close'])
                item.append(total_vol)
                data.append(item)

        return data


    """
    Get data from date1 to date2
    format date: date_origin = "%Y:%m:%d %H:%M:%S"
    export csv file
    """
    def export_data_csv(self, from_date, to_date, pair):
        date_start = datetime.strptime(from_date,  "%Y:%m:%d %H:%M:%S")
        date_end = datetime.strptime(to_date, "%Y:%m:%d %H:%M:%S")
        time_start = date_start.timestamp() * 1000  # change to mili sec
        time_end = date_end.timestamp() * 1000
        ohlcv_series = self.query_document(pair, {'_id': { "$gte": time_start, '$lte': time_end}})
        # add header csv
        csv_data = []
        header = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        if ohlcv_series:
            for ohlcv in ohlcv_series:
                csv_data.append([datetime.fromtimestamp(ohlcv['_id']/1000), ohlcv['open'], ohlcv['high'], ohlcv['low'], ohlcv['close'], ohlcv['vol']])
        # write file csv
        path = 'reports/{}_from_{}_to_{}.csv'.format(pair.replace('/', ''), int(time_start), int(time_end))
        with open(path, mode='w') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(header)
            for row in csv_data:
                writer.writerow(row)
        return path

    """
    Using REST API to get data from server
    return: a list of candle
    """
    def rest_fetch_cdl_data(self, pair, interval, from_time, to_time=None):
        # print(pair, interval, from_time, to_time)
        TIME_INDEX = 0
        OPEN_INDEX = 1
        HIGH_INDEX = 2
        LOW_INDEX = 3
        CLOSE_INDEX = 4
        VOL_INDEX = 5
        data = []
        if not to_time:
            to_time = from_time + (24*60*60*1000) #fetch 24h cdl if value to_time is None
        # Call rest-api
        klines = self.client.get_historical_klines(pair.replace('/',''), interval , str(from_time), str(to_time))
        if klines:
            for cdl in klines:
                data.append([cdl[TIME_INDEX], float(cdl[OPEN_INDEX]), float(cdl[HIGH_INDEX]), \
                             float(cdl[LOW_INDEX]), float(cdl[CLOSE_INDEX]), float(cdl[VOL_INDEX])])
        return data

    """
    Get trade history
    return: a list of trade ['Time', 'Id', 'Price', 'Volume', 'Side']
    """
    def rest_fetch_trade_history(self, pair, from_time, to_time=None):
        if not to_time:
            to_time = from_time + (12*60*60*1000) #fetch 12h cdl if value to_time is None
        g_pair = str(pair.replace('/',''))
        klines = self.client.aggregate_trade_iter(g_pair, from_time)
        #data = []
        for cdl in klines:
            if to_time and int(cdl.get('T')) > to_time:
                return
            side = 'sell' if cdl.get('m') else 'buy'
            yield [cdl.get('T'), cdl.get('a'), float(cdl.get('p')), float(cdl.get('q')), side]
        #return data

if __name__ == '__main__':
    repository = OhlcvRepository()
    # data = repository.fetch_cdl_list('BTC/USDT', '1m', 1586566860000, 1586649600000)
    data = repository.rest_fetch_trade_history('BTC/USDT', 1588291200000)
    # data = repository.rest_fetch_cdl_data('BTC/USDT', '1m', 1546326300000)
    with open('demo.txt', mode='w') as csv_file:
        for item in data:
            csv_file.write("%s\n" % item)
    # repository.export_data_csv('2020:02:23 00:00:00', '2020:03:11 00:00:00', 'BTC/USDT')
