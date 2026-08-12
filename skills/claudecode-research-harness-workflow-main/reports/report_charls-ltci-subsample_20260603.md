# 任务完成报告：CHARLS LTCI 复现子样本提取

**任务日期**：2026-06-03  
**执行脚本**：charls_10 / charls_11 / charls_12  
**目标论文**：Zhang et al. (2026) "The effect of long-term care insurance on labor force participation among informal caregivers: evidence from China"

---

## 任务背景

用户希望复现上述论文，需要从 CHARLS 原始数据中提取与论文完全对应的子样本，并生成 codebook，以便直接用于回归分析。

论文使用 CHARLS 2011、2013、2018 三波数据（共 32,238 人次），通过照护筛选后得到非正式照护者样本 N=4,626。采用交错双重差分（Staggered DID）方法估计 LTCI 政策对照护者劳动力参与的效应。

---

## 执行过程

### 第一步：变量发现（charls_10_discover_vars.py）

- 读取 2011/2013/2018 三波共 9 个模块的 Stata 变量标签（metadataonly=True）
- 扫描关键词（照护、就业、人口统计、健康等），标记相关变量
- 输出：`data/intermediate/charls_10_var_list.csv`（15,827 条变量-标签对）
- 日志：`logs/charls_10_vars.log`

关键发现：
- **照护筛选变量**：2011/2013 的 `CF004`（"Take Care of Your Parents/Parents-in-Law"）；2018 变为人头级 `CF004_W4_1_` 至 `CF004_W4_8_`
- **城市标识**：PSU 文件含 `CITY` 字段（中文城市名字符串），可直接匹配 LTCI 试点城市
- **就业变量**：农业雇佣劳动 = FC001（不是 FA001，FA001 包含自家农业劳动）；非农就业 = FC014（2011/2013）/ FA002_W4（2018）

### 第二步：子样本提取（charls_11_ltci_subsample.py）

加载 7 个模块（Demographic_Background、Family_Transfer、Work_Retirement、Health_Status_and_Functioning、Health_Care_and_Insurance、Household_Income、PSU），执行以下操作：

1. 从 PSU 文件构建 450 个社区到城市名的映射，匹配 12 个 LTCI 试点城市
2. 按波次加载数据，构造 29 个分析变量
3. 筛选照护者（CF004==1 或任意 CF004_W4_N_==1）：56,126 → 4,665
4. 赋值 TREAT/POST/TREAT_X_POST
5. 保存至 `data/intermediate/charls_ltci_subsample.parquet` + CSV

### 第三步：Codebook 生成（charls_12_subsample_codebook.py）

- 读取子样本，计算每个变量的统计摘要
- 加入论文 Table 1 的变量定义和 Table 2 均值对比
- 保存至 `data/processed/charls_ltci_codebook.csv`

---

## 关键结果

所有数值来源于脚本日志，不得估算。

### 样本规模（来自 logs/charls_11_subsample.log）

| 指标 | 本次提取 | 论文目标 |
|------|---------|---------|
| 照护者总观测数 | **4,665** | 4,626 |
| 处理组（LTCI 试点城市） | **358** | 357 |
| 对照组 | **4,307** | 4,269 |
| Post=1（政策实施后） | **189** | — |
| Treat×Post=1 | **189** | — |

波次构成：2011年=1,315 obs / 2013年=1,083 obs / 2018年=2,267 obs

### 变量均值对比（来自 logs/charls_12_codebook.log）

| 变量 | 本次 | 论文 Table 2 | 吻合度 |
|------|------|------------|-------|
| AGE | 53.43 | 53.67 | 接近 |
| HUKOU（城镇=1） | 0.303（N=2,397） | 0.290 | 接近 |
| GENDER（男=1） | 0.473（N=3,582） | 0.450 | 较接近 |
| N_CHRONIC | 0.789 | 0.838 | 较接近 |
| MARITAL（已婚=0，其他=1） | 0.174 | 0.074 | 偏差 |
| EDUCATION（初中及以上=1） | 0.614 | 0.534 | 较接近 |
| AGRI_EMPLOY | 0.027 | 0.075 | 方向正确，数值偏低 |
| NON_AGRI_EMPLOY | 0.283 | 0.462 | 偏差（见下） |
| HEALTH_INSURED | 0.485 | 0.965 | 偏差（见下） |

---

## 数据质量说明

### 变量缺失情况

