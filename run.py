from sail.heat.rule import BackTestRuleMacd, Rule
# from celery_task.tasks import stock_pool_update

# stock_pool_update()

latest = False
macd = Rule(latest=latest)
macd.compute_stock_pool_macd()
# print("-"*50)
# bm = BackTestRuleMacd()
# bm.start_back_test()
# back_test()
# from sail.db import db 
# from celery_task.tasks import stock_pool_update

# stock_pool_update()
# stock_pool_code_list = db.find_stock_pool()
# print(stock_pool_code_list)
# mr = MacdRule(stock_pool_code_list[10:])
# mr.run()
