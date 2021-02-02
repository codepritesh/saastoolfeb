from pymongo import MongoClient
from urllib.parse import quote_plus

MONGODB_DEFAULT_SERVER = 'localhost'
MONGODB_DEFAULT_PORT = 27017

class DB():
    def __init__(self, server=MONGODB_DEFAULT_SERVER, port=MONGODB_DEFAULT_PORT, username='', passwd=''):
        self.__server = server
        self.__port = port
        self.__username = quote_plus(username)
        self.__password = quote_plus(passwd)
        if username:
            self.__uri = 'mongodb://%s:%s@%s:%s' % (self.__username, self.__password, server, port)
        else:
            self.__uri = 'mongodb://%s:%s' % (server, port)
        self.__client = MongoClient(self.__uri)
        self.__db_name = ''
        self.__db = None

    def get_client(self):
        return self.__client

    def close_client(self):
        self.__client.close()

    def get_all_databases_in_client(self):
        return self.__client.list_database_names()

    def get_all_collections(self):
        return self.__db.list_collection_names()

    def create_database(self, db_name):
        self.__db_name = db_name
        self.__db = self.__client[db_name]

    def get_database(self, db_name=''):
        if not db_name:
            return self.__db
        return self.__client[db_name]

    def delete_database(self, db_name):
        self.__client.drop_database(db_name)

    def self_delete(self):
        self.__client.drop_database(self.__db_name)
        self.__client.close()

    def add_collection(self, collection):
        self.__db[collection]

    def get_collection(self, collection):
        return self.__db[collection]

    def drop_collection(self, collection):
        self.__db[collection].drop()

    def insert_document(self, collection, doc={}):
        self.__db[collection].insert_one(doc)

    def query_document(self, collection, query, find_one=False):
        if find_one:
            return self.__db[collection].find_one(query)
        else:
            return self.__db[collection].find(query)

    def update_document(self, collection, query, new_value):
        set_new_value = {'$set': new_value}
        self.__db[collection].find_one_and_update(query, set_new_value, upsert=True)
        return True

    def delete_document(self, collection, query):
        self.__db[collection].delete_one(query)
        return True

    def delete_many(self, collection, query):
        return self.__db[collection].delete_many(query)
