# paper-to-beamer

A Claude Code skill that turns an academic paper (PDF) into a compilable
LaTeX Beamer presentation — figure extraction, slide structure, bibliography
wiring, and validation, all in one pipeline.

Ships with the **Crimson** theme (`crimson.sty`): a minimalist red-accent
Beamer layout tuned for paper-reading talks and group meetings (组会). The
theme emphasizes a rigorous academic register (declarative frame titles,
third-person body voice, no narrator flourishes) over a pedagogical or
social-media tone.

## What the skill does

Given a paper PDF, the skill:

1. Reads the paper and extracts title, authors, contributions, figures, tables, key equations.
2. Asks the user 3–4 clarifying questions (language, duration, logo, figure strategy).
3. Runs `scripts/extract_assets.py` to pull every figure + table from the PDF into `figs/` with a `manifest.json` catalog.
4. Assigns each asset to the slide its caption actually supports (no hard-coded domain rules).
5. Generates `main.tex` with the Crimson theme, xeCJK + Times New Roman fonts, BibTeX wiring, and all content slides.
6. Validates the output: environment balance, brace balance, citation coverage, figure-file existence, section/subsection sanity.
7. Optionally compiles via `xelatex → bibtex → xelatex → xelatex` if TeX Live is installed locally.

## Repository layout

```
paper-to-beamer/
├── SKILL.md                     # Skill instructions Claude Code follows
├── LICENSE                      # MIT (fonts excluded, see LICENSE)
├── README.md
├── assets/
│   └── template/                # Copied into working directory at Phase 3b
│       ├── crimson.sty          # The Crimson theme
│       ├── template_main.tex    # Preamble + frame skeleton
│       └── fonts/
│           ├── STKAITI.TTF      # CJK font (see font note below)
│           └── wingding.ttf     # Itemize-icon font (see font note below)
├── scripts/
│   └── extract_assets.py        # PyMuPDF + pdfplumber figure/table extractor
├── references/
│   └── pitfalls.md              # 20+ known-issue catalog (fonts, packages, layout)
└── evals/
    └── evals.json               # Example prompts + expected properties for testing
```

## Quick install

Drop the entire `paper-to-beamer/` directory into your Claude Code skill
search path (typically `~/.claude/skills/`). The next time Claude sees a
prompt matching "turn this paper into beamer slides" / "做一个论文的 PPT"
etc., the skill auto-triggers.

Python dependencies for figure extraction (only needed the first time you
run the skill):
```
pip3 install PyMuPDF pdfplumber
```

## Compiling the generated deck

The skill produces a standard XeLaTeX project. From the working directory:

```bash
xelatex main.tex
bibtex main
xelatex main.tex
xelatex main.tex
```

Or upload to Overleaf and set compiler → XeLaTeX.

## The Crimson theme at a glance

- Single crimson accent (RGB `175,37,28`) on frame titles, structure, and `\alert{}`.
- `gray!12` footer with crimson text — breaks the three-layer red stack that pure-red beamer themes suffer from.
- Smoothbars outer theme, circles inner theme, enlarged nav section labels for projector legibility.
- Auto-inserts a TOC slide before every `\section` (do NOT use `\subsection{}` or manual `\tableofcontents` — both cause duplication).
- Optional `\sectionlead{...}` command for attaching a one-line italic lead-in below each section TOC.
- Times New Roman math-mode digits via `mathspec` (loaded before xeCJK) — avoids the classic "body text is Times, but `$0.31^\circ$` renders in Computer Modern" inconsistency.

## A note on the bundled fonts

`STKAITI.TTF` (华文楷体) and `wingding.ttf` are shipped for compilation
convenience. They are **not** covered by this repository's MIT License — see
`LICENSE` for the exact scope. STKaiti ships with macOS; Wingdings ships
with Windows. If you plan to redistribute this skill publicly or use it in a
context where those fonts aren't licensed, substitute freely-licensed
alternatives:

- **CJK body**: LXGW WenKai (霞鹜文楷, SIL OFL), Source Han Serif (思源宋体, SIL OFL)
- **Itemize icon**: drop wingding.ttf and replace `\XeTeXglyph190` with a plain Unicode glyph (e.g. `▸` or `►`)

## Known pitfalls

See `references/pitfalls.md` — 20+ concrete symptoms + fixes for
compilation engine mismatches, font fallback, layout overflow, bibliography
wiring, and package conflicts (pstricks, hyperref, ctex).

## License

MIT for all code and documentation in this repository. See `LICENSE`.

Bundled fonts are governed by their original vendor licenses (Apple /
DynaComware for STKaiti, Microsoft for Wingdings) and are not
sublicensed by this repository.
