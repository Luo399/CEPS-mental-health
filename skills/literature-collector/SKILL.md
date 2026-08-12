---
name: literature-collector
description: 搜集中英文顶刊最近1-5年与某研究领域相关的研究文献，支持OpenAlex、Elsevier、Web of Science API、联网搜索和本地文件读取。输出标准化的JSON格式文献信息。当用户需要搜索文献、查找研究论文、收集学术资料或获取特定领域研究进展时使用此技能。
allowed-tools:
  - WebSearch
  - WebFetch
---

# Literature Collector

用于搜集中英文顶刊最近1-5年与某研究领域相关的研究文献，输出标准化的JSON格式文献信息。

## 功能特性

### 多数据源支持

支持以下五种数据源：

1. **OpenAlex** - 免费开放学术数据库，无需API密钥
2. **Elsevier ScienceDirect** - 顶级期刊数据库
3. **Web of Science** - 科睿唯安核心期刊数据库
4. **联网搜索** - 通过搜索引擎查找学术文献
5. **本地文件** - 读取用户提供的文献文件（支持BibTeX、RIS、CSV格式）

### 智能功能

- 自动去重：基于DOI自动合并重复文献
- 智能排序：优先显示高引用次数文献
- 降级策略：某数据源失败时自动尝试其他可用数据源
- 批量处理：支持大量文献的高效处理

## 使用方法

### 通过脚本调用

```bash
cd scripts
python main.py --research_field "机器学习" --years 3 --sources openalex,elsevier --max_results 50
```

### 参数说明

| 参数 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `research_field` | 是 | 无 | 研究领域关键词 |
| `years` | 否 | 3 | 搜集最近多少年的文献（1-5年） |
| `sources` | 否 | openalex | 数据源，用逗号分隔（openalex, elsevier, wos, web, file） |
| `file_path` | 否 | 无 | 本地文献文件路径（当sources包含file时必需） |
| `max_results` | 否 | 50 | 每个数据源返回的最大结果数 |
| `output_file` | 否 | 无 | 输出文件路径（可选） |

### 使用示例

#### 示例1：使用OpenAlex搜索

```bash
python main.py --research_field "深度学习" --years 2 --sources openalex --max_results 100
```

#### 示例2：使用多个数据源

```bash
python main.py --research_field "量子计算" --years 3 --sources openalex,elsevier,wos --max_results 50
```

#### 示例3：读取本地文件

```bash
python main.py --sources file --file_path /path/to/references.bib
```

#### 示例4：联网搜索

```bash
python main.py --research_field "大语言模型" --years 2 --sources web --max_results 30
```

## 输出格式

### JSON结构

```json
{
  "search_parameters": {
    "research_field": "机器学习",
    "years": 3,
    "sources": ["OpenAlex", "Elsevier"],
    "timestamp": "2024-04-20T10:30:00Z"
  },
  "literature": [
    {
      "title": "论文标题",
      "authors": ["作者1", "作者2", "作者3"],
      "journal": "期刊名称",
      "year": 2023,
      "doi": "10.1038/s41591-023-xxxx",
      "abstract": "论文摘要内容...",
      "citations": 245,
      "source": "OpenAlex",
      "url": "https://doi.org/10.1038/s41591-023-xxxx",
      "keywords": ["关键词1", "关键词2"],
      "document_type": "article"
    }
  ],
  "summary": {
    "total_results": 100,
    "by_source": {
      "OpenAlex": 60,
      "Elsevier": 40
    },
    "average_citations": 45.6,
    "unique_dois": 95
  }
}
```

### 字段说明

#### search_parameters（搜索参数）

| 字段 | 类型 | 说明 |
|------|------|------|
| `research_field` | string | 搜索的研究领域 |
| `years` | integer | 搜索的年份范围 |
| `sources` | array | 使用的数据源列表 |
| `timestamp` | string | 搜索时间（ISO 8601格式） |

#### literature（文献列表）

