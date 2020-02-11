package main

import (
	"fmt"
	"time"
)

var testChan chan int

func main() {
	testChan = make(chan int, 9)
	fmt.Printf("1 len:%d,cap:%d\n", len(testChan), cap(testChan))
	go func() {
		fmt.Printf("5 len:%d,cap:%d\n", len(testChan), cap(testChan))
		for v := range testChan {
			fmt.Println("recive: ", v)
			fmt.Printf("2 len:%d,cap:%d\n", len(testChan), cap(testChan))

		}
	}()
	testChan <- 9
	fmt.Printf("3 len:%d,cap:%d\n", len(testChan), cap(testChan))

	time.Sleep(time.Microsecond * 200)
	fmt.Printf("4 len:%d,cap:%d\n", len(testChan), cap(testChan))

}
