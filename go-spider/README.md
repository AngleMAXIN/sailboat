# Golang 爬虫 

- 爬取沪深A股的股票信息,例如

    ```json
    "stockname" : "北巴传媒",
    "stockid" : "600386",
    "stockcode" : "sh600386",
    "historydata" : [
        {
            "open" : 6.9,
            "close" : 6.75,
            "volume" : 72552.05,
            "ma5" : 6.75,
            "ma10" : 6.75,
            "ma20" : 6.75,
            "date" : "2017-09-25"
        },
        {
            "open" : 6.73,
            "close" : 6.73,
            "volume" : 47736.84,
            "ma5" : 6.74,
            "ma10" : 6.74,
            "ma20" : 6.74,
            "date" : "2017-09-26"
        }
    ]
    ```

- 爬取的数据存储MongoDB
