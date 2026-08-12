# 第 8 章 · 从文献到论文：研究设计与 Stata 计划

**本章你会读到**

- `/empirical-design` 是怎么把"一句研究问题"变成"一份完整研究设计"的
- 这份研究设计里每一项的依据是什么、为什么这样做
- `/stata-plan` 怎么把研究设计转成可执行的 Stata 代码骨架
- 这两个 skill 串起来后，研究者还需要做什么

---

## 8.1 一句研究问题，一份研究设计

读完文献之后，研究者面对的下一个问题是——**轮到我自己做研究了，我怎么把读过的东西变成自己的研究设计**？

传统流程是这样的：研究者在脑子里酝酿研究问题，反复想几周，逐渐形成大致的研究设计；查阅文献确认没人做过；写一份开题报告；跑数据，调整设计；写论文。这个过程从想到第一个 idea 到能动手跑数据，通常需要几周。

EmpiricalWiki 在这个流程里加了一个工具——`/empirical-design`。它的输入是一句研究问题，输出是一份完整的研究设计提案。**输入到输出之间花的时间是几分钟，不是几周**。

具体怎么用？打开 Claude Code，输入：

```bash
> /empirical-design "耐心资本对企业 ESG 表现的影响"
```

模型会读取整个 wiki 当前的状态，基于已有变量、模型、识别策略、数据集，生成一份针对这个问题的研究设计提案。

## 8.2 研究设计提案里有什么

`/empirical-design` 输出的内容大致包括以下几块：

**第一块：研究问题的精细化**

模型会把研究者输入的"一句话"问题展开成更精细的形态——明确自变量、因变量、中介或调节变量、潜在的内生性来源。

```markdown
## 研究问题

核心问题：耐心资本（PC）是否对企业 ESG 综合表现（ESG）有显著的正向影响？

子问题：
1. 这种影响是否存在异质性（按所有制、按行业、按地区）？
2. 这种影响通过哪些机制（融资约束缓解？管理者短视抑制？战略稳定性？）？
3. 这种影响是否存在非线性（U 型、倒 U 型、阈值效应）？

潜在内生性来源：
- 反向因果：好的 ESG 表现可能吸引耐心资本
- 遗漏变量：公司治理质量同时影响 PC 和 ESG
- 测量误差：PC 的不同测算口径可能给出不同结论
```

这里每一条都不是凭空写的——子问题来自 wiki 里已有的耐心资本论文中提及的研究方向，潜在内生性来源来自 `identification/` 目录里累积的常见识别问题。

**第二块：变量设计**

```markdown
## 变量设计

自变量（Patient Capital）：建议同时使用三种测算口径
- A1 经典换手率三分组法（参考 [[paper-X1]]、[[paper-X2]]）
- B1 持股时长法（参考 [[he-wenbin-2025]]）
- C 综合指标 PCA 法（参考 [[paper-U1]]）
理由：跨变体一致性是稳健性的重要支撑，单一变体的结论容易被推翻。

因变量（ESG）：
- 主测算：华证 ESG 综合评级（[[datasets/huazheng-esg]]）
- 稳健性：商道融绿 / Wind / MSCI 三种第三方评级（[[datasets/sino-securities]]、[[datasets/wind-esg]]、[[datasets/msci-esg]]）

控制变量：参考 [[paper-V]] 的标准控制变量集
- 公司规模、杠杆率、ROA、年龄、上市板块、产权性质、行业、年份固定效应
```

每个变量后面都挂着 wikilink——研究者可以直接跳转到来源页面看具体测算公式和文献依据。

**第三块：模型设定**

```markdown
## 模型设定

主回归：双向固定效应模型
ESG_{i,t} = α + β·PC_{i,t-1} + γ·X_{i,t} + μ_i + ν_t + ε_{i,t}

具体设定参考 [[models/twoway-fixed-effects]]：
- 公司固定效应 μ_i 控制时间不变的企业层面异质性
- 年份固定效应 ν_t 控制宏观经济波动
- 标准误聚类到公司层面
- PC 滞后一期，缓解反向因果

非线性扩展：在主回归基础上加 PC 二次项
ESG_{i,t} = α + β1·PC_{i,t-1} + β2·PC²_{i,t-1} + γ·X_{i,t} + μ_i + ν_t + ε_{i,t}
后续用 [[robustness/sasabuchi-u-shape]] 验证 U 型关系是否真的成立
```

**第四块：识别策略**

