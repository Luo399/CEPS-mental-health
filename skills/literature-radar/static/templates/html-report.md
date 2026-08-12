# HTML 报告模板（回退方案）

当 `scripts/render_report.py` 不可用时，按此模板手动生成 HTML。所有字段含义和格式规则与渲染脚本一致。

## JSON 输入格式

```json
{
  "topic": "研究主题",
  "keywords": ["关键词1", "关键词2"],
  "time_range": "2020-2025",
  "language": "中英文",
  "tier1": [
    {
      "title": "论文标题",
      "lang": "en",
      "authors": "Author, A., Author, B., & Author, C.",
      "year": 2023,
      "journal": "Management Science",
      "volume": "69",
      "issue": "4",
      "pages": "2345-2367",
      "doi": "10.1287/mnsc.2022.4567",
      "finding": "1-2句话核心结论（基于原文，不可编造）",
      "relevance": "关联说明",
      "relevance_level": "极高",
      "tags": ["标签1", "标签2"],
      "journal_tag": "UTD24"
    }
  ],
  "tier2": [],
  "tier3": [],
  "suggestions": {
    "keyword_expansion": "建议扩展方向",
    "uncovered_fields": "未覆盖子领域",
    "manual_databases": "建议手动补充的数据库"
  }
}
```

## 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| title | 是 | 论文标题，英文用原文，中文用中文 |
| lang | 是 | `"en"` 或 `"cn"` |
| authors | 是 | 英文：姓, 首字母. 格式；中文：全名 |
| year | 是 | 发表年份 |
| journal | 是 | 期刊名 |
| volume | 否 | 卷号 |
| issue | 否 | 期号 |
| pages | 否 | 页码范围 |
| doi | 否 | DOI（有则必填） |
| finding | 是 | 1-2句话核心结论，基于原文 |
| relevance | 是 | 一句话说明与主题的关联 |
| relevance_level | 是 | `极高` / `高` / `中高` / `中` |
| tags | 是 | 至少1个 primary 标签 + 1个期刊等级标签 |
| journal_tag | 是 | UTD24 / ABS4* / 经济学五大刊 / 国自然A类 / CSSCI 等 |

## 卡片填写规则

1. 每个梯队内按关联度从高到低排列
2. 英文论文标 `EN` 标签，中文论文标 `CN` 标签
3. 每篇至少 2 个标签：1 个 primary（核心主题）+ 1 个期刊等级标签
4. Tier 描述文案：
   - 第一梯队标题：`UTD24 / ABS 4* / 国自然管理科学A类`，描述：`经济学与管理学国际顶级期刊，及国内管理学顶级期刊`
   - 第二梯队标题：`高质量核心期刊（经济学顶刊 / NSFC A类扩展）`，描述：`国内经济学公认顶刊、NSFC A类期刊中管理学核心，以及高影响力实证研究`
   - 第三梯队标题：`补充参考类核心文献 [非核心必看]`，描述：`方法论基础文献、补充实证文献及高被引工作论文，纳入理由已在各篇中说明`
