from sail.heat.rule.rule import MacdRule
from celery_task.tasks import stock_pool_update

stock_codes = ['000001']
mr = MacdRule(stock_codes)
mr.run()
