#!/usr/bin/env python3
"""Export a Presentation Forge deck to a clean PDF — one page per slide.

The built deck's own print button collapses every progressive-reveal
(``.fragment``) onto a single page and can fire mid-animation, which makes PDFs
of decks with step-by-step reveals unreliable. This renders each slide in its
**settled final state** — all fragments revealed, nothing animating — at the
exact design size, one slide per page.

How it works: it reads the already-built ``index.html`` (everything is inlined
there), rebuilds a *static* print document with one fixed-size page per slide and
all fragments forced visible, then renders that to PDF with a headless browser.
Because the print document has no script and no animation, the "final state" is
guaranteed by construction — there is nothing to wait for.

Rendering backend (hybrid, in order):
  1. a system Chrome / Chromium / Edge / Brave in headless mode (no install), then
  2. Playwright's bundled Chromium, if installed.

    python3 deck_to_pdf.py path/to/deck/            # builds if needed, -> deck.pdf
    python3 deck_to_pdf.py path/to/index.html       # render an existing build
    python3 deck_to_pdf.py path/to/deck -o talk.pdf # choose the output path
    python3 deck_to_pdf.py path/to/deck --build     # force a rebuild first

Standard library only (plus an optional system browser or Playwright).
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# --- Locating and (re)building the deck ------------------------------------


def resolve_index(target: Path, force_build: bool) -> Path:
    """Return the index.html to render, building from build.py when needed."""
    if target.is_file() and target.suffix.lower() in (".html", ".htm"):
        return target
    if not target.is_dir():
        raise SystemExit(f"error: not a deck folder or .html file: {target}")

    index = target / "index.html"
    build = target / "build.py"
    if force_build or not index.is_file():
        if build.is_file():
            print(f"Building deck: {build}")
            subprocess.run([sys.executable, str(build)], check=True)
        elif not index.is_file():
            raise SystemExit(
                f"error: no index.html and no build.py in {target}\n"
                "Build the deck first (python3 build.py)."
            )
    return index


# --- Turning the built deck into a static print document -------------------

PRINT_CSS = """
* {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
@page {{ size: {w}px {h}px; margin: 0; }}
html, body {{ margin: 0; padding: 0; background: #fff; }}
.pf-print-page {{
  position: relative; width: {w}px; height: {h}px; overflow: hidden;
  page-break-after: always; break-after: page;
}}
.pf-print-page:last-child {{ page-break-after: auto; break-after: auto; }}
/* Each slide fills its page. */
.pf-print-page > * {{
  position: absolute; inset: 0;
  visibility: visible !important; opacity: 1 !important;
}}
/* Final state: reveal every progressive fragment, hide presenter-only notes. */
.fragment {{ opacity: 1 !important; visibility: visible !important; }}
aside.notes {{ display: none !important; }}
"""


def _design_size(html: str):
    m = re.search(r"<deck-stage\b([^>]*)>", html, re.IGNORECASE)
    attrs = m.group(1) if m else ""
    w = re.search(r'\bwidth=["\'](\d+)', attrs)
    h = re.search(r'\bheight=["\'](\d+)', attrs)
    return (int(w.group(1)) if w else 1920, int(h.group(1)) if h else 1080)


def _head_styles(html: str) -> str:
    """All <style> blocks from <head> (engine base + theme), in order.
    Restricted to the head so the engine's <script> body is never captured."""
    head = re.split(r"</head>", html, maxsplit=1, flags=re.IGNORECASE)[0]
    blocks = re.findall(r"<style[^>]*>(.*?)</style>", head, re.DOTALL | re.IGNORECASE)
    return "\n".join(blocks)


def _slide_sections(html: str):
    """The raw HTML of each top-level <section> inside <deck-stage>.
    Depth-counted over <section>/</section> so slide contents are preserved
    verbatim (sections are not expected to nest, but this is robust if they do)."""
    m = re.search(r"<deck-stage\b[^>]*>(.*?)</deck-stage>", html,
                  re.DOTALL | re.IGNORECASE)
    inner = m.group(1) if m else html
    sections, depth, start = [], 0, None
    for tok in re.finditer(r"<section\b[^>]*>|</section\s*>", inner, re.IGNORECASE):
        if tok.group(0).lower().startswith("</"):
            depth -= 1
            if depth == 0 and start is not None:
                sections.append(inner[start:tok.end()])
                start = None
        else:
            if depth == 0:
                start = tok.start()
            depth += 1
    return sections


def build_print_html(index: Path) -> tuple[str, int, int, int]:
    html = index.read_text(encoding="utf-8")
    w, h = _design_size(html)
    styles = _head_styles(html)
    slides = _slide_sections(html)
    if not slides:
        raise SystemExit(f"error: no <section class=\"slide\"> found in {index}")
    pages = "\n".join(f'<div class="pf-print-page">{s}</div>' for s in slides)
    doc = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>{PRINT_CSS.format(w=w, h=h)}</style>
<style>{styles}</style>
</head>
<body>
{pages}
</body>
</html>
"""
    return doc, w, h, len(slides)


# --- Rendering backends -----------------------------------------------------

# Common executable names on PATH and macOS app-bundle locations.
CHROME_CANDIDATES = [
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
    "microsoft-edge", "microsoft-edge-stable", "brave-browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Arc.app/Contents/MacOS/Arc",
]


def find_chrome() -> str | None:
    env = os.environ.get("PRESENTATION_FORGE_CHROME") or os.environ.get("CHROME")
    if env and (shutil.which(env) or Path(env).is_file()):
        return env
    for cand in CHROME_CANDIDATES:
        if Path(cand).is_file():
            return cand
        found = shutil.which(cand)
        if found:
            return found
    return None


def render_with_chrome(chrome: str, print_html: Path, out: Path) -> bool:
    url = print_html.resolve().as_uri()
    with tempfile.TemporaryDirectory() as profile:
        base = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            f"--user-data-dir={profile}",
            "--no-pdf-header-footer",
            f"--print-to-pdf={out}",
            url,
        ]
        # --headless=new is Chrome 109+; retry with legacy --headless if needed.
        for headless in ("--headless=new", "--headless"):
            cmd = list(base)
            cmd[1] = headless
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode == 0 and out.is_file() and out.stat().st_size > 0:
                return True
        sys.stderr.write((proc.stderr or "").strip() + "\n")
    return False


def render_with_playwright(print_html: Path, out: Path, w: int, h: int) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    url = print_html.resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        page.pdf(path=str(out), width=f"{w}px", height=f"{h}px",
                 print_background=True, prefer_css_page_size=True,
                 margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        browser.close()
    return out.is_file() and out.stat().st_size > 0


# --- Main -------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target", help="deck folder, or a built index.html")
    ap.add_argument("-o", "--output", help="output PDF path")
    ap.add_argument("--build", action="store_true",
                    help="rebuild the deck (run build.py) before exporting")
    ap.add_argument("--keep-html", action="store_true",
                    help="keep the intermediate print HTML (for debugging)")
    args = ap.parse_args()

    index = resolve_index(Path(args.target), args.build)
    doc, w, h, n = build_print_html(index)

    out = Path(args.output) if args.output else index.parent / (
        (index.parent.name if index.parent.name not in ("", ".") else index.stem) + ".pdf")
    out = out.resolve()

    print_html = index.parent / "_print.html"
    print_html.write_text(doc, encoding="utf-8")
    try:
        chrome = find_chrome()
        ok = False
        if chrome:
            print(f"Rendering {n} slides with {Path(chrome).name} -> {out.name}")
            ok = render_with_chrome(chrome, print_html, out)
            if not ok:
                print("  ! system browser failed; trying Playwright…",
                      file=sys.stderr)
        if not ok:
            ok = render_with_playwright(print_html, out, w, h)
            if ok:
                print(f"Rendered {n} slides with Playwright -> {out.name}")
        if not ok:
            raise SystemExit(
                "error: could not render the PDF.\n"
                "Install a Chromium browser (Chrome/Chromium/Edge/Brave), or:\n"
                "    pip install playwright && playwright install chromium\n"
                f"The print document was written to {print_html} for inspection."
            )
    finally:
        if not args.keep_html and print_html.exists():
            print_html.unlink()

    size_kb = out.stat().st_size / 1024
    print(f"Wrote {out} — {n} pages, {size_kb:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
