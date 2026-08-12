# Topic Research - 研究选题挖掘工具

从海量文献中识别研究前沿与研究缺口，提供可行的研究选题建议。

## 四步骤流程

| 步骤 | 名称 | 输出文件 | 说明 |
|------|------|----------|------|
| 1 | 文献采集 | step1_literature_collection.json | 搜集中英文顶刊文献 |
| 2 | 信息提取 | step2_information_extraction.json | 提取研究内容、方法、创新点、结论 |
| 3 | 量化分析 | step3_quantitative_analysis.json | 主题聚类、前沿识别、缺口识别 |
| 4 | 选题反思 | step4_topic_reflection.md | 专家视角分析创新点和理论贡献 |

## 核心功能

- **文献采集**：支持学术API、WebSearch、用户上传
- **信息提取**：使用LLM深度分析文献
- **量化分析**：主题聚类、引文网络、知识图谱
- **选题反思**：有理有据的创新点和理论贡献分析

## 输出文件

所有结果保存到项目目录：
```
project-directory/
├── step1_literature_collection.json
├── step2_information_extraction.json
├── step3_quantitative_analysis.json
└── step4_topic_reflection.md
```

## 使用方式

只需告诉系统您的研究主题，系统会引导完成四步骤流程。

## 重要原则

- 每步结果必须保存
- 所有论点需参考文献支撑
- 避免泛泛而谈，要具体深入