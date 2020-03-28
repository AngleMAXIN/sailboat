import json

import grequests
import pandas as pd

from sail.util.log import logger


class Spider:
    def __init__(self, _type="all"):
        self.url = ""
        self.share = ""
        self.sync_size = 4
        self._type = _type if _type else "one"

    def _get(self):
        import requests
        r = requests.get(self.url)
        if r.status_code != 200:
            logger.info("get {0} stock error,status code:{1}".format(
                self.share, r.status_code))
            return ""
        return r.text

    def _get_by_sync(self, url, share):
        self.url = url
        self.share = share
        retry, res_text = 3, []
        while retry and not res_text:
            res_text = self._get()
            retry -= 1
        return res_text

    def get_stock_list(self, url_args, share=""):
        str_type = isinstance(url_args, str)
        res_text = ""
        if str_type:
            res_text = self._get_by_sync(url_args, share)

        list_type = isinstance(url_args, list)
        if list_type:
            res_text = self._get_by_async(url_args)

        if self._type == "all":
            # crawl all stock list
            parsed_result = self._parse_short_data(res_text)
        else:
            # crawl list stock history data
            # if list_type:
            parsed_result = (self._parse_long_data(text)
                             for text in res_text)
        return parsed_result

    

    def _get_by_async(self, urls):
        """
            异步爬取数据
        """

        def _exception_handler(self, r, exception):
            print(r, exception)

        rs = (grequests.get(url) for url in urls)
        result = (res.text for res in grequests.map(
            rs, size=self.sync_size, exception_handler=_exception_handler))
        return result

    def _parse_long_data(self, res_text):
        """
            parse one stock history data
            return : List[List]
        """
        if len(res_text) < 2:
            logger.error("res_text len < 2")
            return
        try:
            raw = json.loads(res_text[1:-1])
            raw_data = raw.get('data')
            code = raw.get("code")
        except json.decoder.JSONDecodeError as e:
            logger.error(e)
            return []

        stock_list = []
        for raw in raw_data:
            raw_line = raw.split(",")
            if len(raw_line) > 2:
                stock_list.append(
                    {
                        "date": raw_line[0],
                        "close": raw_line[2],
                    }
                )

        return code, tuple(stock_list)

    def _parse_short_data(self, res_text=""):
        """
            parse stock list history data
            return : List[List]
        """
        decode_data = json.loads(res_text)
        stock_list = decode_data.get("data", "").get("diff", [])
        logger.info("get total {} stock".format(
            decode_data.get("data", "").get("total", 0)))
        return stock_list


if __name__ == "__main__":
    s = Spider()
    StockHisDataURL = "http://pdfm.eastmoney.com/EM_UBG_PDTI_Fast/api/js?token=4f1862fc3b5e77c150a2b985b12db0fd&rtntype=6&id=0000012&type=k"
    r = s.get_stock_list(StockHisDataURL, "")
    # print(r)
    df = pd.DataFrame(r)
    # print(df)

    # sd = StockDataSource()
    # r1 = sd.get_sh_stock_data()
    # r2 = sd.get_sz_stock_data()
    # r3 = sd.get_kcb_stock_data()
    # print(r1)
    # print(r2)
    # print(r3)
    # r4 = sd.get_all_stock_data()
    # print(len(r4))
