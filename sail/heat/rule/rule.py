import time
from datetime import date
from multiprocessing import Pool, cpu_count

import numpy as np
import pandas as pd

from celery_task.tasks import insert_date_async
from sail.db import db
from sail.util import get_macd
from sail.water import StockHistoryDataNet


def set_trading_time(df):

    df['chance'] = 0
    for i in range(1, df.shape[0]):
        raw = df.iloc[i]
        pre_raw = df.iloc[i-1]
        if raw.macd < 0 and pre_raw.macd > 0:
            df.loc[i, 'chance'] = -1
        elif raw.macd > 0 and pre_raw.macd < 0:
            df.loc[i, 'chance'] = 1
    return df


def select_time_by_macd_process(code, his_data):
    # df DateFrame
    df = pd.DataFrame(his_data)
    df.close = df.close.astype(np.float)
    _, _, _macd = get_macd(df.close.values)

    df.insert(2, "macd", _macd)
    df.dropna(axis=0, how="any", inplace=True)
    df.reset_index(drop=True, inplace=True)
    # df.drop(['close'], axis=1, inplace=True)

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
    # from celery_task.tasks import stock_pool_update
    start_time = time.time()

    # stock_pool_update()
    # 获取当前股票池中的股票，[stock_code...]
    stock_pool_code_list = db.find_stock_pool()
    # 获取股票的历史数据
    source_data = StockHistoryDataNet(stock_pool_code_list).get_all_history()

    pool_size = cpu_count()
    pool = Pool(pool_size)
    for code, data in source_data.items():
        pool.apply_async(func=select_time_by_macd_process, args=(code, data,))

    pool.close()
    pool.join()
    print("============== process over, time cost: {:.2f}s =================".format(
        time.time()-start_time))


def back_test():
    stock_code = "601222"
    result = db.find_macd_rule_stock(stock_code)
    macd_chance = result.get("macd_set")

    initial_capital = 10000
    buy_num = 0
    first_up, first_down = False, False
    for i in range(result.get("size")):
        chance = macd_chance[i][-1]
        if chance > 0:
            price = macd_chance[i][1]
            buy_num = initial_capital//price
            initial_capital -= (buy_num * price)
            first_up = True
            print("买入时间：{}, 钱包：{}, 仓库：{}".format(macd_chance[i][0],int(initial_capital),buy_num *price))
        elif chance < 0 and first_up:
            # first_down = True
            price = macd_chance[i][1]
            buy_out = price * buy_num
            initial_capital +=  buy_out
            print("买出时间：{}, 钱包：{}, 仓库：{}".format(macd_chance[i][0],int(initial_capital),buy_num *price))
    cur_price = macd_chance[-1][1]
    print("finally money:", initial_capital+buy_num *cur_price)