| 变量 | 缺失率 | 原因 |
|------|--------|------|
| GENDER | 23.2% | 2013波次的 Demographic_Background 不含性别变量；需从2011基线补充（但2011/2013 ID格式不同，11位 vs 12位，无法直接匹配） |
| HUKOU | 48.6% | 2018波次 Demographic 仅含户籍变更二值指标，非户籍类型 |
| HEALTH_SELF | 26.7% | 2018年使用 DA002，2011/2013 使用 6-DA001 重编码 |
| CARE_INTENSITY | 48.0% | 2018波次照护变量变为人头级索引，加总逻辑需验证 |
| LN_HH_INCOME | 84.6% | 仅使用工资收入（GA006_1_N_ / GA006_W4_N_），未包含农业收入和转移支付 |
| DEPRESSION_CESD | 51.5% | 2018波次 Health_Status 无 CES-D（DC009-DC018）项目 |

### 已知构造偏差及处置建议

1. **NON_AGRI_EMPLOY（0.283 vs 0.462）**：当前使用 FC014（非农就业，上周），可能仅覆盖已回答该题的人。建议同时尝试 FA002（2011/2013：上月一般工作）OR FA003，再减去农业就业者，验证哪种构造更接近论文。

2. **HEALTH_INSURED（0.485 vs 0.965）**：CHARLS 医疗保险为多选题，变量值等于编号（EA001S3={3} 表示有农村合作医保）。当前已改用 `.notna().any()` 检测，但仍仅为 48.5%。疑因：① 部分波次回答者为家庭代表而非个人；② 2018 年保险变量名 EA001_W4_S1 至 S12，需验证是否全部纳入。

3. **MARITAL（0.174 vs 0.074）**：论文"已婚=0，其他=1"可能定义 BE001 in {1,2} 为已婚（含分居在外），而本次仅 BE001==1。建议将 BE001==2 也归入已婚（改为 be001 > 2 才为"其他"）。

4. **AGRI_EMPLOY（0.027 vs 0.075）**：已正确使用 FC001（雇佣农业劳动），但 2018 年 FC001 覆盖率可能低于 2011/2013。

---

## 输出文件清单

| 文件 | 路径 | 行数 | 列数 |
|------|------|------|------|
| 子样本（Parquet） | `data/intermediate/charls_ltci_subsample.parquet` | 4,665 | 29 |
| 子样本（CSV） | `data/intermediate/charls_ltci_subsample.csv` | 4,665 | 29 |
| Codebook | `data/processed/charls_ltci_codebook.csv` | 29（变量数） | 17（字段数） |
| 变量元数据 | `data/intermediate/charls_10_var_list.csv` | 15,827 | 6 |

---

## 证据链

| 数字来源 | 脚本 | 日志 |
|---------|------|------|
| 4,665 照护者行数 | `scripts/charls_11_ltci_subsample.py` | `logs/charls_11_subsample.log` |
| 358 处理组 / 4,307 对照组 | `scripts/charls_11_ltci_subsample.py` | `logs/charls_11_subsample.log` |
| 变量均值（29 列） | `scripts/charls_12_subsample_codebook.py` | `logs/charls_12_codebook.log` |
| PSU 450 社区城市映射 | `scripts/charls_11_ltci_subsample.py` | `logs/charls_11_subsample.log` |

---

## 待办/遗留问题

1. **NON_AGRI_EMPLOY 重构**：尝试 FA002 OR FA003（直接工作询问）替代 FC014，验证是否更接近 46.2%。如两种构造差异大，需阅读 CHARLS 2011/2013 问卷以确认问题路由。

2. **HEALTH_INSURED 修复**：检查 2018 年保险变量 EA001_W4_S1—S12 是否均正确加入合并；验证医保在 CHARLS 是否按个人还是家庭询问。

3. **GENDER 填充（2013）**：CHARLS 2011 与 2013 的个人 ID 格式不同（11位 vs 12位），无法直接匹配。可尝试通过 HOUSEHOLDID + 在户序号匹配，或从 CHARLS 官方纵向追踪文件获取跨波 ID 对照表。

4. **HUKOU 填充（2018）**：使用 2011/2013 的户籍类型为 2018 同一个体赋值（若有 ID 对照表），或使用 PSU 社区城乡分类（URBAN_NBS）作为替代。

5. **LN_HH_INCOME 完善**：当前仅用工资收入，需加入农业收入（gb001/gb005）、经营收入、转移收入等，才能接近论文的家庭净收入。

6. **MARITAL 编码验证**：将 BE001 in {1,2} 定为"已婚"（含配偶在外）重新检验。
