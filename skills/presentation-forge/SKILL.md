---
name: presentation-forge
description: >-
  Build beautiful, self-contained HTML presentations (slide decks) with the
  Presentation Forge engine: one HTML file per slide, bundled into a single
  portable index.html with presenter mode, progressive reveal, and swappable
  themes. Use this whenever the user wants to create, design, write, or build a
  presentation, slide deck, talk, or "slides" as HTML or for the browser; wants
  a web-based or single-file shareable deck; mentions presentation-forge,
  deck-stage, or "slides as HTML"; wants to turn a topic, brief, outline, notes,
  or a document into slides (technical/IT talks AND any other subject); wants to
  recreate a PowerPoint or Keynote look as a reusable HTML theme; or wants to
  export an HTML deck to PDF (including decks with step-by-step reveals where the
  browser's own print is unreliable). This produces HTML decks, not native
  PowerPoint files; for editable .pptx output, use the pptx tool instead.
---

# Presentation Forge

Presentation Forge turns plain HTML into polished presentations. The author
writes **one HTML file per slide**; a tiny Python build step (`build.py`,
standard library only) bundles the slides, the engine, the chosen theme and all
images into a single **self-contained `index.html`** that opens by double-click,
emails cleanly, and works offline.

Three layers, always kept separate:

- **engine** (`engine/`) — the rendering logic: scaling, navigation, presenter
  mode, progressive reveal, print. **Never edit this** to change content or look.
- **theme** (`themes/<name>/`) — the look: colours, type, spacing, fonts, logos,
  backgrounds. Swap themes without touching slides.
- **content** (`slides/`) — the actual slides, one file each, ordered by name.

This skill is the shared foundation for three commands: **`/new-presentation`**
(author a deck from a brief), **`/import-template`** (turn a PowerPoint, an image
or a text description into a reusable theme), and **`/export-pdf`** (export a
clean PDF). You can also use it directly whenever the task is "make an HTML
presentation."

## Where the template lives

A ready-to-use deck scaffold ships with this plugin at:

```
${CLAUDE_PLUGIN_ROOT}/template/
```

It contains `engine/`, `themes/ink-blue/`, example `slides/`, `assets/`,
`build.py` and `deck.config.json`. If `$CLAUDE_PLUGIN_ROOT` is unset (you are
running from a local checkout of the repo rather than an installed plugin), the
template is the `template/` directory at the repository root — two levels up
from this skill (`skills/presentation-forge/` → repo root → `template/`).

Resolve it once at the start of any deck task:

```sh
ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
TEMPLATE="$ROOT/template"
```

In practice, just check `${CLAUDE_PLUGIN_ROOT}/template` first and fall back to
the repo's `template/` if that variable is empty.

## Creating a deck (core workflow)

1. **Pick a target directory** for the deck (ask the user, or default to a new
   folder named after the topic in the current working directory). Each deck is
   its own folder — never build inside the plugin's `template/`.

2. **Copy the template** into the target, contents and dotfiles included:

   ```sh
   mkdir -p "<target>"
   cp -R "$TEMPLATE/." "<target>/"
   rm -f "<target>/index.html"        # stale demo build; you'll regenerate it
   ```

3. **Set deck metadata** in `<target>/deck.config.json` (see *Configuration*).

4. **Write the slides** in `<target>/slides/`. Replace the example files with the
   real content — one `<section class="slide">` per file, named `01-…`, `02-…` so
   they order correctly. Follow the authoring contract below.

5. **Build**:

   ```sh
   python3 "<target>/build.py"        # -> <target>/index.html (self-contained)
   ```

   `build.py` must run with its own directory as the deck root, so either run it
   from inside `<target>` or pass its path as above (it resolves paths relative
   to its own location). Use `--open` to open the result, `--watch` to rebuild on
   save.

6. **Verify** the build printed `Built index.html — N slides` with the slide
   count you expect, and surface any `! missing image` / `no <section
   class="slide">` warnings it emitted.

## The slide authoring contract

Each file in `slides/` is exactly one slide. Keep the markup plain and lean on
the theme's classes — that is what keeps every slide visually consistent and lets
themes be swapped freely.

```html
<section class="slide">
  <h2 class="title">One clear point per slide.</h2>
  <ul class="bullets">
    <li>One idea per line.</li>
    <li>Short, parallel phrasing.</li>
  </ul>
  <aside class="notes">Speaker notes — shown only in presenter mode.</aside>
</section>
```

Slides are authored on a fixed **1920×1080** canvas; the engine scales it to any
screen, so always design against that fixed size and don't worry about
responsiveness.

### Slide variants

| Class                   | Use                                  |
| ----------------------- | ------------------------------------ |
| `slide`                 | standard content slide               |
| `slide slide--title`    | opening / hero slide                 |
| `slide slide--section`  | section divider (dark background)    |
| `slide slide--conclude` | closing slide                        |

### Content blocks (provided by the theme)

- `.eyebrow` — small uppercase kicker above a heading
- `.display` — largest heading (title slide)
- `h1` / `.title`, `h2` / `.subtitle`, `.lead` — headings and lead text
- `ul.bullets` — a bulleted list
- `.two-col` — a two-column grid (wrap two child blocks)
- `.card` — a boxed callout
- `blockquote` — a pull quote
- `pre > code` — code (escape `<`, `>`, `&` as `&lt; &gt; &amp;`)
- `.footer` — small footer text on a slide
- `.muted`, `.accent` — text-colour helpers (combine with other blocks)
- `aside.notes` — speaker notes, presenter-only, never shown to the audience

### Progressive reveal (fragments)

Add `class="fragment"` to any element to reveal it step by step on click (like
Beamer's `\pause`), instead of showing the whole slide at once:

```html
<ul class="bullets">
  <li class="fragment">First point</li>
  <li class="fragment">Second point</li>
</ul>
```

Each `→` reveals the next fragment, then advances to the next slide. The
presenter view shows `step 2/3`. Fragments are central to how this deck handles
PDF export — see *Exporting to PDF*.

### Images

Put a deck's content images in `assets/` and reference them with a path relative
to the deck root: `<img src="assets/diagram.png" alt="…" />`. `build.py` inlines
them as base64 so the built file stays a single portable artifact. Keep theme
assets (fonts, backgrounds, logos) inside the theme folder instead.

## Configuration (`deck.config.json`)

| Key              | Default        | Purpose                                       |
| ---------------- | -------------- | --------------------------------------------- |
| `title`          | `Presentation` | page title                                    |
| `lang`           | `en`           | document language (`fr`, `en`, …)             |
| `theme`          | `ink-blue`     | which `themes/<name>/` folder to use          |
| `width` `height` | `1920` `1080`  | design canvas size                            |
| `transition`     | `fade`         | `fade` · `slide` · `zoom`                     |
| `exit_hint`      | English string | toast shown when entering full screen         |

## Theming

A theme is a self-contained folder under `themes/`, split by concern:
`tokens.css` (the dials: colours, type scale, spacing, font-family names),
`fonts.css` (`@font-face` declarations), `slides.css` (how the blocks above are
styled), plus `fonts/`, `images/`, `logos/`. To create a new look, copy
`themes/ink-blue/` to `themes/<name>/`, edit `tokens.css` first, and set
`"theme": "<name>"` in `deck.config.json`. Every theme must define the same
token names and style the same slide classes, so switching a theme never breaks a
deck. To build a theme from a PowerPoint, an image or a description, use
**`/import-template`**.

## Exporting to PDF

The built deck has a print button, but the browser's print collapses every
`.fragment` onto a single page and can fire mid-animation — unreliable for decks
with progressive reveal. For a clean PDF, use the bundled script, which renders
each slide in its **settled final state** (all fragments revealed, animations
finished) at the exact design size, one slide per page:

```sh
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/deck_to_pdf.py" <deck-or-index.html> [-o out.pdf]
```

It prefers a system Chrome/Chromium/Edge/Brave and falls back to Playwright. The
**`/export-pdf`** command wraps this; see `scripts/deck_to_pdf.py --help`.

## Reference

For the full authoring guide (navigation, keyboard shortcuts, presenter mode,
printing details, deeper theming), read `${CLAUDE_PLUGIN_ROOT}/template/docs/writing-slides.md`
when you need detail beyond the contract above. Keep `SKILL.md` itself as the
quick contract; load the doc only when a task needs the specifics.

## Guardrails

- One `<section class="slide">` per file in `slides/`; the build warns if a file
  has none.
- Don't edit `engine/` to change content or styling — that's the theme's job.
- Don't build inside `template/`; always copy it into a per-deck folder first.
- Prefer the theme's classes over inline styles, so themes stay swappable.
