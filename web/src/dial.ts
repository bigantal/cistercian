/**
 * A rolling digit wheel (0–9), like one drum of an old mechanical counter.
 *
 * Accessible as an ARIA spinbutton. It can be turned with the mouse wheel or
 * trackpad, by dragging (mouse or touch), by clicking the faded neighbouring
 * digits, or from the keyboard (arrows, PageUp/PageDown, Home/End, or typing
 * a digit). Increasing values roll in from below, as on an odometer.
 */

/** Wrap any integer into 0..9. */
export function wrapDigit(d: number): number {
  return ((d % 10) + 10) % 10;
}

/** Combine [thousands, hundreds, tens, units] into a number. */
export function digitsToNumber(digits: readonly number[]): number {
  return digits.reduce((total, d) => total * 10 + d, 0);
}

/** Split 0..9999 into [thousands, hundreds, tens, units]. */
export function numberToDigits(n: number): [number, number, number, number] {
  return [Math.floor(n / 1000) % 10, Math.floor(n / 100) % 10, Math.floor(n / 10) % 10, n % 10];
}

/** Scroll distance (in pixels) that turns the wheel by one step. */
export const WHEEL_STEP_PX = 40;

/**
 * Convert accumulated scroll into whole steps: returns [steps, remainder].
 * Positive deltaY (scrolling down) increases the digit.
 */
export function wheelSteps(accumulated: number, step = WHEEL_STEP_PX): [number, number] {
  const steps = Math.trunc(accumulated / step);
  return [steps, accumulated - steps * step];
}

export interface DialOptions {
  readonly label: string;
  readonly onChange: (digit: number) => void;
  readonly onActiveChange?: (active: boolean) => void;
}

const VISIBLE_OFFSET = 1; // the strip holds digits v-2..v+2; v-1..v+1 are visible

export class Dial {
  readonly element: HTMLElement;
  private readonly strip: HTMLElement;
  private readonly cells: HTMLElement[] = [];
  private value = 0;
  private pendingValue = 0;
  private wheelRemainder = 0;
  private animating = false;
  private dragStartY: number | null = null;
  private dragSteps = 0;
  private hovered = false;
  private focused = false;

  constructor(private readonly options: DialOptions) {
    this.element = document.createElement("div");
    this.element.className = "dial";
    this.element.tabIndex = 0;
    this.element.setAttribute("role", "spinbutton");
    this.element.setAttribute("aria-label", options.label);
    this.element.setAttribute("aria-valuemin", "0");
    this.element.setAttribute("aria-valuemax", "9");

    const viewport = document.createElement("div");
    viewport.className = "dial-window";
    this.strip = document.createElement("div");
    this.strip.className = "dial-strip";
    this.strip.setAttribute("aria-hidden", "true");
    for (let i = 0; i < 5; i++) {
      const cell = document.createElement("span");
      cell.className = "dial-cell";
      this.cells.push(cell);
      this.strip.append(cell);
    }
    viewport.append(this.strip);
    this.element.append(viewport);

    this.strip.addEventListener("transitionend", () => this.finishAnimation());
    this.element.addEventListener("keydown", (e) => this.onKey(e));
    this.element.addEventListener("wheel", (e) => this.onWheel(e), { passive: false });
    this.element.addEventListener("pointerdown", (e) => this.onPointerDown(e));
    this.element.addEventListener("pointermove", (e) => this.onPointerMove(e));
    this.element.addEventListener("pointerup", (e) => this.onPointerUp(e));
    this.element.addEventListener("pointercancel", () => (this.dragStartY = null));
    this.element.addEventListener("pointerenter", () => this.setActive("hover", true));
    this.element.addEventListener("pointerleave", () => this.setActive("hover", false));
    this.element.addEventListener("focus", () => this.setActive("focus", true));
    this.element.addEventListener("blur", () => this.setActive("focus", false));
    this.paint();
  }

  /** The wheel's value, including a roll that is still animating. */
  get digit(): number {
    return this.animating ? this.pendingValue : this.value;
  }

  /** Set the value from outside (no change event). Rolls if it moves by one and `animate` is set. */
  set(digit: number, animate = true): void {
    const target = wrapDigit(digit);
    const delta = wrapDigit(target - this.value);
    if (animate && delta === 1) this.roll(1, false);
    else if (animate && delta === 9) this.roll(-1, false);
    else if (delta !== 0) {
      this.finishAnimation();
      this.value = target;
      this.paint();
    }
  }

