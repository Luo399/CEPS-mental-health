# Claude Code 科研手记

[English](README_EN.md) | **简体中文**

用 Claude Code 写论文的真实记录。把走过的每一步、踩过的每一个坑、稳定下来的每一条习惯整理成书,并把同期沉淀下来的工具集和实战笔记一并收在这里。

---

## 怎么读

挑一种顺手的方式开始,不用从头读到尾。

- **直接读全本** &nbsp;→&nbsp; 打开 [`book-main.pdf`](book-main.pdf),iPad / Kindle / 打印机都行
- **在线翻章节** &nbsp;→&nbsp; 从 [第 1 章](chapters/chap01.md) 起,完整目录见 [一、书籍](#一书籍)
- **只想拿模板用** &nbsp;→&nbsp; [附录 A · 提示词模板](chapters/appendix-a.md) · [附录 D · CLAUDE.md 模板](chapters/appendix-d.md) · [附录 E · 错误速查](chapters/appendix-e.md)
- **想直接装 Skill** &nbsp;→&nbsp; [`skills/`](skills/) 下按场景分了七类,挑当下最痛的那一类
- **想看实证研究怎么落地** &nbsp;→&nbsp; [`empirical-research-notes/`](empirical-research-notes/) 视频系列配套讲义

---

## 整体框架

仓库下三块内容是**并列结构**,各自独立,串起来覆盖 *方法论 → 工具链 → 落地实战* 完整链路。需要哪一块直接进对应入口,不用从头读起。

| 板块 | 形式 | 内容定位 | 入口 |
|------|------|----------|------|
| **① 书籍** | 16 章 + 6 附录 + 全本 PDF | Claude Code 在科研写作中的方法论与心态 | [`chapters/`](chapters/) · [`book-main.pdf`](book-main.pdf) |
| **② 配套 Skill** | 7 大类共 32 个 Skill | 检索、画图、数据分析、写作纪律的现成工具集 | [`skills/`](skills/) |
| **③ 经管实证研究系列笔记** | 视频配套文字讲义,按集累积 | 从环境准备到正文写作的完整实证研究流水线 | [`empirical-research-notes/`](empirical-research-notes/) |

三块的关系:**书籍**讲为什么这么做、心态怎么放;**Skill** 是这套方法的可复用工具栈;**实证研究笔记**把整套东西在一条具体研究流水线上演一遍。

下面三节按顺序展开。

---

## 一、书籍

**第一部分 · 启程**
1. [Claude Code 是什么,为什么它适合写论文](chapters/chap01.md)
2. [上下文与记忆](chapters/chap02.md)
3. [提示词的实战经验](chapters/chap03.md)

**第二部分 · 核心技能**

4. [文献调研与管理](chapters/chap04.md)
5. [章节写作](chapters/chap05.md)
6. [图表制作](chapters/chap06.md)
7. [引用与参考文献](chapters/chap07.md)
8. [格式排版与文件管理](chapters/chap08.md)

**第三部分 · 进阶能力**

9. [Skills:给 AI 装上专属工具](chapters/chap09.md)
10. [并行 Agent](chapters/chap10.md)
11. [Hooks](chapters/chap11.md)
12. [MCP 工具扩展](chapters/chap12.md)

**第四部分 · 思维方式**

13. [导师教会我的科研写作观](chapters/chap13.md)
14. [与 AI 协作的正确心态](chapters/chap14.md)

**第五部分 · 设计哲学**

15. [设计科研 Skill 的纪律](chapters/chap15.md)
16. [从一篇论文到科研工作习惯](chapters/chap16.md)

**附录**

- [A · 提示词模板](chapters/appendix-a.md)
- [B · 快捷键速查表](chapters/appendix-b.md)
- [C · 必备 Skill 推荐列表](chapters/appendix-c.md)
- [D · CLAUDE.md 科研版模板](chapters/appendix-d.md)
- [E · 常见错误速查](chapters/appendix-e.md)
- [F · paper-to-beamer 实战](chapters/appendix-f.md)

---

## 二、配套 Skill

所有 Skill 收在 [`skills/`](skills/) 下,按场景分成七类。需要哪一类直接进对应子目录,不用全装。

| 子目录 | 用途 | 收录的 skill | 备注 |
|---|---|---|---|
| [`literature-review/`](skills/literature-review) | **文献综述与引用** | arxiv-database · citation-management · pyzotero · review-orchestrator · management-review-planner · management-review-writer · openalex-ajg-insights · systematic-literature-review | review-gen 4 个 + SLR |
| [`figures/`](skills/figures) | **画图制图** | drawio · plotly · seaborn | |
| [`data-analysis/`](skills/data-analysis) | **数据分析** | xlsx · statistical-analysis | |
| [`slides/`](skills/slides) | **幻灯片制作** | paper-to-beamer · pptx | |
| [`document-handling/`](skills/document-handling) | **文档处理** | pdf · docx · markitdown | |
| [`writing-polish/`](skills/writing-polish) | **论文润色** | humanizer-zh · paper-polish-workflow | |
| [`paper-discipline/`](skills/paper-discipline) | **写作纪律** | 12 条 —— 改 Word 前先备份、跨章改术语前先列保护清单、动手前先说明方案 | **chanw 自制** |

---

## 三、经管实证研究系列笔记

视频系列的配套文字讲义,收在 [`empirical-research-notes/`](empirical-research-notes/) 下,按集累积。每一期对应实证研究流程里的一个具体阶段,从环境准备一路走到正文写作完成。

| 期数 | 主题 | 文件 |
|------|------|------|
| 第一期 | Claude Code 与 IDE 安装 | *将随系列推进逐期补齐* |
| 第二期 | 项目制与三个核心 markdown 文件 | *将随系列推进逐期补齐* |
| **第三期** | **用 Skill 做文献综述** | [`ep03-literature-review.md`](empirical-research-notes/ep03-literature-review.md) |

每一期讲义在视频上线时同步发布,主书里的方法论在这条流水线上能看到具体落地形态。

---

## 更新

- 新章节、新 Skill、新一期讲义在 **小红书 chanw** 公告
- 详细更新日志见 [CHANGELOG.md](CHANGELOG.md)
- 拿最新内容:`git pull` 即可

## 报错

发现错别字、命令跑不通、引用失效,直接开 [Issues](https://github.com/Chanw-research/claude-code-paper-writing/issues),通常 24 小时内回复。

## 立场

研究问题、实验数据、学术判断必须是你自己的;Claude Code 帮你把它们更高效地呈现出来,不替你思考。第 14 章和第 15 章把这条边界写成可执行的纪律。

## License

书籍内容 © 2026 chanw,保留所有权利。本仓库仅向 Chanw-research 组织成员开放,不得转发、分享、上传至任何公开网络,仅限购买者本人学习与研究使用。

排版模板 [ElegantBook](https://github.com/ElegantLaTeX/ElegantBook) 遵循 [LPPL v1.3c](License)。
