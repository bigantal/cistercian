package cistercian;

import java.util.ArrayList;
import java.util.EnumSet;
import java.util.List;
import java.util.Set;
import java.util.function.UnaryOperator;

/// Cistercian numeral encoder (Java implementation).
///
/// Approach: a [Stroke] enum names the five basic strokes, each carrying its segment in the
/// units (upper-right) quadrant; a [Place] enum carries the point transform that moves a stroke
/// into its quadrant; a `switch` expression maps each digit to an [EnumSet] of strokes.
/// Geometry values are immutable records.
public final class Cistercian {

    public static final int MIN_VALUE = 1;
    public static final int MAX_VALUE = 9999;

    /// Grid size: `x` in `0..WIDTH`, `y` in `0..HEIGHT`, origin top-left.
    public static final int WIDTH = 2;
    public static final int HEIGHT = 3;

    private Cistercian() {}

    /// A grid point.
    public record Point(int x, int y) {
        Point mirrorX() {
            return new Point(WIDTH - x, y);
        }

        Point mirrorY() {
            return new Point(x, HEIGHT - y);
        }
    }

    /// A straight line between two grid points.
    public record Segment(Point from, Point to) {
        static Segment of(int x1, int y1, int x2, int y2) {
            return new Segment(new Point(x1, y1), new Point(x2, y2));
        }

        Segment map(UnaryOperator<Point> transform) {
            return new Segment(transform.apply(from), transform.apply(to));
        }
    }

    /// Contract-v1 geometry of one number.
    public record Numeral(List<Segment> segments) {
        public Numeral {
            segments = List.copyOf(segments);
        }

        /// Compact JSON, e.g. `{"segments":[[[1,0],[1,3]],[[1,0],[2,0]]]}`.
        public String toJson() {
            var json = new StringBuilder(32 + 24 * segments.size()).append("{\"segments\":[");
            for (int i = 0; i < segments.size(); i++) {
                Segment s = segments.get(i);
                if (i > 0) json.append(',');
                json.append("[[").append(s.from().x()).append(',').append(s.from().y())
                    .append("],[").append(s.to().x()).append(',').append(s.to().y()).append("]]");
            }
            return json.append("]}").toString();
        }
    }

    /// The five basic strokes, in units-quadrant coordinates.
    public enum Stroke {
        TOP(Segment.of(1, 0, 2, 0)),
        LOWER(Segment.of(1, 1, 2, 1)),
        DIAGONAL_DOWN(Segment.of(1, 0, 2, 1)),
        DIAGONAL_UP(Segment.of(1, 1, 2, 0)),
        OUTER(Segment.of(2, 0, 2, 1)); // detached from the stem

        private final Segment units;

        Stroke(Segment units) {
            this.units = units;
        }
    }

    /// Decimal places, each with the transform that moves a units stroke into its quadrant.
    public enum Place {
        UNITS(1, p -> p),
        TENS(10, Point::mirrorX),
        HUNDREDS(100, Point::mirrorY),
        THOUSANDS(1000, p -> p.mirrorX().mirrorY());

        private final int weight;
        private final UnaryOperator<Point> transform;

        Place(int weight, UnaryOperator<Point> transform) {
            this.weight = weight;
            this.transform = transform;
        }

        int digitOf(int n) {
            return n / weight % 10;
        }
    }

    public static final Segment STEM = Segment.of(1, 0, 1, 3);

    /// Strokes that make up a digit (empty for 0).
    public static Set<Stroke> strokes(int digit) {
        return switch (digit) {
            case 0 -> EnumSet.noneOf(Stroke.class);
            case 1 -> EnumSet.of(Stroke.TOP);
            case 2 -> EnumSet.of(Stroke.LOWER);
            case 3 -> EnumSet.of(Stroke.DIAGONAL_DOWN);
            case 4 -> EnumSet.of(Stroke.DIAGONAL_UP);
            case 5 -> EnumSet.of(Stroke.TOP, Stroke.DIAGONAL_UP);
            case 6 -> EnumSet.of(Stroke.OUTER);
            case 7 -> EnumSet.of(Stroke.TOP, Stroke.OUTER);
            case 8 -> EnumSet.of(Stroke.LOWER, Stroke.OUTER);
            case 9 -> EnumSet.of(Stroke.TOP, Stroke.LOWER, Stroke.OUTER);
            default -> throw new IllegalArgumentException("not a digit: " + digit);
        };
    }

    /// Encode `n` (1..9999) as the stem plus each digit's strokes in its quadrant.
    public static Numeral encode(int n) {
        if (n < MIN_VALUE || n > MAX_VALUE) {
            throw new IllegalArgumentException(n + " is outside " + MIN_VALUE + ".." + MAX_VALUE);
        }
        List<Segment> segments = new ArrayList<>();
        segments.add(STEM);
        for (Place place : Place.values()) {
            for (Stroke stroke : strokes(place.digitOf(n))) {
                segments.add(stroke.units.map(place.transform));
            }
        }
        return new Numeral(segments);
    }
}
