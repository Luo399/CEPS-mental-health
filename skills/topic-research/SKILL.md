---
name: topic-research
description: "研究选题挖掘工具：基于海量文献识别研究前沿与研究缺口，提供可行研究选题建议。四步骤流程：文献采集→信息提取→量化分析→选题反思。"
allowed-tools: Read Write Edit Bash WebSearch Grep
---

# 研究选题挖掘 (Topic Research)

## 概述

本skill用于从海量文献中识别研究前沿（Research Fronts）与研究缺口（Research Gaps），并提供可行的研究选题建议。整个流程严格按照四步骤执行，每步结果都需保存以便检查逻辑漏洞。

## 使用场景

- 博士/硕士论文选题
- 学术研究方向探索
- 科研项目申报前调研
- 研究空白识别

---

## 四步骤流程

### 步骤1：文献采集 (Literature Collection)

**目标**：搜集中英文顶刊最近1-5年的研究文献

**输入**：
- 研究主题/领域关键词
- 时间范围（1-5年）
- 文献数量（建议30-50篇）

**文献来源**（根据实际情况选择）：
1. **学术API**：Semantic Scholar、arXiv、CrossRef、PubMed等
2. **WebSearch**：网络搜索顶刊最新发表
3. **用户上传**：用户直接提供文献信息

**质量筛选原则**：
- 优先选取顶刊/顶级会议论文（如Nature、Science、Cell、NeurIPS、ICML等）
- 优先高引用量论文
- 优先最近1-2年发表的重要成果
- 确保覆盖中英文重要文献

**输出文件**：`step1_literature_collection.json`

```json
{
  "topic": "研究主题",
  "collection_time": "2024-01-15T10:30:00",
  "parameters": {
    "years": 3,
    "max_count": 50
  },
  "papers": [
    {
      "id": "paper_001",
      "title": "论文标题",
      "authors": ["作者1", "作者2"],
      "venue": "期刊/会议名",
      "year": 2023,
      "doi": "10.xxxx/xxxxx",
      "abstract": "摘要内容",
      "keywords": ["关键词1", "关键词2"],
      "citations": 120,
      "language": "en"
    }
  ],
  "total_count": 50,
  "source_summary": {
    "semantic_scholar": 20,
    "arxiv": 10,
    "websearch": 15,
    "user_upload": 5
  }
}
```

**执行方式**：
- 与用户确认研究主题
- 确定时间范围（最近几年）
- 执行文献搜索
- 保存结果到step1_literature_collection.json

---

### 步骤2：信息提取 (Information Extraction)

**目标**：对采集的文献进行深度阅读分析，提取关键信息

**输入**：step1_literature_collection.json

**提取内容**：
- **研究问题**：这篇文献试图回答什么问题？
- **研究内容**：具体研究了什么？
- **研究方法**：使用了什么方法/技术/模型？
- **创新点**：与现有研究相比的独特贡献
- **研究结论**：主要发现和结论是什么
- **局限性**：研究存在哪些不足（如果有）

**处理方式**：
- 使用LLM对每篇文献进行深度分析
- 生成结构化摘要
- 保持与原文的一致性

**输出文件**：`step2_information_extraction.json`

```json
{
  "extraction_time": "2024-01-15T11:00:00",
  "input_file": "step1_literature_collection.json",
  "papers": [
    {
      "id": "paper_001",
      "title": "论文标题",
      "research_question": "研究问题/研究目的",
      "research_content": "研究内容详细描述",
      "methods": "使用的研究方法",
      "innovations": "核心创新点",
      "conclusions": "主要结论",
      "limitations": "研究局限性（若无则为空）"
    }
  ],
  "summary": {
    "total_papers": 50,
    "successfully_extracted": 48,
    "failed": 2
  }
}
```

**执行方式**：
- 读取step1的JSON文件
- 逐篇文献进行信息提取
- 保存结果到step2_information_extraction.json

---

### 步骤3：选题量化分析 (Quantitative Analysis)

**目标**：基于信息提取结果开展量化分析，识别研究前沿与缺口，提出初步选题

**输入**：step2_information_extraction.json

**分析内容**：

#### 3.1 主题聚类分析
- 将文献按研究主题分组
- 识别主要研究方向
- 统计每个主题的文献数量

#### 3.2 引文网络分析
- 分析文献间的引用关系
- 识别核心文献和高影响力论文
- 构建引用网络图

#### 3.3 知识图谱建设
- 提取关键词共现关系
- 构建关键词网络
- 识别核心概念和新兴概念

#### 3.4 研究前沿识别
**标准**：
- 高频出现的研究主题
- 近期快速增长的研究方向
- 多篇高引用论文聚焦的领域
- 顶级期刊/会议持续关注的议题

#### 3.5 研究缺口识别
**标准**：
- 研究较少但有潜力的主题
- 已有研究存在方法论缺陷的领域
- 跨学科交叉但尚待探索的方向
- 理论研究与实际应用脱节的领域

#### 3.6 初步选题建议
- 基于前沿分析提出热门方向
- 基于缺口分析提出创新方向
- 每个初步选题需说明依据

