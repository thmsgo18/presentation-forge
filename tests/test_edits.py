"""In-browser edits must survive a rebuild: build.py pulls them back into slides/.

The pure-Python tests fake what the engine saves (the data-pf-changed marks on
an edited index.html). The browser test drives the real engine in headless
Chrome - edit a block, rewrite the notes, save - and checks the slide files.
"""

import html
import re
import unittest

from helpers import DeckTestCase, load_script

TITLE = """<!-- 01 - Title, keep this comment -->
<section class="slide slide--title">
  <h1 class="display">Our Q3 <em>results</em></h1>
  <p class="lead">Revenue up, churn down.</p>
  <aside class="notes">
    <p>Open with the <strong>headline</strong>.</p>
  </aside>
</section>
"""
LIST = """<section class="slide">
  <h2 class="title">Three wins</h2>
  <ul class="bullets">
    <li>
      Revenue <i data-icon="trending-up"></i> up 18%
    </li>
    <li>Churn down to 4%</li>
  </ul>
</section>
"""


def mark(built: str, pattern: str, replacement: str) -> str:
    """Apply one fake browser edit to the built deck; it must hit exactly once."""
    new, count = re.subn(pattern, replacement, built, flags=re.S)
    assert count == 1, f"pattern matched {count} times: {pattern}"
    return new


class EditedDeck(DeckTestCase):
    """A two-slide deck, built, ready to be edited."""

    def setUp(self):
        self.deck = self.make_deck({"01-title.html": TITLE, "02-list.html": LIST},
                                   theme="ink-blue")
        self.built = self.build_ok(self.deck)

    def save(self, built: str) -> None:
        (self.deck / "index.html").write_text(built, encoding="utf-8")

    def slide(self, name: str) -> str:
        return (self.deck / "slides" / name).read_text(encoding="utf-8")


class PullTests(EditedDeck):
    def test_edit_lands_in_the_right_block_and_nothing_else_moves(self):
        self.save(mark(self.built,
                       r'(<h1 class="display" data-pf-edit="\w+")>Our Q3 <em>results</em>',
                       r'\1 data-pf-changed="">Our Q3 <em>record</em> results'))
        proc = self.build(self.deck)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Pulled 1 in-browser edit", proc.stdout)
        self.assertEqual(self.slide("01-title.html"),
                         TITLE.replace("<em>results</em>", "<em>record</em> results"))
        self.assertEqual(self.slide("02-list.html"), LIST)

    def test_icons_and_layout_survive_an_edit(self):
        self.save(mark(self.built, r'(<li data-pf-edit="\w+")(>\s*Revenue <i data-icon.*?</i>) up 18%',
                       r'\1 data-pf-changed=""\2 up 21%'))
        self.build_ok(self.deck)
        self.assertEqual(self.slide("02-list.html"), LIST.replace("up 18%", "up 21%"))

    def test_notes_changed_removed_and_added(self):
        built = mark(self.built, r'(<aside class="notes" data-pf-notes="(\w+)")>.*?</aside>',
                     r'\1 data-pf-changed=""><p>New &amp; better</p><ul><li>a</li></ul></aside>')
        built = mark(built, r'(<section class="slide" data-pf-src="02-list.html">.*?)(</section>)',
                     r'\1<aside class="notes" data-pf-changed=""><p>Fresh</p></aside>\2')
        self.save(built)
        self.build_ok(self.deck)
        self.assertIn("  <aside class=\"notes\">\n    <p>New &amp; better</p>\n    <ul>\n"
                      "      <li>a</li>\n    </ul>\n  </aside>", self.slide("01-title.html"))
        self.assertIn("  <aside class=\"notes\">\n    <p>Fresh</p>\n  </aside>\n</section>",
                      self.slide("02-list.html"))

        rebuilt = (self.deck / "index.html").read_text(encoding="utf-8")
        notes_hash = re.search(r'data-pf-notes="(\w+)"', rebuilt).group(1)
        rebuilt = mark(rebuilt, r'\s*<aside class="notes" data-pf-notes="%s">.*?</aside>' % notes_hash, "")
        rebuilt = mark(rebuilt, r'(data-pf-src="01-title.html")', r'\1 data-pf-notes-removed="%s"' % notes_hash)
        self.save(rebuilt)
        self.build_ok(self.deck)
        self.assertNotIn("aside", self.slide("01-title.html"))

    def test_a_block_changed_on_both_sides_is_kept_aside_not_overwritten(self):
        self.save(mark(self.built, r'(<h2 class="title" data-pf-edit="\w+")>Three wins',
                       r'\1 data-pf-changed="">Three big wins'))
        (self.deck / "slides" / "02-list.html").write_text(
            LIST.replace("Three wins", "Three solid wins"), encoding="utf-8")
        proc = self.build(self.deck)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("could not be merged", proc.stderr)
        self.assertIn("Three solid wins", self.slide("02-list.html"))
        self.assertIn("Three big wins",
                      (self.deck / "index.unmerged-edits.html").read_text(encoding="utf-8"))

    def test_pull_is_idempotent(self):
        self.save(mark(self.built, r'(<p class="lead" data-pf-edit="\w+")>Revenue up',
                       r'\1 data-pf-changed="">Revenue way up'))
        self.assertIn("Pulled 1", self.build(self.deck, "--pull").stdout)
        self.assertIn("already in slides", self.build(self.deck, "--pull").stdout)
        self.build_ok(self.deck)
        self.assertIn("No in-browser edits", self.build(self.deck, "--pull").stdout)
        self.assertEqual(self.slide("01-title.html").count("Revenue way up"), 1)


