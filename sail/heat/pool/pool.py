import datetime

import pandas as pd

from sail.constant import StorePath
from sail.water import StockDataSourceNet

__all__ = ('StockPool')

class StockPool:
    def __init__(self, pool_limit=0, is_storage=True, path=StorePath):
        self.source = StockDataSourceNet()

        self.pool_limit = pool_limit
        self.pool_stock = None

        self.is_storage = is_storage
        self.store_path = path

        self.pe = ""
        self.pe_level = 0.0
        self.pe_top = 0, 0

    def set_pe_rules(self, top, level):
        self.pe = "pe"
        self.pe_level = level
        self.pe_top = top

    def _get_raw_data(self):
        raws = self.source.get_all_stock_data()
        df = pd.DataFrame(raws)
        df.columns = ('stock_pe', 'stock_code', 'stock_name')
        df = df[~(df['stock_pe'] == '-')]
        return df.copy()

    def get_pool(self):
        df = self._get_raw_data()
        if self.pe:
            self.pool_stock = df[(df[self.pe] > self.pe_level) & (df[self.pe] < self.pe_top)]
        # reset index
        self.pool_stock.reset_index(drop=True, inplace=True)

        if self.is_storage:
            self._to_cvs_file()
        return self.pool_stock

    def _to_cvs_file(self):
        csv_path = "{}/{}.csv".format(self.store_path, datetime.date.today().isoformat())
        self.pool_stock.to_csv(csv_path)

    # def to_list(self):
    #     if not self.pool_stock:
    #         return
    #     return self.pool_stock.to_list()

