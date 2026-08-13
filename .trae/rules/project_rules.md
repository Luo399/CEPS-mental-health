# 项目规则：别人家的父母，别人的阴影

## 项目简介
班级同学父母教育水平对青少年心理健康的非对称溢出效应 — 基于CEPS的因果识别。
与殷戈等(2020)《人力资本代际外溢性》直接对话。

---

## 可用 Skills 清单

### 数据分析与统计
| Skill | 用途 | 使用阶段 |
|-------|------|----------|
| `research-data-analysis-workspace` | 科研数据分析全流程（清洗、统计、建模） | 全阶段 |
| `statistical-analysis` | 统计分析（假设检验、效应量、报告标准） | 阶段二 |
| `statsmodels` | 回归分析（OLS、Logit、GLM、时间序列） | 阶段二 |
| `matplotlib` | 数据可视化图表生成 | 阶段二 |
| `seaborn` | 统计图形（分布图、热力图、箱线图） | 阶段二 |

### 文献与写作
| Skill | 用途 | 使用阶段 |
|-------|------|----------|
| `zotero` | 文献管理、BibTeX导出、引用插入 | 阶段四 |
| `literature-review` | 文献综述辅助 | 阶段四 |
| `empirical-paper-writer` | 实证论文正文写作 | 阶段四 |
| `paper-writer` | 证据门控正文写作 | 阶段四 |
| `paper-polish` | 语言润色、去AI腔 | 阶段四 |
| `pre-submission-reviewer` | 投稿前审查 | 阶段四 |

### 研究辅助
| Skill | 用途 | 使用阶段 |
|-------|------|----------|
| `deep-research` | 文献深度调研 | 阶段四 |
| `idea-evaluator` | 研究想法5维评估 | 阶段二前 |
| `figure-designer` | 科研作图建议 | 阶段四 |
| `peer-review` | 同行评审模拟 | 阶段四 |

### 版本控制
| Skill | 用途 | 使用阶段 |
|-------|------|----------|
| `github` | GitHub仓库管理、PR、Issue | 全阶段 |
| `gh-cli` | GitHub CLI操作 | 全阶段 |

---

## 数据处理规则

### 1. 数据安全
- **永不修改原始数据**：CEPS完整版和清洗后数据为只读
- 所有转换在内存中完成，输出到 `data/` 目录
- 中间数据可删除重建，原始数据不可逆

### 2. 目录约定
```
别人家的父母/
├── CEPS/                    # 原始数据（只读）
│   ├── 2013-2014/           # Wave1完整版
│   └── 2014-2015/           # Wave2完整版
├── 教育减负--代码与数据/     # 原始清洗数据（只读）
│   ├── datafile/            # final_ceps_all1123.dta
│   └── dofile/              # Stata脚本
├── data/                    # Python分析输出（可删除）
├── scripts/                 # Python分析脚本
├── tablefile/               # 回归结果表（CSV格式）
├── figurefile/              # 可视化图表（PNG格式）
└── skills/                  # 技能包（只读）
```

### 3. 脚本规范
- 依赖声明：脚本开头注明输入/输出路径
- 路径配置：统一使用 `os.path` 相对路径，不硬编码绝对路径
- 日志输出：每一步打印关键统计信息
- 异常处理：非关键步骤（如可视化）用 try-except 包裹
- 编码标准：输入输出统一 UTF-8

### 4. 变量命名规范
- 数字变量：直接使用原始值，不转为分类变量
- 构造变量：`raw` 后缀表示原始加总，`z` 后缀表示标准化
- 交互项：使用 `_x_` 分隔（如 `cls_mean_edu_x_ses_low`）
- 中间变量：使用 `_inv` 后缀表示反转编码

### 5. 代码规范
- 2空格缩进，小驼峰命名（变量/函数），大驼峰命名（类）
- 全大写命名（常量，如 `BASE_DIR`）
- 关键逻辑添加中文注释
- 函数超过20行需拆分，遵循DRY原则
- 禁止使用 `eval`、`with` 等危险写法
- 代码需可直接运行，不保留TODO

### 6. 分析流程
```
01_merge_mental_health.py     # 合并情绪题 → data/analysis_data.dta
02_construct_variables.py     # 构造变量 → data/analysis_final.dta
03_descriptive_stats.py       # 描述性统计 → tablefile/ + figurefile/
04_baseline_ols.py            # 基准回归 → tablefile/ + figurefile/
```

### 7. Git 提交规范
- 每次提交对应一个完整的功能模块
- 提交信息：`[阶段] 具体内容`（如 `[数据准备] 合并情绪题到清洗数据`）
- 不提交原始数据（已在 .gitignore 中排除 *.dta）