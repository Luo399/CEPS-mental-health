---
name: paper-to-beamer
description: "Generate LaTeX Beamer presentations from academic papers. Use this skill whenever the user wants to create a Beamer/LaTeX presentation, academic slides, seminar talk slides, or paper reading slides from a research paper. Also trigger when the user mentions: 论文汇报PPT, 论文报告幻灯片, paper presentation, beamer slides, 做一个论文的PPT, 论文解读演示文稿, conference talk slides, or any request to turn a paper into slides. This skill handles the full pipeline: reading the paper, extracting figures, structuring slides, generating compilable LaTeX, and validating the output. Even if the user just says 'help me present this paper' or 'make slides for my lab meeting', this skill applies."
---

# Paper-to-Beamer: Academic Paper Presentation Generator

Transform any academic paper into a professional, compilable LaTeX Beamer presentation using the Crimson theme (`crimson.sty`) with XeLaTeX + xeCJK support.

## Quick Start

When this skill triggers, follow these phases in order:

1. **Read the paper** → understand structure, contributions, key figures/tables/equations
2. **Ask the user** → clarify preferences (language, duration, theme, figures)
3. **Prepare resources** → extract figures, build bibliography
4. **Generate LaTeX** → write main.tex following the slide structure patterns
5. **Validate** → check environments, braces, citations, figure files
6. **Compile** → if LaTeX is available, compile and verify
7. **Visual review** → **mandatory** — Read the compiled PDF page-by-page with the vision model, audit for layout/spacing/overlap/TOC density issues, then fix and recompile until clean

**Phase 7 is not optional.** A compile that "succeeds" can still produce broken layouts: figures overlapping body text, single-column TOC running off the page, oversized headings colliding with the nav bar. LaTeX does not flag these — only a visual pass catches them. Always perform Phase 7 before reporting the task complete.

---

## Phase 1: Read the Paper

Use the Read tool to read the paper PDF. Focus on extracting:

- **Title, authors, venue, year**
- **Paper type** (architecture, empirical, survey, theory — see mapping below)
- **Section structure** — map each section to slide allocation
- **Key contributions** — 3-5 bullet points
- **Important figures** — which ones are essential for the presentation
- **Key equations** — transcribe them accurately in LaTeX
- **Main results** — tables with numbers, comparisons
- **Conclusion** — takeaways and future impact

## Phase 2: Ask the User

Before generating, clarify these parameters. Use AskUserQuestion with these four questions:

1. **Language**: 中文为主+英文术语 (recommended) / 全英文 / 双语对照
2. **Duration**: 15-20 min (~15-18 slides) / 25-30 min (~25-27 slides, recommended) / 40-45 min (~35-40 slides)
3. **Logo / 校徽**: 不使用校徽 (recommended, default) / 上传自定义 Logo 图像
4. **Figures**: 从PDF截取 (recommended) / 用TikZ重绘 / 用drawio重绘

If the user picks **上传自定义 Logo 图像** in question 3, follow up with a plain-text question asking for the absolute path to a PNG file (e.g., `/Users/.../mylogo.png`). Do not proceed until you have a valid path — verify the file exists before Phase 3.

## Phase 3: Prepare Resources

### 3a. Auto-extract Figures and Tables

Run the extraction script from the working directory:

```bash
python3 ~/.claude/skills/paper-to-beamer/scripts/extract_assets.py paper.pdf --outdir figs
```

Dependencies (install on first use):
```bash
pip3 install PyMuPDF pdfplumber --user --break-system-packages -i https://pypi.org/simple/
```
`pdfplumber` is optional — without it, tables are screenshot only. PyMuPDF is required.

The script walks the PDF, locates every `Figure N` / `Fig. N` / `图 N` and `Table N` / `表 N` caption, and infers the surrounding content bbox:
- **Figures**: collects images + vector drawings above the caption (figures conventionally sit above their captions), clips to the caption's column in two-column layouts, renders at 3× zoom
- **Tables**: uses pdfplumber's ruling-line detector to find the table body near the caption; small tables (≤ 20 rows, ≤ 8 cols) are rebuilt as `booktabs` LaTeX so numbers stay crisp; wide tables fall back to screenshot

Outputs under `figs/`:
- `figure_1.png, figure_2.png, ...`
- `table_1.png` or `table_1.tex` (depending on size)
- `manifest.json` — indexed metadata consumed in Phase 3.5

**Verify extraction**: read a few figure PNGs with the Read tool to confirm they aren't clipped or contaminated with body text. If a figure looks wrong, re-extract that one manually with tighter coordinates:

