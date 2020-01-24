package main

import "net/url"

import "fmt"

func main() {
	baseURL := "http://api.finance.ifeng.com/akdaily/"
	u, _ := url.Parse(baseURL)
	fmt.Println(u.RequestURI(), u.Query())
	q := u.Query()
	q.Add("code", "sdsds")
	u.RawQuery = q.Encode()
	fmt.Println(u.Query(), u.String())
}
