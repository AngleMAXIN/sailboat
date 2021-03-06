from datetime import date

from sail.constant import DB_COLL_POOL
from sail.db import db
from sail.heat.pool import StockPool

from .celery import app


@app.task
def stock_pool_update():
    sp = StockPool(is_storage=True)

    # set pe rule for get stock pool
    sp.set_pe_rules(top=14.0, level=0.0)
    # get stock pool
    sp.get_pool()

    values, names, size = sp.to_stock_code_list()
    document = {
        "date": date.today().isoformat(),
        "stock_set": values,
        "stock_name": names,
        "pool_size": size,
        "rule": "pe"
    }

    # insert stock code list in mongodb
    db.insert_stock_pool(document, DB_COLL_POOL)
    print("===== get {} stock in pool =====".format(size))
    return document

@app.task
def insert_chance_by_macd_async(doc):
    db.insert_stock_macd(doc)

@app.task
def insert_stock_history_async(doc):
    db.insert_stock_history(doc)

@app.task
def insert_chance_by_ma_async(doc):
    db.insert_stock_ma(doc)

@app.task
def insert_chance_by_kdj_async(doc):
    db.insert_stock_kdj(doc)

@app.task
def insert_back_test_result_async(doc):
    db.insert_back_test_result(doc)

if __name__ == "__main__":
    stock_pool_update()
