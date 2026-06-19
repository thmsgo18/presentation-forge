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
| **`/new-presentation`** `[topic or brief]` | Create a presentation on any subject — a technical talk, a course, a pitch — scaffolded from the template, authored slide by slide, and built to `index.html`. |
| **`/import-template`** `<.pptx \| image \| "description">` | Build a **reusable HTML theme** under `themes/<name>/` from a PowerPoint, an image (slide/brand mockup), or a text description — and optionally integrate your company logo. |
| **`/export-pdf`** `<deck>` | Export a deck to a clean PDF, one page per slide, with progressive reveals shown in their final state — reliable even where the browser's own print isn't. |

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

Then ask Claude to “make a presentation about …”, or run `/new-presentation`.

## Requirements

- **Python 3** (standard library only) — to build decks and run the scripts.
- **A Chromium browser** (Chrome, Chromium, Edge or Brave) **or Playwright** —
  only for `/export-pdf`. The script prefers a system browser and falls back to
  `pip install playwright && playwright install chromium`.
- `/import-template` needs nothing extra: the `.pptx` reader is pure stdlib, and
  image/description references use Claude's own visual judgement.

## Layout

```
.claude-plugin/        plugin + marketplace manifests
commands/              /new-presentation, /import-template, /export-pdf
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
