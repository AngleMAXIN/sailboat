package spider

import (
	"testing"
)

func Test_initDB(t *testing.T) {
	tests := []struct {
		name string
		give database
		want error
	}{
		// TODO: Add test cases.
		{
			name: "test for successful init db",
			give: database{
				poolSize: uint64(30),
				connURI:  "mongodb://admin:maxin123@localhost:27017",
				dbName:   "sailboat_db",
			},
			want: nil,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := initDB(tt.give.poolSize, tt.give.connURI, tt.give.dbName); got != tt.want {
				t.Errorf("InitDB() = %v, want %v", got, tt.want)
			}
		})
	}

}

func Test_insertOne(t *testing.T) {
	// database{
	poolSize := uint64(30)
	connURI := "mongodb://admin:maxin123@localhost:27017"
	dbName := "sailboat_db"
	// }
	type insert struct {
		Name string
		Age  int
	}
	initDB(poolSize, connURI, dbName)
	tests := []struct {
		name string
		give interface{}
		want error
	}{
		{
			name: "insert struct data ok",
			give: insert{Name: "maxin", Age: 45},
			want: nil,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := DB.insertOne("test_insert", tt.give); got != tt.want {
				t.Errorf("DB.InsertOne() = %v, want %v", got, tt.want)
			}
		})
	}

}
