import json
import pandas as pd
import requests
from sail.util.log import logger


class Spider:
    def __init__(self, type="all"):
        self.url = ""
        self.share = ""
        self.type = type if not type else "one"

    def _get(self):
        r = requests.get(self.url)
        if r.status_code != 200:
            logger.info("get {0} stock error,status code:{1}".format(self.share, r.status_code))
            return None
        return r.text

    def get_stock_list(self, url, share=""):
        self.url = url
        self.share = share
        retry, res_text = 3, []
        while retry and not res_text:
            res_text = self._get()
            retry -= 1
        if not res_text:
            return []

        if self.type == "all":
            # crawl all stock list
            parsed_result = self._parse_short_data(res_text)
        else:
            # crawl one stock history data
            parsed_result = self._parse_long_data(res_text)
        return parsed_result

    def _parse_long_data(self, res_text):
        """
            parse one stock history data
            return : List[List]
        """
        if len(res_text) < 2:
            logger.error("res_text len < 2")
            return
        try:
            raw_data = json.loads(res_text[1:-1])['data']
        except json.decoder.JSONDecodeError:
            logger.info(res_text)
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

        return stock_list

    def _parse_short_data(self, res_text):
        """
            parse stock list history data
            return : List[List]
        """
        decode_data = json.loads(res_text)
        stock_list = decode_data.get("data", "").get("diff", [])
        logger.info("get total {} stock".format(decode_data.get("data", "").get("total", 0)))
        return stock_list


if __name__ == "__main__":
    s = Spider()
    StockHisDataURL = "http://pdfm.eastmoney.com/EM_UBG_PDTI_Fast/api/js?token=4f1862fc3b5e77c150a2b985b12db0fd&rtntype=6&id=0000012&type=k"
    r = s.get_stock_list(StockHisDataURL, "")
    print(r)
    df = pd.DataFrame(r)
    print(df)

    # sd = StockDataSource()
    # r1 = sd.get_sh_stock_data()
    # r2 = sd.get_sz_stock_data()
    # r3 = sd.get_kcb_stock_data()
    # print(r1)
    # print(r2)
    # print(r3)
    # r4 = sd.get_all_stock_data()
    # print(len(r4))
