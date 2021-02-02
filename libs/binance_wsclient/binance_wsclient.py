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
bots_path = this_path + '/../../bots'
sys.path.append(bots_path)
from binance_common import BinanceSpotWssClient, \
                           BinanceMarginWssClient, \
                           BinanceCommon
from wsclient_common import on_message_handler
from bot_constant import *
from audit_ws_data import *


class Binance(BinanceCommon, AuditData):
    """ High-level library BINANCE """
    ACCOUNT_TYPE_KW = 'account_type'
    SPOT = 'spot'
    MARGIN = 'margin'

    def __init__(self, key=None, secret=None, logger=None, rest_api=None, *args, **kwargs):
        #print(kwargs)
        if kwargs.get(self.ACCOUNT_TYPE_KW) == self.MARGIN:
            ws_manager = BinanceMarginWssClient(key, secret, logger)
        else: # Spot is default
            ws_manager = BinanceSpotWssClient(key, secret, logger)
        BinanceCommon.__init__(self, rest_api=rest_api, ws_manager=ws_manager, logger=logger)

    def get_symbol_from_pair(self, pair, stream_symbol=True):
        ws_pair = pair.replace('/', '').lower()
        return ws_pair if stream_symbol else pair

    @on_message_handler()
    def _user_stream_handler(self, msg):
        try:
            # print('msg {}'.format(msg))
            # Binance msf is a dict
            # Example payload:
            # {'P': '0.00000000', 'N': None, 'L': '0.00000000', ...,
            #  'i': 691888660, 's': 'BTCUSDT', 'S': 'BUY',... 'X': 'CANCELED', ..,'x': 'CANCELED', 'e': 'executionReport'}
            if not isinstance(msg, dict):
                return
            if msg.get('e') == 'update_order_progress':
                self._log('BINM: re-register user-stream, force update_order_progress')
                for pair in self.order_progress_pairs:
                    self.update_order_progress(pair)
                return
            if msg.get('e') == 'executionReport':
                order_id = str(msg.get('i'))
                order_status = msg.get('X')
                accu_amount = msg.get('z') # Cumulative filled quantity
                accu_quote_amount = msg.get('Z') # Cumulative quote asset transacted quantity

                if order_status:
                    order_status = order_status.lower()
                    # Convert binanace order status to align with kraken
                    if order_status == 'new' or order_status == 'partially_filled':
                        order_status = 'open'
                    elif order_status == 'filled':
                        order_status = 'closed'

                # First payload
                if not self.websocket_data['order_progress'].get(order_id):
                    ws_pair = msg.get('s').lower()
                    pair = self.get_pair_from_symbol(ws_pair)
                    amount = float(msg.get('q'))
                    side = msg.get('S').lower()
                    price = float(msg.get('p'))
                    creation_time = int(float(msg.get('O'))) # msec
                    accu_amount = float(accu_amount)
                    avg_price = 0.0
                    if accu_quote_amount and accu_amount > 0.0:
                        avg_price = float(Decimal(str(accu_quote_amount)) / Decimal(str(accu_amount)))
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
                # Update Payload
                else:
                    if order_status:
                        old_status = self.websocket_data['order_progress'][order_id].get('order_status')
                        if ORDER_CLOSED == old_status or ORDER_CANCELED == old_status:
                            #self._log(f'Order {order_id} has old status {old_status}, ignore update status from ws, new status {order_status}')
                            # return
                            return
                        else:

                            self.websocket_data['order_progress'][order_id].update({
                                'order_status': order_status,
                            })
                            #self._log(f'Order {order_id} update status {order_status}, previous status {old_status}')
                            self.append_update_time_ws_data(order_id)
                    if accu_amount:
                        accu_amount = float(accu_amount)
                        self.websocket_data['order_progress'][order_id].update({
                            'accu_amount': accu_amount,
                        })
                        if accu_quote_amount and accu_amount > 0.0:
                            avg_price = float(Decimal(str(accu_quote_amount)) / Decimal(str(accu_amount)))
                            self.websocket_data['order_progress'][order_id].update({
                                'avg_price': avg_price,
                            })
            # Also get balance via user_socket for binance
            elif msg.get('e') == 'outboundAccountPosition':
                acc_update = msg.get('B')
                if not acc_update:
                    return
                for coin in acc_update:
                    name = coin.get('a')
                    free = float(coin.get('f'))
                    locked = float(coin.get('l'))
                    total = float(Decimal(coin.get('f')) + Decimal(coin.get('l')))
                    self.websocket_data['balances'][name] = {'free': free, 'used': locked, 'total': total}
                    # self._log(f'Balance coin {name}, free: {free}, used: {locked}, total: {total}')
        except:
            tb = traceback.format_exc()
            self._log(f'{tb}', severity='error')
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
        ws_pair = msg.get('s').lower()
        pair = self.get_pair_from_symbol(ws_pair)
        first_ev_id = int(msg.get('U'))
        final_ev_id = int(msg.get('u'))

        for ask, bid in zip(msg.get('a'), msg.get('b')):
            if isinstance(ask, list) and isinstance(bid, list):
                self.vol_ask_count += float(ask[1])
                self.vol_bid_count += float(bid[1])

        depth = self.websocket_data['order_book'][pair]['depth']
        # Snapshot order_book
        if self.websocket_data['order_book'][pair].get('lastUpdateId'):
            last_update_id = self.websocket_data['order_book'][pair]['lastUpdateId']
            # Need a newer event.
            if final_ev_id <= last_update_id:
                pass
            # First order_book update. (new U) <= (prev u) + 1 and (new u) >= (prev u) + 1
            elif first_ev_id <= last_update_id + 1 and final_ev_id >= last_update_id + 1:
                self.websocket_data['order_book'][pair].pop('lastUpdateId')
                self.websocket_data['order_book'][pair]['nonce'] = final_ev_id
                self._update_order_book(pair, 'asks', msg.get('a'), depth)
                self._update_order_book(pair, 'bids', msg.get('b'), depth)
            # Unluckily, the prev snapshot is obsolete, need to take another snapshot.
            else:
                # Re-initialize order_book with restapi
                self._init_order_book(pair)
        # Update order_book
        else:
            if first_ev_id == self.websocket_data['order_book'][pair]['nonce'] + 1:
                self.websocket_data['order_book'][pair]['nonce'] = final_ev_id
                self._update_order_book(pair, 'asks', msg.get('a'), depth)
                self._update_order_book(pair, 'bids', msg.get('b'), depth)
    # END _order_book_handler

    @on_message_handler()
    def _trade_stream_handler(self, msg):
        if msg.get('e') != 'trade':
            return
        ws_pair = msg.get('s').lower()
        pair = self.get_pair_from_symbol(ws_pair)
        time = int(float(msg.get('T'))/1000)
        tmp_dict = {'price': float(msg.get('p')), 'vol': float(msg.get('q')), 'm': msg.get('m'), 'num': 1}
        if not self.websocket_data['trade'][pair].get(time):
            self.websocket_data['trade'][pair][time] = {'time_event': int(float(msg.get('T'))), 'price': float(msg.get('p')), 'vol': float(msg.get('q'))}

        if msg.get('m'): #sell
            if not self.websocket_data['trade'][pair]['sell'].get(time):
                self.websocket_data['trade'][pair]['sell'][time] = tmp_dict
                # self.websocket_data['trade'][pair]['sell'].update({time: tmp_dict})
            else:
                price = float(Decimal(str(self.websocket_data['trade'][pair]['sell'][time].get('price'))) + Decimal(str(msg.get('p'))))/2
                volume = float(Decimal(str(self.websocket_data['trade'][pair]['sell'][time].get('vol'))) + Decimal(str(msg.get('q'))))
                num_sell = int(self.websocket_data['trade'][pair]['sell'][time].get('num')) + 1
                update_data = {'price': price, 'vol': volume, 'm': msg.get('m'), 'num': num_sell}
                self.websocket_data['trade'][pair]['sell'].update({time: update_data})
        else: #buy
            if not self.websocket_data['trade'][pair]['buy'].get(time):
                self.websocket_data['trade'][pair]['buy'][time] = tmp_dict
                # self.websocket_data['trade'][pair]['sell'].update({time: tmp_dict})
            else:
                price = float(Decimal(str(self.websocket_data['trade'][pair]['buy'][time].get('price'))) + Decimal(str(msg.get('p'))))/2
                volume = float(Decimal(str(self.websocket_data['trade'][pair]['buy'][time].get('vol'))) + Decimal(str(msg.get('q'))))
                num_buy = int(self.websocket_data['trade'][pair]['buy'][time].get('num')) + 1
                update_data = {'price': price, 'vol': volume, 'm': msg.get('m'), 'num': num_buy}
                self.websocket_data['trade'][pair]['buy'].update({time: update_data})

    def register_trade_stream(self, pair):
        if pair not in self.websocket_data['trade']:
            self.websocket_data['trade'][pair] = {}
            self.websocket_data['trade'][pair]['buy'] = {}
            self.websocket_data['trade'][pair]['sell'] = {}
        symbol = self.get_symbol_from_pair(pair)
        stream_name = f'{symbol}@trade'
        self._ws_manager.subscribe_public(subscription=stream_name, callback=self._trade_stream_handler)

    def unregister_trade_stream(self, pair):
        symbol = self.get_symbol_from_pair(pair)
        stream_name = f'{symbol}@trade'
        self._ws_manager.unsubscribe(subscription=stream_name)
