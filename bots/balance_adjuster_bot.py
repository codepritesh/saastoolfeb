import sys
import ccxt
import time
import signal
import re
import os
import uuid
import logging
from threading import Thread, Lock
import argparse
signal.signal(signal.SIGINT, lambda x,y: os._exit(0))
from flask_socketio import SocketIO, emit
from datetime import datetime
from decimal import Decimal
dir_path = os.path.dirname(os.path.realpath(__file__))
lib_path = dir_path+'/../libs'
sys.path.append(lib_path)
from exchange_lib import *
from common import log, socket_emit


def arg_parser(web_inputs=None):
    args_dict = web_inputs
    if not web_inputs:
        parser = argparse.ArgumentParser(description='Nico bot')
        parser.add_argument('ex_and_coin', type=str, help='Exchanges and coins')
        parser.add_argument('fees', type=str, help='Order fees for the coin and target coin')
        parser.add_argument('target_coin', type=str, help='Target coin')
        parser.add_argument('buyback_exchange', type=str, help='Buyback exchange')
        parser.add_argument('-s', '--threshold', type=str, default='0', help='threshold to adjust (default 0)')
        parser.add_argument('-i', '--interval', type=str, default='1', help='Checking interval in minute (default 1m)')
        parser.add_argument('-b', '--buyback', type=bool, nargs='?', const=True, default=False, help='Buyback')
        args = parser.parse_args()
        args_dict = vars(args)
    # end if

    ex_and_coin_list = args_dict.get('ex_and_coin')
    fees = args_dict.get('fees')
    ex_and_coin_fee_dict = {}
    kra_coins = []
    bin_coins = []
    
    for coin, fee in zip(ex_and_coin_list.split('-'), fees.split('-')):
        fee = Decimal(fee)
        ex_id = coin[:3]
        coin_fee_list = ex_and_coin_fee_dict.get(ex_id)
        if not coin_fee_list:
            coin_fee_list = []
        coin_fee_list.append((coin[3:], fee))
        ex_and_coin_fee_dict.update({ex_id: coin_fee_list})

    target_coin = args_dict.get('target_coin')
    buyback_exchange = args_dict.get('buyback_exchange')
    checking_interval = float(args_dict.get('interval'))
    threshold = Decimal(args_dict.get('threshold'))
    buyback = args_dict.get('buyback')
    if buyback == 'False':
        buyback = False
    elif buyback == 'True':
        buyback = True

    return {
            'ex_and_coin_fee': ex_and_coin_fee_dict,
            'checking_interval': checking_interval,
            'target_coin': target_coin,
            'buyback_exchange': buyback_exchange,
            'threshold': threshold,
            'buyback': buyback,
            'account_sell_buy': args_dict['account_sell_buy'],
            'account_buy_sell': args_dict['account_buy_sell'],
            'own_username': args_dict['own_username']
    }


