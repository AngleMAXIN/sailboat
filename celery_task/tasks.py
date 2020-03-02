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

    values, size = sp.to_stock_code_list()
    document = {
        "date": date.today().isoformat(),
        "stock_set": values,
        "pool_size": size,
        "rule": "pe"
    }

    # insert stock code list in mongodb
    db.insert_stock_pool(document, DB_COLL_POOL)
    print("=====insert data successful=====")
    return "ok"


if __name__ == "__main__":
    stock_pool_update()
