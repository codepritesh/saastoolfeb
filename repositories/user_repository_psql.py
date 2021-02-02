import psycopg2
from const_postgresql import *
import traceback
from singleton_decorator import singleton


@singleton
class UserRepositoryPSQL:

    def __init__(self):
        try:
            self._conn = psycopg2.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD)
        except Exception as e:
            tb = traceback.format_exc()
            print('ERROR {}'.format(tb))

    def get_api_4_exchange(self, username, key_name):
        api = None, None, None
        try:
            # create a cursor
            self._cur = self._conn.cursor()
            # create a cursor
            self._cur.execute(f"""SELECT api_keys, secret_keys, passphrase FROM setup_apikey_apikey JOIN auth_user au ON setup_apikey_apikey.own_name_id = au.id WHERE setup_apikey_apikey.name='{key_name}' AND au.username='{username}';""")
            # display the PostgreSQL database server version
            data = self._cur.fetchall()
            if data:
                api = data[0]
            # close the communication with the PostgreSQL
            self._cur.close()
        except psycopg2.InterfaceError:
            self._conn = psycopg2.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD)
        except Exception as e:
            tb = traceback.format_exc()
            print('ERROR {}'.format(tb))
        return api

    def list_name_api_key(self, username):
        api_names = []
        try:
            # create a cursor
            self._cur = self._conn.cursor()
            self._cur.execute(f"""SELECT name FROM setup_apikey_apikey JOIN auth_user au ON setup_apikey_apikey.own_name_id = au.id WHERE au.username='{username}';""")
            # display the PostgreSQL database server version
            data = self._cur.fetchall()
            if data:
                for item in data:
                    api_names.append(''.join(item))
            # close the communication with the PostgreSQL
            self._cur.close()
        except psycopg2.InterfaceError:
            self._conn = psycopg2.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD)
            # return self.list_name_api_key(username)
        except Exception as e:
            tb = traceback.format_exc()
            print('ERROR {}'.format(tb))
        return api_names

    def get_name_api_for_user(self, username, ex=None):
        data = []
        vip_user = [ 'master', 'vip_trader01', 'vip_trader02']
        try:
            # create a cursor
            self._cur = self._conn.cursor()
            if username in vip_user:
                if not ex:
                    self._cur.execute(f"""SELECT name, ex_id FROM setup_apikey_apikey where setup_apikey_apikey.exclude_pnl=false;""")
                else:
                    self._cur.execute(f"""SELECT name, ex_id FROM setup_apikey_apikey where setup_apikey_apikey.ex_id='{ex}' and setup_apikey_apikey.exclude_pnl=false;""")
                # display the PostgreSQL database server version
                data = self._cur.fetchall()
                # if data:
                #     for item in data:
                #         api_names.append(''.join(item))
                # close the communication with the PostgreSQL
            self._cur.close()
        except psycopg2.InterfaceError:
            self._conn = psycopg2.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD)
            # return self.list_name_api_key(username)
        except Exception as e:
            tb = traceback.format_exc()
            print('ERROR {}'.format(tb))
        return data

    def get_own_name(self, api_name):
        data = None
        try:
            # create a cursor
            self._cur = self._conn.cursor()
            self._cur.execute(f"""SELECT ex_id, username FROM setup_apikey_apikey JOIN auth_user au ON setup_apikey_apikey.own_name_id = au.id WHERE setup_apikey_apikey.name='{api_name}'; """)
            # display the PostgreSQL database server version
            data = self._cur.fetchall()
            # close the communication with the PostgreSQL
            self._cur.close()
        except psycopg2.InterfaceError:
            self._conn = psycopg2.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD)
            # return self.list_name_api_key(username)
        except Exception as e:
            tb = traceback.format_exc()
            print('ERROR {}'.format(tb))
        if data:
            return data[0]

if __name__ == '__main__':
    a = UserRepositoryPSQL()
    print(a.get_own_name('ngocngoc.hh1'))
    # a.get_name_api_for_user('master', 'HIT')
