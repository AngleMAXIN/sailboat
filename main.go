package main

import (
	"sailboat/spider"
	"time"
)

func main() {
	spider.RunSpider()
	spider.StoreDataEvent()

	time.Sleep(time.Second * 2000)
}
