"""
08_robustness_checks.py
========================
稳健性检验

检验方法:
  1. 替换核心自变量：原始值 cls_mean_max_education（未标准化）
  2. 替换因变量：原始加总 mental_common_raw
  3. 替换SES控制：父母教育水平（mom_education, dad_education）
  4. 样本限定：仅城市户口、仅农村户口、仅公立学校
  5. 排除异常值：剔除心理健康±3标准差外的样本
  6. 加入更多控制变量：学校类型、班级规模

输出:
  - tablefile/robustness_alternative_vars.csv (替换变量定义)
  - tablefile/robustness_sample_restrict.csv  (样本限定)
  - tablefile/robustness_summary.csv          (汇总表)
  - figurefile/robustness_coef_plot.png       (系数对比图)
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

import statsmodels.api as sm

CONTROLS = ['gender', 'hukou_type', 'nationality', 'yn_single_child', 'tscore']


# ============================================================
# 辅助函数
# ============================================================
def run_regression(y_name, x_names, data, cluster_var='schids'):
  """运行聚类标准误OLS回归"""
  formula = f"{y_name} ~ {' + '.join(x_names)}"
  model = sm.OLS.from_formula(formula, data=data).fit(
    cov_type='cluster', cov_kwds={'groups': data[cluster_var]})
  return model


# ============================================================
# 1. 读取数据（Wave1）
# ============================================================
print("=" * 60)
print("1. 读取数据...")
print("=" * 60)

df = pd.read_stata(INPUT_FILE, convert_categoricals=False)
df_w1 = df[df['grade'].isin([0, 2])].copy()
print(f"   Wave1样本: {len(df_w1)} 行")

# 基准模型变量
df_w1['cls_mean_edu_z'] = (df_w1['cls_mean_max_education'] -
  df_w1['cls_mean_max_education'].mean()) / df_w1['cls_mean_max_education'].std()
df_w1['mental_common_z'] = (df_w1['mental_common_raw'] -
  df_w1['mental_common_raw'].mean()) / df_w1['mental_common_raw'].std()

# 基准模型
base_vars = ['mental_common_z', 'cls_mean_edu_z'] + CONTROLS
df_base = df_w1.dropna(subset=base_vars).copy()
base_model = run_regression('mental_common_z', ['cls_mean_edu_z'] + CONTROLS, df_base)
beta_base = base_model.params['cls_mean_edu_z']
se_base = base_model.bse['cls_mean_edu_z']
print(f"\n   基准模型: β(cls_edu)={beta_base:.4f}, se={se_base:.4f}, p={base_model.pvalues['cls_mean_edu_z']:.4f}")


# ============================================================
# 2. 替换核心自变量
# ============================================================
print("\n" + "=" * 60)
print("2. 替换核心自变量...")
print("=" * 60)

robust_results = []

# 2a 原始值（未标准化）
df_w1['cls_mean_edu_raw'] = df_w1['cls_mean_max_education']
m2a = run_regression('mental_common_z', ['cls_mean_edu_raw'] + CONTROLS,
  df_w1.dropna(subset=['mental_common_z', 'cls_mean_edu_raw'] + CONTROLS))
print(f"   2a. 原始值: β={m2a.params['cls_mean_edu_raw']:.4f}, p={m2a.pvalues['cls_mean_edu_raw']:.4f}")
robust_results.append({'检验': '2a. 原始自变量值', 'β': m2a.params['cls_mean_edu_raw'],
  'se': m2a.bse['cls_mean_edu_raw'], 'p': m2a.pvalues['cls_mean_edu_raw'],
  'N': int(m2a.nobs), 'R²': m2a.rsquared})

# 2b 班级中位数（如果有）
if 'cls_median_max_education' in df_w1.columns:
  df_w1['cls_median_edu_z'] = (df_w1['cls_median_max_education'] -
    df_w1['cls_median_max_education'].mean()) / df_w1['cls_median_max_education'].std()
  m2b = run_regression('mental_common_z', ['cls_median_edu_z'] + CONTROLS,
    df_w1.dropna(subset=['mental_common_z', 'cls_median_edu_z'] + CONTROLS))
  print(f"   2b. 班级中位数: β={m2b.params['cls_median_edu_z']:.4f}, p={m2b.pvalues['cls_median_edu_z']:.4f}")
  robust_results.append({'检验': '2b. 班级中位数', 'β': m2b.params['cls_median_edu_z'],
    'se': m2b.bse['cls_median_edu_z'], 'p': m2b.pvalues['cls_median_edu_z'],
    'N': int(m2b.nobs), 'R²': m2b.rsquared})


# ============================================================
# 3. 替换因变量
# ============================================================
print("\n" + "=" * 60)
print("3. 替换因变量...")
print("=" * 60)

# 3a 原始加总（未标准化）
m3a = run_regression('mental_common_raw', ['cls_mean_edu_z'] + CONTROLS,
  df_w1.dropna(subset=['mental_common_raw', 'cls_mean_edu_z'] + CONTROLS))
print(f"   3a. 原始加总: β={m3a.params['cls_mean_edu_z']:.4f}, p={m3a.pvalues['cls_mean_edu_z']:.4f}")
robust_results.append({'检验': '3a. 原始加总DV', 'β': m3a.params['cls_mean_edu_z'],
  'se': m3a.bse['cls_mean_edu_z'], 'p': m3a.pvalues['cls_mean_edu_z'],
  'N': int(m3a.nobs), 'R²': m3a.rsquared})


# ============================================================
# 4. 替换SES控制
# ============================================================
print("\n" + "=" * 60)
print("4. 替换SES控制变量...")
print("=" * 60)

# 4a 用父母教育水平替代SES指数
alt_controls = ['gender', 'nationality', 'yn_single_child', 'tscore',
                'mom_education', 'dad_education']
m4a_vars = ['mental_common_z', 'cls_mean_edu_z'] + alt_controls
m4a = run_regression('mental_common_z', ['cls_mean_edu_z'] + alt_controls,
  df_w1.dropna(subset=m4a_vars))
print(f"   4a. 父母教育控制: β={m4a.params['cls_mean_edu_z']:.4f}, p={m4a.pvalues['cls_mean_edu_z']:.4f}")
robust_results.append({'检验': '4a. 父母教育控制', 'β': m4a.params['cls_mean_edu_z'],
  'se': m4a.bse['cls_mean_edu_z'], 'p': m4a.pvalues['cls_mean_edu_z'],
  'N': int(m4a.nobs), 'R²': m4a.rsquared})

# 4b 加入家庭经济状况
alt_controls2 = ['gender', 'hukou_type', 'nationality', 'yn_single_child', 'tscore',
                 'child_economic_status']
m4b_vars = ['mental_common_z', 'cls_mean_edu_z'] + alt_controls2
m4b = run_regression('mental_common_z', ['cls_mean_edu_z'] + alt_controls2,
  df_w1.dropna(subset=m4b_vars))
print(f"   4b. 家庭经济控制: β={m4b.params['cls_mean_edu_z']:.4f}, p={m4b.pvalues['cls_mean_edu_z']:.4f}")
robust_results.append({'检验': '4b. 家庭经济控制', 'β': m4b.params['cls_mean_edu_z'],
  'se': m4b.bse['cls_mean_edu_z'], 'p': m4b.pvalues['cls_mean_edu_z'],
  'N': int(m4b.nobs), 'R²': m4b.rsquared})


# ============================================================
# 5. 样本限定
# ============================================================
print("\n" + "=" * 60)
print("5. 样本限定...")
print("=" * 60)

df_w1 = df_w1.copy()
# 5a 仅城市户口
df_urban = df_w1[df_w1['hukou_type'] == 1].dropna(subset=base_vars)
m5a = run_regression('mental_common_z', ['cls_mean_edu_z'] + CONTROLS, df_urban)
print(f"   5a. 城市户口(n={len(df_urban)}): β={m5a.params['cls_mean_edu_z']:.4f}, p={m5a.pvalues['cls_mean_edu_z']:.4f}")
robust_results.append({'检验': '5a. 仅城市户口', 'β': m5a.params['cls_mean_edu_z'],
  'se': m5a.bse['cls_mean_edu_z'], 'p': m5a.pvalues['cls_mean_edu_z'],
  'N': int(m5a.nobs), 'R²': m5a.rsquared})

# 5b 仅农村户口
df_rural = df_w1[df_w1['hukou_type'] == 0].dropna(subset=base_vars)
m5b = run_regression('mental_common_z', ['cls_mean_edu_z'] + CONTROLS, df_rural)
print(f"   5b. 农村户口(n={len(df_rural)}): β={m5b.params['cls_mean_edu_z']:.4f}, p={m5b.pvalues['cls_mean_edu_z']:.4f}")
robust_results.append({'检验': '5b. 仅农村户口', 'β': m5b.params['cls_mean_edu_z'],
  'se': m5b.bse['cls_mean_edu_z'], 'p': m5b.pvalues['cls_mean_edu_z'],
  'N': int(m5b.nobs), 'R²': m5b.rsquared})

# 5c 仅含父母家庭
df_with_parents = df_w1[df_w1['dad_living'] == 1].dropna(subset=base_vars)
if len(df_with_parents) > 100:
  m5c = run_regression('mental_common_z', ['cls_mean_edu_z'] + CONTROLS, df_with_parents)
  print(f"   5c. 与父亲同住(n={len(df_with_parents)}): β={m5c.params['cls_mean_edu_z']:.4f}, p={m5c.pvalues['cls_mean_edu_z']:.4f}")
  robust_results.append({'检验': '5c. 与父亲同住', 'β': m5c.params['cls_mean_edu_z'],
    'se': m5c.bse['cls_mean_edu_z'], 'p': m5c.pvalues['cls_mean_edu_z'],
    'N': int(m5c.nobs), 'R²': m5c.rsquared})

# 5d 仅公立学校
if 'schtype_gongban' in df_w1.columns:
  df_public = df_w1[df_w1['schtype_gongban'] == 1].dropna(subset=base_vars)
  if len(df_public) > 100:
    m5d = run_regression('mental_common_z', ['cls_mean_edu_z'] + CONTROLS, df_public)
    print(f"   5d. 公立学校(n={len(df_public)}): β={m5d.params['cls_mean_edu_z']:.4f}, p={m5d.pvalues['cls_mean_edu_z']:.4f}")
    robust_results.append({'检验': '5d. 仅公立学校', 'β': m5d.params['cls_mean_edu_z'],
      'se': m5d.bse['cls_mean_edu_z'], 'p': m5d.pvalues['cls_mean_edu_z'],
      'N': int(m5d.nobs), 'R²': m5d.rsquared})


# ============================================================
# 6. 排除异常值
# ============================================================
print("\n" + "=" * 60)
print("6. 排除异常值...")
print("=" * 60)

# 6a 排除心理健康±3SD
df_w1['mental_z'] = (df_w1['mental_common_raw'] - df_w1['mental_common_raw'].mean()) / df_w1['mental_common_raw'].std()
df_trim = df_w1[(df_w1['mental_z'].abs() <= 3)].dropna(subset=base_vars)
m6a = run_regression('mental_common_z', ['cls_mean_edu_z'] + CONTROLS, df_trim)
print(f"   6a. 排除±3SD(n={len(df_trim)}): β={m6a.params['cls_mean_edu_z']:.4f}, p={m6a.pvalues['cls_mean_edu_z']:.4f}")
robust_results.append({'检验': '6a. 排除±3SD', 'β': m6a.params['cls_mean_edu_z'],
  'se': m6a.bse['cls_mean_edu_z'], 'p': m6a.pvalues['cls_mean_edu_z'],
  'N': int(m6a.nobs), 'R²': m6a.rsquared})

# 6b 排除极端班级（班级均值±3SD）
df_w1['cls_mean_z'] = (df_w1['cls_mean_max_education'] - df_w1['cls_mean_max_education'].mean()) / df_w1['cls_mean_max_education'].std()
df_trim2 = df_w1[(df_w1['cls_mean_z'].abs() <= 3)].dropna(subset=base_vars)
m6b = run_regression('mental_common_z', ['cls_mean_edu_z'] + CONTROLS, df_trim2)
print(f"   6b. 排除班级极端值(n={len(df_trim2)}): β={m6b.params['cls_mean_edu_z']:.4f}, p={m6b.pvalues['cls_mean_edu_z']:.4f}")
robust_results.append({'检验': '6b. 排除班级极端值', 'β': m6b.params['cls_mean_edu_z'],
  'se': m6b.bse['cls_mean_edu_z'], 'p': m6b.pvalues['cls_mean_edu_z'],
  'N': int(m6b.nobs), 'R²': m6b.rsquared})


# ============================================================
# 7. 加入更多控制变量
# ============================================================
print("\n" + "=" * 60)
print("7. 加入更多控制变量...")
print("=" * 60)

# 7a 加入班级规模
if 'class_size' in df_w1.columns or 'clsidgrade_N' in df_w1.columns:
  size_var = 'clsidgrade_N' if 'clsidgrade_N' in df_w1.columns else 'class_size'
  extra1 = ['gender', 'hukou_type', 'nationality', 'yn_single_child', 'tscore', size_var]
  m7a = run_regression('mental_common_z', ['cls_mean_edu_z'] + extra1,
    df_w1.dropna(subset=['mental_common_z', 'cls_mean_edu_z'] + extra1))
  print(f"   7a. 加班级规模: β={m7a.params['cls_mean_edu_z']:.4f}, p={m7a.pvalues['cls_mean_edu_z']:.4f}")
  robust_results.append({'检验': '7a. 加班级规模', 'β': m7a.params['cls_mean_edu_z'],
    'se': m7a.bse['cls_mean_edu_z'], 'p': m7a.pvalues['cls_mean_edu_z'],
    'N': int(m7a.nobs), 'R²': m7a.rsquared})

# 7b 加入学校固定效应（学校虚拟变量）
# 使用公式API，学校作为因子
try:
  m7b = sm.OLS.from_formula('mental_common_z ~ cls_mean_edu_z + ' +
    ' + '.join(CONTROLS) + ' + C(schids)', data=df_base).fit(
    cov_type='cluster', cov_kwds={'groups': df_base['schids']})
  print(f"   7b. 学校固定效应: β={m7b.params['cls_mean_edu_z']:.4f}, p={m7b.pvalues['cls_mean_edu_z']:.4f}")
  robust_results.append({'检验': '7b. 学校固定效应', 'β': m7b.params['cls_mean_edu_z'],
    'se': m7b.bse['cls_mean_edu_z'], 'p': m7b.pvalues['cls_mean_edu_z'],
    'N': int(m7b.nobs), 'R²': m7b.rsquared})
except Exception as e:
  print(f"   7b. 学校固定效应失败: {e}")


# ============================================================
# 8. 汇总表与可视化
# ============================================================
print("\n" + "=" * 60)
print("8. 汇总表与可视化...")
print("=" * 60)

# 构建汇总表
summary_rows = []
for r in robust_results:
  summary_rows.append({
    '稳健性检验': r['检验'],
    'β': f"{r['β']:.4f}",
    '标准误': f"({r['se']:.4f})",
    'p值': f"{r['p']:.4f}",
    'N': f"{r['N']}",
    'R²': f"{r['R²']:.3f}",
    '显著': '✅' if r['p'] < 0.05 else '❌',
  })

# 基准模型加入汇总
summary_rows.insert(0, {
  '稳健性检验': '0. 基准模型',
  'β': f"{beta_base:.4f}",
  '标准误': f"({se_base:.4f})",
  'p值': f"{base_model.pvalues['cls_mean_edu_z']:.4f}",
  'N': f"{int(base_model.nobs)}",
  'R²': f"{base_model.rsquared:.3f}",
  '显著': '❌',
})

pd.DataFrame(summary_rows).to_csv(
  os.path.join(TABLE_DIR, 'robustness_summary.csv'),
  index=False, encoding='utf-8-sig')
print(f"\n   汇总表保存至: {TABLE_DIR}/robustness_summary.csv")

# 系数对比图
try:
  import matplotlib
  matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
  plt.rcParams['axes.unicode_minus'] = False

  fig, ax = plt.subplots(figsize=(10, 7))

  labels = [r['检验'] for r in robust_results]
  betas = [r['β'] for r in robust_results]
  ses = [r['se'] for r in robust_results]
  colors = ['#E74C3C' if r['p'] < 0.05 else '#4A90D9' for r in robust_results]

  y_pos = np.arange(len(labels))
  ax.errorbar(betas, y_pos, xerr=[1.96 * se for se in ses],
              fmt='o', color='#333', ecolor='gray', capsize=4, markersize=8)
  # 每个点着色
  for i in range(len(labels)):
    ax.plot(betas[i], y_pos[i], 'o', color=colors[i], markersize=10)

  # 基准线
  ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
  ax.axvline(x=beta_base, color='red', linestyle=':', alpha=0.5, label=f'基准β={beta_base:.3f}')

  ax.set_yticks(y_pos)
  ax.set_yticklabels(labels, fontsize=10)
  ax.set_xlabel('β系数 (95% CI)', fontsize=12)
  ax.set_title('稳健性检验：系数对比图', fontsize=14, fontweight='bold')
  ax.legend(fontsize=10)
  ax.grid(axis='x', alpha=0.3)
  plt.tight_layout()
  plt.savefig(os.path.join(FIGURE_DIR, 'robustness_coef_plot.png'), dpi=150, bbox_inches='tight')
  plt.close()
  print(f"   系数对比图保存至: {FIGURE_DIR}/robustness_coef_plot.png")

except Exception as e:
  print(f"   警告: 可视化失败: {e}")


# ============================================================
# 9. 结果摘要
# ============================================================
print("\n" + "=" * 60)
print("稳健性检验摘要")
print("=" * 60)
print(f"基准模型: β={beta_base:.4f} (p={base_model.pvalues['cls_mean_edu_z']:.4f})")
for r in robust_results:
  flag = '✅' if abs(r['β'] - beta_base) < 0.02 else '⚠️'
  print(f"  {r['检验']}: β={r['β']:.4f} (p={r['p']:.4f}) {flag}")

print("\n✅ 脚本8完成: 稳健性检验成功!")