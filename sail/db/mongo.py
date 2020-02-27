from pymongo import MongoClient
from sail.constant import DBURL
__all__ = ['db']


class DB:
    def __init__(self, url):
        self.url = url
        self.client = MongoClient(self.url, maxPoolSize=40)
        self.db = self.client.sailboat_db
        self.coll = self.db.pool_his

    def insert(self, document, coll_name=""):
        result = self.coll[coll_name].insert(document)
        return result.inserted_id


url = DBURL
db = DB(url)
