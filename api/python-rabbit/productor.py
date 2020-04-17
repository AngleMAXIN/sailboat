import pika
import json

credentials = pika.PlainCredentials('guest', 'guest')  # mq用户名和密码
# 虚拟队列需要指定参数 virtual_host，如果是默认的可以不填。
connection = pika.BlockingConnection(pika.ConnectionParameters(host = '127.0.0.1',port = 5672,virtual_host = '/',credentials = credentials))
channel=connection.channel()
# 声明消息队列，消息将在这个队列传递，如不存在，则创建
result = channel.queue_declare(queue = 'python-test')

for i in range(10000):
    message=json.dumps({'OrderId':"1000%s"%i})
# 向队列插入数值 routing_key是队列名
    channel.basic_publish(exchange = '',routing_key = 'python-test',body = message)
    print(message)
connection.close()