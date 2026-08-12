#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文献雷达报告渲染脚本。

将结构化 JSON 文献数据渲染为自包含 HTML 报告，确保输出质量一致。
纯 stdlib 实现，无第三方依赖。

用法:
  python render_report.py input.json -o report.html
  python render_report.py input.json                # 默认输出 literature-review.html
  python render_report.py --example                  # 生成示例 JSON + 示例 HTML

JSON 输入格式:
{
  "topic": "数字化转型与企业创新",
  "keywords": ["digital transformation", "corporate innovation"],
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
      "finding": "1-2句话核心结论",
      "relevance": "极高。直接研究了数字化转型对企业创新的影响机制",
      "relevance_level": "极高",
      "tags": ["数字化转型", "企业创新"],
      "journal_tag": "UTD24"
    }
  ],
  "tier2": [...],
  "tier3": [...],
  "suggestions": {
    "keyword_expansion": "建议扩展的方向",
    "uncovered_fields": "尚未覆盖的子领域",
    "manual_databases": "建议手动补充检索的数据库"
  }
}
"""

import json
import sys
import os
from datetime import datetime
from html import escape

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>核心文献清单：{topic}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&family=Noto+Serif+SC:wght@400;600;700&display=swap');

  :root {{
    --bg: #fafafa;
    --bg2: #f0f0f0;
    --ink: #1a1a1a;
    --muted: #666;
    --rule: #ddd;
    --accent: #c0392b;
    --accent2: #2980b9;
    --card-bg: #ffffff;
    --tier1: #c0392b;
    --tier2: #d4740e;
    --tier3: #27ae60;
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: 'Noto Sans SC', sans-serif;
    background: var(--bg);
    color: var(--ink);
    font-size: 15px;
    line-height: 1.8;
    -webkit-font-smoothing: antialiased;
  }}

  .container {{
    max-width: 960px;
    margin: 0 auto;
    padding: 2rem 2rem 4rem;
  }}

  .header {{
    text-align: center;
    padding: 3rem 0 2rem;
    border-bottom: 2px solid var(--accent);
    margin-bottom: 2rem;
  }}
  .header h1 {{
    font-family: 'Noto Serif SC', serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 0.5rem;
  }}
  .header .subtitle {{
    font-size: 0.95rem;
    color: var(--muted);
    font-weight: 300;
  }}
  .header .meta {{
    font-size: 0.8rem;
    color: var(--muted);
    margin-top: 1rem;
    opacity: 0.7;
  }}

  .search-summary {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 2rem;
    padding: 1rem 1.2rem;
    background: var(--card-bg);
    border: 1px solid var(--rule);
    border-radius: 6px;
    font-size: 0.85rem;
    color: var(--muted);
  }}
  .search-summary .label {{ font-weight: 700; color: var(--ink); }}
  .search-summary .stat {{
    margin-left: auto;
    font-weight: 500;
  }}
  .search-summary .stat b {{ color: var(--accent); }}

  .tier-section {{ margin-bottom: 3rem; }}
  .tier-badge {{
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 3px;
    color: #fff;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
  }}
  .tier-1 .tier-badge {{ background: var(--tier1); }}
  .tier-2 .tier-badge {{ background: var(--tier2); }}
  .tier-3 .tier-badge {{ background: var(--tier3); }}

  .tier-section h2 {{
    font-family: 'Noto Serif SC', serif;
    font-size: 1.3rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
  }}
  .tier-desc {{
    font-size: 0.85rem;
    color: var(--muted);
    margin-bottom: 1.5rem;
  }}

  .paper {{
    background: var(--card-bg);
    border: 1px solid var(--rule);
    border-radius: 6px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: box-shadow 0.2s;
  }}
  .paper:hover {{ box-shadow: 0 2px 12px rgba(0,0,0,0.06); }}
  .paper .title {{
    font-weight: 700;
    font-size: 1rem;
    color: var(--ink);
    margin-bottom: 0.4rem;
    line-height: 1.5;
  }}
  .paper .title .lang-tag {{
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 500;
    padding: 0.1rem 0.4rem;
    border-radius: 2px;
    margin-left: 0.4rem;
    vertical-align: middle;
    font-weight: 700;
    letter-spacing: 0.03em;
  }}
  .lang-en {{ background: #e8f0fe; color: #1a73e8; }}
  .lang-cn {{ background: #fce8e6; color: var(--accent); }}

  .paper .citation {{
    font-size: 0.82rem;
    color: var(--muted);
    margin-bottom: 0.6rem;
  }}
  .paper .citation .journal {{
    font-style: italic;
    font-weight: 500;
    color: var(--ink);
  }}
  .paper .finding {{
    font-size: 0.88rem;
    line-height: 1.7;
    margin-bottom: 0.6rem;
    color: #333;
  }}
  .paper .relevance {{
    font-size: 0.82rem;
    padding: 0.4rem 0.6rem;
    background: var(--bg);
    border-radius: 4px;
    border-left: 3px solid var(--accent);
  }}
  .paper .relevance strong {{ color: var(--accent); }}

  .tag {{
    display: inline-block;
    font-size: 0.7rem;
    padding: 0.15rem 0.5rem;
    border-radius: 3px;
    background: var(--bg2);
    color: var(--muted);
    margin-right: 0.3rem;
    margin-top: 0.5rem;
    font-weight: 500;
  }}
  .tag.primary {{ background: #fef3cd; color: #856404; }}

  .suggestions {{
    margin-top: 1rem;
    padding: 1.2rem 1.5rem;
    background: #f0f7ff;
    border: 1px solid #b3d4fc;
    border-radius: 6px;
  }}
  .suggestions h3 {{
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--accent2);
    margin-bottom: 0.8rem;
  }}
  .suggestions ul {{
    list-style: none;
    padding: 0;
  }}
  .suggestions li {{
    font-size: 0.85rem;
    line-height: 1.7;
    padding-left: 1.2rem;
    position: relative;
    margin-bottom: 0.4rem;
    color: #333;
  }}
  .suggestions li::before {{
    content: "\2192";
    position: absolute;
    left: 0;
    color: var(--accent2);
    font-weight: 700;
  }}

  .disclaimer {{
    margin-top: 3rem;
    padding: 1.2rem 1.5rem;
    background: #fffbe6;
    border: 1px solid #ffe58f;
    border-radius: 6px;
    font-size: 0.82rem;
    color: #666;
    line-height: 1.7;
  }}
  .disclaimer strong {{ color: var(--ink); }}

  @media (max-width: 768px) {{
    .container {{ padding: 1rem 1rem 2rem; }}
    .header h1 {{ font-size: 1.4rem; }}
    .paper {{ padding: 1rem; }}
  }}
</style>
</head>
<body>
<div class="container">

<div class="header">
  <h1>核心文献清单</h1>
  <div class="subtitle">{topic}</div>
  <div class="meta">整理时间：{date} &nbsp;|&nbsp; 核心关键词：{keywords}</div>
</div>

<div class="search-summary">
  <span><span class="label">检索范围：</span>{time_range}</span>
  <span><span class="label">语言：</span>{language}</span>
  <span class="stat">命中 <b>{tier1_count}</b> 篇核心池 &nbsp;/&nbsp; <b>{tier2_count}</b> 篇第二梯队 &nbsp;/&nbsp; <b>{tier3_count}</b> 篇补充池</span>
</div>

{tier1_html}

{tier2_html}

{tier3_html}

{suggestions_html}

<div class="disclaimer">
  <strong>使用说明：</strong>本清单基于多源检索（Web Search 交叉验证）整理，所有英文文献均可通过 DOI 或 Google Scholar 验证；中文文献已通过期刊官网、维普、万方等平台交叉确认。<strong>建议在使用前，通过 Google Scholar 或 CNKI 对关键文献做最终核实</strong>。期刊等级判定依据 UTD24 官方名单、ABS Academic Journal Guide 2024、NSFC 管理科学部认定 A 类期刊目录。
</div>

</div>
</body>
</html>"""

