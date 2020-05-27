import matplotlib as pplt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import random
import datetime
pplt.use('TkAgg')


def pie_back_test_result(profit_num, loss_num):
    labels = 'Profit', 'Loss'
    sizes = (profit_num, loss_num,)
    explode = (0, 0.1,)  # only "explode" the 2nd slice (i.e. 'Hogs')
    plt = pplt.pyplot

    _, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    plt.title("Stock Back Test Result")
    ax1.axis('equal')
    


def plot_profit(_type, stock_code, date, profit_list):
    plt = pplt.pyplot

    data = {
        "date": date,
        "balancd": profit_list,
    }
    plt.figure(figsize=(20, 10)) 
    ax = plt.subplot(1, 1, 1)
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df.set_index(['date'], inplace=True)
    title = "{} StockCode {}".format(_type, stock_code)
    df['balancd'].plot(title=title, ax=ax)
    plt.savefig("/home/maxin/self/sailboat/sail/image/{}.png".format(title))
    plt.close()
    


if __name__ == "__main__":
    # pro_num,loss_num = 90,456
    # pie_back_test_result(pro_num, loss_num)
    num = 17
    pro_list = [random.uniform(i, i+100) * i for i in range(num)]
    date = pd.date_range('2014-09-01', '2014-09-17')
    print(date)
    plot_profit("up", "0000001", date, pro_list)
