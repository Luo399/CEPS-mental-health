"""
04_baseline_ols.py
===================
基准OLS回归：班级同学父母教育水平对心理健康的影响。

分析策略（四步递进）:
  1. 全样本OLS：同学父母教育 → 心理健康
  2. 低SES vs 高SES子样本回归 + Wald检验组间差异
  3. 交互项模型：PeerEdu × SES
  4. 边际效应图

输出:
  - tablefile/baseline_ols.csv              (全样本OLS结果)
  - tablefile/by_ses_ols.csv                (分SES组OLS结果)
  - tablefile/interaction_ols.csv           (交互项模型)
  - figurefile/marginal_effects.png         (边际效应图)
"""

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 路径配置
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'analysis_final.dta')
TABLE_DIR = os.path.join(BASE_DIR, 'tablefile')
FIGURE_DIR = os.path.join(BASE_DIR, 'figurefile')
os.makedirs(TABLE_DIR, exist_ok=True)
os.makedirs(FIGURE_DIR, exist_ok=True)

# 控制变量列表
CONTROLS = ['gender', 'hukou_type', 'nationality', 'yn_single_child', 'tscore']
SCHOOL_FE = 'schids'  # 学校固定效应


# ============================================================
# 1. 读取并准备数据
# ============================================================
print("=" * 60)
print("1. 读取并准备数据...")
print("=" * 60)

df = pd.read_stata(INPUT_FILE, convert_categoricals=False)
print(f"   总数据: {df.shape[0]} 行 × {df.shape[1]} 列")

# 仅保留wave1截面样本
df_w1 = df[df['grade'].isin([0, 2])].copy()
print(f"   Wave1样本: {len(df_w1)} 行")

# 构造回归所需变量
df_w1['cls_mean_edu'] = df_w1['cls_mean_max_education']  # 核心自变量简称
# ses_tercile在.dta中为0,1,2, 对应低/中/高SES
df_w1['ses_low'] = (df_w1['ses_tercile'] == 0).astype(float)
df_w1['ses_high'] = (df_w1['ses_tercile'] == 2).astype(float)

# 标准化核心自变量（便于解释系数）
df_w1['cls_mean_edu_z'] = (df_w1['cls_mean_edu'] - df_w1['cls_mean_edu'].mean()) / df_w1['cls_mean_edu'].std()

# 构造交互项
df_w1['cls_edu_x_ses_low'] = df_w1['cls_mean_edu_z'] * df_w1['ses_low']
df_w1['cls_edu_x_ses_high'] = df_w1['cls_mean_edu_z'] * df_w1['ses_high']

# 完整分析样本
reg_vars = ['mental_common_z', 'cls_mean_edu_z', 'cls_mean_edu',
            'ses_index', 'ses_low', 'ses_high', 'ses_tercile',
            'cls_edu_x_ses_low', 'cls_edu_x_ses_high'] + CONTROLS + [SCHOOL_FE]
df_reg = df_w1.dropna(subset=reg_vars).copy()
print(f"   完整分析样本: {len(df_reg)} 行")
print(f"   班级数: {df_reg['clsids'].nunique()}, 学校数: {df_reg['schids'].nunique()}")


# ============================================================
# 2. 全样本OLS回归
# ============================================================
print("\n" + "=" * 60)
print("2. 全样本OLS回归...")
print("=" * 60)

import statsmodels.api as sm
from statsmodels.iolib.summary2 import summary_col

def run_ols(y_name, x_names, data, cluster_var=None, use_formula=False, fe_var=None):
  """
  运行OLS回归，可选聚类标准误
  返回: fitted模型
  """
  if use_formula:
    # 使用公式API（支持分类变量和固定效应）
    formula = f"{y_name} ~ {' + '.join(x_names)}"
    if fe_var:
      formula += f" + C({fe_var})"
    model = sm.OLS.from_formula(formula, data=data).fit(
      cov_type='cluster', cov_kwds={'groups': data[cluster_var]}) if cluster_var else \
      sm.OLS.from_formula(formula, data=data).fit()
    return model

  y = data[y_name]
  X = data[x_names]
  X = sm.add_constant(X)
  model = sm.OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': data[cluster_var]}) if cluster_var else sm.OLS(y, X).fit()
  return model

