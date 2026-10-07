"""Tests for the deck build and the generated artifacts.

Standard library only (``python3 -m unittest``); no third-party test runner, to
match the skill's zero-dependency promise.
"""

import subprocess
import sys
import unittest

from helpers import REPO, DeckTestCase

TITLE_SLIDE = """<section class="slide slide--title">
  <h1 class="display">Hello</h1>
</section>
"""


class NewDeckTests(DeckTestCase):
    def test_new_deck_starts_empty_and_configured(self):
        deck = self.make_deck({}, title="Résultats", lang="fr", motion="lively")
        self.assertEqual(list((deck / "slides").glob("*.html")), [])
        config = (deck / "deck.config.json").read_text(encoding="utf-8")
        self.assertIn('"title": "Résultats"', config)
        self.assertIn('"motion": "lively"', config)

    def test_new_deck_refuses_a_folder_with_files(self):
        deck = self.make_deck({})
        proc = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "new_deck.py"), str(deck)],
            capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)

    def test_empty_deck_does_not_build(self):
        deck = self.make_deck({})
        proc = self.build(deck)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("no slides", proc.stderr)


class BuildTests(DeckTestCase):
    def test_builds_and_reports_slide_count(self):
        deck = self.make_deck({"01-title.html": TITLE_SLIDE})
        proc = self.build(deck)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("1 slides", proc.stdout)
        self.assertNotIn("! ", proc.stderr)

    def test_only_used_components_are_bundled(self):
        deck = self.make_deck({
            "01-stats.html": '<section class="slide"><div class="stats"><div class="stat">'
                             '<p class="stat__value" data-count>42</p></div></div></section>',
        })
        html = self.build_ok(deck)
        self.assertIn(".stat--hero", html)                 # from components/stats.css
        self.assertNotIn("@keyframes pf-line-grow", html)  # components/timeline.css
        self.assertNotIn(".bars--vertical", html)          # components/bars.css

    def test_icons_are_inlined_and_unknown_ones_warned(self):
        deck = self.make_deck({
            "01-icons.html": '<section class="slide"><p><i data-icon="rocket"></i> '
                             '<i data-icon="no-such-icon"></i></p></section>',
        })
        proc = self.build(deck)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn('unknown icon "no-such-icon"', proc.stderr)
        html = (deck / "index.html").read_text(encoding="utf-8")
        self.assertRegex(html, r'<i data-icon="rocket"><svg viewBox="0 0 24 24"[^>]*><path')

    def test_motion_none_leaves_the_toolkit_out(self):
        slide = {"01.html": TITLE_SLIDE}
        still = self.build_ok(self.make_deck(slide, motion="none"))
        lively = self.build_ok(self.make_deck(slide, motion="lively"))
        self.assertNotIn("@keyframes pf-rise", still)
        self.assertIn('motion="none"', still)
        self.assertIn("@keyframes pf-rise", lively)

    def test_bad_motion_level_is_refused(self):
        deck = self.make_deck({"01.html": TITLE_SLIDE})
        config = deck / "deck.config.json"
        config.write_text(config.read_text(encoding="utf-8").replace('"balanced"', '"wild"'),
                          encoding="utf-8")
        proc = self.build(deck)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('"motion" must be one of', proc.stderr)

    def test_title_and_attributes_are_escaped(self):
        deck = self.make_deck({"01.html": TITLE_SLIDE}, title='R&D <"2026">')
        html = self.build_ok(deck)
        self.assertIn("<title>R&amp;D &lt;\"2026\"&gt;</title>", html)

    def test_editable_blocks_and_notes_are_stamped(self):
        deck = self.make_deck({"01.html": """<section class="slide">
  <h2 class="title">Point</h2>
  <ul class="bullets"><li>One</li><li>Two</li></ul>
  <pre><code>not editable</code></pre>
  <div aria-hidden="true"><p>decor</p></div>
  <aside class="notes"><p>Say it.</p></aside>
</section>
"""})
        html = self.build_ok(deck)
        self.assertIn('data-pf-src="01.html"', html)
        self.assertEqual(html.count("data-pf-edit="), 3)    # the title and two bullets
        self.assertEqual(html.count("data-pf-notes="), 1)


class GeneratedArtifactTests(unittest.TestCase):
    def test_showcase_build_is_in_sync(self):
        proc = subprocess.run([sys.executable, "tools/build_showcase.py", "--check"],
                              cwd=REPO, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_skill_archive_is_in_sync(self):
        proc = subprocess.run([sys.executable, "tools/pack.py", "--check"],
                              cwd=REPO, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
