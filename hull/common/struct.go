package common

/*
{
    "record": [
        [
            "2020-01-22", 日期 0
            "55.100", 开盘价   1
            "64.950", 最高价   2
            "53.360", 收盘价   3
            "53.010", 最低价
            "159637.84",  成交量
            "36.870", 价格变动
            "223.59", 涨跌
            "53.360", 5日均价 8
            "53.360", 10日均价 9
            "53.360", 20日均价  10
            "159,637.84", 5日均量
            "159,637.84", 5日均量
            "159,637.84" 5日均量
		],
	}

*/

type RawStockDetailInfo struct {
	// Code string
	Record [][]string `json:"record"`
}

type StockSetItem struct {
	StockList []*RawStockInfo
}

// RawStockList 股票列表
type RawStockList struct {
	Data resStock `json:"data"`
}

type resStock struct {
	Total int           `json:"total"`
	Diff  []*RawStockInfo `json:"diff"`
}

// RawStockInfo include stock company_name code and id
type RawStockInfo struct {
	StockName string `json:"f14"`
	StockID   string `json:"f12"`
	StockCode string
}

type StockDetail struct {
	StockName   string
	StockID     string
	StockCode   string
	HistoryData []*StockDataDay
}

// type StockShare struct {
// 	share string
// 	stock stockDetail
// }

type StockDataDay struct {
	Open   float64
	Close  float64
	Volume float64 // 交易量
	Ma5    float64
	Ma10   float64
	Ma20   float64
	Date   string
}
