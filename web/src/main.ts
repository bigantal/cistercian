import { decompose, digitSegments, encode, type Place } from "cistercian-encoder";
import { Dial, digitsToNumber, numberToDigits } from "./dial.ts";
import { parseNumber } from "./input.ts";
import { renderNumeral } from "./render.ts";

const CORNERS: Record<Place, string> = {
  units: "upper right",
  tens: "upper left",
  hundreds: "lower right",
  thousands: "lower left",
};

/** Most significant first, matching numberToDigits/digitsToNumber. */
const PLACES: readonly Place[] = ["thousands", "hundreds", "tens", "units"];

function element<T extends HTMLElement | SVGElement>(id: string): T {
  const found = document.getElementById(id);
  if (!found) throw new Error(`missing #${id}`);
  return found as T;
}

const stage = document.querySelector<HTMLElement>(".stage")!;
const input = element<HTMLInputElement>("number");
const error = element<HTMLParagraphElement>("number-error");
const dialMessage = element<HTMLParagraphElement>("dial-message");
const readout = element<HTMLParagraphElement>("dial-readout");
const svg = element<SVGSVGElement>("glyph");
const table = element<HTMLTableSectionElement>("decomposition");
const json = element<HTMLPreElement>("json");
const exampleButtons = [...document.querySelectorAll<HTMLButtonElement>("[data-example]")];
const viewButtons = [...document.querySelectorAll<HTMLButtonElement>(".view-switch [data-view]")];

/** The last valid number shown. */
let current = 1986;
/** Corner to emphasise (hovered/focused dial, or briefly after a turn). */
let activePlace: Place | null = null;
let flashPlace: Place | null = null;
let flashTimer: number | undefined;

function cell(text: string): HTMLTableCellElement {
  const td = document.createElement("td");
  td.textContent = text;
  return td;
}

/** Large read-only number for the dials view; leading zeros are shown faintly. */
function drawReadout(digits: readonly number[]): void {
  const place = activePlace ?? flashPlace;
  const firstSignificant = digits.findIndex((d) => d !== 0);
  readout.querySelectorAll<HTMLSpanElement>("span").forEach((span, i) => {
    span.textContent = String(digits[i] ?? 0);
    span.classList.toggle("leading-zero", firstSignificant === -1 || i < firstSignificant);
    span.classList.toggle("active", span.dataset.place === place);
  });
  const n = digitsToNumber(digits);
  readout.setAttribute("aria-label", n === 0 ? "0" : String(n));
}

function drawGlyph(): void {
  drawReadout(dials.length ? dials.map((d) => d.digit) : numberToDigits(current));
  const place = activePlace ?? flashPlace;
  const highlight = place ? digitSegments(numberToDigits(current)[PLACES.indexOf(place)] ?? 0, place) : [];
  renderNumeral(svg, encode(current), `Cistercian numeral for ${current}`, undefined, { highlight });
}

/** Show a valid number everywhere except the control it came from. */
function show(n: number, source: "input" | "dials" | "other" | "initial"): void {
  current = n;
  document.body.classList.remove("stale");
  error.textContent = "";
  dialMessage.textContent = "";
  input.setAttribute("aria-invalid", "false");
  if (source !== "input") input.value = String(n);
  if (source !== "dials") numberToDigits(n).forEach((d, i) => dials[i]?.set(d, source !== "initial"));
  for (const button of exampleButtons) {
    button.setAttribute("aria-pressed", String(String(n) === button.dataset.example));
  }

  drawGlyph();
  const numeral = encode(n);
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

/** Keep the last valid result visible but dimmed, so it is not mistaken for the current input. */
function showInvalid(target: HTMLElement, message: string): void {
  document.body.classList.add("stale");
  target.textContent = message;
  for (const button of exampleButtons) button.setAttribute("aria-pressed", "false");
}

// ------------------------------------------------------------------ dials

const dials: Dial[] = PLACES.map((place) => {
  const dial = new Dial({
    label: `${place[0]!.toUpperCase()}${place.slice(1)} digit`,
    onChange: () => {
      const n = digitsToNumber(dials.map((d) => d.digit));
      flashPlace = place;
      window.clearTimeout(flashTimer);
      flashTimer = window.setTimeout(() => {
        flashPlace = null;
        drawGlyph();
      }, 700);
      if (n === 0) {
        drawReadout([0, 0, 0, 0]);
        showInvalid(dialMessage, "There is no Cistercian zero — turn any wheel to start at 1.");
        input.value = "0";
        return;
      }
      show(n, "dials");
    },
    onActiveChange: (active) => {
      activePlace = active ? place : activePlace === place ? null : activePlace;
      if (!document.body.classList.contains("stale")) drawGlyph();
      else drawReadout(dials.map((d) => d.digit));
    },
  });
  document.querySelector(`.dial-slot[data-place="${place}"]`)?.prepend(dial.element);
  return dial;
});

// ------------------------------------------------------------------ type view

input.addEventListener("input", () => {
  const parsed = parseNumber(input.value);
  input.setAttribute("aria-invalid", String(!parsed.ok));
  if (parsed.ok) show(parsed.value, "input");
  else showInvalid(error, parsed.message);
});

for (const button of exampleButtons) {
  button.addEventListener("click", () => {
    show(Number(button.dataset.example), "other");
    input.focus();
  });
}

// ------------------------------------------------------------------ view switch

function setView(view: string): void {
  stage.dataset.view = view;
  for (const button of viewButtons) button.setAttribute("aria-pressed", String(button.dataset.view === view));
  // Leaving the type view with an invalid entry falls back to the last valid number.
  if (document.body.classList.contains("stale")) show(current, "other");
}

for (const button of viewButtons) {
  button.addEventListener("click", () => setView(button.dataset.view ?? "type"));
}

const initial = parseNumber(input.value);
show(initial.ok ? initial.value : current, "initial");
