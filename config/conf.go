package config

const (
	// ShStockListURL 沪市A股列表
	// ShStockListURL = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=%d&num=%d&sort=symbol&asc=1&node=%s&symbol=&_s_r_a=init"
	ShStockListURL = "http://84.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=%d&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:13,m:0+t:80&fields=f12,f14&_=1580530618530"
	// SzStockListURL 深市A股列表
	SzStockListURL = "http://84.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=%d&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:13,m:0+t:80&fields=f12,f14&_=1580530618530"
	// KcbStockListURL 科创板列表
	KcbStockListURL = "http://84.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=%d&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:1+t:23&fields=f12,f14&_=1580530618599"
	// StockInfoURL 单个股票
	StockInfoURL = "http://api.finance.ifeng.com/akdaily/?code=%s&type=last"

	// IsStockList 是否爬取股票列表
	IsStockList = true
	// IsStockInfo 是否爬取股票详情
	IsStockInfo = true
	// ShA 沪市A股
	ShA = "sh"
	// SzA 深市A股
	SzA = "sz"
	// Kcb 创业板
	Kcb = "kcb"
	// StockNumLimit 一次爬取的股票数量
	StockNumLimit = 4500
	// IsShA 是否爬取上证A股
	IsShA = false
	// IsShB 是否爬取上证B股
	IsShB = false
	// IsSzA 是否爬取深证A股
	IsSzA = false
	// IsSzB 是否爬取深证B股
	IsSzB = false
	// IsKcb 是否爬取创业板
	IsKcb = true
	// PoolSize 爬虫池 worker 数量
	PoolSize = 4
	// DBPoolSize 数据库连接池大小
	DBPoolSize = uint64(50)
	// DBconnURI 数据库连接uri
	DBconnURI = "mongodb://admin:maxin123@localhost:27017"
	// DBName 数据库连接名称
	DBName = "sailboat_db"
)
