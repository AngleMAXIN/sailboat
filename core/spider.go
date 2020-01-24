package core

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
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

func buildURL(baseURL string, params map[string]string) string {
	u, err := url.Parse(baseURL)
	if err != nil {
		log.Println("parse url erorr:%s", err)
	}
	q := u.Query()
	for key, values := range params {
		q.Add(key, values)
	}
	u.RawQuery = q.Encode()
	return u.String()

}

func requestHeaders() map[string]string {
	return nil
}

func doRequest(url string) ([]byte, error) {
	client := &http.Client{}
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		log.Println("new get request error:", err)
		return nil, err
	}
	log.Printf("URL: %s\n", url)

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
		log.Fatalln("status code is:", resp.StatusCode)
	}
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Println("read all body error:", err)
		return nil, err

	}
	// log.Println("Body: ",string(body))
	return body, nil

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

type stockInfo struct {
	// Code string
	Record [][]string
}

// type stockInfo struct {
// Data detail
// }

func parseResToStruct(res []byte) *stockInfo {
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

// Dispatch 运行爬虫
func Dispatch() {
	// baseURL := "http://58.push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.600579&ut=fa5fd1943c7b386f172d6893dbfba10b" +
	// "&fields1=f1%2Cf2&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58&klt=101&fqt=0&end=20500101&lmt=1000000&_=1579508724957"

	baseURL := "http://api.finance.ifeng.com/akdaily/"
	params := map[string]string{
		"code": "sz000001",
		"type": "last",
	}

	// for i := 0; i < 50; i++ {
	// 	url := fmt.Sprintf(baseURL, i)
	// 	fmt.Println(url)
	// 	time.Sleep(time.Second * 4)
	// 	text := getHtmlTest(url)
	// 	parseText(text)
	// }
	// params := make(map[string]string)
	// params := map[string]string{
	// 	"secid":   "1.600579",
	// 	"ut":      "fa5fd1943c7b386f172d6893dbfba10b",
	// 	"fields1": "f1,f2,f3,f4",
	// 	"fields2": "f4,f67,f43",
	// 	"klt":     "101",
	// 	"fqt":     "0",
	// 	"end":     "2050101",
	// 	"lmt":     "1000000",
	// 	"_":       "1579508724957",
	// }
	url := buildURL(baseURL, params)
	resData, err := doRequest(url)
	if err != nil {
		log.Printf("URL: %s, err: %s\n", url, err.Error())
	}
	parseResToStruct(resData)

}
