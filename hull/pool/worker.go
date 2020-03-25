package pool

import (
	"fmt"
	"hull/common"
	"hull/config"
	"hull/storage"
	"log"
	"sync"
	"sync/atomic"
)

// Pool global pool instance
var Pool *pool

// Task task instance
type Task struct {
	f      func(stockCode string) []*common.StockDataDay
	params string
	result *common.StockDetail
}

// NewTask init task
func NewTask(argFunc func(stockCode string) []*common.StockDataDay, s *common.RawStockInfo) *Task {
	t := Task{
		f:      argFunc,
		params: s.StockCode,
		result: &common.StockDetail{
			StockName: s.StockName,
			StockID:   s.StockID,
			StockCode: s.StockCode,
		},
	}

	return &t
}

func (t *Task) execute() *common.StockDetail {
	t.result.HistoryData = t.f(t.params)
	return t.result
}

type pool struct {
	workerNum int
	// 对外Task入口
	EntryChannel chan *Task
	// 对内Task入口
	jobsChannel chan *Task

	resultChannel chan *common.StockDetail

	taskNumber int32

	wg *sync.WaitGroup
}

func newPool(cap int) *pool {
	p := pool{
		EntryChannel:  make(chan *Task, 3),
		jobsChannel:   make(chan *Task, 3),
		resultChannel: make(chan *common.StockDetail),
		workerNum:     cap,
		taskNumber:    0,
		wg:            &sync.WaitGroup{},
	}
	return &p
}

func (p *pool) worker() {
	for task := range p.jobsChannel {
		p.resultChannel <- task.execute()
	}
}

func (p *pool) run() {

	saver := storage.Saver
	go func() {
		log.Println("pool start listen ResultChannel start ...")
		i := 0
		for v := range p.resultChannel {
			saver.ReceivedData(v)
			i++
			fmt.Printf("consumer  %d task\r", i)
			isStop := p.SubTaskNumber(1)
			if isStop == 0 {
				p.stop()
				saver.Stop()
			}
		}
		fmt.Println()
	}()

	go func() {
		for task := range p.EntryChannel {
			p.jobsChannel <- task
		}
	}()

	for wID := 0; wID < p.workerNum; wID++ {
		go p.worker()
	}
}
func (p *pool) stop() {
	close(p.EntryChannel)
	close(p.jobsChannel)
	close(p.resultChannel)
	log.Println("pool chan is closed, ", len(p.EntryChannel), len(p.jobsChannel), len(p.resultChannel))
}

func (p *pool) AddTaskNumber(delta int32) int32 {
	atomic.AddInt32(&p.taskNumber, delta)
	log.Println("register task number is:", p.taskNumber)
	return p.taskNumber
}

func (p *pool) SubTaskNumber(delta int32) int32 {
	p.taskNumber -= delta
	return p.taskNumber
}

// InitWorkerPool 初始化消费池
func InitWorkerPool() {

	Pool = newPool(config.PoolSize)

	Pool.run()
}
