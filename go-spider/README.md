# Golang 爬虫

- 爬取沪深A股的股票信息,例如

    ```json
    "stockname" : "振华股份",
    "stockid" : "603067",
    "stockcode" : "6030671",
    "historydata" : [
        {
            "date" : "2016-09-13",
            "close" : 8.83,
            "high" : 8.83,
            "low" : 8.83
        },
        {
            "date" : "2016-09-14",
            "close" : 9.71,
            "high" : 9.71,
            "low" : 9.71
        },
    ]
    ```

- 爬取的数据存储MongoDB
