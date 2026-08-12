# Beamer + XeLaTeX Known Pitfalls and Solutions

## Table of Contents
1. [Compilation Issues](#compilation-issues)
2. [Font Issues](#font-issues)
3. [Content Layout Issues](#content-layout-issues)
4. [Bibliography Issues](#bibliography-issues)
5. [Figure Issues](#figure-issues)
6. [Package Conflicts](#package-conflicts)

---

## Compilation Issues

### 1. Wrong compilation engine
**Symptom:** Errors about undefined control sequences for CJK characters, or `\XeTeXglyph` not recognized.
**Cause:** Compiling with pdfLaTeX instead of XeLaTeX.
**Fix:** Add `% !TEX program = xelatex` as the first line. In Overleaf, set Menu → Compiler → XeLaTeX.

### 2. Shell escape required for certain packages
**Symptom:** Error when using pstricks, minted, or auto-pst-pdf.
**Cause:** These packages need `--shell-escape` flag.
**Fix:** Don't use pstricks in the generated output. If absolutely needed: `xelatex --shell-escape main.tex`.

### 3. Multiple compilation passes needed
**Symptom:** References show as `[?]`, table of contents is empty, page numbers wrong.
**Cause:** LaTeX needs multiple passes to resolve cross-references.
**Fix:** Run the full compilation chain: `xelatex → bibtex → xelatex → xelatex`.

---

## Font Issues

### 4. STKAITI.TTF not found
**Symptom:** `Font "STKAITI.TTF" not found` error.
**Cause:** Font file missing or path wrong.
**Fix:** Ensure `fonts/STKAITI.TTF` exists relative to main.tex. The `\setCJKmainfont[Path=fonts/]{STKAITI.TTF}` directive requires the `Path=fonts/` option.

### 5. Chinese characters display as boxes
**Symptom:** Chinese text shows as empty rectangles.
**Cause:** CJK font not loaded or wrong encoding.
**Fix:** Verify xeCJK package is loaded with `[BoldFont,SlantFont]` and font path is correct.

### 6. wingding font glyph not found
**Symptom:** Itemize bullets show as missing characters.
**Cause:** wingding.ttf missing or `\XeTeXglyph190` not available.
**Fix:** Ensure `fonts/wingding.ttf` exists. This glyph command is XeTeX-specific — it will not work with pdfLaTeX.

### 7. Times New Roman not available
**Symptom:** Font substitution warning for Times New Roman.
**Cause:** Font not installed on the system.
**Fix:** On Linux, install `ttf-mscorefonts-installer`. On macOS, it's usually pre-installed. Alternatively, use `\setmainfont{TeX Gyre Termes}` as a free substitute.

### 7b. Math-mode digits render in Computer Modern
**Symptom:** Body text is Times New Roman, but digits inside `$...$` (e.g. `$0.31^{\circ}$`, `$-1{,}800$\,m`) appear in Computer Modern — visually inconsistent with the rest of the slide.
**Cause:** `fontspec`'s `\setmainfont` only sets text-mode font. Math-mode digits and Latin letters go through a separate pipeline that defaults to Computer Modern.
**Fix:** Load `mathspec` **before** `xeCJK` and configure it to route math digits/Latin through Times New Roman:
```latex
\usepackage{mathspec}
\setmainfont{Times New Roman}
\setmathsfont(Digits,Latin)[Numbers={Lining,Proportional}]{Times New Roman}
% then xeCJK and everything else
```
**Verify:** `pdffonts main.pdf` — digits should appear as `TimesNewRomanPSMT`; only genuine math symbols like θ, ∼, ∂ should remain on CM.

### 7c. `calligra.sty` not found
**Symptom:** `! LaTeX Error: File 'calligra.sty' not found.`
**Cause:** TeX Live ships the font file `callig15` but not a `.sty` wrapper around it.
**Fix:** Remove `calligra` from the `\usepackage{}` list and declare the family inline:
```latex
\DeclareFontFamily{OT1}{callig}{}
\DeclareFontShape{OT1}{callig}{m}{n}{<-> s * [2.2] callig15}{}
\newcommand*{\calligra}{\usefont{OT1}{callig}{m}{n}}
```
This provides the same `\calligra` command used by the Thanks slide.

### 7d. `perpage.sty` not found
**Symptom:** `! LaTeX Error: File 'perpage.sty' not found.`
**Cause:** The `perpage` file ships as part of the `bigfoot` bundle in newer TeX Live, not under a standalone `perpage` package name.
**Fix:** `tlmgr install bigfoot`.

---

## Content Layout Issues

### 8. Frame overflow (Overfull vbox)
**Symptom:** Warning "Overfull \vbox" and content runs off the bottom of the slide.
**Cause:** Too much content for one frame.
**Fix:** 
- Split into multiple frames
- Reduce content (max 6 bullets, max 2 equations)
- Use `\small` or `\footnotesize` for supplementary text
- NEVER use `[shrink]` — it makes text unreadable

### 9. Table too wide for frame
**Symptom:** Table extends beyond the right margin.
**Cause:** Too many columns or wide cell content.
**Fix:** Wrap with `\resizebox{\textwidth}{!}{...}` or use `\small`/`\scriptsize` inside the table.

### 10. Figure too large in columns layout
**Symptom:** Figure overlaps with text column or overflows.
**Cause:** Using absolute width instead of relative sizing.
**Fix:** Use `height=0.55\textheight` for figures in columns, not `width=\textwidth`.

### 11. Equation number overlaps with text
**Symptom:** Equation number renders on top of the equation or falls off-frame.
**Cause:** Long equations with numbered mode.
**Fix:** Use `equation*` (unnumbered) for display equations, or `align*` for multi-line. Only number equations you'll reference later.

---

## Bibliography Issues

### 12. Bibliography not displayed
**Symptom:** `\bibliography{ref}` produces nothing, or shows `[?]` markers.
**Cause:** bibtex not run, or .bib file not found.
**Fix:** Run `bibtex main` after the first xelatex pass. Ensure `ref.bib` is in the same directory as main.tex.

### 13. Bibliography style issues
**Symptom:** References look wrong or have missing fields.
**Cause:** Using `\bibliographystyle{apalike}` but entries lack required fields.
**Fix:** Ensure each bib entry has at minimum: title, author, year, and either journal/booktitle.

### 14. Too many references for one slide
**Symptom:** References overflow the frame.
**Cause:** Many citations without `allowframebreaks`.
**Fix:** Use `\begin{frame}[allowframebreaks]` and `\tiny\bibliographystyle{apalike}` for the reference frame.

---

## Figure Issues

### 15. Figure format not supported
**Symptom:** Cannot include .eps or .ps files.
**Cause:** XeLaTeX doesn't support PostScript formats directly.
**Fix:** Convert to PDF or PNG. Use `\includegraphics` with .pdf or .png files only.

### 16. Low-resolution figures from PDF extraction
**Symptom:** Figures look blurry on slides.
**Cause:** Extraction zoom factor too low.
**Fix:** Use `fitz.Matrix(3, 3)` or higher for 3x zoom. For critical figures like architecture diagrams, use 4x.

### 17. PDF figures with transparent background
**Symptom:** Figure background is not white on the slide.
**Cause:** The extracted figure has a transparent background that shows the slide background.
**Fix:** When extracting with PyMuPDF, the default white background is preserved. If using other tools, explicitly set white background.

---

## Package Conflicts

### 18. pstricks + XeLaTeX
**Symptom:** Various errors related to PostScript specials.
**Cause:** pstricks relies on PostScript features not natively available in XeLaTeX.
**Fix:** Remove `\usepackage{pstricks}` entirely. Use `\includegraphics` or TikZ for diagrams instead.

### 19. Duplicate hyperref loading
**Symptom:** Warning about duplicate option declarations for hyperref.
**Cause:** Beamer loads hyperref automatically; explicit `\usepackage{hyperref}` causes a conflict.
**Fix:** Remove `\usepackage{hyperref}` from the preamble.

### 20. ctex vs xeCJK
**Symptom:** Font conflicts or unexpected formatting.
**Cause:** ctex package overrides font settings.
**Fix:** Use xeCJK directly (as in the Crimson template), not ctex. The template already handles this correctly.
