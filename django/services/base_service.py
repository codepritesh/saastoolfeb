import os, sys, time
import traceback
import uuid
#from datetime import datetime
from socket import gethostname
from threading import Thread
from singleton_decorator import singleton
from channels.layers import get_channel_layer
dir_path = os.path.dirname(os.path.realpath(__file__))
repo_path = dir_path + '/../..'
repo_path = os.path.abspath(repo_path)
log_path = repo_path + '/django/logs'
lib_path = repo_path + '/libs'
repositories_path = repo_path + '/repositories'
sys.path.append(lib_path)
sys.path.append(repositories_path)
from common import socket_emit2, datetime_now
from pprint import pprint
from services.bot_running_databasepush import *
import json


@singleton
class BaseService:
    INSTANCE_ACTIVE = 'active'
    INSTANCE_STOPPED = 'stopped'
    def __init__(self):
        self.bot_instances = {}
        self.srv_id = str(uuid.uuid1())
        self._channel = 'd028aee0-5323-11eb-89c5-a3e60c8ea960'
        self.__channel_layer = get_channel_layer()
        self._db = None
        self._collection = ''

        self.bot_dic_list = {}

        Thread(target=self.__check_running_instances, args=()).start()

    def __check_running_instances(self):
        while True:
            bot_data = []
            self.bot_dic_list={}
            for alias, bot_info_dict in self.bot_instances.copy().items():
                num_bot = 0
                web_data = []
                bot_data = []
                for uuid, value in bot_info_dict.copy().items():
                    if uuid == 'last_num_bots':
                        last_num_bots = value
                        continue
                    num_bot += 1
                    start_time = value.get('time')
                    web_input = value.get('web_input')
                    pair = web_input.get('pair')
                    own_name = web_input.get('own_name')
                    ex_id = web_input.get('ex_id')
                    api_name = web_input.get('api_name')
                    # get link dashboard
                    link = web_input.get('link_grafana')
                    bot_alias_obj = value.get('bot')
                    bot_alias_name= bot_alias_obj.alias

                    if not link:
                        link = ''
                        web_input.update({
                            'link_grafana': link
                        })
                    web_data.append({'uuid': uuid, 'time': start_time, 'own_name': own_name, 'pair': pair,
                                     'ex_id': ex_id, 'api_name': api_name, 'link_grafana': link})
                    bot_data.append({'uuid': uuid, 'time': start_time, 'own_name': own_name, 'pair': pair,
                                     'ex_id': ex_id, 'api_name': api_name,'bot_alias':bot_alias_name})
                self.bot_dic_list[bot_alias_name] = bot_data

                
                if not num_bot and not last_num_bots:
                    continue
                self.bot_instances[alias].update({'last_num_bots': num_bot})
                channel = alias + self.srv_id
                self._channel = channel
                socket_emit2(web_data, self.__channel_layer, channel, 'tracking')
                #print("web-------------------------data",web_data)
                socket_emit2(self.bot_dic_list, self.__channel_layer, channel, 'tracking')
                #print("bot_dic_list-------------------------bot_dic_list",self.bot_dic_list)

                
                try:
                    running_bot_file = open("services/running_bot_file.txt",'w')
                    json.dump(self.bot_dic_list, running_bot_file)
                    running_bot_file.close()
                except:
                    print("Unable to write running_bot_file")
                try:
                    running_bot_file = open('services/running_bot_instances_file.txt', 'wt')
                    running_bot_file.write(str(self.bot_instances))
                    running_bot_file.close()
                except:
                    print("Unable to write running bot_instances")


                #pprint(self.bot_dic_list)
                #print("-------------------------------------")
                

                
            time.sleep(2)
            update_status = update_running_bot_to_database()           

    def add_bot_running(self, bot_alias, bot_uuid, bot, thread, web_input, bot_input):
        time.sleep(3)
        check_max_bot_running = get_max_bot_running(bot_alias,web_input)
        if check_max_bot_running == True:
        #pprint(vars(self))
            if not self.bot_instances.get(bot_alias):
                self.bot_instances[bot_alias] = {'last_num_bots': 0}
            dt_now = datetime_now()
            epoch = int(time.time() * 1000)
            instance_data = {bot_uuid: {'bot': bot, 'thread': thread, 'web_input': web_input,
                                        'bot_input': bot_input, 'time': dt_now}}
            self.bot_instances[bot_alias].update(instance_data)
            hostname = gethostname()
            port = web_input.get('port')
            if not self._collection and port:
                self._collection = '{}:{}'.format(hostname, port)
            if self._db and self._collection:
                instance_data = {'bot_alias': bot_alias, 'web_input': web_input, 'time': dt_now,
                                                 'epoch': epoch, 'status': self.INSTANCE_ACTIVE}
                self._db.update_document(self._collection, {'_id': bot_uuid}, instance_data)
        else:
            return None


    def start_bot(self, bot_alias, web_input):
        pass

    def fetch_detail(self, bot_alias, bot_uuid):
        if bot_uuid in self.bot_instances.get(bot_alias, {}).keys():
            return self.bot_instances[bot_alias][bot_uuid]['web_input']
        return None

    def stop_bot(self, bot_alias, data, bot_index=0):
        uuid = data['uuid']
        if uuid in self.bot_instances.copy().get(bot_alias, {}).keys():
            bot_info = self.bot_instances[bot_alias].pop(uuid)
            if self._db and self._collection:
                self._db.delete_document(self._collection, {'_id': uuid})
            bot = bot_info['bot']
            try:
                # handle one way
                if isinstance(bot, list):
                    for item in bot.copy():
                        if hasattr(item, 'terminate'):
                            item.terminate()
                    return True
                bot.terminate()
                return True
            except Exception as e:
                tb = traceback.format_exc()
                print('ERROR Base_Service: {} {}'.format(e, tb))
                return False
        return False

    def fetch_list(self, bot_alias):
        data = []
        for uuid in self.bot_instances.copy().get(bot_alias, {}).keys():
            web_input = self.bot_instances[bot_alias][uuid]['web_input']
            time_val = self.bot_instances[bot_alias][uuid]['time']
            item = web_input
            item.update({'uuid': uuid, 'time': time_val})
            data.append(item)
        return data

    # handel 2 case: bot: bot and bot=[bot1, bot2]
    # default if bot is list, return bot index 0
    def fetch_bot(self, bot_alias, uuid, bot_index=0):
        if not uuid:
            return None
        if uuid in self.bot_instances.get(bot_alias, {}).keys():
            if isinstance(self.bot_instances[bot_alias][uuid]['bot'], list):
                return self.bot_instances[bot_alias][uuid]['bot'][bot_index]
            return self.bot_instances[bot_alias][uuid]['bot']
        return None

    # check bot is alive or dead
    # invoke when call tracking bot
    # handel if list thread (one way bot), return thread has index 0
    # else return thread
    def check_bot_status(self, thread_index=0):
        for uuid in self.bot_instances.copy().keys():
            if issubclass(self.bot_instances[uuid]['thread'], list):
                thread = self.bot_instances[uuid]['thread'][0]
            else:
                thread = self.bot_instances[uuid]['thread']
            if not thread.isAlive():
                # kill thread in another bot
                try:
                    if isinstance(self.bot_instances[uuid]['bot'], list):
                        for index, item in enumerate(self.bot_instances[uuid]['bot']):
                            if 0 == index:
                                continue
                            if hasattr(item, 'terminate'):
                                item.terminate()
                except Exception as e:
                    print('Error {}'.format(e))
                # del key uuid
                del self.bot_instances[uuid]

    # stop scanning
    def stop_scanning(self, bot_alias, web_input):
        bot = self.fetch_bot(bot_alias, web_input['uuid'])
        if not bot:
            return 'Bot not found'
        if hasattr(bot, 'stop_scanning'):
            bot.stop_scanning()
            return 'Stop scanning call success'
        return 'Method not found'
