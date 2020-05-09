package server

import (
	"context"
	"log"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"go.mongodb.org/mongo-driver/mongo/readpref"
)

// DB 数据库实例
var DB *dbInstance

type dbInstance struct {
	client        *mongo.Client
	dbName        string
	poolSize      uint64
	connURI       string
	stockPoolColl string
	backTestColl  string
}

// 初始化
func init() {
	saver := &dbInstance{
		dbName:        dbName,
		connURI:       dbConnURI,
		poolSize:      dbPoolSize,
		stockPoolColl: stockPoolCollName,
		backTestColl:  backTestCollName,
	}
	client, err := saver.setConnect()
	if err != nil {
		panic(err)
	}
	saver.client = client
	DB = saver
	log.Println("connected db successful.")
}

// SetConnect 连接设置
func (db *dbInstance) setConnect() (*mongo.Client, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	client, err := mongo.Connect(ctx, options.Client().ApplyURI(db.connURI).SetMaxPoolSize(db.poolSize)) // 连接池
	if err != nil {
		return nil, err
	}
	if err = client.Ping(ctx, readpref.Primary()); err != nil {
		return nil, err
	}
	return client, err
}

// GetStockPoolData 获取股票池
func (db *dbInstance) GetStockPoolData() (interface{}, error) {
	resultSet := &stockPoolResult{}
	c, _ := db.client.Database(db.dbName).Collection(db.stockPoolColl).Clone()

	ctx, cancel := context.WithTimeout(context.Background(), time.Second*2)
	defer cancel()

	option := options.FindOne().SetSort(bson.D{{"_id", -1}})

	err := c.FindOne(ctx, bson.D{}, option).Decode(resultSet)

	if err != nil {
		return nil, err
	}
	return resultSet, nil
}

// GetBackTestResultData 获取回测结果
func (db *dbInstance) GetBackTestResultData() (interface{}, error) {

	c, _ := db.client.Database(db.dbName).Collection(db.backTestColl).Clone()

	ctx, cancel := context.WithTimeout(context.Background(), time.Second*2)
	defer cancel()

	option := options.FindOne().SetSort(bson.D{{"_id", -1}})
	singleResult := &backTestResult{}
	err := c.FindOne(ctx, bson.D{}, option).Decode(singleResult)

	if err != nil {
		log.Println("db error:", err.Error())
	}
	return singleResult, err

}
