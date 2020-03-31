import pandas as pd

from sail.constant.constant import (KcbStockListURL, ShStockListURL,
                                    StockHisDataURL, SzStockListURL)
from sail.db import db
from sail.util import Spider, logger
from celery_task.tasks import insert_stock_history_async

__all__ = ['StockDataSourceNet',
           'StockDataSourceInternet', 'StockDataSourceDB']


class StockDataSourceNet:
    """
        股票池原始资源
        Data from crawl Internet, include sh, sz, kcb stock ,data fields: stock_code, stock_name, stock_pe
    """

    def __init__(self):
        self.type = "all"
        self.internet_source = Spider(self.type)

        self._sh = "sh"
        self._sz = "sz"
        self._kcb = "kcb"

        self._sh_stock_api = ShStockListURL
        self._sz_stock_api = SzStockListURL
        self._kcb_stock_api = KcbStockListURL

        self._sh_stock_list = []
        self._sz_stock_list = []
        self._kcb_stock_list = []

    def _get_sh_stock_data(self):
        self._sh_stock_list = self.internet_source.get_stock_list(
            self._sh_stock_api, self._sh)
        return self._sh_stock_list

    def _get_sz_stock_data(self):
        self._sz_stock_list = self.internet_source.get_stock_list(
            self._sz_stock_api, self._sh)
        return self._sz_stock_list

    def get_kcb_stock_data(self):
        self._kcb_stock_list = self.internet_source.get_stock_list(
            self._kcb_stock_api, self._sh)
        return self.internet_source.get_stock_list(self._kcb_stock_api, self._kcb)

    def get_all_stock_data(self, kcb=False):
        # if not self._sz_stock_list:
        self._sz_stock_list = self._get_sz_stock_data()

        # if not self._sh_stock_list:
        self._sh_stock_list = self._get_sh_stock_data()

        all_stock = []
        if kcb:
            if not self._kcb_stock_list:
                self._kcb_stock_list = self.get_kcb_stock_data()

        all_stock.extend(self._sz_stock_list)
        all_stock.extend(self._sh_stock_list)
        all_stock.extend(self._kcb_stock_list)

        return tuple(all_stock)


class StockDataSourceInternet:
    """
    Data from crawl Internet, include one stock all history, data fields: [date, open, close]
    """

    def __init__(self, ):
        self.type = "one"
        self._from = Spider(self.type)

        # key: stock_code, values: Tuple
        self.data_map = {}
        self.data_tuple = tuple()
        # stock_code prefix 0, is sz ,suffix is 2; prefix is 6, is sh, suffix is 1
        self.prefix_code = {"0": "2", "6": "1"}

        self.url_format = StockHisDataURL

    def get_all_history(self, stock_code=""):
        """
        Return: Map[ stock_code ][ DateFrame[ date,close ] ]
        """
        return self.data_map.get(stock_code, self.data_map)

    def _start_get_data(self, stock_codes):
        task_url = []
        for r_code in stock_codes:
            code = r_code + self.prefix_code[r_code[0]]
            task_url.append(self.url_format.format(code))

        self.stock_set = self._from.get_stock_list(task_url)

    def get_batch_stock_close(self, stock_codes=None):
        self._start_get_data(stock_codes)
        return self.stock_set

    def async_insert(self):
        for _set in self.stock_set:
            insert_stock_history_async(_set)


class StockDataSourceDB:
    """
    Return data source from local storage
    Type: DataFrame 
    Include:1> raw data of close price
            2> include ma5, ma10 ,ma20

    """

    def __init__(self):
        self.db_source = db
    # self.close_exclude = ['open', 'volume', 'ma5', 'ma10', 'ma20', ]
        # self.ma_exclude = ["open", "volume", ]

        # self.close_type = 2
        # self.ma_type = 1

    def _generate_df(self, one):
        code = one.get("stock_code")
        list_history = one.get("history_data")

        df = pd.DataFrame(list_history)
        try:
            df.set_index(['date'], inplace=True)
        except KeyError:
            return code, None

        # if _type == self.ma_type:
            # lebels = self.ma_exclude
        # elif _type == self.close_type:
            # lebels = self.close_exclude
 
        # df = df.drop(lebels, axis=1)
        # print(df.columns)
        return code, df

    def get_one_stock_ma(self, stock_code=""):
        '''

        返回一只股票的均线值，包括5日，10日，20日均线
        ～～～～～～～～～～～～～～～
        Type: DataFrame
        Include: date, ma5, ma10, ma20
        '''
        if not stock_code:
            return
        one = self.db_source.get_one_stock(stock_code=stock_code)
        _, df = self._generate_df(one)
        return df

    def get_one_stock_close(self, stock_code=""):
        '''
        返回一只股票的历史收盘价数据
        ～～～～～～～～～～～～～～～
        Type: DataFrame
        Include: date, close
        '''
        if not stock_code:
            return
        one = self.db_source.get_one_stock(stock_code=stock_code)
        if not one:
            return
        _, df = self._generate_df(one)
        return df

    def get_batch_stock_close(self, stock_codes=None):
        '''
        批量返回一批股票的历史收盘价
        ～～～～～～～～～～～～～～～
        Type: Tuple(Tuple(string, DataFrame))
        Include: code, df
        '''
        result_set = self.db_source.get_all_stock(stock_codes)

        if not result_set:
            return
        generate_result = (self._generate_df(one) for one in result_set)
        return generate_result

    def get_stock_pool(self):
        '''
        返回股票池里的股票
        ～～～～～～～～～～～～～～～
        Type: Dict
        Include: date, stock_set, pool_size, rule
        '''
        stock_pool = self.db_source.get_stock_pool()
        if stock_pool is None:
            logger.error("stock pool is Null")
            return dict()
        return stock_pool

    def get_macd_rule_stock(self, stock_codes):
        '''
        返回一只股票的macd值，包含已经计算好的买卖点
        ～～～～～～～～～～～～～～～
        Type: Dict
        Include: date, stock_code, size, macd_set
        '''
        return self.db_source.get_macd_of_stock(stock_codes)


if __name__ == '__main__':
    sd = StockDataSourceNet()
    r = sd.get_all_stock_data()
    print(r)
