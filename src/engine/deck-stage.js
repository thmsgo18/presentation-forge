/*
 * <deck-stage> — the presentation engine.
 *
 * A zero-dependency custom element that turns a list of <section> slides into
 * a navigable, auto-scaling deck. It is intentionally small and readable: the
 * slides are plain HTML you author by hand, this file only handles mechanics.
 *
 * What it does:
 *   - Auto-scaling: slides are authored on a fixed canvas (default 1920x1080)
 *     and scaled with `transform: scale()` to fit the stage area, letterboxed.
 *   - Navigation: Left/Right, PageUp/PageDown, Space, Home/End, digits 1-9,
 *     and on-screen prev/next buttons. On touch screens, tapping the left/right
 *     half of the stage goes prev/next (taps on controls are left alone).
 *   - Thumbnail rail (windowed only): a left-hand list of live, scaled clones
 *     of every slide — you see the real content. Click one to jump to it.
 *   - Full screen: a button (and the `f` key) toggles the browser Fullscreen
 *     API. On entering, a short toast reminds you to press Esc to leave. While
 *     full screen, the controls and cursor fade out when idle and come back on
 *     mouse move; the rail is hidden.
 *   - Deep-linking: the current slide is mirrored to the URL hash (#3).
 *   - A small slide counter, and printing (see themes/base.css).
 *
 * Usage:
 *   <link rel="stylesheet" href="themes/base.css">
 *   <link rel="stylesheet" href="themes/ink-blue.css">
 *   <deck-stage width="1920" height="1080" exit-hint="Press Esc to exit">
 *     <section class="slide slide--title">...</section>
 *     <section class="slide">...</section>
 *   </deck-stage>
 *   <script src="engine/deck-stage.js"></script>
 *
 * Attributes:
 *   width / height  the design canvas size (default 1920x1080)
 *   exit-hint       text of the toast shown when entering full screen
 *   no-rail         hide the thumbnail rail
 */
