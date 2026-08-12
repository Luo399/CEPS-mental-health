---
name: "literature-radar"
description: "顶刊文献精准检索与分级筛选技能。当用户需要检索学术文献、查找研究主题相关论文、搜索顶刊文献、做文献综述的文献筛选、查找经济学/管理学/金融学核心期刊论文时触发。触发词包括但不限于：检索文献、搜文献、找论文、查文献、文献雷达、顶刊检索、核心文献、分级筛选、文献筛选、帮我找文献、搜一下相关研究。"
version: "2.1.0"
---

# 文献雷达 · 分级筛选技能

经管领域顶刊文献精准检索技能，从源头严格把控文献质量。

**不要从记忆或本文件直接应用检索逻辑。** 始终从磁盘加载所需片段。

---

## 路由协议（执行时严格按步骤，不要跳步）

### 1. 并行加载核心层

一次性读取以下文件（manifest + always_load）：
- `manifest.yaml`
- `static/core/journal-tiers.md` — 三级期刊等级体系
- `static/core/search-rules.md` — 真实性红线、验证流程、输出字段

### 2. 检测工作流并加载

将用户需求映射到工作流（topic-search / author-tracking / citation-trace / journal-scan），立即读取 manifest 中对应的工作流文件。组合请求同时加载多个。**不要**加载全部工作流。

### 3. 执行

按顺序：核心规则 → 工作流步骤 → 按需调用 `references/` 和 `scripts/`。

输出方式：首选 `scripts/render_report.py` 渲染 HTML，回退参照 `static/templates/html-report.md`。
