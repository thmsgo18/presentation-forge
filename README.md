# Presentation Forge

Build presentations as clean, readable HTML.

Presentation Forge is a small, zero-dependency engine for slide decks. You
write each slide as plain, semantic HTML; the engine handles scaling,
navigation, the slide counter, printing to PDF, and bundling to a single
portable file. There is no framework to learn and nothing to compile — open a
deck in a browser and it just works.

*[Version française](README.fr.md)*

## Why

- **Readable.** A deck is `<section class="slide">` elements with ordinary
  content inside. Anyone comfortable with HTML can open one and find their way
  around.
- **Consistent.** A theme provides the design tokens and block styles, so every
  slide looks coherent without per-slide fiddling.
- **Portable.** One build step inlines everything into a single `.html` file you
  can email, host anywhere, or open with a double-click.
- **No dependencies.** The engine is one vanilla JavaScript file; the bundler is
  one Python file using only the standard library.

## Quick start

```sh
git clone https://github.com/thmsgo18/presentation-forge.git
cd presentation-forge
open examples/starter/index.html      # or double-click it
```

Use the arrow keys (or Space) to move through the slides.

To produce a single shareable file:

```sh
python3 build.py examples/starter/index.html
# -> dist/starter.html
```

## Project layout

```
presentation-forge/
├── src/
│   ├── engine/
│   │   └── deck-stage.js     # the presentation engine (one file, no deps)
│   └── themes/
│       ├── base.css          # mechanics only: scaling, layout, print
│       └── ink-blue.css      # a sober blue / ink theme (colours, fonts, type)
├── examples/
│   └── starter/
│       └── index.html        # a demo deck showing every slide type
├── docs/
│   └── writing-slides.md     # how to author a deck
└── build.py                  # bundle a deck into one portable .html
```

## Writing a deck

See [docs/writing-slides.md](docs/writing-slides.md). In short: a deck is one
`<deck-stage>` containing `<section class="slide">` children, authored on a
fixed 1920×1080 canvas that the engine scales to fit any screen.

## License

[MIT](LICENSE) © Thomas Gourmelen
