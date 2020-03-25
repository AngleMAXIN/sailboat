import time
from datetime import date
from multiprocessing import Pool, cpu_count
import gevent
import numpy as np
import pandas as pd

from celery_task.tasks import insert_date_async
from sail.db import db
from sail.util import get_macd
from sail.water import StockHistoryDataNet
from celery_task.tasks import stock_pool_update


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
    # df = df.drop(df[df.chance == 0].index)
    return df


def select_time_by_macd(code, his_data):
    # df DateFrame
    df = pd.DataFrame(his_data)
    df.close = df.close.astype(np.float)
    _, _, _macd = get_macd(df.close.values)

    df.insert(2, "macd", _macd)
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

    insert_date_async.delay(document)


def run_pro():
    start_time = time.time()

    # stock_pool_update()
    # 获取当前股票池中的股票，[stock_code...]
    stock_pool = db.find_stock_pool()
    # 通过爬虫获取获取股票的历史数据
    if not stock_pool:
        print("stock is null")
        return
    source_data = StockHistoryDataNet(stock_pool.get("stock_set")).get_tuple()

    crawl_end = time.time()
    print("{0}\n crawl data total: {1} end, time cost: {2:.2f}s \n{3}\n".format("=" * 35, stock_pool.get("pool_size"),
                                                                                crawl_end - start_time, "=" * 35))

    pool_size = cpu_count()
    pool = Pool(pool_size)
    for code, data in source_data:
        pool.apply_async(func=select_time_by_macd, args=(code, data,))

    pool.close()
    pool.join()
    print("compiter macd end, time cost: {0:.2f}s \n{1}".format(
        time.time() - crawl_end, "=" * 35))


class BackTestRuleMacd:
    """
        对按照macd计算得来的买卖点进行回测
        每只股票的初始资金为10000，对比按买卖点交易之后，是否盈利
    """

    def __init__(self):
        self.stock_set = None
        self.source = db

        self._get_pool_stock()
        self.base_initial_cap = 10000
        self.initial_capital = self.base_initial_cap*self.stock_count
        self.back_result = []

    def _get_pool_stock(self):
        """
            获取当前股票池的所有股票代码
            如果股票非最新，更新股票池
        """
        stock_set = self.source.find_stock_pool()
        if not stock_set:
            stock_set = stock_pool_update()

        self.stock_set = stock_set.get("stock_set")
        self.stock_count = stock_set.get("pool_size")

    def start_back_test(self):
        f = self.back_test_one_stock
        # print("---")
        # async_task = [gevent.spawn(f, stock_code, self.base_initial_cap)
        #               for stock_code in self.stock_set]
        # gevent.joinall(async_task)
        for stock_code in self.stock_set:
            f(stock_code,self.base_initial_cap)

        print("finally money:", sum(self.back_result))

    def back_test_one_stock(self, stock_code, initial_capital=10000):
        macd_rule_set = self.source.find_macd_rule_stock(stock_code)
        macd_chance = macd_rule_set.get("macd_set")
        start_initial_cap = initial_capital
        buy_num, first_up, size = 0, False, macd_rule_set.get("size")
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
                # print("买出时间：{}, 钱包：{}, 仓库：{}".format(macd_chance[i][0], int(initial_capital), buy_num * price))
        cur_price = macd_chance[-1][1]
        open_funds = initial_capital + buy_num * cur_price

        print("stock code {0} finally money: {1}",
              stock_code, open_funds, end=" ")
        # is_up = False
        if open_funds > start_initial_cap:
            is_up = True
            print("盈利")
        else:
            print("亏本了")
        self.back_result.append(open_funds)
        # return open_funds, is_up
