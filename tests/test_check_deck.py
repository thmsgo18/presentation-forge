"""The visual check: it must catch real layout problems and save the images.

Needs a Chromium-family browser; skipped where there is none.
"""

import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import SCRIPTS, DeckTestCase, load_script

BROWSER = load_script("check_deck").find_browser()

FINE = """<section class="slide">
  <h2 class="title">A slide that fits.</h2>
  <ul class="bullets"><li>One idea.</li><li>Another.</li></ul>
</section>
"""
CROWDED = ("<section class=\"slide\">\n  <h2 class=\"title\">Far too much.</h2>\n"
           "  <ul class=\"bullets\">\n"
           + "".join(f"    <li>Point number {n}, which goes on for a while.</li>\n" for n in range(30))
           + "  </ul>\n</section>\n")
BROKEN_IMAGE = """<section class="slide">
  <h2 class="title">A picture.</h2>
  <img src="data:image/png;base64,bm90IGFuIGltYWdl" alt="">
</section>
"""


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"{path} is not a PNG"
    return struct.unpack(">II", data[16:24])


@unittest.skipUnless(BROWSER, "needs Chrome, Chromium, Edge or Brave")
class CheckDeckTests(DeckTestCase):
    def check(self, deck: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPTS / "check_deck.py"), str(deck), *args],
                              capture_output=True, text=True, timeout=300)

    def test_reports_overflow_and_broken_images(self):
        deck = self.make_deck({"01-fine.html": FINE, "02-crowded.html": CROWDED,
                               "03-image.html": BROKEN_IMAGE}, theme="ink-blue")
        self.build_ok(deck)
        proc = self.check(deck, "--no-shots")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("slide 2 (02-crowded.html)", proc.stdout)
        self.assertIn("edge by", proc.stdout)
        self.assertIn("slide 3 (03-image.html): image failed to load", proc.stdout)
        self.assertNotIn("slide 1 ", proc.stdout)

    def test_clean_deck_passes_and_saves_images(self):
        deck = self.make_deck({"01-fine.html": FINE, "02-fine.html": FINE})
        self.build_ok(deck)
        with tempfile.TemporaryDirectory() as out:
            proc = self.check(deck, "--slides", "2", "--out", out)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("no layout problems", proc.stdout)
            self.assertEqual(png_size(Path(out) / "slide-02.png"), (960, 540))
            self.assertEqual(png_size(Path(out) / "sheet.png")[0], 1920)
            self.assertFalse((Path(out) / "slide-01.png").exists())

    def test_unbuilt_deck_is_reported(self):
        deck = self.make_deck({"01-fine.html": FINE})
        proc = self.check(deck, "--no-shots")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("run build.py first", proc.stderr)


if __name__ == "__main__":
    unittest.main()
