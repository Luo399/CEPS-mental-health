# Reading workflow

Run these four steps for any paper-reading job. Steps 1-2 build the extraction, step 3 produces the report, step 4 covers follow-up.

## 1. Extract text from source

The source-format fragment loaded for this job covers how to extract from the specific input. At a high level:

- For PDF (text or scanned): extract full text using Read tool, process entire document
- For DOI/URL: resolve to obtainable full text or fall back to abstract + metadata
- For pasted text: work with whatever the user provides

**Required user inputs** (ask if not provided):
- **PDF file(s)** or source material
- **研究主题**: user's current research topic / paper title
- **核心假设**: user's core hypotheses (1-3), used for fit assessment

**Optional user inputs**:
- **重点关注维度**: user can specify dimensions of interest (does not suppress other dimensions)
- **语言偏好**: output language defaults to Chinese; English paper titles and quotable sentences keep English original

Process the entire document, not just the abstract or first pages. Watch for multi-column layout issues in PDF extraction.

## 2. Structured 8-dimension extraction

From the extracted text, pull information for all 8 dimensions. Follow the filling rules in `output-contract.md`.

For each paper:
- Identify the research question in one sentence using "本文研究X对Y的影响/关系" phrasing
- Extract hypotheses and their theoretical derivation logic
- Capture data source, sample size, core variables, and identification strategy (DID/IV/RDD/etc.)
- Summarize main regression results using "发现X显著促进/抑制Y" phrasing
- Note mediating channels, moderating variables, subgroup differences
- Assess theoretical contribution, methodological innovation, and limitations
- Map to user's research: which hypothesis, which chapter, what specific value (load `references/fit-assessment.md`)
- Select 2-3 quotable sentences with page references (load `references/quotable-sentences.md`)

Assign lightweight source anchors: tag each dimension with the primary source page number(s). For detailed source tracing rules, load `references/source-tracing.md`.

If the paper contains key tables or figures (regression results, conceptual frameworks), note them for optional embedding (load `references/figure-extraction.md`).

## 3. Generate HTML reading report

Build `reading-report.html` following the template and CSS in `output-contract.md`. The report must:

- Use the standard header with research topic and paper count
- Render each paper as a numbered section with 8-dimension card grid
- Highlight dimension 7 (适配性) and dimension 8 (可引用句) as full-width accent cards
- Show fit badge (高适配/中适配/低适配) on each paper title
- Attach source page anchors to each dimension card
- For batch mode, append the 横向对比表 at the end
- Include the disclaimer block at the bottom

Single-paper summary (dimensions 1-6): ≤300 Chinese characters, excluding dimension 7 and 8.

## 4. Follow-up support

After the report is generated:
- If the user asks about a specific dimension or paper, refer back to the report and cite the source page
- If the user wants to refine fit assessment, re-evaluate against updated hypotheses
- If the user asks for more quotable sentences, re-scan the original and append
