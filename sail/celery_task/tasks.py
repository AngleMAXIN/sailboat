from sail.heat.pool import StockPool
from .celery import app

@app.task
def stock_pool_update():
    sp = StockPool(is_storage=True)
    sp.get_pool().to_lisy()
    # save monogo
    pass