import time
from sail.heat.rule import Rule, BackTestRule
from celery_task.tasks import stock_pool_update


if __name__ == "__main__":
    # is_update_stock =  input("is update stock pool(y/n):")
    # latest = False
    # if is_update_stock == "y":
    #     latest = True
    # rule = Rule(latest=latest)

    # is_cmp_ma = input("is cmp ma(y/n):")
    # if is_cmp_ma == "y":
    #     rule.compute_stock_pool_ma()

    # is_cmp_macd = input("is cmp macd(y/n):")
    # if is_cmp_macd == "y":
    #     rule.compute_stock_pool_macd()

    # is_cmp_kdj = input("is cmp kdj(y/n):")
    # if is_cmp_kdj == "y":
    #     rule.compute_stock_pool_kdj()

    # rule.run()
    
    is_back_test = input("is back test(y/n):")
    if is_back_test == "y":
        print("-"*50)
        is_debug = 0
        back_test = BackTestRule(is_debug)
        back_test.back_test()
