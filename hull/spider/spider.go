package spider

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
	"net/http"
	"sailboat/config"
	"strconv"
	"time"
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

	stockCountMap = make(map[string]int)

	stockNum int

	stockShareNameChan = make(chan *stockShareName, 0)

	stockShareMap = map[string]string{
		"kcb": "sh",
		"sh":  "sh",
		"sz":  "sz",
	}

	// t = time.NewTicker(1000 * time.Millisecond)
)

type stockInfo struct {
	// Code string
	Record [][]string `json:"record"`
}

type stockShareName struct {
	share     string
	stockList []resStockName
}

/*
{
    "record": [
        [
            "2020-01-22", 日期 0
            "55.100", 开盘价   1
            "64.950", 最高价   2
            "53.360", 收盘价   3
            "53.010", 最低价
            "159637.84",  成交量
            "36.870", 价格变动
            "223.59", 涨跌
            "53.360", 5日均价 8
            "53.360", 10日均价 9
            "53.360", 20日均价  10
            "159,637.84", 5日均量
            "159,637.84", 5日均量
            "159,637.84" 5日均量
		],
	}

*/

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

type stockDetail struct {
	StockName   string
	StockID     string
	StockCode   string
	HistoryData []*oneDayStockInfo
}

type oneDayStockInfo struct {
	Open   float64
	Close  float64
	Volume float64 // 交易量
	Ma5    float64
	Ma10   float64
	Ma20   float64
	// TurnoverRate float64 // 换手率
	Date string
}

func init() {
	rand.Seed(time.Now().UnixNano())
}

// requestHeaders 请求头
func requestHeaders() map[string]string {
	return nil
}

// doRequest 发起请求
func doRequest(url string) ([]byte, error) {
	sleepTime := rand.Intn(3000)
	time.Sleep(time.Microsecond * time.Duration(sleepTime))

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
	var resp *http.Response
	var retry = 3
	for resp, err = client.Do(req); retry > 0; retry-- {
		if err != nil {
			log.Println("request error: ", err)
		} else {
			retry = 0
		}
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

// parseOneStockDateil 解析一只股票数据，格式化数据
func parseOneStockDateil(res []byte) []*oneDayStockInfo {
	oneStock := &stockInfo{}
	err := json.Unmarshal(res, oneStock)
	if err != nil {
		log.Printf("parse response data. error:%s, data:%s", err, res)
		return []*oneDayStockInfo{}
	}

	stockSet := oneStock.Record
	stockResultSet := make([]*oneDayStockInfo, 0, len(stockSet))
	for i := 0; i < len(stockSet); i++ {
		s := stockSet[i]
		stock := new(oneDayStockInfo)
		stock.Date = s[0]
		stock.Open, _ = strconv.ParseFloat(s[1], 64)
		stock.Close, _ = strconv.ParseFloat(s[3], 64)
		stock.Volume, _ = strconv.ParseFloat(s[5], 64)
		stock.Ma5, _ = strconv.ParseFloat(s[8], 64)
		stock.Ma10, _ = strconv.ParseFloat(s[9], 64)
		stock.Ma20, _ = strconv.ParseFloat(s[10], 64)

		stockResultSet = append(stockResultSet, stock)
	}
	return stockResultSet
}

// parseResData 解析数据
func parseStockListResData(content []byte, share string) []resStockName {
	var res resStockList
	if err := json.Unmarshal(content, &res); err != nil {
		log.Printf("parseStockListResData share: %s, error: %s\n", share, err)
	}

	log.Println("stock type: %s, total: %d\n", share, res.Data.Total)

	stockList := res.Data.Diff
	codePrefix := stockShareMap[share]
	for i := 0; i < res.Data.Total; i++ {
		stockList[i].StockCode = codePrefix + stockList[i].StockID
	}
	return stockList
}

// crawlStockList 爬取股票列表
func crawlStockList(urlFomart string, share string) {
	baseURL := fmt.Sprintf(urlFomart, config.StockNumLimit)
	res, err := doRequest(baseURL)
	if err != nil {
		log.Printf("url: %s, error: %s", baseURL, err)
	}
	sShareName := stockShareName{
		stockList: parseStockListResData(res, share),
		share:     share,
	}
	stockShareNameChan <- &sShareName
}

func processListen() {
	go func() {
		log.Println("processListen start...")
		num := 0
		for v := range stockShareNameChan {

			go func(sSN *stockShareName) {
				stockList := sSN.stockList
				share := sSN.share
				for idx := range stockList {
					sDetail := &stockDetail{
						StockCode: stockList[idx].StockCode,
						StockName: stockList[idx].StockName,
						StockID:   stockList[idx].StockID,
					}

					t := newTask(
						crawlOneStock,
						share,
						stockList[idx].StockCode,
						sDetail)

					p.entryChannel <- t
				}
			}(v)
			if num++; num == stockNum {
				close(stockShareNameChan)
				log.Println("stockShareNameChan Chan is close")
			}
		}

	}()
}

func crawlOneStock(stockCode string) []*oneDayStockInfo {
	url := fmt.Sprintf(config.StockInfoURL, stockCode)
	response, err := doRequest(url)
	if err != nil {
		log.Printf("crawlOneStockInfo error: %s, url: %s", err, url)
	}
	stockHistoryData := parseOneStockDateil(response)
	return stockHistoryData

}

// RunSpider 运行爬虫的入口
func RunSpider() {

	initScheduler()
	processListen()

	if config.IsShA {
		go crawlStockList(config.ShStockListURL, config.ShA)
		stockNum++
	}

	if config.IsSzA {
		go crawlStockList(config.SzStockListURL, config.SzA)
		stockNum++
	}

	if config.IsKcb {
		go crawlStockList(config.KcbStockListURL, config.Kcb)
		stockNum++
	}

}
