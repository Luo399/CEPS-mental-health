# 第 3 章 · 三层架构在 EmpiricalWiki 里长什么样

**本章你会读到**

- raw / wiki / schema 这三个文件夹在硬盘上的具体形态
- 每一层的文件命名规则、修改权限、生命周期
- 为什么把这三层做成"严格分开的目录"，而不是放在一个大文件夹里
- 当你 `git clone` EmpiricalWiki 之后，看到的目录结构每一项是干什么的

---

## 3.1 把三层架构落到硬盘上

第 2 章讲清楚了 Karpathy 设计的三层架构是怎么一回事。但 raw 也好，wiki 也好，schema 也好，听起来都是抽象概念。具体到电脑硬盘上，它们究竟以什么形态存在？

答案直白：**就是三个文件夹**。

把 EmpiricalWiki 项目克隆到本地，进入项目目录，运行一条命令：

```bash
ls
```

会看到这样一份清单（删去了一些跟主架构不直接相关的文件）：

```
EmpiricalWiki/
├── CLAUDE.md          ← 这是 schema
├── raw/               ← 这是 raw
└── wiki/              ← 这是 wiki
```

就这么简单。三层架构在硬盘上对应三件东西：一个 markdown 文件（CLAUDE.md），两个目录（raw/ 和 wiki/）。整套设计能跑起来，靠的不是多复杂的工程，而是这三件东西之间的边界画得清楚。

剩下三节会逐一展开每一层。

## 3.2 raw 层：你给系统看的所有原始材料

raw 目录是你给 EmpiricalWiki 看的所有原始材料的存放地。这里面的文件**永远不被任何摄入流程修改**——这条规矩第 2 章讲过，这里看具体落地。

raw 目录的实际结构是这样的：

```
raw/
├── papers/            ← 你自己的 PDF 论文
├── notes/             ← 你自己的研究笔记
├── web/               ← 你保存的网页 / 博客文章
├── discovered/        ← /init 和 /daily-arxiv 自动下载的论文
└── tmp/               ← /init 临时生成的 sidecar 文件
```

前三个目录（papers, notes, web）属于"用户自有材料"。系统对这三个目录的访问权限是**只读**——任何 skill 都不允许往这里写文件，更不允许修改已有文件。这是底线。

后两个目录（discovered, tmp）是"系统生成材料"，存放的是自动抓取或处理过程中产生的中间文件。这两个目录的存在不是为了好玩，是为了把"用户自有"和"系统自有"严格隔开。比如 `/daily-arxiv` 这个 skill 每天会去 arXiv 抓新论文，这些论文必须有地方放，但不能跟你自己挑选的 `raw/papers/` 混在一起——否则三个月后你打开 `raw/papers/` 已经分不清哪些是你自己挑的、哪些是系统抓的。所以系统抓的全部进 `raw/discovered/`。

> [!NOTE]
> **铁律：raw 只读**
>
> 任何 EmpiricalWiki 的 skill，无论它是 `/empirical-ingest` 还是 `/edit` 还是 `/check`，对 `raw/papers/`、`raw/notes/`、`raw/web/` 这三个目录的访问权限都是只读。这条规矩写在 CLAUDE.md 里，被每一个 skill 强制执行。
>
> 唯一允许在 raw 下新增内容的入口是 `/edit`，且必须有用户的明确指令。这个 skill 的逻辑也是把新材料追加到 raw 里，**永不修改既有文件**。

raw 这一层的设计哲学是：**研究者投喂给系统的材料，是研究者的资产，不是系统的资产**。系统只能读，不能改。这条规矩看起来很苛刻，但它解决了一件大事——**任何时候你想销毁整个 wiki 重新来过，raw 都还在，可以从零再生成一份**。这就是第 2 章说的"信任"——只要 raw 还原封不动，wiki 出问题永远可以推倒重来。

## 3.3 wiki 层：模型实际工作的地方

wiki 目录是 EmpiricalWiki 真正"干活"的地方。模型每次摄入新材料，最后输出的所有改动都落在这里。

wiki 目录长这样：

```
wiki/
├── papers/            ← 论文卡片
├── variables/         ← 变量定义
├── datasets/          ← 数据集说明
├── models/            ← 模型设定
├── mechanisms/        ← 机制路径
├── hypotheses/        ← 研究假设
├── identification/    ← 识别策略
├── robustness/        ← 稳健性检验
├── heterogeneity/     ← 异质性分组
├── tables/            ← 表格说明
├── concepts/          ← 通用概念页
├── topics/            ← 研究主题地图
├── people/            ← 研究者档案
├── ideas/             ← 你自己的研究 idea
├── claims/            ← 可被验证的断言
├── Summary/           ← 综述
├── foundations/       ← 教科书背景
├── outputs/           ← 生成的产物
├── graph/             ← 自动生成的图谱
├── index.md           ← 内容目录
└── log.md             ← 编年志
```

