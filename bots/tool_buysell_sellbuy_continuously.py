import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
lib_path = dir_path + '/../libs'
bot_ac_path = dir_path + '/../bot_action'
sys.path.append(lib_path)
sys.path.append(dir_path)
sys.path.append(bot_ac_path)
from bot_father import BotFather
from sqldata_insert import *

from exchange_lib import *
from support_order_follow_market import SupportOrderFollowMarket
from pprint import pprint



class BSSBContinuouslyTool(SupportOrderFollowMarket, BotFather):

    bot_alias = 'BSSBContinuouslyTool'
    open_pos_num = 'open_position_num'
    tp_filled_num = 'tp_closed_num'
    open_tp_list = 'open_tp_list'
    is_running = 'is_running'

    def __init__(self):
        super().__init__(self.bot_alias)
        

    def bot_entry(self, web_input):
        
        #{'own_name': 'pmpmaharana97@gmail.com', 'uuid': '8a2d7230-3df8-11eb-9737-6d26a412779a', 'ex_id': 'BIN', 'api_name': 'rohitsirapi', 'amount': '0.001', 'pair': 'BTC/USDT', 'profit': '5', 'timer': '10', 'postOnly': False, 'port': '8000', 'signal': 'start', 'is_production': False, 'framework': 'Django'}
        
        super().bot_entry(web_input)

        self._cost = 0
        self._trade_id = 0
        self._trade_info = {}
        self._num_tp_close = 0
        self.submit_task(self._print_log_profit)
        

    def begin_trading(self, web_input, buysell=True):
        try:
            self._log('tool_buysell_sellbuy_continuouslymom---38 Bot {} start, web_input {}'.format(self.alias, web_input))
            amount = float(web_input['amount'])
            postOnly = web_input.get('postOnly', True)
            timer = float(web_input['timer'])
            self._trade_id += 1
            trade_id = str(self._trade_id)
            self._trade_info.update({trade_id: {
                self.open_pos_num: 0,
                self.tp_filled_num: 0,
                self.open_tp_list: [],
                self.is_running: True,
            }
            })
            open_postion_side = BUY if buysell else SELL
            web_input.update({'trade_id': trade_id})
            self._log(f'tool_buysell_sellbuy_continuouslymom---53#{trade_id} place open position order')
            self._trade_info[trade_id][self.open_pos_num] += 1
            self.msf_place_order_follow_market_helper(self._pair, open_postion_side, amount, 0,
                                                  self._open_position_cb, meta_data=web_input,
                                                  postOnly=postOnly, verbose=False)
        except:
            tb = traceback.format_exc()
            self._log('tool_buysell_sellbuy_continuously---60ERROR {}'.format(tb), severity='error')
        pprint(web_input)
        pprint(vars(self))

    def _print_log_profit(self):
        try:
            while not self._terminate:
                if self._trade_id:
                    self._log(
                        f'tool_buysell_sellbuy_continuouslymom---68##### running_trade_info={self._trade_info[str(self._trade_id)]} #### total tp_closed={self._num_tp_close} ##### volume={self._cost}')
                time.sleep(60)
        except:
            tb = traceback.format_exc()
            self._log('tool_buysell_sellbuy_continuouslymom---72ERR {}'.format(tb))

    def _open_position_cb(self, data):
        try:
            if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
                self._log(f'tool_buysell_sellbuy_continuouslymom---76Open position filled {data}')

                datainserted = sql_insertbssb(data)
                
                self._log(f'tool_buysell_sellbuy_continuouslymom---open position filled data inserted to database{datainserted}')

                print("datainserted---------------",datainserted)
                meta_data = data[KEY_GET_ORDER_META_DATA]
                profit = float(meta_data['profit'])
                postOnly = meta_data['postOnly']
                trade_id = meta_data['trade_id']
                self._cost = float(Decimal(str(self._cost)) + Decimal(str(data[KEY_GET_ORDER_FILLED])) * Decimal(
                    str(data[KEY_GET_ORDER_AVERAGE_PRICE])))

                self._trade_info[trade_id][self.open_pos_num] -= 1

                tp_side = self._fetch_revert_side(data[KEY_GET_ORDER_SIDE])
                # price profit
                tp_price = float(
                    Decimal(str(data[KEY_GET_ORDER_AVERAGE_PRICE])) - DECIMAL_STEP_WISE[tp_side] * Decimal(str(profit)))
                tp_amount = data[KEY_GET_ORDER_FILLED]
                self._mbf_waiting_enough_balance_to_place_order(self._pair, tp_side, tp_amount, tp_price)
                order_type = LIMIT_MAKER if postOnly else LIMIT
                order_info = self.place_order(tp_price, tp_amount, tp_side, self._pair, type=order_type, meta_data=meta_data,
                                              callback=self._callback_take_profit_order)
                while not self._terminate and self._trade_info[trade_id][self.is_running]:
                    if order_info:
                        order_progress = self._fetch_order_progress(order_info[KEY_GET_ORDER_ID])
                        if (order_progress and order_progress[KEY_GET_ORDER_STATUS] == ORDER_EXPIRED) or \
                                order_info[KEY_GET_ORDER_STATUS] == ORDER_EXPIRED:
                            new_price = self._fetch_best_price(self._pair, tp_side)
                            if STEP_WISE[tp_side] * new_price > STEP_WISE[tp_side] * tp_price:
                                new_price = tp_price
                            self._mbf_waiting_enough_balance_to_place_order(self._pair, tp_side, tp_amount, new_price)
                            order_info = self.place_order(new_price, tp_amount, tp_side,
                                                          self._pair, meta_data=meta_data, type=order_type, callback=self._callback_take_profit_order)
                        else:
                            # Tp-order is filled or open, created successfully
                            break
                    else:
                        self._log(f'tool_buysell_sellbuy_continuouslymom---110# STRANGE: can not place {tp_side} order')
                        break
                    time.sleep(0.5)
                self._log(f'tool_buysell_sellbuy_continuouslymom---119Place_profit_order {order_info}')
                # in this line we are storing data to mysql using thissqldata_insert
                datainserted = sql_insert_bssb_order_info(order_info)
                print("datainserted---------------",datainserted)
                self._log(f'tool_buysell_sellbuy_continuouslymom---121Place_profit_order data inserted to database{datainserted}')
                # in this line we are storing data to mysql using thissqldata_insert
                if not order_info:
                    self._log(f'tool_buysell_sellbuy_continuously---116# STRANGE cannot place tp order {tp_side}@{tp_price}')
                    return
                order_progress = self._fetch_order_progress(order_info[KEY_GET_ORDER_ID])
                if order_progress and order_progress[KEY_GET_ORDER_STATUS] == ORDER_OPEN:
                    self._trade_info[trade_id][self.open_tp_list].append(order_info)

                # Replace open-pos order
                timer = float(meta_data['timer'])
                self._interuptable_waiting(timer)
                if self._trade_info[trade_id][self.is_running]:
                    self._log(f'tool_buysell_sellbuy_continuouslymom---126#{trade_id} place open position order')
                    self._trade_info[trade_id][self.open_pos_num] += 1
                    self.msf_place_order_follow_market_helper(self._pair, data[KEY_GET_ORDER_SIDE], data[KEY_GET_ORDER_AMOUNT], 0,
                                                          self._open_position_cb, meta_data=meta_data,
                                                          postOnly=postOnly, verbose=False)
        except:
            tb = traceback.format_exc()
            self._log('tool_buysell_sellbuy_continuouslymom---ERROR {}'.format(tb))


    """
    cb when take profit order filled
    """
    def _callback_take_profit_order(self, data):
        # order filled, begin new trade
        if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
            meta_data = data[KEY_GET_ORDER_META_DATA]
            postOnly = meta_data['postOnly']
            trade_id = meta_data['trade_id']
            side = data[KEY_GET_ORDER_SIDE]
            self._cost = float(Decimal(str(self._cost)) + Decimal(str(data[KEY_GET_ORDER_FILLED])) * Decimal(
                str(data[KEY_GET_ORDER_AVERAGE_PRICE])))
            self._log(f'tool_buysell_sellbuy_continuouslymom---148#{trade_id} Order take profit filled... {data}')
            # in this line we are storing data to mysql using thissqldata_insert
            datainserted = sql_insertbssb(data)
            self._log(f'tool_buysell_sellbuy_continuouslymom---Order take profit filled data inserted to database{datainserted}')

            print("datainserted---------------",datainserted)
            # in this line we are storing data to mysql using thissqldata_insert
            self._trade_info[trade_id][self.tp_filled_num] += 1
            self._num_tp_close += 1
            self._remove_order_filled(trade_id, data[KEY_GET_ORDER_ID], side)
        elif ORDER_CANCELED == data[KEY_GET_ORDER_STATUS]:
            meta_data = data[KEY_GET_ORDER_META_DATA]
            trade_id = meta_data['trade_id']
            side = data[KEY_GET_ORDER_SIDE]
            self._log(f'tool_buysell_sellbuy_continuouslymom---156#{trade_id} Order take profit canceled... {data}')
            self._remove_order_filled(trade_id, data[KEY_GET_ORDER_ID], side)

    def _remove_order_filled(self, trade_id, order_id, side):
        try:
            # remove order profit
            target_list = self._trade_info[trade_id][self.open_tp_list]
            for item in target_list.copy():
                if item[KEY_GET_ORDER_ID] == order_id:
                    target_list.remove(item)
            self._log(f'tool_buysell_sellbuy_continuouslymom---166# Remove {order_id}, remain {side} is {len(target_list)} \n Detail \
                      {[(item[KEY_GET_ORDER_ID], item[KEY_GET_ORDER_PRICE]) for item in target_list]}')
        except:
            tb = traceback.format_exc()
            self._log('tool_buysell_sellbuy_continuouslymom---170ERROR {}'.format(tb), severity='error')

    def stop_trade(self, web_input):
        try:
            trade_id = str(self._trade_id)
            self._trade_info[trade_id][self.is_running] = False
            #for open_tp_order in self._trade_info[trade_id][self.open_tp_list].copy():
            #    self._cancel_order_with_retry(open_tp_order[KEY_GET_ORDER_ID], self._pair)
            self._log(f'tool_buysell_sellbuy_continuouslymom---178#{trade_id} finished!')
        except:
            tb = traceback.format_exc()
            self._log('tool_buysell_sellbuy_continuouslymom---181 {}'.format(tb), severity='error')
