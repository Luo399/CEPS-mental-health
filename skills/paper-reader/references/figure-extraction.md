# Figure and table extraction (optional embedding)

This reference covers how to optionally embed key tables or figures from the paper into the HTML reading report. This is a lightweight version of nature-reader's figure extraction — paper-reader does not require full figure cropping, but can embed key visuals when they add significant value to the 8-dimension report.

## When to embed

Embed a table or figure **only** when it is central to a dimension's content:

- **Dimension 3 (研究设计)**: embed the main regression result table (Table 2 or Table 3 typically) if it summarizes the core identification strategy and key variables
- **Dimension 4 (核心发现)**: embed the main result table if the findings are best understood visually
- **Dimension 5 (机制与异质性)**: embed a mechanism test table or heterogeneity result table
- **Conceptual framework figure**: embed if the paper has a research framework diagram that clarifies the hypothesis structure

Do **not** embed:
- Summary statistics tables (dimension 3 text description is sufficient)
- Robustness check tables (mention in text, don't embed)
- Minor figures that don't directly support a dimension

## Embedding format

Use the `.key-visual` CSS class already defined in the HTML template:

```html
<div class="key-visual">
  <img src="data:image/png;base64,[base64编码的图片]" alt="Table 2: Main regression results">
  <div class="visual-caption">Table 2: [核心回归结果 — 基准模型]</div>
</div>
```

Or if the image is saved as a file:

```html
<div class="key-visual">
  <img src="[图片文件路径]" alt="Table 2: Main regression results">
  <div class="visual-caption">Table 2: [核心回归结果 — 基准模型]</div>
</div>
```

## Extraction method

1. Use the Read tool on the PDF to capture the specific page containing the table/figure
2. If the Read tool returns the table as readable text, consider rendering it as an HTML table instead of an image
3. If the table is only available as an image, crop it tightly (table content only, exclude page headers/footers)
4. For HTML tables, use this structure within the `.key-visual` div:

```html
<div class="key-visual">
  <table style="width:100%; font-size:0.78rem; border-collapse:collapse; margin-top:0.4rem;">
    <thead>
      <tr style="background:var(--ink); color:#fff;">
        <th style="padding:0.3rem; text-align:left;">Variable</th>
        <th style="padding:0.3rem; text-align:center;">(1)</th>
        <th style="padding:0.3rem; text-align:center;">(2)</th>
      </tr>
    </thead>
    <tbody>
      <tr style="border-bottom:1px solid var(--rule);">
        <td style="padding:0.3rem;">X</td>
        <td style="padding:0.3rem; text-align:center;">0.123***</td>
        <td style="padding:0.3rem; text-align:center;">0.456***</td>
      </tr>
    </tbody>
  </table>
  <div class="visual-caption">Table 2: 基准回归结果</div>
</div>
```

## Constraints

- Maximum 1 embedded visual per paper (to keep the report concise)
- If multiple tables are equally important, embed the main result table and mention others in text
- Always include the visual-caption with table/figure number and a short Chinese description
