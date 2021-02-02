import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
lib_path = dir_path + '/../libs'
bot_ac_path = dir_path + '/../bot_action'
sys.path.append(lib_path)
sys.path.append(dir_path)
sys.path.append(bot_ac_path)
from bot_father import *
from support_order_follow_market import SupportOrderFollowMarket
from bot_constant import *
from sqldata_insert import *
from pprint import pprint


class TwoWaySpBot(SupportOrderFollowMarket, BotFather):

    bot_alias = 'TwoWaySpBot'

    def __init__(self):
        super().__init__(self.bot_alias)
        self._amount = '0.0'
        self._profit = '0.0'

    def bot_entry(self, web_input):
        super().bot_entry(web_input)

    def begin_trading(self, web_input):
        try:
            self._log(f'two_way_sp_strategy_botmom---29Start new trade with config {web_input}')
            amount = float(web_input['amount'])
            pair1_side = web_input['side']
            self._side = pair1_side
            min_profit = float(web_input.get('min_profit', 0))
            self._min_profit = min_profit
            is_follow_market = web_input['follow_market']
            self._follow_market = is_follow_market
            pair_first_index = int(web_input['pair_first'])
            self._pair_first = pair_first_index
            gap = float(web_input.get('gap', 0))
            self._gap = gap

            follow_gap = float(web_input.get('follow_gap', 0))
            self.follow_gap = follow_gap
            postOnly = web_input.get('postOnly', False)
            self._postOnly = postOnly

            # Place 1st pair order
            if pair_first_index == 0:
                p1, p2 = self._pair_mix_type
            else:
                p2, p1 = self._pair_mix_type
            meta_data = {
                'pair2': p2,
                'min_profit': min_profit,
                'gap': gap,
                'follow_gap': follow_gap,
                'postOnly': postOnly,
            }
            if is_follow_market:
                self.msf_place_order_follow_market_helper(p1, pair1_side, amount, 0, self._cb_pair1,
                                            meta_data=meta_data, is_quote_coin_amount=True, gap=gap, follow_gap=follow_gap, postOnly=postOnly)
            else:
                self._log('two_way_sp_strategy_botmom---55## UNSUPPORTED YET')
        except:
            tb = traceback.format_exc()
            self._log('two_way_sp_strategy_botmom---58ERROR {}'.format(tb), severity='error')
    def _cb_pair1(self, data):
        if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
            self._log(f'two_way_sp_strategy_botmom---62Order 1 is filled: {data}')

            two_way_bot_datainserted = sql_two_way_sp_strategy_bot(data,self._own_name,self._channel,self._ex_id,self._api_name,self._amount,self._pair_list,self._follow_market,self._pair_first,self._min_profit,self._postOnly,self._gap,self.follow_gap,self._side)
            self._log(f'tool_buysell_sellbuy_continuouslymom---open position filled data inserted to database{two_way_bot_datainserted}')

            print("datainserted---------------",two_way_bot_datainserted)
            meta_data = data.get(KEY_GET_ORDER_META_DATA, {})
            if not meta_data:
                self._log(f'two_way_sp_strategy_botmom---65# STRANGE Order 1 metadata None')
                return
            pair2 = meta_data['pair2']
            gap = meta_data['gap']
            postOnly = meta_data['postOnly']
            follow_gap = meta_data['follow_gap']
            min_profit_info = {}
            if meta_data.get('min_profit'):
                min_profit_info = {
                    self.INIT_AMOUNT: data[KEY_GET_ORDER_FILLED],
                    self.MIN_PROFIT: meta_data.get('min_profit'),
                }
            pair2_side = self._fetch_revert_side(data[KEY_GET_ORDER_SIDE])
            pair2_amount = float(Decimal(str(data[KEY_GET_ORDER_AVERAGE_PRICE])) * Decimal(str(data[KEY_GET_ORDER_FILLED])))
            self.msf_place_order_follow_market_helper(pair2, pair2_side, pair2_amount, 0, self._cb_pair2,
                                                      is_quote_coin_amount=True, min_profit=min_profit_info, gap=gap, follow_gap=follow_gap, postOnly=postOnly)

    def _cb_pair2(self, data):
        if ORDER_CLOSED == data[KEY_GET_ORDER_STATUS]:
            self._log(f'two_way_sp_strategy_botmom---84Order 2 is filled: {data}')



