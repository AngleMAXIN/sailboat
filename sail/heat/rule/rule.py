import pandas as pd
import numpy as np
from datetime import date
from sail.util import get_macd
from sail.water import StockHistoryDataNet
from sail.db import db


class MacdRule:
    def __init__(self, stock_pool_codes, store=True):
        self.stock_codes = stock_pool_codes
        self.store = store

    def _get_macd(self):

        source = StockHistoryDataNet(self.stock_codes)
        source_data = source.get_all_history()
        for code, his_data in source_data.items():
            df = pd.DataFrame(his_data)
            df.close = df.close.astype(np.float)
            _, _, _macd = get_macd(df.close.values)

            df.insert(2, "macd", _macd)
            df.dropna(axis=0, how="any", inplace=True)
            df.reset_index(drop=True, inplace=True)
            if self.store:
                df.drop(['close'], axis=1, inplace=True)
                document = {
                    "date": date.today().isoformat(),
                    "stock_code": code,
                    "size": int(df.size),
                    "macd_set": df.values.tolist(),
                }
                db.insert_stock_macd(document)
                df.to_csv(
                    "/home/maxin/{0}_{1}_macd.csv".format(code, date.today().isoformat()))
        return df.shift()

    def get_macd_data(self, code=""):

        pass

    def run(self):
        macd_df = self._get_macd()
        self._set_trading_time(macd_df)

    def _set_trading_time(self,df):

        df['chance'] = 0
        for i in range(1, df.shape[0]):
            raw = df.iloc[i]
            pre_raw = df.iloc[i-1]
            if raw.macd < 0 and pre_raw.macd > 0:
                df.loc[i, 'chance'] = -1
            elif raw.macd > 0 and pre_raw.macd < 0:
                df.loc[i, 'chance'] = 1            
        df.to_csv("./result.csv")