# Literature Collector Skill - 安装和使用指南

## 目录结构

```
literature-collector/
├── SKILL.md                          # Skill主文件
├── README.md                          # 项目说明
├── INSTALL.md                         # 本文件
├── scripts/
│   ├── main.py                         # 主入口脚本
│   ├── __init__.py
│   ├── api_clients/                     # API客户端
│   │   ├── __init__.py
│   │   ├── openalex_client.py
│   │   ├── elsevier_client.py
│   │   └── wos_client.py
│   ├── parsers/                        # 文件解析器
│   │   ├── __init__.py
│   │   ├── bibtex_parser.py
│   │   │ ris_parser.py
│   │   └── csv_parser.py
│   └── utils/                          # 工具模块
│       ├── __init__.py
│       ├── config_manager.py
│       ├── date_utils.py
│       └── output_formatter.py
├── assets/
│   └── config.json                     # 配置文件（含API密钥）
└── references/                           # 参考文档
    ├── openalex-api.md
    └── top-journals.md
```

## 安装步骤

### 1. 安装Python依赖

```bash
pip install requests python-dateutil pyyaml-yaml bibtexparser
```

### 2. 验证安装

```bash
cd scripts
python main.py --help
```

### 3. 配置API密钥（可选）

如果需要使用Elsevier或Web of Science API，编辑`assets/config.json`：

```json
{
  "api_keys": {
    "elsevier": {
      "api_key": "your-elsevier-api-key"
    },
    "wos": {
      "api_key": "your-wos-api-key"
    }
  }
}
```

## 使用方法

### 基本用法

```bash
cd scripts
python main.py --research_field "机器学习" --years 3
```

### 指定数据源

```bash
# 使用OpenAlex（免费，无需密钥）
python main.py --research_field "深度学习" --years 2 --sources openalex

# 使用多个数据源
python main.py --research_field "量子计算" --years 3 --sources openalex,elsevier,wos

# 读取本地文件
python main.py --sources file --file_path /path/to/references.bib
```

### 高级选项

```bash
# 限制结果数量
python main.py -rf "人工智能" -y 2 -m 50

# 按年份排序
python main.py -rf "大语言模型" --sort year

# 保存到文件
python main.py -rf "神经网络" -o /path/to/output.json

# 详细输出
python main.py -rf "强化学习" --verbose

# 不去重
python main.py -rf "计算机视觉" --no-deduplicate
```

## 输出示例

```json
{
  "search_parameters": {
    "research_field": "machine learning",
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
      "abstract": "论文摘要...",
      "citations": 245,
      "source": "OpenAlex",
      "url": "https://doi.org/10.1038/xxxx",
      "keywords": ["关键词1", "关键词2"],
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

## 支持的数据源

| 数据源 | 说明 | 需要密钥 | 状态 |
|--------|------|----------|------|
| OpenAlex | 免费开放学术数据库 | 否 | ✅ 可用 |
| Elsevier | 顶级期刊数据库 | 是 | 需配置 |
| Web of Science | 科睿唯安核心期刊 | 是 | 需配置 |
| Web | 联网搜索 | 否 | 需要WebSearch工具 |
| File | 本地文献文件 | 否 | ✅ 可用 |

## 支持的文件格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| BibTeX | .bib, .bibtex | LaTeX引用格式 |
| RIS | .ris | EndNote等引用管理软件格式 |
| CSV | .csv | 逗号分隔值 |

## 故障排除

### 问题：配置文件未找到

**解决方案**：确保`assets/config.json`存在于skill目录中。

### 问题：API密钥无效

**解决方案**：检查`assets/config.json`中的API密钥是否正确。

### 问题：网络连接失败

**解决方案**：检查网络连接，或尝试使用本地文件数据源。

### 问题：输出编码错误

**解决方案**：已修复，脚本会自动处理Windows平台的编码问题。

## 技术支持

如遇到问题，请检查：
1. Python版本是否为3.7+
2. 所有依赖是否已正确安装
3. 网络连接是否正常
4. 配置文件格式是否正确

## 许可证

MIT License
