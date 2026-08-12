# 别人家的父母，别人的阴影

> **班级同学父母教育水平对青少年心理健康的非对称溢出效应——基于CEPS的因果识别**

---

## 项目概述

本文与殷戈等(2020)《人力资本代际外溢性——来自"别人家的父母"的证据》（《经济学（季刊）》）进行直接对话：

- **殷戈问**：别人家的父母对孩子**发展性结果**（成绩、认知、非认知能力）的影响 → 答案是"正面的"（涓滴效应）
- **本研究问**：别人家的父母对孩子**心理健康**的影响 → 答案可能是**"非对称的"**

**核心假设**：
- 对低SES学生：相对剥夺效应（心理健康恶化）
- 对高SES学生：榜样效应（心理健康改善或无显著影响）
- 净效应：加剧心理健康不平等

## 数据

- **CEPS 2013-2014（基线）**：七年级/九年级学生，19,487人
- **CEPS 2014-2015（追踪）**：八年级/十年级学生，10,750人
- **已有清洗数据**：`final_ceps_all1123.dta`（30,708行×240变量，两期堆叠）

## 工作目录结构

```
别人家的父母/
├── README.md                 # 本项目说明
├── WORK_PLAN.md              # 完整工作清单
├── .gitignore                # Git忽略规则
├── 别人家的父母别人的阴影.html   # 论文框架与完整研究设计
│
├── 教育减负--代码与数据/       # ⭐ 核心工作目录
│   ├── dofile/               # Stata脚本（数据合并→清洗→回归）
│   ├── datafile/             # 最终清洗数据
│   ├── rawfile/              # 原始数据（删减版）
│   ├── tempfile/             # 中间数据
│   ├── tablefile/            # 回归结果表格（18张）
│   ├── figurefile/           # 图形
│   └── logfile/              # 运行日志
│
├── CEPS/                     # 完整版CEPS原始数据（含情绪题）
│   ├── 2013-2014/            # 基线完整版（300变量）
│   └── 2014-2015/            # 追踪完整版（311变量）
│
├── scripts/                  # Python分析脚本（待创建）
│   ├── 01_construct_mental_health.py
│   ├── 02_construct_ses.py
│   ├── 03_construct_mediators.py
│   ├── 04_descriptive_stats.py
│   ├── 05_baseline_ols.py
│   ├── 06_asymmetric_effects.py
│   ├── 07_did_analysis.py
│   ├── 08_iv_analysis.py
│   ├── 09_mechanism_tests.py
│   └── 10_robustness_checks.py
│
└── skills/                   # 研究辅助技能包
    └── Supervisor-Skills-main/  # Supervisor-Skills（12个技能）
```

## 研究方法

### 识别策略（四步递进）

1. **截面OLS**（与殷戈2020保持可比）
   `MentalHealth = α + β₁·PeerParentalEdu + γ·X + δ_school + ε`

2. **非对称效应检验**（交互项）
   `MH = α + β₁·PeerEdu + β₂·SES + β₃·PeerEdu×SES + γ·X + δ_school + ε`

3. **双重差分（DID）**
   `MH_it = α + β₁·Treat_i×Post_t + β₂·Post_t + μ_i + ε_it`

4. **工具变量（IV）**
   IV: 同校其他年级同学父母教育水平

### 核心变量

| 变量类型 | 变量 | 数据来源 |
|---|---|---|
| 核心自变量 | 班级同学父母教育水平均值 | `cls_mean_max_education`（已构造） |
| 因变量 | 心理健康指数（基线a18/追踪w2c25） | 从完整版CEPS合并 |
| 调节变量 | 家庭SES综合指数 | 需构造（父母教育+经济条件） |
| 中介变量 | 学业压力（b32/w2a29） | 从完整版CEPS提取 |
| 中介变量 | 教养方式（b22-b24/w2a18-a21） | 需自行构造 |

## Supervisor-Skills 安装确认

项目来自 [HKUSTDial/Supervisor-Skills](https://github.com/HKUSTDial/Supervisor-Skills)，已下载至 `skills/Supervisor-Skills-main/`。

包含 **12个可用技能** 和 **6章handbook指南**：

| 技能 | 阶段用途 |
|---|---|
| `deep-research` | 文献深度调研 |
| `idea-evaluator` | 研究Idea评估 |
| `intro-drafter` | 引言写作 |
| `paper-writer` | 证据门控正文写作 |
| `paper-polish` | 语言润色 |
| `pre-submission-reviewer` | 投稿前审查 |
| `figure-designer` | 科研作图建议 |
| `drawio-reconstruction` | 参考图→drawio重建 |

## 复现流程

```
数据准备 → 变量构造 → 描述性统计 → 基准回归 → 非对称效应 → DID → IV → 机制检验 → 稳健性 → 论文写作
```

所有代码和脚本将上传至GitHub公开仓库，供审稿人核查。

## 授权

本项目代码部分采用 MIT 协议。