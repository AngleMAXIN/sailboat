package core

import (
	"fmt"
	"testing"
)

func Test_getHtmlTest(t *testing.T)  {
	url :=  "http://q.10jqka.com.cn/"
	res := GetHtmlTest(url)
	//t.Error(res)
	fmt.Println(res)
}