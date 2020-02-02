package config

const (
	// ShStockListURL 沪市A股列表
	// ShStockListURL = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=%d&num=%d&sort=symbol&asc=1&node=%s&symbol=&_s_r_a=init"
	ShStockListURL = "http://84.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=%d&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:13,m:0+t:80&fields=f12,f14&_=1580530618530"
	// SzStockListURL 深市A股列表
	SzStockListURL = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=%d&num=%d&sort=symbol&asc=1&node=sz_a&symbol=&_s_r_a=init"
	// KcbStockListURL 科创板列表
	KcbStockListURL = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=%d&num=%d&sort=symbol&asc=1&node=kcb&symbol=&_s_r_a=init"
	// StockInfoURL 单个股票
	StockInfoURL = "http://api.finance.ifeng.com/akdaily/?code=%s&type=last"

	// IsStockList 是否爬取股票列表
	IsStockList = true
	// IsStockInfo 是否爬取股票详情
	IsStockInfo = true

	// StockNumLimit 一次爬取的股票数量
	StockNumLimit = 4500
	// IsShA 是否爬取上证A股
	IsShA = true
	// IsShB 是否爬取上证B股
	IsShB = true
	// IsSzA 是否爬取深证A股
	IsSzA = true
	// IsSzB 是否爬取深证B股
	IsSzB = true
	// IsKcb 是否爬取创业板
	IsKcb = true
)
