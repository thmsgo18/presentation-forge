"""Tests for theme packing/unpacking, including path-traversal hardening.

A ``.pfstyle.json`` is untrusted input (shared between people and conversations),
so ``unpack`` must never write outside the destination theme folder.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "theme_bundle.py"
THEME = REPO / "template" / "themes" / "ink-blue"


def _run(*args, cwd):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd, capture_output=True, text=True,
    )


class RoundTripTests(unittest.TestCase):
    def test_pack_then_unpack_restores_the_theme(self):
        tmp = Path(tempfile.mkdtemp(prefix="forge-theme-"))
        self.addCleanup(lambda: __import__("shutil").rmtree(tmp, ignore_errors=True))
        bundle = tmp / "ink-blue.pfstyle.json"
        themes = tmp / "themes"
        themes.mkdir()

        packed = _run("pack", str(THEME), "-o", str(bundle), cwd=tmp)
        self.assertEqual(packed.returncode, 0, packed.stderr)
        self.assertTrue(bundle.is_file())

        unpacked = _run("unpack", str(bundle), str(themes), cwd=tmp)
        self.assertEqual(unpacked.returncode, 0, unpacked.stderr)
        self.assertTrue((themes / "ink-blue" / "tokens.css").is_file())


class PathTraversalTests(unittest.TestCase):
    def _attempt(self, files=None, name=None):
        tmp = Path(tempfile.mkdtemp(prefix="forge-evil-"))
        self.addCleanup(lambda: __import__("shutil").rmtree(tmp, ignore_errors=True))
        themes = tmp / "themes"
        themes.mkdir()
        bundle = tmp / "evil.pfstyle.json"
        payload = {
            "format": "presentation-forge-theme",
            "version": 1,
            "name": name or "evil",
            "files": files or {},
        }
        bundle.write_text(json.dumps(payload), encoding="utf-8")
        sentinel = tmp / "PWNED.txt"
        args = ["unpack", str(bundle), str(themes)]
        proc = _run(*args, cwd=tmp)
        return proc, sentinel

    def test_rejects_parent_traversal_in_file_key(self):
        proc, sentinel = self._attempt(
            files={"../../PWNED.txt": {"encoding": "utf-8", "text": "pwned"}}
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("unsafe", proc.stderr.lower())
        self.assertFalse(sentinel.exists(), "file escaped the theme folder")

    def test_rejects_traversal_in_theme_name(self):
        proc, _ = self._attempt(name="../evil")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("unsafe", proc.stderr.lower())


if __name__ == "__main__":
    unittest.main()