  /** Turn by `steps` and report the change. */
  step(steps: number): void {
    if (steps === 0) return;
    if (Math.abs(steps) === 1) this.roll(steps, true);
    else {
      this.finishAnimation();
      this.value = wrapDigit(this.value + steps);
      this.paint();
      this.options.onChange(this.value);
    }
  }

  private roll(direction: number, notify: boolean): void {
    this.finishAnimation();
    const reduceMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;
    const target = wrapDigit(this.value + direction);
    if (reduceMotion) {
      this.value = target;
      this.paint();
    } else {
      // Slide the strip one cell, then re-centre on the new value when the transition ends.
      this.animating = true;
      this.pendingValue = target;
      this.strip.classList.add("rolling");
      this.strip.style.setProperty("--offset", String(VISIBLE_OFFSET + direction));
      this.cells.forEach((cell, i) => cell.classList.toggle("current", i === 2 + direction));
      this.element.setAttribute("aria-valuenow", String(target));
      this.element.setAttribute("aria-valuetext", String(target));
    }
    if (notify) this.options.onChange(target);
  }

  private finishAnimation(): void {
    if (!this.animating) return;
    this.animating = false;
    this.value = this.pendingValue;
    this.paint();
  }

  private paint(): void {
    this.strip.classList.remove("rolling");
    this.strip.style.setProperty("--offset", String(VISIBLE_OFFSET));
    this.cells.forEach((cell, i) => {
      cell.textContent = String(wrapDigit(this.value + i - 2));
      cell.classList.toggle("current", i === 2);
    });
    this.element.setAttribute("aria-valuenow", String(this.value));
    this.element.setAttribute("aria-valuetext", String(this.value));
  }

  private onKey(e: KeyboardEvent): void {
    const steps: Record<string, number> = { ArrowUp: 1, ArrowDown: -1, PageUp: 3, PageDown: -3 };
    if (e.key in steps) {
      this.step(steps[e.key] ?? 0);
    } else if (e.key === "Home" || e.key === "End" || /^[0-9]$/.test(e.key)) {
      const target = e.key === "Home" ? 0 : e.key === "End" ? 9 : Number(e.key);
      const forward = wrapDigit(target - this.value);
      this.step(forward <= 5 ? forward : forward - 10); // shortest way round
    } else {
      return;
    }
    e.preventDefault();
  }

  private onWheel(e: WheelEvent): void {
    e.preventDefault();
    const pixels = e.deltaMode === 1 ? e.deltaY * 16 : e.deltaMode === 2 ? e.deltaY * 400 : e.deltaY;
    const [steps, remainder] = wheelSteps(this.wheelRemainder + pixels);
    this.wheelRemainder = remainder;
    // One step per event keeps fast flicks readable; the remainder carries over.
    if (steps !== 0) this.step(Math.sign(steps));
  }

  private cellHeight(): number {
    return this.cells[2]?.getBoundingClientRect().height || 32;
  }

  private onPointerDown(e: PointerEvent): void {
    this.dragStartY = e.clientY;
    this.dragSteps = 0;
    this.element.setPointerCapture(e.pointerId);
  }

  private onPointerMove(e: PointerEvent): void {
    if (this.dragStartY === null) return;
    // Dragging up reveals the larger digits below, like flicking a drum.
    const steps = Math.trunc((this.dragStartY - e.clientY) / this.cellHeight());
    if (steps !== this.dragSteps) {
      this.step(Math.sign(steps - this.dragSteps));
      this.dragSteps += Math.sign(steps - this.dragSteps);
    }
  }

  private onPointerUp(e: PointerEvent): void {
    if (this.dragStartY === null) return;
    const moved = Math.abs(this.dragStartY - e.clientY);
    this.dragStartY = null;
    if (moved < 4) {
      // A click: the faded digit above means one less, the one below one more.
      const rect = this.element.getBoundingClientRect();
      const third = (e.clientY - rect.top) / rect.height;
      if (third < 1 / 3) this.step(-1);
      else if (third > 2 / 3) this.step(1);
      this.element.focus();
    }
  }

  private setActive(kind: "hover" | "focus", on: boolean): void {
    const before = this.hovered || this.focused;
    if (kind === "hover") this.hovered = on;
    else this.focused = on;
    const after = this.hovered || this.focused;
    if (before !== after) this.options.onActiveChange?.(after);
  }
}
