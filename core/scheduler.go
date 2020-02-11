package core

import (
	"log"
	"sailboat/config"
)

var p *pool

type stockShare struct {
	share string
	stock *stockDetail
}
type task struct {
	f      func(stockCode string) []*oneDayStockInfo
	params string
	stockShare
}

func newTask(argFunc func(stockCode string) []*oneDayStockInfo, share string, params string, s *stockDetail) *task {
	t := task{
		f:          argFunc,
		params:     params,
		stockShare: stockShare{stock: s, share: share},
	}

	return &t
}

func (t *task) execute() *stockShare {
	t.stockShare.stock.HistoryData = t.f(t.params)
	return &t.stockShare
}

type pool struct {
	workerNum int
	// 对外Task入口
	entryChannel chan *task
	// 对内Task入口
	jobsChannel chan *task

	resultChannel chan *stockShare
}

func newPool(cap int) *pool {
	p := pool{
		entryChannel:  make(chan *task, 3),
		jobsChannel:   make(chan *task, 3),
		resultChannel: make(chan *stockShare),
		workerNum:     cap,
	}
	return &p
}

func (p *pool) worker(workerID int) {
	for task := range p.jobsChannel {
		p.resultChannel <- task.execute()
	}
}

func (p *pool) run() {
	for wID := 0; wID < p.workerNum; wID++ {
		go p.worker(wID)
	}

	go func() {
		log.Println("listen ResultChannel start ...")
		for v := range p.resultChannel {
			switch v.share {
			case "sz":
				szStockResultChan <- v.stock
			case "sh":
				shStockResultChan <- v.stock
			case "kcb":
				kcbStockResultChan <- v.stock
			default:
				log.Println("See a ghost")
			}
		}
	}()

	go func() {
		log.Println("listen EntryChannel start...")
		for {
			for task := range p.entryChannel {
				log.Printf("start crawl stock share: %s\n", task.params)
				p.jobsChannel <- task
			}
		}

	}()
}

func initScheduler() {

	p = newPool(config.PoolSize)

	p.run()

}