```python
import fitz
doc = fitz.open("paper.pdf")
mat = fitz.Matrix(3, 3)
page = doc[PAGE_INDEX]
pix = page.get_pixmap(matrix=mat, clip=fitz.Rect(x0, y0, x1, y1))
pix.save("figs/figure_name.png")
```
Page coordinates: origin top-left, units are points (1/72 inch), standard page 612 × 792.

### 3b. Set Up Template Files

Copy template files from the skill's `assets/template/` directory to the working directory:
- `crimson.sty` → working directory
- `fonts/STKAITI.TTF` and `fonts/wingding.ttf` → `fonts/` subdirectory
- Keep existing `figs/` directory for extracted figures

If the template files already exist in the working directory (e.g., user cloned from Overleaf), skip this step.

### 3c. Build Bibliography

Create or expand `ref.bib` with all papers cited in the presentation. Use standard BibTeX format. The bibliography must include at minimum the paper being presented.

### 3d. Logo / 校徽 Placement

**Logo anchor point**: In Beamer, the title-page logo is controlled by `\titlegraphic{...}`, placed in the preamble between `\usepackage{crimson}` and `\begin{document}`. This is the single authoritative insertion site. When present, the logo renders on the title page directly below the date; when absent, nothing appears — the title page collapses cleanly.

Choose one branch based on the user's Phase 2 answer:

**Branch A — 不使用校徽 (default)**:
- Do **not** emit any `\titlegraphic` line.
- Do not copy any logo file into the working directory.

**Branch B — 上传自定义 Logo 图像**:
1. Verify the user-supplied PNG path exists. If it does not, stop and ask again.
2. Copy the PNG into the working directory as `figs/logo.png` (overwrite if present). Keeping the logo inside `figs/` avoids cluttering the project root and keeps it colocated with other graphics.
3. Emit this exact block in the preamble, right after `\usepackage{crimson}`:
   ```latex
   % === LOGO / 校徽 anchor ===
   \titlegraphic{\includegraphics[height=1.8cm,keepaspectratio]{figs/logo.png}}
   ```
4. **Sizing rule (proportional scaling)**: always specify `height=1.8cm` with `keepaspectratio`. Never give both `width` and `height` simultaneously — that would distort the aspect ratio. `1.8cm` is calibrated so a square校徽 (≈ 1.8×1.8 cm) sits cleanly below the date without crowding the title block. For a wide/horizontal logo, the command still renders at the same height, letting the width grow naturally to whatever the aspect ratio demands.
5. If the supplied PNG is transparent, it will blend with the title page background — no further work needed. If it has a solid background, warn the user that the logo may show a white rectangle against the crimson title banner.

## Phase 3.5: Assign Assets to Slides

Before writing any LaTeX, read `figs/manifest.json`. Each entry carries the asset's `caption`, `page`, `type`, `render`, and `path` — this is your catalog. For each asset, decide (a) whether to include it, and (b) which slide's argument it supports.

Do **not** apply hard-coded domain rules — the same mechanism must work for CS/ML, economics, biology, social science, theory, and so on. Use these cross-domain principles instead:

1. **Every asset must earn its place.** If you can't state which slide's argument an asset supports, drop it. A 25-min talk typically uses 4–8 assets, not all of them.
2. **Caption semantics drive placement.** The paper's own caption tells you the slide it belongs on. Read each caption carefully and match on meaning, not position:
   - Captions mentioning "architecture", "overview", "framework", "pipeline", "proposed", "our method" → method/approach slide
   - Captions mentioning "results on", "comparison with", "performance", "accuracy", "effect" → results slide
   - Captions mentioning "ablation", "without X", "effect of X", "sensitivity to X" → ablation slide
   - Captions mentioning "example", "case", "visualization", "qualitative" → motivation or qualitative slide
   - Captions mentioning "distribution", "statistics", "summary of data", "dataset" → data slide
   These keywords are hints, not a lookup table — a caption mentioning both "overview" and "results" belongs wherever its semantic weight lies.
3. **Page order is a weak prior.** The asset order in the paper roughly follows the presentation's natural flow. Break ties with this signal, but never use page order to override caption semantics.
4. **Prefer "main" / "overall" / "proposed" assets.** Any caption tagged with these words is almost always worth including — it's the paper's own signal of which asset is load-bearing.
5. **Respect the render type.** `render: "image"` → use `\includegraphics{path}`. `render: "latex"` → `\input{path}` inside a `table` environment, or inline the file content. Never screenshot a LaTeX-reconstructed table.

