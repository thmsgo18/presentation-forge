/*
 * <deck-stage> — the presentation engine.
 *
 * A zero-dependency custom element that turns a list of <section> slides into
 * a navigable, auto-scaling deck. It is intentionally small and readable: the
 * slides are plain HTML you author by hand, this file only handles mechanics.
 *
 * What it does:
 *   - Auto-scaling: slides are authored on a fixed canvas (default 1920x1080)
 *     and scaled with `transform: scale()` to fit the viewport, letterboxed.
 *   - Navigation: Left/Right, PageUp/PageDown, Space, Home/End, digits 1-9.
 *     On touch screens, tapping the left/right half of the screen goes
 *     prev/next (taps on links and buttons are left alone).
 *   - Deep-linking: the current slide is mirrored to the URL hash (#3), so a
 *     reload or a shared link reopens on the same slide.
 *   - A small slide counter that fades out when idle.
 *   - Printing: see themes/base.css — `@media print` lays every slide out as
 *     its own page, so "Print -> Save as PDF" gives one page per slide.
 *
 * Usage:
 *   <link rel="stylesheet" href="themes/base.css">
 *   <link rel="stylesheet" href="themes/ink-blue.css">
 *   <deck-stage width="1920" height="1080">
 *     <section class="slide slide--title">...</section>
 *     <section class="slide">...</section>
 *   </deck-stage>
 *   <script src="engine/deck-stage.js"></script>
 *
 * Slides are the direct element children of <deck-stage>. The active slide
 * carries the `data-active` attribute; the others stay in the DOM (their
 * videos, iframes and form state are preserved) but are hidden via CSS.
 */
(() => {
  "use strict";

  const DESIGN_W = 1920;
  const DESIGN_H = 1080;
  const OVERLAY_IDLE_MS = 1800;

  // Slide-authored controls that should keep a tap instead of navigating.
  const INTERACTIVE =
    'a[href], button, input, select, textarea, summary, label, ' +
    'video[controls], audio[controls], [role="button"], [onclick], [tabindex]';

  class DeckStage extends HTMLElement {
    connectedCallback() {
      // Guard against the element being upgraded twice.
      if (this._ready) return;
      this._ready = true;

      this.designW = Number(this.getAttribute("width")) || DESIGN_W;
      this.designH = Number(this.getAttribute("height")) || DESIGN_H;
      this.style.setProperty("--design-w", this.designW + "px");
      this.style.setProperty("--design-h", this.designH + "px");

      // The authored slides are our direct element children. Move them onto a
      // fixed-size canvas that we then scale to fit the viewport.
      this.slides = Array.from(this.children).filter((el) => el.nodeType === 1);
      this.canvas = document.createElement("div");
      this.canvas.className = "pf-canvas";
      this.canvas.style.width = this.designW + "px";
      this.canvas.style.height = this.designH + "px";
      this.slides.forEach((slide, i) => {
        slide.setAttribute("data-index", String(i));
        this.canvas.appendChild(slide);
      });
      this.appendChild(this.canvas);

      // Slide counter overlay (e.g. "3 / 12").
      this.overlay = document.createElement("div");
      this.overlay.className = "pf-overlay";
      this.appendChild(this.overlay);

      this.index = this.indexFromHash();
      this.show(this.index, { updateHash: false });
      this.scaleToViewport();

      this._onResize = () => this.scaleToViewport();
      this._onKey = (e) => this.onKeyDown(e);
      this._onHash = () => this.show(this.indexFromHash(), { updateHash: false });
      window.addEventListener("resize", this._onResize);
      window.addEventListener("keydown", this._onKey);
      window.addEventListener("hashchange", this._onHash);
      this.bindTouch();
    }

    disconnectedCallback() {
      window.removeEventListener("resize", this._onResize);
      window.removeEventListener("keydown", this._onKey);
      window.removeEventListener("hashchange", this._onHash);
    }

    /* ---- navigation ---- */

    get count() {
      return this.slides.length;
    }

    clamp(i) {
      return Math.max(0, Math.min(this.count - 1, i));
    }

    indexFromHash() {
      const n = parseInt(location.hash.replace("#", ""), 10);
      return Number.isFinite(n) ? this.clamp(n - 1) : 0;
    }

    show(i, { updateHash = true } = {}) {
      this.index = this.clamp(i);
      this.slides.forEach((slide, n) => {
        if (n === this.index) slide.setAttribute("data-active", "");
        else slide.removeAttribute("data-active");
      });
      this.overlay.textContent = `${this.index + 1} / ${this.count}`;
      this.pokeOverlay();
      if (updateHash) {
        const hash = "#" + (this.index + 1);
        if (location.hash !== hash) history.replaceState(null, "", hash);
      }
    }

    next() {
      if (this.index < this.count - 1) this.show(this.index + 1);
    }

    prev() {
      if (this.index > 0) this.show(this.index - 1);
    }

    onKeyDown(e) {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      switch (e.key) {
        case "ArrowRight":
        case "PageDown":
        case " ":
          e.preventDefault();
          this.next();
          break;
        case "ArrowLeft":
        case "PageUp":
          e.preventDefault();
          this.prev();
          break;
        case "Home":
          e.preventDefault();
          this.show(0);
          break;
        case "End":
          e.preventDefault();
          this.show(this.count - 1);
          break;
        default:
          if (/^[1-9]$/.test(e.key)) {
            e.preventDefault();
            this.show(Number(e.key) - 1);
          }
      }
    }

    bindTouch() {
      if (!matchMedia("(hover: none)").matches) return;
      this.addEventListener("click", (e) => {
        if (e.target.closest(INTERACTIVE)) return;
        const half = window.innerWidth / 2;
        if (e.clientX < half) this.prev();
        else this.next();
      });
    }

    /* ---- presentation mechanics ---- */

    scaleToViewport() {
      const scale = Math.min(
        window.innerWidth / this.designW,
        window.innerHeight / this.designH
      );
      this.canvas.style.transform =
        `translate(-50%, -50%) scale(${scale})`;
    }

    pokeOverlay() {
      this.overlay.classList.add("is-visible");
      clearTimeout(this._overlayTimer);
      this._overlayTimer = setTimeout(
        () => this.overlay.classList.remove("is-visible"),
        OVERLAY_IDLE_MS
      );
    }
  }

  if (!customElements.get("deck-stage")) {
    customElements.define("deck-stage", DeckStage);
  }
})();
