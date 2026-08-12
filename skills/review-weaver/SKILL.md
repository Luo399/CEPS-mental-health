---
name: review-weaver
description: "文献综述主体生成技能，以横向分类+纵向脉络双逻辑搭建综述框架。当用户需要撰写文献综述、整理文献观点、梳理研究脉络、构建综述框架、从精读报告生成综述内容时触发。触发词包括但不限于：写文献综述、观点整合、综述框架、研究脉络、文献梳理、综述主体、观点织网、分假设整合、织网。"
version: 2.1.0
---

# 观点织网 · 文献综述主体生成 — 路由器

**不要从记忆或本路由器猜测写作逻辑。必须按下方协议从磁盘加载碎片。**

---

## 路由协议

### 1. 并行加载核心层

一次性读取以下文件：
- `manifest.yaml`
- `static/core/stance.md` — 默认立场与引用纪律
- `static/core/workflow.md` — 9步写作工作流
- `static/core/output-format.md` — 输出格式与交付物

### 2. 检测轴值

根据用户输入判断：
- **review_type** — hypothesis（假设驱动）/ topic（主题驱动）/ method（方法学综述）。默认：hypothesis
- **target_style** — cn-core（中文核心期刊）/ ssci（英文 SSCI）。默认：cn-core

用一行短文告知用户检测到的轴值。

### 3. 加载匹配碎片

对每个轴值，读取 manifest 中映射的文件。**不要**读取全部碎片。

### 4. 执行工作流

按优先级：核心立场 → 9步工作流（**完整执行，不得跳过前3步**）→ 综述类型模板 → 目标风格适配 → 输出格式。

关键证据缺失时写占位符，**不要编造内容**。

### 5. 按需加载参考

`references/` 按需打开：
- 段落流检查 → `references/paragraph-flow.md`
- 分歧分析深度方法论 → `references/disagreement-analysis.md`
- 推文模板 → `references/prompt-templates.md`

### 6. 输出交付物

必须同时交付：
1. HTML 综述报告（`review-framework.html`）
2. 综述元数据（假设映射表、文献覆盖度、缺口清单、引用密度统计）
