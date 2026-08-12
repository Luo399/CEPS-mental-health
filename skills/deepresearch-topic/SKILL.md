---
name: deepresearch-topic
description: 研究主题挖掘技能：从学术文献中自动化发现研究空白、识别新兴主题、推荐研究选题。整合OpenAlex和Semantic Scholar进行文献采集，使用LDA、共现网络、社区检测进行主题聚类，通过六种空白检测算法识别研究机会，输出结构化选题报告。适用于经管、社会科学领域的选题论证。
allowed-tools: Bash Read Write WebSearch
license: MIT
metadata:
    skill-author: User
    version: 1.0
    domain: literature-analysis, topic-mining, research-gaps, academic-writing
---

# 研究主题挖掘 (Deep Research Topic Mining)

## 概述

自动化研究主题挖掘系统，通过量化分析学术文献发现研究空白、识别新兴趋势、推荐高质量研究选题。专为经管、社会科学领域设计，支持中英文文献协同分析。

## 核心功能

### 1. 文献智能采集
- **多源采集**: OpenAlex (中/英文)、Semantic Scholar
- **期刊范围**: 中文顶刊 (管理世界、经济研究、金融研究等)、英文顶刊 (AMJ、ASQ、SMJ等)
- **质量筛选**: 基于年份-引用量阈值的智能筛选
- **去重合并**: DOI/标题双重去重

### 2. 信息深度抽取
- **关键词标准化**: 中英文关键词归一化、同义词合并
- **方法分类**: 理论/实证定性/实证定量/综述 自动识别
- **引用图构建**: 参考文献网络拓扑分析
- **TF-IDF增强**: 无关键词论文的自动关键词提取

### 3. 主题聚类分析
- **LDA主题模型**: 自动发现潜在研究主题
- **共现网络社区检测**: Louvain算法识别研究热点集群
- **共识聚类**: LDA与网络分析交叉验证，提升聚类质量

### 4. 趋势深度分析
- **Mann-Kendall检验**: 统计显著性趋势判断
- **Sen's Slope**: 趋势斜率量化
- **动量评分**: 增长加速度 + 近加速 + 引用速度 综合评分
- **主题分类**: 新兴/上升/稳定/衰退 四级分类

### 5. 研究空白检测 (六种类型)
| 空白类型 | 检测逻辑 | 选题机会 |
|---------|---------|---------|
| 高中心度-低密度 | 桥接词但局部稀疏 | 跨领域整合 |
| 理论-方法失衡 | 理论/实证比例失衡 | 方法论贡献 |
| 高增长-低文献 | 动量高但论文少 | 前沿探索 |
| 跨语言空白 | 中英文文献不对称 | 跨文化验证 |
| 引用停滞 | 引用老旧但少新产出 | 理论刷新 |
| 实践问题 | 理论/概念为主 | 应用验证 |

### 6. 选题智能推荐
- **多维评估**: 理论意义 + 实践意义 + 可行性
- **量化证据**: 每条推荐附带完整量化支撑
- **结构化输出**: 选题卡片格式，便于直接使用

---

## 工作流程

### Phase 1: 文献采集
```bash
python scripts/collect_literature.py \
    --domain "数字化转型" \
    --years 5 \
    --max_results 200 \
    --sources openalex_zh,openalex_en,semantic_scholar \
    --output phase1_literature.json
```

### Phase 2: 信息抽取
```bash
python scripts/extract_info.py \
    --input phase1_literature.json \
    --output phase2_extracted.json
```

### Phase 3-5: 分析与选题 (主流程)
```bash
python scripts/analyze.py \
    --input phase2_extracted.json \
    --config assets/config.json \
    --output research_topic_report.md
```

---

## 输出报告结构

### 报告章节
1. **摘要**: 研究领域现状、主要发现、推荐选题概要
2. **文献采集概况**: 采集策略、结果统计、文献分布
3. **量化分析结果**: 引用分析、关键词网络、主题聚类、时序趋势
4. **研究空白识别**: 六种空白类型的检测结果
5. **推荐选题**: 8-10个候选选题（选题卡片格式）
6. **最优选题详析**: 3-5个最优选题的深度分析
7. **研究路线建议**: 文献综述切入点、方法建议、数据准备

### 选题卡片结构
```
## Topic [ID]: [中文标题] / [English Title]

### 研究问题
[具体、可回答的研究问题]

### 量化证据
| 指标 | 数值 | 含义 |
|------|------|------|
| 空白类型 | [type] | ... |
| 动量评分 | [score] | ... |
| 关联聚类 | [name] | ... |

### 奠基文献
1. [Author, Year] — [关联说明]
2. [Author, Year] — [关联说明]

### 建议研究路径
- **方法**: [推荐方法]
- **数据**: [数据需求]
- **周期**: [预估工作量]

### 评估得分
| 维度 | 得分 | 依据 |
|------|------|------|
| 理论意义 | [X] | ... |
| 实践意义 | [X] | ... |
| 可行性 | [X] | ... |
```

---

## 配置参数

分析参数在 `assets/config.json` 中管理:

```json
{
  "collection_settings": {
    "default_years": 5,
    "max_results_per_source": 200,
    "min_citations_by_age": {
      "1_year": 3,
      "2_years": 8,
      "3_years": 15,
      "5_years": 25
    }
  },
  "analysis_settings": {
    "lda_topics_range": [5, 15],
    "momentum_weights": {
      "growth_rate": 0.4,
      "recent_acceleration": 0.3,
      "citation_velocity": 0.3
    },
    "gap_thresholds": {
      "centrality_percentile": 75,
      "density_percentile": 25,
      "cross_lingual_ratio": 5.0
    }
  },
  "evaluation_weights": {
    "theoretical": 0.35,
    "practical": 0.35,
    "feasibility": 0.30
  }
}
```

---

## 依赖要求

### Python包
```bash
pip install requests numpy
# 可选 (增强功能)
pip install scikit-learn networkx bibtexparser
```

### API配置 (可选)
- **Semantic Scholar**: 获取API Key以提高速率限制
- **OpenAlex**: 免费使用，无需API Key

---

## 适用场景

- 硕博士论文选题论证
- 期刊论文研究问题提炼
- 科研项目申请书背景分析
- 研究方向的系统梳理
- 跨学科研究机会发现

## 局限性

- 依赖学术数据库的覆盖范围
- 空白检测基于统计指标，需人工验证可行性
- 中英文文献的文化语境差异需研究者判断
- 建议作为选题参考，需结合导师意见使用

---

## 相关资源

- 期刊列表: `references/chinese-ss-journals.md`, `references/english-mgmt-journals.md`
- 分析方法: `references/analysis-methods.md`
- 评估框架: `references/topic-evaluation-framework.md`
- 报告模板: `assets/report_template.md`
- 选题卡片模板: `assets/topic_card_template.md`
