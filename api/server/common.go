package server

const (
	resCodeOk          = 1001
	resCodeNotResource = 1002
)

var resMsg = map[int]string{
	resCodeOk:          "ok",
	resCodeNotResource: "数据不存在",
}

// type ResultSet interface {
// 	GetStruct()
// }

type stockReItem struct {
	Rule            string `bson:"rule,omitempty"`
	StockCode       string `bson:"stock_code,omitempty"`
	StartInitialCap int    `bson:"start_initial_cap,omitempty"`
	Balance         int    `bson:"balance,omitempty"`
	Profitability   int    `bson:"profitability,omitempty"`
}
type stockSet struct {
	Total    int                       `bson:"total,omitempty"`
	StockSet map[string][]*stockReItem `bson:"stock_set,omitempty"`
}

type stockPoolResult struct {
	Date      string   `bson:"date",omitempty,json:"-"`
	StockSet  []string `bson:"stock_set",omitempty,json:"stock_set"`
	StockName []string `bson:"stock_name",omitempty,json:"stock_name"`
	PoolSize  int      `bson:"pool_size",omitempty,json:"pool_size"`
	Rule      string   `bson:"rule",omitempty,json:"rule"`
}

/*
 "stock_set" : {
            "601808" : [
                {
                    "rule" : "ma",
                    "stock_code" : "601808",
                    "start_initial_cap" : 10000,
                    "balance:" : 11993.86,
                    "profitability" : 19.9386000000001
                },
                {
                    "rule" : "macd",
                    "stock_code" : "601808",
                    "start_initial_cap" : 10000,
                    "balance:" : 10530.08,
                    "profitability" : 5.30079999999989
                }
            ],
*/
type backTestResult struct {
	Date         string    `bson:"date,omitempty"`
	UpStockSet   *stockSet `bson:"up_stock_set,omitempty"`
	DownStockSet *stockSet `bson:"down_stock_set,omitempty"`
}

type Response struct {
	code int
	msg  string
	data interface{}
}
