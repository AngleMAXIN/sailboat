package core

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"strings"

	"github.com/PuerkitoBio/goquery"
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

func startReq(params []string) {


}

func getResponse(url string) []byte {
	client := &http.Client{}
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		log.Fatal("new get request error:", err)
	}
	for key, value := range header {
		req.Header.Add(key, value)
	}

	resp, err := client.Do(req)
	if err != nil {
		log.Fatal("request error:", err)
	}

	defer resp.Body.Close()
	if resp.StatusCode != 200 {
		log.Fatal("status code is:", resp.StatusCode)
	}
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Fatal("read all body error:", err)
	}

	return body

}

func parseResText(text string) {
	fmt.Println(text)
	dom, err := goquery.NewDocumentFromReader(strings.NewReader(text))
	if err != nil {
		log.Fatal("parse text error:", err)
	}
	dom.Find("td>a").Each(func(i int, selection *goquery.Selection) {
		if selection.Text() != "" {
			fmt.Println(selection.Text())
		}
	})
}


type detail struct {
	Code   string
	Klines []string
}

type stockInfo struct {
	Data detail
}

func parseResToStrucr(res []byte) *stockInfo {
	oneStock := &stockInfo{}
	err := json.Unmarshal(res, oneStock)
	if err != nil {
		log.Fatal("parse response data. error:", err)
	}
	klines := oneStock.Data.Klines
	// for idx := range klines {
	// fmt.Println(klines[idx])
	// }
	fmt.Println("len", len(klines))
	return oneStock
}

// Dispatch 运行爬虫
func Dispatch() {
	urlTemp := "http://58.push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.600579&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58&klt=101&fqt=0&end=20500101&lmt=1000000&_=1579508724957"
	// for i := 0; i < 50; i++ {
	// 	url := fmt.Sprintf(urlTemp, i)
	// 	fmt.Println(url)
	// 	time.Sleep(time.Second * 4)
	// 	text := getHtmlTest(url)
	// 	parseText(text)
	// }
	resData := getResponse(urlTemp)
	parseResToStrucr(resData)

}