# Tier section templates
TIER_SECTION_TPL = """<div class="tier-section tier-{n}">
  <span class="tier-badge">第{label}梯队</span>
  <h2>{title}</h2>
  <div class="tier-desc">{desc}</div>
{papers}
</div>"""

PAPER_TPL = """  <div class="paper">
    <div class="title">
      {title}
      <span class="lang-tag lang-{lang}">{lang_upper}</span>
    </div>
    <div class="citation">
      {authors} ({year}). <span class="journal">{journal}</span>{volume}{pages}{doi}
    </div>
    <div class="finding">
      {finding}
    </div>
    <div class="relevance">
      <strong>关联度：{relevance_level}。</strong>{relevance}
    </div>
    {tags}
  </div>"""

TIER_CONFIG = {
    "1": {
        "n": "1",
        "label": "一",
        "title": "UTD24 / ABS 4* / 国自然管理科学A类",
        "desc": "经济学与管理学国际顶级期刊，及国内管理学顶级期刊",
    },
    "2": {
        "n": "2",
        "label": "二",
        "title": "高质量核心期刊（经济学顶刊 / NSFC A类扩展）",
        "desc": "国内经济学公认顶刊、NSFC A类期刊中管理学核心，以及高影响力实证研究",
    },
    "3": {
        "n": "3",
        "label": "三",
        "title": "补充参考类核心文献 [非核心必看]",
        "desc": "方法论基础文献、补充实证文献及高被引工作论文，纳入理由已在各篇中说明",
    },
}


