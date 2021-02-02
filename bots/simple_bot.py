import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
lib_path = dir_path + '/../libs'
sys.path.append(lib_path)
sys.path.append(dir_path)
from bot_father import BotFather
from bot_constant import *
from exception_decor import exception_logging


class SimpleBot(BotFather):

    bot_alias = 'BOT_ALIAS'

    def __init__(self):
        super().__init__(self.bot_alias)
        self._amount = '0.0'
        self._profit = '0.0'

    @exception_logging
    def bot_entry(self, web_input):
        super().bot_entry(web_input)
        self._amount = web_input['amount']
        self._profit = web_input['profit']
        # report open order
        # self.executor.submit(self.fetch_open_order)
        # begin trading
        # self._log('Balance START {}'.format(self.ex_instance.fetch_balance()))
        self.begin_trading(web_input)

    @exception_logging
    def begin_trading(self, web_input):
        self._log('simple_botmom---35 Bot {} start, web_input {}'.format(self.alias, web_input))


