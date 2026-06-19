---
description: Export a Presentation Forge deck to a clean PDF (one page per slide, all progressive reveals shown), reliable even for decks with step-by-step animations.
argument-hint: <deck folder | index.html> [-o output.pdf]
---

Export an HTML deck to PDF using the bundled renderer. Read the
**presentation-forge** skill if it isn't loaded — the *Exporting to PDF* section
explains why this exists: the deck's own print button collapses every
`.fragment` onto one page and can fire mid-animation, so it's unreliable for
decks with progressive reveal. This renders each slide in its **settled final
state** (all fragments revealed) at the design size, one slide per page.

## Input

From **$ARGUMENTS**: a deck folder (or a built `index.html`), plus an optional
`-o <output.pdf>`. If nothing is given, ask which deck to export (or infer it
from the deck the user is currently working on).

## Steps

1. Run the hybrid renderer (system Chrome/Chromium/Edge/Brave first, Playwright
   fallback). It builds the deck first if `index.html` is missing:

   ```sh
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/deck_to_pdf.py" <deck-or-index.html> [-o <out.pdf>]
   ```

   Pass `--build` to force a rebuild before exporting, `--keep-html` to keep the
   intermediate print document for debugging.

2. Report the output path and the page count it printed.

3. If it fails because no renderer is available, relay the script's guidance:
   install a Chromium-based browser, or `pip install playwright && playwright
   install chromium`. Don't fall back to the in-browser print button — that's the
   unreliable path this command exists to replace.

## Notes

- "Final state" is guaranteed by construction: the renderer builds a static,
  script-free print document with fragments forced visible, so there is no
  animation to wait on and nothing renders half-finished.
- For a deck whose fragments should appear as *separate* cumulative pages
  (Beamer-style build-up), say so — that's a different export mode than the
  default final-state output and would need a small extension to the script.
- Backgrounds and dark section slides are preserved (print colour adjustment is
  forced on).