Write out your picks as a short plan before generating LaTeX — one line per asset: `figure_3 → 方法/整体架构 slide (caption: "Overall architecture of ...")`. This keeps the assignment auditable and prevents drift during generation.

## Phase 3.6: Identify Punchline Numbers

Before writing slides, scan the paper's abstract, introduction, and conclusion for **quantitative punchlines** — the numbers a reviewer or reader walks away remembering. Typical patterns:

- Headline percentages: "X% improvement", "covers ~Y% of surface area"
- Effect sizes / absolute scales: "10.2 M km²", "1,800 m elevation band"
- Statistical significance: "p = 1.07×10⁻⁶", "H(2) = 27.5"
- Ratios: "11× rebound", "4× reduction"

Collect 3–6 of these. They get first-class visual treatment in two places:

1. **Pitch slide** (Phase 4a): the three most headline-worthy numbers go in a three-column `\Huge` row.
2. **Inline highlighting**: wherever the number appears in a body slide, wrap it in `\alert{\textbf{...}}` so it reads at projection distance. Raw prose buries the punchline.

Do not mechanically alert every number — only the ones that actually make the argument. Over-alerting trains the audience to tune out red text.

## Phase 4: Generate LaTeX

### Template Structure

The generated `main.tex` must follow this structure:

```latex
% !TEX program = xelatex
\documentclass{beamer}

% ==== Fonts: mathspec MUST load before xeCJK/fontspec to catch math-mode digits ====
% Without mathspec, math-mode digits (e.g. $0.31^{\circ}$) fall back to Computer
% Modern and look visually inconsistent with body Times New Roman. mathspec
% routes math Digits+Latin through Times New Roman while leaving symbols (θ, ∼,
% ∂) on CM. This is the only place where the load order actually matters.
\usepackage{mathspec}
\setmainfont{Times New Roman}
\setsansfont{Times New Roman}
\setmonofont{Times New Roman}
\setmathsfont(Digits,Latin)[Numbers={Lining,Proportional}]{Times New Roman}

% ==== CJK ====
\usepackage[BoldFont,SlantFont]{xeCJK}
\setCJKmainfont[Path=fonts/]{STKAITI.TTF}
\setCJKsansfont[Path=fonts/]{STKAITI.TTF}
\setCJKmonofont[Path=fonts/]{STKAITI.TTF}

% ==== Packages — DO NOT include pstricks or hyperref ====
\usepackage{fontenc}
\usepackage{latexsym,amsmath,xcolor,multicol,booktabs}
% Inline calligra: TeX Live 2026 ships the font files (callig15) but not the
% .sty. Declaring the family inline avoids the "File `calligra.sty' not found"
% compile error. Used only by the Thanks slide.
\DeclareFontFamily{OT1}{callig}{}
\DeclareFontShape{OT1}{callig}{m}{n}{<-> s * [2.2] callig15}{}
\newcommand*{\calligra}{\usefont{OT1}{callig}{m}{n}}
\usepackage{graphicx,stackengine}
\usepackage{bm,amssymb,multirow}
\usefonttheme{serif}
\setbeamertemplate{navigation symbols}{}

% Metadata
\author{Paper Authors}
\title{Paper Title}
\subtitle{论文解读 / Paper Reading}
\institute{Venue Year}
\date{\today}
\usepackage{crimson}

% === LOGO / 校徽 anchor (Phase 3d) ===
% Branch A (不使用校徽): leave this block empty — do not emit \titlegraphic.
% Branch B (自定义 Logo): uncomment the line below; figs/logo.png is pre-copied.
% \titlegraphic{\includegraphics[height=1.8cm,keepaspectratio]{figs/logo.png}}

% Chinese captions
\setbeamertemplate{caption}[numbered]
\renewcommand\figurename{图}
\renewcommand\tablename{表}

% Footnotes
\usepackage{perpage}
\MakePerPage{footnote}

% Wingding itemize icons
\newfontfamily\wingdingfamily[Path=fonts/]{wingding.ttf}
\newcommand\headtoright{%
  \texorpdfstring{{\wingdingfamily\XeTeXglyph190\relax}}{>}}
\setbeamertemplate{itemize item}{\headtoright}
\setbeamertemplate{itemize subitem}{$\bullet$}
\setbeamertemplate{itemize subsubitem}{$\circ$}

