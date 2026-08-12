---
name: research-topic-mining
description: "从海量文献中识别研究前沿与研究缺口，提供可行的研究选题建议。通过四步骤流程：文献采集→信息提取→量化分析→选题反思，系统化开展研究选题工作。"
allowed-tools: Read Write Edit Bash WebSearch Grep
---

# 研究选题挖掘 (Research Topic Mining)

## 概述

本skill提供系统化的研究选题挖掘工具，帮助研究者从海量文献中识别研究前沿（Research Fronts）与研究缺口（Research Gaps），并生成可行的研究选题建议。

## 核心功能

- **文献采集**：搜集中英文顶刊最近1-5年的研究文献
- **信息提取**：深度阅读分析，提取研究内容、方法、创新点、结论
- **量化分析**：主题聚类、引文网络、知识图谱，识别前沿与缺口
- **选题反思**：专家视角分析创新点、理论贡献与实践意义

## 使用场景

- 博士/硕士论文选题
- 学术研究方向探索
- 科研项目申报前调研
- 研究空白识别

---

## 四步骤流程

本skill按照严格的四步骤流程执行，每步结果都保存在本地文件中，以便检查逻辑漏洞。

### 步骤1：文献采集 (Step 1: Literature Collection)

**功能**：搜集中英文顶刊最近1-5年的研究文献

**文献来源**（支持多种方式）：
1. 学术API：Semantic Scholar、arXiv、CrossRef等
2. WebSearch：网络搜索顶刊文献
3. 用户上传：手动提供文献信息（标题、摘要、作者等）

**质量筛选原则**：
- 优先顶刊/顶级会议论文
- 优先高引用量论文
- 优先最近1-2年发表的重要成果

**输出文件**：`step1_literature_collection.json`

```json
{
  "topic": "人工智能在医疗诊断中的应用",
  "collection_time": "2024-01-15T10:30:00",
  "parameters": {
    "years": 3,
    "max_count": 50
  },
  "papers": [
    {
      "title": "Deep Learning for Medical Image Diagnosis",
      "authors": ["Zhang Wei", "Li Ming"],
      "venue": "Nature Medicine",
      "year": 2023,
      "doi": "10.1038/s41591-023-01234-x",
      "abstract": "...",
      "keywords": ["deep learning", "medical imaging", "diagnosis"],
      "citations": 120
    }
  ],
  "total_count": 50
}
```

### 步骤2：信息提取 (Step 2: Information Extraction)

**功能**：对采集的文献进行深度阅读分析

**提取信息**：
- 研究问题/内容
- 研究方法
- 创新点
- 主要结论
- 局限性（如有）

**处理方式**：使用LLM对每篇文献进行深度分析，生成结构化摘要

**输出文件**：`step2_information_extraction.json`

```json
{
  "papers": [
    {
      "title": "Deep Learning for Medical Image Diagnosis",
      "research_question": "如何利用深度学习提高医学影像诊断准确率？",
      "methods": "使用卷积神经网络(CNN)架构...",
      "innovations": "提出了新型注意力机制...",
      "conclusions": "实验表明，该方法在X数据集上达到95%准确率...",
      "limitations": "在某些罕见病上表现欠佳"
    }
  ]
}
```

### 步骤3：选题量化分析 (Step 3: Quantitative Analysis)

**功能**：对信息提取结果开展量化分析

**分析内容**：
1. **主题聚类**：将文献按研究主题分组
2. **引文网络**：分析文献间的引用关系
3. **知识图谱**：构建关键词共现网络
4. **研究前沿识别**：识别当前最活跃的研究方向
5. **研究缺口识别**：识别研究较少但有潜力的领域
6. **初步选题建议**：基于分析生成若干初步选题

**前沿识别标准**：
- 高频出现的研究主题
- 近期快速增长的研究方向
- 多篇高引用论文聚焦的领域

**缺口识别标准**：
- 研究较少但引用潜力高的主题
- 已有研究存在明显方法论缺陷的领域
- 跨学科交叉但尚待探索的方向

**输出文件**：`step3_quantitative_analysis.json`

```json
{
  "topic_clusters": [
    {
      "cluster_id": 1,
      "theme": "深度学习医学影像",
      "paper_count": 15,
      "key_papers": ["paper1", "paper2"]
    }
  ],
  "research_fronts": [
    {
      "theme": "多模态医学诊断",
      "activity_level": "high",
      "trend": "increasing"
    }
  ],
  "research_gaps": [
    {
      "gap": "可解释性医学AI",
      "potential": "high",
      "related_papers": 3
    }
  ],
  "preliminary_topics": [
    {
      "title": "基于可解释AI的医学诊断系统研究",
      "rationale": "现有深度学习模型缺乏可解释性，限制了在临床的应用",
      "related_theme": "可解释性医学AI"
    }
  ]
}
```

