import pandas as pd

from sail.util import get_macd
from sail.water import StockHistoryDataNet


def macd_rule():
    stock_codes = ["000001", "000002"]
    source = StockHistoryDataNet(stock_codes)
    source_data = source.get_all_history(stock_codes[0])
    df = pd.DataFrame(data=source_data)
    close = df.close.values
    DIF, DEA, _MACD = get_macd(close)

    value_dict = {
        "MACD": _MACD,
        "DIF": DIF,
        "DEA": DEA,
    }

    df = pd.DataFrame(value_dict, index=df.date)
    df = df.dropna(axis=0, how="all")

    df.eval('cross=DIF-DEA', inplace=True)
    df.to_csv("/home/maxin/result.csv")


