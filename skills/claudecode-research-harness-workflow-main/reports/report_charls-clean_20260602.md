# CHARLS 数据清理合并任务报告

**任务编号：** charls-clean  
**报告日期：** 2026-06-02  
**执行者：** Claude Code

---

## 任务背景

用户将 CHARLS（中国健康与养老追踪调查）原始数据存放于 `input/data/CHARLS_raw/`，包含：

- **5 个主面板波次**：2011、2013、2015、2018、2020，每波 10–18 个 `.dta` 模块文件
- **1 个独立专项调查**：2014 年生命历史调查（Life History Survey），7 个回顾性模块
- **2 个参考用预处理文件**：Harmonized CHARLS C/D（未纳入管线，仅审计备注）

任务目标：按照 CLAUDE.md 规范，从原始 `.dta` 文件构建长格式个人级面板数据（ID × wave），生成合并 CSV、Codebook 及数据质量报告。

---

## 执行过程

### 环境说明

Python 可执行文件：`C:\Users\zhuch\.conda\envs\gnn\python.exe`（Python 3.10.18）  
已安装包：pandas 2.3.3、pyreadstat 1.3.5、pyarrow 24.0.0

> 注：原 `snipar_env` 环境的 `python.exe` 丢失（conda 更新中断），本次改用 `gnn` 环境并通过 pip 补装 pyreadstat、pyarrow 和 pandas。

### 脚本执行顺序

| 脚本 | 功能 | 运行时间 | 状态 |
|------|------|---------|------|
| `charls_00_scaffold.py` | 创建目录、初始化合并报告 | <1 min | ✓ SUCCESS |
| `charls_01_audit.py` | 审计所有 .dta 文件行列数及 ID 列 | ~2 min | ✓ SUCCESS |
| `charls_02_spine.py` | 从 Demographic_Background 构建 ID×wave 脊柱 | ~1 min | ✓ SUCCESS |
| `charls_03_individual.py` | 合并个人级模块（HSF、HCI、INC、WRP、OBS、WGT） | ~22 min | ✓ SUCCESS |
| `charls_04_household.py` | 合并家户级模块（HHInc、Housing、FamInfo、FamTfr） | ~27 min | ✓ SUCCESS |
| `charls_05_supplement.py` | 合并波次专属模块（生物标志物、血液、认知等） | ~2 min | ✓ SUCCESS |
| `charls_06_export.py` | 导出主面板 CSV 及 Codebook | ~64 min | ✓ SUCCESS |
| `charls_07_life_history.py` | 2014 生命历史单独建表并导出 | ~4 min | ✓ SUCCESS |

### 关键处理决策

1. **混合类型列清理**：CHARLS .dta 文件在跨波拼接时产生 bytes+float 混合类型（如 BD014 列：2015 波空字符串、2018 波浮点数）。解决方案：在 `write_parquet` 前对全列运行 `clean_dtypes()`，空字符串列统一强转为数值型，含义义字符串的列转为 str 类型。
2. **内存优化**：合并后面板宽度达 19,222 列，do_merge 函数的指示连接（indicator join）改为仅使用 key 列，避免 11 GB 内存溢出。
3. **重复列清理**：个人模块合并时，HOUSEHOLDID_right / COMMUNITYID_right 重复列在写入 parquet 前通过 `df.loc[:, ~df.columns.duplicated()]` 清除（共 10 列）。
4. **脚本 05 轻量化**：supplement 合并仅载入 4 列 key frame（ID、WAVE、HOUSEHOLDID、COMMUNITYID），避免 19,222 列面板二次复制引发 OOM。

---

## 关键结果

> 以下所有数字均来自日志文件，不含估算。

### 主面板（charls_merged_panel.csv）

| 指标 | 数值 | 来源日志 |
|------|------|---------|
| 总行数 | 96,616 | charls_06_export.log |
| 总列数 | 20,879 | charls_06_export.log |
| 独立个体数 | 42,455 | charls_06_export.log |
| 独立家户数 | 24,181 | charls_06_export.log |
| 整体缺失率 | 95.50% | charls_06_export.log |

**波次行数分布**（来源：charls_06_export.log）

| 波次 | 行数 | 个体数（来源：charls_02_spine.log） | 家户数 |
|------|------|------|------|
| 2011 | 17,705 | 17,705 | 10,251 |
| 2013 | 18,605 | 18,605 | 10,822 |
| 2015 | 21,095 | 21,095 | 12,235 |
| 2018 | 19,816 | 19,816 | 11,635 |
| 2020 | 19,395 | 19,395 | 11,412 |

