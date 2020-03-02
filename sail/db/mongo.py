from pymongo import MongoClient
from datetime import date
from sail.constant import DBURL

__all__ = ['db']


class DB:
    
    POOL_COLL = "pool_his"
    STOCK_MACD_COLL = "stock_macd_his"
    def __init__(self, url):
        self.url = url
        self.client = MongoClient(self.url, maxPoolSize=40)
        self.db = self.client.sailboat_db

    def insert_stock_pool(self, document, coll_name=""):
        """
        document :{
            date,
            size,
            stock_set,
        }
        """
        coll = coll_name if coll_name else self.POOL_COLL
        filter = {"date": document['date']}
        update = {"$set": {"stock_set": document['stock_set']}}

        return self._insert(filter, update, document, coll)

    def _insert(self, filter, update, document, coll_name):

        self.coll = self.db[coll_name]
        # if document exist, update data
        res = self.coll.find_one_and_update(filter, update)
        if not res:
            self.coll.insert_one(document)
        return "ok"

    def insert_stock_macd(self, document, coll_name=""):
        """
        document :{
            date,
            stock_code,
            size,
            macd_set,
        }
        """
        coll = coll_name if coll_name else self.STOCK_MACD_COLL
        filter = {"date": document['date'],
                  "stock_code": document['stock_code']}
        update = {"$set": {"macd_set": document['macd_set']}}

        return self._insert(filter, update, document, coll)

    def find_stock_pool(self, coll_name=""):
        if not coll_name:
            coll_name = self.POOL_COLL
        self.coll = self.db[coll_name]

        filter = {"date": date.today().isoformat()}
        result_data = self.db[coll_name].find_one(filter=filter)
        return result_data.get("stock_set")


url = DBURL
db = DB(url)
