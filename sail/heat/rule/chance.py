# import time
from datetime import date

import pandas as pd

from celery_task.tasks import (insert_chance_by_ma_async,
                               insert_chance_by_macd_async, stock_pool_update)
from sail.util import get_ma, get_macd


def set_trading_time_macd(df):
    df['chance'] = 0
    for i in range(1, df.shape[0]):
        raw = df.iloc[i]
        pre_raw = df.iloc[i - 1]
        if raw.macd < 0 and pre_raw.macd > 0:
            df.loc[i, 'chance'] = -1
        elif raw.macd > 0 and pre_raw.macd < 0:
            df.loc[i, 'chance'] = 1

    #  删除没有买卖点的列，节省存储空间,优化计算效率
    df = df.drop(df[df.chance == 0].index)
    return df


def select_time_by_macd(code, df):
    if df is None:
        print("df is None code:", code)
        return
    _, _, _macd = get_macd(df.close.values)

    df.insert(1, "macd", _macd)
    df.dropna(axis=0, how="any", inplace=True)
    df.reset_index(drop=False, inplace=True)

    # set time of business, 1 buy, -1 sell
    df_time = set_trading_time_macd(df)

    document = {
        "date": date.today().isoformat(),
        "stock_code": code,
        "size": int(df_time.shape[0]),
        "macd_set": df_time.values.tolist(),
    }

    insert_chance_by_macd_async.delay(document)


def set_trading_time_ma(df):
    s2 = df["ma5"] > df["ma20"]
    s1 = df["ma5"] < df["ma20"]

    gold = df.loc[~(s1 | s2.shift(1))].index
    death = df.loc[(s1 & s2.shift(1))].index
    g1 = pd.Series(1, index=gold)  # 金叉标志位 1
    d1 = pd.Series(-1, index=death)  # 死叉标志位 -1
    gb = g1.append(d1).sort_index()
    gb.name = "chance"

    df = pd.concat([df, gb], axis=1)
    df.dropna(axis=0, how="any", inplace=True)
    return df


def select_time_by_ma(code, df):
    ma5, ma10, ma20 = get_ma(df.close.values)
    df["ma5"] = ma5
    df["ma10"] = ma10
    df["ma20"] = ma20

    df.dropna(axis=0, how="any", inplace=True)
    df.reset_index(drop=False, inplace=True)

    df_time = set_trading_time_ma(df)

    document = {
        "date": date.today().isoformat(),
        "stock_code": code,
        "size": int(df_time.shape[0]),
        "macd_set": df_time.values.tolist(),
    }

    insert_chance_by_ma_async.delay(document)

def select_time_by_kdj(code, df):
    df['kdj_k'], df['kdj_d'] = ta.STOCH(df['high'].values,
                        df['low'].values,
                        fd['close'].values,
                        fastk_period=9,
                        slowk_period=3,
                        slowk_matype=0,
                        slowd_period=3,
                        slowd_matype=0)
    a = 1
    b = 2
    df['kdj_j'] = 3*df['kdj_k']-2*df['kdj_d'];