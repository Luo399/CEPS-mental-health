"""
06_iv_analysis.py
===================
工具变量（IV）分析：班级同学父母教育水平对心理健康的影响。

识别策略:
  IV = 同校其他年级同学父母教育水平均值 (schg_mean_max_education)
  理由: 其他年级的家长教育水平影响班级构成但不直接影响心理健康

分析步骤:
  1. 构造IV并检验相关性
  2. 第一阶段回归 + F统计量（弱工具变量检验）
  3. 第二阶段IV回归（2SLS）
  4. 过度识别检验（使用多个IV：均值+标准差）
  5. 分SES组的IV回归

输出:
  - tablefile/iv_first_stage.csv       (第一阶段回归)
  - tablefile/iv_second_stage.csv      (第二阶段IV回归)
  - tablefile/iv_by_ses.csv            (分SES组IV)
  - figurefile/iv_first_stage.png      (第一阶段可视化)
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

CONTROLS = ['gender', 'hukou_type', 'nationality', 'yn_single_child', 'tscore']


# ============================================================
# 1. 读取并准备数据
# ============================================================
print("=" * 60)
print("1. 读取并准备数据...")
print("=" * 60)

df = pd.read_stata(INPUT_FILE, convert_categoricals=False)
print(f"   总数据: {df.shape[0]} 行 × {df.shape[1]} 列")

# 仅保留wave1样本
df_w1 = df[df['grade'].isin([0, 2])].copy()
print(f"   Wave1样本: {len(df_w1)} 行")

# 核心自变量标准化
df_w1['cls_mean_edu'] = df_w1['cls_mean_max_education']
df_w1['cls_mean_edu_z'] = (df_w1['cls_mean_edu'] -
  df_w1['cls_mean_edu'].mean()) / df_w1['cls_mean_edu'].std()

# IV: 同校其他年级同学父母教育水平均值
# schg_mean_max_education 已经是学校-年级层面的均值
# 但我们需要"同校其他年级"的均值，需要进行leave-one-out处理
# 对于每个学校，排除本年级后计算其他年级的均值
print("\n   构造IV: 同校其他年级同学父母教育水平...")

# 计算每个学校-年级层面的均值
sch_grade_mean = df_w1.groupby('schidgrade')['cls_mean_edu'].mean().reset_index()
sch_grade_mean.columns = ['schidgrade', 'schg_own_mean']

# 合并回数据
df_w1 = df_w1.merge(sch_grade_mean, on='schidgrade', how='left')

# 计算每个学校中其他年级的均值 (leave-one-grade-out)
iv_data = []
for sch_id in df_w1['schids'].unique():
  sch_mask = df_w1['schids'] == sch_id
  sch_grades = df_w1.loc[sch_mask, 'schidgrade'].unique()
  if len(sch_grades) <= 1:
    # 只有1个年级的学校，无法构造leave-one-out IV
    continue
  for sg in sch_grades:
    other_grades = [g for g in sch_grades if g != sg]
    other_mean = df_w1.loc[df_w1['schidgrade'].isin(other_grades), 'cls_mean_edu'].mean()
    iv_data.append({'schidgrade': sg, 'iv_other_grade_mean': other_mean})

df_iv = pd.DataFrame(iv_data)
df_w1 = df_w1.merge(df_iv, on='schidgrade', how='left')

# 同时使用学校的标准差作为第二个IV（用于过度识别检验）
sch_grade_sd = df_w1.groupby('schidgrade')['cls_mean_edu'].std().reset_index()
sch_grade_sd.columns = ['schidgrade', 'schg_own_sd']
df_w1 = df_w1.merge(sch_grade_sd, on='schidgrade', how='left')

# 对IV标准化
df_w1['iv_other_grade_mean_z'] = (df_w1['iv_other_grade_mean'] -
  df_w1['iv_other_grade_mean'].mean()) / df_w1['iv_other_grade_mean'].std()

# 删除缺失
iv_vars = ['mental_common_z', 'cls_mean_edu_z', 'cls_mean_edu',
           'iv_other_grade_mean', 'iv_other_grade_mean_z',
           'schg_own_mean', 'schg_own_sd',
           'ses_index', 'ses_tercile', 'ses_low', 'ses_high'] + CONTROLS
df_iv = df_w1.dropna(subset=iv_vars).copy()
print(f"   完整IV样本: {len(df_iv)} 行")
print(f"   学校数: {df_iv['schids'].nunique()}")
print(f"   有IV的学校数: {df_iv['iv_other_grade_mean'].notna().sum() > 0}")


# ============================================================
# 2. 第一阶段回归：IV → 内生变量
# ============================================================
print("\n" + "=" * 60)
print("2. 第一阶段回归...")
print("=" * 60)

import statsmodels.api as sm
from scipy import stats

def run_iv_1sls(y_name, x_names, data, cluster_var='schids'):
  """运行第一阶段回归"""
  y = data[y_name]
  X = data[x_names]
  X = sm.add_constant(X)
  model = sm.OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': data[cluster_var]})
  return model

# 第一阶段: cls_mean_edu_z = α + β·IV + γ·X + ε
fs1_x = ['iv_other_grade_mean_z'] + CONTROLS
fs1 = run_iv_1sls('cls_mean_edu_z', fs1_x, df_iv)
print(f"   第一阶段: cls_mean_edu_z ~ iv_other_grade_mean_z + controls")
print(f"   β(IV)={fs1.params['iv_other_grade_mean_z']:.4f}, "
      f"se={fs1.bse['iv_other_grade_mean_z']:.4f}, "
      f"t={fs1.tvalues['iv_other_grade_mean_z']:.3f}, "
      f"p={fs1.pvalues['iv_other_grade_mean_z']:.4f}")

# F统计量（弱工具变量检验）
# 计算partial F-statistic for IV
r2_u = fs1.rsquared  # 不受限模型R²
# 受限模型（仅控制变量）
r1 = run_iv_1sls('cls_mean_edu_z', CONTROLS, df_iv)
r2_r = r1.rsquared  # 受限模型R²
n = int(fs1.nobs)
k = len(fs1_x)  # 参数个数（含IV）
f_stat = ((r2_u - r2_r) / 1) / ((1 - r2_u) / (n - k))
print(f"   Partial F统计量: {f_stat:.3f}")
print(f"   弱工具变量检验: {'通过 (F>10)' if f_stat > 10 else '警告: F<10, 可能存在弱工具变量问题'}")

# 获取预测值
df_iv['cls_edu_hat'] = fs1.predict(sm.add_constant(df_iv[fs1_x]))


# ============================================================
# 3. 第二阶段IV回归（2SLS）
# ============================================================
print("\n" + "=" * 60)
print("3. 第二阶段IV回归（2SLS）...")
print("=" * 60)

# 手动2SLS: 第二阶段用预测值
ss_x = ['cls_edu_hat'] + CONTROLS
y_ss = df_iv['mental_common_z']
X_ss = df_iv[ss_x]
X_ss = sm.add_constant(X_ss)

# 第二阶段回归（标准误需要校正）
ss_model = sm.OLS(y_ss, X_ss).fit(cov_type='cluster', cov_kwds={'groups': df_iv['schids']})

# 校正标准误（2SLS标准误应使用残差=原始y - β·真实X, 而非β·预测X）
residuals = df_iv['mental_common_z'] - ss_model.predict(X_ss)
X_real = sm.add_constant(df_iv[['cls_mean_edu_z'] + CONTROLS])
# 手动计算校正后的方差-协方差矩阵
sigma2 = np.sum(residuals**2) / (len(residuals) - len(ss_x) - 1)
# 使用sandwich estimator
X_real_np = X_real.values.astype(np.float64)
residuals_np = residuals.values.astype(np.float64)
sch_ids = df_iv['schids'].values
meat = np.zeros((X_real_np.shape[1], X_real_np.shape[1]))
for sch_id in np.unique(sch_ids):
  mask = sch_ids == sch_id
  X_g = X_real_np[mask]
  res_g = residuals_np[mask]
  meat += X_g.T @ (res_g.reshape(-1, 1) @ res_g.reshape(1, -1)) @ X_g
bread = np.linalg.inv(X_real_np.T @ X_real_np)
vcv_corrected = bread @ meat @ bread

# 获取校正后的系数和标准误
beta_2sls = ss_model.params['cls_edu_hat']
se_2sls_corrected = np.sqrt(np.diag(vcv_corrected))[1]  # 第1个是cls_edu_hat
t_2sls = beta_2sls / se_2sls_corrected
p_2sls = 2 * (1 - stats.norm.cdf(abs(t_2sls)))
print(f"   第二阶段: mental_common_z ~ cls_mean_edu_hat + controls")
print(f"   β(cls_edu)={beta_2sls:.4f}, 校正se={se_2sls_corrected:.4f}, "
      f"t={t_2sls:.3f}, p={p_2sls:.4f}")
print(f"   R²={ss_model.rsquared:.3f}")

# 对比OLS结果（同一模型无IV）
ols_comp = sm.OLS(df_iv['mental_common_z'],
  sm.add_constant(df_iv[['cls_mean_edu_z'] + CONTROLS])).fit(
  cov_type='cluster', cov_kwds={'groups': df_iv['schids']})
print(f"\n   对比: OLS β(cls_edu)={ols_comp.params['cls_mean_edu_z']:.4f}, "
      f"se={ols_comp.bse['cls_mean_edu_z']:.4f}")


# ============================================================
# 4. 过度识别检验（Hansen J检验）
# ============================================================
print("\n" + "=" * 60)
print("4. 过度识别检验（Hansen J检验）...")
print("=" * 60)

# 使用两个IV: iv_other_grade_mean_z 和 schg_own_sd
# 第一步: 用两个IV做第一阶段
fs2_x = ['iv_other_grade_mean_z', 'schg_own_sd'] + CONTROLS
fs2 = run_iv_1sls('cls_mean_edu_z', fs2_x, df_iv)
print(f"   双IV第一阶段:")
print(f"   β(IV1_other_mean)={fs2.params['iv_other_grade_mean_z']:.4f}, "
      f"p={fs2.pvalues['iv_other_grade_mean_z']:.4f}")
print(f"   β(IV2_sch_sd)={fs2.params['schg_own_sd']:.4f}, "
      f"p={fs2.pvalues['schg_own_sd']:.4f}")

# F统计量（联合检验）
r2_u_2iv = fs2.rsquared
r2_r_2iv = r1.rsquared
f_stat_2iv = ((r2_u_2iv - r2_r_2iv) / 2) / ((1 - r2_u_2iv) / (n - len(fs2_x)))
print(f"   联合F统计量: {f_stat_2iv:.3f}")

# 获取预测值
df_iv['cls_edu_hat_2iv'] = fs2.predict(sm.add_constant(df_iv[fs2_x]))

# 第二阶段: 用预测值
ss2 = sm.OLS(df_iv['mental_common_z'],
  sm.add_constant(df_iv[['cls_edu_hat_2iv'] + CONTROLS])).fit(
  cov_type='cluster', cov_kwds={'groups': df_iv['schids']})

# Hansen J检验: 残差对IV回归
# 残差 = 真实y - 第二阶段系数 × 真实X
beta_2sls_2iv = ss2.params['cls_edu_hat_2iv']
# 提取控制变量系数
ctrl_params = np.array([ss2.params[c] for c in CONTROLS])
ctrl_vals = df_iv[CONTROLS].values.astype(np.float64)
j_residuals = df_iv['mental_common_z'].values.astype(np.float64) - (
  beta_2sls_2iv * df_iv['cls_mean_edu_z'].values.astype(np.float64) +
  ctrl_vals @ ctrl_params +
  ss2.params['const']
)

# 残差对IV和控制变量回归
j_X = sm.add_constant(df_iv[['iv_other_grade_mean_z', 'schg_own_sd'] + CONTROLS])
j_model = sm.OLS(j_residuals, j_X).fit()
j_stat = j_model.nobs * j_model.rsquared  # J统计量
j_pval = 1 - stats.chi2.cdf(j_stat, df=1)  # 过度识别df=2IV-1内生=1
print(f"   Hansen J统计量: {j_stat:.3f}")
print(f"   J检验p值: {j_pval:.4f}")
print(f"   过度识别检验: {'通过 (p>0.05)' if j_pval > 0.05 else '未通过 (p<0.05)'}")


# ============================================================
# 5. 分SES组的IV回归
# ============================================================
print("\n" + "=" * 60)
print("5. 分SES组的IV回归...")
print("=" * 60)

ses_iv_results = {}
for ses_val, ses_label in [(0, '低SES'), (1, '中SES'), (2, '高SES')]:
  subset = df_iv[df_iv['ses_tercile'] == ses_val]
  if len(subset) < 50:
    print(f"   {ses_label}: 样本不足, 跳过")
    continue
  # 第一阶段
  fs_ses = run_iv_1sls('cls_mean_edu_z', fs1_x, subset)
  f_ses = ((fs_ses.rsquared - r1.rsquared) / 1) / ((1 - fs_ses.rsquared) / (len(subset) - len(fs1_x)))
  # 预测值
  subset = subset.copy()
  subset['cls_edu_hat_ses'] = fs_ses.predict(sm.add_constant(subset[fs1_x]))
  # 第二阶段
  ss_ses = sm.OLS(subset['mental_common_z'],
    sm.add_constant(subset[['cls_edu_hat_ses'] + CONTROLS])).fit(
    cov_type='cluster', cov_kwds={'groups': subset['schids']})
  # 校正标准误
  res_ses = subset['mental_common_z'] - ss_ses.predict(
    sm.add_constant(subset[['cls_edu_hat_ses'] + CONTROLS]))
  X_real_ses = sm.add_constant(subset[['cls_mean_edu_z'] + CONTROLS])
  X_real_ses_np = X_real_ses.values.astype(np.float64)
  res_ses_np = res_ses.values.astype(np.float64)
  sch_ids_ses = subset['schids'].values
  meat_ses = np.zeros((X_real_ses_np.shape[1], X_real_ses_np.shape[1]))
  for sch_id in np.unique(sch_ids_ses):
    mask = sch_ids_ses == sch_id
    X_g = X_real_ses_np[mask]
    res_g = res_ses_np[mask]
    meat_ses += X_g.T @ (res_g.reshape(-1, 1) @ res_g.reshape(1, -1)) @ X_g
  bread_ses = np.linalg.inv(X_real_ses_np.T @ X_real_ses_np)
  vcv_ses = bread_ses @ meat_ses @ bread_ses
  se_ses = np.sqrt(np.diag(vcv_ses))[1]  # cls_edu_hat的se
  t_ses = ss_ses.params['cls_edu_hat_ses'] / se_ses
  p_ses = 2 * (1 - stats.norm.cdf(abs(t_ses)))

  ses_iv_results[ses_label] = {
    'beta': ss_ses.params['cls_edu_hat_ses'], 'se': se_ses,
    'pval': p_ses, 'f_stat': f_ses, 'n': len(subset)
  }
  print(f"   {ses_label}(n={len(subset)}): IV β={ses_iv_results[ses_label]['beta']:.4f}, "
        f"se={ses_iv_results[ses_label]['se']:.4f}, "
        f"p={ses_iv_results[ses_label]['pval']:.4f}, "
        f"F={ses_iv_results[ses_label]['f_stat']:.2f}")


# ============================================================
# 6. 保存结果表
# ============================================================
print("\n" + "=" * 60)
print("6. 保存结果表...")
print("=" * 60)

# 第一阶段结果
fs_results = [{
  '模型': '第一阶段',
  '内生变量': 'cls_mean_edu_z',
  'IV': '同校其他年级均值',
  'IV系数': f"{fs1.params['iv_other_grade_mean_z']:.4f}",
  'IV标准误': f"({fs1.bse['iv_other_grade_mean_z']:.4f})",
  'IV_p值': f"{fs1.pvalues['iv_other_grade_mean_z']:.4f}",
  'Partial F': f"{f_stat:.3f}",
  'R²': f"{fs1.rsquared:.3f}",
  'N': f"{int(fs1.nobs)}",
}]
pd.DataFrame(fs_results).to_csv(os.path.join(TABLE_DIR, 'iv_first_stage.csv'),
                                 index=False, encoding='utf-8-sig')
print(f"   第一阶段结果保存至: {TABLE_DIR}/iv_first_stage.csv")

# 第二阶段结果
ss_results = [{
  '模型': '2SLS',
  'IV': '同校其他年级均值',
  'β(cls_edu)': f"{beta_2sls:.4f}",
  '校正标准误': f"({se_2sls_corrected:.4f})",
  'p值': f"{p_2sls:.4f}",
  'R²': f"{ss_model.rsquared:.3f}",
  'N': f"{int(ss_model.nobs)}",
  'Partial F': f"{f_stat:.3f}",
  '对比OLS β': f"{ols_comp.params['cls_mean_edu_z']:.4f}",
  '对比OLS se': f"({ols_comp.bse['cls_mean_edu_z']:.4f})",
}]
# 添加过度识别检验
if j_pval < 1:
  ss_results[0]['Hansen J'] = f"{j_stat:.3f}"
  ss_results[0]['J检验p值'] = f"{j_pval:.4f}"

pd.DataFrame(ss_results).to_csv(os.path.join(TABLE_DIR, 'iv_second_stage.csv'),
                                 index=False, encoding='utf-8-sig')
print(f"   第二阶段结果保存至: {TABLE_DIR}/iv_second_stage.csv")

# 分SES组IV
ses_rows = []
for label, r in ses_iv_results.items():
  ses_rows.append({
    'SES组': label,
    'IV β': f"{r['beta']:.4f}",
    '校正se': f"({r['se']:.4f})",
    'p值': f"{r['pval']:.4f}",
    'F统计量': f"{r['f_stat']:.2f}",
    'N': f"{r['n']}",
  })
pd.DataFrame(ses_rows).to_csv(os.path.join(TABLE_DIR, 'iv_by_ses.csv'),
                               index=False, encoding='utf-8-sig')
print(f"   分SES组IV结果保存至: {TABLE_DIR}/iv_by_ses.csv")


# ============================================================
# 7. 第一阶段可视化
# ============================================================
print("\n" + "=" * 60)
print("7. 第一阶段可视化...")
print("=" * 60)

try:
  import matplotlib
  matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
  plt.rcParams['axes.unicode_minus'] = False

  fig, axes = plt.subplots(1, 2, figsize=(12, 5))

  # 7a IV与内生变量的散点图
  axes[0].scatter(df_iv['iv_other_grade_mean_z'], df_iv['cls_mean_edu_z'],
                  alpha=0.3, s=5, c='#4A90D9')
  # 拟合线
  from numpy.polynomial import polynomial as P
  x_sort = np.sort(df_iv['iv_other_grade_mean_z'].dropna())
  coeffs = np.polyfit(df_iv['iv_other_grade_mean_z'].dropna(),
                      df_iv['cls_mean_edu_z'].dropna(), 1)
  axes[0].plot(x_sort, np.polyval(coeffs, x_sort), 'r-', linewidth=2)
  axes[0].set_xlabel('同校其他年级平均父母教育水平 (z-score)')
  axes[0].set_ylabel('本班平均父母教育水平 (z-score)')
  axes[0].set_title('第一阶段: IV与内生变量的相关性')
  axes[0].text(0.05, 0.95, f'F={f_stat:.1f}', transform=axes[0].transAxes,
               fontsize=12, verticalalignment='top')

  # 7b 分SES组的IV系数
  if ses_iv_results:
    labels = list(ses_iv_results.keys())
    betas_iv = [ses_iv_results[s]['beta'] for s in labels]
    ses_errors_iv = [ses_iv_results[s]['se'] for s in labels]
    colors = ['#E74C3C', '#F39C12', '#2ECC71']
    x_pos = np.arange(len(labels))
    axes[1].bar(x_pos, betas_iv, yerr=[1.96 * se for se in ses_errors_iv],
                color=colors, alpha=0.8, capsize=6, width=0.5)
    axes[1].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    axes[1].set_xticks(x_pos)
    axes[1].set_xticklabels(labels, fontsize=12)
    axes[1].set_ylabel('IV估计量 (2SLS)', fontsize=11)
    axes[1].set_title('不同SES水平的IV估计（95%置信区间）', fontsize=13)

  plt.tight_layout()
  plt.savefig(os.path.join(FIGURE_DIR, 'iv_first_stage.png'), dpi=150, bbox_inches='tight')
  plt.close()
  print(f"   第一阶段图保存至: {FIGURE_DIR}/iv_first_stage.png")

except Exception as e:
  print(f"   警告: 可视化失败: {e}")


# ============================================================
# 8. 结果摘要
# ============================================================
print("\n" + "=" * 60)
print("IV分析结果摘要")
print("=" * 60)
print(f"1. 第一阶段: IV系数={fs1.params['iv_other_grade_mean_z']:.4f} (p={fs1.pvalues['iv_other_grade_mean_z']:.4f})")
print(f"   Partial F统计量={f_stat:.2f} {'✅' if f_stat > 10 else '⚠️'}")
print(f"2. 2SLS: β(cls_edu)={beta_2sls:.4f} (校正se={se_2sls_corrected:.4f}, p={p_2sls:.4f})")
print(f"   对比OLS: β(cls_edu)={ols_comp.params['cls_mean_edu_z']:.4f} (se={ols_comp.bse['cls_mean_edu_z']:.4f})")
print(f"3. Hansen J检验: J={j_stat:.3f}, p={j_pval:.4f}")
print(f"4. SES非对称IV:")
for label, r in ses_iv_results.items():
  print(f"   {label}: β={r['beta']:.4f} (p={r['pval']:.4f}, F={r['f_stat']:.2f})")
print("\n✅ 脚本6完成: IV分析成功!")