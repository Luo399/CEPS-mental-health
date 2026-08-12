# Source tracing (lightweight)

This reference expands on how to assign source anchors to each dimension card. Unlike nature-reader's full `source_map.json`, paper-reader uses a lightweight page-level anchoring system.

## Anchor format

Every dimension card in the HTML report includes a source anchor:

```html
<span class="dim-source">来源：p.[页码]</span>
```

## Assignment rules

### Per-dimension primary source pages

| 维度 | Primary source location | Typical pages |
|------|------------------------|---------------|
| 1. 研究问题 | Introduction, last paragraph of intro | p.1-3 |
| 2. 核心假设 | End of literature review or dedicated hypothesis section | p.5-8 |
| 3. 研究设计 | Methodology / Data section | p.8-14 |
| 4. 核心发现 | Results section, main regression table discussion | p.14-20 |
| 5. 机制与异质性 | Mechanism analysis / heterogeneity subsection | p.20-24 |
| 6. 研究贡献与局限 | Discussion or Conclusion | p.24-28 |
| 7. 适配性 | Synthesized from all above; anchor to the most relevant | varies |
| 8. 可引用句 | Exact page where each quote appears | varies |

### Page range notation

- Single page: `来源：p.5`
- Page range: `来源：p.3-5`
- Multiple locations: `来源：p.3, p.12`
- Section-based (for pasted text / DOI-only): `来源：[Introduction 部分]`

### When page numbers are unavailable

- **Scanned PDF**: mark as `来源：p.[?](扫描版)` for unreadable sections
- **DOI/abstract only**: mark as `来源：[摘要]`
- **Pasted text**: mark as `来源：[用户提供的文本]`

## Follow-up grounding

When the user asks a follow-up question about a specific dimension:

1. Identify the source page(s) from the dim-source tag
2. If the original text is still in context, answer from it directly
3. If not in context, re-read the relevant page(s) of the PDF
4. Cite the page number in the answer: "根据原文 p.5-6 的假设推导..."

Do not answer from memory when the user asks about specific claims. Always verify against the source.