看起来有点多。这二十来个东西可以分成三类。

**第一类是经管特化的实体目录**（papers, variables, datasets, models, mechanisms, hypotheses, identification, robustness, heterogeneity, tables）。这十个目录是 EmpiricalWiki 在 Karpathy 通用模式上做的核心特化，每一个都对应实证研究流程里的一个具体环节。第 4 章会专门讲这十个为什么这样切分。

**第二类是通用研究 wiki 类型**（concepts, topics, people, ideas, claims, Summary, foundations）。这七个目录继承自上游的通用 wiki 框架，处理跟具体研究主题没关系的东西——比如理论概念、研究者档案、研究主题地图。

**第三类是系统生成的目录和文件**（outputs, graph, index.md, log.md）。这些不是给你直接看的，是系统跑出来的辅助产物。`graph/` 里存放着所有页面之间的链接关系，是双向链接网络的底层数据；`index.md` 是 wiki 的内容目录，每次摄入后自动重建；`log.md` 是 wiki 的编年志，每次有什么事发生都会被追加一行。

> [!TIP]
> **wiki 目录的命名约定**
>
> 大部分目录小写英文，唯独 `Summary/` 首字母大写。这不是手抖，是为了视觉上把"综述"这种"高层产物"和那些"原子实体"区分开。打开 wiki 目录时一眼能看出哪些是"原料"哪些是"加工产物"。这是从上游 ΩmegaWiki 继承来的设计。

每个目录里的文件都是 markdown 格式，文件名就是这个实体的 slug。比如 `wiki/variables/patient-capital.md` 就是耐心资本这个变量的页面。打开来看长这样（这里只截取最关键的部分）：

```markdown
---
title: "耐心资本（Patient Capital）"
slug: "patient-capital"
construct_type: "explanatory"
date_added: 2026-04-12
source_papers:
  - dai-fei-2025
  - chu-pei-pei-2025
  - jia-yong-2025
---

# 耐心资本

## 定义
耐心资本指愿意长期持有、容忍短期波动并深度参与公司治理的资本类型。

## Literature Variants（跨论文变体累积）

### A1 经典版（机构投资者换手率三分组）
来源论文：[[dai-fei-2025]]、[[jia-yong-2025]]
测算：按机构投资者年度换手率三分组，最低组定义为耐心资本机构...

### A2 标准差变体
来源论文：[[chu-pei-pei-2025]]
测算：用过去三年持股稳定性的标准差倒数...
```

这就是 wiki 这一层每个文件的实际样子——**头部一段叫 frontmatter 的元数据，下面是结构化的正文章节**。

每个文件的频率和形态都不一样。论文页面会有"研究问题、变量、模型、识别"这些固定章节；变量页面会有"定义、Literature Variants、可用数据源"这些章节；机制页面会有"机制名、文献证据、跨论文一致性"这些章节。具体长什么样下一章会展开讲。

wiki 这一层是动态的，会随着每次摄入而变化。今天 ingest 一篇新论文，明天打开 `wiki/variables/patient-capital.md` 可能比昨天多了一段 Literature Variants。这是这套系统真正运转起来后的样子。

## 3.4 schema 层：CLAUDE.md 这一份文件

schema 这一层在 EmpiricalWiki 里就是一份文件——`CLAUDE.md`，放在项目根目录。

CLAUDE.md 的内容是给模型读的"工作守则"。它不是注释，不是说明书，而是**模型每次启动时第一个读的文件**，里面写的每一条规则都直接影响接下来摄入的行为。

CLAUDE.md 的具体内容大概可以分为四块。

第一块是**项目身份信息**。这是 wiki 是什么、研究主题是什么、有什么主要文献。这块的作用是让模型每次启动时知道自己在哪。比如：

```markdown
# 这是一个关于「耐心资本」研究的 EmpiricalWiki

研究主题：长期持有资本对企业行为的影响
主要文献：20 篇 2015-2026 年发表于中文核心期刊的实证论文
研究阶段：文献摄入完成，进入综述写作阶段
```

第二块是**术语锁定**。每个研究领域都有一些核心术语，这些术语在不同论文里可能用不同的中文翻译或缩写。模型如果不知道这些术语必须保持一致，就会出现一篇论文里用"耐心资本"、另一篇用"PC 资本"、第三篇用"长期资本"的混乱情况。术语锁定就是把这些核心术语的标准写法定下来：

