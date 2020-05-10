package server

import (
	"log"
	"net/http"

	"github.com/fvbock/endless"
	"github.com/gin-gonic/gin"
)

func makeResponse(code int, data interface{}) map[string]interface{} {
	msg := resMsg[code]

	return gin.H{"code": code, "data": data, "msg": msg}
}

func Cors() gin.HandlerFunc {
	return func(c *gin.Context) {
		method := c.Request.Method

		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Headers", "Content-Type,AccessToken,X-CSRF-Token, Authorization, Token")
		c.Header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
		c.Header("Access-Control-Expose-Headers", "Content-Length, Access-Control-Allow-Origin, Access-Control-Allow-Headers, Content-Type")
		c.Header("Access-Control-Allow-Credentials", "true")

		//放行所有OPTIONS方法
		if method == "OPTIONS" {
			c.AbortWithStatus(http.StatusNoContent)
		}
		// 处理请求
		c.Next()
	}
}

func getStockPoolDataHandler(ctx *gin.Context) {
	code := resCodeOk
	stockPoolData, err := DB.GetStockPoolData()
	if err != nil {
		log.Printf("%v", err)
		code = resCodeNotResource
	}
	response := makeResponse(code, stockPoolData)
	ctx.JSON(http.StatusOK, response)
	return
}

func getBackTestResultHandler(ctx *gin.Context) {
	code := resCodeOk
	backTestResult, err := DB.GetBackTestResultData()
	if err != nil {
		code = resCodeNotResource
	}
	response := makeResponse(code, backTestResult)
	ctx.JSON(http.StatusOK, response)
	return
}

func StartServer() {
	router := gin.Default()
	router.Use(Cors())
	router.GET("/api.v1/stock-pool", getStockPoolDataHandler)
	router.GET("/api.v1/back-test-result", getBackTestResultHandler)

	err := endless.ListenAndServe(":8081", router)
	if err != nil {
		log.Fatal(err)
	}
}