(() => {
  "use strict";

  const DESIGN_W = 1920;
  const DESIGN_H = 1080;
  const IDLE_MS = 2500; // how long controls stay up after the last mouse move
  const TOAST_MS = 2800; // how long the full-screen hint stays up
  const DEFAULT_EXIT_HINT = "Press Esc to exit full screen.";

  // Slide-authored controls that should keep a tap instead of navigating.
  const INTERACTIVE =
    'a[href], button, input, select, textarea, summary, label, ' +
    'video[controls], audio[controls], [role="button"], [onclick], [tabindex]';

  // Inline icons (Lucide-style), coloured via `currentColor`.
  const ICONS = {
    prev: '<svg viewBox="0 0 24 24"><path d="M15 6l-6 6 6 6"/></svg>',
    next: '<svg viewBox="0 0 24 24"><path d="M9 6l6 6-6 6"/></svg>',
    expand:
      '<svg viewBox="0 0 24 24"><path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M16 3h3a2 2 0 0 1 2 2v3"/><path d="M21 16v3a2 2 0 0 1-2 2h-3"/><path d="M3 16v3a2 2 0 0 0 2 2h3"/></svg>',
    compress:
      '<svg viewBox="0 0 24 24"><path d="M8 3v3a2 2 0 0 1-2 2H3"/><path d="M21 8h-3a2 2 0 0 1-2-2V3"/><path d="M3 16h3a2 2 0 0 1 2 2v3"/><path d="M16 21v-3a2 2 0 0 1 2-2h3"/></svg>',
  };

  const el = (tag, cls) => {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    return node;
  };

  const button = (cls, label, svg, onClick) => {
    const b = el("button", "pf-btn " + cls);
    b.type = "button";
    b.setAttribute("aria-label", label);
    b.title = label;
    b.innerHTML = svg;
    b.addEventListener("click", onClick);
    return b;
  };

  const fullscreenElement = () =>
    document.fullscreenElement || document.webkitFullscreenElement || null;

  class DeckStage extends HTMLElement {
    connectedCallback() {
      if (this._ready) return; // guard against double upgrade
      this._ready = true;

      this.designW = Number(this.getAttribute("width")) || DESIGN_W;
      this.designH = Number(this.getAttribute("height")) || DESIGN_H;
      this.exitHint = this.getAttribute("exit-hint") || DEFAULT_EXIT_HINT;
      this.style.setProperty("--design-w", this.designW + "px");
      this.style.setProperty("--design-h", this.designH + "px");

      // The authored slides are our direct element children.
      this.slides = Array.from(this.children).filter((c) => c.nodeType === 1);

      this.buildRail();
      this.buildStage();
      this.buildControls();
      this.overlay = el("div", "pf-overlay");
      this.toast = el("div", "pf-toast");
      this.append(this.overlay, this.toast);

      this.index = this.indexFromHash();
      this.show(this.index, { updateHash: false });
      this.layout();
      this.scaleThumbs();

      this._onResize = () => {
        this.layout();
        this.scaleThumbs();
      };
      this._onKey = (e) => this.onKeyDown(e);
      this._onHash = () => this.show(this.indexFromHash(), { updateHash: false });
      this._onMove = () => this.markActive();
      this._onFs = () => this.onFullscreenChange();
      window.addEventListener("resize", this._onResize);
      window.addEventListener("keydown", this._onKey);
      window.addEventListener("hashchange", this._onHash);
      this.addEventListener("mousemove", this._onMove);
      document.addEventListener("fullscreenchange", this._onFs);
      document.addEventListener("webkitfullscreenchange", this._onFs);
      this.bindTouch();
    }

    disconnectedCallback() {
      window.removeEventListener("resize", this._onResize);
      window.removeEventListener("keydown", this._onKey);
      window.removeEventListener("hashchange", this._onHash);
      document.removeEventListener("fullscreenchange", this._onFs);
      document.removeEventListener("webkitfullscreenchange", this._onFs);
    }

    /* ---- DOM construction ---- */

    buildStage() {
      // A fixed-size canvas, centred and scaled inside the stage area.
      this.stage = el("div", "pf-stage");
      this.canvas = el("div", "pf-canvas");
      this.canvas.style.width = this.designW + "px";
      this.canvas.style.height = this.designH + "px";
      this.slides.forEach((slide, i) => {
        slide.setAttribute("data-index", String(i));
        this.canvas.appendChild(slide);
      });
      this.stage.appendChild(this.canvas);
      this.appendChild(this.stage);
    }

    buildRail() {
      // A left column of live, scaled-down clones of each slide.
      this.rail = el("div", "pf-rail");
      this.thumbs = this.slides.map((slide, i) => {
        const thumb = el("button", "pf-thumb");
        thumb.type = "button";
        thumb.setAttribute("aria-label", "Go to slide " + (i + 1));

        const num = el("span", "pf-thumb-num");
        num.textContent = String(i + 1);

        const frame = el("span", "pf-thumb-frame");
        const mini = el("span", "pf-thumb-canvas");
        mini.style.width = this.designW + "px";
        mini.style.height = this.designH + "px";

        const clone = slide.cloneNode(true);
        clone.removeAttribute("data-active");
        clone.removeAttribute("data-index");
        clone.removeAttribute("id");
        clone.querySelectorAll("[id]").forEach((n) => n.removeAttribute("id"));

        mini.appendChild(clone);
        frame.appendChild(mini);
        thumb.append(num, frame);
        thumb.addEventListener("click", () => this.show(i));
        this.rail.appendChild(thumb);
        return thumb;
      });
      this.appendChild(this.rail); // first child = left column
    }

    buildControls() {
      this.controls = el("div", "pf-controls");
      this.prevBtn = button("pf-prev", "Previous slide", ICONS.prev, () =>
        this.prev()
      );
      this.nextBtn = button("pf-next", "Next slide", ICONS.next, () =>
        this.next()
      );
      this.fsBtn = button("pf-fs", "Full screen", ICONS.expand, () =>
        this.toggleFullscreen()
      );
      this.controls.append(this.prevBtn, this.nextBtn, this.fsBtn);
      this.appendChild(this.controls);
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
      this.thumbs.forEach((thumb, n) =>
        thumb.classList.toggle("is-active", n === this.index)
      );
      const active = this.thumbs[this.index];
      if (active && active.scrollIntoView) {
        active.scrollIntoView({ block: "nearest" });
      }
      this.overlay.textContent = `${this.index + 1} / ${this.count}`;
      this.prevBtn.disabled = this.index === 0;
      this.nextBtn.disabled = this.index === this.count - 1;
      this.markActive();
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
        case "f":
        case "F":
          e.preventDefault();
          this.toggleFullscreen();
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
      this.stage.addEventListener("click", (e) => {
        if (e.target.closest(INTERACTIVE)) return;
        const half = this.stage.getBoundingClientRect();
        if (e.clientX < half.left + half.width / 2) this.prev();
        else this.next();
      });
    }

    /* ---- full screen ---- */

    toggleFullscreen() {
      if (fullscreenElement()) {
        (document.exitFullscreen || document.webkitExitFullscreen).call(document);
      } else {
        (this.requestFullscreen || this.webkitRequestFullscreen).call(this);
      }
    }

    onFullscreenChange() {
      const on = fullscreenElement() === this;
      this.classList.toggle("is-fullscreen", on);
      this.fsBtn.innerHTML = on ? ICONS.compress : ICONS.expand;
      const label = on ? "Exit full screen" : "Full screen";
      this.fsBtn.setAttribute("aria-label", label);
      this.fsBtn.title = label;
      if (on) {
        this.showToast(this.exitHint);
        this.markActive();
      }
      // The rail toggles, so the stage changes size: re-fit on next frame.
      requestAnimationFrame(() => {
        this.layout();
        this.scaleThumbs();
      });
    }

    /* ---- presentation mechanics ---- */

    layout() {
      const w = this.stage.clientWidth;
      const h = this.stage.clientHeight;
      const scale = Math.min(w / this.designW, h / this.designH);
      this.canvas.style.transform = `translate(-50%, -50%) scale(${scale})`;
    }

    // Fit each thumbnail's 1920x1080 clone into its frame.
    scaleThumbs() {
      if (!this.thumbs.length) return;
      const frame = this.thumbs[0].querySelector(".pf-thumb-frame");
      const w = frame.clientWidth;
      if (!w) return; // rail hidden (full screen / narrow) — nothing to do
      const scale = w / this.designW;
      this.thumbs.forEach((thumb) => {
        thumb.querySelector(".pf-thumb-canvas").style.transform =
          `scale(${scale})`;
      });
    }

    // Reveal the controls (and cursor); they fade again after IDLE_MS.
    markActive() {
      if (!this.classList.contains("is-active-ui")) {
        this.classList.add("is-active-ui");
      }
      clearTimeout(this._idleTimer);
      this._idleTimer = setTimeout(
        () => this.classList.remove("is-active-ui"),
        IDLE_MS
      );
    }

    showToast(text) {
      if (!text) return;
      this.toast.textContent = text;
      this.toast.classList.add("is-visible");
      clearTimeout(this._toastTimer);
      this._toastTimer = setTimeout(
        () => this.toast.classList.remove("is-visible"),
        TOAST_MS
      );
    }
  }

  if (!customElements.get("deck-stage")) {
    customElements.define("deck-stage", DeckStage);
  }
})();
