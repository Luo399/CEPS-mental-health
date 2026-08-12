# Claude Code for Research Writing

[简体中文](README.md) | **English**

A management-science master's student's real working notes on using Claude Code for academic writing. Every step taken, every pitfall encountered, every workflow that finally stabilized — collected here as a living book. These notes started as my own reference (I kept hitting the same problems and forgetting how I'd solved them last time), and grew into an open resource for fellow researchers.

The book is not about how impressive AI is. It's about how to use AI to present already-finished research work better. As my advisor put it: "Doing the experiments is step one. Writing them up is step two." This book is about making step two faster.

The book itself was written with Claude Code, all examples are from real usage logs (not fabricated). Your research questions, your data, and your scholarly judgment are still yours; AI helps you present them more efficiently.

---

## Table of Contents

**Part 1 · Getting Started**

1. **[What is Claude Code, and why it fits academic writing](chapters/chap01.md)** — zero-coding setup, first session walkthrough
1. **[Context and memory](chapters/chap02.md)** — CLAUDE.md and Memory: making it remember your research
1. **[Practical prompting](chapters/chap03.md)** — how to talk to it without being misunderstood

**Part 2 · Core Skills**

1. **[Literature review and management](chapters/chap04.md)** — from a pile of PDFs to a coherent review
1. **[Chapter writing](chapters/chap05.md)** — let it help, but keep authorial control
1. **[Figures and tables](chapters/chap06.md)** — academic figures with Python / Draw.io
1. **[Citations and references](chapters/chap07.md)** — automated BibTeX validation and formatting
1. **[Formatting and file management](chapters/chap08.md)** — Word's pitfalls and migrating to LaTeX

**Part 3 · Advanced Capabilities**

1. **[Skills: giving AI custom tools](chapters/chap09.md)** — codifying rules into reusable Skills
1. **[Parallel agents](chapters/chap10.md)** — accelerating batch tasks
1. **[Hooks](chapters/chap11.md)** — system-level automation triggers
1. **[MCP tool extensions](chapters/chap12.md)** — connecting Zotero, Draw.io, academic databases

**Part 4 · Mindset**

1. **[What my advisor taught me about academic writing](chapters/chap13.md)** — methodology beyond the tool
1. **[The right mindset for collaborating with AI](chapters/chap14.md)** — division of labor and high-risk areas

**Part 5 · Design Philosophy**

1. **[Discipline for designing research Skills](chapters/chap15.md)** — codifying "think first, then act" into a workflow
1. **[From one paper to research habits](chapters/chap16.md)** — making experience portable to the next project

**Appendices**

1. **[A · Common prompt templates](chapters/appendix-a.md)** — copy-paste-ready instruction templates
1. **[B · Keyboard shortcuts cheat sheet](chapters/appendix-b.md)** — Esc / `--continue` / `/clear` etc.
1. **[C · Recommended Skills for research](chapters/appendix-c.md)** — sorted by usage frequency
1. **[D · CLAUDE.md template for research](chapters/appendix-d.md)** — drop into a new project to get started
1. **[E · Common errors and solutions](chapters/appendix-e.md)** — 10 typical errors with fixes
1. **[F · paper-to-beamer in practice](chapters/appendix-f.md)** — paper PDF to seminar slides automation

---

## Updates

Repository updates are announced through:

- **Xiaohongshu @chanw** — primary channel; new chapters, new Skills, new video tutorials all surface here first
- **[CHANGELOG.md](CHANGELOG.md)** — detailed in-repo log; the top section gets updated with each push

Subscribed members can `git pull` to get the latest content. Before pulling, glance at the top of CHANGELOG to see what's new.

## Ebook versions

The latest compiled PDF lives in the repo root:

- **[Full PDF](book-main.pdf)** — compiled with the ElegantBook template; suitable for iPad / Kindle / print

The PDF is downloaded together with `git clone` (and any subsequent `git pull`), so just open it directly after cloning. Each substantive content update triggers a PDF recompile, which gets committed alongside the markdown changes.

## Lectures and Talks

A video series on Xiaohongshu walks through **practical applications of Claude Code in empirical management research**. Each video corresponds to one chapter or one type of operation in the book.

Links will appear here as videos go live (placeholders for now):

- Episode 1 · *TBD* — `link placeholder`
- Episode 2 · *TBD* — `link placeholder`

## Companion Skill Sets

Two Skill directories in the repo solve different problems. Install whichever speaks to your most painful current task.

### [book-companion-skills/](book-companion-skills/) · 15 general-purpose writing tools

The 14 Skills from Appendix C plus the `paper-to-beamer` Skill from Appendix F: PDF reading, diagramming, reference management, Word/Excel/PPT handling, statistical analysis, visualization, and paper-to-slides automation.

If unsure which to install first, the recommended trio covers the highest-frequency operations:

- [pdf](book-companion-skills/pdf) — read PDFs / merge / split / OCR
- [drawio](book-companion-skills/drawio) — research framework and process diagrams
- [humanizer-zh](book-companion-skills/humanizer-zh) — Chinese academic polishing and AI-tone removal

### [skills/](skills/) · 12 writing disciplines

These don't give you new tools; they convert "lessons learned the hard way" into mandatory pre-action checks for Claude Code. Always back up before editing Word; list a protected-terminology list before cross-chapter edits; describe the plan before acting. When you're tired and tempted to "skip a step just this once," these Skills block that shortcut.

See [skills/README.md](skills/README.md) for details.

## Shortcuts

When opening the repo for the first time and unsure where to look, these are the most-traveled paths:

**Templates and quick references**

- [Common prompt templates](chapters/appendix-a.md) — 8 scenarios: chapter editing, citation checks, figure generation, abstract polishing, etc.
- [CLAUDE.md research template](chapters/appendix-d.md) — copy into a new project and start
- [Common errors quick reference](chapters/appendix-e.md) — 10 typical errors (terms changed, files overwritten, citations fabricated) with fixes

**Essential entry chapters**

- [Chapter 1 · Getting Started](chapters/chap01.md) — install, register, first run (start here if new to the command line)
- [Chapter 2 · CLAUDE.md](chapters/chap02.md) — what to auto-load at the start of every session
- [Chapter 9 · Skills](chapters/chap09.md) — installing and writing Skills

**Advanced**

- [Chapter 10 · Parallel agents](chapters/chap10.md) — how 156 references got verified in 40 minutes
- [Chapter 11 · Hooks](chapters/chap11.md) — turning soft rules into hard enforcement
- [Appendix F · paper-to-beamer](chapters/appendix-f.md) — paper-to-slides automation

## Discussions

- **[Issues](https://github.com/Chanw-research/claude-code-paper-writing/issues)** — bug reports, errata, suggestions; usually answered within 24 hours
- **Xiaohongshu @chanw** — direct messaging for richer back-and-forth or video access
- **Critical errors** (incorrect numbers / broken commands) — fixed in the next push and noted in CHANGELOG

## Roadmap

This book isn't a frozen artifact; it grows alongside my own research work. The full list of shipped, in-progress, and planned items lives in [CHANGELOG.md](CHANGELOG.md). Quick preview:

- **In progress** — paper-to-beamer Skill being packaged into `book-companion-skills/`; Xiaohongshu video series
- **Planned** — Empirical Wiki (a Karpathy-LLM-Wiki-inspired semantic reference for empirical research); applied-case books (causal inference / meta-analysis / HLM / time series)

## A note on AI-assisted writing

This book was written with Claude Code's assistance. Research questions, data, and scholarly judgments must remain yours; AI's role is to help present existing work more efficiently — not to author research from scratch.

Chapter 14 covers the human-AI division of labor, four high-risk areas, and a three-step verification habit. Chapter 15 codifies these constraints into executable Skill disciplines.

## Acknowledgments

Thanks to my advisor for repeatedly criticizing my titles, paragraphs, and argumentation logic during the thesis writing — those notes eventually crystallized into Chapter 13's writing philosophy and Chapter 15's Skill discipline.

Thanks to the senior students and labmates who read early drafts — your feedback made the code examples more robust for newcomers.

Thanks to [Stas Bekman](https://github.com/stas00) and his [ml-engineering](https://github.com/stas00/ml-engineering) Open Book — its TOC organization, chapter layout, and downloadable-ebook engineering pattern inspired this repo's overall architecture.

Layout based on [ElegantBook](https://github.com/ElegantLaTeX/ElegantBook) (LPPL v1.3c). Some companion Skills derive from open-source community Skills (humanizer-zh, pdf, drawio, etc.); their original licenses are preserved within the respective Skill folders.

## Citation

If you reference this book in research or public talks, the BibTeX entry:

```bibtex
@misc{chanw2026claudecode,
  author       = {chanw},
  title        = {Claude Code for Research Writing: Lessons from Using Claude Code in Academic Work},
  year         = {2026},
  publisher    = {Chanw-research},
  howpublished = {\url{https://github.com/Chanw-research/claude-code-paper-writing}},
  note         = {Private repository, available to organization members}
}
```

## Repository Map

The Chanw-research organization hosts a series of research-writing books — the main trunk being this *Claude Code for Research Writing*, with applied-case books showing the methodology in specific research domains.

✔ **Main trunk**

- [Claude Code for Research Writing](https://github.com/Chanw-research/claude-code-paper-writing) — this book; methodology

✔ **Applied cases** (rolling out)

- Causal Inference R Practice — RHC dataset + nine causal methods compared *(migrating soon)*
- Meta-Analysis R Practice — *planned*
- HLM Multilevel Modeling Practice — *planned*
- Time Series Forecasting Practice — *planned*

✔ **Companion Skill sets** (within this repo)

- [book-companion-skills/](book-companion-skills/) — 15 general-purpose tools
- [skills/](skills/) — 12 writing disciplines

## License

Book content © 2026 chanw, all rights reserved. This repository is open only to Chanw-research organization members; redistribution, sharing, or uploading to public networks is prohibited. For personal study and research use by the original purchaser only.

The ElegantBook layout template is licensed under [LPPL v1.3c](License).
