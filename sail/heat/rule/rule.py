import time
from datetime import date
from multiprocessing import Pool, cpu_count

import gevent
import numpy as np
import pandas as pd

from celery_task.tasks import insert_chance_by_macd_async, stock_pool_update, insert_chance_by_ma_async
from sail.db import db
from sail.util import get_macd, get_ma
from sail.water import StockDataSourceDB

__all__ = ['Rule', 'BackTestRuleMacd']


def set_trading_time(df):
    df['chance'] = 0
    for i in range(1, df.shape[0]):
        raw = df.iloc[i]
        pre_raw = df.iloc[i - 1]
        if raw.macd < 0 and pre_raw.macd > 0:
            df.loc[i, 'chance'] = -1
        elif raw.macd > 0 and pre_raw.macd < 0:
            df.loc[i, 'chance'] = 1

    #  删除没有买卖点的列，节省存储空间
    df = df.drop(df[df.chance == 0].index)
    return df


def select_time_by_macd(code, df):

    _, _, _macd = get_macd(df.close.values)

    df.insert(1, "macd", _macd)
    df.dropna(axis=0, how="any", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # set time of business, 1 buy, -1 sell
    df_time = set_trading_time(df)

    document = {
        "date": date.today().isoformat(),
        "stock_code": code,
        "size": int(df_time.shape[0]),
        "macd_set": df_time.values.tolist(),
    }

    insert_chance_by_macd_async.delay(document)

def set_trading_time_ma(df):
    s2 = df["ma5"] > df["ma30"]
    s1 = df["ma5"] < df["ma30"]

    gold=df.loc[~(s1 | s2.shift(1))].index
    death=df.loc[(s1 & s2.shift(1))].index 
    g1=pd.Series(1,index=gold)                   #金叉标志位 1
    d1=pd.Series(0,index=death)                  #死叉标志位 0
    gd=g1.append(d1).sort_index()

    df.append(gb)
    return df

def select_time_by_ma(code, df):
    ma5, ma10, ma20 = get_ma(df.close.values)
    df["ma5"] = ma5
    df["ma10"] = ma10
    df["ma20"] =ma20
    
    df.dropna(axis=0, how="any", inplace=True)
    df.reset_index(drop=True, inplace=True)

    df_time = set_trading_time_ma(df)

    document = {
        "date":date.today().isoformat(),
        "stock_code":code,
        "size":int(df_time.shape[0]),
        "macd_set":df_time.values.tolist(),
    }

    insert_chance_by_ma_async(document)

class Rule:
    """
    指标计算 例如MACD,MA,KDJ等
    """
    def __init__(self, latest=False, from_internet=False):
        # 股票来源 股票池，所有股票
        self.latest = latest
        self.from_internet = from_internet

        self.db_source = StockDataSourceDB()

        self.pool = Pool(cpu_count())

        self._compute_macd_func = select_time_by_macd
        self._compute_ma_func = select_time_by_ma

    def _get_raw_close(self):
        list_stock_code = list()
        if self.latest:
            # get lastest stock pool
            stock_pool_update()

        if self.from_internet:
            source = self.internet_source
        else:
            source = self.db_source

        stock_codes = self.db_source.get_stock_pool().get("stock_set")

        raw_data = source.get_batch_stock_close(stock_codes)
        return raw_data

    def compute_stock_pool_macd(self):
        rule = "macd"
        self._compute(raw_data, rule)

    def computer_stock_pool_ma(self):
        rule = "ma"
        self._compute(raw_data, rule)

    def _compute(self, raw_data, rule_type="macd"):

        if rule_type == "macd":
            f = self._compute_macd_func
        elif rule_type == "ma":
            f = self._compute_ma_func
        else:
            print("error rule:", rule)
            return

        raw_data = self._get_raw_close()

        start_time = time.time()
        for code, data in raw_data:
            self.pool.apply_async(func=self._compute_func, args=(code, data,))

        self.pool.close()
        self.pool.join()

        print("compiter {0} end, time cost: {1:.2f}s \n{2}".format(rule_type,
            time.time() - start_time, "=" * 35))
        


class BackTestRuleMacd:
    """
        对按照macd计算得来的买卖点进行回测
        每只股票的初始资金为10000，对比按买卖点交易之后，是否盈利
    """

    def __init__(self):
        self.stock_set = None
        self.db_source = StockDataSourceDB()

        # self.pool = Pool(cpu_count()-1)

        self._get_pool_stock()
        self.base_initial_cap = 10000
        self.initial_capital = self.base_initial_cap*self.stock_count
        self.back_result = []
        self.f = back_test_one_stock
        self.init_data_set = None

    def _get_pool_stock(self):
        """
            获取当前股票池的所有股票代码
            如果股票非最新，更新股票池
        """
        stock_pool = self.db_source.get_stock_pool()
        if not stock_pool:
            stock_pool = stock_pool_update()

        self.stock_set = stock_pool.get("stock_set")
        self.stock_count = stock_pool.get("pool_size", 0)

    def _prepare_macd(self):
        macd_result = self.db_source.get_macd_rule_stock(self.stock_set)

        init_data_set = ((macd.get("stock_code"), macd.get(
            "macd_set"), macd.get("size"), self.base_initial_cap) for macd in macd_result)
        self.init_data_set = init_data_set

    def start_back_test(self):

        self._prepare_macd()
        task_id = 0
        for code, macd_set, size ,base_cap in self.init_data_set:
            # self.pool.apply_async(func=self.f, args=(
            #     code, macd_set, base_cap,))
            task_id+=1
            self.f(task_id, code, macd_set, size, base_cap)
        # self.pool.close()
        # self.pool.join()

        print("finally money:", sum(self.back_result))

def back_test_one_stock(task_id, stock_code, macd_chance, size, initial_capital=10000):

    start_initial_cap = initial_capital
    buy_num, first_up = 0, False, 

    for i in range(size):
        chance = macd_chance[i][-1]
        if chance > 0:
            price = macd_chance[i][1]
            buy_num = initial_capital // price
            initial_capital -= (buy_num * price)
            first_up = True
            # print("买入时间：{}, 钱包：{}, 仓库：{}".format(macd_chance[i][0], int(initial_capital), buy_num * price))
        elif chance < 0 and first_up:
            # first_down = True
            price = macd_chance[i][1]
            buy_out = price * buy_num
            initial_capital += buy_out
            buy_num = 0
            # print("买出时间：{}, 钱包：{}, 仓库：{}".format(macd_chance[i][0], int(initial_capital), buy_num * price))
    cur_price = macd_chance[-1][1]
    open_funds = initial_capital + buy_num * cur_price
   

    if open_funds > start_initial_cap:
        print("盈利",end=" ")
    else:
        print("亏本了",end=" ")

    print("stock code {0} finally money: {1}".format(stock_code, open_funds))