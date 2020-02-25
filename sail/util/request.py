import json
import requests
from sail.util.log import logger


class Spider:
    def __init__(self):
        self.url = ""
        self.share = ""

    def _get(self):
        r = requests.get(self.url)
        if r.status_code != 200:
            logger.info("get {0} stock error,status code:{1}".format(self.share, r.status_code))
            return None
        return r.text

    def get_stock_list(self, url, share):
        self.url = url
        self.share = share
        retry, res_text = 3, []
        while retry and not res_text:
            res_text = self._get()
            retry -= 1
        if not res_text:
            return []
        decode_data = json.loads(res_text)
        stock_list = decode_data.get("data", "").get("diff", [])
        logger.info("get total {} stock".format(decode_data.get("data", "").get("total", 0)))
        return stock_list




    # sd = StockDataSource()
    # r1 = sd.get_sh_stock_data()
    # r2 = sd.get_sz_stock_data()
    # r3 = sd.get_kcb_stock_data()
    # print(r1)
    # print(r2)
    # print(r3)
    # r4 = sd.get_all_stock_data()
    # print(len(r4))
