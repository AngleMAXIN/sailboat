package spider

import (
	"context"
	"log"
	"hull/config"
	"time"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"go.mongodb.org/mongo-driver/mongo/readpref"
)

// DB 数据库实例
var DB *database
var szStockResultChan = make(chan *stockDetail, 2)
var shStockResultChan = make(chan *stockDetail, 2)
var kcbStockResultChan = make(chan *stockDetail, 2)

type database struct {
	client *mongo.Client
	dbName string
	// collection string
	poolSize uint64
	connURI  string
}

// InitDB 初始化
func initDB(poolSize uint64, connURI string, dbName string) error {
	db := &database{
		// client:,
		dbName:   dbName,
		connURI:  connURI,
		poolSize: poolSize,
	}
	client, err := db.setConnect()
	if err != nil {
		return err
	}
	db.client = client
	DB = db
	log.Println("connected db succesful.")
	return err
}

// SetConnect 连接设置
func (db *database) setConnect() (*mongo.Client, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	client, err := mongo.Connect(ctx, options.Client().ApplyURI(db.connURI).SetMaxPoolSize(db.poolSize)) // 连接池
	if err != nil {
		// log.Panic(err)
		return nil, err
	}
	if err = client.Ping(ctx, readpref.Primary()); err != nil {
		// log.Printf(err.Error())
		return nil, err

	}
	// db.client = client
	return client, err
}

// InsertOne 插入单个
func (db *database) insertOne(collection string, value interface{}) error {
	c := db.client.Database(db.dbName).Collection(collection)
	_, err := c.InsertOne(context.TODO(), value)
	if err != nil {
		return err
	}
	return nil
}

// InsertMany 批量插入
func (db *database) insertMany(collection string, value []interface{}) error {
	c := db.client.Database(db.dbName).Collection(collection)
	_, err := c.InsertMany(context.TODO(), value)
	if err != nil {
		return err
	}
	return nil
}

// StoreDataEvent 存储事件监听
func StoreDataEvent() {
	pSize := config.DBPoolSize
	dbConnURI := config.DBconnURI
	dbName := config.DBName

	initDB(pSize, dbConnURI, dbName)

	var (
		szStockInsertNum  uint
		shStockInsertNum  uint
		kcbStockInsertNum uint
	)
	// go func() {
	log.Println("StoreDataEvent start...")
	for {
		select {
		case v := <-szStockResultChan:
			DB.insertOne("sz_stock", *v)
			szStockInsertNum++
		case v := <-shStockResultChan:
			DB.insertOne("sh_stock", *v)
			shStockInsertNum++
		case v := <-kcbStockResultChan:
			DB.insertOne("kcb_stock", *v)
			kcbStockInsertNum++
		}
	}

	// }()
}

// func NewMgo(database, collection string) *mgo {

// return &mgo{
// database,
// collection,
// }
// }

// 查询单个
// func (m *mgo) FindOne(key string, value interface{}) *mongo.SingleResult {
// 	client := models.DB.Mongo
// 	collection, _ := client.Database(m.database).Collection(m.collection).Clone()
// 	//collection.
// 	filter := bson.D{{key, value}}
// 	singleResult := collection.FindOne(context.TODO(), filter)
// 	return singleResult
// }

// //查询集合里有多少数据
// func (m *mgo) CollectionCount() (string, int64) {
// 	client := models.DB.Mongo
// 	collection := client.Database(m.database).Collection(m.collection)
// 	name := collection.Name()
// 	size, _ := collection.EstimatedDocumentCount(context.TODO())
// 	return name, size
// }

// //按选项查询集合 Skip 跳过 Limit 读取数量 sort 1 ，-1 . 1 为最初时间读取 ， -1 为最新时间读取
// func (m *mgo) CollectionDocuments(Skip, Limit int64, sort int) *mongo.Cursor {
// 	client := models.DB.Mongo
// 	collection := client.Database(m.database).Collection(m.collection)
// 	SORT := bson.D{{"_id", sort}} //filter := bson.D{{key,value}}
// 	filter := bson.D{{}}
// 	findOptions := options.Find().SetSort(SORT).SetLimit(Limit).SetSkip(Skip)
// 	//findOptions.SetLimit(i)
// 	temp, _ := collection.Find(context.Background(), filter, findOptions)
// 	return temp
// }

// //获取集合创建时间和编号
// func (m *mgo) ParsingId(result string) (time.Time, uint64) {
// 	temp1 := result[:8]
// 	timestamp, _ := strconv.ParseInt(temp1, 16, 64)
// 	dateTime := time.Unix(timestamp, 0) //这是截获情报时间 时间格式 2019-04-24 09:23:39 +0800 CST
// 	temp2 := result[18:]
// 	count, _ := strconv.ParseUint(temp2, 16, 64) //截获情报的编号
// 	return dateTime, count
// }

// //删除文章和查询文章
// func (m *mgo) DeleteAndFind(key string, value interface{}) (int64, *mongo.SingleResult) {
// 	client := models.DB.Mongo
// 	collection := client.Database(m.database).Collection(m.collection)
// 	filter := bson.D{{key, value}}
// 	singleResult := collection.FindOne(context.TODO(), filter)
// 	DeleteResult, err := collection.DeleteOne(context.TODO(), filter, nil)
// 	if err != nil {
// 		fmt.Println("删除时出现错误，你删不掉的~")
// 	}
// 	return DeleteResult.DeletedCount, singleResult
// }

// //删除文章
// func (m *mgo) Delete(key string, value interface{}) int64 {
// 	client := models.DB.Mongo
// 	collection := client.Database(m.database).Collection(m.collection)
// 	filter := bson.D{{key, value}}
// 	count, err := collection.DeleteOne(context.TODO(), filter, nil)
// 	if err != nil {
// 		fmt.Println(err)
// 	}
// 	return count.DeletedCount

// } 'Liberation Mono'

// //删除多个
// func (m *mgo) DeleteMany(key string, value interface{}) int64 {
// 	client := models.DB.Mongo
// 	collection := client.Database(m.database).Collection(m.collection)
// 	filter := bson.D{{key, value}}

// 	count, err := collection.DeleteMany(context.TODO(), filter)
// 	if err != nil {
// 		fmt.Println(err)
// 	}
// 	return count.DeletedCount
// }