def render_paper(p: dict) -> str:
    lang = p.get("lang", "en")
    lang_upper = "EN" if lang == "en" else "CN"

    volume = ""
    if p.get("volume"):
        volume = f", {p['volume']}"
        if p.get("issue"):
            volume += f"({p['issue']})"

    pages = ""
    if p.get("pages"):
        pages = f", {p['pages']}"

    doi = ""
    if p.get("doi"):
        doi = f". DOI: {p['doi']}"

    tags_html = ""
    tags = p.get("tags", [])
    journal_tag = p.get("journal_tag", "")
    if tags:
        first = True
        for t in tags:
            cls = "primary" if first else ""
            tags_html += f'    <span class="tag {cls}">{escape(t)}</span>\n'
            first = False
    if journal_tag:
        tags_html += f'    <span class="tag">{escape(journal_tag)}</span>\n'

    return PAPER_TPL.format(
        title=escape(p.get("title", "")),
        lang=lang,
        lang_upper=lang_upper,
        authors=escape(p.get("authors", "")),
        year=p.get("year", ""),
        journal=escape(p.get("journal", "")),
        volume=volume,
        pages=pages,
        doi=doi,
        finding=escape(p.get("finding", "")),
        relevance_level=escape(p.get("relevance_level", "")),
        relevance=escape(p.get("relevance", "")),
        tags=tags_html,
    )


def render_tier(tier_key: str, papers: list) -> str:
    if not papers:
        return ""
    cfg = TIER_CONFIG[tier_key]
    papers_html = "\n".join(render_paper(p) for p in papers)
    return TIER_SECTION_TPL.format(
        n=cfg["n"],
        label=cfg["label"],
        title=cfg["title"],
        desc=cfg["desc"],
        papers=papers_html,
    )


def render_suggestions(data: dict) -> str:
    s = data.get("suggestions", {})
    if not s:
        return ""

    items = []
    if s.get("keyword_expansion"):
        items.append(f"<li><strong>关键词扩展方向：</strong>{escape(s['keyword_expansion'])}</li>")
    if s.get("uncovered_fields"):
        items.append(f"<li><strong>尚未覆盖的子领域：</strong>{escape(s['uncovered_fields'])}</li>")
    if s.get("manual_databases"):
        items.append(f"<li><strong>建议手动补充检索的数据库：</strong>{escape(s['manual_databases'])}</li>")

    if not items:
        return ""

    return f"""<div class="suggestions">
  <h3>检索建议与下一步</h3>
  <ul>
{chr(10).join(items)}
  </ul>
</div>"""


def render(data: dict) -> str:
    topic = escape(data.get("topic", ""))
    keywords = " / ".join(escape(k) for k in data.get("keywords", []))
    time_range = escape(data.get("time_range", "近5年"))
    language = escape(data.get("language", "中英文"))
    date = datetime.now().strftime("%Y年%m月")

    tier1_html = render_tier("1", data.get("tier1", []))
    tier2_html = render_tier("2", data.get("tier2", []))
    tier3_html = render_tier("3", data.get("tier3", []))
    suggestions_html = render_suggestions(data)

    return HTML_TEMPLATE.format(
        topic=topic,
        keywords=keywords,
        time_range=time_range,
        language=language,
        date=date,
        tier1_count=len(data.get("tier1", [])),
        tier2_count=len(data.get("tier2", [])),
        tier3_count=len(data.get("tier3", [])),
        tier1_html=tier1_html,
        tier2_html=tier2_html,
        tier3_html=tier3_html,
        suggestions_html=suggestions_html,
    )


