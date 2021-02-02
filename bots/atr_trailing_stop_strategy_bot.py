import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
lib_path = dir_path + '/../libs'
sys.path.append(lib_path)
sys.path.append(dir_path)
from bot_father import BotFather
from bot_constant import *
from exception_decor import exception_logging
from sqldata_insert import *


class AtrTrailingStopBot(BotFather):

    bot_alias = 'AtrTrailingStopBot'
    # mode
    mode_simple = 'simple'
    mode_divide_and_conrque = 'divide_and_conrque'
    mode_trailing_stop = 'trailing_stop'

    def __init__(self):
        super().__init__(self.bot_alias)
        self._amount = '0.0'
        self._profit = '0.0'

    @exception_logging
    def bot_entry(self, web_input):
        super().bot_entry(web_input)
        self._amount = float(web_input['amount'])
        self._profit = float(web_input['profit'])
        self._profit = float(web_input['fees'])
        self._mode = web_input['mode']
        self._loss_covering = web_input['loss_covering']
        self._trailing_margin = float(web_input['trailing_margin'])
        self._min_profit = float(web_input['min_profit'])
        # report open order
        # self.executor.submit(self.fetch_open_order)
        # begin trading
        # self._log('Balance START {}'.format(self.ex_instance.fetch_balance()))
        self.begin_trading(web_input)

    @exception_logging
    def begin_trading(self, web_input):
        self._log('Bot {} start'.format(self.alias))


