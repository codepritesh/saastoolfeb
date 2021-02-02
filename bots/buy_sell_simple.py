import os
import sys
import time
cur_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(cur_path + '/../libs')
sys.path.append(cur_path + '/../repositories')
from exchange_lib import *
from bot_father import BotFather
from bot_constant import *


class BotConstant():
    BT_BUY = 'BUY'
    BT_SELL = 'SELL'
    SRC_OPEN = 'open'
    SRC_CLOSE = 'close'
    CHECKING_INTERVAL = 0.2
    CUTLOSS_TYPE = 'own_stoploss_market'
    OPEN_POSITION_ORDER = 'open_position_order'
    CLOSE_POSITION_ORDER = 'close_position_order'
    TRADE_RUNNING = 'Running'
    TRADE_CUTLOSS = 'Cutloss'
    TRADE_PROFIT = 'Profit'
    TRADE_CANCELED = 'Canceled'
    STEP_WISE = {BT_BUY: 1, BT_SELL: -1}


class BuySellSimple(BotFather):
    def __init__(self):
        super().__init__('BuySellSimple')
        self._init_type = BotConstant.BT_BUY
        self._cutloss_price = 20
        self._profit_margin = 60
        self._amount = 0.002
        self.TRADE_FM = {
            'TradeId': None,
            'Type': None,
            'StartTime': None,
            'StopTime': None,
            'OpenOrder': None,
            'OpenPrice': 0,
            'CloseOrder': None,
            'ClosePrice': 0,
            'TradeProfit': 0,
            'TradeStatus': BotConstant.TRADE_RUNNING,
        }
    # END __init__(self)
    
    def _check_close_position(self, trade_id, bot_type, open_position_price):
        side = SELL if bot_type == BotConstant.BT_BUY else BUY
        # Place take-profit order with base_vol amount
        profit_price = open_position_price + BotConstant.STEP_WISE[bot_type] * self._profit_margin
        profit_order = self.place_order(profit_price, self._amount, side, self._pair, 'limit',
                        meta_data={'bot_type': bot_type, 'order_type': BotConstant.CLOSE_POSITION_ORDER, 'trade_id': trade_id},
                        callback=self._order_status_cb)
        self._log('buy_sell_simplemom---56 BOT_TYPE {}: Trade {}, placed take-profit_order {} @ {} '.format(bot_type, trade_id, profit_order['order_id'], profit_price))
        # Place our own stoploss order
        stoploss_price = open_position_price - BotConstant.STEP_WISE[bot_type] * self._cutloss_price
        cutloss_order_id = self.ex_instance.create_order(self._pair, BotConstant.CUTLOSS_TYPE,
                                side, self._amount, stoploss_price,
                                params={'stopPrice': stoploss_price,
                                        'profit-order-id': profit_order['order_id'],
                                        'bot_type': bot_type})
                                        
        while self._process_running and not self._terminate:
            self._interuptable_waiting(ORDER_PROFILE['time_sleep'])
            # Check cutloss order status
            while not self.ex_instance.fetch_order_progress(cutloss_order_id):
                self._interuptable_waiting(ORDER_PROFILE['time_sleep'])
            progress = self.ex_instance.fetch_order_progress(cutloss_order_id)
            if not progress:
                continue
            cutloss_order_status = progress['order_status']
            if ORDER_PROFILE['status']['closed'] == cutloss_order_status:
                # Update trade info in report
                cutloss_order_price = progress['avg_price']
                profit = BotConstant.STEP_WISE[bot_type] * self._amount * (cutloss_order_price - self._report.get_trade_info(trade_id, key='OpenPrice'))
                stop_time = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
                update_info = {
                        'StopTime': stop_time, 'CloseOrder': cutloss_order_id,
                        'ClosePrice': cutloss_order_price, 'TradeProfit': profit, 'TradeStatus': BotConstant.TRADE_CUTLOSS
                    }
                self._report.update_trade_info(trade_id, update_info)
                self._log('buy_sell_simplemom---84BOT_TYPE {}: cutloss_order {} closed @ avg_price {}. Finish trade {}'.format(bot_type,
                                                cutloss_order_id, cutloss_order_price, trade_id))
                self._is_cutloss = True
                # Finish trade
                self._process_running = False
                break
            elif ORDER_PROFILE['status']['canceled'] == cutloss_order_status:
                # For sure in case of canceled manually
                self._log('buy_sell_simplemom---92 BOT_TYPE {}: Trade {}, cutloss_order {} canceled, meta data {}'.format(bot_type, trade_id, cutloss_order_id, progress))
                self._process_running = False
                break
    # END _check_close_position(self, trade_id, bot_type, open_position_price)
        
    def _order_status_cb(self, data):
        meta_data = data.get('meta_data', {})
        bot_type = meta_data.get('bot_type')
        order_type = meta_data.get('order_type')
        trade_id = meta_data.get('trade_id')
        order_id = data['order_id']
        order_status = data['status']
        if order_type == BotConstant.OPEN_POSITION_ORDER:
            if ORDER_PROFILE['status']['closed'] == order_status:
                # Start a trade by place open position order
                open_position_price = float(data['average'])
                self._report.update_trade_info(trade_id, {'OpenPrice': open_position_price})
                self._log('buy_sell_simplemom---109 BOT_TYPE {}: Trade {}, {} {} closed @ avg_price {}'.format(bot_type, trade_id, order_type, order_id, open_position_price))
                self._check_close_position(trade_id, bot_type, open_position_price)
            if ORDER_PROFILE['status']['canceled'] == order_status:
                self._log('buy_sell_simplemom---112 BOT_TYPE {}: Trade {}, {} {} canceled, meta data {}. Finish trade {}'.format(bot_type, trade_id, order_type, order_id, data, trade_id))
                self._report.update_trade_info(trade_id, {'TradeStatus': BotConstant.TRADE_CANCELED})
        elif order_type == BotConstant.CLOSE_POSITION_ORDER:
            if ORDER_PROFILE['status']['closed'] == order_status:
                filled = data['filled']
                close_position_price = data['average']
                stop_time = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
                profit = BotConstant.STEP_WISE[bot_type] * self._amount * (close_position_price - self._report.get_trade_info(trade_id, key='OpenPrice'))
                update_info = {
                        'StopTime': stop_time, 'CloseOrder': order_id, 'ClosePrice': close_position_price,
                        'TradeProfit': profit, 'TradeStatus': BotConstant.TRADE_PROFIT
                    }
                self._report.update_trade_info(trade_id, update_info)
                self._log('buy_sell_simplemom---125 BOT_TYPE {}: {} {} closed @ avg_price {} amount={}. Finish trade {}'.format(bot_type, order_type, order_id, close_position_price, filled, trade_id))
                self._process_running = False
            if ORDER_PROFILE['status']['canceled'] == order_status:
                self._log('buy_sell_simplemom---128 BOT_TYPE {}: Trade {}, {} {} canceled manually, meta data {}'.format(bot_type, trade_id, order_type, order_id, data))
    # END _order_status_cb(self, data)
    
    def bot_entry(self, web_input):
        super().bot_entry(web_input)
        self._pair = web_input.get('pair', 'BTC/USDT')
        self._init_type = web_input.get('bot_type', BotConstant.BT_BUY).upper()
        self._cutloss_price = float(web_input.get('loss_price', 10))
        self._profit_margin = float(web_input.get('profit', 15))
        self._init_amount = float(web_input.get('amount', 0.002))
        self._error_margin = int(web_input.get('error_margin', 2))
        self._double_steps = int(web_input.get('double_step', 4))
        self._running_type = self._init_type
        self._process_running = False
        self._is_cutloss = False
        self._cutloss_counter_for_side = 0
        self._cutloss_counter_for_amount = 0
        self._trade_no = 0
        self._report.take_start_balance_snapshot()
        
        while not self._terminate:
            if not self._process_running:
                self._process_running = True
                # Decide what is next running type, change type if previous round is cutloss otherwise keep this type
                if self._is_cutloss:
                    self._is_cutloss = False
                    self._cutloss_counter_for_side += 1
                    self._cutloss_counter_for_amount += 1
                    if self._cutloss_counter_for_amount >= self._double_steps:
                        self._cutloss_counter_for_amount = 0
                    if self._cutloss_counter_for_side >= self._error_margin:
                        self._cutloss_counter_for_side = 0
                        self._running_type = BotConstant.BT_SELL if self._running_type == BotConstant.BT_BUY else BotConstant.BT_BUY
                else:
                    self._cutloss_counter_for_amount = 0
                # Start trade with market order
                side = BUY if self._running_type == BotConstant.BT_BUY else SELL
                self._trade_no += 1
                self._amount = self._init_amount * 2 ** self._cutloss_counter_for_amount
                trade_id = self._trade_no
                new_trade = self.TRADE_FM.copy()
                start_time = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
                new_trade.update({'TradeId': trade_id, 'Type': self._running_type, 'StartTime': start_time})
                self._report.add_trade_to_report(trade_id, new_trade)
                self._log('buy_sell_simplemom---172 BOT_TYPE {}: Start trade {}'.format(self._running_type, self._trade_no))    
                try:
                    order_data = self.place_order(0, self._amount, side, self._pair, type='market',
                        meta_data={'bot_type': self._running_type, 'order_type': BotConstant.OPEN_POSITION_ORDER, 'trade_id': trade_id},
                        callback=self._order_status_cb)
                    update_info = {'OpenOrder': order_data.get('order_id')}
                except:
                    update_info = {'TradeStatus': BotConstant.TRADE_CANCELED}
                    self._log('buy_sell_simplemom---180 BOT_TYPE {}: place open order failed. Finish trade {}'.format(trade_id))
                self._report.update_trade_info(trade_id, update_info)
            self._interuptable_waiting(BotConstant.CHECKING_INTERVAL)
            
        self._report.take_end_balance_snapshot()
        self._report.write_trade_report_to_csv(self._csv_filepath)
        self._report.write_balance_report_to_csv(self._csv_filepath, margin=2, mode='a')
        self._log('buy_sell_simplemom---187 BOT {} EXIT!'.format(self.alias))
    # END bot_entry(self, web_input)


if __name__ == '__main__':
    a_bot = BuySellSimple()
    input = {'pair': 'BTC/USDT', 'uuid': '1234', 'socket': None, 'own_name': 'dev', 'api_name': 'ngocngoc.hh1', 'ex_id': 'BIN'}
    a_bot.bot_entry(input)
    os._exit(0)