```markdown
## 识别策略

主策略：双向固定效应 + 滞后自变量（[[identification/firm-fixed-effects]]）

辅助策略：
- 工具变量（[[identification/instrumental-variable]]）：考虑用同行业平均 PC 作为工具
- 倾向得分匹配（[[identification/psm]]）：按公司特征匹配高 PC 与低 PC 公司
- 双重差分（[[identification/diff-in-diff]]）：利用某个 PC 政策冲击作为外生变化
```

**第五块：稳健性 + 异质性**

```markdown
## 稳健性检验
- 替换 PC 测算（A1 ↔ B1 ↔ C）
- 替换 ESG 测算（华证 ↔ 商道融绿 ↔ Wind）
- 子样本检验（剔除金融行业、剔除 ST 公司）
- Sasabuchi U 型检验（[[robustness/sasabuchi-u-shape]]）
- 安慰剂检验（[[robustness/placebo]]）

## 异质性分析
- 按产权性质（国企 vs 非国企，参考 [[heterogeneity/state-ownership-split]]）
- 按行业（重污染 vs 非重污染）
- 按地区（东部 vs 中西部）
- 按公司规模
```

**第六块：数据缺口**

这一块是 `/empirical-design` 比较有意思的特性——它会主动指出**当前 wiki 里缺的东西**。

```markdown
## 数据缺口（需要研究者补齐）

⚠ 当前 wiki 中尚未涵盖的内容：
1. ESG 评级数据：仅有华证 ESG 已建数据集页面，商道融绿/Wind/MSCI 还需补 dataset 卡片
2. 重污染行业分类：[[heterogeneity/state-ownership-split]] 已有，但行业污染分类需要建立新的 heterogeneity 页面
3. 工具变量的有效性：使用同行业平均 PC 作为工具是常见做法，但 wiki 中尚无关于这个具体工具变量的详细页面（包括其外生性论证、实际估计中的弱工具问题等）

建议：
- 先用 /edit 命令补齐 dataset 卡片
- 然后用 /ingest 摄入若干篇用了上述方法的论文
- 然后回来重新跑 /empirical-design 得到更完整的提案
```

这一块的存在让研究设计**自带可验证性**——研究者一眼能看出哪些设计还缺论文支撑、哪些数据集需要补齐，把"看似完整其实纸糊"的设计漏洞暴露出来。

## 8.3 研究设计完成后的下一步：Stata 计划

研究设计有了，下一步是把它变成可以跑的代码。这一步用 `/stata-plan`：

```bash
> /stata-plan
```

模型读取上一步生成的研究设计提案，输出一份 Stata `.do` 文件骨架：

```stata
*=================================================================
* 研究：耐心资本对企业 ESG 表现的影响
* 主作者：[研究者名]
* 日期：2026-04-15
*=================================================================

* ---------- 1. 数据准备 ----------
use "raw_data/csmar_listed_companies.dta", clear
* 合并 PC 测算（A1 经典版）
merge 1:1 stkcd year using "raw_data/patient_capital_a1.dta"
keep if _merge == 3
drop _merge

* 合并 ESG 评级
merge 1:1 stkcd year using "raw_data/huazheng_esg.dta"
keep if _merge == 3
drop _merge

* 合并控制变量
merge 1:1 stkcd year using "raw_data/control_variables.dta"
keep if _merge == 3
drop _merge

* ---------- 2. 变量构造 ----------
* 滞后处理
xtset stkcd year
gen pc_lag1 = L.pc_a1

* 缩尾处理（按年-行业 1% 双侧缩尾）
foreach v in pc_a1 pc_lag1 esg_huazheng size lev roa age {
    winsor2 `v', cuts(1 99) replace by(year industry)
}

