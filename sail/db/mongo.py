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

        self.is_clean = False

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

        coll = self.db[coll_name]
        # if document exist, update data
        res = coll.find_one_and_update(filter, update)
        if not res:
            coll.insert_one(document)
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
        if not self.is_clean:
            # 清除以往的数据，保证每一次计算都是最新的数据
            self.db[coll].drop()
            self.is_clean = True

        filter = {"date": document['date'],
                  "stock_code": document['stock_code']}
        update = {"$set": {"macd_set": document['macd_set']}}

        return self._insert(filter, update, document, coll)

    def find_stock_pool(self, coll_name=""):
        if not coll_name:
            coll_name = self.POOL_COLL
        coll = self.db[coll_name]

        _filter = {"date": date.today().isoformat()}
        result_data = coll.find_one(filter=_filter)
        return result_data.get("stock_set")

    def find_macd_rule_stock(self, stock_code=""):

        coll = self.db[self.STOCK_MACD_COLL]
        if not stock_code:
            result_data = coll.find()
        else:
            _filter = {"stock_code": stock_code}
            result_data = coll.find_one(filter=_filter)
        return result_data


url = DBURL
db = DB(url)
