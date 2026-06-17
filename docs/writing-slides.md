# Writing slides

A deck is a single HTML file. You only ever write three kinds of thing:

1. a `<deck-stage>` wrapper,
2. a list of `<section class="slide">` children, and
3. plain content inside each slide, using classes from the theme.

Everything else — scaling, navigation, the slide counter, printing — is handled
by the engine.

## Skeleton

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="stylesheet" href="../../src/themes/base.css" />
    <link rel="stylesheet" href="../../src/themes/ink-blue.css" />
    <title>My talk</title>
  </head>
  <body>
    <deck-stage width="1920" height="1080">
      <section class="slide slide--title">…</section>
      <section class="slide">…</section>
    </deck-stage>
    <script src="../../src/engine/deck-stage.js"></script>
  </body>
</html>
```

Slides are authored on a fixed **1920×1080** canvas. The engine scales that
canvas to fit any screen, so you always design against the same fixed size.

## Slide variants

| Class                    | Use                          |
| ------------------------ | ---------------------------- |
| `slide`                  | standard content slide       |
| `slide slide--title`     | opening / hero slide         |
| `slide slide--section`   | section divider (dark)       |
| `slide slide--conclude`  | closing slide                |

## Content blocks

These classes are provided by the theme:

- `.eyebrow` — small uppercase kicker above a title
- `.display` — the largest heading (title slide)
- `h1` / `.title`, `h2` / `.subtitle`, `.lead` — headings and lead text
- `ul.bullets` — a bulleted list
- `.two-col` — a two-column grid
- `.card` — a boxed callout
- `blockquote` — a pull quote
- `pre` / `code` — code
- `.footer` — a running footer (page number, talk title)
- `.muted`, `.accent` — text colour helpers

## Navigating

- **Next:** → · PageDown · Space
- **Previous:** ← · PageUp
- **First / last:** Home · End
- **Jump:** number keys `1`–`9`
- **Touch:** tap the left / right half of the screen
- The current slide is kept in the URL (`#3`), so reloading or sharing a link
  reopens on the same slide.

## Printing to PDF

Open the deck and use the browser's **Print → Save as PDF**. Each slide becomes
one page at the design size — no extra setup.

## Sharing one file

The deck is split across files for readability. To get a single portable file
you can email or host anywhere, bundle it:

```sh
python3 build.py examples/starter/index.html
# -> dist/starter.html  (self-contained: styles, script and images inlined)
```

## Theming

A theme is one stylesheet that defines the design tokens (colours, fonts, type
scale, spacing) and styles the blocks above. To make a new look, copy
`src/themes/ink-blue.css`, change the tokens, and point your deck's second
`<link>` at it.
