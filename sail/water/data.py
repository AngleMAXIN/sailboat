from sail.util import Spider
from sail.constant.constant import ShStockListURL, SzStockListURL, KcbStockListURL


class StockDataSource(Spider):
    def __init__(self):
        super().__init__()

        self._sh = "sh"
        self._sz = "sz"
        self._kcb = "kcb"

        self._sh_stock_api = ShStockListURL
        self._sz_stock_api = SzStockListURL
        self._kcb_stock_api = KcbStockListURL

        _sh_stock_list = []
        _sz_stock_list = []
        _kcb_stock_list = []

    def get_sh_stock_data(self):
        return super().get_stock_list(self._sh_stock_api, self._sh)

    def get_sz_stock_data(self):
        return super().get_stock_list(self._sz_stock_api, self._sz)

    def get_kcb_stock_data(self):
        return super().get_stock_list(self._kcb_stock_api, self._kcb)

    def get_all_stock_data(self):
        sh_stock = super().get_stock_list(self._sh_stock_api, self._sh)
        sz_stock = super().get_stock_list(self._sz_stock_api, self._sz)
        kcb_stock = super().get_stock_list(self._kcb_stock_api, self._kcb)

        all_stock = []
        all_stock.extend(sh_stock)
        all_stock.extend(sz_stock)
        all_stock.extend(kcb_stock)
        return tuple(all_stock)

