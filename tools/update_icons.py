#!/usr/bin/env python3
"""Refresh the bundled icon set, ``template/engine/icons.json``.

The deck engine ships a curated set of Lucide icons (https://lucide.dev, ISC
licence) so a slide can say ``<i data-icon="rocket"></i>`` instead of hand-drawing
SVG. ``build.py`` inlines only the icons a deck actually uses, so the set can be
generous without making any deck heavier.

This script is maintenance-only (it needs network access): it downloads the
pinned Lucide release, keeps just the drawing elements of each icon (the outer
``<svg>`` is rebuilt by ``build.py``), and writes them as one sorted JSON file.

    python3 tools/update_icons.py

To add an icon, append its Lucide name to ICONS and rerun. Standard library only.
"""

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "template" / "engine" / "icons.json"
VERSION = "1.52.0"
URL = "https://unpkg.com/lucide-static@{version}/icons/{name}.svg"

ICONS = [
    # arrows and marks
    "arrow-right", "arrow-up-right", "arrow-down-right", "check", "x",
    "circle-check", "circle-x", "triangle-alert", "info", "circle-help", "plus",
    "minus",
    # ideas and goals
    "lightbulb", "rocket", "target", "flag", "sparkles", "zap", "brain",
    "puzzle", "trophy", "award", "star", "heart", "thumbs-up",
    # data and growth
    "trending-up", "trending-down", "chart-column", "chart-line", "chart-pie",
    "gauge", "percent", "scale",
    # people and organisations
    "user", "users", "handshake", "building-2", "briefcase", "graduation-cap",
    "megaphone", "message-circle", "mail", "phone", "bell",
    # money and commerce
    "euro", "dollar-sign", "coins", "piggy-bank", "shopping-cart", "package",
    "truck",
    # time and place
    "clock", "hourglass", "calendar", "map-pin", "globe",
    # tech
    "code", "terminal", "database", "server", "cloud", "cpu", "smartphone",
    "monitor", "wifi", "git-branch", "workflow", "layers", "settings",
    "wrench", "search", "link", "download", "refresh-cw", "play", "eye",
    "file-text", "image",
    # safety and nature
    "lock", "shield-check", "leaf", "recycle", "flask-conical", "book-open",
]

# Drawing elements only - the outer <svg> wrapper is rebuilt at build time.
SHAPE_RE = re.compile(r"<(?:path|circle|rect|line|polyline|polygon|ellipse)\b[^>]*/>")


def fetch(name: str) -> str:
    url = URL.format(version=VERSION, name=name)
    with urllib.request.urlopen(url, timeout=20) as resp:
        svg = resp.read().decode("utf-8")
    shapes = SHAPE_RE.findall(svg)
    if not shapes:
        raise ValueError(f"no drawable shapes found in {url}")
    return "".join(re.sub(r"\s+", " ", s).replace(" />", "/>") for s in shapes)


def main() -> int:
    icons = {}
    for name in sorted(set(ICONS)):
        try:
            icons[name] = fetch(name)
        except (urllib.error.URLError, ValueError) as e:
            print(f"error: {name}: {e}", file=sys.stderr)
            return 1
    payload = {
        "source": f"Lucide {VERSION} (https://lucide.dev) - see icons-LICENSE",
        "viewBox": "0 0 24 24",
        "icons": icons,
    }
    OUT.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8", newline="\n")
    print(f"Wrote {OUT.relative_to(REPO)} - {len(icons)} icons, "
          f"{OUT.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
