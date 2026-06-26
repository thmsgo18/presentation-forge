"""Smoke tests for the deck build and the distributable artifacts.

Standard library only (``python3 -m unittest``); no third-party test runner, to
match the skill's zero-dependency promise. These guard the two generated files
that live in the repo - the bundled demo and the skill archive - against drift.
"""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEMPLATE = REPO / "template"
EXPECTED_SLIDES = 20


class BuildTests(unittest.TestCase):
    def _build_in_temp(self):
        """Build the template in a throwaway copy; return (dir, completed proc)."""
        tmp = Path(tempfile.mkdtemp(prefix="forge-build-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        shutil.copytree(TEMPLATE, tmp, dirs_exist_ok=True)
        (tmp / "index.html").unlink(missing_ok=True)
        proc = subprocess.run(
            [sys.executable, "build.py"],
            cwd=tmp, capture_output=True, text=True,
        )
        return tmp, proc

    def test_build_succeeds_with_expected_slides(self):
        tmp, proc = self._build_in_temp()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn(f"{EXPECTED_SLIDES} slides", proc.stdout)
        self.assertTrue((tmp / "index.html").is_file())

    def test_build_reports_no_missing_assets(self):
        _, proc = self._build_in_temp()
        self.assertNotIn("! missing", proc.stderr)
        self.assertNotIn("no <section", proc.stderr)

    def test_committed_demo_is_in_sync(self):
        tmp, _ = self._build_in_temp()
        built = (tmp / "index.html").read_bytes()
        committed = (TEMPLATE / "index.html").read_bytes()
        self.assertEqual(
            built, committed,
            "template/index.html is stale - run `python3 template/build.py` "
            "and commit the result.",
        )


class ArchiveTests(unittest.TestCase):
    def test_skill_archive_is_in_sync(self):
        proc = subprocess.run(
            [sys.executable, "tools/pack.py", "--check"],
            cwd=REPO, capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
