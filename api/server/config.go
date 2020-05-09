package server

const (
	dbPoolSize = uint64(50)
	// DBconnURI 数据库连接uri
	dbConnURI = "mongodb://admin:maxin123@localhost:27017"
	// dbConnURI = "mongodb://39.106.120.138:27017"
	// DBName 数据库连接名称
	dbName = "sailboat_db"
	
	stockPoolCollName = "pool_his"
	backTestCollName = "back_test_his"
)
