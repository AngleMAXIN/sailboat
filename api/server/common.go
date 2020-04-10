package server

const (
	resCodeOk  = 1001
	resCodeNotResource = 1002
)

var resMsg = map[int]string{
	resCodeOk:"ok",
	resCodeNotResource:"数据不存在",
}

type stockPool struct {
	Date     string   `bson:"date",omitempty,json:"-"`
	StockSet []string `bson:"stock_set",omitempty,json:"stock_set"`
	PoolSize int      `bson:"pool_size",omitempty,json:"pool_size"`
	Rule     string   `bson:"rule",omitempty,json:"rule"`
}

type Response struct {
	code int
	msg string
	data interface{}
}