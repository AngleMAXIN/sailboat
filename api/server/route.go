package server

import (
	"github.com/fvbock/endless"
	"github.com/gin-gonic/gin"
	"log"
	"net/http"
)

func makeResponse(code int, data interface{}) map[string]interface{} {
	msg := resMsg[code]
	return gin.H{"code": code, "data": data, "msg": msg}
}

func getStockPoolDataHandler(ctx *gin.Context) {
	code := resCodeOk
	stockPoolData, err := DB.GetStockPoolData()
	if err != nil {
		code = resCodeNotResource
	}
	response := makeResponse(code, *stockPoolData)
	ctx.JSON(http.StatusOK,response)
	return
}

func StartServer() {
	router := gin.Default()
	router.GET("/api.v1/stock-pool", getStockPoolDataHandler)
	err := endless.ListenAndServe(":8081", router)
	if err != nil {
		log.Fatal(err)
	}
}
