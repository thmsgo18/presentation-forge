#!/usr/bin/env python3
"""Build the distributable skill archive, ``dist/presentation-forge-skill.zip``.

That archive is what users upload to the Claude apps and the API (see the
README). It must contain exactly the skill's runtime - ``SKILL.md``, the
reference docs, the runtime scripts and the deck template - and nothing else: no
repo metadata (README, LICENSE, CI config), no generated demo build, no caches.

The build is deterministic: entries are sorted and timestamps fixed, so the same
sources always produce the same archive. That lets CI verify the committed zip
is in sync with the sources (``--check``) instead of trusting a human to repack.

    python3 tools/pack.py            # (re)build dist/presentation-forge-skill.zip
    python3 tools/pack.py --check    # verify the committed zip matches the sources

Standard library only.
"""

import argparse
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ARCHIVE = REPO / "dist" / "presentation-forge-skill.zip"

# The skill's name inside the archive: everything lives under this one folder so
# it unzips cleanly as a single skill directory.
PREFIX = "presentation-forge"

# What the skill needs at runtime. Everything else in the repo (README, LICENSE,
# .github, tools/, dist/) is repo scaffolding and stays out of the archive.
INCLUDE = ["SKILL.md", "reference", "scripts", "template"]

# Never ship: caches, OS/editor cruft, and the generated demo build (each deck
# regenerates its own index.html).
EXCLUDE_NAMES = {".DS_Store"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".swp"}
EXCLUDE_DIRS = {"__pycache__"}
EXCLUDE_PATHS = {"template/index.html"}

# A fixed timestamp keeps the archive byte-stable across machines and clocks.
ZIP_DATE = (1980, 1, 1, 0, 0, 0)


def _excluded(rel: str, path: Path) -> bool:
    parts = set(Path(rel).parts)
    return (
        rel in EXCLUDE_PATHS
        or path.name in EXCLUDE_NAMES
        or path.suffix.lower() in EXCLUDE_SUFFIXES
        or bool(parts & EXCLUDE_DIRS)
    )


def members() -> list[tuple[str, Path]]:
    """(arcname, source path) for every file in the archive, sorted by arcname."""
    found: list[tuple[str, Path]] = []
    for entry in INCLUDE:
        root = REPO / entry
        paths = [root] if root.is_file() else sorted(root.rglob("*"))
        for path in paths:
            if not path.is_file():
                continue
            rel = path.relative_to(REPO).as_posix()
            if _excluded(rel, path):
                continue
            found.append((f"{PREFIX}/{rel}", path))
    return sorted(found)


def pack() -> Path:
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ARCHIVE, "w", zipfile.ZIP_DEFLATED) as zf:
        for arcname, path in members():
            info = zipfile.ZipInfo(arcname, date_time=ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, path.read_bytes())
    entries = len(members())
    print(f"Packed {ARCHIVE.relative_to(REPO)} - {entries} files, "
          f"{ARCHIVE.stat().st_size // 1024} KB")
    return ARCHIVE


def check() -> list[str]:
    """Differences between the committed archive's contents and the sources.

    Compares uncompressed file contents (not compressed bytes), so the check is
    stable across zlib versions and only flags real drift."""
    expected = {arc: path.read_bytes() for arc, path in members()}
    if not ARCHIVE.is_file():
        return [f"missing archive: {ARCHIVE.relative_to(REPO)} (run tools/pack.py)"]
    diffs: list[str] = []
    with zipfile.ZipFile(ARCHIVE) as zf:
        actual = set(zf.namelist())
        for arc in sorted(actual - expected.keys()):
            diffs.append(f"stale entry in archive (not in sources): {arc}")
        for arc in sorted(expected.keys() - actual):
            diffs.append(f"missing from archive: {arc}")
        for arc in sorted(expected.keys() & actual):
            if zf.read(arc) != expected[arc]:
                diffs.append(f"out of date in archive: {arc}")
    return diffs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="verify the committed archive matches the sources; "
                         "exit non-zero if it is stale")
    args = ap.parse_args()

    if args.check:
        diffs = check()
        if diffs:
            print("Skill archive is out of sync with the sources:", file=sys.stderr)
            for d in diffs:
                print(f"  - {d}", file=sys.stderr)
            print("\nRun: python3 tools/pack.py", file=sys.stderr)
            return 1
        print(f"OK: {ARCHIVE.relative_to(REPO)} is in sync with the sources.")
        return 0

    pack()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