# 模型1: 仅核心自变量
m1 = run_ols('mental_common_z', ['cls_mean_edu_z'], df_reg, cluster_var='schids')

# 模型2: 加控制变量
m2 = run_ols('mental_common_z', ['cls_mean_edu_z'] + CONTROLS, df_reg, cluster_var='schids')

# 模型3: 加学校固定效应
m3 = run_ols('mental_common_z', ['cls_mean_edu_z'] + CONTROLS, df_reg,
             cluster_var='schids', use_formula=True, fe_var='schids')

print("\n   全样本OLS结果:")
print(f"   模型1 (仅核心自变量): R²={m1.rsquared:.3f}, β(cls_mean_edu)={m1.params['cls_mean_edu_z']:.4f} (p={m1.pvalues['cls_mean_edu_z']:.4f})")
print(f"   模型2 (+控制变量): R²={m2.rsquared:.3f}, β(cls_mean_edu)={m2.params['cls_mean_edu_z']:.4f} (p={m2.pvalues['cls_mean_edu_z']:.4f})")
# 模型3用了公式API, 参数名可能有前缀
m3_cls_key = [k for k in m3.params.index if 'cls_mean_edu_z' in k][0]
print(f"   模型3 (+学校FE): R²={m3.rsquared:.3f}, β(cls_mean_edu)={m3.params[m3_cls_key]:.4f} (p={m3.pvalues[m3_cls_key]:.4f})")


# ============================================================
# 3. 分SES组回归
# ============================================================
print("\n" + "=" * 60)
print("3. 分SES三分组回归...")
print("=" * 60)

ses_models = {}
for ses_val, ses_label in [(0, '低SES'), (1, '中SES'), (2, '高SES')]:
  subset = df_reg[df_reg['ses_tercile'] == ses_val]
  if len(subset) < 50:
    print(f"   {ses_label}: 样本不足({len(subset)}), 跳过")
    continue
  m = run_ols('mental_common_z', ['cls_mean_edu_z'] + CONTROLS, subset, cluster_var='schids')
  ses_models[ses_label] = m
  print(f"   {ses_label}(n={len(subset)}): β={m.params['cls_mean_edu_z']:.4f}, "
        f"p={m.pvalues['cls_mean_edu_z']:.4f}, R²={m.rsquared:.3f}")

# Wald检验: 低SES vs 高SES的系数是否显著不同
b_diff_info = None
if '低SES' in ses_models and '高SES' in ses_models:
  b_low = ses_models['低SES'].params['cls_mean_edu_z']
  b_high = ses_models['高SES'].params['cls_mean_edu_z']
  se_low = ses_models['低SES'].bse['cls_mean_edu_z']
  se_high = ses_models['高SES'].bse['cls_mean_edu_z']
  from scipy import stats as scipy_stats
  z_stat = (b_low - b_high) / np.sqrt(se_low**2 + se_high**2)
  p_val = 2 * (1 - scipy_stats.norm.cdf(abs(z_stat)))
  b_diff_info = {'b_low': b_low, 'b_high': b_high, 'z_stat': z_stat, 'p_val': p_val}
  print(f"\n   Wald检验(Suest): 低SES - 高SES")
  print(f"   系数差: {b_low - b_high:.4f}")
  print(f"   z统计量: {z_stat:.3f}")
  print(f"   p值: {p_val:.4f}")


# ============================================================
# 4. 交互项模型
# ============================================================
print("\n" + "=" * 60)
print("4. 交互项模型：PeerEdu × SES...")
print("=" * 60)

# 模型4: 核心自变量 + SES主效应 + 交互项
m4 = run_ols('mental_common_z',
             ['cls_mean_edu_z', 'ses_index', 'cls_edu_x_ses_low', 'cls_edu_x_ses_high'] + CONTROLS,
             df_reg, cluster_var='schids')
