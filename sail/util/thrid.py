import pandas as pd
import talib
import tushare as ts


def get_macd(close_v):
    diff, dea, macd = talib.MACDEXT(close_v, fastperiod=12, fastmatype=1, slowperiod=26, slowmatype=1,
                                    signalperiod=9, signalmatype=1)

    return diff, dea, macd * 2