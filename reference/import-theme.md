# Importing a theme

Build a **reusable** Presentation Forge theme from a brand or visual reference.
The goal is to capture the *design language* - palette, typography, logo,
background - into `themes/<name>/`, so any deck can adopt the look with
`"theme": "<name>"`. This is **not** a pixel-perfect clone of specific slides.

The reference can be a PowerPoint, image(s), a text description, or a combination
- plus an optional company logo. Handle whatever the user provides; if a logo is
mentioned but not attached, ask for the file.

`<skill-dir>` below is this skill's folder (where `SKILL.md` lives); `template/`
and `scripts/` are inside it.

## Step 1 - Derive the design language

Do this for **each** source the user gives.

### From a PowerPoint (`.pptx`)

Run the bundled extractor (pure standard library - no pip, no network):

```sh
python3 "<skill-dir>/scripts/pptx_theme.py" <file.pptx> --dump-media /tmp/pptx-media
```

It prints JSON with:
- `palette` - the theme colours (`dk1`, `lt1`, `dk2`, `lt2`, `accent1…6`, `hlink`),
- `fonts` - `major` (headings) and `minor` (body),
- `slide_size_px`,
- `suggested_tokens` - a rough first mapping to Presentation Forge tokens,
- `media` - embedded images with dimensions; the files are dumped to the given dir
  so you can inspect them (logos, backgrounds).

Start from `suggested_tokens`, then refine by eye.

### From image(s)

When the user gives a slide screenshot, a brand-guidelines page, or a moodboard,
**view the image** and read off:
- the **background** colour and the **main text** colour,
- the **accent** colour(s),
- the **typography feel** - serif vs sans, weight, character (geometric, humanist,
  condensed…),
- any **layout signature** worth echoing (hairline rules, generous margins, a
  colour band, a corner logo).

Pick concrete hex values. Reading by eye is fine because the user validates by
building; if they want exact dominant colours and Pillow happens to be available,
you may sample the image programmatically, but treat that as optional.

### From a text description

Translate brand words into concrete tokens:
- mood → light/dark `--bg` and `--ink` (e.g. "dark, sleek" → near-black bg, light
  ink);
- a named or implied brand colour → `--accent`;
- "modern geometric sans" / "classic serif" / "monospace accents" → font families
  with safe fallbacks;
- "airy", "minimal", "lots of whitespace" → larger spacing tokens.

State the choices you inferred so the user can correct them.

## Step 2 - Create the theme folder

Decide the deck folder first (scaffold a fresh one from `template/` if needed, per
the skill's Workflow 1). Then create `themes/<name>/` by **copying
`themes/ink-blue/`**:

```sh
cp -R "<deck>/themes/ink-blue" "<deck>/themes/<name>"
```

This keeps the proven `slides.css` block styling and the token contract intact -
you override the look, not the structure. Choose `<name>` from the brand (kebab-
case).

## Step 3 - Map the palette into `themes/<name>/tokens.css`

| Token             | Set from                                                     |
| ----------------- | ------------------------------------------------------------ |
| `--bg`            | main background (pptx `lt1`)                                  |
| `--bg-soft`       | a near-background tint (pptx `lt2`)                           |
| `--ink`           | body text (pptx `dk1`)                                        |
| `--accent`        | the brand colour (pptx `accent1`)                            |
| `--accent-deep`   | a darkened accent or near-black (pptx `dk2`)                 |
| `--accent-soft`   | a lighter accent                                             |
| `--accent-tint`   | a very light accent, ~8-12% alpha (e.g. `#RRGGBB14`)          |
| `--muted`         | a mid grey                                                    |
| `--rule`          | `--ink` at low alpha (hairlines)                             |

Keep the existing **type scale and spacing** unless the reference clearly calls
for different proportions - the ink-blue scale is tuned for the 1920×1080 canvas.

## Step 4 - Set the fonts

Put the heading/body families into the `--font-serif` / `--font-sans` (and
`--font-mono` if relevant) tokens. If the exact fonts aren't available, use the
closest **safe fallbacks** (the matching system fonts). When you have the real
font files, drop the `.woff2` into `themes/<name>/fonts/` and declare them with
`@font-face` in `fonts.css` so the built deck looks identical offline (the build
inlines them as base64).

## Step 5 - Integrate the logo

When the user provides a logo (or one is clearly the brand asset among the pptx
media):

1. **Place it** in `themes/<name>/logos/` (keep the original file; prefer a
   transparent PNG or an SVG).
2. **Wire it into `slides.css`** with `url(logos/<file>)` (relative to the theme
   folder - the build inlines it). Common, tasteful patterns:
   - **Small corner logo on every slide** - add a background image to `.slide`:
     ```css
     .slide {
       background-image: url(logos/logo.png);
       background-repeat: no-repeat;
       background-position: right 48px top 40px;   /* keep clear of content */
       background-size: 160px auto;
     }
     ```
   - **Larger logo on the title slide only** - scope it to `.slide--title`.
   - **Logo in a footer** - if the theme uses `.footer`, place it there instead.
3. **Mind legibility**: size it modestly (it should never compete with the title),
   keep it clear of text, and on dark variants (`slide--section`) use a light/
   monochrome version if the colour logo doesn't read. If only a colour logo
   exists and it clashes on dark slides, suppress it there
   (`.slide--section { background-image: none; }`).
4. Discard incidental pptx media (sample screenshots, content icons) - only the
   real brand mark is the logo.

## Step 6 - Backgrounds (optional)

If the reference implies a background image or texture (distinct from the logo),
place it in `themes/<name>/images/` and apply it to `slide--title` /
`slide--section` (or all slides) - tastefully, never so busy that text becomes
hard to read. Add an overlay/tint if needed to preserve contrast.

## Step 7 - Activate, verify, report

1. Set `"theme": "<name>"` in `deck.config.json`.
2. `python3 build.py` and open the result.
3. Check a **title** slide, a **content** slide, and a **`slide--section`**
   against the reference; tune `tokens.css` (and the logo placement) until the
   feel matches and text stays legible.
4. **Report** the colours and fonts you chose, where the logo was placed, and any
   assumptions (substituted fonts, inferred brand colour, which media you treated
   as the logo) so the user can correct them.

## Notes

- Because every theme defines the same tokens and styles the same slide classes,
  the new theme immediately works with any existing deck.
- For a `.pptx`, this reads its theme/master design, not the content of its sample
  slides.
- Clean up any `/tmp/pptx-media` you created.
