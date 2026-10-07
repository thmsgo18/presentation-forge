"""Shared helpers for the test suite: make a throwaway deck and build it."""

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEMPLATE = REPO / "template"
SCRIPTS = REPO / "scripts"


def load_script(name: str):
    """Import scripts/<name>.py as a module (they are not a package)."""
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeckTestCase(unittest.TestCase):
    """A test that works on a fresh deck made with scripts/new_deck.py."""

    def make_deck(self, slides: dict[str, str], **options) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="forge-deck-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        deck = tmp / "deck"
        args = [sys.executable, str(SCRIPTS / "new_deck.py"), str(deck)]
        for key, value in options.items():
            args += [f"--{key}", value]
        proc = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        for name, markup in slides.items():
            (deck / "slides" / name).write_text(markup, encoding="utf-8", newline="\n")
        return deck

    def build(self, deck: Path, *extra: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "build.py", *extra], cwd=deck,
                              capture_output=True, text=True)

    def build_ok(self, deck: Path, *extra: str) -> str:
        proc = self.build(deck, *extra)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return (deck / "index.html").read_text(encoding="utf-8")
