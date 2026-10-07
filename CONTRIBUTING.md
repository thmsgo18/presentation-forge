# Contributing

Thanks for helping improve Presentation Forge. It's a small, dependency-free
project — Python standard library and plain HTML/CSS/JS — and it should stay that
way.

## Project layout

```
SKILL.md          the skill's instructions to Claude (the contract)
reference/        docs Claude loads on demand (writing, layouts, components, motion, theme import)
scripts/          runtime helpers shipped with the skill (new deck, visual check, fonts,
                  colours, pptx, theme bundle)
template/         the deck scaffold every new deck starts from (no slides)
  engine/         the rendering engine, motion toolkit, components and icons
  themes/         the look (tokens.css, fonts.css, slides.css + assets)
  build.py        bundles everything into a single index.html, pulls browser edits back
examples/showcase the live demo: a deck like any other (slides/, config, deck.css)
tools/            repo maintenance (build the showcase, pack the skill, refresh icons)
                  — not shipped in the skill
tests/            standard-library tests (the browser ones skip without Chrome)
dist/             the distributable skill archive (generated)
```

Keep the three layers separate: **engine** (logic), **theme** (look), **content**
(slides). A change to one should not require touching another.

## Two files are generated — don't hand-edit them

| File | Rebuild with |
| ---- | ------------ |
| `examples/showcase/index.html` (the live demo) | `python3 tools/build_showcase.py` |
| `dist/presentation-forge-skill.zip` (skill archive) | `python3 tools/pack.py` |

CI fails if either drifts from its sources, so after changing the engine, a
theme, the showcase, or any packaged file, regenerate and commit both. To check
locally before pushing:

```bash
python3 tools/build_showcase.py --check   # demo in sync with sources?
python3 tools/pack.py --check             # archive in sync with sources?
python3 -m unittest discover -s tests -v
```

`template/engine/icons.json` is generated too, but only when the icon set
changes: add a name to `tools/update_icons.py` and run it (needs network).

## Before opening a PR

1. `python3 -m unittest discover -s tests -v` — all green.
2. `python3 tools/pack.py --check` — archive in sync (or repack and commit).
3. If you touched the engine, a theme or the showcase, rebuild the demo
   (`python3 tools/build_showcase.py`), look at it
   (`python3 scripts/check_deck.py examples/showcase`), and commit it.
4. Keep it standard-library / zero-dependency. No new runtime requirements.
5. Match the surrounding style: 4-space indent in Python, 2-space in JS/CSS/HTML,
   and the existing comment voice.

## Requirements

- **Python 3.10+** (the scripts use `X | None` type annotations).
- A browser to view the built deck; Chrome, Chromium, Edge or Brave for the
  visual check and the browser tests.

By contributing, you agree your contributions are licensed under the
[MIT License](LICENSE).
