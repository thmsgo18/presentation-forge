# Presentation Forge — Claude Code plugin

Build beautiful, **self-contained HTML presentations** with Claude Code. You
describe a talk; Claude writes one HTML file per slide and bundles them — engine,
theme and images included — into a single portable `index.html` you can
double-click, email, or host anywhere. No framework, no runtime dependencies.

This plugin wraps the [Presentation Forge](template/README.md) deck engine and
adds three commands.

## Commands

| Command | What it does |
| ------- | ------------ |
| **`/new-deck`** `[topic or brief]` | Create a presentation on any subject — a technical talk, a course, a pitch — scaffolded from the template, authored slide by slide, and built to `index.html`. |
| **`/import-pptx-theme`** `<file.pptx>` | Recreate a PowerPoint's look (colours, fonts, logo, backgrounds) as a **reusable HTML theme** under `themes/<name>/`, usable by any deck. |
| **`/deck-to-pdf`** `<deck>` | Export a deck to a clean PDF, one page per slide, with progressive reveals shown in their final state — reliable even where the browser's own print isn't. |

A **skill** (`presentation-forge`) carries the shared knowledge — the slide
authoring contract, building, theming — so Claude can also just build a deck when
you ask, without a command.

## Install

The repository is its own marketplace:

```sh
# in Claude Code
/plugin marketplace add thmsgo18/presentation-forge
/plugin install presentation-forge@thmsgo18
```

Then ask Claude to “make a presentation about …”, or run `/new-deck`.

## Requirements

- **Python 3** (standard library only) — to build decks and run the scripts.
- **A Chromium browser** (Chrome, Chromium, Edge or Brave) **or Playwright** —
  only for `/deck-to-pdf`. The script prefers a system browser and falls back to
  `pip install playwright && playwright install chromium`.
- `/import-pptx-theme` needs nothing extra: the `.pptx` reader is pure stdlib.

## Layout

```
.claude-plugin/        plugin + marketplace manifests
commands/              /new-deck, /import-pptx-theme, /deck-to-pdf
skills/presentation-forge/SKILL.md   shared authoring knowledge
scripts/               deck_to_pdf.py (PDF export), pptx_theme.py (theme import)
template/              the deck scaffold copied into each new presentation
                       (engine/, themes/, slides/, build.py, docs/ …)
```

The engine, themes and authoring guide live in [`template/`](template/) — see
[`template/README.md`](template/README.md) and
[`template/docs/writing-slides.md`](template/docs/writing-slides.md) for the deck
system itself.

## License

[MIT](LICENSE) © Thomas Gourmelen