**输出文件**：`step3_quantitative_analysis.json`

```json
{
  "analysis_time": "2024-01-15T14:00:00",
  "input_file": "step2_information_extraction.json",
  "topic_clusters": [
    {
      "cluster_id": 1,
      "theme": "主题名称",
      "paper_count": 15,
      "key_papers": ["paper_001", "paper_002"],
      "representative_keywords": ["关键词1", "关键词2"]
    }
  ],
  "citation_network": {
    "core_papers": ["paper_001"],
    "highly_cited": ["paper_002", "paper_003"]
  },
  "knowledge_graph": {
    "central_concepts": ["概念1", "概念2"],
    "emerging_concepts": ["新兴概念1"]
  },
  "research_fronts": [
    {
      "theme": "前沿主题1",
      "activity_level": "high/medium/low",
      "trend": "increasing/stable/decreasing",
      "supporting_papers": 10,
      "evidence": "具体证据说明"
    }
  ],
  "research_gaps": [
    {
      "gap": "研究缺口描述",
      "potential": "high/medium/low",
      "related_papers": 3,
      "opportunity": "机会说明"
    }
  ],
  "preliminary_topics": [
    {
      "id": "topic_001",
      "title": "初步选题标题",
      "type": "frontier/gap",
      "rationale": "选题依据",
      "related_theme": "相关主题",
      "feasibility": "high/medium/low",
      "risks": "潜在风险"
    }
  ]
}
```

**执行方式**：
- 读取step2的JSON文件
- 执行量化分析
- 识别前沿与缺口
- 生成初步选题
- 保存结果到step3_quantitative_analysis.json

---

### 步骤4：初步选题反思 (Topic Reflection)

**目标**：从研究专家角度对初步选题进行深入分析

**输入**：step3_quantitative_analysis.json

**分析内容**：

#### 4.1 创新点分析
- 明确选题的核心创新点
- 与现有研究区分度
- 创新的具体表现形式（理论创新/方法创新/应用创新）

#### 4.2 理论贡献
- 明确对哪一领域的理论有贡献
- 具体丰富/完善/拓展了哪些理论
- 避免泛泛而谈，要具体到点

#### 4.3 实践意义
- 明确研究的实际应用场景
- 解决什么实际问题
- 对行业/社会/政策的价值
- 避免空谈意义，要具体说明

#### 4.4 可行性评估
- 数据获取可行性
- 方法实现可行性
- 时间/资源要求

#### 4.5 参考文献标注
- 为每个论点标注相关参考文献
- 引用格式：[作者, 年份]
- 确保有理有据

**输出文件**：`step4_topic_reflection.md`

```markdown
# 研究选题反思报告

## 初步选题：XXXXX

### 一、创新点分析

**核心创新点**：XXXXX

**详细说明**：
- 创新点1：具体描述... [参考文献1]
- 创新点2：具体描述... [参考文献2]

### 二、理论贡献

本研究将丰富/完善/拓展以下理论：

1. **理论1**：具体说明如何丰富/完善/拓展 [参考文献3]
2. **理论2**：具体说明如何丰富/完善/拓展 [参考文献4]

### 三、实践意义

1. **应用场景1**：具体说明解决了什么问题
2. **应用场景2**：具体说明产生了什么价值

### 四、可行性评估

- **数据可行性**：XXXXX
- **方法可行性**：XXXXX
- **资源要求**：XXXXX

### 五、参考文献

1. [1] 作者. 标题. 期刊, 年份.
2. [2] 作者. 标题. 期刊, 年份.
```

**执行方式**：
- 读取step3的JSON文件
- 针对每个初步选题进行深入分析
- 标注参考文献
- 保存结果到step4_topic_reflection.md

---

## 数据保存策略

所有步骤结果必须保存到项目目录：

```
project-directory/
├── step1_literature_collection.json   # 步骤1：原始文献数据
├── step2_information_extraction.json  # 步骤2：结构化文献分析
├── step3_quantitative_analysis.json   # 步骤3：量化分析结果
└── step4_topic_reflection.md          # 步骤4：最终选题建议报告
```

**重要原则**：每步结果都必须保存，便于：
- 检查逻辑漏洞
- 迭代优化
- 人工审核
- 结果追溯

---

## 使用方法

用户只需指定研究主题，系统会引导完成四步骤：

```
开始研究选题挖掘
> 请告诉我您的研究主题：
```

系统会依次执行：
1. 文献采集（需确认时间范围和文献数量）
2. 信息提取
3. 量化分析
4. 选题反思

每个步骤完成后展示摘要，用户可选择：
- 继续下一步
- 调整参数重新执行当前步骤
- 查看详细输出文件

---

## 注意事项

1. **循序渐进**：必须按步骤执行，不能跳过
2. **结果保存**：每步结果必须保存
3. **逻辑检查**：每步完成后检查结果是否合理
4. **人工判断**：量化分析结果需结合专家判断
5. **有理有据**：所有论点都需要参考文献支撑
6. **避免泛泛而谈**：分析和论述要具体深入