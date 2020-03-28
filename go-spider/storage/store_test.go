package storage

import (
	"testing"
)

func Test_insertOne(t *testing.T) {
	// database{
	// }
	type insert struct {
		Name string
		Age  int
	}
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
			if got := Saver.insertOne("test_insert", tt.give); got != tt.want {
				t.Errorf("DB.InsertOne() = %v, want %v", got, tt.want)
			}
		})
	}

}
