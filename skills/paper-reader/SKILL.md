---
name: paper-reader
description: "PDF文献结构化精读与信息抽取技能。当用户提供PDF论文文件并需要精读拆解、提取核心信息、生成结构化阅读报告时触发。触发词包括但不限于：精读论文、读论文、拆解文献、论文解析、帮我读这篇论文、提炼论文核心、结构化阅读、批量读论文、论文精读报告。"
version: 2.1.0
author: 光年进化 (科研人员), refactored into static/dynamic layers
---

# 精读拆解 · 结构化信息抽取 — Router

Do not try to apply the reading logic from memory or from this router. Always load fragments from disk as described below.

## Routing protocol

### 1. Parallel load core

Read these files in one pass:
- `manifest.yaml`
- `static/core/principles.md`
- `static/core/workflow.md`
- `static/core/output-contract.md`

### 2. Detect source format

Decide the `source_format` value:
- `pdf-text` — selectable-text PDF (default)
- `scanned-pdf` — image-only or OCR-required PDF
- `doi-url` — bare DOI, arXiv ID, or publisher URL
- `pasted-text` — pasted abstract, prose, or notes

State the detected value in one short line. A source may map to more than one value (e.g. DOI → PDF); load the resolution fragment first.

### 3. Load matching fragment(s)

Read the file mapped for the detected `source_format`. Do **not** read every fragment. Load only what step 2 selected.

### 4. Build the report

Apply loaded fragments in priority order:
1. Core principles — 8-dimension extraction, 300-word cap, user-research anchoring
2. Source-format fragment — text/figure/table extraction for this input
3. Reading workflow — four-step extraction-to-report process
4. Output contract — HTML template, verification checklist

Load `references/` on demand per the manifest's `on_demand` table.

If source cannot be resolved or PDF is unreadable, still create a draft report with missing content clearly labeled. Do not switch to a generic summary.

### 5. References on demand

- Source block ID assignment / page anchoring → `references/source-tracing.md`
- Key tables/figures extraction → `references/figure-extraction.md`
- Fit level assessment / hypothesis mapping → `references/fit-assessment.md`
- Quotable sentences / citation format → `references/quotable-sentences.md`
