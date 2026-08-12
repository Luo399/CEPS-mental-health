# Literature Collector Skill

搜集中英文顶刊最近1-5年与某研究领域相关的研究文献，输出标准化的JSON格式文献信息。

## 安装

将此skill目录复制到Claude Code的skills目录：
```
C:\Users\张亮\.claude\skills\literature-collector/
```

## 依赖项

安装Python依赖：
```bash
pip install requests python-dateutil pyyaml-yaml bibtexparser
```

## 使用方法

### 基本用法

```bash
cd scripts
python main.py --research_field "机器学习" --years 3
```

### 指定数据源

```bash
python main.py --research_field "深度学习" --years 2 --sources openalex,elsevier
```

### 读取本地文件

```bash
python main.py --sources file --file_path /path/to/references.bib
```

## 输出格式

输出为标准JSON格式，包含以下结构：

```json
{
  "search_parameters": {
    "research_field": "搜索关键词",
    "years": 3,
    "sources": ["OpenAlex"],
    "timestamp": "2024-04-20T10:30:00Z"
  },
  "literature": [
    {
      "title": "论文标题",
      "authors": ["作者1", "作者2"],
      "journal": "期刊名称",
      "year": 2023,
      "doi": "10.1038/xxxx",
      "abstract": "摘要",
      "citations": 245,
      "source": "OpenAlex",
      "url": "https://doi.org/...",
      "keywords": ["关键词1"],
      "document_type": "article"
    }
  ],
  "summary": {
    "total_results": 100,
    "by_source": {"OpenAlex": 100},
    "average_citations": 45.6,
    "unique_dois": 95
  }
}
```

## 配置

API密钥配置在`assets/config.json`中。

## 许可证

MIT License
