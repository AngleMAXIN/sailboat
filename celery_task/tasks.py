import datetime
from sail.heat.pool import StockPool
from sail.constant import DB_COLL_POOL
from sail.db import db
from .celery import app


@app.task
def stock_pool_update():
    sp = StockPool(is_storage=True)

    # set pe rule for get stock pool
    sp.set_pe_rules(top=14.0, level=0.0)
    # get stock pool
    sp.get_pool()

    values, size = sp.to_stock_code_list()
    document = {
        datetime.date.today().isoformat(): values,
        "pool_size": size,
        "rule": "pe"
    }

    # insert stock code list in mongodb
    db.insert(document,DB_COLL_POOL)
    print("=====insert data successful=====")
    return "ok"
