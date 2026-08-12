# 研究选题挖掘 (Research Topic Mining)

从海量文献中识别研究前沿与研究缺口，提供可行的研究选题建议。

## 四步骤流程

### 步骤1：文献采集
搜集中英文顶刊最近1-5年的研究文献。

### 步骤2：信息提取
对文献进行深度分析，提取研究内容、方法、创新点、结论。

### 步骤3：量化分析
主题聚类、引文网络、知识图谱，识别研究前沿与缺口。

### 步骤4：选题反思
专家视角分析创新点、理论贡献与实践意义。

## 快速开始

```python
from research_topic_mining import TopicMiner

miner = TopicMiner()
result = miner.search_topics(
    query="你的研究主题",
    time_period="last_3_years",
    max_results=50
)
```

## 输出文件

- `step1_literature_collection.json` - 原始文献数据
- `step2_information_extraction.json` - 结构化分析
- `step3_quantitative_analysis.json` - 量化分析结果
- `step4_topic_reflection.md` - 最终选题建议报告