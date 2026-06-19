---
description: Turn a PowerPoint (.pptx) into a reusable Presentation Forge HTML theme — extract its colours, fonts, logo and backgrounds into themes/<name>/.
argument-hint: <path/to/template.pptx> [theme-name] [target deck folder]
---

Recreate the *visual language* of a PowerPoint template as a reusable
Presentation Forge theme. Read the **presentation-forge** skill first if it
isn't loaded — it explains the theme structure (`tokens.css`, `fonts.css`,
`slides.css`, `fonts/`, `images/`, `logos/`) and the token contract every theme
must honour.

Goal: a **reusable theme**, not a pixel-perfect clone of specific slides. Capture
the palette, typography, logo and background so any deck can adopt the look by
setting `"theme": "<name>"`.

## Inputs

From **$ARGUMENTS**: the `.pptx` path, an optional theme name (default: a
kebab-case name from the file or brand), and an optional deck folder to install
the theme into. If the `.pptx` path is missing, ask for it. If no deck folder is
given, ask whether to add the theme to an existing deck or to a fresh copy of the
template.

## Steps

1. **Extract the design tokens** with the bundled stdlib extractor (no pip
   needed):

   ```sh
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pptx_theme.py" <file.pptx> --dump-media /tmp/pptx-media
   ```

   It prints JSON with `palette` (theme colours), `fonts` (major/minor),
   `slide_size_px`, a `suggested_tokens` mapping, and a `media` list; media files
   are dumped to the given dir for inspection.

2. **Locate the target theme folder.** Decide the deck folder (scaffold a fresh
   one from the template if needed, per the skill), then create
   `themes/<name>/` by **copying `themes/ink-blue/`** — this keeps the proven
   `slides.css` block styling and the token contract intact. You'll override the
   look, not rebuild the structure.

3. **Map the palette into `themes/<name>/tokens.css`.** Start from
   `suggested_tokens` and refine by eye:
   - `--bg` ← light background (`lt1`); `--bg-soft` ← `lt2` or a near-white tint.
   - `--ink` ← main text (`dk1`); `--accent-deep` ← `dk2` or a darkened accent.
   - `--accent` ← `accent1`; derive `--accent-soft` (lighter) and `--accent-tint`
     (very light, ~8–12% alpha) from it; `--muted` ← a mid grey/`dk2`; `--rule` ←
     `--ink` at low alpha.
   Keep the existing **type scale and spacing** unless the template clearly calls
   for different proportions — the ink-blue scale is tuned for 1920×1080.

4. **Set the fonts.** Put the major/minor font family names into the
   `--font-serif` / `--font-sans` (and `--font-mono` if relevant) tokens. If the
   exact fonts aren't bundled, list safe fallbacks (the matching system fonts)
   and, when you have the actual font files, drop `.woff2` into
   `themes/<name>/fonts/` and declare them in `fonts.css` so the built deck looks
   identical offline.

5. **Place the assets.** Inspect the dumped media and pick the **logo** (small,
   often transparent PNG) → `themes/<name>/logos/`, and any **background/texture**
   → `themes/<name>/images/`. Wire them into `slides.css` (e.g. a logo on title
   or every slide, a background on `slide--title` / `slide--section`) using
   `url(...)` relative to the theme folder — `build.py` inlines them. Discard
   incidental media (screenshots, icons from sample slides) that aren't part of
   the brand.

6. **Activate & verify.** Set `"theme": "<name>"` in `deck.config.json`, run
   `python3 build.py`, and open the result. Check the title slide, a content
   slide, and a `slide--section` against the source template; tune `tokens.css`
   until the feel matches. Report the colours/fonts you mapped and any
   assumptions (substituted fonts, which media you treated as the logo) so the
   user can correct them.

## Notes

- This reads only the template's theme/master design — it does not copy the
  content of the sample slides.
- Because every theme defines the same tokens and styles the same slide classes,
  the new theme immediately works with any existing deck.
- Clean up `/tmp/pptx-media` when done.
