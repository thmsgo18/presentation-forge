# Presentation Forge - a portable Claude skill

Build beautiful, **self-contained HTML presentations** with Claude. You describe a
talk; Claude writes one HTML file per slide and bundles them - engine, theme and
images included - into a single portable `index.html` you can double-click,
email, or host anywhere. No framework, no runtime dependencies.

This is an **Agent Skill**: a single folder that works everywhere Claude has a
filesystem and Python - **Claude Code**, the **Claude apps** (claude.ai / desktop),
and the **API**.

## What it does

Two workflows, triggered in plain language (no slash command needed):

- **Create a presentation** - *“make an HTML presentation about …”*. Any subject:
  a technical talk, a course, a pitch. Claude scaffolds a deck, writes the slides,
  and builds it to a single `index.html`.
- **Import a theme** - *“reuse this brand / this .pptx / this look”*. Build a
  **reusable theme** from a PowerPoint (`.pptx`), an image (slide/brand mockup),
  or a text description - and integrate a **company logo**.

The skill bundles the whole engine in [`template/`](template/); the authoring
contract and theme guide live in [`SKILL.md`](SKILL.md) and
[`reference/import-theme.md`](reference/import-theme.md).

## Install

### In the Claude apps (claude.ai / desktop)
Upload **`dist/presentation-forge-skill.zip`** in **Settings → Features → Skills**
(Pro, Max, Team, or Enterprise, with code execution enabled). Then just ask Claude
to make a presentation.

### In Claude Code
Drop the skill into your skills folder - Claude discovers it automatically:
```sh
git clone https://github.com/thmsgo18/presentation-forge.git ~/.claude/skills/presentation-forge
```
(or copy this folder to `.claude/skills/presentation-forge/` inside a project).

### Via the API
Upload the same `dist/presentation-forge-skill.zip` through the Skills API
(`/v1/skills`) and reference it from the code-execution container.

> Custom skills don’t sync across surfaces - upload the zip once per surface where
> you want it.

## Requirements

- **Python 3** (standard library only) - to build decks and read `.pptx` files.
- Nothing else. Theme import from images or descriptions uses Claude’s own visual
  judgement.

## Layout

```
SKILL.md                 the skill: workflows + slide authoring contract
reference/import-theme.md detailed theme-import guide (pptx · image · description · logo)
scripts/pptx_theme.py    extract palette/fonts/media from a .pptx (pure stdlib)
template/                the deck engine copied into each presentation
                         (engine/, themes/, slides/, build.py, docs/ …)
dist/                    packaged skill zip for upload
```

## License

[MIT](LICENSE) © Thomas Gourmelen
