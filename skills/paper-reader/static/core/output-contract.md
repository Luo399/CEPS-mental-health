# Output contract

Prefer this output:

- `reading-report.html` — the primary deliverable, self-contained HTML file
- `reading-notes.md` — optional Markdown companion for quick reference (only if user requests)

Do not hide missing information. If a dimension cannot be filled, label it as "信息不足" with a brief explanation.

## Pre-response verification

Before final response, verify:

- `reading-report.html` contains all 8 dimensions for every paper
- dimension 7 (适配性) has an explicit fit level (高/中/低) and maps to user's hypothesis number
- dimension 8 (可引用句) has 2-3 verbatim sentences with author + year + page references
- single-paper summary (dimensions 1-6) is within 300 Chinese characters
- batch mode (if applicable) includes the 横向对比表 with all papers listed
- each dimension card has at least one source page anchor
- the HTML file is valid and self-contained (no broken asset links)
- fit badge color class matches the declared fit level (`fit-high`/`fit-mid`/`fit-low`)

If any check fails, fix before delivering. Do not deliver an incomplete report silently.

## HTML report template

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>精读拆解报告：[研究主题]</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&family=Noto+Serif+SC:wght@400;600;700&display=swap');

  :root {
    --bg: #fafafa;
    --bg2: #f0f0f0;
    --ink: #1a1a1a;
    --muted: #666;
    --rule: #ddd;
    --accent: #c0392b;
    --accent2: #2980b9;
    --card-bg: #ffffff;
    --fit-high: #27ae60;
    --fit-mid: #f39c12;
    --fit-low: #95a5a6;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'Noto Sans SC', sans-serif;
    background: var(--bg);
    color: var(--ink);
    font-size: 15px;
    line-height: 1.8;
    -webkit-font-smoothing: antialiased;
  }

  .container {
    max-width: 960px;
    margin: 0 auto;
    padding: 2rem 2rem 4rem;
  }

  /* Header */
  .header {
    text-align: center;
    padding: 3rem 0 2rem;
    border-bottom: 2px solid var(--accent);
    margin-bottom: 2rem;
  }
  .header h1 {
    font-family: 'Noto Serif SC', serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 0.5rem;
  }
  .header .subtitle {
    font-size: 0.95rem;
    color: var(--muted);
    font-weight: 300;
  }
  .header .meta {
    font-size: 0.8rem;
    color: var(--muted);
    margin-top: 1rem;
    opacity: 0.7;
  }

  /* Paper section */
  .paper-section {
    margin-bottom: 3rem;
  }
  .paper-header {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--rule);
  }
  .paper-number {
    flex-shrink: 0;
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 50%;
    background: var(--accent);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.9rem;
  }
  .paper-info h2 {
    font-family: 'Noto Serif SC', serif;
    font-size: 1.15rem;
    font-weight: 700;
    line-height: 1.5;
    margin-bottom: 0.3rem;
  }
  .paper-info .citation {
    font-size: 0.82rem;
    color: var(--muted);
  }
  .paper-info .citation .journal {
    font-style: italic;
    font-weight: 500;
    color: var(--ink);
  }

  /* Fit badge */
  .fit-badge {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.2rem 0.6rem;
    border-radius: 3px;
    color: #fff;
    margin-left: 0.5rem;
    vertical-align: middle;
  }
  .fit-high { background: var(--fit-high); }
  .fit-mid { background: var(--fit-mid); }
  .fit-low { background: var(--fit-low); }

  /* Dimension cards */
  .dim-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }
  .dim-card {
    background: var(--card-bg);
    border: 1px solid var(--rule);
    border-radius: 6px;
    padding: 1.2rem;
    transition: box-shadow 0.2s;
  }
  .dim-card:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
  .dim-card.full-width {
    grid-column: 1 / -1;
  }
  .dim-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--accent);
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.3rem;
  }
  .dim-label .dim-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.3rem;
    height: 1.3rem;
    border-radius: 50%;
    background: var(--accent);
    color: #fff;
    font-size: 0.6rem;
    font-weight: 700;
  }
  .dim-card.highlight {
    border-color: var(--accent);
    border-width: 2px;
    background: #fffafa;
  }
  .dim-card.highlight .dim-label {
    color: var(--accent);
    font-size: 0.8rem;
  }
  .dim-card.highlight .dim-label .dim-num {
    background: var(--accent);
  }
  .dim-content {
    font-size: 0.88rem;
    line-height: 1.7;
    color: #333;
  }
  .dim-source {
    display: block;
    margin-top: 0.4rem;
    font-size: 0.7rem;
    color: var(--muted);
    opacity: 0.7;
  }

  /* Quotable sentences */
  .quote-list {
    margin-top: 0.5rem;
  }
  .quote-item {
    font-size: 0.85rem;
    line-height: 1.7;
    padding: 0.5rem 0.8rem;
    background: var(--bg);
    border-radius: 4px;
    border-left: 3px solid var(--accent2);
    margin-bottom: 0.5rem;
    color: #444;
  }
  .quote-item .quote-ref {
    font-size: 0.75rem;
    color: var(--muted);
    display: block;
    margin-top: 0.2rem;
  }

  /* Key table/figure embed (optional) */
  .key-visual {
    margin-top: 0.5rem;
    padding: 0.8rem;
    background: var(--bg2);
    border-radius: 4px;
    font-size: 0.82rem;
    color: var(--muted);
  }
  .key-visual img {
    max-width: 100%;
    border-radius: 4px;
    margin-top: 0.4rem;
  }
  .key-visual .visual-caption {
    font-size: 0.78rem;
    color: var(--muted);
    margin-top: 0.3rem;
  }

  /* Comparison table (batch mode) */
  .compare-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1.5rem;
    font-size: 0.85rem;
  }
  .compare-table thead th {
    background: var(--ink);
    color: #fff;
    font-weight: 500;
    padding: 0.6rem 0.8rem;
    text-align: left;
  }
  .compare-table tbody td {
    padding: 0.6rem 0.8rem;
    border-bottom: 1px solid var(--rule);
    vertical-align: top;
    line-height: 1.5;
  }
  .compare-table tbody tr:hover { background: #f5f5f5; }

  /* Section divider */
  .section-divider {
    border: none;
    border-top: 1px dashed var(--rule);
    margin: 3rem 0;
  }

  /* Disclaimer */
  .disclaimer {
    margin-top: 3rem;
    padding: 1.2rem 1.5rem;
    background: #fffbe6;
    border: 1px solid #ffe58f;
    border-radius: 6px;
    font-size: 0.82rem;
    color: #666;
    line-height: 1.7;
  }
  .disclaimer strong { color: var(--ink); }

  /* Responsive */
  @media (max-width: 768px) {
    .container { padding: 1rem 1rem 2rem; }
    .header h1 { font-size: 1.4rem; }
    .dim-grid { grid-template-columns: 1fr; }
    .paper-header { flex-direction: column; gap: 0.5rem; }
  }
</style>
</head>
<body>
<div class="container">

<div class="header">
  <h1>精读拆解报告</h1>
  <div class="subtitle">[研究主题] — 结构化精读 [N] 篇</div>
  <div class="meta">整理时间：[当前年月] &nbsp;|&nbsp; 单篇凝练 ≤300字（不含引用句）</div>
</div>

<!-- ==================== 单篇精读区块 ==================== -->
<!-- 每篇论文重复以下结构，paper-number 递增 -->

<div class="paper-section">

  <!-- 论文标题区 -->
  <div class="paper-header">
    <div class="paper-number">1</div>
    <div class="paper-info">
      <h2>[论文标题] <span class="fit-badge fit-high">高适配</span></h2>
      <div class="citation">
        [作者姓, 首字母] et al. ([年份]). <span class="journal">[期刊名]</span>, [卷](期), [页码].
      </div>
    </div>
  </div>

  <!-- 8 维度卡片网格 -->
  <div class="dim-grid">

    <!-- 维度 1：研究问题 -->
    <div class="dim-card">
      <div class="dim-label"><span class="dim-num">1</span> 研究问题</div>
      <div class="dim-content">[1句话概括论文核心研究问题]</div>
      <span class="dim-source">来源：p.[页码]</span>
    </div>

    <!-- 维度 2：核心假设 -->
    <div class="dim-card">
      <div class="dim-label"><span class="dim-num">2</span> 核心假设</div>
      <div class="dim-content">[1-2句话概括主要假设及推导逻辑]</div>
      <span class="dim-source">来源：p.[页码]</span>
    </div>

    <!-- 维度 3：研究设计 -->
    <div class="dim-card">
      <div class="dim-label"><span class="dim-num">3</span> 研究设计</div>
      <div class="dim-content">[数据、样本、方法、识别策略]</div>
      <span class="dim-source">来源：p.[页码]</span>
      <!-- 可选：嵌入关键表格图片 -->
      <!--
      <div class="key-visual">
        <img src="[表格图片路径]" alt="[Table X]">
        <div class="visual-caption">Table X: [表格说明]</div>
      </div>
      -->
    </div>

    <!-- 维度 4：核心发现 -->
    <div class="dim-card">
      <div class="dim-label"><span class="dim-num">4</span> 核心发现</div>
      <div class="dim-content">[1-2句话概括主要实证结果]</div>
      <span class="dim-source">来源：p.[页码]</span>
    </div>

    <!-- 维度 5：机制与异质性 -->
    <div class="dim-card">
      <div class="dim-label"><span class="dim-num">5</span> 机制与异质性</div>
      <div class="dim-content">[中介机制、调节效应、subgroup差异]</div>
      <span class="dim-source">来源：p.[页码]</span>
    </div>

    <!-- 维度 6：研究贡献与局限 -->
    <div class="dim-card">
      <div class="dim-label"><span class="dim-num">6</span> 研究贡献与局限</div>
      <div class="dim-content">[理论贡献+方法创新+主要局限]</div>
      <span class="dim-source">来源：p.[页码]</span>
    </div>

    <!-- 维度 7：适配性（核心维度，高亮+全宽） -->
    <div class="dim-card highlight full-width">
      <div class="dim-label"><span class="dim-num">7</span> 适配性分析</div>
      <div class="dim-content">
        <strong>适配等级：[高/中/低]</strong><br>
        <strong>对应假设：</strong>[支撑用户第几条假设 / 哪个具体假设内容]<br>
        <strong>对应章节：</strong>[引言/文献综述/研究设计/机制分析/异质性分析等]<br>
        <strong>具体价值：</strong>[一句话说明这篇论文对用户研究的具体用处]
      </div>
      <span class="dim-source">来源：p.[页码]</span>
    </div>

    <!-- 维度 8：可引用句（核心维度，高亮+全宽） -->
    <div class="dim-card highlight full-width">
      <div class="dim-label"><span class="dim-num">8</span> 可引用句</div>
      <div class="dim-content quote-list">
        <div class="quote-item">
          "[原文摘录的学术表达，可直接用于文献综述或论证]"
          <span class="quote-ref">— [作者姓] et al. ([年份]), p. [页码]</span>
        </div>
        <div class="quote-item">
          "[第二条可引用句]"
          <span class="quote-ref">— [作者姓] et al. ([年份]), p. [页码]</span>
        </div>
      </div>
      <span class="dim-source">来源：p.[页码]</span>
    </div>

  </div>
</div>

<!-- 第二篇论文用 hr 分隔 -->
<hr class="section-divider">

<!-- 批量模式：横向对比表 -->
<div class="paper-section" style="margin-top: 2rem;">
  <h2 style="font-family: 'Noto Serif SC', serif; font-size: 1.15rem; margin-bottom: 1rem; color: var(--ink);">横向对比汇总</h2>
  <table class="compare-table">
    <thead>
      <tr>
        <th style="width:20%">论文</th>
        <th style="width:20%">研究问题</th>
        <th style="width:25%">方法与数据</th>
        <th style="width:20%">核心结论</th>
        <th style="width:15%">适配性</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>[作者 年份]</td>
        <td>[核心问题]</td>
        <td>[方法+数据]</td>
        <td>[核心结论]</td>
        <td><span class="fit-badge fit-high">高</span></td>
      </tr>
      <tr>
        <td>[作者 年份]</td>
        <td>[核心问题]</td>
        <td>[方法+数据]</td>
        <td>[核心结论]</td>
        <td><span class="fit-badge fit-mid">中</span></td>
      </tr>
    </tbody>
  </table>
</div>

<!-- 免责声明 -->
<div class="disclaimer">
  <strong>使用说明：</strong>本精读报告基于原文自动抽取生成，所有概括均基于论文原文内容。<strong>维度 7（适配性）和维度 8（可引用句）为核心输出项</strong>，直接对接论文写作。建议在使用可引用句前，对照原文确认措辞准确性。扫描版 PDF 可能导致抽取不完整，建议使用文本版 PDF 或先进行 OCR 处理。
</div>

</div>
</body>
</html>
```

## Card filling rules

### 8-dimension filling spec

| 维度 | 字数要求 | 填写要点 |
|------|---------|---------|
| 1. 研究问题 | 1句话 | 用"本文研究X对Y的影响/关系"句式 |
| 2. 核心假设 | 1-2句话 | 列出主假设 + 推导逻辑（基于什么理论/机制推导） |
| 3. 研究设计 | 1-2句话 | 数据来源+样本量+核心变量+识别策略（DID/IV/RDD等） |
| 4. 核心发现 | 1-2句话 | 主回归结果，用"发现X显著促进/抑制Y"句式 |
| 5. 机制与异质性 | 1-2句话 | 中介渠道+调节变量+subgroup差异，择要列出 |
| 6. 贡献与局限 | 1-2句话 | 贡献：理论/方法/政策；局限：数据/方法/外推性 |
| 7. 适配性 | 3-4句话 | **必须**指出对应哪条假设、哪个章节、具体价值 |
| 8. 可引用句 | 2-3句 | 原文摘录，学术表达精准，适合放入文献综述 |

### Source anchor format

Each dimension card must include a source page reference in this format:

```html
<span class="dim-source">来源：p.[页码]</span>
```

If a dimension draws from multiple pages, list the primary page:
- `来源：p.3-5`
- `来源：p.12`

This provides lightweight traceability without the overhead of a full source_map.json.

### Fit badge rules

The fit badge class must match the declared fit level in dimension 7:
- 高适配 → `fit-badge fit-high`
- 中适配 → `fit-badge fit-mid`
- 低适配 → `fit-badge fit-low`

### Quotable sentence rules

- Must be verbatim from the original text, not paraphrased
- Prioritize: theoretical framework definitions, core mechanism articulation, research contribution statements
- Avoid: pure data descriptions, simple table/figure recaps
- 2-3 sentences per paper, with page references for user cross-checking
