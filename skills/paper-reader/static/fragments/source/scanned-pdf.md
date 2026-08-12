# Source: scanned PDF (image-only)

The PDF is image-only or has an unreliable text layer. OCR is required before structured extraction.

## Extraction rules

- Attempt text extraction first. If the Read tool returns mostly empty or garbled content, the PDF is scanned.
- Inform the user: "该 PDF 为扫描版，部分内容可能无法完整提取。建议先进行 OCR 处理（推荐 Adobe Acrobat、ABBYY FineReader、或在线 OCR 工具），转换为可搜索文本后再提供。"
- If the user confirms they want to proceed without OCR, work with whatever text can be extracted and mark uncertain dimensions.
- If some pages have a text layer and others are scanned, treat the scanned pages with reduced confidence and note which pages are affected.

## Confidence marking

For scanned PDFs, add a confidence note to the HTML report header:

```html
<div class="disclaimer" style="background: #fff2f0; border-color: #ffccc7;">
  <strong>扫描版提示：</strong>本文为扫描版 PDF，以下精读报告基于可提取的文本内容生成。
  部分维度可能因 OCR 限制而不完整，已用 [信息不足] 标注。
</div>
```

## Dimension handling with incomplete text

- If abstract and introduction are readable but methodology/results are not: fill dimensions 1-2 from available text, mark dimensions 3-6 as "信息不足：扫描版 PDF 该部分无法提取"
- Always attempt dimension 7 (适配性) based on whatever information is available
- Skip dimension 8 (可引用句) if body text is not reliably extractable; note "扫描版 PDF，无法确认引用句准确性"