\begin{document}
% ... slides ...
\end{document}
```

**Critical: Do NOT include `\usepackage{pstricks}` or `\usepackage{hyperref}`** — pstricks has XeLaTeX compatibility issues, and hyperref is auto-loaded by beamer.

**Critical: Auto-TOC slide duplication bug.** The `crimson.sty` theme has `\AtBeginSection` AND `\AtBeginSubsection` hooks that automatically insert a table-of-contents slide before every section and every subsection. This means:
- **Do NOT add a manual `\tableofcontents` frame** — the `\AtBeginSection` hook already handles this
- **Do NOT use `\subsection{}` commands** — each subsection triggers an extra auto-TOC slide, causing massive repetition. With 7 sections and 8 subsections, you'd get 15 auto-TOC slides polluting the presentation
- Only use `\section{}` for top-level divisions. Structure within a section using frame titles alone

### Paper Type → Slide Structure Mapping

Choose the structure based on the paper type:

Note: Slide counts below are **content frames only**. The `crimson.sty` theme auto-inserts a TOC slide before each `\section`, so the actual total = content frames + number of sections. Do NOT manually add `\tableofcontents` or `\subsection{}`.

### 4a. Mandatory Opening Sequence

Every presentation opens with **three slides in this exact order**, regardless of paper type:

1. **标题页 (Title page)** — `\titlepage` only.
2. **研究概览 (Overview) / Research Overview** — a one-paragraph formal summary plus 3 punchline numbers from Phase 3.6. Frame title must be a noun phrase (`研究概览` / `研究核心` / `Research Overview`); **never** use rhetorical/colloquial openers like `一句话讲完`, `三点说清楚`, `这篇论文讲了啥`. Template:
   ```latex
   \begin{frame}{研究概览}
     \begin{exampleblock}{核心论断}
       <formal 2-3 sentence summary: what problem, what approach, what result.
        Write as a research abstract — third person or passive voice, no
        rhetorical questions, no "我们" / "本文作者巧妙地...".>
     \end{exampleblock}
     \vfill
     \begin{columns}[T]
       \begin{column}{0.32\textwidth}\centering
         {\small <metric label>}\\[4pt]
         {\Large\alert{\textbf{<number 1>}}}\\[4pt]
         {\footnotesize <what it means>}
       \end{column}
       % ... 2 more columns
     \end{columns}
   \end{frame}
   ```
   This slide lets the audience answer "what problem, what method, what result" after 90 seconds. Do not skip it, even for short talks.
3. **核心贡献 / Core Contributions** — a declarative itemize listing 3–5 contributions. Avoid hook-style phrasing; each bullet should state one methodological or empirical claim.

### 4b. Paper Type → Slide Structure Mapping

Append the type-specific slide sequence AFTER the mandatory opening above.

#### Architecture Paper (e.g., Transformer, ResNet, BERT)
```
论文概述 (2 slides): 标题页 + 核心贡献
研究背景与动机 (3-4 slides): 前序工作 + 问题陈述 + 核心思想
模型架构 (8-10 slides): 整体架构 + 各组件详解 + 对比
训练细节 (2-3 slides): 数据/硬件 + 优化器 + 正则化
实验结果 (3-4 slides): 主实验 + 消融 + 泛化
总结与影响 (2 slides): 总结 + 后续影响
参考文献 (1 slide) + Thanks
```

#### Empirical Paper (e.g., scaling laws, benchmark papers)
```
论文概述 (2 slides)
研究背景 (3 slides): 领域现状 + 研究问题
实验设置 (3 slides): 数据集 + 模型 + 评估指标
实验结果 (6 slides): 主实验 + 分析 + 可视化
讨论 (2 slides)
总结 (2 slides)
参考文献 (1 slide) + Thanks
```

#### Survey Paper
```
论文概述 (2 slides)
领域概述 (3 slides): 定义 + 发展历程
分类体系 (3 slides): 方法分类
重点方法 (8 slides): 各代表性方法
对比分析 (3 slides): 性能/特点对比
未来展望 (2 slides)
参考文献 (1 slide) + Thanks
```

#### Theory Paper
```
论文概述 (2 slides)
预备知识 (4 slides): 符号 + 前置定理
主要结论 (8 slides): 定理 + 证明思路
应用 (3 slides)
总结 (2 slides)
参考文献 (1 slide) + Thanks
```

### Slide Content Guidelines

#### Content Density Rules
These prevent frame overflow — the single most common Beamer compilation annoyance:
- **Maximum 6 bullet points** per frame
- **Maximum 2 equations** per frame (unless using `align` for tightly related equations)
- **Tables wider than 10cm**: wrap with `\resizebox{\textwidth}{!}{...}`
- **Large tables**: show only the most relevant rows, not the entire table
- If a topic needs more space, **split across multiple frames** rather than shrinking

#### Beamer Environment Usage
- `block{}` — for definitions and neutral information
- `exampleblock{}` — for equations, examples, and key formulas
- `alertblock{}` — for warnings, problems, and limitations
- `columns` + `column` — for side-by-side figure+text layouts
- `[<+-| alert@+>]` on itemize — for incremental reveal with highlighting (use sparingly, only on contribution/motivation slides)
- `\pause` — for separating build-up from punchline

#### Figure Sizing
Beamer's `\textheight` is much smaller than articles. Use these as starting points:
- Full-frame figure: `height=0.78\textheight`
- Figure in a column: `height=0.55\textheight`
- Small inline figure: `width=0.3\linewidth`

#### Table Formatting
Always use `booktabs` (`\toprule`, `\midrule`, `\bottomrule`). Bold the best result. Use `\small` or `\footnotesize` for dense tables.

#### Section Lead-in (TOC Page Enrichment)
Auto-TOC pages from `\AtBeginSection` are visually repetitive — same TOC with different highlighting, 7× per talk. Use `\sectionlead{...}` (defined in `crimson.sty`) to attach a one-line italic lead-in to the TOC page of each section. Place it **immediately before** the `\section{}`:

```latex
\sectionlead{基于坡度与曲率的极小值带，将陆海过渡带形式化为可在全球 DEM 上逐像元计算的判据。}
\section{研究方法}
```

**Register**: The lead-in is addressed to a peer research audience, so write it as a declarative summary of the section's goal — not a rhetorical question, not a pep-talk hook.
- ✗ `本节要回答：火星古海洋到底争在哪里？` — rhetorical question, colloquial register
- ✗ `地球这关过了，现在把同一把尺子放到火星上看会怎样。` — self-indulgent narrator voice
- ✓ `回顾火星古海洋假说三十年的研究进程，并指出现有海岸线证据在方法层面的主要局限。` — declarative, states scope
- ✓ `以地球 ETOPO1 数据为基准，评估该判据在已知大陆架上的识别能力与分辨率稳健性。` — declarative, names the evaluation

The lead resets after each section, so omitting `\sectionlead{}` gives a vanilla TOC page. The refs section does not need a lead-in.

#### Math Style
- Never embed raw conversion constants like `57.29578`. Write `\cdot \tfrac{180}{\pi}` or drop the factor and specify units in prose.
- Wrap long formulas with `\displaystyle` when they appear in bullets (inline math defaults to cramped style).
- Prefer `\tfrac{}{}` over `\frac{}{}` in inline math to keep row height consistent.
- All digits and Latin letters in math mode should render in Times New Roman via `mathspec` (see preamble). If any number is still rendering in Computer Modern on compile, the mathspec load order is wrong — it must come **before** xeCJK.

#### Academic Register (学术组会语气)

The audience of a paper-reading presentation is a research group meeting (组会) or conference session — peers in the same subfield, not a general audience. The register must stay **formal, declarative, and third-person**. This is the single biggest cause of "AI flavor" feedback on generated slides, so enforce it throughout.

**Hard rules for Chinese content:**

1. **Frame titles are declarative noun phrases.** Never rhetorical questions, never punchline slogans, never slang.
   - ✗ `一句话讲完` / `三点带走` / `带回家的三句话`
   - ✗ `未来验证 —— 2030 将见分晓` / `什么是真正的 shelf`
   - ✗ `换个思路` / `再看一眼` / `把「平」写成像元判据`
   - ✓ `研究概览` / `主要结论` / `后续验证：ExoMars Rosalind Franklin 任务`
   - ✓ `Geomorphons：平坦地形的像元级判据` / `研究假设的提出`

2. **Block / alertblock / exampleblock titles follow the same rule.**
   - ✗ `核心困境` / `问题的要害` / `shelf 之内、shelf 之上` / `地球的启示`
   - ✓ `主要局限` / `方法层面的共同局限` / `候选 shelf 内的独立地质证据` / `地球类比：陆海过渡的带状结构`

3. **Sectionleads are declarative section-goal summaries**, not rhetorical setups. See the Section Lead-in section above for positive/negative examples.

4. **Banned sentence patterns (AI tells / colloquial register):**
   - ✗ `不是 X，而是 Y` → ✓ write the positive statement directly.
   - ✗ `与其 X，不如 Y` → ✓ just make the Y claim.
   - ✗ Chinese em-dash `——` used as a rhetorical flourish → ✓ use a comma, or split into two sentences. (Em-dashes are fine inside compound words like `河-海系统`.)
   - ✗ Full-width `（English term）` for English annotation → ✓ `中文术语，英文称 XXX` inline form. Half-width `(term)` is tolerated for one-word definitions but also discouraged.
   - ✗ Narrator-voice transitions: `让我们来看看` / `接下来我们` / `现在把它放到` / `这关过了` / `带回家的` / `见分晓`.
   - ✗ Evaluative hype: `精妙地` / `巧妙地` / `令人惊讶的是` / `不难发现` / `值得注意的是` / `大幅压缩` / `彻底解决`.
   - ✗ First-person self-reference in a paper-reading talk: `我们在这里证明` — use `本文 / 本研究 / 作者` instead.

5. **Body text stays in passive/third-person research-report voice.** Write as if narrating a Methods or Results section: "判据形式化为...", "在 5 km 分辨率下检出率为 69%", not "我们的做法是..." / "我们惊讶地发现...".

6. **Don't pedagogically simplify for insiders.** Assume the audience knows the subfield's vocabulary. Skip "首先解释一下什么是 shelf"-style hedges unless the term is genuinely cross-field.

7. **`\section{}` names are plain enumerations, not editorial headers.** When a paper has several parallel result sections, name them `结果 1` / `结果 2` / `结果 3` (or `Result 1` / `Result 2` in English mode), not `主要结果：XXX` / `关键洞察：XXX` / `核心发现：XXX`. Editorial adjectives like 主要 / 核心 / 关键 are filler that bloats the auto-TOC page and leaks AI register.
   - ✗ `\section{主要结果：Cer/Sis 缺失与机制转换}` / `\section{关键发现：受限 Vκ 库}` / `\section{核心结果 1}`
   - ✓ `\section{结果 1}` (with the descriptive subtitle placed in the sectionlead, not the section name)
   - ✓ `\section{研究背景}` / `\section{实验体系}` / `\section{讨论}` — these are genuine structural labels, not editorial wrappers, so they stay
   The rule is: if removing the adjective (主要/核心/关键) doesn't change what the section covers, the adjective is filler — remove it.

**When in doubt:** re-read the slide aloud in a hypothetical 组会. If it sounds like a social-media post or a YouTube pop-sci script, rewrite. The target register is closer to the paper's Introduction/Methods sections.

## Phase 5: Validate

Run a validation check before considering the output complete. Use this Python script inline:

```python
import re, os

