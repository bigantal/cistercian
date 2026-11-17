package cistercian_test

import (
	"encoding/json"
	"fmt"
	"testing"

	"github.com/bigantal/cistercian/implementations/go"
)

func ExampleEncode() {
	numeral, _ := cistercian.Encode(1)
	out, _ := json.Marshal(numeral)
	fmt.Println(string(out))
	// Output: {"segments":[[[1,0],[1,3]],[[1,0],[2,0]]]}
}

func TestEncodeRejectsOutOfRange(t *testing.T) {
	for _, n := range []int{0, -1, 10000} {
		if _, err := cistercian.Encode(n); err == nil {
			t.Errorf("Encode(%d): want error", n)
		}
	}
}

func TestEncodeStaysOnGrid(t *testing.T) {
	for n := cistercian.MinValue; n <= cistercian.MaxValue; n++ {
		numeral, err := cistercian.Encode(n)
		if err != nil {
			t.Fatalf("Encode(%d): %v", n, err)
		}
		if numeral.Segments[0] != cistercian.Stem {
			t.Fatalf("Encode(%d): first segment %v is not the stem", n, numeral.Segments[0])
		}
		for _, s := range numeral.Segments {
			for _, p := range s {
				if p[0] < 0 || p[0] > cistercian.Width || p[1] < 0 || p[1] > cistercian.Height {
					t.Fatalf("Encode(%d): point %v off the grid", n, p)
				}
			}
		}
	}
}

func TestZeroDigitsAddNothing(t *testing.T) {
	for _, n := range []int{1, 10, 100, 1000} {
		numeral, _ := cistercian.Encode(n)
		if got := len(numeral.Segments); got != 2 { // the stem plus one stroke
			t.Errorf("Encode(%d): %d segments, want stem + 1", n, got)
		}
	}
}
