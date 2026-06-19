---
name: presentation-forge
description: >-
  Build beautiful, self-contained HTML presentations (slide decks) with the
  bundled Presentation Forge engine: one HTML file per slide, bundled into a
  single portable index.html with presenter mode, progressive reveal, and
  swappable themes. Use this whenever the user wants to create, design, write, or
  build a presentation, slide deck, talk, or "slides" as HTML or for the browser;
  wants a web-based or single-file shareable deck; wants to turn a topic, brief,
  outline, notes, or a document into slides (technical talks AND any other
  subject); or wants to recreate a brand/PowerPoint look as a reusable theme, from
  a .pptx, from image(s), or from a text description, optionally integrating a
  company logo. Produces HTML decks, not native PowerPoint files.
---

# Presentation Forge

Presentation Forge turns plain HTML into polished presentations. You write **one
HTML file per slide**; a tiny Python build step (`build.py`, standard library
only) bundles the slides, the engine, the chosen theme and all images into a
single **self-contained `index.html`** that opens by double-click, emails
cleanly, and works offline.

Everything needed ships **inside this skill**, so it works the same in Claude
Code, in the Claude apps, and via the API - anywhere Claude has a filesystem and
can run Python.

Three layers, always kept separate:

- **engine** (`template/engine/`) - rendering logic: scaling, navigation,
  presenter mode, progressive reveal. **Don't edit it** to change content or look.
- **theme** (`template/themes/<name>/`) - the look: colours, type, spacing, fonts,
  logos, backgrounds. Swap themes without touching slides.
- **content** (`slides/`) - the slides, one file each, ordered by name.

This skill supports two workflows, chosen from what the user asks:

1. **Create a presentation** - author a deck from a topic or brief.
2. **Import a theme** - build a reusable theme from a `.pptx`, image(s), or a
   description, with optional logo integration. See
   [`reference/import-theme.md`](reference/import-theme.md) for the full procedure.

## Where the engine lives

This skill bundles the deck scaffold in **`template/`**, a sibling of this
`SKILL.md`. It contains `engine/`, `themes/ink-blue/`, example `slides/`,
`assets/`, `build.py` and `deck.config.json`.

Resolve the skill's own directory first (it's wherever this `SKILL.md` was read
from), then treat `template/` as relative to it. A robust way to locate it:

```sh
SKILL_DIR="$(dirname "$(find . -name SKILL.md -path '*presentation-forge*' 2>/dev/null | head -1)")"
# or just use the directory you read this SKILL.md from
TEMPLATE="$SKILL_DIR/template"
```

In Claude Code the skill folder is known directly; in the Claude apps / API the
skill is unzipped into the working filesystem - in both cases `template/` sits
next to `SKILL.md`.

## Workflow 1 - Create a presentation

1. **Pick a target directory** for the deck (ask the user, or default to a new
   kebab-case folder named after the topic, in the current working directory).
   Each deck is its own folder - never build inside the skill's `template/`.

2. **Copy the template** into the target, contents and dotfiles included:

   ```sh
   mkdir -p "<target>"
   cp -R "$TEMPLATE/." "<target>/"
   rm -f "<target>/index.html"        # stale demo build; you'll regenerate it
   ```

3. **Configure** `<target>/deck.config.json`: `title`, `lang`, `theme` (see
   *Configuration*).

4. **Outline, then write the slides** in `<target>/slides/` - replace the example
   files with real content, one `<section class="slide">` per file, numbered
   `01-`, `02-`, … so they order correctly. Plan a tight arc:
   - `01-title.html` → `slide slide--title` with `.eyebrow`, `.display`, `.lead`.
   - an agenda slide for longer decks; `slide--section` dividers between parts.
   - content slides: **one idea per slide** - a strong `.title` plus a few
     `.bullets`, a `.two-col`, a `.card`, a `blockquote`, or a `pre>code` block.
     Vary the blocks so the deck breathes; avoid walls of text.
   - a `slide--conclude` closing slide.
   - `aside.notes` for speaker notes; `class="fragment"` to reveal points step by
     step when build-up helps. Follow the authoring contract below.

5. **Build**: `python3 build.py` run inside `<target>` (or `python3
   "<target>/build.py"`). Add `--open` to open it, `--watch` to rebuild on save.

