from sail.heat.rule.rule import BackTestRuleMacd
# from celery_task.tasks import stock_pool_update

# stock_pool_update()
bm = BackTestRuleMacd()
bm.start_back_test()
# back_test()
# from sail.db import db 
# from celery_task.tasks import stock_pool_update

# stock_pool_update()
# stock_pool_code_list = db.find_stock_pool()
# print(stock_pool_code_list)
# mr = MacdRule(stock_pool_code_list[10:])
# mr.run()
