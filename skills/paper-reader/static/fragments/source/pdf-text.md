# Source: selectable-text PDF

The PDF has an extractable text layer. This is the default and most common input format.

## Extraction rules

- Extract the text layer directly using the Read tool; do not OCR text that is already selectable.
- Process the entire document, not just the abstract or first pages.
- Watch for multi-column layouts: recover natural reading order rather than top-to-bottom raw stream order.
- Keep ligatures, hyphenated line breaks, superscripts, subscripts, and math intact; rejoin words split across line breaks.
- Note the page number for each major section (Introduction, Literature Review, Methodology, Results, Discussion, Conclusion) for source anchoring.

## Page tracking

Record approximate page boundaries for the paper's major sections:
- Title/Abstract → p.1
- Introduction → p.1-3
- Literature Review / Hypotheses → p.3-8
- Methodology / Research Design → p.8-12
- Results → p.12-20
- Discussion → p.20-24
- Conclusion → p.24-26

These page ranges are approximations that vary by paper. Use the actual page numbers observed during extraction. Tag each dimension's source anchor accordingly.

## Table and figure awareness

When extracting text, note the location of:
- Regression result tables (main results, robustness checks, mechanism tests)
- Conceptual framework diagrams or figures
- Summary statistics tables

Record their page numbers and table/figure numbers for optional embedding via `references/figure-extraction.md`.
