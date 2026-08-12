# 国际数据库参考

## Fama-French因子数据库

### 因子数据

| 因子 | 描述 |
|-----|------|
| Fama-French 3因子 | 市场因子(MKT)、规模因子(SMB)、价值因子(HML) |
| Fama-French 5因子 | + 盈利能力因子(RMW)、投资因子(CMA) |
| Carhart 4因子 | 3因子 + 动量因子(UMD) |

### 数据来源

- 网站：http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/
- 格式：CSV/Excel

---

## World Bank（世界银行）

### 主要指标

| 类别 | 指标示例 |
|-----|---------|
| 经济 | GDP、人均GDP、经济增长率 |
| 人口 | 总人口、城市化率、人口增长率 |
| 金融 | 利率、信贷/GDP、金融可及性 |
| 贸易 | 进出口、贸易开放度 |
| 环境 | CO2排放、能源使用 |

### 数据获取

- 数据库：World Bank Data Bank (data.worldbank.org)
- 格式：CSV、Excel、API

---

## CRSP / Compustat

### 数据内容

| 数据库 | 内容 |
|-------|------|
| CRSP | 美国股票日/月收益率、交易数据 |
| Compustat | 美国上市公司财务数据 |

### 常用字段

- CRSP：PERMNO、RET、VOL、PRC
- Compustat：GVKEY、SALE、AT、LEV

### 访问方式

- Wharton WRDS平台
- S&P Capital IQ

---

## NBER（美国国家经济研究局）

### 主要数据集

| 类别 | 数据集 |
|-----|-------|
| 宏观经济 | GDP、物价、就业 |
| 金融 | 利率、股价、波动率 |
| 国际贸易 | 贸易流量、关税 |
| 产业组织 | 行业集中度 |

### 数据获取

- 网站：https://data.nber.org
- 部分数据需申请

---

## 其他常用数据源

| 数据源 | 内容 |
|-------|------|
| FRED | 美联储经济数据 |
| OECD | 经合组织成员国数据 |
| IMF | 国际货币基金组织数据 |
| Bloomberg | 金融数据（需订阅）|
| FactSet | 金融数据（需订阅）|