with open("main.tex", "r") as f:
    content = f.read()

# 1. Environment balance
begins = re.findall(r'\\begin\{(\w+)\}', content)
ends = re.findall(r'\\end\{(\w+)\}', content)
begin_counts, end_counts = {}, {}
for b in begins: begin_counts[b] = begin_counts.get(b, 0) + 1
for e in ends: end_counts[e] = end_counts.get(e, 0) + 1
for env in set(list(begin_counts.keys()) + list(end_counts.keys())):
    bc, ec = begin_counts.get(env, 0), end_counts.get(env, 0)
    if bc != ec:
        print(f"MISMATCH: {env} begin={bc} end={ec}")

# 2. Brace balance
if content.count('{') != content.count('}'):
    print(f"BRACE MISMATCH: open={content.count('{')} close={content.count('}')}")

# 3. Frame count and auto-TOC check
frames = len(re.findall(r'\\begin\{frame\}', content))
sections = len(re.findall(r'\\section\{', content))
subsections = len(re.findall(r'\\subsection\{', content))
manual_toc = len(re.findall(r'\\tableofcontents', content))
print(f"Content frames: {frames}")
print(f"Auto-TOC slides (from crimson.sty): {sections} (section) + {subsections} (subsection)")
print(f"Total slides: {frames + sections + subsections}")
if subsections > 0:
    print(f"WARNING: {subsections} \\subsection found! crimson.sty auto-inserts TOC for each — remove them!")