* ---------- 3. 描述性统计 ----------
summarize esg_huazheng pc_lag1 size lev roa age
* 把结果导出到 Table 1
estout, cells("mean(fmt(3)) sd(fmt(3)) min(fmt(2)) max(fmt(2))") ///
    label varlabels(`e(labels)') style(tex) ///
    using "tables/table1_summary.tex"

* ---------- 4. 主回归 ----------
* 模型 1：基准
reghdfe esg_huazheng pc_lag1 size lev roa age, ///
    absorb(stkcd year) cluster(stkcd)
estimates store m1

* 模型 2：加非线性项
gen pc_lag1_sq = pc_lag1 * pc_lag1
reghdfe esg_huazheng pc_lag1 pc_lag1_sq size lev roa age, ///
    absorb(stkcd year) cluster(stkcd)
estimates store m2

* 模型 3：仅大公司子样本（稳健性）
reghdfe esg_huazheng pc_lag1 size lev roa age if size > r(p50), ///
    absorb(stkcd year) cluster(stkcd)
estimates store m3

* ---------- 5. Sasabuchi U 型检验 ----------
* 用模型 2 的结果做 utest
utest pc_lag1 pc_lag1_sq

* ---------- 6. 输出回归表 ----------
estout m1 m2 m3 using "tables/table2_main_regression.tex", ///
    cells(b(star fmt(3)) se(par fmt(3))) stats(N r2_a) ///
    label collabels("基准" "U型扩展" "大公司子样本") style(tex)
```

这份 `.do` 文件骨架不是最终的——它**只是开始**。研究者需要：

1. 把它跑通（在 Stata 里能编译运行）
2. 接入自己的实际数据（PC 测算可能需要研究者自己计算）
3. 根据初步结果调整模型设定
4. 加上更多稳健性检验

但这个起点比"从空白文件开始"快得多。所有标准操作（数据合并、缩尾处理、双向 FE、聚类标准误、回归表输出）都已经写好了。研究者把精力放在**自己研究的特殊部分**——独特变量怎么构造、特定稳健性怎么做。

> [!TIP]
> **Stata 不是 EmpiricalWiki 的唯一支持**
>
> `/stata-plan` 当前主要支持 Stata，因为这是中文经管实证研究最主流的工具。但研究设计这一层是工具无关的——研究者完全可以拿同一份 `/empirical-design` 输出的研究设计，让模型按 R / Python pandas / Julia 的语法生成代码骨架。这只需要在 schema 里加一条规则。

## 8.4 这两个 skill 串起来意味着什么

`/empirical-design` 和 `/stata-plan` 串起来构成了一座桥——**从"读完文献"到"能跑数据"的桥**。

之前需要几周时间走过的桥，现在压缩到几小时。研究者还是要做核心判断（研究问题对不对、设计是否真的可行、模型设定是否合理），但所有"机械性的整理工作"——把文献里学到的方法变成自己研究设计里的一段、把研究设计变成 Stata 代码——都被加速了。

这种加速不是"AI 替你做研究"。这种加速是**让研究者把时间花在更值得思考的事情上**。机械性整理被压缩了，腾出来的时间可以用来反复推敲研究问题、跟同行讨论设计、看更多最新文献——也就是真正决定一项研究质量高低的事情。

<div align="center">
  <img src="../assets/chap08/08_design_to_stata.gif" alt="empirical-design 到 stata-plan 的工作流" width="640" />
</div>

## 8.5 设计提案不是定论

最后强调一个边界——**`/empirical-design` 输出的研究设计提案不是"标准答案"**。

它是基于当前 wiki 里已有内容做出的一份合理建议。它给出的变量、模型、识别策略都是文献里已经被采用过的成熟做法。**但它不能替研究者判断"这个研究值不值得做、做出来有没有意思"**。

研究者拿到提案后要做的事情包括：

1. **审视研究问题本身**：这个问题真的有研究价值吗？文献里是不是已经有人做了？
2. **审视设计的可行性**：自己手头的数据是否够用？是否能拿到提案要求的 ESG 评级数据？
3. **审视设计的创新性**：这份提案是不是太"标准"了，没什么新意？怎么让设计更有特色？

这些判断都要研究者自己做。`/empirical-design` 给出的是基础设施——它把所有文献里已有的方法整理好摆出来，但**最终的研究 idea、做哪一块的判断、怎么做出新意，仍然是研究者的工作**。

> [!NOTE]
> **AI 加速 ≠ AI 替代**
>
> 这是 EmpiricalWiki 整个设计哲学的一条主线。AI 可以替你处理那些机械性、重复性的整理工作，但不能替你完成那些需要主体判断的工作——发现问题、判断创新性、决定研究方向。
>
> 真正的科研工作里，机械整理大约占 40% 的时间，主体判断占 60%。EmpiricalWiki 把那 40% 压缩到 10%，腾出 30% 让你花在那 60% 上。**这就是 AI 在科研中应该扮演的角色**。

---

## 本章小结

`/empirical-design` 把"一句研究问题"变成"一份完整研究设计提案"，提案包括研究问题精细化、变量设计、模型设定、识别策略、稳健性、异质性、数据缺口七个部分，每一部分都基于 wiki 里累积的文献内容。`/stata-plan` 把研究设计提案转成可执行的 Stata `.do` 文件骨架。两个 skill 串起来，把"读完文献到能跑数据"这件几周的事情压缩到几小时。

但这不是"AI 替你做研究"。AI 加速的是机械性整理，研究者仍然要做主体判断——发现问题、判断创新性、决定方向。这是 EmpiricalWiki 设计哲学的核心：腾出时间，让研究者花在更值得思考的事情上。

---
