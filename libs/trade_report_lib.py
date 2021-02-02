import sys
import os
import traceback
import csv
import time
from copy import deepcopy

lib_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(lib_path)
from common import datetime_now
from decimal import Decimal

class TradeReport:
    INSTANCE_FMT = {'_id': '',
                    'InstanceStartTime': '',
                    'InstanceResumeTime': '',
                    'InstanceStopTime': '',
                    'OpenOrderStart': {},
                    'OpenOrderStop': {},
                    'BalanceSnapshots': {},
                    'Trades': {},
                   }
    COIN_FIELDS = {'Coin': None, 'Balance': None, 'PnL': None, 'PriceInTarget': None}
    CSV_HEADER = ['COIN', 'START', 'CURRENT', 'MARGIN', 'PNL', 'PRICE']

    def __init__(self, instance_id, ex_coin_dict={}, db=None, collection=''):
        self._instance_id = instance_id
        self._db = db
        self._coll = collection
        self._query = {'_id': self._instance_id}
        self._use_db = False
        self._started = False
        if self._db and self._coll:
            self._use_db = True
        else:
            self._instance_rp = deepcopy(self.INSTANCE_FMT)
        self._id_ex_coin_dict = {} # {str(id(ex_api1)): {'coin_list': [<coin_list>], 'target': <coin>, }}
        self._id_exapi_map = {}
        self._csv_data = {}
        self._create_id_exapi_map(ex_coin_dict)

    def _create_id_exapi_map(self, ex_coin_dict):
        if ex_coin_dict:
            self._id_ex_coin_dict = {}
            self._id_exapi_map = {}
            for k, v in ex_coin_dict.items():
                id_exapi = k.get_exchange_uuid()
                if not id_exapi:
                    id_exapi = str(id(k))
                id_exapi = '_'.join([k.get_exchange_id(), id_exapi])
                self._id_ex_coin_dict.update({id_exapi: v})
                self._id_exapi_map.update({id_exapi: k})

    def init_exchange_coin_dict(self, ex_coin_dict):
        self._create_id_exapi_map(ex_coin_dict)

    def _register_ticker_price(self):
        for id_exapi in self._id_ex_coin_dict:
            ex = self._id_exapi_map.get(id_exapi)
            target = self._id_ex_coin_dict[id_exapi].get('target', '')
            if not target:
                continue
            for coin in self._id_ex_coin_dict[id_exapi].get('coin_list', []):
                pair = ex.get_valid_pair_from_2coins(coin, target)
                if pair:
                    ex.register_ticker_info(pair)

    def get_instance_report(self):
        return deepcopy(self._instance_rp)

    def initiate_instance_report(self):
        if self._started:
            return
        self._register_ticker_price()
        self._started = True
        if self._use_db:
            saved_instance_rp = self._db.query_document(self._coll, self._query, find_one=True)
            dt_now = datetime_now()
            if saved_instance_rp:
                self._instance_rp = deepcopy(saved_instance_rp)
                self._instance_rp.update({'InstanceResumeTime': dt_now})
                self._db.update_document(self._coll, self._query, {'InstanceResumeTime': dt_now})
            else:
                self._instance_rp = deepcopy(self.INSTANCE_FMT)
                self._instance_rp.update({'_id': self._instance_id, 'InstanceStartTime': dt_now})
                self._db.insert_document(self._coll, self._instance_rp)

    def finish_instance_report(self):
        if not self._started:
            return
        self._started = False
        if self._use_db:
            self._db.update_document(self._coll, self._query, {'InstanceStopTime': datetime_now()})

    def record_open_orders(self, open_orders: dict, when='start'):
        if not self._started:
            return
        if when.lower() not in ['start', 'stop']:
            return
        pos = 'OpenOrderStart' if when == 'start' else 'OpenOrderStop'
        self._instance_rp.update({pos: open_orders})
        if self._use_db:
            self._db.update_document(self._coll, self._query, {pos: open_orders})

    # If prune=True, BalanceSnapshots only keeps 3 snapshots:
    # 1st and 2 latest ones.
    def take_balance_snapshot(self, prune=False):
        if not self._started:
            return None
        if not self._id_ex_coin_dict:
            return None
        now = datetime_now()
        for id_exapi in self._id_ex_coin_dict:
            snapshot = {}
            ex_api = self._id_exapi_map.get(id_exapi)
            try:
                bl = ex_api.fetch_balance()
            except:
                continue
            coin_list = self._id_ex_coin_dict[id_exapi].get('coin_list', [])
            target = self._id_ex_coin_dict[id_exapi].get('target', '')
            if not coin_list:
                continue
            snapshot[now] = {}
            total = 0
            calc_pnl = True
            if not self._instance_rp['BalanceSnapshots'].get(id_exapi):
                self._instance_rp['BalanceSnapshots'][id_exapi] = []
                calc_pnl = False
            for coin in coin_list:
                snapshot[now][coin] = self.COIN_FIELDS.copy()
                snapshot[now][coin].update({'Coin': coin})
                snapshot[now][coin].update({'Balance': bl.get(coin, {}).get('total', 0.0)})
                self._csv_data.update({coin: []})
                if not calc_pnl:
                    continue
                start_snapshot = self._instance_rp['BalanceSnapshots'][id_exapi][0]
                _, start_balance = list(start_snapshot.items())[0]
                snapshot[now][coin]['PnL'] = float(Decimal(str(snapshot[now][coin]['Balance'])) - Decimal(str(start_balance[coin]['Balance'])))

                if not target:
                    continue
                if coin == target:
                    snapshot[now][coin]['PriceInTarget'] = 1
                    self._csv_data[coin] = [start_balance[coin]['Balance'], snapshot[now][coin]['Balance'],
                                            snapshot[now][coin]['PnL'], snapshot[now][coin]['PnL'] , 1]
                    total += snapshot[now][coin]['PnL']
                    continue
                pair = ex_api.get_valid_pair_from_2coins(coin, target)
                max_retries = 5
                cur_price = ex_api.fetch_ticker_price(pair)
                retries = max_retries
                while not cur_price and retries > 1:
                    time.sleep(0.5)
                    cur_price = ex_api.fetch_ticker_price(pair)
                    retries -= 1
                if not cur_price:
                    print(f'WARN {id_exapi} could not fetch ticker price for {pair} after {max_retries} tries')
                    cur_price = 1.0

                snapshot[now][coin]['PriceInTarget'] = cur_price
                self._csv_data[coin] = [start_balance[coin]['Balance'], snapshot[now][coin]['Balance'],
                                        snapshot[now][coin]['PnL'],  float(Decimal(str(snapshot[now][coin]['PnL'])) * Decimal(str(cur_price))), cur_price]
                if target == pair.split('/')[0]: # baseAsset
                    total += (snapshot[now][coin]['PnL'] / cur_price)
                else: # quoteAsset
                    total += (snapshot[now][coin]['PnL'] * cur_price)
            if target:
                snapshot[now]['TotalPnL'] = self.COIN_FIELDS.copy()
                snapshot[now]['TotalPnL'].update({'Coin': target})
                snapshot[now]['TotalPnL'].update({'PnL': total})
            self._instance_rp['BalanceSnapshots'][id_exapi].append(deepcopy(snapshot))
            if prune:
                num_snapshots = len(self._instance_rp['BalanceSnapshots'][id_exapi])
                if num_snapshots == 4:
                    self._instance_rp['BalanceSnapshots'][id_exapi].pop(1)
                elif num_snapshots > 4:
                    tmp_list = []
                    tmp_list.append(self._instance_rp['BalanceSnapshots'][id_exapi].pop(0))
                    tmp_list.append(self._instance_rp['BalanceSnapshots'][id_exapi].pop(-2))
                    tmp_list.append(self._instance_rp['BalanceSnapshots'][id_exapi].pop(-1))
                    self._instance_rp['BalanceSnapshots'][id_exapi] = deepcopy(tmp_list)
        # END for
        if self._use_db:
            self._db.update_document(self._coll, self._query, {'BalanceSnapshots': self._instance_rp['BalanceSnapshots']})
            # TODO: write to csv file
            # file_csv = f'./data/pnl_{self._instance_id}.csv'
            # self.write_balance_report_to_csv(file_csv, self.CSV_HEADER)

    def add_trade_to_report(self, trade_id, trade_info: dict):
        if not self._started:
            return
        if self._instance_rp['Trades'].get(trade_id):
            return
        self._instance_rp['Trades'][trade_id] = trade_info
        if self._use_db:
            self._db.update_document(self._coll, self._query, {'Trades': self._instance_rp['Trades']})

    def update_trade_info(self, trade_id, update_info: dict):
        if not self._started:
            return
        if not update_info:
            return
        if not self._instance_rp['Trades'].get(trade_id):
            return
        self._instance_rp['Trades'][trade_id].update(update_info)
        if self._use_db:
            self._db.update_document(self._coll, self._query, {'Trades': self._instance_rp['Trades']})

    def get_trade_info(self, trade_id, key=None):
        if not self._started:
            return None
        if not self._instance_rp['Trades'].get(trade_id):
            return None
        if not key:
            return self._instance_rp['Trades'][trade_id]
        return self._instance_rp['Trades'][trade_id].get(key)

    def write_trade_report_to_csv(self, file_path, header: list=[], margin=0, mode='w'):
        pass
        #if not self._trades['report']:
        #    return
        #if header:
        #    fields = header
        #else:
        #    fields = self._trades['fields']
        #with open(file_path, mode=mode) as csv_file:
        #    if margin > 0 and isinstance(margin, int):
        #        csv_file.write('\n' * margin)
        #    writer = csv.DictWriter(csv_file, fieldnames=fields)
        #    writer.writeheader()
        #    for trade_id in self._trades['report']:
        #        writer.writerow(self._trades['report'][trade_id])

    def write_balance_report_to_csv(self, file_path, header: list=[], margin=0, mode='w'):
        data = []
        tt_pnl = Decimal('0')
        tt_init_balance = Decimal('0')
        print('data', self._csv_data)
        for coin, dt in self._csv_data.items():
            if len(dt) < 1:
                dt = [0]*5
            if len(dt) >= 3:
                tt_pnl += Decimal(str(dt[3]))
                tt_init_balance += Decimal(str(dt[0])) * Decimal(str(dt[4]))
            data.append([coin] + dt)
        data.append(['', '', '', 'Total', float(tt_pnl), ''])
        if not float(tt_init_balance):
            data.append(['', '', '', '%PNL', '', ''])
        else:
            data.append(['', '', '', '%PNL', round(float((tt_pnl/tt_init_balance)*Decimal('100')),6), ''])
        with open(file_path, mode=mode) as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(header)
            for row in data:
               writer.writerow(row)