check_deck = load_script("check_deck")
BROWSER = check_deck.find_browser()

# Drives the real engine: edit mode on, one block retyped (the input event is
# what marks it), notes rewritten through the notes panel, then the exact HTML
# the Save button would write goes into a textarea for the test to read back.
DRIVER = """<script>
(function () {
  var d = document.querySelector("deck-stage");
  d._buildEditing();
  d._enterEditMode();
  var block = d.slides[1].querySelector(".title");
  block.textContent = "Three big wins";
  block.dispatchEvent(new Event("input"));
  d.show(0);
  d._openNotes();
  d.notesTA.value = "Lead with the number\\n- 18% up\\n- churn 4%";
  d._closeNotes();
  d._exitEditMode();
  var out = document.createElement("textarea");
  out.id = "pf-saved";
  out.textContent = d._serializeForSave();
  document.body.appendChild(out);
})();
</script>
"""


@unittest.skipUnless(BROWSER, "needs Chrome, Chromium, Edge or Brave")
class BrowserEditTests(EditedDeck):
    def test_engine_save_is_pulled_back(self):
        harness = self.deck / "harness.html"
        # Before the page's own </body> - the last one; the engine's code has others.
        head, _, tail = self.built.rpartition("</body>")
        harness.write_text(head + DRIVER + "</body>" + tail, encoding="utf-8")
        dom = check_deck.run_browser(BROWSER, harness.as_uri(), width=1920, height=1080)
        saved = re.search(r'<textarea id="pf-saved">(.*?)</textarea>', dom, re.S)
        self.assertIsNotNone(saved, "the engine did not produce a save")
        self.save(html.unescape(saved.group(1)))

        self.build_ok(self.deck)
        self.assertEqual(self.slide("02-list.html"), LIST.replace("Three wins", "Three big wins"))
        title = self.slide("01-title.html")
        self.assertIn("    <p>Lead with the number</p>\n    <ul>\n      <li>18% up</li>\n"
                      "      <li>churn 4%</li>\n    </ul>", title)
        self.assertTrue(title.startswith("<!-- 01 - Title, keep this comment -->\n"))


if __name__ == "__main__":
    unittest.main()
