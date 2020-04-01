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