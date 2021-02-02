import os, sys
import time


this_path = os.path.dirname(os.path.realpath(__file__))
bots_path = this_path + '/../bots'
sys.path.append(bots_path)
from bot_constant import *
import  traceback

class AuditData:

    def append_update_time_ws_data(self, order_id):
        try:
            # if order_id not in ws_data progress
            if order_id not in self.websocket_data[WS_DATA.ORDER_PROGRESS].keys():
                # if order had status cancel closed
                print(f'Cant update time of  order id {order_id} in ws data')
            else:
                order_infos = self.websocket_data[WS_DATA.ORDER_PROGRESS].get(order_id)
                if not order_infos:
                    print(f'STRANGE: Order id: {order_id} had no content in ws data')
                    return
                arr_update_time = order_infos.get(WS_ORDER_PROGRESS.UPDATE_TIME)
                if ORDER_OPEN != order_infos[WS_ORDER_PROGRESS.STATUS]:
                    if not arr_update_time:
                        self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id].update({
                            WS_ORDER_PROGRESS.UPDATE_TIME: [time.time()]
                        })
                    else:
                        self.websocket_data[WS_DATA.ORDER_PROGRESS][order_id][WS_ORDER_PROGRESS.UPDATE_TIME].append(time.time())
        except:
            tb = traceback.format_exc()
            print(f'ERROR {tb}')