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
	"strings"
	"sync"
	"time"
)

var (
	// StockCount all stock counte
	stockSetChan = make(chan *common.StockSetItem, 2)

	stockShareMap = map[byte]string{
		'0': "2",
		'6': "1",
		'3': "2",
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
	sleepTime := rand.Intn(6666)
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
	content = content[1 : len(content)-1]
	rawStock := &common.RawStockDetailInfo{}
	if err := json.Unmarshal(content, rawStock); err != nil {
		log.Printf("parse stock detail info error: %s, data: %s", err, content)
		return nil
	}

	stockSet := rawStock.Data
	stockResultSet := make([]*common.StockDataDay, 0, len(stockSet))
	for i := 0; i < len(stockSet); i++ {
		day := stockSet[i]
		splitRes := strings.Split(day, ",")
		stock := new(common.StockDataDay)
		stock.Date = splitRes[0]
		stock.Close, _ = strconv.ParseFloat(splitRes[2], 64)
		stock.High, _ = strconv.ParseFloat(splitRes[3], 64)
		stock.Low, _ = strconv.ParseFloat(splitRes[4], 64)

		stockResultSet = append(stockResultSet, stock)
	}
	return stockResultSet
}

// parseStockList parse stock list data
func parseStockList(content []byte, share string) []*common.RawStockInfo {
	var res common.RawStockList
	if err := json.Unmarshal(content, &res); err != nil {
		log.Printf("parse stock code list error, share: %s, error: %s\n", share, err)
	}

	log.Printf("stock type: %s, total: %d\n", share, res.Data.Total)

	stockList := res.Data.Diff

	for i := 0; i < int(res.Data.Total); i++ {
		code := stockList[i].StockID
		stockList[i].StockCode = stockList[i].StockID + stockShareMap[code[0]]
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
	url := fmt.Sprintf(config.StockHisDataURL, stockCode)
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
