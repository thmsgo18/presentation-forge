# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **obsidian** — a second bundled theme: a dark, editorial look with embedded
  Fraunces, Inter and JetBrains Mono fonts. The template now ships it by default;
  the light `ink-blue` theme remains available.
- A 19-slide showcase deck (the template's example slides) that tours the
  engine's features and doubles as the GitHub Pages live demo.
- Continuous integration (GitHub Actions): syntax check, test suite, and a check
  that the committed skill archive stays in sync with the sources.
- `tools/pack.py` — deterministic, reproducible build of
  `dist/presentation-forge-skill.zip`, with a `--check` mode for CI.
- Standard-library test suite under `tests/` (build smoke test, demo/archive
  sync, theme round-trip, path-traversal hardening).
- Live demo published to GitHub Pages from the bundled deck.
- Repo scaffolding: `CONTRIBUTING.md`, `.editorconfig`, `.gitattributes`, issue
  and pull-request templates.
- Engine exposes its version as `DeckStage.version`.

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

[Unreleased]: https://github.com/thmsgo18/presentation-forge/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/thmsgo18/presentation-forge/releases/tag/v1.0.0
