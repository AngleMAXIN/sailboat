package core

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"sailboat/config"
)

var (
	header = map[string]string{
		"User-Agent":                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
		"Upgrade-Insecure-Requests": "1",
		"Referer":                   "http://q.10jqka.com.cn/",
		"Content-Type":              "test/html",
		"Host":                      "q.10jqka.com.cn",
		"X-Requested-With":          "XMLHttpRequest",
		"Cookie":                    "spversion=20130314; historystock=1A0001%7C*%7C601318; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1577956133,1578385411; Hm_lpvt_78c58f01938e4d85eaf619eae71b4ed1=1578385411; v=At0J-6B9X2jHbjtEVwdUabo05bLT-h2yGyh1eZ-iGzJji_MkZ0ohHKt-h_Us",
	}
)

type stockInfo struct {
	// Code string
	Record [][]string
}

// Spider 爬虫
type Spider struct {
	baseURL string
	params  map[string]string
	headers map[string]string
}

// StockList 股票列表
type resStockList struct {
	Data resStock `json:"data"`
}

type resStock struct {
	Total int            `json:"total"`
	Diff  []resStockName `json:"diff"`
}

// StockName 股票名称，代码
type resStockName struct {
	StockName string `json:"f14"`
	StockID   string `json:"f12"`
	StockCode string
}

// buildURL 构造完整的url
// func buildURL(baseURL string, params map[string]string) string {
// 	u, err := url.Parse(baseURL)
// 	if err != nil {
// 		log.Printf("parse url erorr:%s", err)
// 	}
// 	q := u.Query()
// 	for key, values := range params {
// 		q.Add(key, values)
// 	}
// 	u.RawQuery = q.Encode()
// 	return u.String()

// }

// requestHeaders 请求头
func requestHeaders() map[string]string {
	return nil
}

// doRequest 发起请求
func doRequest(url string) ([]byte, error) {
	client := &http.Client{}
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		log.Println("new get request error:", err)
		return nil, err
	}

	if headers := requestHeaders(); headers != nil {
		for key, value := range headers {
			req.Header.Add(key, value)
		}
	}

	resp, err := client.Do(req)
	if err != nil {
		log.Println("request error:", err)
		return nil, err
	}

	defer resp.Body.Close()
	if resp.StatusCode != 200 {
		log.Println("status code is:", resp.StatusCode)
	}
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Println("read all body error:", err)
		return nil, err

	}
	return body, nil

}

// func parseResText(text string) {
// 	fmt.Println(text)
// 	dom, err := goquery.NewDocumentFromReader(strings.NewReader(text))
// 	if err != nil {
// 		log.Fatal("parse text error:", err)
// 	}
// 	dom.Find("td>a").Each(func(i int, selection *goquery.Selection) {
// 		if selection.Text() != "" {
// 			fmt.Println(selection.Text())
// 		}
// 	})
// }

// parseResToStruct 解析返回的数据，格式化数据
func parseResData1(res []byte) *stockInfo {
	oneStock := &stockInfo{}
	err := json.Unmarshal(res, oneStock)
	if err != nil {
		log.Fatal("parse response data. error:", err)
	}

	stockSet := oneStock.Record
	fmt.Println("len:", len(stockSet))
	for i := 0; i < 1; i++ {
		for _, v := range stockSet[i] {
			fmt.Println(v)
		}
	}
	return oneStock
}

// parseResData 解析数据
func parseResData(content []byte) *resStockList {
	var res resStockList

	err := json.Unmarshal(content, &res)
	if err != nil {
		log.Println("parse response error: ", err)
	}

	fmt.Println("len:", len(res.Data.Diff))
	stockList := res.Data.Diff
	for i := 0; i < len(stockList); i++ {
		fmt.Println(stockList[i])
	}
	return nil
}

// crawlShStockList 爬取上证A股股票
func crawlStockList(urlFomart string) {
	baseURL := fmt.Sprintf(urlFomart, config.StockNumLimit)
	res, err := doRequest(baseURL)
	if err != nil {
		log.Printf("url: %s, error: %s", baseURL, err)
	}
	parseResData(res)

}

func crawlOneStockInfo(stockCode string) {
	url := fmt.Sprintf(config.StockInfoURL, stockCode)
	response, err := doRequest(url)
	if err != nil {
		log.Printf("crawlOneStockInfo error: %s, url: %s", err, url)
	}
	parseResData(response)
}

// RunSpider 运行爬虫的入口
func RunSpider() {
	switch {
	case config.IsShA:
		crawlStockList(config.ShStockListURL)
		fallthrough
	case config.IsSzA:
		crawlStockList(config.SzStockListURL)
		fallthrough
	case config.IsKcb:
		crawlStockList(config.KcbStockListURL)
	}

}
