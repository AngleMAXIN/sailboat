import time
from datetime import date
from multiprocessing import Pool, cpu_count

import pandas as pd

from celery_task.tasks import (insert_chance_by_ma_async,
                               insert_chance_by_macd_async, stock_pool_update)
from sail.util import get_ma, get_macd
from sail.water import StockDataSourceDB
from .chance import select_time_by_ma, select_time_by_macd

__all__ = ['Rule', 'BackTestRuleMacd']


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

    def _get_raw_close(self, limit=0):
        if self.latest:
            # get lastest stock pool
            stock_pool_update()

        source = self.db_source
        stock_codes = source.get_stock_pool().get("stock_set")
        if limit > 0:
            stock_codes = stock_codes[:limit]
        raw_data = source.get_batch_stock_close(stock_codes)
        return raw_data

    def compute_stock_pool_macd(self):
        rule = "macd"
        self._compute(self._get_raw_close(), rule)

    def compute_stock_pool_ma(self):
        rule = "ma"
        self._compute(self._get_raw_close(), rule)

    def _compute(self, raw_data, rule_type="macd"):

        if rule_type == "macd":
            f = self._compute_macd_func
        elif rule_type == "ma":
            f = self._compute_ma_func
        else:
            print("error rule:", rule_type)
            return

        # print(raw_data)
        start_time = time.time()
        for code, data in raw_data:
            self.pool.apply_async(func=f, args=(code, data,))
        self.pool.close()
        self.pool.join()

        print("compiter {0} end, time cost: {1:.2f}s \n{2}".format(rule_type,
                                                                   time.time() - start_time, "=" * 35))


class BackTestRuleMacd:
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

        self.up_stock_set = []

        self.down_stock_set = []

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

        self.down_stock_set = []
        self.up_stock_set = []

        init_data_set = ((macd.get("stock_code"), macd.get(
            "macd_set"), macd.get("size"), self.base_initial_cap) for macd in result)
        self.init_data_set = init_data_set

    def _save_result(self, _type):
        up_stock_number = len(self.up_stock_set)
        down_stock_number = len(self.down_stock_set)
        test_result = {
            "date": date.today().isoformat(),
            "rule_by": _type,
            "up_stock_set": {"stock_set": self.up_stock_set, "total": up_stock_number},
            "down_stock_set": {"stock_set": self.down_stock_set, "total": down_stock_number},
            "total": up_stock_number+down_stock_number,
        }
        pass

    def back_test_ma(self):
        _type = "ma"
        self._prepare_test_cases(_type)
        self._back_test()
        print("盈利股票: {}只， 亏损股票: {}只".format(
            len(self.up_stock_set), len(self.down_stock_set)))

    def back_test_macd(self):
        _type = "macd"
        self._prepare_test_cases(_type)
        self._back_test()
        print("盈利股票: {}只， 亏损股票: {}只".format(
            len(self.up_stock_set), len(self.down_stock_set)))

    def _back_test(self):
        for code, macd_set, _, base_cap in self.init_data_set:
            self.back_test_one_stock(code, macd_set, base_cap)

    def back_test_one_stock(self, stock_code, test_case_set, initial_capital=10000):
        start_initial_cap = initial_capital
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
                print("买出时间:{}, 价格: {}， 余额: {:.2f}".format(
                    test_case_set[i][0], price, initial_capital))

        cur_price = test_case_set[-1][1]
        open_funds = initial_capital + buy_num * cur_price

        profitababilty = ((open_funds-start_initial_cap) /
                          start_initial_cap) * 100
        result = {
            "stock_code": stock_code,
            "balance:": open_funds,
            "tprofitability": profitababilty,
        }
        if profitababilty > 0:
            self.up_stock_set.append(result)
            print("盈利", end=" ")
        else:
            self.down_stock_set.append(result)
            print("亏损", end=" ")

        print("stock code: {0},finally balance: {1:.2f},\tprofitability: {2:.2f}".format(
            stock_code, open_funds, profitababilty))
