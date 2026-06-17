/*
 * <deck-stage> — the presentation engine.
 *
 * A zero-dependency custom element that turns a list of <section> slides into
 * a navigable, auto-scaling deck.
 *
 * Three operating modes:
 *   windowed      default; shows the thumbnail rail on the left.
 *   full screen   single screen (or no Window Management permission);
 *                 rail hidden, controls fade on idle, Esc to exit.
 *   presenter     two or more screens detected; opens an audience window on
 *                 the secondary screen (full-screen slide only) and shows a
 *                 presenter sidebar (next-slide preview, notes, timer) here.
 *
 * Speaker notes authoring:
 *   <section class="slide">
 *     <h2 class="title">…</h2>
 *     <aside class="notes">Anything here — only visible in presenter mode.</aside>
 *   </section>
 *
 * Attributes on <deck-stage>:
 *   width / height   design canvas size (default 1920 × 1080)
 *   exit-hint        toast text shown on entering single-screen full screen
 *   no-rail          always hide the thumbnail rail
 */
(() => {
  "use strict";

  const DESIGN_W = 1920;
  const DESIGN_H = 1080;
  const IDLE_MS = 2500;
  const TOAST_MS = 2800;
  const DEFAULT_EXIT_HINT = "Press Esc to exit full screen.";

  const INTERACTIVE =
    'a[href], button, input, select, textarea, summary, label, ' +
    'video[controls], audio[controls], [role="button"], [onclick], [tabindex]';

  const ICONS = {
    prev:     '<svg viewBox="0 0 24 24"><path d="M15 6l-6 6 6 6"/></svg>',
    next:     '<svg viewBox="0 0 24 24"><path d="M9 6l6 6-6 6"/></svg>',
    expand:   '<svg viewBox="0 0 24 24"><path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M16 3h3a2 2 0 0 1 2 2v3"/><path d="M21 16v3a2 2 0 0 1-2 2h-3"/><path d="M3 16v3a2 2 0 0 0 2 2h3"/></svg>',
    compress: '<svg viewBox="0 0 24 24"><path d="M8 3v3a2 2 0 0 1-2 2H3"/><path d="M21 8h-3a2 2 0 0 1-2-2V3"/><path d="M3 16h3a2 2 0 0 1 2 2v3"/><path d="M16 21v-3a2 2 0 0 1 2-2h3"/></svg>',
  };

  const el = (tag, cls) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    return n;
  };

  const mkBtn = (cls, label, svg, onClick) => {
    const b = el("button", "pf-btn " + cls);
    b.type = "button";
    b.setAttribute("aria-label", label);
    b.title = label;
    b.innerHTML = svg;
    b.addEventListener("click", onClick);
    return b;
  };

  const pad2 = (n) => String(n).padStart(2, "0");
  const fsEl = () => document.fullscreenElement || document.webkitFullscreenElement || null;

  class DeckStage extends HTMLElement {
    connectedCallback() {
      if (this._ready) return;
      this._ready = true;

      this.designW = Number(this.getAttribute("width")) || DESIGN_W;
      this.designH = Number(this.getAttribute("height")) || DESIGN_H;
      this.exitHint = this.getAttribute("exit-hint") || DEFAULT_EXIT_HINT;
      this.style.setProperty("--design-w", this.designW + "px");
      this.style.setProperty("--design-h", this.designH + "px");

      this.slides = Array.from(this.children).filter((c) => c.nodeType === 1);

      this._buildRail();
      this._buildStage();
      this._buildControls();
      this.overlay = el("div", "pf-overlay");
      this.toast   = el("div", "pf-toast");
      this.append(this.overlay, this.toast);

      this.index = this._indexFromHash();
      this.show(this.index, { updateHash: false });
      this._layout();
      this._scaleThumbs();

      this._onResize = () => { this._layout(); this._scaleThumbs(); };
      this._onKey    = (e) => this._onKeyDown(e);
      this._onHash   = () => this.show(this._indexFromHash(), { updateHash: false });
      this._onMove   = () => this._markActive();
      this._onFs     = () => this._onFullscreenChange();

      window.addEventListener("resize",          this._onResize);
      window.addEventListener("keydown",         this._onKey);
      window.addEventListener("hashchange",      this._onHash);
      this.addEventListener("mousemove",         this._onMove);
      document.addEventListener("fullscreenchange",        this._onFs);
      document.addEventListener("webkitfullscreenchange",  this._onFs);
      this._bindTouch();
    }

    disconnectedCallback() {
      window.removeEventListener("resize",     this._onResize);
      window.removeEventListener("keydown",    this._onKey);
      window.removeEventListener("hashchange", this._onHash);
      document.removeEventListener("fullscreenchange",       this._onFs);
      document.removeEventListener("webkitfullscreenchange", this._onFs);
    }

    /* ------------------------------------------------------------------ */
    /* DOM construction                                                     */
    /* ------------------------------------------------------------------ */

    _buildStage() {
      this.stage  = el("div", "pf-stage");
      this.canvas = el("div", "pf-canvas");
      this.canvas.style.width  = this.designW + "px";
      this.canvas.style.height = this.designH + "px";
      this.slides.forEach((slide, i) => {
        slide.setAttribute("data-index", String(i));
        this.canvas.appendChild(slide);
      });
      this.stage.appendChild(this.canvas);
      this.appendChild(this.stage);
    }

    _buildRail() {
      this.rail   = el("div", "pf-rail");
      this.thumbs = this.slides.map((slide, i) => {
        const thumb = el("button", "pf-thumb");
        thumb.type  = "button";
        thumb.setAttribute("aria-label", "Go to slide " + (i + 1));

        const num   = el("span", "pf-thumb-num");
        num.textContent = String(i + 1);

        const frame = el("span", "pf-thumb-frame");
        const mini  = el("span", "pf-thumb-canvas");
        mini.style.width  = this.designW + "px";
        mini.style.height = this.designH + "px";

        const clone = slide.cloneNode(true);
        clone.removeAttribute("data-active");
        clone.removeAttribute("data-index");
        clone.removeAttribute("id");
        clone.querySelectorAll("[id]").forEach((n) => n.removeAttribute("id"));
        clone.querySelectorAll("aside.notes").forEach((n) => n.remove());

        mini.appendChild(clone);
        frame.appendChild(mini);
        thumb.append(num, frame);
        thumb.addEventListener("click", () => this.show(i));
        this.rail.appendChild(thumb);
        return thumb;
      });
      this.appendChild(this.rail);
    }

    _buildControls() {
      this.controls = el("div", "pf-controls");
      this.prevBtn  = mkBtn("pf-prev", "Previous slide", ICONS.prev,  () => this.prev());
      this.nextBtn  = mkBtn("pf-next", "Next slide",     ICONS.next,  () => this.next());
      this.fsBtn    = mkBtn("pf-fs",   "Full screen",    ICONS.expand, () => this.toggleFullscreen());
      this.controls.append(this.prevBtn, this.nextBtn, this.fsBtn);
      this.appendChild(this.controls);
    }

    /* ------------------------------------------------------------------ */
    /* Navigation                                                           */
    /* ------------------------------------------------------------------ */

    get count() { return this.slides.length; }
    _clamp(i)   { return Math.max(0, Math.min(this.count - 1, i)); }

    _indexFromHash() {
      const n = parseInt(location.hash.replace("#", ""), 10);
      return Number.isFinite(n) ? this._clamp(n - 1) : 0;
    }

    show(i, { updateHash = true } = {}) {
      this.index = this._clamp(i);

      this.slides.forEach((s, n) =>
        n === this.index ? s.setAttribute("data-active", "") : s.removeAttribute("data-active")
      );
      this.thumbs.forEach((t, n) => t.classList.toggle("is-active", n === this.index));

      const active = this.thumbs[this.index];
      if (active) {
        // scrollIntoView with options: Safari 15+. Fallback for older browsers.
        try { active.scrollIntoView({ block: "nearest" }); }
        catch (_) { active.scrollIntoView(false); }
      }

      this.overlay.textContent = `${this.index + 1} / ${this.count}`;
      this.prevBtn.disabled = this.index === 0;
      this.nextBtn.disabled = this.index === this.count - 1;

      this._markActive();
      this._syncAudience(this.index);
      this._updatePresenterView();

      if (updateHash) {
        const h = "#" + (this.index + 1);
        if (location.hash !== h) history.replaceState(null, "", h);
      }
    }

    next() { if (this.index < this.count - 1) this.show(this.index + 1); }
    prev() { if (this.index > 0)              this.show(this.index - 1); }

    _onKeyDown(e) {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      switch (e.key) {
        case "ArrowRight": case "PageDown": case " ":
          e.preventDefault(); this.next(); break;
        case "ArrowLeft": case "PageUp":
          e.preventDefault(); this.prev(); break;
        case "Home": e.preventDefault(); this.show(0);              break;
        case "End":  e.preventDefault(); this.show(this.count - 1); break;
        case "f": case "F":
          e.preventDefault(); this.toggleFullscreen(); break;
        case "Escape":
          // Intercept Esc in presenter mode before the browser acts on it.
          if (this._presenterActive) {
            e.preventDefault();
            e.stopImmediatePropagation();
            this.exitPresenterMode();
          }
          break;
        default:
          if (/^[1-9]$/.test(e.key)) { e.preventDefault(); this.show(Number(e.key) - 1); }
      }
    }

    _bindTouch() {
      if (!matchMedia("(hover: none)").matches) return;
      this.stage.addEventListener("click", (e) => {
        if (e.target.closest(INTERACTIVE)) return;
        const r = this.stage.getBoundingClientRect();
        if (e.clientX < r.left + r.width / 2) this.prev(); else this.next();
      });
    }

    /* ------------------------------------------------------------------ */
    /* Full screen & presenter mode                                        */
    /* ------------------------------------------------------------------ */

    toggleFullscreen() {
      if (this._presenterActive) {
        this.exitPresenterMode();
        return;
      }
      if (fsEl()) {
        (document.exitFullscreen || document.webkitExitFullscreen).call(document);
        return;
      }
      // Two or more screens → presenter mode; otherwise normal full screen.
      if (window.screen.isExtended) {
        // _openPresenter is async but we don't await it here so that
        // window.open() inside it runs before the first await, staying
        // within the user-gesture activation context (required by Safari
        // and Firefox to allow popups).
        this._openPresenter();
      } else {
        const el = this.stage;
        const req = el.requestFullscreen || el.webkitRequestFullscreen;
        if (req) req.call(el).catch(() => {});
      }
    }

    _onFullscreenChange() {
      if (this._presenterActive) return;
      // We check any fullscreen element — we are the only caller of
      // requestFullscreen so any active fullscreen is ours.
      const on = !!fsEl();
      this.classList.toggle("is-fullscreen", on);
      this.fsBtn.innerHTML = on ? ICONS.compress : ICONS.expand;
      const label = on ? "Exit full screen" : "Full screen";
      this.fsBtn.setAttribute("aria-label", label);
      this.fsBtn.title = label;
      if (on) this._showToast(this.exitHint);
      requestAnimationFrame(() => { this._layout(); this._scaleThumbs(); });
    }

    /* ---- Presenter mode --------------------------------------------- */

    async _openPresenter() {
      // 1. Open the popup SYNCHRONOUSLY (before any await) so that popup
      //    blockers in Safari and Firefox see the user-gesture context.
      const left = (window.screen.availLeft || 0) + window.screen.availWidth;
      const top  = window.screen.availTop  || 0;
      const w    = window.screen.availWidth;
      const h    = window.screen.availHeight;
      const features = `left=${left},top=${top},width=${w},height=${h},popup=1`;
      const win = window.open("about:blank", "_blank", features);

      if (!win) {
        // Popup blocked — fall back to single-screen full screen.
        const el = this.stage;
        const req = el.requestFullscreen || el.webkitRequestFullscreen;
        if (req) req.call(el).catch(() => {});
        return;
      }

      // 2. Now we can await — try to move the window to the secondary screen.
      if ("getScreenDetails" in window) {
        try {
          const details   = await window.getScreenDetails();
          const secondary = details.screens.find((s) => !s.isPrimary);
          if (secondary && !win.closed) {
            try { win.moveTo(secondary.availLeft, secondary.availTop); }   catch {}
            try { win.resizeTo(secondary.availWidth, secondary.availHeight); } catch {}
          }
        } catch { /* permission denied — the initial offset heuristic stands */ }
      }

      if (win.closed) return;

      // 3. Write the audience document.
      //    about:blank inherits the opener's origin, so document.write is
      //    same-origin and works across all browsers.
      win.document.write(this._buildAudienceHTML());
      win.document.close();
      win.addEventListener("beforeunload", () => {
        if (this._presenterActive) this.exitPresenterMode();
      });

      this._audienceWin     = win;
      this._presenterActive = true;
      this.classList.add("is-presenter");
      this._buildPresenterSidebar();
      this._syncAudience(this.index);
      this._updatePresenterView();
    }

    exitPresenterMode() {
      if (!this._presenterActive) return;
      this._presenterActive = false;
      this.classList.remove("is-presenter");

      const win = this._audienceWin;
      this._audienceWin = null;
      if (win && !win.closed) win.close();

      if (this._presenterSidebar) { this._presenterSidebar.remove(); this._presenterSidebar = null; }
      clearInterval(this._timerInterval);

      this.fsBtn.innerHTML = ICONS.expand;
      this.fsBtn.setAttribute("aria-label", "Full screen");
      this.fsBtn.title = "Full screen";

      requestAnimationFrame(() => { this._layout(); this._scaleThumbs(); });
    }

    _syncAudience(i) {
      if (this._audienceWin && !this._audienceWin.closed) {
        this._audienceWin.postMessage({ pfSlide: i }, "*");
      }
    }

    /* ---- Presenter sidebar ------------------------------------------ */

    _buildPresenterSidebar() {
      this._presenterSidebar = el("div", "pf-presenter-sidebar");

      // — Next slide section —
      const nextLabel = el("p", "pf-presenter-label");
      nextLabel.textContent = "Slide suivante";

      this._nextFrame  = el("div", "pf-next-frame");
      this._nextCanvas = el("div", "pf-next-canvas");
      this._nextCanvas.style.width  = this.designW + "px";
      this._nextCanvas.style.height = this.designH + "px";
      this._nextSlot   = el("div", "pf-next-slot");
      this._nextCanvas.appendChild(this._nextSlot);
      this._nextFrame.appendChild(this._nextCanvas);

      // — Notes section —
      const notesLabel = el("p", "pf-presenter-label");
      notesLabel.textContent = "Notes";
      this._notesEl = el("div", "pf-notes");

      // — Bar: controls + counter + timer —
      const bar = el("div", "pf-presenter-bar");

      this._presenterPrev  = mkBtn("", "Précédent",              ICONS.prev,     () => this.prev());
      this._presenterNext  = mkBtn("", "Suivant",                ICONS.next,     () => this.next());
      this._presenterCount = el("span", "pf-presenter-count");
      this._timerEl        = el("span", "pf-timer");
      const exitBtn        = mkBtn("", "Quitter la présentation", ICONS.compress, () => this.exitPresenterMode());

      bar.append(this._presenterPrev, this._presenterCount, this._presenterNext, this._timerEl, exitBtn);
      this._presenterSidebar.append(nextLabel, this._nextFrame, notesLabel, this._notesEl, bar);
      this.appendChild(this._presenterSidebar);

      // Timer
      this._timerStart = Date.now();
      this._updateTimer();
      this._timerInterval = setInterval(() => this._updateTimer(), 1000);

      requestAnimationFrame(() => this._scaleNextPreview());
    }

    _updatePresenterView() {
      if (!this._presenterActive || !this._presenterSidebar) return;

      // Next slide preview
      const next = this.slides[this.index + 1];
      this._nextSlot.innerHTML = "";
      if (next) {
        const clone = next.cloneNode(true);
        clone.removeAttribute("data-active");
        clone.querySelectorAll("aside.notes").forEach((n) => n.remove());
        this._nextSlot.appendChild(clone);
        this._nextCanvas.style.opacity = "1";
      } else {
        const msg = el("div", "pf-next-end");
        msg.textContent = "Fin de la présentation";
        this._nextSlot.appendChild(msg);
        this._nextCanvas.style.opacity = "0.4";
      }
      this._scaleNextPreview();

      // Notes
      const curr      = this.slides[this.index];
      const notesNode = curr && curr.querySelector("aside.notes");
      this._notesEl.innerHTML = notesNode
        ? notesNode.innerHTML
        : '<span class="pf-no-notes">Aucune note pour cette slide.</span>';

      // Counter + buttons state
      this._presenterCount.textContent   = `${this.index + 1} / ${this.count}`;
      this._presenterPrev.disabled       = this.index === 0;
      this._presenterNext.disabled       = this.index === this.count - 1;
    }

    _scaleNextPreview() {
      if (!this._nextFrame) return;
      const w = this._nextFrame.clientWidth;
      if (!w) return;
      const scale = w / this.designW;
      this._nextCanvas.style.transform       = `scale(${scale})`;
      this._nextCanvas.style.transformOrigin = "top left";
    }

    _updateTimer() {
      if (!this._timerEl) return;
      const s = Math.floor((Date.now() - this._timerStart) / 1000);
      this._timerEl.textContent = `${pad2(Math.floor(s / 60))}:${pad2(s % 60)}`;
    }

    /* ---- Audience window HTML ---------------------------------------- */

    _buildAudienceHTML() {
      // Collect CSS from all same-origin stylesheets (covers both dev and bundle).
      const css = Array.from(document.styleSheets).map((ss) => {
        try {
          return Array.from(ss.cssRules).map((r) => r.cssText).join("\n");
        } catch {
          // Cross-origin sheet — skip (fonts etc. are decorative).
          return "";
        }
      }).join("\n");

      const slidesHTML = this.slides.map((s) => {
        const c = s.cloneNode(true);
        c.removeAttribute("data-active");
        c.querySelectorAll("aside.notes").forEach((n) => n.remove());
        return c.outerHTML;
      }).join("\n");

      const W = this.designW, H = this.designH;
      return `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
html,body{margin:0;height:100%;overflow:hidden;background:#000}
.pf-canvas{position:fixed;left:50%;top:50%;transform-origin:center center;width:${W}px;height:${H}px}
.pf-canvas>*{position:absolute;inset:0;visibility:hidden;opacity:0;transition:opacity .35s ease}
.pf-canvas>[data-active]{visibility:visible;opacity:1}
aside.notes{display:none!important}
${css}
</style>
</head>
<body>
<div class="pf-canvas" id="c">${slidesHTML}</div>
<script>
(function(){
  var C=document.getElementById('c'), slides=C.querySelectorAll(':scope>*');
  var W=${W}, H=${H};
  function scale(){ C.style.transform='translate(-50%,-50%) scale('+Math.min(innerWidth/W,innerHeight/H)+')' }
  function show(i){ slides.forEach(function(s,n){ n===i?s.setAttribute('data-active',''):s.removeAttribute('data-active') }) }
  window.addEventListener('resize', scale);
  scale(); show(0);
  window.addEventListener('message', function(e){ if(e.data && typeof e.data.pfSlide==='number') show(e.data.pfSlide) });
  try{ document.documentElement.requestFullscreen() }catch(e){}
})();
<\/script>
</body>
</html>`;
    }

    /* ------------------------------------------------------------------ */
    /* Presentation mechanics                                               */
    /* ------------------------------------------------------------------ */

    _layout() {
      const w = this.stage.clientWidth;
      const h = this.stage.clientHeight;
      const scale = Math.min(w / this.designW, h / this.designH);
      this.canvas.style.transform = `translate(-50%, -50%) scale(${scale})`;
      if (this._presenterActive) this._scaleNextPreview();
    }

    _scaleThumbs() {
      if (!this.thumbs.length) return;
      const frame = this.thumbs[0].querySelector(".pf-thumb-frame");
      const w = frame.clientWidth;
      if (!w) return;
      const scale = w / this.designW;
      this.thumbs.forEach((t) => {
        t.querySelector(".pf-thumb-canvas").style.transform = `scale(${scale})`;
      });
    }

    _markActive() {
      this.classList.add("is-active-ui");
      clearTimeout(this._idleTimer);
      this._idleTimer = setTimeout(
        () => this.classList.remove("is-active-ui"),
        IDLE_MS
      );
    }

    _showToast(text) {
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
