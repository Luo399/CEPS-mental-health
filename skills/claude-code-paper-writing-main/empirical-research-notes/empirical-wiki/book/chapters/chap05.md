# 第 5 章 · 28 个命令构成的工作流

**本章你会读到**

- skill 在 EmpiricalWiki 里到底是什么形态的东西
- 28 个 skill 按四个研究阶段怎么划分
- 经管特化的那 4 个 skill 各自解决什么问题
- 一项研究从读文献到出论文，会用到哪些 skill 串成的工作流

---

## 5.1 skill 是研究者跟 wiki 打交道的方式

第 3 章讲了 EmpiricalWiki 的三层架构（raw / wiki / schema），第 4 章讲了 wiki 里的 10 类经管特化实体。但是研究者每天打开电脑要做的事，不是直接编辑这些 markdown 文件——**研究者需要一种方便的方式让模型代替自己干活**。这个方式就是 skill。

skill 在 EmpiricalWiki 里的具体形态是**斜杠命令**（slash command）。在 Claude Code 的命令行界面里输入 `/empirical-ingest`，就触发了"摄入一篇实证论文"这个工作流；输入 `/variable-map`，就触发了"汇总某个构念在所有论文里的测算变体"这个工作流。

每个 skill 在底层是一份 markdown 文件，定义了"这个命令需要做什么、需要读什么文件、需要写什么文件、需要遵守什么规则"。用户在终端打入命令，模型读取对应的 skill 定义文件，按里面写的步骤执行。

这种设计的关键好处是**透明**——所有 skill 的行为都写在 markdown 文件里，不是埋在代码里。任何研究者都可以打开 `.claude/skills/empirical-ingest/SKILL.md` 看这个命令到底做了什么。觉得不对，可以直接修改这个文件，下次执行就按新的逻辑走。

> [!NOTE]
> **skill 是声明式的，不是过程式的**
>
> 传统软件里的"功能"是用代码实现的，要改功能得改代码。EmpiricalWiki 里的 skill 是用自然语言描述的，要改 skill 行为，改的是 markdown 文件里的描述。这种"声明式"的设计让所有研究者——不只是会编程的——都能定制自己的工作流。

EmpiricalWiki 当前共有 **28 个 skill**，按研究的四个阶段划分。

## 5.2 第一阶段：环境准备（Setup）

这一阶段只有 2 个 skill，用于第一次配置 EmpiricalWiki 项目。

| 命令 | 干什么 |
|:---|:---|
| `/setup` | 第一次配置 API key、语言、依赖 |
| `/reset` | 销毁式清理（按范围：wiki / raw / log / checkpoints / all） |

`/setup` 是新用户第一次跑的命令。`/reset` 在开发迭代或某次 ingest 出问题想推倒重来时用——这就是第 3 章说的"raw 不动 → wiki 永远可重建"的实际入口。

## 5.3 第二阶段：知识基础（Knowledge Foundation）

这一阶段是把研究材料变成结构化 wiki 内容的核心工作流，共 **8 个 skill**：

| 命令 | 干什么 |
|:---|:---|
| `/prefill` | 用领域基础知识填充 `foundations/`（避免 ingest 时给教科书概念建独立页面） |
| `/init` | 基于 `raw/papers/` 文献批量初始化整个 wiki |
| **`/empirical-ingest`** | **【经管特化】** 把一篇实证论文消化成完整的 10 类实体 + 双向链接 |
| `/ingest` | 通用版本的 ingest（非纯实证论文用这个） |
| `/discover` | 从已有 wiki 推荐"接下来该读哪些论文" |
| **`/variable-map`** | **【经管特化】** 汇总某个构念在 wiki 里所有的测算变体 |
| `/edit` | 增删 raw 来源、修订 wiki 内容 |
| `/ask` | 对 wiki 提问，模型读 wiki 给答案 |

这 8 个里有两个加粗了——`/empirical-ingest` 和 `/variable-map`。它们是 EmpiricalWiki 在通用 LLM Wiki 模式之上做的经管特化 skill。

`/empirical-ingest` 的作用是把一篇实证论文按第 4 章讲的 10 类实体拆分摄入。它跟通用 `/ingest` 的差异是：通用 ingest 会把论文塞进 papers + concepts + people 三种通用类型，经管 ingest 会拆出变量、数据集、模型、机制、识别、稳健性、异质性、表格这些一等公民实体。

