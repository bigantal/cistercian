import { decompose, encode, type Place } from "cistercian-encoder";
import { parseNumber } from "./input.ts";
import { renderNumeral } from "./render.ts";

const CORNERS: Record<Place, string> = {
  units: "upper right",
  tens: "upper left",
  hundreds: "lower right",
  thousands: "lower left",
};

function element<T extends HTMLElement | SVGElement>(id: string): T {
  const found = document.getElementById(id);
  if (!found) throw new Error(`missing #${id}`);
  return found as T;
}

const input = element<HTMLInputElement>("number");
const error = element<HTMLParagraphElement>("number-error");
const svg = element<SVGSVGElement>("glyph");
const table = element<HTMLTableSectionElement>("decomposition");
const json = element<HTMLPreElement>("json");

function cell(text: string): HTMLTableCellElement {
  const td = document.createElement("td");
  td.textContent = text;
  return td;
}

function show(raw: string): void {
  const parsed = parseNumber(raw);
  input.setAttribute("aria-invalid", String(!parsed.ok));
  // Keep the last valid result visible but dimmed, so it is not mistaken for the current input.
  document.body.classList.toggle("stale", !parsed.ok);
  if (!parsed.ok) {
    error.textContent = parsed.message;
    return;
  }
  error.textContent = "";

  const n = parsed.value;
  const numeral = encode(n);
  renderNumeral(svg, numeral, `Cistercian numeral for ${n}`);

  table.replaceChildren(
    ...decompose(n).map(({ place, digit, value }) => {
      const row = document.createElement("tr");
      row.classList.toggle("zero", digit === 0);
      row.append(cell(place), cell(CORNERS[place]), cell(String(digit)), cell(digit === 0 ? "nothing" : value.toLocaleString("en")));
      return row;
    }),
  );
  json.textContent = JSON.stringify(numeral);
}

input.addEventListener("input", () => show(input.value));
for (const button of document.querySelectorAll<HTMLButtonElement>("[data-example]")) {
  button.addEventListener("click", () => {
    input.value = button.dataset.example ?? "";
    show(input.value);
    input.focus();
  });
}
show(input.value);
