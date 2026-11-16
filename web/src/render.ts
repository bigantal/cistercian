/**
 * SVG presentation of encoder output. Pure presentation: maps grid
 * coordinates to pixels and draws the segments it is given. It contains no
 * digit-to-glyph knowledge; that lives only in the encoder.
 */

import { GRID, type Numeral, type Segment } from "cistercian-encoder";

const SVG_NS = "http://www.w3.org/2000/svg";

export interface Layout {
  /** Pixels per grid unit. */
  readonly unit: number;
  /** Padding around the grid, in pixels. */
  readonly margin: number;
  /** Stroke width as a fraction of the unit (kept well below the 1-unit gap between motifs). */
  readonly stroke: number;
}

export const DEFAULT_LAYOUT: Layout = { unit: 60, margin: 24, stroke: 0.12 };

export interface PixelLine {
  readonly x1: number;
  readonly y1: number;
  readonly x2: number;
  readonly y2: number;
}

export function canvasSize(layout: Layout = DEFAULT_LAYOUT): { width: number; height: number } {
  return {
    width: GRID.width * layout.unit + 2 * layout.margin,
    height: GRID.height * layout.unit + 2 * layout.margin,
  };
}

export function toPixel(value: number, layout: Layout = DEFAULT_LAYOUT): number {
  return layout.margin + value * layout.unit;
}

export function toPixelLines(numeral: Numeral, layout: Layout = DEFAULT_LAYOUT): PixelLine[] {
  return numeral.segments.map(([[x1, y1], [x2, y2]]) => ({
    x1: toPixel(x1, layout),
    y1: toPixel(y1, layout),
    x2: toPixel(x2, layout),
    y2: toPixel(y2, layout),
  }));
}

function svgElement<K extends keyof SVGElementTagNameMap>(
  tag: K,
  attributes: Record<string, string | number>,
): SVGElementTagNameMap[K] {
  const element = document.createElementNS(SVG_NS, tag);
  for (const [name, value] of Object.entries(attributes)) element.setAttribute(name, String(value));
  return element;
}

export interface RenderOptions {
  /** Draw faint dots at every grid point (useful for inspecting geometry; off by default). */
  readonly showGrid?: boolean;
  /** Segments to emphasise on top of the glyph, e.g. one digit's strokes from the encoder. */
  readonly highlight?: readonly Segment[];
}

/** Replace the contents of `svg` with the numeral and an accessible title. */
export function renderNumeral(
  svg: SVGSVGElement,
  numeral: Numeral,
  label: string,
  layout: Layout = DEFAULT_LAYOUT,
  options: RenderOptions = {},
): void {
  const { width, height } = canvasSize(layout);
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.setAttribute("role", "img");
  svg.replaceChildren();

  const title = svgElement("title", {});
  title.textContent = label;
  svg.append(title);

  if (options.showGrid) {
    const dots = svgElement("g", { class: "grid-dots", "aria-hidden": "true" });
    for (let x = 0; x <= GRID.width; x++) {
      for (let y = 0; y <= GRID.height; y++) {
        dots.append(svgElement("circle", { cx: toPixel(x, layout), cy: toPixel(y, layout), r: layout.unit * 0.04 }));
      }
    }
    svg.append(dots);
  }

  const strokes = svgElement("g", {
    class: "strokes",
    "stroke-width": layout.unit * layout.stroke,
    "stroke-linecap": "round",
    "stroke-linejoin": "round",
  });
  for (const line of toPixelLines(numeral, layout)) {
    strokes.append(svgElement("line", { ...line }));
  }
  svg.append(strokes);

  if (options.highlight?.length) {
    const emphasis = svgElement("g", {
      class: "highlight",
      "stroke-width": layout.unit * layout.stroke,
      "stroke-linecap": "round",
      "stroke-linejoin": "round",
    });
    for (const line of toPixelLines({ segments: options.highlight }, layout)) {
      emphasis.append(svgElement("line", { ...line }));
    }
    svg.append(emphasis);
  }
}
