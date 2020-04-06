import time

from celery_task.tasks import insert_stock_history_async, stock_pool_update
from sail.heat.rule import Rule
from sail.water.data import StockDataSourceInternet, StockDataSourceNet

all_stock_source = StockDataSourceNet()
code_list = all_stock_source.get_stock_codes()
s = StockDataSourceInternet()


def process(code_list):
    stock_set = s.get_batch_stock_close(code_list)
    for _set in stock_set:
        insert_stock_history_async.delay(_set)


length, step, start, end = len(code_list), 40, 0, 0
print("get total stock count:", length)
while end < length:
    end = start + step
    if end >= length:
        end = length
    codes = code_list[start: end]
    process(codes)
    print("process total stock start {0} - {1}".format(start, end))
    time.sleep(2)
    start = end