print(f"\n   交互项模型: R²={m4.rsquared:.3f}")
print(f"   cls_mean_edu: β={m4.params['cls_mean_edu_z']:.4f} (p={m4.pvalues['cls_mean_edu_z']:.4f})")
print(f"   ses_index: β={m4.params['ses_index']:.4f} (p={m4.pvalues['ses_index']:.4f})")
print(f"   cls_edu × ses_low: β={m4.params['cls_edu_x_ses_low']:.4f} (p={m4.pvalues['cls_edu_x_ses_low']:.4f})")
print(f"   cls_edu × ses_high: β={m4.params['cls_edu_x_ses_high']:.4f} (p={m4.pvalues['cls_edu_x_ses_high']:.4f})")


# ============================================================
# 5. 边际效应图
# ============================================================
print("\n" + "=" * 60)
print("5. 生成边际效应图...")
print("=" * 60)

try:
  import matplotlib
  matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
  plt.rcParams['axes.unicode_minus'] = False

  # 从交互项模型计算边际效应
  beta_cls = m4.params['cls_mean_edu_z']
  beta_interact_low = m4.params['cls_edu_x_ses_low']
  beta_interact_high = m4.params['cls_edu_x_ses_high']

  # 对低SES的边际效应: β_cls + β_interact_low
  me_low = beta_cls + beta_interact_low
  # 对高SES的边际效应: β_cls + β_interact_high
  me_high = beta_cls + beta_interact_high
  # 对中SES的边际效应: β_cls (基准)
  me_mid = beta_cls

  # 计算标准误（近似）
  cov = m4.cov_params()
  se_low = np.sqrt(cov.loc['cls_mean_edu_z', 'cls_mean_edu_z'] +
                   cov.loc['cls_edu_x_ses_low', 'cls_edu_x_ses_low'] +
                   2 * cov.loc['cls_mean_edu_z', 'cls_edu_x_ses_low'])
  se_high = np.sqrt(cov.loc['cls_mean_edu_z', 'cls_mean_edu_z'] +
                    cov.loc['cls_edu_x_ses_high', 'cls_edu_x_ses_high'] +
                    2 * cov.loc['cls_mean_edu_z', 'cls_edu_x_ses_high'])
  se_mid = np.sqrt(cov.loc['cls_mean_edu_z', 'cls_mean_edu_z'])

  # 绘图
  fig, ax = plt.subplots(figsize=(8, 5))
  groups = ['低SES', '中SES', '高SES']
  mes = [me_low, me_mid, me_high]
  ses_errors = [se_low, se_mid, se_high]
  colors = ['#E74C3C', '#F39C12', '#2ECC71']

  x_pos = np.arange(len(groups))
  ax.bar(x_pos, mes, yerr=[1.96 * se for se in ses_errors], color=colors,
         alpha=0.8, capsize=6, width=0.5, error_kw={'linewidth': 1.5})
  ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
  ax.set_xticks(x_pos)
  ax.set_xticklabels(groups, fontsize=12)
  ax.set_ylabel('班级平均父母教育对心理健康的边际效应', fontsize=11)
  ax.set_title('不同SES水平下同学父母教育的边际效应（95%置信区间）', fontsize=13)

  # 添加数值标签
  for i, (v, se) in enumerate(zip(mes, ses_errors)):
    ax.text(i, v + 1.96*se + 0.02, f'{v:.3f}', ha='center', fontsize=10,
            fontweight='bold', color=colors[i])

  plt.tight_layout()
  plt.savefig(os.path.join(FIGURE_DIR, 'marginal_effects.png'), dpi=150, bbox_inches='tight')
  plt.close()
  print(f"   边际效应图保存至: {FIGURE_DIR}/marginal_effects.png")

except Exception as e:
  print(f"   警告: 边际效应图生成失败: {e}")


# ============================================================
# 6. 保存回归结果表
# ============================================================
print("\n" + "=" * 60)
print("6. 保存回归结果表...")
print("=" * 60)

