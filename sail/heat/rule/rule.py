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
from sail.plt import pie_back_test_result, plot_profit
from .chance import select_time_by_kdj, select_time_by_ma, select_time_by_macd

__all__ = ['Rule', 'BackTestRule']


class Rule:
    """
    指标计算 例如MACD,MA,KDJ等
    """

    def __init__(self, latest=False, from_internet=False,limit=0):
        # 股票来源 股票池，所有股票
        self.latest = latest
        self.from_internet = from_internet

        self.db_source = StockDataSourceDB()

        self.pool = Pool(cpu_count())
        self.f_list = []
        self._compute_macd_func = select_time_by_macd
        self._compute_ma_func = select_time_by_ma
        self._compute_kdj_func = select_time_by_kdj

        self._get_raw_close(limit)

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
            "stock_set"), macd.get("size"), self.base_initial_cap) for macd in result)
        self.init_data_set = init_data_set

    def clean(self, stock_dict):
        after = {code:values for code, values in stock_dict.items() if len(stock_dict[code]) > 1}
        return after

    def _save_result(self):
        self.up_stock_set = self.clean(self.up_stock_set)
        self.down_stock_set = self.clean(self.down_stock_set)
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
        pie_back_test_result(len(self.up_stock_set), len(self.down_stock_set))

    def _run(self):
        i = 0
        for code, _set, _, base_cap in self.init_data_set:
            self.back_test_one_stock(i,code, _set, base_cap)
            i += 1

    def back_test_one_stock(self, i, stock_code, test_case_set, initial_capital=10000):
        start_initial_cap = initial_capital
        # print("=============\n",start_initial_cap,"\n=================")
        buy_num, first_up = 0, False,
        change_tiems, balance_change = [], []
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
            change_tiems.append(test_case_set[i][0])
            balance_change.append((initial_capital + buy_num * price))

            if self.debug:
                print("买出时间:{}, 价格: {}，余额: {:.2f}".format(
                    test_case_set[i][0], price, initial_capital))

        profitabilty = ((balance_change[-1]-start_initial_cap) /
                        start_initial_cap) * 100
        result = {
            "rule": self._curr_rule,
            "stock_code": stock_code,
            "date": change_tiems,
            "balance_change": balance_change,
            "start_initial_cap": start_initial_cap,
            "balance": balance_change[-1],
            "profitability": int(profitabilty),
        }
        _type = ""
        if profitabilty > 0:
            _type = "up"
            self.up_stock_set[stock_code].append(result)
        else:
            _type = "down"
            self.down_stock_set[stock_code].append(result)
        # if i < 20:
        plot_profit(_type, stock_code, change_tiems, balance_change)
        print("stock code: {0}; finally balance: {1:.2f}; \tprofitability: {2:.2f}".format(
            stock_code, balance_change[-1], profitabilty))
