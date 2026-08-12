# Core principles (paper-reader)

Use this skill to turn a research paper into a structured 8-dimension reading report. The default output should read like a research assistant's concise briefing, not a full-paper translation:

- extract and condense, do not reproduce full paragraphs
- anchor every dimension to the user's own research (hypotheses, chapters, writing sections)
- preserve exact quotable sentences with page references for direct citation use
- attach lightweight source anchors (page numbers) for traceability
- output a self-contained HTML file (`reading-report.html`) by default

This skill is for journal articles, working papers, preprints, and conference proceedings in economics, management, finance, and social sciences. It is optimized for the researcher who needs to quickly judge a paper's value and know exactly how to use it.

## Non-negotiable defaults

When the user asks for 精读论文, 读论文, 拆解文献, 论文解析, or any equivalent trigger, produce an 8-dimension structured report by default.

Do not replace the report with:

- a full-paper Chinese-only summary without the 8-dimension structure
- a bilingual paragraph-by-paragraph translation (that is a different skill)
- a list of key points without fit assessment
- only the abstract or selected highlights

If constraints prevent full processing, still create a draft report and clearly label missing dimensions or low-confidence extractions. Do not switch to a generic summary.

## Core principle

Condense for actionability, not for completeness. The report must answer: "What is this paper about, and how do I use it in my own research?" Keep each dimension to 1-2 sentences. The 300-word cap applies to dimensions 1-6 (excluding dimension 7 fit analysis and dimension 8 quotable sentences).

Dimension 7 (适配性) is the core output — it must explicitly state which of the user's hypotheses this paper supports, which writing chapter it maps to, and what specific value it provides.

Dimension 8 (可引用句) provides ready-to-use academic expressions extracted verbatim from the original, with author + year + page annotations.

## Mandatory 8 dimensions

Every paper must be analyzed along these 8 dimensions, no more, no less, no merging:

1. **研究问题** — the core question the paper asks (1 sentence)
2. **核心假设** — main hypotheses and their logical derivation (1-2 sentences)
3. **研究设计** — data source, sample, variable definitions, identification strategy (1-2 sentences)
4. **核心发现** — main empirical results (1-2 sentences)
5. **机制与异质性** — mediating mechanisms, moderating effects, subgroup analyses (1-2 sentences)
6. **研究贡献与局限** — theoretical contribution + methodological innovation + limitations (1-2 sentences)
7. **适配性分析** — mapping to user's hypotheses and writing chapters (3-4 sentences, full-width highlight)
8. **可引用句** — verbatim academic expressions from original text (2-3 sentences, with page refs)

## Batch processing

- Maximum 10 papers per batch (recommended 5-8 for quality).
- Each paper gets an independent full 8-dimension report.
- Batch summary ends with a横向对比表 (research question, method, core conclusion, fit level — four columns).
- Sort by fit level descending (high → mid → low).

## Copyright caution

For copyrighted publisher PDFs, keep chat responses short and point to the local HTML file. In the HTML report, keep dimension content as condensed analysis, not large verbatim reproduction. Only dimension 8 (可引用句) contains verbatim text, limited to 2-3 short sentences per paper.

## Quality bar

Good output feels like a research assistant briefing, not a machine-generated dump. It should let a researcher:

- judge a paper's value in under 60 seconds
- know exactly which hypothesis or chapter this paper supports
- grab quotable sentences for literature review without re-reading the original
- compare multiple papers at a glance via the batch comparison table
