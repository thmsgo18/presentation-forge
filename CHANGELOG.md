# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Two questions before a deck is written**: how to build it (plan first -
  the default -, all at once, or slide by slide with a review after each one)
  and how much animation. Content stays the user's call: Claude builds from
  their brief and doesn't quiz them about it.
- **Motion levels**: `"motion"` in `deck.config.json` - `none`, `subtle`,
  `balanced` (default), `lively`, `extra` - scales every animation in the deck
  without touching a slide. `none` leaves the toolkit out of the build entirely.
- **Animation toolkit** (`engine/motion.css`): entrances (`data-anim`: fade,
  rise, drop, from-left, from-right, zoom, pop, blur, wipe, type, flip, draw),
  one-after-the-other lists (`data-stagger`), fragment effects including a
  `highlight` marker, ambient loops (`data-loop`), counting figures
  (`data-count`), and per-slide transitions (`data-transition`: none, fade,
  slide, zoom, rise, blur, flip). Entrances only play moving forward; the audience
  window animates in sync.
- **Components** (`engine/components/`): key figures (`stats`), bar charts
  (`bars`), gauges (`ring`), processes (`steps`), timelines (`timeline`),
  comparison tables (`compare`), card columns (`grid`) and decoration (`fx`),
  all following the active theme. The build bundles only the ones a deck uses.
- **84 line icons** (Lucide, ISC) via `<i data-icon="rocket"></i>`, inlined at
  build time - only the icons a deck uses.
- **Visual self-check**, `scripts/check_deck.py`: renders the deck in headless
  Chrome / Edge, reports text past a slide's edge, content cut off and broken
  images, and saves a contact sheet plus images of the slides asked for.
  SKILL.md makes it a required step before handing a deck over.
- **In-browser edits survive rebuilds**: the build stamps every editable block,
  the engine marks what was edited, and every `build.py` run (or
  `build.py --pull`) writes those edits back into `slides/*.html` - only the
  edited text, leaving formatting, comments and icons as written. An edit to a
  block that also changed in `slides/` is never forced in: the edited deck is
  kept as `index.unmerged-edits.html`.
- `scripts/new_deck.py`: creates an empty deck (title, language, theme, motion,
  transition) in one command.
- `deck.css`: optional styles for one deck only, loaded after the theme.
- `reference/layouts.md`, `reference/components.md`, `reference/motion.md`:
  short menus Claude reads instead of inventing layouts, CSS or keyframes.
- Tests for the build, the edit round trip (including one driving the real
  engine in headless Chrome) and the visual check; CI also verifies the
  showcase build.

### Changed

- **New decks start empty.** The 22-slide demo moved out of `template/` into
  `examples/showcase/` (still the live demo, built by
  `tools/build_showcase.py`) and is no longer shipped in the skill, so a deck is
  a first draft of the user's talk rather than a reworded copy of the demo.
  `reference/layouts.md` and `writing-decks.md` no longer suggest a fixed arc:
  only the title and closing slides are fixed.
- The `obsidian` theme holds only theme styles now: the demo's mockups moved to
  the showcase's `deck.css`, and its ambient drift and line draw follow the
  motion level. The demo deck renders correctly under `ink-blue` too.
- The edit mode only touches blocks the build stamped as editable (one rule set,
  in `build.py`), types and pastes plain text only, and Esc restores a block
  exactly, inline markup included.
- The page title and `<deck-stage>` attributes are HTML-escaped.

### Fixed

- Slide copies in the thumbnail rail and the overview (`o`) inherited the
  centred text of their buttons and no longer looked like the slide.
- In-browser editing: typing in an edited text block no longer triggers deck
  shortcuts. Space advanced to the next slide and letters such as `f`, `p`,
  `l` or `b` toggled full screen, presenter mode, the laser or a black screen
  instead of being typed.
- Speaker notes kept their structure through the notes panel. Opening and
  closing it flattened paragraphs and bullet lists into one block of text, and
  saved that to disk once editing was on. Untouched notes are now never
  rewritten, and edited ones keep paragraphs and lists (`- ` / `1. ` lines).

## [2.0.0] - 2026-06-29

### Added

- **obsidian** — a second bundled theme: a dark, editorial look with embedded
  Fraunces, Inter and JetBrains Mono fonts. The template now ships it by default;
  the light `ink-blue` theme remains available.
- A 20-slide showcase deck (the template's example slides) that tours the
  engine's features and doubles as the GitHub Pages live demo.
- In-browser editing of slide text and speaker notes, saved straight back to
  disk via the File System Access API. Chrome, Edge and other Chromium
  browsers only, and only for a deck opened from a local file - the control is
  absent everywhere it couldn't actually save.
- Continuous integration (GitHub Actions): syntax check, test suite, and a check
  that the committed skill archive stays in sync with the sources, now run on
  Ubuntu, Windows and macOS so the build is verified cross-platform, not just
  on Linux.
- `tools/pack.py` — deterministic, reproducible build of
  `dist/presentation-forge-skill.zip`, with a `--check` mode for CI.
- Standard-library test suite under `tests/` (build smoke test, demo/archive
  sync, theme round-trip, path-traversal hardening).
- Live demo published to GitHub Pages from the bundled deck.
- Repo scaffolding: `CONTRIBUTING.md`, `.editorconfig`, `.gitattributes`, issue
  and pull-request templates.
- Engine exposes its version as `DeckStage.version`.

### Changed

- Clarified the install instructions for Windows: `python` instead of
  `python3` where Python's `python3` alias isn't on `PATH`, and a note that
  the `git clone ... ~/.claude/skills/...` line needs a POSIX-style shell
  (Git Bash, WSL) since plain PowerShell/cmd don't expand `~`.

### Security

- `scripts/theme_bundle.py unpack` now rejects path traversal in a
  `.pfstyle.json` (file keys and theme name), so an untrusted style file can no
  longer write outside the destination theme folder.

## [1.0.0] - 2026-06-25

### Added

- Presentation Forge as a portable Agent Skill: author one HTML file per slide,
  build a single self-contained `index.html` with `build.py` (standard library
  only).
- Engine with windowed/full-screen/presenter modes, speaker notes, timer,
  next-slide preview, progressive reveal (`fragment`), keyboard navigation, and
  auto-scaling from a fixed 1920×1080 canvas.
- Swappable themes (`tokens.css`, `fonts.css`, `slides.css` + assets) with the
  bundled `ink-blue` theme.
- Theme import from a `.pptx`, image(s), or a text description, plus export/import
  of a portable `.pfstyle.json` style file.
- Bilingual documentation (English and French).

[Unreleased]: https://github.com/thmsgo18/presentation-forge/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/thmsgo18/presentation-forge/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/thmsgo18/presentation-forge/releases/tag/v1.0.0
