"""
05_did_analysis.py
===================
双重差分（DID）分析：班级同学父母教育水平变化对心理健康的影响。

分析策略:
  1. 面板数据预处理：宽表→长表转换，构造两期面板
  2. DID基准回归：个体固定效应模型
  3. 按SES分组的DID（非对称效应）
  4. 安慰剂检验：伪处理时间（假设wave1为处理期）

输出:
  - tablefile/did_baseline.csv        (DID基准回归结果)
  - tablefile/did_by_ses.csv          (分SES组DID)
  - tablefile/did_placebo.csv         (安慰剂检验)
  - figurefile/did_parallel_trend.png (平行趋势检验图)
  - figurefile/did_marginal.png       (DID边际效应图)
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
# 1. 读取并准备面板数据
# ============================================================
print("=" * 60)
print("1. 读取并准备面板数据...")
print("=" * 60)

df = pd.read_stata(INPUT_FILE, convert_categoricals=False)
print(f"   总数据: {df.shape[0]} 行 × {df.shape[1]} 列")

# 标记wave: grade=0/2为wave1(基期), grade=1为wave2(追踪)
df['wave'] = np.where(df['grade'].isin([0, 2]), 0, 1)
print(f"   Wave0(基期): {(df['wave']==0).sum()}, Wave1(追踪): {(df['wave']==1).sum()}")

# 保留两期都有观测的样本（平衡面板）
ids_w0 = set(df[df['wave']==0]['ids'])
ids_w1 = set(df[df['wave']==1]['ids'])
balanced_ids = ids_w0 & ids_w1
df_balanced = df[df['ids'].isin(balanced_ids)].copy()
print(f"   平衡面板: {len(df_balanced)} 行, {len(balanced_ids)} 个学生")

# 构造核心变量
# 核心自变量标准化
df_balanced['cls_mean_edu'] = df_balanced['cls_mean_max_education']
df_balanced['cls_mean_edu_z'] = (df_balanced['cls_mean_edu'] -
  df_balanced['cls_mean_edu'].mean()) / df_balanced['cls_mean_edu'].std()

# 定义"高同学教育水平"处理变量 (binary treatment)
# 按wave分别计算中位数，定义该wave中高于中位数的班级为"高教育班级"
df_balanced['high_peer_edu'] = 0.0
for w in [0, 1]:
  mask = df_balanced['wave'] == w
  med = df_balanced.loc[mask, 'cls_mean_edu'].median()
  df_balanced.loc[mask & (df_balanced['cls_mean_edu'] > med), 'high_peer_edu'] = 1.0
print(f"   高同学教育班级(Treat): {df_balanced['high_peer_edu'].mean()*100:.1f}%")

# 交互项: treat × post
df_balanced['treat_x_post'] = df_balanced['high_peer_edu'] * df_balanced['wave']

# 删除缺失
did_vars = ['mental_common_z', 'cls_mean_edu_z', 'high_peer_edu', 'treat_x_post',
            'wave', 'ses_index', 'ses_tercile', 'ses_low', 'ses_high'] + CONTROLS
df_did = df_balanced.dropna(subset=did_vars).copy()
print(f"   完整DID样本: {len(df_did)} 行, {df_did['ids'].nunique()} 个学生")


# ============================================================
# 2. DID基准回归：个体固定效应模型
# ============================================================
print("\n" + "=" * 60)
print("2. DID基准回归...")
print("=" * 60)

import statsmodels.api as sm

def run_fe_ols(y_name, x_names, data, fe_var='ids', cluster_var='schids'):
  """
  个体固定效应OLS回归
  通过组内去均值(demean)实现固定效应
  """
  y = data[y_name].values
  X = data[x_names].values
  # 组内去均值
  groups = data[fe_var].values
  uniq_groups = np.unique(groups)
  group_mean_y = np.zeros_like(y)
  group_mean_X = np.zeros_like(X)
  for g in uniq_groups:
    mask = groups == g
    group_mean_y[mask] = y[mask].mean()
    group_mean_X[mask] = X[mask].mean(axis=0, keepdims=True)
  y_demean = y - group_mean_y
  X_demean = X - group_mean_X
  # 去除全零行（组内无变化）
  valid = ~np.all(X_demean == 0, axis=1)
  y_demean, X_demean = y_demean[valid], X_demean[valid]
  groups_valid = groups[valid]
  # OLS回归
  X_demean = sm.add_constant(X_demean)
  model = sm.OLS(y_demean, X_demean).fit(
    cov_type='cluster', cov_kwds={'groups': groups_valid})
  return model, x_names

# 模型1: DID基本模型 (Treat × Post + Post)
m1_x = ['treat_x_post', 'wave']
m1, _ = run_fe_ols('mental_common_z', m1_x, df_did)
print(f"   模型1 (DID基本): β(treat×post)={m1.params[1]:.4f}, p={m1.pvalues[1]:.4f}, R²={m1.rsquared:.3f}")

# 模型2: DID + 控制变量
m2_x = ['treat_x_post', 'wave'] + CONTROLS
m2, _ = run_fe_ols('mental_common_z', m2_x, df_did)
print(f"   模型2 (+控制): β(treat×post)={m2.params[1]:.4f}, p={m2.pvalues[1]:.4f}, R²={m2.rsquared:.3f}")

# 模型3: 连续型DID (cls_mean_edu_z × wave)
df_did['cls_edu_x_wave'] = df_did['cls_mean_edu_z'] * df_did['wave']
m3_x = ['cls_mean_edu_z', 'wave', 'cls_edu_x_wave'] + CONTROLS
m3, _ = run_fe_ols('mental_common_z', m3_x, df_did)
print(f"   模型3 (连续DID): β(cls_edu×wave)={m3.params[3]:.4f}, p={m3.pvalues[3]:.4f}, R²={m3.rsquared:.3f}")


# ============================================================
# 3. 按SES分组的DID
# ============================================================
print("\n" + "=" * 60)
print("3. 按SES分组的DID...")
print("=" * 60)

ses_did_results = {}
for ses_val, ses_label in [(0, '低SES'), (1, '中SES'), (2, '高SES')]:
  subset = df_did[df_did['ses_tercile'] == ses_val]
  if len(subset) < 100:
    print(f"   {ses_label}: 样本不足, 跳过")
    continue
  m, names = run_fe_ols('mental_common_z', m2_x, subset)
  # 找到treat_x_post系数位置
  tp_idx = names.index('treat_x_post') + 1  # +1 for constant
  ses_did_results[ses_label] = {
    'beta': m.params[tp_idx], 'pval': m.pvalues[tp_idx],
    'se': m.bse[tp_idx], 'n': int(subset['ids'].nunique()),
    'r2': m.rsquared
  }
  print(f"   {ses_label}(n={ses_did_results[ses_label]['n']}): "
        f"β(treat×post)={ses_did_results[ses_label]['beta']:.4f}, "
        f"p={ses_did_results[ses_label]['pval']:.4f}")


# ============================================================
# 4. 安慰剂检验：伪处理时间
# ============================================================
print("\n" + "=" * 60)
print("4. 安慰剂检验：伪处理时间...")
print("=" * 60)

# 仅在wave1样本中，随机将部分学生"伪处理"为wave1即受处理
# 核心思想：如果DID结果由真实处理驱动，伪处理不应显著
np.random.seed(42)
placebo_results = []
n_placebo = 500  # 重复次数

# 仅使用wave1样本，构造伪post变量
df_w1 = df_did[df_did['wave'] == 0].copy()
for i in range(n_placebo):
  # 随机生成伪处理状态
  df_w1['placebo_treat'] = np.random.binomial(1, 0.5, size=len(df_w1))
  df_w1['placebo_interact'] = df_w1['placebo_treat'] * 1  # 伪post=1
  # 回归
  y = df_w1['mental_common_z'].values
  X = df_w1[['placebo_interact'] + CONTROLS].values
  X = sm.add_constant(X)
  m = sm.OLS(y, X).fit()
  placebo_results.append(m.params[1])  # 伪交互项系数

placebo_results = np.array(placebo_results)
pct_gt_actual = np.mean(np.abs(placebo_results) > np.abs(m1.params[1]))
print(f"   安慰剂检验: {n_placebo}次随机化")
print(f"   伪处理系数均值: {placebo_results.mean():.4f}")
print(f"   伪处理系数标准差: {placebo_results.std():.4f}")
print(f"   真实DID系数在安慰剂分布中的位置: p={pct_gt_actual:.4f}")


# ============================================================
# 5. 平行趋势检验（简化版）
# ============================================================
print("\n" + "=" * 60)
print("5. 平行趋势检验...")
print("=" * 60)

try:
  import matplotlib
  matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
  plt.rcParams['axes.unicode_minus'] = False

  # 按wave和treat分组，计算心理健康均值
  trend_data = df_did.groupby(['wave', 'high_peer_edu'])['mental_common_z'].agg(['mean', 'sem']).reset_index()
  trend_data['group'] = trend_data['high_peer_edu'].map({0: '低同学教育水平', 1: '高同学教育水平'})
  trend_data['wave_label'] = trend_data['wave'].map({0: '基期(Wave1)', 1: '追踪(Wave2)'})

  fig, ax = plt.subplots(figsize=(8, 5))
  for group_label, color in [('低同学教育水平', '#E74C3C'), ('高同学教育水平', '#2ECC71')]:
    subset = trend_data[trend_data['group'] == group_label]
    ax.errorbar(subset['wave'], subset['mean'], yerr=subset['sem']*1.96,
                marker='o', color=color, label=group_label, capsize=4, linewidth=2, markersize=8)

  ax.set_xlabel('调查期')
  ax.set_ylabel('心理健康(z-score)')
  ax.set_title('平行趋势检验：不同处理组心理健康变化趋势')
  ax.set_xticks([0, 1])
  ax.set_xticklabels(['基期(Wave1)', '追踪(Wave2)'])
  ax.legend()
  ax.axhline(y=0, color='gray', linestyle='--', alpha=0.3)
  plt.tight_layout()
  plt.savefig(os.path.join(FIGURE_DIR, 'did_parallel_trend.png'), dpi=150, bbox_inches='tight')
  plt.close()
  print(f"   平行趋势图保存至: {FIGURE_DIR}/did_parallel_trend.png")

  # DID边际效应图
  fig, ax = plt.subplots(figsize=(8, 5))
  ses_labels = list(ses_did_results.keys())
  betas = [ses_did_results[s]['beta'] for s in ses_labels]
  ses_errors = [ses_did_results[s]['se'] for s in ses_labels]
  colors = ['#E74C3C', '#F39C12', '#2ECC71']

  x_pos = np.arange(len(ses_labels))
  ax.bar(x_pos, betas, yerr=[1.96 * se for se in ses_errors], color=colors,
         alpha=0.8, capsize=6, width=0.5)
  ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
  ax.set_xticks(x_pos)
  ax.set_xticklabels(ses_labels, fontsize=12)
  ax.set_ylabel('DID估计量 (Treat×Post)', fontsize=11)
  ax.set_title('不同SES水平的DID效应（95%置信区间）', fontsize=13)
  for i, (v, se) in enumerate(zip(betas, ses_errors)):
    ax.text(i, v + 1.96*se + 0.02, f'{v:.3f}', ha='center', fontsize=10,
            fontweight='bold', color=colors[i])
  plt.tight_layout()
  plt.savefig(os.path.join(FIGURE_DIR, 'did_marginal.png'), dpi=150, bbox_inches='tight')
  plt.close()
  print(f"   DID边际效应图保存至: {FIGURE_DIR}/did_marginal.png")

except Exception as e:
  print(f"   警告: 可视化失败: {e}")


# ============================================================
# 6. 保存结果表
# ============================================================
print("\n" + "=" * 60)
print("6. 保存结果表...")
print("=" * 60)

# DID基准回归
did_results = []
for name, model, x_names in [
  ('DID基本模型', m1, m1_x),
  ('DID+控制变量', m2, m2_x),
  ('连续DID', m3, m3_x)
]:
  # 交互项系数位置
  interact_idx = [i for i, n in enumerate(x_names) if 'x_' in n or 'interact' in n]
  interact_idx = interact_idx[0] + 1 if interact_idx else 1  # +1 for constant
  did_results.append({
    '模型': name,
    '交互项系数': f"{model.params[interact_idx]:.4f}",
    '标准误': f"({model.bse[interact_idx]:.4f})",
    'p值': f"{model.pvalues[interact_idx]:.4f}",
    'R²_within': f"{model.rsquared:.3f}",
    'N(学生)': f"{int(df_did['ids'].nunique())}",
    'N(观测)': f"{int(model.nobs)}",
  })

pd.DataFrame(did_results).to_csv(os.path.join(TABLE_DIR, 'did_baseline.csv'),
                                  index=False, encoding='utf-8-sig')
print(f"   DID基准回归保存至: {TABLE_DIR}/did_baseline.csv")

# 分SES组DID
ses_rows = []
for label, r in ses_did_results.items():
  ses_rows.append({
    'SES组': label,
    'DID估计量': f"{r['beta']:.4f}",
    '标准误': f"({r['se']:.4f})",
    'p值': f"{r['pval']:.4f}",
    'R²': f"{r['r2']:.3f}",
    'N(学生)': f"{r['n']}",
  })
pd.DataFrame(ses_rows).to_csv(os.path.join(TABLE_DIR, 'did_by_ses.csv'),
                               index=False, encoding='utf-8-sig')
print(f"   分SES组DID保存至: {TABLE_DIR}/did_by_ses.csv")

# 安慰剂检验
placebo_summary = {
  '检验方法': '随机分配处理状态 (500次)',
  '真实DID系数': f"{m1.params[1]:.4f}",
  '安慰剂系数均值': f"{placebo_results.mean():.4f}",
  '安慰剂系数标准差': f"{placebo_results.std():.4f}",
  'p值(真实在分布中位置)': f"{pct_gt_actual:.4f}",
  '结论': '安慰剂检验通过' if pct_gt_actual > 0.05 else '安慰剂检验未通过',
}
pd.DataFrame([placebo_summary]).to_csv(os.path.join(TABLE_DIR, 'did_placebo.csv'),
                                        index=False, encoding='utf-8-sig')
print(f"   安慰剂检验保存至: {TABLE_DIR}/did_placebo.csv")


# ============================================================
# 7. 结果摘要
# ============================================================
print("\n" + "=" * 60)
print("DID分析结果摘要")
print("=" * 60)
print(f"1. DID基本模型: β(treat×post)={m1.params[1]:.4f} (p={m1.pvalues[1]:.4f})")
print(f"2. 连续DID: β(cls_edu×wave)={m3.params[3]:.4f} (p={m3.pvalues[3]:.4f})")
print(f"3. SES非对称DID:")
for label, r in ses_did_results.items():
  print(f"   {label}: β={r['beta']:.4f} (p={r['pval']:.4f})")
print(f"4. 安慰剂检验: p={pct_gt_actual:.4f}")
print("\n✅ 脚本5完成: DID分析成功!")

# 清理临时变量
if 'cls_edu_x_wave' in df_did.columns:
  df_did.drop(columns=['cls_edu_x_wave'], inplace=True)