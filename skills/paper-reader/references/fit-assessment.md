# Fit assessment (适配性判断细则)

This reference provides detailed rules for judging how well a paper fits the user's research, covering dimension 7 (适配性分析).

## Required user context

Before assessing fit, the user must have provided:
- **研究主题**: their current paper's topic/title
- **核心假设**: 1-3 hypotheses from their own research

If the user has not provided hypotheses, ask for them. Fit assessment without user hypotheses is guesswork.

## Three-level fit system

### 高适配 (fit-high, green badge)

Award when the paper meets **any** of these criteria:

1. **Direct hypothesis support**: the paper's findings directly confirm or contradict one of the user's hypotheses
   - Example: user's hypothesis is "X promotes Y", paper finds "X significantly increases Y" → 高适配
2. **Method replication**: the paper's research design (identification strategy, data source, variable construction) can be directly replicated or adapted for the user's research
   - Example: paper uses DID with a policy shock that the user also studies → 高适配
3. **Core theoretical framework**: the paper's theoretical foundation is central to the user's literature review or theoretical framework chapter
   - Example: paper proposes the mechanism "X→M→Y" that the user's hypothesis 2 relies on → 高适配

### 中适配 (fit-mid, orange badge)

Award when the paper meets **any** of these criteria:

1. **Background support**: provides empirical context, industry background, or policy environment description useful for the user's introduction
   - Example: paper describes the regulatory history of the industry the user studies → 中适配
2. **Partial method reference**: some aspect of the research design is useful (e.g., variable definition, data cleaning approach) but the overall design doesn't match
   - Example: paper's robustness check method is applicable → 中适配
3. **Comparison literature**: serves as a contrast or counter-argument in the user's literature review
   - Example: paper finds X inhibits Y (opposite to user's hypothesis) → 中适配

### 低适配 (fit-low, gray badge)

Award when:

1. The paper is tangentially related to the user's research field but has no direct connection to their hypotheses or methodology
2. The paper was included for completeness (e.g., a seminal paper in the broader field) but doesn't map to specific writing sections
3. **Always explain why** it's included even when low fit: "低适配：与用户研究主题关联弱，但可作为方法论参考（[具体方法]）"

## Dimension 7 output format

```html
<div class="dim-card highlight full-width">
  <div class="dim-label"><span class="dim-num">7</span> 适配性分析</div>
  <div class="dim-content">
    <strong>适配等级：高适配</strong><br>
    <strong>对应假设：</strong>支撑用户假设 2（[复述用户假设2的具体内容]）<br>
    <strong>对应章节：</strong>文献综述第三节 / 机制分析<br>
    <strong>具体价值：</strong>本文提供了 X 通过 M 影响 Y 的实证证据，可直接用于支撑用户论文中 [具体段落/论证环节] 的论述
  </div>
  <span class="dim-source">来源：p.5, p.18-20</span>
</div>
```

## Common mistakes to avoid

- **Do not** inflate fit level to please the user. If a paper is low fit, say so clearly.
- **Do not** assess fit based on topic similarity alone. A paper about "digital transformation" and a user studying "digital transformation" is not automatically high fit — assess whether the specific hypotheses and methods align.
- **Do not** leave dimension 7 vague. "有一定参考价值" is not acceptable. Must specify hypothesis number and chapter.
- **Do not** use 中适配 as a safe default. Make a clear judgment: 高 or 低 is better than a non-committal 中.
