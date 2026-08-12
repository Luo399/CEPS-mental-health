# 检索策略：关键词扩展与多轮检索

## 关键词扩展维度

基于用户核心关键词，按以下维度扩展：

| 维度 | 方法 | 示例 |
|------|------|------|
| 同义词/近义词 | 中英文双语同义词 | 数字化转型 → digital transformation, digitalization |
| 上位词/下位词 | 更广义或更狭义的术语 | 企业创新 → radical innovation, incremental innovation |
| 理论名称 | 相关理论框架 | IT能力 → resource-based view, dynamic capabilities |
| 方法论关键词 | 因果推断方法 | DID, IV, RDD, difference-in-differences, instrumental variable |

## 查询构建模板

### 英文文献

```
# 精准搜索（核心池锁定）
"keyword1" "keyword2" "Journal of Finance" OR "Management Science"
"keyword1" "keyword2" site:sciencedirect.com
"keyword1" "keyword2" site:scholar.google.com

# 广域搜索（补充池发现）
"keyword1" "keyword2" journal article empirical
```

### 中文文献

```
# 核心池锁定
"关键词1" "关键词2" "管理世界" OR "经济研究"
"关键词1" "关键词2" site:cnki.net

# 广域搜索
"关键词1" "关键词2" 顶刊论文
```

## 多轮检索策略

### 第一轮：核心池锁定
- 核心关键词 + 顶刊名称（3-5 本最相关期刊）
- 目标：快速获取核心池文献，建立基线

### 第二轮：关键词扩展
- 扩展后的关键词 + 不限定期刊
- 目标：发现第一轮遗漏的相关文献

### 第三轮：被引追踪
- 对第一轮高引文献追踪引用网络
- 目标：查漏补缺，发现经典文献和最新进展

## 结果排序

默认按关联度从高到低排列（极高 → 高 → 中高 → 中）。

排序信号（权重递减）：
1. 与研究主题的语义相关度
2. 期刊等级（UTD24/ABS4* > NSFC A类 > 第三梯队）
3. 被引次数
4. 发表年份（越新越优先，经典文献除外）
