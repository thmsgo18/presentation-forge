---
description: Create a new self-contained HTML presentation (deck) from a topic or brief — any subject — and build it to a single index.html.
argument-hint: [topic or brief] (e.g. "intro to Kubernetes for backend devs, ~12 slides, fr")
---

Create a new HTML presentation with the **presentation-forge** engine. Read that
skill first if it isn't already loaded — it defines the scaffold workflow, the
slide authoring contract (classes, variants, fragments), configuration, and
building. This command is the authoring entry point on top of it.

## Request

The user's brief: **$ARGUMENTS**

If the brief is empty or thin, ask briefly for what you actually need before
generating — don't stall on details you can reasonably choose. Useful to know:

- **Topic & angle** — what it's about and the core message. Works for technical/IT
  talks *and* any other subject (a course, a pitch, a wedding speech, a report).
- **Audience** — shapes depth and vocabulary.
- **Length** — number of slides (default ~10–14 incl. title and closing).
- **Language** — set `lang` accordingly (default to the brief's language).
- **Theme** — default `ink-blue`, or another theme already in `themes/`.
- **Target folder** — default a new kebab-case folder named after the topic, in
  the current working directory.

## Steps

1. **Scaffold.** Resolve the template (`${CLAUDE_PLUGIN_ROOT}/template`, or the
   repo's `template/` in a local checkout) and copy it into the target folder, as
   described in the skill. Remove the stale demo `index.html`.

2. **Configure.** Edit `deck.config.json`: `title`, `lang`, and `theme`.

3. **Outline, then write.** Plan a tight arc before writing files:
   - `01-title.html` → `slide slide--title` with `.eyebrow`, `.display`, `.lead`.
   - An agenda slide for longer decks.
   - `slide--section` dividers between major parts.
   - Content slides: **one idea per slide**. Prefer a strong `.title` plus a few
     `.bullets`, a `.two-col`, a `.card` callout, a `blockquote`, or a `pre>code`
     block — not walls of text. Vary the block types so the deck breathes.
   - A `slide--conclude` closing slide (takeaways / call to action / thanks).
   - Add `aside.notes` with speaker notes where they help.
   - Use `class="fragment"` to reveal points step by step when build-up aids the
     narration (lists of arguments, before/after, progressive diagrams).
   Write one file per slide in `slides/`, numbered `01-`, `02-`, … Delete the
   example slides you don't reuse.

4. **Build & check.** Run `python3 build.py` in the deck folder. Confirm the
   reported slide count, resolve any warnings (missing images, slide files with no
   `<section class="slide">`), and offer to open it (`python3 build.py --open`).

5. **Report** the deck folder path and how to present (arrow keys / Space, `p` for
   presenter mode, `?` for shortcuts), and mention `/deck-to-pdf` for a PDF.

## Quality bar

Write slides a person would actually present from: concrete titles that state the
point (not "Introduction"), parallel and scannable bullets, and real content
drawn from the brief rather than placeholder lorem. Match the deck's language to
the audience. When you invent specifics to fill a thin brief, keep them plausible
and flag them so the user can correct.
