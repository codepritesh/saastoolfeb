import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
lib_path = dir_path + '/../libs'
sys.path.append(lib_path)
sys.path.append(dir_path)
from bot_father import *
from bot_constant import *
from exception_decor import exception_logging


class SupportOrderStopLoss(BotFather):

    def __init__(self, alias):
        super().__init__(alias)

    def print_metheod_stoploss(self, msg):
        print(f'support_order_stop_lossmom---19 Msg {msg}')