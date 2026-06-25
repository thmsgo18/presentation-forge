# Contributing

Thanks for helping improve Presentation Forge. It's a small, dependency-free
project — Python standard library and plain HTML/CSS/JS — and it should stay that
way.

## Project layout

```
SKILL.md          the skill's instructions to Claude (the contract)
reference/        deep-dive docs Claude loads on demand (writing, theme import)
scripts/          runtime helpers shipped with the skill (fonts, colours, pptx, theme bundle)
template/         the deck scaffold copied for every new deck
  engine/         the rendering engine — never edited to change content or look
  themes/         the look (tokens.css, fonts.css, slides.css + assets)
  slides/         example slides, one <section class="slide"> per file
  build.py        bundles everything into a single index.html
tools/            repo maintenance (pack the skill archive) — not shipped in the skill
tests/            standard-library smoke tests
dist/             the distributable skill archive (generated)
```

Keep the three layers separate: **engine** (logic), **theme** (look), **content**
(slides). A change to one should not require touching another.

## Two files are generated — don't hand-edit them

| File | Rebuild with |
| ---- | ------------ |
| `template/index.html` (bundled demo) | `python3 template/build.py` |
| `dist/presentation-forge-skill.zip` (skill archive) | `python3 tools/pack.py` |

CI fails if either drifts from its sources, so after changing the engine, a
theme, the slides, or any packaged file, regenerate and commit both. To check
locally before pushing:

```bash
python3 tools/pack.py --check     # archive in sync with sources?
python3 -m unittest discover -s tests -v
```

## Before opening a PR

1. `python3 -m unittest discover -s tests -v` — all green.
2. `python3 tools/pack.py --check` — archive in sync (or repack and commit).
3. If you touched the engine/themes/slides, rebuild the demo and commit it.
4. Keep it standard-library / zero-dependency. No new runtime requirements.
5. Match the surrounding style: 4-space indent in Python, 2-space in JS/CSS/HTML,
   and the existing comment voice.

## Requirements

- **Python 3.10+** (the scripts use `X | None` type annotations).
- A browser to view the built deck.

By contributing, you agree your contributions are licensed under the
[MIT License](LICENSE).
