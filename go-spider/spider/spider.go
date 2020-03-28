package spider

import (
	"encoding/json"
	"fmt"
	"go-spider/common"
	"go-spider/config"
	"go-spider/pool"
	"io/ioutil"
	"log"
	"math/rand"
	"net/http"
	"strconv"
	"sync"
	"time"
)

var (
	// StockCount all stock counte
	stockSetChan = make(chan *common.StockSetItem, 2)

	stockShareMap = map[string]string{
		"kcb": "sh",
		"sh":  "sh",
		"sz":  "sz",
	}
)

func init() {
	rand.Seed(time.Now().UnixNano())
}

// requestHeaders 请求头
func requestHeaders() *string {
	index := rand.Intn(len(userAgent))
	return &userAgent[index]
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

	if ug := requestHeaders(); ug != nil {
		req.Header.Add("User-Agent", *ug)
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

// parseOneStockDetails parse one stock datails info every day
func parseOneStockDetails(content []byte) []*common.StockDataDay {
	rawStock := &common.RawStockDetailInfo{}
	if err := json.Unmarshal(content, rawStock); err != nil {
		log.Printf("parse response data error: %s, data: %s", err, content)
		return []*common.StockDataDay{}
	}

	stockSet := rawStock.Record
	stockResultSet := make([]*common.StockDataDay, 0, len(stockSet))
	for i := 0; i < len(stockSet); i++ {
		day := stockSet[i]
		stock := new(common.StockDataDay)
		stock.Date = day[0]
		stock.Open, _ = strconv.ParseFloat(day[1], 64)
		stock.Close, _ = strconv.ParseFloat(day[3], 64)
		stock.Volume, _ = strconv.ParseFloat(day[5], 64)
		stock.Ma5, _ = strconv.ParseFloat(day[8], 64)
		stock.Ma10, _ = strconv.ParseFloat(day[9], 64)
		stock.Ma20, _ = strconv.ParseFloat(day[10], 64)

		stockResultSet = append(stockResultSet, stock)
	}
	return stockResultSet
}

// parseStockList parse stock list data
func parseStockList(content []byte, share string) []*common.RawStockInfo {
	var res common.RawStockList
	if err := json.Unmarshal(content, &res); err != nil {
		log.Printf("parse StockList share: %s, error: %s\n", share, err)
	}

	log.Printf("stock type: %s, total: %d\n", share, res.Data.Total)

	stockList := res.Data.Diff
	codePrefix := stockShareMap[share]

	for i := 0; i < int(res.Data.Total); i++ {
		stockList[i].StockCode = codePrefix + stockList[i].StockID
	}
	return stockList
}

// crawlStockList 爬取股票列表
func crawlStockList(wg *sync.WaitGroup, urlFomart string, share string) {
	defer wg.Done()

	url := fmt.Sprintf(urlFomart, config.StockNumLimit)
	content, err := doRequest(url)
	if err != nil {
		log.Printf("url: %s, error: %s", url, err)
		return
	}
	ssItem := common.StockSetItem{
		StockList: parseStockList(content, share),
	}
	pool.Pool.AddTaskNumber(int32(len(ssItem.StockList)))
	stockSetChan <- &ssItem
}

func crawlOneStock(stockCode string) []*common.StockDataDay {
	url := fmt.Sprintf(config.StockInfoURL, stockCode)
	content, err := doRequest(url)
	if err != nil {
		log.Printf("crawlOneStockInfo error: %s, url: %s", err, url)
		return []*common.StockDataDay{}
	}
	return parseOneStockDetails(content)

}

func transferTaskToWorkerPool() {
	go func() {
		log.Println("spider start tansfer task to worker pool...")
		for ssItem := range stockSetChan {

			go func(ssItem *common.StockSetItem) {
				for _, item := range ssItem.StockList {
					// fmt.Println("recevied a task stock code is", item.StockCode)
					task := pool.NewTask(crawlOneStock, item)

					pool.Pool.EntryChannel <- task
				}
			}(ssItem)
		}
	}()
}

// StartSpider 运行爬虫的入口
func StartSpider() {
	transferTaskToWorkerPool()
	var wg sync.WaitGroup

	if config.IsShA {
		wg.Add(1)
		go crawlStockList(&wg, config.ShStockListURL, config.ShA)
	}

	if config.IsSzA {
		wg.Add(1)
		go crawlStockList(&wg, config.SzStockListURL, config.SzA)
	}

	wg.Wait()
	close(stockSetChan)
}
