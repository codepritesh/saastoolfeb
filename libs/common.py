import csv
import traceback
import pytz
from datetime import datetime, timedelta
from time import strftime, localtime, sleep
from threading import Timer, Thread
from asgiref.sync import async_to_sync
from common_bot_data_base import get_database_data
from pprint import pprint


# some common defines
WEB_FLASK = 'Flask'
WEB_DJANGO = 'Django'
DATETIME_FMT = '%Y-%m-%dT%H-%M-%S%z'
DEFAULT_TZ = 'Asia/Ho_Chi_Minh'


#def send_userdata_common (tracking_username_from_views):
#    global tracking_username
 #   tracking_username = tracking_username_from_views
  #  return True


def datetime_now(datetime_fmt=DATETIME_FMT):
    return strftime(datetime_fmt, localtime())


def datetime_now_raw():
    return datetime.now(pytz.timezone(DEFAULT_TZ))


# def date_to_str(date, fmt=DATETIME_FMT):
#     return strftime(fmt, date)

def str_to_date(str_date, fmt=DATETIME_FMT):
    return datetime.strptime(str_date, fmt)


#TODO (Flask) == Deprecated. To be removed!! ==
def log(data, logger=None, socketio=None, channel_uuid='', sk_namespace='/test', console=True, log_severity='info'):
    #print("socket_emit2-common.py---log---40",data)
    
    if data:
        data_str = str(data)
    else:
        data_str = 'None'
    if logger and log_severity:
        try:
            exec('logger.{}(data_str)'.format(log_severity))
        except:
            tb = traceback.format_exc()
            print(tb)
            pass
    # socketlog and console are mutex. socketlog has higher priority than console.
    # data_str = '[{}] [{}] {}'.format(datetime_now(), log_severity.upper(), data_str)
    data_str = '{}'.format(data_str)
    if socketio and channel_uuid:
        channel = 'log_'+channel_uuid
        try:
            socketio.emit(channel, {'data': data_str, 'channel': channel}, namespace=sk_namespace)
            
        except:
            tb = traceback.format_exc()
            print(tb)
            pass
    elif console:
        print(data_str)

def socket_emit(data, socketio, channel_uuid='', channel='', sk_namespace='/test'):
    #print("socket_emit2-common.py---socket_emit---70",data)
    if socketio:
        if channel_uuid:
            channel = channel+'_'+ channel_uuid
        try:
            socketio.emit(channel, {'data': data, 'channel': channel}, namespace=sk_namespace)
            
        except:
            tb = traceback.format_exc()
            print(tb)
#TODO (Flask) == Deprecated. To be removed!! ==


def log2(data, logger=None, channel_layer=None, channel_uuid='', channel_mux='', console=True, severity='info'):
    #print("socket_emit2-common.py---log2---84",data)
    try:
        if data:
            data_str = str(data)
        else:
            data_str = 'None'
        if logger and severity:
            exec('logger.{}(data_str)'.format(severity))
        # socketlog and console are mutex. socketlog has higher priority than console.
        # data_str = '[{}] [{}] {}'.format(datetime_now(), severity.upper(), data_str)
        if channel_layer and channel_uuid:
            # group_send always requires group_name (i.e channel_uuid) and data that is a dict with mandatory fields: 'type' and 'message'
            # Here, we implicitly define 'type' = 'forward_msg'. See BaseConsumer class: async def forward_msg()
            try:
                async_to_sync(channel_layer.group_send)(channel_uuid, {'type': 'forward_msg', 'message': data_str, 'channel_mux': channel_mux})

            except:
                tb = traceback.format_exc()
                print(tb)
        elif console:
            data_str = '[{}] [{}] {}'.format(datetime_now(), severity.upper(), data_str)
            
    except Exception as e:
        print(f'ERROR log2: {e}')

def socket_emit2(data, channel_layer, channel_uuid, channel_mux='', own_name =''):
    #print("socket_emit2-common.py---data---106",data)
    #print("socket_emit2-common.py---channel_layer---109",channel_layer)
    #print("socket_emit2-common.py---channel_uuid---110",channel_uuid)
    #print("socket_emit2-common.py---channel_mux---111",channel_mux)
    #print("socket_emit2-common.py---own_name---1",own_name)
    
    try:
        if not channel_layer:
            return
        try:
            if channel_mux == "price":
                

                #print("common.pymom---104print data string-------------newdata------------",data)
                
                username = own_name
                

                
                #print('---------------username-----------',username)
                x=get_database_data(username)
                
                
                newdata = x.copy()
                newdata.update(data)
                
                
                
                async_to_sync(channel_layer.group_send)(channel_uuid, {'type': 'forward_msg', 'message': newdata,'channel_mux': channel_mux})
                



            else:
                async_to_sync(channel_layer.group_send)(channel_uuid, {'type': 'forward_msg', 'message': data,'channel_mux': channel_mux})

            #elif channel_mux == "tracking":
             #   exampleSet= data
              #  
               # 
                #keyValList = [username]
                #expectedResult = [d for d in exampleSet if d['own_name'] in keyValList]
                #print('-----------expectedResult----------',expectedResult)
                  #

                #async_to_sync(channel_layer.group_send)(channel_uuid, {'type': 'forward_msg', 'message': expectedResult,'channel_mux': channel_mux})"""




            



            
            #print("common.pymom---104print data string-------------newdata------------",data)
            #print("common.pymom---105print data string------------channel_mux-------------",channel_mux)
            #print("common.pymom---105print data string-------web_input_common------------------",web_input_common['own_name'])
            #print("common.pymom---105print data string----------common_bot_name---------------",common_bot_name)
            

        except:
            tb = traceback.format_exc()
            print(tb)
    except Exception as e:
        print(f'ERROR socket_emit2: {e}')

def write_csv(file_path, header, data:list, mode='w'):
    with open(file_path, mode=mode) as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        for row in data:
            writer.writerow(row)

class IntObject():
    __integer_number = 0
    def __int__(self):
        return self.__integer_number
    def inc(self):
        self.__integer_number += 1
        return self.__integer_number
    def dec(self):
        self.__integer_number -= 1
        return self.__integer_number
    def set(self, new_value):
        if isinstance(new_value, int):
            self.__integer_number = new_value
            return self.__integer_number
        else:
            raise Exception('Except int type only!')

def roundTime(dt=None, dateDelta=timedelta(minutes=1)):
    """Round a datetime object to a multiple of a timedelta
    dt : datetime object, default now.
    dateDelta : timedelta object, we round to a multiple of this, default 1 minute.
    """
    roundTo = dateDelta.total_seconds()
    if dt == None: dt = datetime.now()
    seconds = (dt - dt.min).seconds
    # // is a floor division, not a comment on following line:
    rounding = (seconds + roundTo / 2) // roundTo * roundTo
    return dt + timedelta(0, rounding - seconds, -dt.microsecond)

# Overwrite 'run' method of class Timer in /usr/lib/pythonXXX/threading.py.
# It will call a user-func after a given interval,
# So make sure that the func does not execute longer than the interval.
class DelayedRepeatTimer(Timer):
    def run(self):
        # Waiting for round time to start timer
        mins = int(self.interval / 60) if self.interval > 60 else 1
        rounded_time = roundTime(datetime.now(), timedelta(minutes=mins))
        while datetime.now() <= rounded_time:
            sleep(1)
        Thread(target=self.function, args=self.args, kwargs=self.kwargs).start()
        while not self.finished.wait(self.interval):
            Thread(target=self.function, args=self.args, kwargs=self.kwargs).start()

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            Thread(target=self.function, args=self.args, kwargs=self.kwargs).start()