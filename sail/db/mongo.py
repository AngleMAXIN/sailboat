import time
from datetime import date

from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)

from pymongo import MongoClient, DESCENDING

from sail.constant import DBURL


__all__ = ['db']
 

class DB:
    STOCK_RAW_COLL = "stock"
    POOL_COLL = "pool_his"
    STOCK_MACD_COLL = "stock_macd_his"
    STOCK_MA_COLL = "stock_ma_his"
    STOCK_KDJ_COLL = "stock_kdj_his"
    BACK_TEST_RES = "back_test_his"
    
    def __init__(self, url):
        self.url = url
        self.client = MongoClient(self.url, maxPoolSize=40)
        self.db = self.client.sailboat_db

        self.macd_is_clean = False
        self.ma_is_clean = False
        self.kdj_is_clean = False

    def insert_stock_pool(self, document, coll_name=""):
        """
        document :{
            date,
            size,
            stock_set,
        }
        """
        coll = coll_name if coll_name else self.POOL_COLL
        _filter = {"date": document['date']}
        update = {"$set": {"stock_set": document['stock_set']}}
        document["pool_id"] = int(time.time())
        return self._insert(_filter, update, document, coll)

    def _insert(self, _filter=None, update=None, document=None, coll_name=""):

        coll = self.db[coll_name]
        # if document exist, update data
        res = None
        if update and _filter:
            res = coll.find_one_and_update(_filter, update)
        if not res:
            coll.insert_one(document)
        return "ok"

    def insert_stock_history(self, document, coll_name=""):

        coll = self.STOCK_RAW_COLL
        _filter = {"stock_code": document.get('stock_code',"")}
        update = {"$set": {"history_data": document.get('history_data')}}

        return self._insert(_filter, update, document, coll)

    def insert_back_test_result(self, document, coll_name=""):

        coll = coll_name if coll_name else self.BACK_TEST_RES
        # _filter = {"date": document['date']}
        # update = {"$set": {"stock_set": document['stock_set']}}
        _filter = None
        update = None
        return self._insert(_filter, update, document, coll)


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
        if not self.macd_is_clean:
            # 清除以往的数据，保证每一次计算都是最新的数据
            self.db[coll].drop()
            self.macd_is_clean = True

        _filter = {"date": document['date'],
                  "stock_code": document['stock_code']}
        update = {"$set": {"stock_set": document['stock_set']}}

        return self._insert(_filter, update, document, coll)

    def insert_stock_ma(self, document, coll_name=""):
        """
        document :{
            date,
            stock_code,
            size,
            macd_set,
        }
        """

        coll = coll_name if coll_name else self.STOCK_MA_COLL
        if not self.ma_is_clean:
            print("clean data:",self.ma_is_clean)
            # 清除以往的数据，保证每一次计算都是最新的数据
            self.db[coll].drop()
            self.ma_is_clean = True

        _filter = {"date": document['date'],
                  "stock_code": document['stock_code']}
        update = {"$set": {"stock_set": document['stock_set']}}

        return self._insert(_filter, update, document, coll)

    def insert_stock_kdj(self, document, coll_name=""):
        """
        document :{
            date,
            stock_code,
            size,
            macd_set,
        }
        """

        coll = coll_name if coll_name else self.STOCK_KDJ_COLL
        if not self.kdj_is_clean:
            # 清除以往的数据，保证每一次计算都是最新的数据
            self.db[coll].drop()
            self.kdj_is_clean = True

        _filter = {"date": document['date'],
                  "stock_code": document['stock_code']}
        update = {"$set": {"stock_set": document['stock_set']}}

        return self._insert(_filter, update, document, coll)

    def get_stock_pool(self, coll_name=""):
        """
            获取当前最新股票池的股票数据
            return：
        """
        if not coll_name:
            coll_name = self.POOL_COLL
        coll = self.db[coll_name]

        _filter = {"date": date.today().isoformat()}
        result_data = coll.find().sort("_id", DESCENDING).limit(1)[0]
        return result_data

    def get_macd_of_stock(self, stock_codes=None):

        coll = self.db[self.STOCK_MACD_COLL]
        return self._get_data_of_stock(coll,stock_codes)

    def get_ma_of_stock(self, stock_codes=None):

        coll = self.db[self.STOCK_MA_COLL]
        return self._get_data_of_stock(coll,stock_codes)

    def get_kdj_of_stock(self, stock_codes=None):
        coll = self.db[self.STOCK_KDJ_COLL]
        return self._get_data_of_stock(coll,stock_codes)

    def _get_data_of_stock(self, coll,stock_codes):
        if len(stock_codes) < 2:
            _filter = {"stock_code": stock_codes}
        else:
            _filter = {"stock_code": {"$in":stock_codes}}
        result_data = coll.find(_filter)
        return result_data
        
    def get_all_stock(self,stock_codes=None):
        coll = self.db[self.STOCK_RAW_COLL]
        if not stock_codes:
            list_result = coll.find()
        else:
            _filter = {"stockid":{"$in":stock_codes}}
            list_result = coll.find(_filter)
        return list_result

    def get_one_stock(self, stock_code=""):
        if not stock_code:
            return dict()
        coll = self.db[self.STOCK_RAW_COLL]
        _filter = {"stockid":stock_code}
        one_result = coll.find_one(filter=_filter)
        return  one_result

url = DBURL
db = DB(url)
