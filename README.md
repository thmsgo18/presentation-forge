<p align="right"><b>English</b> | <a href="./README.fr.md">Français</a></p>

<h1 align="center">Presentation Forge</h1>

<p align="center">
  <b>Describe your talk to Claude. It writes the slides and bundles them into a single, portable <code>index.html</code> you can double-click, email, or host anywhere.</b>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-22c55e?style=for-the-badge" alt="License MIT"></a>
  <img src="https://img.shields.io/badge/claude-skill-d97757?style=for-the-badge" alt="Claude Skill">
  <img src="https://img.shields.io/badge/output-single%20file-2563eb?style=for-the-badge" alt="Single file output">
  <img src="https://img.shields.io/badge/python-stdlib%20only-f59e0b?style=for-the-badge" alt="Python stdlib only">
</p>

<p align="center">
  <a href="#why">Why</a> •
  <a href="#what-it-can-do">What it can do</a> •
  <a href="#install">Install</a> •
  <a href="#example">Example</a> •
  <a href="#how-it-works">How it works</a> •
  <a href="#themes">Themes</a>
</p>

---

## What is this?

A [Claude](https://claude.com) skill that turns plain language into polished, web native slide decks. You say *"make me a presentation about X"*; Claude scaffolds the deck, writes one HTML file per slide, picks or builds a theme, and compiles everything into a single **self-contained `index.html`**. Engine, theme, fonts and images are all inlined, so the file opens by double-click, emails cleanly, and works fully offline. No framework, no build server, no runtime dependencies.

It is an **Agent Skill**: one folder that works everywhere Claude has a filesystem and Python. The same skill runs in **Claude Code**, the **Claude apps** (claude.ai and desktop), and through the **API**. No slash command to remember, just ask.

## Why

Building a deck the usual way means fighting your tools before you write a single idea. Presentation Forge flips that around: you bring the content, Claude handles the craft.

| Without Presentation Forge | With Presentation Forge |
| :------------------------- | :---------------------- |
| Open PowerPoint or Keynote, wrestle with layouts, alignment and master slides | Describe the talk in a sentence and get a structured deck back |
| Fonts and styling break the moment the file lands on another machine | Everything inlined into one `index.html` that renders identically everywhere |
| Sharing means heavy attachments or a cloud account | Send one HTML file, or host it as a static page |
| "Just reuse the company template" turns into an afternoon of copy-paste | Import a brand once, save it as a style file, reapply it in seconds |
| Speaker notes, progressive reveal and a presenter view are fiddly add-ons | Built in: presenter mode, step-by-step reveal, keyboard navigation |
| The deck is a binary blob you cannot diff or version cleanly | Plain HTML you can read, edit, and track in git |

The result is a deck that is **portable** (a single file), **professional** (real typography and a coherent theme), and **yours to edit** (readable HTML, no lock-in).

## What it can do

- **Turn any brief into a deck.** A topic, an outline, rough notes, or a whole document. Technical talks, courses, pitches, lectures, any subject.
- **Write slides that actually land.** Assertion style titles, one idea per slide, tight bullets, two-column layouts, callout cards, quotes and clean code blocks. Walls of text go into the speaker notes, not the screen.
- **Present like a pro.** Built-in presenter mode with notes and a timer, progressive reveal (`fragment`) to build a point step by step, and full keyboard navigation. Press `?` for shortcuts.
- **Stay on brand.** Swappable themes keep colours, type and spacing consistent. Switch the look without touching a single slide.
- **Import a brand.** Recreate a visual identity as a reusable theme from a **PowerPoint** (`.pptx`), an **image** (a slide or brand mockup), or just a **text description**, and drop in a **company logo**.
- **Save a style once, reuse it forever.** Any theme exports to a single portable **`.pfstyle.json`**. Hand that file back in any future conversation to recreate the exact same look, byte for byte, with no original PowerPoint or image needed.
- **Ship a single file.** One `index.html`, offline ready, no dependencies, that opens anywhere a browser exists.

## Install

This is a standard [Claude skill](https://docs.claude.com/en/docs/claude-code/skills): a folder with a `SKILL.md` that Claude loads automatically when it is relevant. Install it once on each surface where you want it.

### Claude Code

Drop the skill into your skills folder and Claude discovers it on its own:

```bash
git clone https://github.com/thmsgo18/presentation-forge.git ~/.claude/skills/presentation-forge
```

For a single project only, clone into `.claude/skills/presentation-forge/` inside that repository instead.

### Claude apps (claude.ai and desktop)

Upload **`dist/presentation-forge-skill.zip`** in **Settings → Features → Skills** (requires Pro, Max, Team or Enterprise with code execution enabled). Then just ask Claude for a presentation.

### API

Upload the same `dist/presentation-forge-skill.zip` through the Skills API (`/v1/skills`) and reference it from the code-execution container.

> Custom skills do not sync across surfaces. Upload the zip once per surface where you want it.

## Example

```
You: Make an HTML presentation about our Q3 results for the all-hands.
     Five minutes, upbeat tone. Highlights: revenue up 18%, churn down to
     4%, two new enterprise logos. Use our brand, here is the deck template
     from last quarter (attached .pptx).

Claude: [imports the brand from the .pptx into a reusable theme, scaffolds
        the deck, writes a title slide, an agenda, three assertion-led
        content slides with speaker notes, and a closing slide with the
        takeaway, then builds it to a single index.html]

        Done. Your deck is in q3-all-hands/index.html (7 slides).
        Open it and press p for presenter mode, arrow keys to navigate,
        ? for all shortcuts. I also saved the theme as acme.pfstyle.json
        so you can reuse this exact look next quarter.
```

## How it works

Three layers, always kept separate so a deck never breaks when you reskin it:

- **engine** (`template/engine/`): rendering, scaling, navigation, presenter mode, progressive reveal. Never edited to change content or look.
- **theme** (`template/themes/<name>/`): the look. Colours, type, spacing, fonts, logos, backgrounds.
- **content** (`slides/`): the slides, one HTML file each, ordered by name.

The pipeline is deliberately boring, which is what makes it portable:

1. Pick a target folder and copy the template into it.
2. Configure `deck.config.json` (title, language, theme, transition).
3. Write the slides in `slides/`, one `<section class="slide">` per file, numbered `01-`, `02-`, ...
4. Run `python3 build.py`. It inlines the engine, the theme, the fonts and every image, then writes a single `index.html`.
5. Open it, present it, share it. Add `--watch` to rebuild on save.

Slides are authored on a fixed **1920x1080** canvas and the engine scales that to any screen, so a deck looks the same on a laptop, a projector or a phone. The full authoring contract and theme guide live in [`SKILL.md`](SKILL.md) and [`reference/`](reference/).

## Themes

A theme is a self-contained folder (`tokens.css`, `fonts.css`, `slides.css`, plus `fonts/`, `images/`, `logos/`). Every theme defines the same token names and styles the same slide classes, so switching themes never breaks a deck.

You can build a theme from a brand in four ways:

| Source | What Claude does |
| :----- | :--------------- |
| `.pptx` PowerPoint | Extracts the palette, fonts, embedded media and master layout geometry |
| Image (slide or mockup) | Samples the exact dominant colours, reads typography and layout by sight |
| Text description | Maps brand words to design tokens |
| `.pfstyle.json` | Rebuilds the entire theme (CSS, fonts, logos, backgrounds) in one step |

Whatever the source, the theme exports to a single portable **`.pfstyle.json`**. Keep that file and you can recreate the exact same identity in any future conversation, no original assets required. Full procedure in [`reference/import-theme.md`](reference/import-theme.md).

## Requirements

- A Claude client that supports skills ([Claude Code](https://docs.claude.com/en/docs/claude-code), the Claude apps, or the API).
- **Python 3**, standard library only, to build decks and read `.pptx` files. Nothing else to install.
- A browser to view the result. That is it.

## License

[MIT](LICENSE) © Thomas Gourmelen
