package main

import (
	"go-spider/pool"
	"go-spider/spider"
	"go-spider/storage"
	"log"
	"time"
)

func main() {
	start := time.Now().Unix()

	pool.InitWorkerPool()

	spider.StartSpider()

	storage.Saver.StartSaveProcess()

	log.Printf("======== Process finished. cost time: %d s =======", time.Now().Unix()-start)
}
