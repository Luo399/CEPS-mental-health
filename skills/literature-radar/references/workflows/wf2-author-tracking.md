# 工作流 2：按作者/团队追踪

**目的**：追踪特定学者或研究团队在核心期刊中的发表记录。

**使用**：[去重引擎](../dedup-engine.md)

## 流程

### 1. 确认目标

- 目标学者姓名（中英文）
- 目标机构（可选，用于消歧同名学者）
- ORCID 或 Google Scholar ID（如有，最精准）

### 2. 检索

- **WebSearch**：`"作者名" "期刊名" site:scholar.google.com` 或 `"作者名" "期刊名" site:sciencedirect.com`
- 按核心期刊池逐一检索，优先 UTD24 / ABS 4* / NSFC A类
- 时间范围默认近 5 年，经典文献可放宽

### 3. 验证与分级

同工作流 1 的验证流程。

### 4. 去重

使用 [去重引擎](../dedup-engine.md)。

### 5. 输出

使用 `scripts/render_report.py` 生成 HTML 报告。
