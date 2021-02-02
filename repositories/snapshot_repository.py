import sys
import os
from datetime import datetime

from zope.interface import named

dir_path = os.path.dirname(os.path.realpath(__file__))
lib_path = dir_path + '/../libs'
sys.path.append(lib_path)
sys.path.append(dir_path)
from libdb import DB
from config_db import *
from singleton_decorator import singleton


@singleton
class SnapshotRepository():
    def __init__(self):
        self._database_name = 'bot_snapshots'
        self._db = DB(server=FANSIPAN_DB, port=FANSIPAN_DB_PORT,
                      username=FANSIPAN_DB_USERNAME, passwd=FANSIPAN_DB_PASSWD)
        self._db.create_database(self._database_name)

    def insert_document(self, collection, data={}):
        self._db.insert_document(collection, data)
        return True

    def query_document(self, collection, query, find_one=False):
        return self._db.query_document(collection, query, find_one)

    def update_document(self, collection, query, new_value):
        return self._db.update_document(collection, query, new_value)

    def delete_document(self, collection, query):
        return self._db.delete_document(collection, query)

    def delete_many(self, collection, query):
        return self._db.delete_many(collection, query)

    def fetch_all_bot(self, collection):
        return self.query_document(collection, {})

    def fetch_data(self, collection, _id=None):
        if _id:
            return self.query_document(collection, {'_id': _id, 'terminated': False}, True)
        else:
            return self.query_document(collection, {'terminated': False})
