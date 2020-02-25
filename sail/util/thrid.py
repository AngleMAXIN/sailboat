import talib
import pandas as pd
import tushare as ts

stock_code = "000001"
dw = ts.get_k_data(stock_code)
# dw = dw[-50:]  # 取最后50天的数据
close = dw.close.values


def get_macd(close_v):
    diff, dea, macd = talib.MACDEXT(close_v, fastperiod=12, fastmatype=1, slowperiod=26, slowmatype=1,
                                            signalperiod=9, signalmatype=1)

    return diff, dea, macd * 2


DIF, DEA, _MACD = get_macd(close)

value_dict = {
    "MACD": _MACD,
    "DIF": DIF,
    "DEA": DEA,
}
df = pd.DataFrame(value_dict, index=dw.date)
print(df.iloc[:36])