class balance_adjuster_bot():
    def __init__(self):
        self._exchanges = {}
        self._adjuster_coins = {}
        self._adjuster_coins_in_total = {}
        self._target_coin = ''
        self._buyback_exchange = ''
        self._threshold = 0
        self._buyback = True
        self._args = None
        self._terminate = False
        self._socketio = None
        self._channel_uuid = ''
        self._socketdata = {}
        self._logger = logging.getLogger('BalanceAdjusterBot')

    def terminate(self):
        self._terminate = True

    def _config_logger(self):
        self._logger.setLevel(logging.DEBUG)
        script_path = os.path.dirname(os.path.realpath(__file__))
        file_name = 'balance_adjuster_cmd_' + datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        if self._socketio:
            file_name = 'balance_adjuster_web_' + self._channel_uuid
        # create file handler which logs even debug messages
        fh = logging.FileHandler(script_path + '/../web/logs/'+ str(file_name) + '.log')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self._logger.addHandler(fh)

    def _log(self, data='', severity='info'):
        log(data, self._logger, self._socketio, self._channel_uuid, log_severity=severity)

    def _get_target_coin_amount_from_coin(self, coin_fee_pair):
        # Check if this coin is direct coin to target coin
        target_coin_amount = Decimal(0)
        buyback_order_amount = Decimal(0)
        order_info = ()
        if coin_fee_pair[-1] != None:
            coin, fee, pair = coin_fee_pair
            if coin == 'USD':
                exchange_id = 'KRA'
            else:
                exchange_id = pair[:3]
            pair = pair[3:]
            buyback_order_side = ''
            buyback_order_amount = Decimal(0)
            coin_position_in_pair = 1 if pair.find(coin) == 0 else 2
            order_book = self._exchanges.get(exchange_id).fetch_order_book(pair, 1)
            pair_price = 0
            coin_amount = self._adjuster_coins_in_total[coin_fee_pair][2]
            # Return None if price isn't initiated yet
            if order_book == (None, None):
                return False, Decimal(0), ()

            if coin_position_in_pair == 1:
                buyback_order_amount = abs(coin_amount)
                if coin_amount < 0:
                    buyback_order_side = 'buy'
                    pair_price = Decimal(str(order_book[1][0]))
                    target_coin_amount = coin_amount * pair_price * (1 + fee/100)
                elif coin_amount > 0:
                    buyback_order_side = 'sell'
                    pair_price = Decimal(str(order_book[0][0]))
                    target_coin_amount = coin_amount * pair_price * (1 - fee/100)
            elif coin_position_in_pair == 2:
                if coin_amount < 0:
                    buyback_order_side = 'sell'
                    pair_price = Decimal(str(order_book[0][0]))
                    target_coin_amount = coin_amount / pair_price * (1 + fee/100)
                    buyback_order_amount = abs(target_coin_amount)
                elif coin_amount > 0:
                    buyback_order_side = 'buy'
                    pair_price = Decimal(str(order_book[1][0]))
                    target_coin_amount = coin_amount / pair_price * (1 - fee/100)
                    buyback_order_amount = target_coin_amount
            order_info = (pair, buyback_order_side, buyback_order_amount, pair_price)
        # TODO will adapt later to new requirement. Indirect coin, hava intermediate coin
        else:
            coin, fees, _ = coin_fee_pair
            pair1, fee1 = fees[0]
            buyback_order_side1 = ''
            buyback_order_amount1 = Decimal(0)
            coin_position_in_pair = 1 if pair1.find(coin) == 0 else 2
            order_book1 = self._exchanges.get(exchange).fetch_order_book(pair1, 1)
            pair1_price = Decimal(0)
            coin_amount = self._adjuster_coins[exchange][coin_fee_pair][2]
            intermediate_coin_amount = Decimal(0)
            # Return None if price isn't initiated yet
            if order_book1 == (None, None):
                return False, Decimal(0), ()

            if coin_position_in_pair == 1:
                buyback_order_amount1 = abs(coin_amount)
                if coin_amount < 0:
                    buyback_order_side1 = 'buy'
                    pair1_price = Decimal(str(order_book1[1][0]))
                    intermediate_coin_amount = coin_amount * pair1_price * (1 + fee1/100)
                elif coin_amount > 0:
                    buyback_order_side1 = 'sell'
                    pair1_price = Decimal(str(order_book1[0][0]))
                    intermediate_coin_amount = coin_amount * pair1_price * (1 - fee1/100)
            elif coin_position_in_pair == 2:
                if coin_amount < 0:
                    buyback_order_side1 = 'sell'
                    pair1_price = Decimal(str(order_book1[0][0]))
                    intermediate_coin_amount = coin_amount / pair1_price * (1 + fee1/100)
                    buyback_order_amount1 = abs(intermediate_coin_amount)
                elif coin_amount > 0:
                    buyback_order_side1 = 'buy'
                    pair1_price = Decimal(str(order_book1[1][0]))
                    intermediate_coin_amount = coin_amount / pair1_price * (1 - fee1/100)
                    buyback_order_amount1 = intermediate_coin_amount

            pair2, fee2 = fees[1]
            buyback_order_side2 = ''
            buyback_order_amount2 = Decimal(0)
            target_coin_position_in_pair = 1 if pair2.find(self._target_coin) == 0 else 2
            order_book2 = self._exchanges.get(exchange).fetch_order_book(pair2, 1)
            pair2_price = Decimal(0)
            # Return None if price isn't initiated yet
            if order_book2 == (None, None):
                return False, Decimal(0), ()

            if target_coin_position_in_pair == 1:
                if intermediate_coin_amount < 0:
                    buyback_order_side2 = 'sell'
                    pair2_price = Decimal(str(order_book2[0][0]))
                    target_coin_amount = intermediate_coin_amount / pair2_price * (1 + fee2/100)
                    buyback_order_amount2 = abs(target_coin_amount)
                elif intermediate_coin_amount > 0:
                    pair2_price = Decimal(str(order_book2[1][0]))
                    buyback_order_side2 = 'buy'
                    target_coin_amount = intermediate_coin_amount / pair2_price * (1 - fee2/100)
                    buyback_order_amount2 = target_coin_amount
            elif target_coin_position_in_pair == 2:
                buyback_order_amount2 = abs(intermediate_coin_amount)
                if intermediate_coin_amount < 0:
                    buyback_order_side1 = 'buy'
                    pair2_price = Decimal(str(order_book2[1][0]))
                    target_coin_amount = intermediate_coin_amount * pair2_price * (1 + fee2/100)
                elif intermediate_coin_amount > 0:
                    buyback_order_side2 = 'sell'
                    pair2_price = Decimal(str(order_book2[0][0]))
                    target_coin_amount = intermediate_coin_amount * pair2_price * (1 - fee2/100)
            order_info = ((pair1, buyback_order_side1, buyback_order_amount1, pair1_price), (pair2, buyback_order_side2, buyback_order_amount2, pair2_price))
        return True, target_coin_amount, order_info

    """
        Check for all coin adjuster if they can be buyback and still have profit 
    """
    def _adjuster_check(self):
        accumulate_amount_of_target_coin = Decimal(0)
        for coin_fee_pair, value in self._adjuster_coins_in_total.items():
            if coin_fee_pair[0] != self._target_coin:
                status, target_coin_buyback_amount, buyback_order_input = self._get_target_coin_amount_from_coin(coin_fee_pair)
                #self._log('{} {} {}'.format(coin_fee_pair[0], target_coin_buyback_amount, buyback_order_input))
                if not status:
                    self._log('balance_adjuster_botmom---235Not status {}'.format(coin_fee_pair[0]), severity='error')
                    return False
                # (coin, fee, pair): [start, end, adjuster_amount, order_info_adjuster]
                self._adjuster_coins_in_total[coin_fee_pair][-1] = buyback_order_input
                accumulate_amount_of_target_coin += target_coin_buyback_amount
            else:
                accumulate_amount_of_target_coin += value[2]
        self._socketdata.update({'TOTAL_MARGIN': float(accumulate_amount_of_target_coin)})
        log('Total margin in target coin: {}'.format(float(accumulate_amount_of_target_coin)), console=False)
        if accumulate_amount_of_target_coin > self._threshold:
            return True
        return False

    def _cancel_opening_orders_then_buyback(self):
        coin_list = [k[0] for k in self._adjuster_coins_in_total.keys()]
        for ex_obj in self._exchanges.values():
            ex_obj.cancel_all_open_orders(coin_list)
        for coin_fee_pair, value in self._adjuster_coins_in_total.items():
            if coin_fee_pair[0] == self._target_coin:
                continue
            # (coin, fee, pair): [start, end, adjuster_amount, order_info_adjuster]
            if value[-2] != 0:
                # Direct pair
                if coin_fee_pair[-1]:
                    pair, side, amount, price = value[-1]
                    ex = pair[:3]
                    pair = pair[3:]
                    self._exchanges.get(ex).create_order(pair, 'limit', side, float(amount), float(price))
                # TODO later Indirect pair, must have intermediate
                else:
                    for order_info in coin_fee_pair[-1]:
                        pair, side, amount, price = order_info
                        ex = pair[:3]
                        pair = pair[3:]
                        self._exchanges.get(ex).create_order(pair, 'limit', side, float(amount), float(price))


    def _balances_snapshot(self, at):
        if at == 'start':            
            position = 0
        elif at == 'end':
            position = 1

        # Reset total counter before update
        for _, couters in self._adjuster_coins_in_total.items():
            couters[position] = 0

        for ex, coin_info in self._adjuster_coins.items():
            cur_balances = self._exchanges.get(ex).fetch_balance()
            # self._adjuster_coins_in_total: {(coin, fee, pair): [start, end, adjuster_amount, order_info_adjuster]}
            #self._log('coin_info {}'.format(coin_info))
            for coin, _ in coin_info.items():
                if not cur_balances:
                    continue
                if not cur_balances.get(coin):
                    continue
                cur_balance = Decimal(str(cur_balances.get(coin).get('total')))
                self._adjuster_coins[ex][coin][position] = cur_balance
                if at == 'end':
                    start_balance = self._adjuster_coins[ex][coin][0]
                    self._adjuster_coins[ex][coin][2] = cur_balance - start_balance

                coin_fee_pair = ()
                for item in self._adjuster_coins_in_total.keys():
                    if coin == item[0]:
                        coin_fee_pair = item
                        break

                exist_amount = self._adjuster_coins_in_total.get(coin_fee_pair)[position]
                new_amount = exist_amount + cur_balance
                self._adjuster_coins_in_total[coin_fee_pair][position] = new_amount
        if at == 'end':
            for coin_fee_pair in self._adjuster_coins_in_total.keys():
                start_total_balance = self._adjuster_coins_in_total[coin_fee_pair][0]
                cur_total_balance = self._adjuster_coins_in_total[coin_fee_pair][1]
                self._adjuster_coins_in_total[coin_fee_pair][2] = cur_total_balance - start_total_balance

        self._socketdata = {}
        adjuster_coins_data = self._adjuster_coins.copy()
        for ex, coin_info in adjuster_coins_data.items():
            coin_dict = {}
            for coin, values in coin_info.items():
                coin_dict.update({coin: [float(e) if isinstance(e, Decimal) else e for e in values]})
            self._socketdata.update({ex: coin_dict})
        self._socketdata.update({'TOTAL': []})
        self._socketdata.update({'TOTAL_MARGIN': 0})

        print_out = 'EXCHAGES INFO\n'
        for ex, coin_info_list in self._adjuster_coins.items():
            print_out += '{}\n'.format(ex)
            for k, v in coin_info_list.items():
                print_out += '\t{}\t{}\n'.format(k, [float(e) if isinstance(e, Decimal) else e for e in v])
        log(print_out, console=False)
        print_out = '\nTOTAL INFO\n'
        for k, v in self._adjuster_coins_in_total.items():
            value = [float(e) if isinstance(e, Decimal) else e for e in v[:-1]]
            self._socketdata['TOTAL'].append({k[0]: value})
            print_out += '\t{}\t{}\n'.format(k[0], value)
        log("{}+++++++Balance checking at {} interval++++++++++".format(print_out, at), console=False)


    def _find_pair_in_exchange(self, coin1, coin2):
        pair = None
        # Exception case for 'USD' on KRA
        if coin1 == 'USD' or coin2 == 'USD':
            exchange_id = 'KRA'
        else:
            exchange_id = self._buyback_exchange
        market_pairs = [i.get('symbol') for i in self._exchanges.get(exchange_id).api.fetch_markets()]
        pair1 = "{}/{}".format(coin1, coin2)
        pair2 = "{}/{}".format(coin2, coin1)
        if pair1 in market_pairs:
            pair = pair1
        elif pair2 in market_pairs:
            pair = pair2
        # ee.g. KRAUSDT/USD or BINBTC/USDT
        return exchange_id + pair

    def bot_entry(self, web_inputs=None):
        socketio = None
        channel_uuid = ''
        if web_inputs:
            self._socketio = web_inputs.get('socketio')
            socketio = self._socketio
            self._channel_uuid = web_inputs.get('uuid')
            channel_uuid = self._channel_uuid
            self._logger = logging.getLogger(channel_uuid)

        self._args = arg_parser(web_inputs)
        self._target_coin = self._args.get('target_coin')
        self._buyback_exchange = self._args.get('buyback_exchange')
        self._buyback = self._args.get('buyback')
        self._threshold = self._args.get('threshold')
        checking_interval = self._args.get('checking_interval')
        ex_and_coin_fee_dict = self._args.get('ex_and_coin_fee')

        # Config logger
        self._config_logger()

        self._log('START THE BALANCE_ADJUSTER_BOT, INITIALIZING...')
        timer_thread = None
        for exchange_id in ex_and_coin_fee_dict:
            api_file_no = 0
            ex_id = exchange_id
            api_name = ''
            if re.match(r"^.*\d$", ex_id):
                api_file_no = ex_id[-1]
                if ex_id[:-1] == 'BI':
                    ex_id = 'BIN'
                elif ex_id[:-1] == 'KR':
                    ex_id = 'KRA'
            if '1' == str(api_file_no):
                api_name = self._args.get('account_sell_buy')
            elif '2' == str(api_file_no):
                api_name = self._args.get('account_buy_sell')

            exchange_obj = exchange(ex_id, api_name=api_name, own_username=self._args.get('own_username'), api_from_file=api_file_no)
            self._exchanges.update({exchange_id: exchange_obj})

        # Initial adjuster list of coins, each item has format: exchang_id: {coin: [start, end, adjuster_amount]}
        # self._adjuster_coins_in_total: {(coin, fee, pair): [start, end, adjuster_amount, order_info_adjuster]}
        for ex, coin_fee_list in ex_and_coin_fee_dict.items():
            self._adjuster_coins.update({ex: {}})
            for coin, fee in coin_fee_list:
                if coin == self._target_coin:
                    self._adjuster_coins[ex].update({coin: [Decimal(0), Decimal(0), Decimal(0)]})
                    self._adjuster_coins_in_total.update({(coin, fee, None): [Decimal(0), Decimal(0), Decimal(0), ()]})
                    continue
                pair = self._find_pair_in_exchange(self._target_coin, coin)
                if pair:
                    if coin == 'USD':
                        exchange_id = 'KRA'
                    else:
                        exchange_id = pair[:3]
                    self._exchanges.get(exchange_id).register_order_book(pair[3:])
                    self._adjuster_coins[ex].update({coin: [Decimal(0), Decimal(0), Decimal(0)]})
                    if coin not in [i[0] for i in self._adjuster_coins_in_total.keys()]:
                        self._adjuster_coins_in_total.update({(coin, fee, pair): [Decimal(0), Decimal(0), Decimal(0), ()]})
                else:
                    # TODO later. There is no direct pair for the coin and target coin, it must have intermediate coin
                    info = coin[1][1:-1].split('+')
                    intermediate_coin = info[0]
                    pair1 = self._find_pair_in_exchange(intermediate_coin, coin[0])
                    pair2 = self._find_pair_in_exchange(intermediate_coin, self._target_coin)
                    if not pair1 or not pair2:
                        self._log("balance_adjuster_botmom---420Couldn't find pair for {} {} {}".format(intermediate_coin, coin[0], self._target_coin), severity='error')
                    self._exchanges.get(ex).register_order_book(pair1)
                    self._exchanges.get(ex).register_order_book(pair2)
                    fees = ((pair1, info[1]), (pair2, info[2]))
                    self._adjuster_coins[ex].update({(coin[0], fees, None): [Decimal(0), Decimal(0), Decimal(0)]})

        # Take START balances snapshot
        self._balances_snapshot(at='start')
        socket_emit(self._socketdata, self._socketio, self._channel_uuid, 'log_one_way_balance')
        while not self._terminate:
            time.sleep(checking_interval * 60)
            # Take END balances snapshot
            self._balances_snapshot(at='end')
            check_flag = self._adjuster_check()
            socket_emit(self._socketdata, self._socketio, self._channel_uuid, 'log_one_way_balance')
            if check_flag and self._buyback:
                self._log('balance_adjuster_botmom---436**************SIGNAL, ADJUSTING BALANCE ...')
                self._cancel_opening_orders_then_buyback()
            log("-------------------------------------------------------------------------------------------------------------", console=False)

        # end while
        if timer_thread:
            timer_thread.join()
        self._log("balance_adjuster_botmom---443BALANCE_ADJUSTER_BOT EXIT!")
    # end bot_entry mothod
# end balance_adjuster_bot class


if __name__ == "__main__":
    a_bot = balance_adjuster_bot()
    a_bot.bot_entry()
    os._exit(0)
