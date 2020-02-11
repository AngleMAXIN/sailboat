package main

import (
	"sailboat/core"
	"time"
)

func main() {
	core.StoreDataEvent()
	core.RunSpider()
	time.Sleep(time.Second*2000)
}