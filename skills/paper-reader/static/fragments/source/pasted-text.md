# Source: pasted text

The user pasted abstract, notes, or prose without a retrievable original file. This is the least structured input format.

## Extraction rules

- Work directly with the provided text content.
- If the user pasted only an abstract: fill dimensions 1-2 from the abstract, mark dimensions 3-6 as "信息不足：仅提供摘要文本", attempt dimension 7 based on abstract, skip or limit dimension 8.
- If the user pasted notes or a summary: use the provided content as-is for the dimensions it covers, mark gaps explicitly.
- If the user pasted substantial body text (multiple sections): treat it similarly to pdf-text extraction, filling all dimensions from the available content.

## Source anchoring

Since there are no page numbers, use section names or paragraph positions instead:

```html
<span class="dim-source">来源：[Introduction 部分]</span>
<span class="dim-source">来源：[用户粘贴文本]</span>
```

## Limitations note

Add a note to the HTML report when working from pasted text:

```html
<div class="disclaimer" style="background: #e6f7ff; border-color: #91d5ff;">
  <strong>来源提示：</strong>本报告基于用户提供的文本内容生成，非完整论文原文提取。
  部分维度可能因文本不完整而标注"信息不足"。建议提供完整 PDF 以获得最佳精读效果。
</div>
```

## Encourage structured input

If the pasted text is very short (under 200 characters), suggest the user provide either:
- The full PDF file path for complete analysis
- A DOI/arXiv ID for automated resolution
- At minimum, the abstract + methodology section for reasonable coverage
