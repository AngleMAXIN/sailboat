import talib


def get_macd(close_v):
    diff, dea, macd = talib.MACDEXT(close_v, fastperiod=12, fastmatype=1, slowperiod=26, slowmatype=1,
                                    signalperiod=9, signalmatype=1)

    return diff, dea, macd * 2

def get_ma(close_v):
    ma5 = talib.MA(close_v, timeperiod=5, matype=0)
    ma10 = talib.MA(close_v, timeperiod=10, matype=0)
    ma20 = talib.MA(close_v, timeperiod=20, matype=0)
    return ma5, ma10, ma20

def get_kdj(close_v,high_v,low_v)
    kdj_k, kdj_d = ta.STOCH(high_v.values,
                        low_v.values,
                        close_v.values,
                        fastk_period=9,
                        slowk_period=3,
                        slowk_matype=0,
                        slowd_period=3,
                        slowd_matype=0)
    return kdj_k, kdj_d