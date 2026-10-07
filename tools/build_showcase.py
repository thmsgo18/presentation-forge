#!/usr/bin/env python3
"""Build the showcase deck, ``examples/showcase/index.html``.

The showcase is a deck like any other - its own ``slides/``,
``deck.config.json`` and ``deck.css`` - built with the template's engine and
themes. It lives outside ``template/`` on purpose: a new deck starts empty, so
it is a first draft of the user's talk, never a reworded copy of this demo.

This copies the template into a temporary folder, lays the showcase files over
it, runs that folder's ``build.py`` and brings ``index.html`` back - exactly
what a real deck goes through. The result is the GitHub Pages live demo.

    python3 tools/build_showcase.py            # rebuild examples/showcase/index.html
    python3 tools/build_showcase.py --check    # verify the committed build is current

Standard library only.
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEMPLATE = REPO / "template"
SHOWCASE = REPO / "examples" / "showcase"
OUTPUT = SHOWCASE / "index.html"
# The showcase's own files; everything else comes from the template.
OVERLAY = ["slides", "assets", "deck.config.json", "deck.css"]
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "index.html")


def build_to(dest: Path) -> subprocess.CompletedProcess:
    """Assemble and build the showcase in ``dest``; return the build process."""
    shutil.copytree(TEMPLATE, dest, ignore=IGNORE, dirs_exist_ok=True)
    shutil.rmtree(dest / "slides", ignore_errors=True)
    for name in OVERLAY:
        src = SHOWCASE / name
        if src.is_dir():
            shutil.copytree(src, dest / name, ignore=IGNORE, dirs_exist_ok=True)
        elif src.is_file():
            shutil.copy2(src, dest / name)
    return subprocess.run([sys.executable, "build.py"], cwd=dest,
                          capture_output=True, text=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="verify examples/showcase/index.html is up to date; "
                         "exit non-zero if it is stale")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix="forge-showcase-") as tmp:
        proc = build_to(Path(tmp))
        sys.stderr.write(proc.stderr)
        if proc.returncode != 0:
            print("Showcase build failed.", file=sys.stderr)
            return proc.returncode
        built = (Path(tmp) / "index.html").read_bytes()

    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_bytes() != built:
            print("examples/showcase/index.html is stale.\n\n"
                  "Run: python3 tools/build_showcase.py", file=sys.stderr)
            return 1
        print("OK: examples/showcase/index.html is up to date.")
        return 0

    OUTPUT.write_bytes(built)
    print(proc.stdout.strip().replace("Built index.html", f"Built {OUTPUT.relative_to(REPO)}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
