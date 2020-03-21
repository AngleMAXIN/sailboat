from sail.constant.constant import (KcbStockListURL, ShStockListURL,
                                    StockHisDataURL, SzStockListURL)
from sail.util import Spider, logger

__all__ = ['StockDataSourceNet', 'StockHistoryDataNet']


class StockDataSourceNet:
    """
    Data from crawl Internet, include sh, sz, kcb stock ,data fields: stock_code, stock_name, stock_pe
    """

    def __init__(self):
        self.type = "all"
        self._from = Spider(self.type)

        self._sh = "sh"
        self._sz = "sz"
        self._kcb = "kcb"

        self._sh_stock_api = ShStockListURL
        self._sz_stock_api = SzStockListURL
        self._kcb_stock_api = KcbStockListURL

        self._sh_stock_list = []
        self._sz_stock_list = []
        self._kcb_stock_list = []

    def get_sh_stock_data(self):
        self._sh_stock_list = self._from.get_stock_list(
            self._sh_stock_api, self._sh)
        return self._sh_stock_list

    def get_sz_stock_data(self):
        self._sz_stock_list = self._from.get_stock_list(
            self._sz_stock_api, self._sh)
        return self._sz_stock_list

    def get_kcb_stock_data(self):
        self._kcb_stock_list = self._from.get_stock_list(
            self._kcb_stock_api, self._sh)
        return self._from.get_stock_list(self._kcb_stock_api, self._kcb)

    def get_all_stock_data(self, kcb=False):
        if not self._sz_stock_list:
            self._sz_stock_list = self.get_sz_stock_data()

        if not self._sh_stock_list:
            self._sh_stock_list = self.get_sh_stock_data()

        all_stock = []
        if kcb:
            if not self._kcb_stock_list:
                self._kcb_stock_list = self.get_kcb_stock_data()

        all_stock.extend(self._kcb_stock_list)
        all_stock.extend(self._sh_stock_list)
        all_stock.extend(self._kcb_stock_list)

        return tuple(all_stock)


class StockHistoryDataNet:
    """
    Data from crawl Internet, include one stock all history, data fields: [date, open, close]
    """

    def __init__(self, stock_codes):
        self.type = "one"
        self._from = Spider(self.type)

        # key: stock_code, values: Tuple
        self.data_map = {}
        # stock_code prefix 0, is sz ,suffix is 2; prefix is 6, is sh, suffix is 1
        self.prefix_code = {"0": "2", "6": "1"}

        self.url_format = StockHisDataURL
        self.stock_codes = stock_codes if stock_codes else []

        self._start_get_data()

    def get_all_history(self, stock_code=""):
        """
        Return: Map[ stock_code ][ DateFrame[ date,close ] ]
        """
        return self.data_map.get(stock_code, self.data_map)

    def _start_get_data(self):
        for r_code in self.stock_codes:
            code = r_code + self.prefix_code[r_code[0]]
            url = self.url_format.format(code)

            tuple_stock_his = self._from.get_stock_list(url)
            if tuple_stock_his:
                logger.info("get stock code {0} successful".format(code))
            else:
                logger.error("get stock code {0} failed".format(code))
            self.data_map[r_code] = tuple_stock_his


if __name__ == '__main__':
    sd = StockDataSourceNet()
    r = sd.get_all_stock_data()
    print(r)
