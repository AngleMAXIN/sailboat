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
	StockName []string `bson:"stock_name",omitempty,json:"stock_name"`
	PoolSize int      `bson:"pool_size",omitempty,json:"pool_size"`
	Rule     string   `bson:"rule",omitempty,json:"rule"`
}


/*
"date": date.today().isoformat(),
"up_stock_set": {"stock_set": up_stock_set.most_common(), "total": len(up_stock_set)},
 "down_stock_set": {"stock_set": down_stock_set.most_common(), "total": len(down_stock_set)},
*/
type stockSet struct {
	Total int
	StockSet map[string]int
}

type backTestResult struct {
	Date string
	UpStockSet *stockSet
	DownStockSet *stockSet
}

type Response struct {
	code int
	msg string
	data interface{}
}