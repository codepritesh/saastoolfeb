# coding=utf-8
import os
import sys
import traceback
import time
from decimal import Decimal

this_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(this_path)
lib_path = this_path + '/../'
sys.path.append(lib_path)
bots_path = lib_path + '/../bots'
sys.path.append(bots_path)
from binance_common import BinanceUsdtFuturesWssClient, \
                           BinanceCoinFuturesWssClient, \
                           BinanceCommon
from wsclient_common import on_message_handler
from bot_constant import  *
from audit_ws_data import *


class BinanceF(BinanceCommon, AuditData):
    """ High-level library BINANCE Futures """
    FUTURE_TYPE_KW = 'future_type'
    # Future type
    USDT_FUTURES = 'USDT-Futures'
    COIN_FUTURES = 'COIN-Futures'
    # Contract type. Applicable for COIN-Futures
    CURRENT_QUARTER = 'CURRENT_QUARTER'
    NEXT_QUARTER = 'NEXT_QUARTER'
    PERPETUAL = 'PERPETUAL'

    def __init__(self, key, secret=None, logger=None, rest_api=None, *args, **kwargs):
        if kwargs.get(self.FUTURE_TYPE_KW) == self.COIN_FUTURES:
            ws_manager = BinanceCoinFuturesWssClient(key, secret, logger)
            self._future_type = self.COIN_FUTURES
        else:
            ws_manager = BinanceUsdtFuturesWssClient(key, secret, logger)
            self._future_type = self.USDT_FUTURES
        # Support 'CURRENT_QUARTER' by default
        # Only applicable for COIN-Futures
        self._contract_type = self.CURRENT_QUARTER
        BinanceCommon.__init__(self, rest_api=rest_api, ws_manager=ws_manager, logger=logger)

    def set_contract_type(self, contract_type):
        if contract_type not in [self.CURRENT_QUARTER, self.NEXT_QUARTER, self.PERPETUAL]:
            self._log(f'COIN-Futures does not support contract_type {contract_type}!')
            return
        self._contract_type = contract_type

    def get_contract_type(self):
        return self._contract_type

    #TODO override func in BinanceCommon
    def get_symbol_from_pair(self, pair, stream_symbol=True):
        ws_pair = pair.replace('/', '').lower()
        if self._future_type != self.COIN_FUTURES:
            return ws_pair if stream_symbol else pair

        if not self._contract_type:
            return ''
        if self._contract_type not in self._pair_dict[ws_pair]:
            self._log(f'Pair {self._pair_dict[ws_pair]["pair"]} does not support contract type {self._contract_type}')
            return ''
        symbol = '_'.join([ws_pair, self._pair_dict[ws_pair][self._contract_type]])
        return symbol.lower() if stream_symbol else symbol.upper()

    @on_message_handler()
    def _user_stream_handler(self, msg):
        # Binancef msg is a dict
        # Example payload:
        # {'P': '0.00000000', 'N': None, 'L': '0.00000000', ...,
        #  'i': 691888660, 's': 'BTCUSD_PERP', 'ps': 'BTCUSD', 'S': 'BUY',... 'X': 'CANCELED', ..,'x': 'CANCELED', 'e': 'executionReport'}
        if not isinstance(msg, dict):
            return
        if msg.get('e') == 'update_order_progress':
            self._log('BIFD: re-register user-stream, force update_order_progress')
            for pair in self.order_progress_pairs:
                self.update_order_progress(pair)
            return
        if msg.get('e') == 'ORDER_TRADE_UPDATE':
            order_data = msg.get('o')
            order_id = str(order_data.get('i'))
            order_status = order_data.get('X')
            accu_amount = order_data.get('z') # Cumulative filled quantity
            avg_price = order_data.get('L') # Last filled quantity

            if order_status:
                order_status = order_status.lower()
                # Convert binanace order status to align with kraken
                if order_status == 'new' or order_status == 'partially_filled':
                    order_status = 'open'
                elif order_status == 'filled':
                    order_status = 'closed'

            # First payload
            if not self.websocket_data['order_progress'].get(order_id):
                symbol = order_data.get('s').lower()
                pair = self.get_pair_from_symbol(symbol)
                amount = float(order_data.get('q'))
                side = order_data.get('S').lower()
                price = float(order_data.get('p'))
                creation_time = int(float(msg.get('T'))) # msec
                accu_amount = float(accu_amount)
                avg_price = float(avg_price)
                stored_data = {
                        'order_status': order_status,
                        'pair': pair,
                        'accu_amount': accu_amount,
                        'avg_price': avg_price,
                        'amount': amount,
                        'side': side,
                        'price': price,
                        'creation_time': creation_time,
                        WS_ORDER_PROGRESS.IS_USING: True,
                        WS_ORDER_PROGRESS.UPDATE_TIME: [time.time()]
                    }
                self.websocket_data['order_progress'][order_id] = stored_data
                self.append_update_time_ws_data(order_id)
                #self._log(f'Create new ws data, order id {order_id} : f{stored_data}')
            # Update Payload
            else:
                if order_status:
                    old_status = self.websocket_data['order_progress'][order_id].get('order_status')
                    if ORDER_CLOSED == old_status or ORDER_CANCELED == old_status:
                        #self._log(f'Order {order_id} has old status {old_status}, ignore update status from ws, new status {order_status}')
                        return
                    else:
                        self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id].get(
                            WS_ORDER_PROGRESS.UPDATE_TIME, []).append(time.time())
                        self.websocket_data['order_progress'][order_id].update({
                            'order_status': order_status
                        })
                        self.append_update_time_ws_data(order_id)
                        #self._log(f'Order {order_id} update status {order_status}, previous staus {old_status}')
                if accu_amount:
                    self.websocket_data['order_progress'][order_id].update({
                        'accu_amount': float(accu_amount)
                    })
                    #self._log(f'Order {order_id} update accu_amount {accu_amount}')
                if avg_price:
                    self.websocket_data['order_progress'][order_id].update({
                        'avg_price': float(avg_price),
                    })
                    #self._log(f'Order {order_id} update accu_amount {avg_price}')
        # Also get balance via user_socket for binance
        elif msg.get('e') == 'ACCOUNT_UPDATE':
            update_data = msg.get('a')
            balance_update = update_data.get('B')
            if not balance_update:
                return
            for asset_update in balance_update:
                asset = asset_update.get('a')
                wallet_balance = float(asset_update.get('wb'))
                cross_wb = float(asset_update.get('cw'))
                total = float(Decimal(str(wallet_balance)) + Decimal(str(cross_wb)))
                self.websocket_data['balances'][asset] = {'free': wallet_balance, 'used': cross_wb, 'total': total}
    # END _user_stream_handler

    @on_message_handler()
    def _order_book_handler(self, msg):
        # Binance msg is a dict
        # Example payload:
        # {'s': 'BTCUSDT', 'u': 1249195479, 'U': 1249195391, 'e': 'depthUpdate', 'E': 1572274799215,
        # 'a': [['9331.76000000', '0.00000000'], ['9331.77000000', '0.00000000'], ['9331.78000000', '0.00000000'],...],
        # 'b': [['9330.57000000', '0.16333300'], ['9330.50000000', '0.10404100'], ['9330.40000000', '0.10404100'],...]}
        if not isinstance(msg, dict):
            return
        if msg.get('e') != 'depthUpdate':
            return
        symbol = msg.get('s').lower()
        pair = self.get_pair_from_symbol(symbol)
        first_ev_id = int(msg.get('U'))
        last_ev_id = int(msg.get('u'))
        last_ev_id_prev_update = int(msg.get('pu'))

        depth = self.websocket_data['order_book'][pair]['depth']
        # Snapshot order_book
        if self.websocket_data['order_book'][pair].get('lastUpdateId'):
            last_update_id = self.websocket_data['order_book'][pair]['lastUpdateId']
            # Need a newer event.
            if last_ev_id < last_update_id:
                pass
            # First order_book update. (new U) <= (prev u) and (new u) >= (prev u)
            elif first_ev_id <= last_update_id and last_ev_id >= last_update_id:
                self.websocket_data['order_book'][pair].pop('lastUpdateId')
                self.websocket_data['order_book'][pair]['nonce'] = last_ev_id
                self._update_order_book(pair, 'asks', msg.get('a'), depth)
                self._update_order_book(pair, 'bids', msg.get('b'), depth)
            # Unluckily, the prev snapshot is obsolete, need to take another snapshot.
            else:
                # Re-initialize order_book
                self._init_order_book(pair)
        # Update order_book
        else:
            if last_ev_id_prev_update == self.websocket_data['order_book'][pair]['nonce']:
                self.websocket_data['order_book'][pair]['nonce'] = last_ev_id
                self._update_order_book(pair, 'asks', msg.get('a'), depth)
                self._update_order_book(pair, 'bids', msg.get('b'), depth)
            else:
                # Re-initialize order_book
                self._init_order_book(pair)
    # END _order_book_handler