`/variable-map` 的作用是查询某个构念的测算累积。比如运行：

```bash
/variable-map "耐心资本"
```

模型会扫描 wiki 里所有跟耐心资本相关的论文页面，汇总 8 种测算口径、每种口径用了哪些论文、每种口径的优缺点和适用场景，输出一份 markdown 报告。

> [!TIP]
> **为什么 `/variable-map` 单独做一个 skill**
>
> 因为这是经管实证研究最频繁的查询动作之一。任何研究者写综述、做对比、决定自己用哪种测算时，都会反复问"这个构念有几种测算方式、各自有什么差异"。把它做成一个 skill，意味着这个动作有了**专门的入口**——研究者不需要每次都重新组织语言去问，一条命令就够。

`/ask` 是更通用的查询入口。任何 wiki 里能查到的问题都可以问 `/ask`。它跟 `/variable-map` 的差异是：`/variable-map` 是结构化查询（专门查变量测算），`/ask` 是自由查询（任何问题）。

`/check` 不在这一节，但跟 ask 关系密切——它是 wiki 的健康扫描，每隔一段时间跑一次，找出双向链接缺失、孤立实体、字段不合规等问题。

## 5.4 第三阶段：研究设计与执行（Research Design & Execution）

这一阶段把 wiki 里的知识转化为研究设计与执行计划，共 **11 个 skill**：

| 命令 | 干什么 |
|:---|:---|
| **`/empirical-design`** | **【经管特化】** 基于 wiki 知识生成研究问题 + 变量设计 + 模型 + 识别 + 异质性 + 稳健性 + 数据缺口 |
| **`/stata-plan`** | **【经管特化】** 把研究设计转成 Stata 执行计划，可一并生成 .do 骨架 |
| `/daily-arxiv` | 每日自动从 arXiv 拉新论文（cron 任务） |
| `/ideate` | 从 wiki 中跨主题寻找研究 idea |
| `/novelty` | 多源验证某个 idea 是否新颖 |
| `/review` | 跨模型对任何研究产物做评审 |
| `/exp-design` | claim 驱动的实验设计（用于计算实验、仿真） |
| `/exp-run` | 部署 + 监控实验 |
| `/exp-status` | 实验状态看板 |
| `/exp-eval` | 实验结果裁决，自动更新 claims |
| `/refine` | 多轮迭代改进任意研究产物 |

加粗的两个又是经管特化的。

`/empirical-design` 是这一阶段的核心入口。它的输入是一句简单的研究问题（比如"耐心资本对企业 ESG 表现的影响"），输出是一份完整的实证设计提案：研究问题怎么定义、自变量因变量怎么测算（基于 wiki 里已有变量页面）、用什么模型（基于 wiki 里已有模型页面）、识别策略是什么、异质性怎么切、稳健性查什么。它不是凭空生成的——**它的所有内容都是从 wiki 里已有的实体页面拼装出来的**，所以提案里每个建议都能追溯到具体文献。

`/stata-plan` 是 `/empirical-design` 之后的下一步。给它一份研究设计，它输出可以直接在 Stata 里运行的 .do 文件骨架——数据合并代码、变量构造代码、回归代码、稳健性检验代码、表格输出代码。研究者拿到这份骨架，跑数据，看结果，需要的话再调整。

剩下的 9 个 skill 大部分是从上游 ΩmegaWiki 继承来的通用工具，主要服务于"探索性研究 + 实验执行"场景。在经管实证里，最常用的是 `/review`（让另一个模型评审你的研究设计或论文初稿，给出独立意见）和 `/refine`（多轮迭代改进，每轮跑一次 review，再修改）。

## 5.5 第四阶段：写作与提交（Writing & Submission）

这一阶段是把所有积累的知识转化为成品论文的工作流，共 **6 个 skill**：