if manual_toc > 0:
    print(f"WARNING: Manual \\tableofcontents found — redundant with crimson.sty \\AtBeginSection!")

# 4. Graphics files exist
for g in re.findall(r'\\includegraphics.*?\{([^}]+)\}', content):
    print(f"  {g}: {'OK' if os.path.exists(g) else 'MISSING'}")

# 5. Citations exist in bib
cites = re.findall(r'\\cite\{([^}]+)\}', content)
with open("ref.bib", "r") as f:
    bib_keys = re.findall(r'@\w+\{(\w+)', f.read())
for c in cites:
    for key in c.split(','):
        key = key.strip()
        if key not in bib_keys:
            print(f"  MISSING citation: {key}")

print("Validation complete.")
```

## Phase 6: Compile

If `xelatex` is available on the system:
```bash
xelatex main.tex && bibtex main && xelatex main.tex && xelatex main.tex
```

If not available, inform the user:
- Upload to Overleaf (set compiler to XeLaTeX)
- Or install TeX Live / MacTeX locally

---

## Phase 7: Visual Review of the Compiled PDF (Mandatory)

A successful compile means LaTeX ran without errors — it does **not** mean the slides look right. Phase 7 closes that gap. You must open `main.pdf` with the Read tool and inspect every page visually, then fix any layout issues and recompile. Skipping this phase is the single biggest source of complaints about the generated deck.

### 7a. How to Read the PDF

The Read tool accepts PDFs and returns each page as an image. Read in 10–20 page batches:

```
Read(file_path="/abs/path/main.pdf", pages="1-20")
Read(file_path="/abs/path/main.pdf", pages="21-40")
```

Scan every returned page as a rendered image — this is the only way to see spacing, overlap, and density problems.

### 7b. The Checklist — Inspect Each Page For

**(i) Spacing and width**
- Content frames: does body text extend past the right-edge safe area, or collide with the nav bar at the top?
- TOC pages: is the list single-column and spilling into / over the footer? (See 7c for the fix.)
- Empty space: if a frame has huge gaps between blocks, content is probably misaligned — review the `\begin{columns}` widths and column-break points.

**(ii) Short-vs-long content placement**
- Short related points (1–3 lines each) can share a frame.
- Long paragraphs, bulleted blocks with 6+ items, or figure+text combinations that already fill a frame must **not** be stuffed together. Split them onto separate frames.
- If you see one frame with an image AND a long bullet list AND a block, it is over-stuffed — split.

**(iii) Figure + content layout**
- When a figure sits next to body text via `columns`, check that text column's content doesn't overflow vertically past the figure's bottom. If it does, the text will wrap under the image and read as overlap.
- Figure sizing: `height=0.78\textheight` is the default but may be too tall for dense captions — drop to `0.72` if the text column has 6+ lines.
- Never put an `\includegraphics` right above a block in a single column — the figure will clip the block header. Always use `columns` OR `\vspace{0.3cm}` between figure and next element.

**(iv) TOC density**
- If the deck has 7+ sections, the auto-TOC page from `crimson.sty` **will overflow** in single-column layout. This is the most common Phase 7 failure. See 7c for the fix.

**(v) Over-stuffed headings / section names**
- Section names with `主要结果：XXX` / `关键洞察：YYY` balloon the TOC width and force line wraps. Enforce the plain enumeration rule (§Academic Register rule 7): `结果 1` / `结果 2` / ...

### 7c. Multi-Column TOC Patch (Apply When 5+ Sections)

`crimson.sty`'s default TOC is single-column. When the deck has 5 or more sections, the auto-TOC page will either overflow vertically or run into the footer. Fix it by wrapping the auto-TOC in a 2-column `multicols` block via a preamble patch in `main.tex` (do NOT edit `crimson.sty` — keep the theme clean):

```latex
% Two-column TOC patch — place AFTER \usepackage{crimson}
\usepackage{multicol}
\makeatletter
\renewcommand*{\beamer@sectionintoc}[5]{%
  \ifnum\c@section=#1\relax
    \def\beamer@toc@sectionstyle{shaded}%
  \else
    \def\beamer@toc@sectionstyle{show}%
  \fi
  \ifx\beamer@toc@sectionstyle\beamer@empty
  \else
    \vskip2pt
    \ifnum\c@section=#1\relax
      {\color{crimson}\textbullet~\small\bfseries #2}\par
    \else
      {\color{black!45}\textbullet~\small #2}\par
    \fi
  \fi
}
\AtBeginSection[]{%
  \begin{frame}{目录}
    \begin{multicols}{2}
      \tableofcontents[sectionstyle=show/shaded,subsectionstyle=hide]
    \end{multicols}
    \ifx\@currentsectionlead\@empty\else
      \vfill
      {\centering\parbox{0.85\textwidth}{\centering\footnotesize\color{crimson!85!black}\itshape\@currentsectionlead}\par}
      \global\let\@currentsectionlead\@empty
    \fi
  \end{frame}
}
\makeatother
```

This overrides `crimson.sty`'s `\AtBeginSection` hook with a 2-column version. The threshold for applying this patch is **5+ `\section{}` commands in the deck**; below that, the single-column default is fine.

**Reference look**: mimic a conventional journal/thesis PDF TOC — two columns of section names, each prefixed with a bullet or number, left-aligned, compact leading. Don't add page numbers (auto-TOC in beamer doesn't need them).

### 7d. Fix-then-Recompile Loop

After you identify issues from the visual scan:
1. Group the fixes by file (`main.tex` edits, preamble patches, figure sizing).
2. Apply them with Edit.
3. Re-run `xelatex && bibtex main && xelatex && xelatex`.
4. Re-read the PDF pages that had issues. Confirm they now render correctly.
5. Repeat until clean. Two fix-rounds is typical; more than three usually means you missed a systemic problem (wrong section-name convention, too many sections, figure-path mismatch).

### 7e. When to Stop

Phase 7 is complete when:
- Every page fits within the frame without overflow.
- No figure overlaps body text.
- TOC pages are readable in one glance (≤ 8 items per column; 2 columns if > 5 sections).
- Section names in the TOC are plain enumerations, not editorial headers.
- No frame is both over-stuffed and visually crowded.

Only then report the task complete.

---

## Known Issues and Solutions

Read `references/pitfalls.md` for the complete list. The most critical ones:

| Issue | Solution |
|-------|----------|
| pstricks breaks XeLaTeX | Don't include it — use `\includegraphics` instead |
| hyperref duplicate loading | Don't include it — beamer loads it automatically |
| Frame overflow (Overfull vbox) | Split content across frames; never use `[shrink]` |
| Chinese text shows as boxes | Ensure STKAITI.TTF is in `fonts/` with `Path=fonts/` |
| wingding icons missing | Ensure wingding.ttf is in `fonts/` |
| Bibliography not showing | Must run `bibtex main` between xelatex passes |
| Wide tables overflow | Use `\resizebox{\textwidth}{!}{...}` |
| PyMuPDF install fails | Try `-i https://pypi.org/simple/` to use official PyPI |
| Compilation engine wrong | Add `% !TEX program = xelatex` as first line |
| Auto-TOC slide explosion | Do NOT use `\subsection{}` or manual `\tableofcontents` — crimson.sty auto-inserts TOC at every `\section` and `\subsection` |
| Logo distorted on title page | Use `\titlegraphic{\includegraphics[height=1.8cm,keepaspectratio]{figs/logo.png}}` — never combine `width=` with `height=` |
| Logo file missing at compile | The custom PNG must be copied to `figs/logo.png` before compilation; verify in Phase 5 with the graphics-exists check |
| Extracted figure shows paper's own caption at 6pt below | Bug fixed in `extract_assets.py` — `figure_bbox` now clips strictly above `cap_bbox.y0`. If old PNGs still have this artifact, re-run the extraction script |
| Three layers of red feel oppressive (nav bar + title bar + footer) | `crimson.sty` uses `gray!12` footer with crimson text; `\alert{}` is pinned to crimson to stay on-theme |
| Math-mode digits render in Computer Modern even though body text is Times New Roman | Load `mathspec` **before** `xeCJK` and set `\setmathsfont(Digits,Latin)[Numbers={Lining,Proportional}]{Times New Roman}`. Verify with `pdffonts main.pdf` — digits should appear as `TimesNewRomanPSMT`; only math symbols (θ, ∼, ∂) may remain on CM |
| `calligra.sty` not found in TeX Live | TeX Live ships the font `callig15` but not the `.sty`. Declare the family inline: `\DeclareFontFamily{OT1}{callig}{}` + `\DeclareFontShape{OT1}{callig}{m}{n}{<-> s * [2.2] callig15}{}` + `\newcommand*{\calligra}{\usefont{OT1}{callig}{m}{n}}`. Remove `calligra` from the `\usepackage{}` line |
| `\beamer@collect@@body` runaway error → PDF truncated to a few pages | Usually caused by a `\begin{center}...\end{center}` environment inside an `\ifx\else\fi` conditional (e.g. inside `\AtBeginSection` of a theme file). The `center` env uses `\trivlist`, which clashes with beamer's fragile-frame body collector. Fix: replace with a `{\centering ... \par}` group |
| `perpage.sty` not found | The file is provided by the `bigfoot` bundle, not `perpage`. Install with `tlmgr install bigfoot` |
| Slides sound AI-flavored / colloquial ("一句话讲完", "带三句话回家", "见分晓") | See §Academic Register in Phase 4b. Frame titles and sectionleads must be declarative noun phrases / section-goal summaries, not rhetorical hooks |
