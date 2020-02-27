import pandas as pd
import  numpy as np
from sail.util import get_macd
from sail.water import StockHistoryDataNet


def macd_rule():
    stock_codes = ["000001", "000002"]
    source = StockHistoryDataNet(stock_codes)
    source_data = source.get_all_history(stock_codes[0])
    df = pd.DataFrame(data=source_data)
    df.close = df.close.astype(np.float)
    DIF, DEA, _MACD = get_macd(df.close.values)

    value_dict = {
        "MACD": _MACD,
        "DIF": DIF,
        "DEA": DEA,
    }

    df = pd.DataFrame(value_dict, index=df.date)
    df = df.dropna(axis=0, how="all")

    df.eval('cross=DIF-DEA', inplace=True)
    df.to_csv("/home/maxin/result.csv")


if __name__ == '__main__':
    macd_rule()
