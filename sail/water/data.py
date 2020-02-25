from sail.util import Spider
from sail.constant.constant import ShStockListURL, SzStockListURL, KcbStockListURL


class StockDataSourceNet:
    """
    Data from crawl Internet, data fields: stock_code, stock_name, stock_pe
    """
    def __init__(self):
        self._from = Spider()

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
        self._sh_stock_list = self._from.get_stock_list(self._sh_stock_api, self._sh)
        return self._sh_stock_list

    def get_sz_stock_data(self):
        self._sz_stock_list = self._from.get_stock_list(self._sz_stock_api, self._sh)
        return self._sz_stock_list

    def get_kcb_stock_data(self):
        self._kcb_stock_list = self._from.get_stock_list(self._kcb_stock_api, self._sh)
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


if __name__ == '__main__':
    sd = StockDataSourceNet()
    r = sd.get_all_stock_data()
    print(r)
