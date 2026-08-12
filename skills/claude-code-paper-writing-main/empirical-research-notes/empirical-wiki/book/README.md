# EmpiricalWiki 实战手册：从 Karpathy LLM Wiki 到实证

> 本书是 EmpiricalWiki 这一研究工具的使用手册，介绍其设计依据与工作流程。读者将了解如何把自己研究方向的文献库导入 EmpiricalWiki，得到可累积、可查询、可作为论文写作输入的结构化研究 wiki。

2026 年 4 月 3 日，Andrej Karpathy 在 GitHub Gist 上发布了一份名为 *llm-wiki* 的设计文档，提出大语言模型在研究工作流中的一个新定位：模型不应被作为问答接口使用，而应被作为一份持久知识库的维护者。使用者向模型提供原始材料，模型在每次摄入新材料时更新一份结构化的 markdown 知识库；后续的查询直接读取该知识库，而不再读取原始文档。Karpathy 在文中明确指出该提议是一种模式（pattern），需要在每个具体领域做出适配。

EmpiricalWiki 是该模式在经管实证研究领域的具体实现。其主要特化在两个方面：第一，将 Karpathy 提出的通用实体类型（`entity / concept / synthesis`）替换为 10 类与实证研究流程对应的实体（papers, variables, datasets, models, mechanisms, hypotheses, identification, robustness, heterogeneity, tables）；第二，在通用 skill 之外补充了 4 个经管特化的命令（`/empirical-ingest`, `/variable-map`, `/empirical-design`, `/stata-plan`），用于处理变量构造、跨文献变体汇总、研究设计生成与 Stata 执行计划生成等任务。

本书的目的是将上述设计与实现讲清楚：第 1 部分梳理 LLM Wiki 设想的提出背景与必要性，第 2 部分介绍 EmpiricalWiki 的具体形态，第 3 部分演示其完整使用流程。

<div align="center">
  <img src="assets/chap01/01_failure_loop.gif" alt="人维护 wiki 的失败循环" width="640" />
</div>

---

## 章节目录

<div align="center">

| 章 | 标题 |
|:--|:--|
| **第 1 部分 · 为什么需要 wiki** ||
| [第 1 章](chapters/chap01.md) | 一个 1945 年提出至今没解决的问题 |
| [第 2 章](chapters/chap02.md) | Karpathy 提的那个新思路，到底新在哪里 |
| **第 2 部分 · EmpiricalWiki 是什么** ||
| [第 3 章](chapters/chap03.md) | 三层架构在 EmpiricalWiki 里长什么样 |
| [第 4 章](chapters/chap04.md) | 一篇实证论文，能被拆成多少个零件 |
| [第 5 章](chapters/chap05.md) | 28 个命令构成的工作流 |
| **第 3 部分 · 怎么用** ||
| [第 6 章](chapters/chap06.md) | 第一篇文献的摄入：5 分钟里发生了什么 |
| [第 7 章](chapters/chap07.md) | 跨论文累积：一张变量页面如何从一段长到八段 |
| [第 8 章](chapters/chap08.md) | 从文献到论文：研究设计与 Stata 计划 |

</div>

---

## 关于示例材料

本书在介绍 EmpiricalWiki 的具体环节时，会以一个真实的实证研究项目作为示意材料，主题为耐心资本，由若干篇中文核心期刊论文构成。**研究主题在本书中处于辅助位置**，读者无需具备相关背景，将其视为一个抽象的研究构念即可。涉及该主题的特定术语（如 A1 测算、双元创新、Sasabuchi 检验等）将以脚注形式给出简短定义。

读者将本书内容应用于自身研究方向时，把"耐心资本"替换为自己的核心构念，把该构念的多种测算口径替换为相应文献中的不同操作化方式即可。EmpiricalWiki 的处理流程对具体研究主题不敏感，适用于具有"多种测算变体 + 多类识别策略 + 多种稳健性检验"的实证研究。

---

## 致谢

- **[Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)** —— 提出 LLM-Wiki 模式，确立了三层架构（raw / wiki / schema）与三个核心操作（ingest / query / lint）的概念框架。本书全部讨论建立于该模式之上。
- **[ΩmegaWiki](https://github.com/skyllwt/OmegaWiki)（PKU [DAIR Lab](https://cuibinpku.github.io/)）** —— EmpiricalWiki 在 ΩmegaWiki 的基础上做经管实证特化。三层架构、双向链接与若干通用 skill 均来自上游。
- **[Claude Code](https://docs.anthropic.com/en/docs/claude-code)** —— EmpiricalWiki 项目所基于的 AI 编辑器。

---

## License

[MIT](LICENSE)