**Codebook（charls_codebook.csv）**：20,879 行（变量数与面板列数一致，校验通过）

### 生命历史面板（charls_life_history_panel.csv）

| 指标 | 数值 | 来源日志 |
|------|------|---------|
| 总行数 | 20,543 | charls_07_life_history.log |
| 总列数 | 6,960 | charls_07_life_history.log |
| 独立个体数 | 20,543 | charls_07_life_history.log |
| 整体缺失率 | 94.97% | charls_07_life_history.log |

**Codebook（charls_life_history_codebook.csv）**：6,960 行

### 各步骤行数守恒验证

| 阶段 | 行数 | 状态 |
|------|------|------|
| 脊柱（5 波拼接） | 96,616 | 等于 5 波 Demographic_Background 行数之和（17705+18605+21095+19816+19395）|
| 个人模块合并后 | 96,616 | 无变化 |
| 家户模块合并后 | 96,616 | 无变化 |
| Supplement 合并后 | 96,616 | 无变化 |
| 最终导出 | 96,616 | 无变化 |

---

## 数据质量说明

### 缺失率说明

主面板缺失率 95.50%，属正常现象：
- 很多模块只覆盖部分波次（如 Biomarker 仅 2011/2013/2015，认知模块仅 2018）
- 长格式面板中非该波次的模块列全为空
- 家户模块按 HOUSEHOLDID 合并，同一家户不同成员共享值（家户级变量仅对主访谈员非空）

### 已知数据问题

1. **Exit 数据匹配失败（2013 波）**：`EXIT_INTERVIEWED_W2013` 列全为 NaN（0 行匹配）。原因：exit interview 受访者为已故者，不在 2013 Demographic_Background 中。2020 波 Exit_Module 匹配 1,961 行（正常，部分已故者仍在 2020 脊柱中）。
2. **BD014 等混合类型列**：2015 波为空字符串（Stata missing），2018 波为浮点数。已在 clean_dtypes 中统一处理为数值型。
3. **2013 Weights.dta**：13 行 null-ID 行已在个人模块合并前过滤。

### 跳过文件清单

| 文件 | 原因 |
|------|------|
| `Harmonized_CHARLS_C/H_CHARLS_C_Data.dta` | 仅供参考，未纳入原始波次管线 |
| `Harmonized_CHARLS_D/H_CHARLS_D_Data.dta` | 同上 |
| `2013/Other_HHmember.dta` | 无 wave 级聚合意义，暂不纳入 |
| `2015/Spousal_Sibling.dta` | 未纳入（计划外） |

---

## 输出文件清单

| 文件路径 | 行数 | 列数 | 来源日志 |
|---------|------|------|---------|
| `data/processed/charls_merged_panel.csv` | 96,616 | 20,879 | charls_06_export.log |
| `data/processed/charls_codebook.csv` | 20,879 | 9 | charls_06_export.log |
| `data/processed/charls_life_history_panel.csv` | 20,543 | 6,960 | charls_07_life_history.log |
| `data/processed/charls_life_history_codebook.csv` | 6,960 | 9 | charls_07_life_history.log |
| `reports/charls_audit_report.md` | — | — | charls_01_audit.log |
| `reports/charls_merge_report.md` | — | — | 各合并步骤追加 |

---

## 证据链

| 关键数字 | 脚本路径 | 日志路径 |
|---------|---------|---------|
| 主面板 96,616 行 × 20,879 列 | `scripts/charls_06_export.py` | `logs/charls_06_export.log` |
| 脊柱行数 = 各波 Demo 之和 (96,616) | `scripts/charls_02_spine.py` | `logs/charls_02_spine.log` |
| 独立个体 42,455 | `scripts/charls_06_export.py` | `logs/charls_06_export.log` |
| LH 面板 20,543 行 × 6,960 列 | `scripts/charls_07_life_history.py` | `logs/charls_07_life_history.log` |
| 缺失率 95.50% | `scripts/charls_06_export.py` | `logs/charls_06_export.log` |

---

## 待办／遗留问题

1. **Exit 数据关联**：应将 exit interview 的 ID 关联到受访者最后一次在世波次（而非 exit 发生波次），目前该指示列无效。
2. **Other_HHmember（2013）、Spousal_Sibling（2015）**：两个子模块未纳入，若研究需要可补充。
3. **Python 环境修复**：`snipar_env` 中 `python.exe` 丢失，需重装 conda 环境方可恢复（建议 `conda install python=3.9 -n snipar_env`）。
4. **超宽 CSV 的后续使用**：主面板 20,879 列对 Stata/R 加载有挑战，建议研究者按需从 codebook 中筛选所需变量子集后再导入。
