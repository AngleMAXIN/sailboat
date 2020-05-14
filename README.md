# 毕设课题： 基于爬虫技术的股票量化交易系统

------

## 技术栈

    - Go            高性能的开发语言,支持语言级别的并发
    - Python        数据分析语言，例如 numpy,pandas，ta-lib等科学计算库
    - Celery        异步处理框架
    - MongoDB       数据库，nosql
    - Docker        容器服务
    - Nginx         前端静态文件代理

## 项目结构

    - api 为前端展示提供api数据服务
    - dist 前端工程目录
    - celery_task 异步以及定时任务，例如定时更新股票池，异步写数据库
    - go-spider 由golang编写的爬虫，目的是爬取沪深A股的所有股票的历史数据，并存入数据库
    - sail 数据分析模块 包含股票池的实现，股票指标，如macd，ma，kdj的计算实现以及股票回测

### 股票池选股条件

    - 市盈率（股票每股市价与每股盈利的比率） 0<=pe<14
    - 定时任务，【每天24点】更新股票池，并把结果分别保存到【CSV文件]和【数据库】中

### 买卖点策略

    - 根据macd计算出买卖点
        - 金叉 dif线 上穿 dea 线，称为金叉，此刻可以进行买入操作
        - 死叉 dif线 下穿 dea线，称为死叉，预示着，股票价格下降，此刻可以进行卖出操作

    - 根据ma计算买卖点
        - 当5日均线上穿20日均线，称为金叉，此刻可以进行买入操作
        - 当5日均线下穿20日均线，称为死叉，此刻可以进行卖出操作

    - 根据kdj计算买卖点
        - 当k线上穿d线，称为金叉，此刻可以进行买入操作
        - 当k线下穿d线，称为死叉，此刻可以进行卖出操作

### 回测

    分别计算出股票池中的股票在上面三种情况下的买卖点，然后进行回测，对回测结果进行统计归类，将结果存入数据库中

### 定时/异步任务

`
> celery -A celery_task worker -l info  // 异步任务
> celery -A celery_task beat -l info    // 定时任务
`