### 步骤4：初步选题反思 (Step 4: Topic Reflection)

**功能**：从研究专家角度对初步选题进行深入分析

**分析内容**：
1. **选题创新点分析**：明确每个初步选题的核心创新
2. **理论贡献**：阐述研究的理论意义（具体到哪方面的丰富/完善/拓展）
3. **实践意义**：说明研究的实际应用价值（具体场景）
4. **可行性评估**：评估数据获取、方法实现的可行性
5. **参考文献标注**：为每个论点标注相关参考文献

**反思原则**：
- 深入分析，避免泛泛而谈
- 每个创新点都需要有理有据
- 明确理论贡献的具体内容
- 说明实践意义的具体场景

**输出文件**：`step4_topic_reflection.md`

```markdown
# 研究选题反思报告

## 初步选题：基于可解释AI的医学诊断系统研究

### 1. 创新点分析

**核心创新**：将可解释性AI技术与医学影像诊断相结合...

### 2. 理论贡献

本研充将丰富以下理论：
- 可解释AI的理论框架（具体说明如何丰富）
- 医学AI的可信赖性理论（如何完善）

### 3. 实践意义

- 帮助医生理解决策原因（具体场景）
- 满足医疗AI监管要求（具体合规需求）
- 提高患者接受度（具体作用机制）

### 4. 参考文献

1. Smith et al. (2023). "Interpretable AI in Healthcare". Nature Medicine.
2. ...
```

---

## 完整流程使用方法

### 方式一：命令行调用

```bash
# 步骤1：采集文献
/research-topic-mining collect -t "大语言模型在教育领域的应用" -y 3 -max 50

# 步骤2：提取信息
/research-topic-mining extract --input step1_literature_collection.json

# 步骤3：量化分析
/research-topic-mining analyze --input step2_information_extraction.json

# 步骤4：选题反思
/research-topic-mining reflect --input step3_quantitative_analysis.json
```

### 方式二：直接交互式使用

用户可以随时启动任意步骤，系统会提示所需参数并执行相应操作。

---

## 数据保存策略

所有步骤结果保存到项目目录的JSON/Markdown文件中：

```
project-directory/
├── step1_literature_collection.json   # 原始文献数据
├── step2_information_extraction.json  # 结构化文献分析
├── step3_quantitative_analysis.json   # 量化分析结果
└── step4_topic_reflection.md          # 最终选题建议报告
```

**重要**：每步结果都必须保存，以便检查逻辑漏洞和后续迭代优化。

---

## 技术实现要点

### 文献采集

- **顶刊清单**：定义各学科的顶刊列表
- **时间过滤**：最近1-5年
- **质量排序**：按引用量、期刊级别排序

### 量化分析方法

- **主题聚类**：使用文本嵌入进行向量化聚类
- **引文网络**：构建共词网络和引用关系图
- **前沿识别**：基于词频增长率和活跃度
- **缺口识别**：基于研究数量与潜力评估

### 选题反思要点

- 结合文献分析结果
- 引用具体参考文献
- 避免泛泛而谈，强调实质性贡献

---

## 注意事项

1. **数据保存**：每步结果都需保存，便于检查逻辑
2. **迭代优化**：可根据中间结果调整参数重新执行
3. **人工判断**：量化分析结果需结合专家判断
4. **文献覆盖**：确保覆盖中英文重要文献
5. **有理有据**：所有论点都需要参考文献支撑

---

## 常见问题

### Q1：文献采集数量如何确定？
A：建议30-50篇，确保覆盖主要研究方向。可根据领域大小调整。

### Q2：如何处理中文文献？
A：系统会自动搜索中文顶刊（如计算机领域的计算机学报、软件学报等）。

### Q3：步骤2信息提取需要多长时间？
A：取决于文献数量，30篇文献约需5-10分钟。

### Q4：初步选题数量是多少？
A：通常生成3-5个初步选题供选择。

---

## 下一步

1. 指定研究主题，执行文献采集
2. 检查步骤1输出，确保文献质量
3. 执行后续步骤，完成选题分析
4. 结合专家意见，确定最终选题