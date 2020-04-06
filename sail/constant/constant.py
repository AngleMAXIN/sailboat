import os
# ShStockListURL 沪市A股股票
ShStockListURL = "http://84.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=3000&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:1+t:2,m:1+t:23&fields=f12,f14,f9&_=1580530618558"
# SzStockListURL 深市A股列表
SzStockListURL = "http://84.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=3000&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:13,m:0+t:80&fields=f12,f14,f9&_=1580530618530"
# KcbStockListURL 科创板列表
KcbStockListURL = "http://84.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=3000&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:1+t:23&fields=f12,f14,f9&_=1580530618599"
# StockInfoURL 单个股票
StockInfoURL = "http://api.finance.ifeng.com/akdaily/?code=%s&type=last"

StockHisDataURL = "http://pdfm.eastmoney.com/EM_UBG_PDTI_Fast/api/js?token=4f1862fc3b5e77c150a2b985b12db0fd&rtntype=6&id={0}&type=k"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
StorePath = BASE_DIR + "/pool_stock_store"

# DBURL = "mongodb://39.106.120.138:27017"
DBURL = "mongodb://admin:maxin123@localhost:27017"

DB_COLL_POOL = "pool_his"