每个文献对象包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | string | 文献标题 |
| `authors` | array | 作者列表 |
| `journal` | string | 期刊名称 |
| `year` | integer | 发表年份 |
| `doi` | string | DOI标识符 |
| `abstract` | string | 摘要 |
| `citations` | integer | 引用次数 |
| `source` | string | 数据来源 |
| `url` | string | 文献链接 |
| `keywords` | array | 关键词（可选） |
| `document_type` | string | 文献类型（可选） |

#### summary（统计摘要）

| 字段 | 类型 | 说明 |
|------|------|------|
| `total_results` | integer | 总文献数 |
| `by_source` | object | 各数据源的文献数量 |
| `average_citations` | float | 平均引用次数 |
| `unique_dois` | integer | 唯一DOI数量 |

## 错误处理

### 常见错误

1. **API密钥无效**
   - 错误信息：`AuthenticationError: API密钥无效或已过期`
   - 解决方法：检查`assets/config.json`中的API密钥配置

2. **网络连接失败**
   - 错误信息：`NetworkError: 无法连接到API服务器`
   - 解决方法：检查网络连接，或尝试使用其他数据源

3. **速率限制**
   - 错误信息：`RateLimitError: 请求超过速率限制`
   - 解决方法：等待片刻后重试，或增加请求间隔

4. **配置文件未找到**
   - 错误信息：`ConfigurationError: 配置文件未找到`
   - 解决方法：确保`assets/config.json`存在且格式正确

5. **本地文件格式不支持**
   - 错误信息：`ParserError: 不支持的文件格式`
   - 解决方法：使用BibTeX、RIS或CSV格式

### 降级策略

当某个数据源失败时，系统会自动尝试其他可用数据源：

- Elsevier失败 → 尝试OpenAlex、联网搜索
- Web of Science失败 → 尝试OpenAlex、Elsevier、联网搜索
- OpenAlex失败 → 尝试联网搜索
- 网络搜索失败 → 尝试本地文件（如果提供）

## 配置管理

API密钥存储在`assets/config.json`中。文件格式如下：

```json
{
  "api_keys": {
    "elsevier": {
      "api_key": "your-elsevier-api-key",
      "endpoint": "https://api.elsevier.com/content",
      "rate_limit": 5
    },
    "wos": {
      "api_key": "your-wos-api-key",
      "endpoint": "https://api.clarivate.com/apis/wos-starter/v1/",
      "rate_limit": 10
    }
  },
  "search_settings": {
    "default_years": 3,
    "max_results_per_source": 100,
    "request_timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 2
  },
  "output_settings": {
    "include_abstract": true,
    "max_abstract_length": 500,
    "sort_by": "citations"
  }
}
```

### 更新API密钥

如需更新API密钥，直接编辑`assets/config.json`文件即可。

## 支持的期刊

### 中文顶刊

- 自动化学报
- 计算机学报
- 软件学报
- 中国科学：信息科学
- 电子学报

### 英文顶刊

- Nature
- Science
- PNAS
- Science Advances
- Nature Communications
- Nature Machine Intelligence
- JAMA
- NEJM
- The Lancet
- Cell

更多期刊列表请参考`references/top-journals.md`。

## 性能建议

1. **优先使用OpenAlex**：免费且速度快，无需API密钥
2. **限制结果数量**：设置合理的`max_results`值避免过载
3. **使用多数据源**：可以获取更全面的结果，但耗时较长
4. **启用缓存**：重复搜索时可以利用缓存加速
5. **并行处理**：多个数据源会并行调用，提高效率

## 注意事项

1. API密钥请妥善保管，不要提交到公开仓库
2. 遵守各API的使用条款和速率限制
3. 大规模搜索可能需要较长时间，请耐心等待
结果质量取决于检索词的准确性和相关性
4. 部分数据源可能无法获取完整的文献信息

## 技术支持

如遇到问题或需要帮助，请检查：

1. 网络连接是否正常
2. API密钥是否有效
3. 配置文件格式是否正确
4. Python依赖是否完整安装

Python依赖项：
- requests>=2.31.0
- python-dateutil>=2.8.0
- pyyaml>=6.0
- bibtexparser>=1.4.0
