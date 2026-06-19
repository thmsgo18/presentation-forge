---
description: Build a reusable Presentation Forge theme from any reference — a PowerPoint (.pptx), an image (slide/brand mockup), or a text description — and optionally integrate a company logo. Output goes to themes/<name>/.
argument-hint: <.pptx | image | "style description"> [logo=path/to/logo.png] [theme-name]
---

Turn a brand or visual reference into a **reusable** Presentation Forge theme.
Read the **presentation-forge** skill first if it isn't loaded — it explains the
theme structure (`tokens.css`, `fonts.css`, `slides.css`, `fonts/`, `images/`,
`logos/`) and the token contract every theme must honour.

Goal: capture the *design language* (palette, typography, logo, background) into
`themes/<name>/`, so any deck can adopt the look with `"theme": "<name>"`. This
is not a pixel-perfect clone of specific slides.

## Inputs (any one — or a combination)

From **$ARGUMENTS**, figure out what the user gave you. Accept and handle all of:

- **A PowerPoint (`.pptx`)** — extract its theme palette, fonts and media.
- **An image** — a screenshot of an existing slide/deck, a brand guideline page,
  a moodboard, or a colour/style reference. Read it and derive the look by eye.
- **A text description** — e.g. "dark, teal accent, modern geometric sans, lots
  of whitespace, corporate". Map the wording to concrete tokens.
- **A logo** (optional, any of the above plus a logo image) — integrate it into
  the theme so it appears on slides.

If the user passed several (e.g. a description *and* a logo, or an image *and* a
logo), use them together. If nothing usable is given, ask which reference they
have. If a logo is mentioned but not provided, ask for the file.

## Steps

1. **Derive the design language** from each source provided:

   - **`.pptx`** → run the bundled stdlib extractor (no pip needed):
     ```sh
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pptx_theme.py" <file.pptx> --dump-media /tmp/pptx-media
     ```
     It prints `palette`, `fonts`, `slide_size_px`, a `suggested_tokens` mapping,
     and a `media` list (dumped for inspection).

   - **Image** → view it. Identify the **background** and **text** colours, the
     **accent(s)**, and the **typography feel** (serif/sans, weight, character).
     Note any layout signature worth echoing (rules, generous margins, a colour
     band). Pick concrete hex values; the user validates by building, so reading
     by eye is fine. If the user wants exact dominant colours and Pillow is
     available, you may sample it programmatically, but it's optional.

   - **Description** → translate the brand words into tokens: mood → light/dark
     `--bg`/`--ink`; named or implied brand colour → `--accent`; "modern sans" /
     "classic serif" → font families with safe fallbacks; "airy/minimal" →
     larger spacing tokens, etc. State the choices you inferred.

2. **Create the theme folder.** Decide the deck folder (scaffold a fresh one from
   the template if needed, per the skill), then make `themes/<name>/` by
   **copying `themes/ink-blue/`** — this keeps the proven `slides.css` and the
   token contract; you override the look, not the structure. Choose `<name>` from
   the brand or the user's argument.

3. **Map the palette into `themes/<name>/tokens.css`:**
   - `--bg` ← main background; `--bg-soft` ← a near-background tint.
   - `--ink` ← body text; `--accent-deep` ← a darkened accent or near-black.
   - `--accent` ← the brand colour; derive `--accent-soft` (lighter),
     `--accent-tint` (very light, ~8–12% alpha); `--muted` ← a mid grey;
     `--rule` ← `--ink` at low alpha.
   Keep the existing **type scale and spacing** unless the reference clearly calls
   for different proportions (it's tuned for 1920×1080).

4. **Set the fonts** in the `--font-serif` / `--font-sans` / `--font-mono`
   tokens. If the exact fonts aren't available, use safe fallbacks; when you have
   real font files, drop `.woff2` into `themes/<name>/fonts/` and declare them in
   `fonts.css` so the built deck looks identical offline.

5. **Integrate the logo** (when provided). Copy it into `themes/<name>/logos/`,
   then wire it into `slides.css` — a common pattern is a small logo pinned to a
   corner of every slide (e.g. via a `.slide` background-image or a `.footer`), or
   larger on the `slide--title`. Use `url(...)` relative to the theme folder;
   `build.py` inlines it. Respect transparency (PNG/SVG) and keep it from
   crowding the content. If the logo came from a `.pptx`'s media, pick the small
   transparent asset; discard incidental media (sample screenshots, icons).

6. **Handle reference backgrounds.** If the source implies a background image or
   texture (not the logo), place it in `themes/<name>/images/` and apply it to
   `slide--title` / `slide--section` (or all slides) tastefully — never so busy
   that text becomes hard to read.

7. **Activate & verify.** Set `"theme": "<name>"` in `deck.config.json`, run
   `python3 build.py`, and open the result. Check a title slide, a content slide,
   and a `slide--section` against the reference; tune `tokens.css` until the feel
   matches. **Report** the colours/fonts you chose, where the logo was placed, and
   any assumptions (substituted fonts, inferred brand colour) so the user can
   correct them.

## Notes

- Reusable by design: because every theme defines the same tokens and styles the
  same slide classes, the new theme immediately works with any existing deck.
- For a `.pptx`, this reads its theme/master design, not the content of its
  sample slides.
- Clean up any `/tmp/pptx-media` you created.
