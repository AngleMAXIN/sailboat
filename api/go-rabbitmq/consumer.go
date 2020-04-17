package main

import (
	"github.com/streadway/amqp"
	"log"
)

func main(){
	// 连接RabbitMQ服务器
	conn, err := amqp.Dial("amqp://guest:guest@127.0.0.1:5672/")
	failOnError(err, "Failed to connect to RabbitMQ")
	defer conn.Close()
	// 创建一个channel
	ch, err := conn.Channel()
	failOnError(err, "Failed to open a channel")
	defer ch.Close()
	// 监听队列
	q, err  := ch.QueueDeclare(
		"python-test",			// 队列名称
		false,			// 是否持久化
		false,		// 是否自动删除
		false,			// 是否独立
		false,nil,
	)
	failOnError(err, "Failed to declare a queue")
	// 消费队列
	msgs, err := ch.Consume(
		q.Name, // queue
		"",     // consumer
		true,   // auto-ack
		false,  // exclusive
		false,  // no-local
		false,  // no-wait
		nil,    // args
	)
	failOnError(err, "Failed to register a consumer")
    // 申明一个goroutine,一遍程序始终监听
	forever := make(chan bool)

	go func() {
		for d := range msgs {
			log.Printf("Received a message: %s", d.Body)
		}
	}()

	log.Printf(" [*] Waiting for messages. To exit press CTRL+C")
	<-forever
}

// 帮助函数检测每一个amqp调用
func failOnError(err error, msg string)  {
	if err != nil {
		log.Fatalf("%s: %s", msg, err)
	}
}
