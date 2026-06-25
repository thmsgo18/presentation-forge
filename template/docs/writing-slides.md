# Writing slides

A deck is a folder. You write **one file per slide** in `slides/`, each holding a
single `<section class="slide">` with plain content using classes from the theme.
Everything else - scaling, navigation, the slide counter, and presenter
mode - is handled by the engine.

You never write the `<deck-stage>` wrapper or link the engine/theme by hand:
`build.py` assembles the slides, the engine, the theme and your images into one
self-contained `index.html`.

## One slide = one file

```html
<!-- slides/02-agenda.html -->
<section class="slide">
  <h2 class="title">What this deck shows.</h2>
  <ul class="bullets">
    <li>One idea per line.</li>
  </ul>
  <aside class="notes">Notes - visible only in presenter mode.</aside>
</section>
```

Slides display in **filename order**, so prefix them (`01-`, `02-`, …). To add a
slide, just drop a new file in `slides/`; to reorder, rename.

Slides are authored on a fixed **1920×1080** canvas. The engine scales that
canvas to fit any screen, so you always design against the same fixed size.

## Building & previewing

```sh
python3 build.py            # -> index.html (self-contained)
python3 build.py --watch    # rebuild on every save
python3 build.py --open     # build, then open in the browser
```

Open `index.html` (double-click works - it's a single file with the engine,
theme and images all inlined).

## Slide variants

| Class                    | Use                          |
| ------------------------ | ---------------------------- |
| `slide`                  | standard content slide       |
| `slide slide--title`     | opening / hero slide         |
| `slide slide--section`   | section divider (dark)       |
| `slide slide--conclude`  | closing slide                |

## Content blocks

These classes are provided by the theme:

- `.eyebrow` - small uppercase kicker above a title
- `.display` - the largest heading (title slide)
- `h1` / `.title`, `h2` / `.subtitle`, `.lead` - headings and lead text
- `ul.bullets` - a bulleted list
- `.two-col` - a two-column grid
- `.card` - a boxed callout
- `blockquote` - a pull quote
- `pre` / `code` - code
- `.muted`, `.accent` - text colour helpers

## Progressive reveal (fragments)

Add `class="fragment"` to any element to reveal it step by step on click,
instead of showing the whole slide at once (like Beamer's `\pause`):

```html
<section class="slide">
  <h2 class="title">My points</h2>
  <ul class="bullets">
    <li class="fragment">First point</li>
    <li class="fragment">Second point</li>
    <li class="fragment">Third point</li>
  </ul>
</section>
```

Each press of → reveals the next fragment; once all are shown, → moves to the
next slide. ← hides the last fragment (and going back to a slide shows all of
its fragments). The audience window and the presenter step counter
(`step 2/3`) stay in sync. A slide with no `.fragment` behaves exactly as
before.

## Images

Put images in `assets/` and reference them from a slide with a path relative to
the project root:

```html
<img src="assets/diagram.png" alt="Architecture" />
```

`build.py` inlines them as base64, so the built `index.html` stays a single
portable file.

## Navigating

- **Next / previous:** → · PageDown · Space  /  ← · PageUp (these also step
  through fragments)
- **First / last:** Home · End
- **Jump:** number keys `1`-`9`, or click a slide in the left-hand rail
- **Overview (all slides):** `o`
- **Full screen:** the button or the `f` key (Esc to leave)
- **Presenter mode:** the button or `p`
- **Black / white screen:** `b` / `w` (any key resumes)
- **Shortcuts overlay:** `?`
- **Touch:** swipe left / right, or tap the left / right half of the stage
- The current slide is kept in the URL. Give a slide an `id` (e.g.
  `<section class="slide" id="intro">`) for a stable named link (`#intro`);
  otherwise it's the slide number (`#3`).

## Deck configuration

Set these in `deck.config.json`:

| Key          | Default        | Purpose                                     |
| ------------ | -------------- | ------------------------------------------- |
| `title`      | `Presentation` | the page title                              |
| `lang`       | `en`           | document language                           |
| `theme`      | `ink-blue`     | which `themes/<name>/` folder to use        |
| `width` `height` | `1920` `1080` | the design canvas size                  |
| `transition` | `fade`         | slide transition: `fade` · `slide` · `zoom` |
| `exit_hint`  | English        | toast text shown when entering full screen  |

## Theming

A theme is a self-contained folder under `themes/`, split by concern:

```
themes/obsidian/   # this deck's theme; a light "ink-blue" theme also ships
├── tokens.css   # the dials: colours, type scale, spacing, font-family names
├── fonts.css    # @font-face declarations
├── slides.css   # how the blocks above are styled
├── fonts/       # font files            ┐ part of the look -
├── images/      # backgrounds, textures │ travels with the theme
└── logos/       # logos                 ┘
```

Keep theme assets (fonts, backgrounds, logos) inside the theme folder, and your
deck's content images in `assets/` - the two never mix.

To make a new look, copy `themes/ink-blue/` to `themes/<name>/`, edit
`tokens.css` (and `slides.css` if needed), and set `"theme": "<name>"` in
`deck.config.json`. Because every theme defines the same tokens and styles the
same slide classes, switching themes never breaks a deck. `build.py` inlines the
theme's stylesheets and assets (base64) into the single-file build.
