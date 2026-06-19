# Presentation Forge

Build presentations as clean, readable HTML.

You write one HTML file per slide; a small build step bundles them with the
engine, the theme and your images into a single self-contained `index.html` you
can double-click, email, or host anywhere. No framework, no dependencies.

*[Version française](README.fr.md)*

## Structure

```
presentation-forge/
├── engine/              # the presentation logic - don't edit
│   ├── deck-stage.js    #   the engine: a <deck-stage> custom element
│   └── base.css         #   its mechanics: scaling, controls, presenter UI, print
├── themes/              # the looks - one folder per theme, swap freely
│   └── ink-blue/
│       ├── tokens.css   #     the dials: colours, type scale, spacing, fonts
│       ├── fonts.css    #     @font-face declarations
│       ├── slides.css   #     how blocks are styled (.title, .bullets, variants…)
│       ├── fonts/       #     font files            ┐ the look - travels
│       ├── images/      #     backgrounds, textures │ with the theme
│       └── logos/       #     logos                 ┘
├── slides/              # your content - one file per slide, ordered by name
│   ├── 01-title.html
│   ├── 02-agenda.html
│   └── …
├── assets/              # content images for THIS deck (kept apart from themes)
├── deck.config.json     # title, size, transition, theme
├── build.py             # bundles everything into one self-contained index.html
├── index.html           # the build output - open & share THIS file
└── README.md
```

Three clear layers: **logic** (`engine/`), **look** (`themes/`), **content**
(`slides/`). A theme is a self-contained folder (styles + its fonts, backgrounds
and logos); switching the `theme` in `deck.config.json` restyles the whole deck
without touching a single slide, because every theme honours the same set of
tokens and slide classes.

## Workflow

```sh
# 1. Edit slides in slides/ (one <section class="slide"> per file).
# 2. Build the deck:
python3 build.py            # -> index.html (self-contained)
# 3. Open or share index.html - it's a single file with everything inside,
#    images included, so it works by double-click and offline.
```

While editing, rebuild on every save and refresh the browser:

```sh
python3 build.py --watch
python3 build.py --open     # build, then open it in the browser
```

Move through the slides with the arrow keys or Space.

## Writing a slide

Each file in `slides/` is one `<section class="slide">`:

```html
<section class="slide">
  <h2 class="title">Your point here.</h2>
  <ul class="bullets">
    <li>One idea per line.</li>
  </ul>
  <aside class="notes">Notes - visible only in presenter mode.</aside>
</section>
```

Slide variants: `slide--title`, `slide--section`, `slide--conclude`.
Content blocks from the theme: `eyebrow`, `display`, `title`, `lead`, `muted`,
`accent`, `bullets`, `two-col`, `card`, `blockquote`, `pre > code`.

Slides display in **filename order** (`01-`, `02-`…); to add one, drop a new
file in `slides/`. See [docs/writing-slides.md](docs/writing-slides.md) for the
full guide.

## Presenting

- **Progressive reveal** - add `class="fragment"` to an element to reveal it
  step by step on click (the presenter view shows `step 2/3`).
- **Full screen** - the ⤢ button or `f`.
- **Presenter mode** - the screen button or `p`: opens an audience window
  (full-screen slide) and a presenter view here with the next-slide preview,
  speaker notes, a wall clock and timers, drawing and a laser pointer.
- **Overview** - `o` shows every slide as a grid; `b` / `w` blanks the screen.
- **Export PDF** - the print button (one page per slide).
- **Keyboard shortcuts** - press `?` for the full list.

## License

[MIT](LICENSE) © Thomas Gourmelen