def generate_example_json(path: str):
    example = {
        "topic": "数字化转型与企业创新",
        "keywords": ["digital transformation", "corporate innovation", "IT capability"],
        "time_range": "2020-2025",
        "language": "中英文",
        "tier1": [
            {
                "title": "The Impact of Digital Transformation on Firm Innovation Performance: Evidence from China",
                "lang": "en",
                "authors": "Li, M., Wang, H., & Zhang, Y.",
                "year": 2023,
                "journal": "Management Science",
                "volume": "69",
                "issue": "4",
                "pages": "2345-2367",
                "doi": "10.1287/mnsc.2022.4567",
                "finding": "数字化转型通过提升知识管理效率和促进组织学习，显著提高了企业创新绩效，且该效应在高科技行业中更为突出。",
                "relevance": "直接研究了数字化转型对企业创新的影响机制，样本为中国上市公司。",
                "relevance_level": "极高",
                "tags": ["数字化转型", "企业创新"],
                "journal_tag": "UTD24",
            },
            {
                "title": "数字化转型、组织韧性与企业创新",
                "lang": "cn",
                "authors": "张三, 李四, 王五",
                "year": 2024,
                "journal": "管理世界",
                "volume": "",
                "issue": "3",
                "pages": "112-130",
                "doi": "",
                "finding": "数字化转型通过增强组织韧性间接促进企业创新，中介效应在环境不确定性较高时更为显著。",
                "relevance": "从组织韧性视角揭示数字化转型影响创新的间接路径，补充了机制分析。",
                "relevance_level": "极高",
                "tags": ["数字化转型", "组织韧性"],
                "journal_tag": "国自然A类",
            },
        ],
        "tier2": [
            {
                "title": "Digital Innovation Ecosystems: A Review and Research Agenda",
                "lang": "en",
                "authors": "Chen, S., & Liu, X.",
                "year": 2022,
                "journal": "Journal of Management Studies",
                "volume": "59",
                "issue": "6",
                "pages": "1567-1590",
                "doi": "10.1111/joms.12890",
                "finding": "构建了数字创新生态系统的分析框架，提出平台治理和生态协同是数字创新绩效的关键驱动因素。",
                "relevance": "提供了数字化创新的生态系统视角，对理解企业数字化转型有理论参考价值。",
                "relevance_level": "高",
                "tags": ["数字创新", "生态系统"],
                "journal_tag": "ABS4*",
            }
        ],
        "tier3": [
            {
                "title": "Does Digital Transformation Improve Firm Performance? Evidence from Chinese Manufacturing",
                "lang": "en",
                "authors": "Wang, J., & Zhao, K.",
                "year": 2023,
                "journal": "Journal of Organizational Computing and Electronic Commerce",
                "volume": "33",
                "issue": "2",
                "pages": "178-198",
                "doi": "10.1080/10919392.2022.2071234",
                "finding": "数字化转型显著提升了制造业企业财务绩效，但创新投入的中介效应仅在高技术制造业中成立。",
                "relevance": "聚焦制造业细分场景，补充了核心池文献的异质性分析。",
                "relevance_level": "中",
                "tags": ["数字化转型", "制造业"],
                "journal_tag": "SSCI",
            }
        ],
        "suggestions": {
            "keyword_expansion": "建议扩展至 \"AI adoption\"、\"digital capability\"、\"technology adoption\" 等术语",
            "uncovered_fields": "数字化转型对绿色创新、ESG表现的影响尚未覆盖",
            "manual_databases": "建议手动在 CNKI 和 Web of Science 中补充检索中文核心文献",
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(example, f, ensure_ascii=False, indent=2)
    print(f"Example JSON saved: {path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python render_report.py input.json [-o output.html]")
        print("       python render_report.py --example")
        sys.exit(1)

    if sys.argv[1] == "--example":
        out_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(out_dir, "example_input.json")
        html_path = os.path.join(out_dir, "example_output.html")
        generate_example_json(json_path)

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        html = render(data)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Example HTML saved: {html_path}")
        sys.exit(0)

    input_path = sys.argv[1]
    output_path = "literature-review.html"

    if "-o" in sys.argv:
        idx = sys.argv.index("-o")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    html = render(data)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Report saved: {output_path}")
    print(f"  Tier 1: {len(data.get('tier1', []))} papers")
    print(f"  Tier 2: {len(data.get('tier2', []))} papers")
    print(f"  Tier 3: {len(data.get('tier3', []))} papers")
    print(f"  Total: {sum(len(data.get(f'tier{i}', [])) for i in [1,2,3])} papers")


if __name__ == "__main__":
    main()
