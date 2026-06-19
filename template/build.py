#!/usr/bin/env python3
"""Bundle the deck into a single, self-contained index.html.

Reads the slides (one file per slide in ``slides/``), the engine and the theme,
and inlines everything - script, styles, and images as base64 data URIs - into
one portable ``index.html`` you can double-click, email, or host anywhere. No
build tools, no third-party packages: just the Python standard library.

    python3 build.py            # build once -> index.html
    python3 build.py --watch    # rebuild whenever a source file changes
    python3 build.py --open     # build, then open the result in the browser

Sources you edit:
    slides/*.html       one <section class="slide"> per file (order = filename)
    themes/<name>/      the look (chosen in deck.config.json)
    deck.config.json    title, size, transition, theme
"""

import argparse
import base64
import json
import mimetypes
import re
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "deck.config.json"
OUTPUT = ROOT / "index.html"

# Matches url(...) inside CSS, a /* ... */ CSS comment, and <img ... src="...">.
CSS_URL_RE = re.compile(r"""url\(\s*["']?([^"')]+)["']?\s*\)""", re.IGNORECASE)
CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
IMG_RE = re.compile(r"""<img\b([^>]*?)\bsrc=["']([^"']+)["']([^>]*?)>""", re.IGNORECASE)


def is_local(ref: str) -> bool:
    """True for paths we should inline (skip http(s):, data:, #anchors)."""
    return not re.match(r"^(?:[a-z]+:|//|#)", ref, re.IGNORECASE)


def data_uri(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    mime = mime or "application/octet-stream"
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{payload}"


def inline_css_assets(css: str, css_dir: Path) -> str:
    """Replace url(...) references in a stylesheet with base64 data URIs."""

    def repl(match: re.Match) -> str:
        ref = match.group(1)
        if not is_local(ref):
            return match.group(0)
        asset = (css_dir / ref).resolve()
        if not asset.is_file():
            print(f"  ! missing CSS asset, left as-is: {ref}", file=sys.stderr)
            return match.group(0)
        return f"url({data_uri(asset)})"

    return CSS_URL_RE.sub(repl, css)


def inline_images(html: str, base: Path) -> str:
    """Replace <img src="..."> with base64 data URIs."""

    def repl(match: re.Match) -> str:
        before, src, after = match.group(1), match.group(2), match.group(3)
        if not is_local(src):
            return match.group(0)
        img = (base / src).resolve()
        if not img.is_file():
            print(f"  ! missing image, left as-is: {src}", file=sys.stderr)
            return match.group(0)
        return f"<img{before}src=\"{data_uri(img)}\"{after}>"

    return IMG_RE.sub(repl, html)


def read_css(path: Path) -> str:
    # Drop comments first so commented-out url() examples aren't treated as real
    # assets (and to keep the bundle lean).
    css = CSS_COMMENT_RE.sub("", path.read_text(encoding="utf-8"))
    return inline_css_assets(css, path.parent)


def slide_files() -> list[Path]:
    return sorted((ROOT / "slides").glob("*.html"))


def theme_css_files(theme: str) -> list[Path]:
    """The theme's stylesheets, in cascade order: fonts, then tokens, then the
    block styles, then any extra .css the author added."""
    theme_dir = ROOT / "themes" / theme
    order = ["fonts.css", "tokens.css", "slides.css"]
    ordered = [theme_dir / name for name in order if (theme_dir / name).is_file()]
    extra = sorted(p for p in theme_dir.glob("*.css") if p.name not in order)
    return ordered + extra


def source_files() -> list[Path]:
    """Every file whose change should trigger a rebuild (for --watch)."""
    files = [CONFIG, ROOT / "engine" / "deck-stage.js", ROOT / "engine" / "base.css"]
    files += slide_files()
    files += [p for p in (ROOT / "themes").rglob("*") if p.is_file()]
    files += [p for p in (ROOT / "assets").rglob("*") if p.is_file()]
    return [f for f in files if f.exists()]


def build() -> Path:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    title = config.get("title", "Presentation")
    lang = config.get("lang", "en")
    theme = config.get("theme", "ink-blue")
    width = config.get("width", 1920)
    height = config.get("height", 1080)
    transition = config.get("transition", "fade")
    exit_hint = config.get("exit_hint", "Press Esc to exit full screen.")

    base_css = read_css(ROOT / "engine" / "base.css")
    theme_dir = ROOT / "themes" / theme
    if not theme_dir.is_dir():
        raise SystemExit(f"error: theme folder not found: {theme_dir}")
    parts = theme_css_files(theme)
    if not parts:
        raise SystemExit(f"error: no .css files in theme: {theme_dir}")
    # Each part's url() assets (fonts, backgrounds, logos) are inlined relative
    # to its own folder (themes/<name>/), so the bundle stays self-contained.
    theme_css = "\n".join(read_css(p) for p in parts)

    engine_js = (ROOT / "engine" / "deck-stage.js").read_text(encoding="utf-8")
    engine_js = engine_js.replace("</script>", "<\\/script>")

    slides = slide_files()
    if not slides:
        raise SystemExit("error: no slides found in slides/")
    parts = []
    for p in slides:
        text = p.read_text(encoding="utf-8").strip()
        # Lightweight author-contract check: each slide file should hold one
        # <section class="slide">. Warn (don't fail) so authoring stays forgiving.
        if 'class="slide' not in text and "class='slide" not in text:
            print(f"  ! {p.name}: no <section class=\"slide\"> found", file=sys.stderr)
        parts.append(inline_images(text, ROOT))
    slides_html = "\n".join(parts)

    html = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
<style>
{base_css}
</style>
<style>
{theme_css}
</style>
</head>
<body>
<deck-stage width="{width}" height="{height}" transition="{transition}" exit-hint="{exit_hint}">
{slides_html}
</deck-stage>
<script>
{engine_js}
</script>
</body>
</html>
"""
    OUTPUT.write_text(html, encoding="utf-8")
    size_kb = OUTPUT.stat().st_size / 1024
    print(f"Built {OUTPUT.name} - {len(slides)} slides, {size_kb:.0f} KB")
    return OUTPUT


def watch() -> None:
    print("Watching for changes - Ctrl+C to stop.")
    mtimes: dict[Path, float] = {}
    try:
        while True:
            changed = False
            for f in source_files():
                m = f.stat().st_mtime
                if mtimes.get(f) != m:
                    mtimes[f] = m
                    changed = True
            if changed:
                try:
                    build()
                except SystemExit as e:
                    print(e, file=sys.stderr)
            time.sleep(0.4)
    except KeyboardInterrupt:
        print("\nStopped.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--watch", action="store_true", help="rebuild on every change")
    parser.add_argument("--open", action="store_true", help="open the result after building")
    args = parser.parse_args()

    out = build()
    if args.open:
        webbrowser.open(out.as_uri())
    if args.watch:
        watch()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
