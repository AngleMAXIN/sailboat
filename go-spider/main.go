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

/***************
func main() {
	var testCahn = make(chan int, 90)
	var quit = make(chan int)
	go func() {
		for v := range testCahn {
			fmt.Println("out ->", v)
			time.Sleep(time.Microsecond * 200)
		}
		quit <- 1
	}()

	go func() {
		count := 90
		for i := 0; i < count; i++ {
			fmt.Println("int <-", i)
			testCahn <- i
		}
		close(testCahn)
		fmt.Println("我都close 了")
	}()
	<-quit
	fmt.Println("end")
}
***************/