6. **Verify** the build printed `Built index.html - N slides` with the count you
   expect, and resolve any `! missing image` / `no <section class="slide">`
   warnings. Report the deck folder and how to present (arrow keys / Space, `p`
   presenter mode, `?` shortcuts).

Write slides a person would actually present from: concrete titles that state the
point (not "Introduction"), scannable parallel bullets, real content from the
brief. Match the deck's language to the audience; flag specifics you invent to
fill a thin brief.

## Workflow 2 - Import a theme

Build a **reusable** theme under `template/themes/<name>/` (or in a deck's
`themes/<name>/`) from any reference - capture the *design language* (palette,
typography, logo, background), not a pixel-perfect clone. The reference can be:

- **a PowerPoint (`.pptx`)** - extract palette, fonts and media with the bundled
  stdlib script `scripts/pptx_theme.py`;
- **image(s)** - a slide screenshot, brand page, or moodboard, read by eye;
- **a text description** - brand words mapped to concrete tokens;
- optionally **a company logo** to integrate onto slides.

The detailed, step-by-step procedure (script invocation, palette mapping, font
handling, and **logo integration**) is in
[`reference/import-theme.md`](reference/import-theme.md). Read it when this
workflow triggers.

## The slide authoring contract

Each file in `slides/` is exactly one slide. Keep markup plain and lean on the
theme's classes - that keeps slides consistent and themes swappable.

```html
<section class="slide">
  <h2 class="title">One clear point per slide.</h2>
  <ul class="bullets">
    <li>One idea per line.</li>
  </ul>
  <aside class="notes">Speaker notes - shown only in presenter mode.</aside>
</section>
```

Slides are authored on a fixed **1920×1080** canvas; the engine scales it to any
screen, so always design against that fixed size.

### Slide variants

| Class                   | Use                               |
| ----------------------- | --------------------------------- |
| `slide`                 | standard content slide            |
| `slide slide--title`    | opening / hero slide              |
| `slide slide--section`  | section divider (dark background) |
| `slide slide--conclude` | closing slide                     |

### Content blocks (from the theme)

`.eyebrow` (kicker) · `.display` (largest heading) · `h1`/`.title`,
`h2`/`.subtitle`, `.lead` · `ul.bullets` · `.two-col` (two-column grid) · `.card`
(callout) · `blockquote` · `pre > code` (escape `< > &`) · `.footer` · `.muted` /
`.accent` (colour helpers) · `aside.notes` (presenter-only notes).

### Progressive reveal

Add `class="fragment"` to any element to reveal it step by step on click. Each
`→` reveals the next fragment, then advances to the next slide; the presenter view
shows `step 2/3`.

### Images

Put a deck's content images in `assets/` and reference them relative to the deck
root (`<img src="assets/diagram.png">`); `build.py` inlines them as base64. Keep
theme assets (fonts, backgrounds, logos) inside the theme folder.

## Configuration (`deck.config.json`)

| Key              | Default        | Purpose                              |
| ---------------- | -------------- | ------------------------------------ |
| `title`          | `Presentation` | page title                           |
| `lang`           | `en`           | document language (`fr`, `en`, …)    |
| `theme`          | `ink-blue`     | which `themes/<name>/` folder to use |
| `width` `height` | `1920` `1080`  | design canvas size                   |
| `transition`     | `fade`         | `fade` · `slide` · `zoom`            |
| `exit_hint`      | English string | toast shown on entering full screen  |

## Theming basics

A theme is a self-contained folder: `tokens.css` (colours, type scale, spacing,
font-family names), `fonts.css` (`@font-face`), `slides.css` (block styling), plus
`fonts/`, `images/`, `logos/`. To make a look, copy `themes/ink-blue/` to
`themes/<name>/`, edit `tokens.css`, and set `"theme": "<name>"`. Every theme must
define the same token names and style the same slide classes, so switching a theme
never breaks a deck.

## Reference

- [`reference/import-theme.md`](reference/import-theme.md) - full theme-import
  procedure (pptx / image / description / logo). Load it for Workflow 2.
- `template/docs/writing-slides.md` - the deep authoring guide (navigation,
  presenter mode, deeper theming). Load it when you need detail beyond the
  contract above.

## Guardrails

- One `<section class="slide">` per file in `slides/`; the build warns otherwise.
- Don't edit `engine/` to change content or styling - that's the theme's job.
- Don't build inside `template/`; always copy it into a per-deck folder first.
- Prefer the theme's classes over inline styles, so themes stay swappable.