| 命令 | 干什么 |
|:---|:---|
| `/survey` | 从 wiki 知识生成 Related Work 章节 |
| `/paper-plan` | claim 图谱 → 论文提纲 |
| `/paper-draft` | 提纲 + wiki → LaTeX 草稿 |
| `/paper-compile` | LaTeX 编译 → PDF，自动修复编译错误 |
| `/research` | 端到端的研究编排器（把以上步骤串起来） |
| `/rebuttal` | 解析审稿意见，逐条生成回复草稿 |

`/survey` 跟传统综述写作的差异是：它读的不是原始 PDF，是 wiki 里已经被结构化的内容。**所以它能立刻给出"耐心资本研究的 8 种主流测算方式"这种结构化结论**，不需要先把 20 篇 PDF 重读一遍。

`/paper-plan` 和 `/paper-draft` 把 wiki 当作论文的素材库——claim 是论点、papers 是证据、variables 是变量定义、models 是方法依据。从 wiki 拼出一份初稿，给研究者一个起点。**真正的论文写作还是要研究者自己来**——AI 不替你想 idea，但可以替你处理"把已有信息组织成段落"的机械性工作。

`/rebuttal` 解决的是审稿意见处理的痛点。审稿人的意见可能涉及"变量测算的稳健性""识别策略的有效性""异质性分析的覆盖度"等等。这些问题在 wiki 里都有结构化答案——`/rebuttal` 把审稿意见解析成原子问题，逐个去 wiki 里找对应证据，组织成回复草稿。

<div align="center">
  <img src="../assets/chap05/05_skill_map.gif" alt="28 个 skill 按四阶段划分" width="640" />
</div>

## 5.6 一项研究的典型工作流

把上面 28 个 skill 串起来，一项研究从开始到投稿的完整工作流大致是这样：

```
1. /setup                   首次配置
2. /init [topic]            投喂初始文献，初始化 wiki
3. /empirical-ingest × N    逐篇精细摄入
4. /variable-map "X"        汇总核心变量的测算变体
5. /empirical-design        生成自己的研究设计
6. /review                  让另一个模型独立评审设计
7. /refine                  根据 review 迭代改进
8. /stata-plan              生成 Stata 执行计划
   ↓ 跑数据，得到结果
9. /paper-plan              基于 claim 图谱生成提纲
10. /paper-draft            按提纲生成草稿
11. /survey                 生成 Related Work 章节
12. /paper-compile          编译成 PDF
   ↓ 投稿
13. /rebuttal               处理审稿意见
```

不是每项研究都会用全部 13 个 skill。大部分研究只会用其中的 5-8 个核心 skill。**这个工作流的意义不是"必须按顺序走完"，而是"每个研究阶段你都知道有现成的工具可以用"**。

## 5.7 skill 列表会随实际使用演化

28 个不是一锤定音的数字。skill 列表会随着实际使用持续调整——某个 skill 长期没人用，会被合并掉；遇到一个反复出现的高频动作没有专门 skill，会新加一个。这种"按使用反馈调整"的方式跟 schema 这一层的演化逻辑一脉相承，整个 EmpiricalWiki 都按这条思路设计：边界清楚，允许长大。

> [!TIP]
> **怎么自己加一个 skill**
>
> 在 `.claude/skills/` 目录下新建一个文件夹，放一份 SKILL.md 文件，写清楚这个 skill 做什么、读什么、写什么。下次启动 Claude Code，新 skill 就出现在命令列表里了。整个过程不需要写一行代码。

---

## 本章小结

EmpiricalWiki 通过 28 个 slash command（skill）让研究者跟 wiki 打交道。这 28 个命令按研究的四个阶段划分：环境准备（2 个）、知识基础（8 个）、研究设计与执行（11 个）、写作与提交（6 个）。其中 4 个是经管特化的——`/empirical-ingest` 处理实证论文的细致摄入，`/variable-map` 汇总跨论文测算变体，`/empirical-design` 从 wiki 生成研究设计，`/stata-plan` 把研究设计转成 Stata 可执行计划。

每个 skill 是一份 markdown 文件而不是代码，研究者可以打开看它的逻辑、自己修改。这种设计让 EmpiricalWiki 的所有功能都对研究者透明——**没有"黑盒"，没有"魔法"**。

下一章会进入实操——拿一篇真实论文走一遍完整的 `/empirical-ingest` 流程，看从 PDF 到 wiki 卡片的整个过程在 5 分钟里发生了什么。

---
