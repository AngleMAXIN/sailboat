import time
from collections import Counter
from datetime import date
from multiprocessing import Pool, cpu_count

import pandas as pd

from celery_task.tasks import (insert_back_test_result_async,
                               insert_chance_by_ma_async,
                               insert_chance_by_macd_async,
                               stock_pool_update)
from sail.water import StockDataSourceDB

from .chance import select_time_by_kdj, select_time_by_ma, select_time_by_macd

__all__ = ['Rule', 'BackTestRule']


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
        self.f_list = []
        self._compute_macd_func = select_time_by_macd
        self._compute_ma_func = select_time_by_ma
        self._compute_kdj_func = select_time_by_kdj

        self._get_raw_close()

    def _get_raw_close(self, limit=0):
        if self.latest:
            # get lastest stock pool
            stock_pool_update()

        source = self.db_source
        stock_codes = source.get_stock_pool().get("stock_set")
        if limit > 0:
            stock_codes = stock_codes[:limit]
        self.raw_data = source.get_batch_stock_close(stock_codes)

    def run(self):
        self._compute()

    def compute_stock_pool_macd(self):
        self.f_list.append(self._compute_macd_func)

    def compute_stock_pool_ma(self):
        self.f_list.append(self._compute_ma_func)

    def compute_stock_pool_kdj(self):
        self.f_list.append(self._compute_kdj_func)

    def _compute(self):
        if len(self.f_list) < 1:
            print("no func is run")
            return

        start_time = time.time()
        count = 0
        for code, data in self.raw_data:
            count += 1
            self.data = data
            for f in self.f_list:
                self.pool.apply_async(func=f, args=(code, data,))

        print("total count:{0}".format(count))
        self.pool.close()
        self.pool.join()

        print("compiter end, time cost: {0:.2f}s \n{1}".format(
            time.time() - start_time, "=" * 35))

    def get_df(self):
        return self.data


class BackTestRule:
    """
        对按照macd计算得来的买卖点进行回测
        每只股票的初始资金为10000，对比按买卖点交易之后，是否盈利
    """

    def __init__(self, is_debug=False):
        self.debug = False

        self.stock_set = None
        self.db_source = StockDataSourceDB()

        # 预准备股票池
        self._prepare_pool_stock()

        # 初始单子股票测试本金
        self.base_initial_cap = 10000

        self.initial_capital = self.base_initial_cap * self.stock_count
        from collections import defaultdict

        self.up_stock_set = defaultdict(list)

        self.down_stock_set = defaultdict(list)

        self.init_data_set = None

        self.back_test_result = None

    def _prepare_pool_stock(self):
        """
            获取当前股票池的所有股票代码
            如果股票非最新，更新股票池
        """
        stock_pool = self.db_source.get_stock_pool()
        if not stock_pool:
            stock_pool = stock_pool_update()

        self.stock_set = stock_pool.get("stock_set")
        self.stock_count = stock_pool.get("pool_size", 0)

    def _prepare_test_cases(self, _type):
        if _type == "macd":
            result = self.db_source.get_macd_rule_stock(self.stock_set)
        elif _type == "ma":
            result = self.db_source.get_ma_rule_stock(self.stock_set)
        elif _type == "kdj":
            result = self.db_source.get_kdj_rule_stock(self.stock_set)

        init_data_set = ((macd.get("stock_code"), macd.get(
            "macd_set"), macd.get("size"), self.base_initial_cap) for macd in result)
        self.init_data_set = init_data_set

    def _save_result(self):

        test_result = {
            "date": date.today().isoformat(),
            "up_stock_set": {"stock_set": self.up_stock_set, "total": len(self.up_stock_set)},
            "down_stock_set": {"stock_set": self.down_stock_set, "total": len(self.down_stock_set)},
        }
        insert_back_test_result_async.delay(test_result)

    def back_test(self):

        _types = ("ma", "macd", "kdj",)
        for t in _types:
            print(
                "=================== start back test:{0} ================".format(t))
            self._curr_rule = t
            self._prepare_test_cases(t)
            self._run()
            print(
                "=================== {0} end ============================".format(t))
        self._save_result()

    def _run(self):
        for code, macd_set, _, base_cap in self.init_data_set:
            self.back_test_one_stock(code, macd_set, base_cap)

    def back_test_one_stock(self, stock_code, test_case_set, initial_capital=10000):
        start_initial_cap = initial_capital
        # print("=============\n",start_initial_cap,"\n=================")
        buy_num, first_up = 0, False,

        for i in range(len(test_case_set)):
            chance = test_case_set[i][-1]
            price = test_case_set[i][1]
            if chance > 0:
                buy_num = initial_capital // price
                initial_capital -= (buy_num * price)
                first_up = True
            elif chance < 0 and first_up:
                buy_out = price * buy_num
                initial_capital += buy_out

            if self.debug:
                print("买出时间:{}, 价格: {}，余额: {:.2f}".format(
                    test_case_set[i][0], price, initial_capital))

        cur_price = test_case_set[-1][1]
        balance = initial_capital + buy_num * cur_price

        profitabilty = ((balance-start_initial_cap) /
                        start_initial_cap) * 100
        result = {
            "rule": self._curr_rule,
            "stock_code": stock_code,
            "start_initial_cap": start_initial_cap,
            "balance": int(balance),
            "profitability": int(profitabilty),
        }
        if profitabilty > 0:
            self.up_stock_set[stock_code].append(result)
        else:
            self.down_stock_set[stock_code].append(result)

        print("stock code: {0}; finally balance: {1:.2f}; \tprofitability: {2:.2f}".format(
            stock_code, balance, profitabilty))
