import time
from sail.heat.rule import Rule, BackTestRuleMacd
from sail.water.data import StockDataSourceInternet, StockDataSourceNet
from celery_task.tasks import stock_pool_update, insert_stock_history_async


# latest =  False
# rule = Rule(latest=latest)
# rule.compute_stock_pool_ma()
print("-"*50)
is_debug = 0
back_test = BackTestRuleMacd(is_debug)
back_test.back_test_ma()
