#!/usr/bin/env python3
"""Bundle a deck into a single, portable .html file.

This reads a deck's index.html and inlines everything it references —
stylesheets, scripts, images and CSS url() assets — into one self-contained
file you can email, host anywhere, or open with a double-click. No build tools
and no third-party packages: just the Python standard library.

    python3 build.py examples/starter/index.html
    python3 build.py examples/starter/index.html -o dist/talk.html

The source stays readable and split across files; the built file is the
portable artifact you share.
"""

import argparse
import base64
import mimetypes
import re
import sys
from pathlib import Path

# Matches a stylesheet <link>, capturing the href value.
LINK_RE = re.compile(
    r"""<link\b[^>]*\brel=["']stylesheet["'][^>]*\bhref=["']([^"']+)["'][^>]*>""",
    re.IGNORECASE,
)
# Matches a <script src="...">...</script> (assumed self-closing/empty body).
SCRIPT_RE = re.compile(
    r"""<script\b[^>]*\bsrc=["']([^"']+)["'][^>]*>\s*</script>""",
    re.IGNORECASE,
)
# Matches <img ... src="...">, capturing the whole tag and the src value.
IMG_RE = re.compile(r"""<img\b([^>]*?)\bsrc=["']([^"']+)["']([^>]*?)>""", re.IGNORECASE)
# Matches url(...) inside CSS.
CSS_URL_RE = re.compile(r"""url\(\s*["']?([^"')]+)["']?\s*\)""", re.IGNORECASE)


def is_local(ref: str) -> bool:
    """True for paths we should inline (skip http(s):, data:, #anchors)."""
    return not re.match(r"^(?:[a-z]+:|//|#)", ref, re.IGNORECASE)


def data_uri(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    mime = mime or "application/octet-stream"
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{payload}"


def inline_css_assets(css: str, css_dir: Path) -> str:
    """Replace url(...) references in a stylesheet with data URIs."""

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


def bundle(index: Path) -> str:
    base = index.parent
    html = index.read_text(encoding="utf-8")

    def inline_link(match: re.Match) -> str:
        href = match.group(1)
        if not is_local(href):
            return match.group(0)
        css_path = (base / href).resolve()
        if not css_path.is_file():
            print(f"  ! missing stylesheet: {href}", file=sys.stderr)
            return match.group(0)
        css = inline_css_assets(css_path.read_text(encoding="utf-8"), css_path.parent)
        print(f"  + inlined stylesheet {href}")
        return f"<style>\n{css}\n</style>"

    def inline_script(match: re.Match) -> str:
        src = match.group(1)
        if not is_local(src):
            return match.group(0)
        js_path = (base / src).resolve()
        if not js_path.is_file():
            print(f"  ! missing script: {src}", file=sys.stderr)
            return match.group(0)
        js = js_path.read_text(encoding="utf-8").replace("</script>", "<\\/script>")
        print(f"  + inlined script {src}")
        return f"<script>\n{js}\n</script>"

    def inline_img(match: re.Match) -> str:
        before, src, after = match.group(1), match.group(2), match.group(3)
        if not is_local(src):
            return match.group(0)
        img_path = (base / src).resolve()
        if not img_path.is_file():
            print(f"  ! missing image: {src}", file=sys.stderr)
            return match.group(0)
        print(f"  + inlined image {src}")
        return f"<img{before}src=\"{data_uri(img_path)}\"{after}>"

    html = LINK_RE.sub(inline_link, html)
    html = SCRIPT_RE.sub(inline_script, html)
    html = IMG_RE.sub(inline_img, html)
    return html


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("index", type=Path, help="path to the deck's index.html")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="output file (default: dist/<deck-folder>.html)",
    )
    args = parser.parse_args()

    index = args.index.resolve()
    if not index.is_file():
        print(f"error: not a file: {index}", file=sys.stderr)
        return 1

    output = args.output or Path("dist") / f"{index.parent.name}.html"
    output.parent.mkdir(parents=True, exist_ok=True)

    print(f"Bundling {index} ...")
    output.write_text(bundle(index), encoding="utf-8")
    size_kb = output.stat().st_size / 1024
    print(f"Done -> {output} ({size_kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