# 全样本结果
ols_results = []
for name, m in [('模型1:仅核心变量', m1), ('模型2:+控制变量', m2), ('模型3:+学校FE', m3)]:
  # 公式API参数名可能不同, 模糊匹配
  cls_key = [k for k in m.params.index if 'cls_mean_edu_z' in k]
  cls_key = cls_key[0] if cls_key else 'cls_mean_edu_z'
  ols_results.append({
    '模型': name,
    'cls_mean_edu_z': f"{m.params.get(cls_key, np.nan):.4f}",
    'cls_mean_edu_z_se': f"({m.bse.get(cls_key, np.nan):.4f})",
    'cls_mean_edu_z_p': f"{m.pvalues.get(cls_key, np.nan):.4f}",
    'R²': f"{m.rsquared:.3f}",
    'adj_R²': f"{m.rsquared_adj:.3f}",
    'N': f"{int(m.nobs)}",
    '控制变量': '否' if '模型1' in name else '是',
    '学校固定效应': '否' if '模型3' not in name else '是',
  })

pd.DataFrame(ols_results).to_csv(os.path.join(TABLE_DIR, 'baseline_ols.csv'),
                                  index=False, encoding='utf-8-sig')
print(f"   全样本OLS结果保存至: {TABLE_DIR}/baseline_ols.csv")

# 分SES组结果
by_ses_results = []
for label, m in ses_models.items():
  by_ses_results.append({
    'SES组': label,
    'cls_mean_edu_z': f"{m.params.get('cls_mean_edu_z', np.nan):.4f}",
    'cls_mean_edu_z_se': f"({m.bse.get('cls_mean_edu_z', np.nan):.4f})",
    'cls_mean_edu_z_p': f"{m.pvalues.get('cls_mean_edu_z', np.nan):.4f}",
    'R²': f"{m.rsquared:.3f}",
    'N': f"{int(m.nobs)}",
  })

pd.DataFrame(by_ses_results).to_csv(os.path.join(TABLE_DIR, 'by_ses_ols.csv'),
                                     index=False, encoding='utf-8-sig')
print(f"   分SES组OLS结果保存至: {TABLE_DIR}/by_ses_ols.csv")

# 交互项模型
interact_results = {
  '模型': '交互项模型',
  'cls_mean_edu_z': f"{m4.params.get('cls_mean_edu_z', np.nan):.4f}",
  'cls_mean_edu_z_se': f"({m4.bse.get('cls_mean_edu_z', np.nan):.4f})",
  'ses_index': f"{m4.params.get('ses_index', np.nan):.4f}",
  'ses_index_se': f"({m4.bse.get('ses_index', np.nan):.4f})",
  'cls_edu_x_ses_low': f"{m4.params.get('cls_edu_x_ses_low', np.nan):.4f}",
  'cls_edu_x_ses_low_se': f"({m4.bse.get('cls_edu_x_ses_low', np.nan):.4f})",
  'cls_edu_x_ses_high': f"{m4.params.get('cls_edu_x_ses_high', np.nan):.4f}",
  'cls_edu_x_ses_high_se': f"({m4.bse.get('cls_edu_x_ses_high', np.nan):.4f})",
  'R²': f"{m4.rsquared:.3f}",
  'N': f"{int(m4.nobs)}",
  '控制变量': '是',
}
pd.DataFrame([interact_results]).to_csv(os.path.join(TABLE_DIR, 'interaction_ols.csv'),
                                         index=False, encoding='utf-8-sig')
print(f"   交互项模型结果保存至: {TABLE_DIR}/interaction_ols.csv")

print("\n✅ 脚本4完成: 基准OLS回归成功!")
print("\n" + "=" * 60)
print("关键发现摘要")
print("=" * 60)
print(f"1. 全样本: 同学父母教育每提高1个标准差, 心理健康变化 {m1.params['cls_mean_edu_z']:.4f} (p={m1.pvalues['cls_mean_edu_z']:.4f})")
if b_diff_info:
  print(f"2. 低SES: β={b_diff_info['b_low']:.4f}, 高SES: β={b_diff_info['b_high']:.4f}")
print(f"3. 交互项: cls_edu × ses_low = {m4.params['cls_edu_x_ses_low']:.4f} (p={m4.pvalues['cls_edu_x_ses_low']:.4f})")