```markdown
术语锁定：
- 耐心资本（不要写成 PC 资本、长期资本、长期主义资本）
- 双元创新（不要写成 ambidextrous innovation）
- Sasabuchi 检验（不要写成 Sasabuchi 试验、Sasabuchi 测试）
```

第三块是**目录写入权限**。这块直接告诉模型哪些目录能写、哪些不能。

```markdown
写入权限：
- raw/papers/、raw/notes/、raw/web/：永远只读
- wiki/papers/、wiki/variables/...：可写
- wiki/graph/、wiki/index.md、wiki/log.md：自动生成，不直接编辑
```

第四块是**双向链接规则**。这是把 Bush 在 1945 年提出的 associative trails 落地的关键。规则的核心是：写一条正向链接，必须同时写对应的反向链接。

```markdown
双向链接规则（必须同步）：
- 在 papers/A.md 里加 [[concept-B]] → 必须在 concepts/B.md 的 source_papers 里加 A
- 在 papers/A.md 里加 [[paper-C]] → 必须在 papers/C.md 的 cited_by 里加 A
（依此类推，所有双向关系都要同步）
```

这四块加起来，构成了模型的工作守则。任何时候你觉得模型表现得不对，**第一件事是检查 CLAUDE.md 里的规则是不是写清楚了**——大概率不是模型有问题，是 CLAUDE.md 没说清楚。

> [!TIP]
> **CLAUDE.md 不是一锤子买卖**
>
> 你的研究方向会演化。今天你只关心论文摘要，半年后你开始重视识别策略，CLAUDE.md 里就要相应加上一条"摄入时识别识别策略，落到 wiki/identification/"的规则。修改 CLAUDE.md 不需要重新训练模型，下次启动模型读到新规则，行为立刻就变了。
>
> 这是 schema 这一层最有意思的地方——**它把"项目规范"做成了一份可以随时编辑的文本文件**。任何懂中文的研究者都能修改它，不需要懂代码。

<div align="center">
  <img src="../assets/chap03/03_three_layers.gif" alt="三层架构的具体目录展开" width="640" />
</div>

## 3.5 为什么要把这三层做成独立的目录

读到这里你可能会问：把 raw、wiki、schema 弄成三个完全独立的东西，会不会太教条？为什么不直接把所有东西放一个大文件夹里？

答案有三个层次。

**第一个层次是技术上的清楚**。三个目录边界清楚，各自的访问规则就好定义。raw 只读，wiki 可写，schema 是规则——一句话说完。如果都堆在一起，每次有写操作都得问"这个文件能不能改"，规则会变得复杂。

**第二个层次是工程上的可恢复**。raw 不动意味着 wiki 永远可以从零重建。如果哪天你觉得 wiki 被某个错误的判断污染了，删掉重来即可——raw 还在。这种"可重置"特性在长期使用中非常重要，因为任何长期生长的系统都会出问题，需要时不时推倒重来。

**第三个层次是认知上的减负**。研究者使用 wiki 时，知道自己在每个时刻动的是哪一层，心里就清楚。读 raw 是输入，读 wiki 是查询，改 schema 是调整规则。三件事各走各的路，不混在一起。这跟代码项目里把"源代码、构建产物、配置文件"分目录是一个道理。

这三个层次合起来，让 EmpiricalWiki 在长期使用中不会因为复杂度上升而崩溃。Bush 设想的 Memex 失败的原因之一就是没有把这种边界画清楚——他设想的是一个"什么都能做"的盒子，结果什么都做不好。Karpathy 这套设计的高明之处在于，它先把边界画清，再让每一层各做各的。

---

## 本章小结

EmpiricalWiki 的三层架构在硬盘上对应三件具体的东西：一份 CLAUDE.md（schema 层）、一个 raw 目录（原始材料层）、一个 wiki 目录（结构化知识层）。raw 是只读的、用户自有的、永远可被用来重新生成 wiki 的输入材料；wiki 是模型实际工作的地方，按经管实证研究流程被切分成多个实体目录；schema 是一份 markdown 格式的工作守则，告诉模型"在这个项目里要遵守哪些规则"。

下一章会展开 wiki 目录里那十个经管特化的实体目录——为什么是这十个、每一个解决什么问题、它们一起怎么覆盖一篇实证论文的所有内容。

---

[^claude-md-design]: 这种"用一份自然语言文件作为项目规范"的设计来自 Anthropic 的 Claude Code 工具。CLAUDE.md 是 Claude Code 在每个项目根目录会自动读取的文件，模型在每次会话开始时把它当作系统指令的一部分。这个设计后来被许多类似的 AI 编辑器采纳。
