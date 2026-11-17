// Package cistercian encodes integers from 1 to 9999 as Cistercian numeral
// geometry: line segments on an integer grid (x 0..2, y 0..3, origin top-left)
// following contract v1 of SPECIFICATION.md.
//
// Approach: the five basic strokes are bit flags; each digit is a set of
// flags. Every digit's strokes are transformed into every quadrant once, at
// package initialisation, into a fixed-size lookup table, so Encode only
// concatenates precomputed slices.
package cistercian

import "fmt"

// Grid bounds and the encodable range.
const (
	Width    = 2
	Height   = 3
	MinValue = 1
	MaxValue = 9999
)

// Point is a grid point [x, y]; as an array it marshals to JSON as [x,y].
type Point [2]int

// Segment is a straight line between two grid points.
type Segment [2]Point

// Numeral is the contract-v1 geometry of one number.
type Numeral struct {
	Segments []Segment `json:"segments"`
}

// Stem is the mandatory vertical stroke shared by every numeral.
var Stem = Segment{{1, 0}, {1, 3}}

type stroke uint8

const (
	top          stroke = 1 << iota // bar at the top of the stem
	lower                           // bar one unit lower
	diagonalDown                    // from the stem top down to the outer corner
	diagonalUp                      // from the stem up to the outer top corner
	outer                           // outer vertical, detached from the stem
)

// unitsStroke[i] is the segment of stroke 1<<i in the units (upper-right) quadrant.
var unitsStroke = [...]Segment{
	{{1, 0}, {2, 0}},
	{{1, 1}, {2, 1}},
	{{1, 0}, {2, 1}},
	{{1, 1}, {2, 0}},
	{{2, 0}, {2, 1}},
}

var digitStrokes = [10]stroke{
	0,
	top,
	lower,
	diagonalDown,
	diagonalUp,
	top | diagonalUp,
	outer,
	top | outer,
	lower | outer,
	top | lower | outer,
}

// quadrant describes how a place mirrors the units quadrant.
type quadrant struct{ mirrorX, mirrorY bool }

// Places from least significant: units, tens, hundreds, thousands.
var quadrants = [4]quadrant{{false, false}, {true, false}, {false, true}, {true, true}}

func (q quadrant) point(p Point) Point {
	if q.mirrorX {
		p[0] = Width - p[0]
	}
	if q.mirrorY {
		p[1] = Height - p[1]
	}
	return p
}

// motifs[place][digit] holds the digit's segments in that place's quadrant.
var motifs [4][10][]Segment

func init() {
	for place, q := range quadrants {
		for digit, strokes := range digitStrokes {
			for bit, s := range unitsStroke {
				if strokes&(1<<bit) != 0 {
					motifs[place][digit] = append(motifs[place][digit], Segment{q.point(s[0]), q.point(s[1])})
				}
			}
		}
	}
}

// Encode returns the geometry of n, which must be between MinValue and MaxValue.
func Encode(n int) (Numeral, error) {
	if n < MinValue || n > MaxValue {
		return Numeral{}, fmt.Errorf("%d is outside %d..%d", n, MinValue, MaxValue)
	}
	segments := make([]Segment, 0, 13) // stem + at most 3 strokes per place
	segments = append(segments, Stem)
	for place, rest := 0, n; place < len(quadrants); place, rest = place+1, rest/10 {
		segments = append(segments, motifs[place][rest%10]...)
	}
	return Numeral{Segments: segments}, nil
}
