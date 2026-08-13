"""
07_mediation_analysis.py
========================
机制检验：中介效应分析

理论框架:
  cls_mean_edu → (学业压力/教养方式) → mental_health

中介路径:
  1. 学业压力路径: 高同学教育水平 → 增加学业压力 → 影响心理健康
  2. 教养方式路径: 高同学教育水平 → 改变教养方式 → 影响心理健康

方法:
  - Baron & Kenny 三步法
  - Sobel 检验（间接效应显著性）
  - 按SES分组的中介效应

输出:
  - tablefile/mediation_academic_pressure.csv (学业压力路径)
  - tablefile/mediation_parenting.csv          (教养方式路径)
  - tablefile/mediation_by_ses.csv             (分SES中介效应)
  - figurefile/mediation_path_diagram.png      (路径图)
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
# 辅助函数
# ============================================================
import statsmodels.api as sm
from scipy import stats as scipy_stats

def run_ols_std(y_name, x_names, data, cluster_var='schids'):
  """运行OLS回归并返回系数矩阵"""
  y = data[y_name]
  X = data[x_names]
  X = sm.add_constant(X)
  model = sm.OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': data[cluster_var]})
  return model

def sobel_test(a, b, se_a, se_b):
  """
  Sobel检验: 检验间接效应a*b是否显著
  z = a*b / sqrt(b²*se_a² + a²*se_b²)
  """
  indirect = a * b
  se_indirect = np.sqrt(b**2 * se_a**2 + a**2 * se_b**2)
  z = indirect / se_indirect if se_indirect > 0 else 0
  p = 2 * (1 - scipy_stats.norm.cdf(abs(z)))
  return indirect, se_indirect, z, p


# ============================================================
# 1. 读取数据
# ============================================================
print("=" * 60)
print("1. 读取数据...")
print("=" * 60)

df = pd.read_stata(INPUT_FILE, convert_categoricals=False)
print(f"   总数据: {df.shape[0]} 行 × {df.shape[1]} 列")

# 仅Wave1样本
df_w1 = df[df['grade'].isin([0, 2])].copy()
print(f"   Wave1样本: {len(df_w1)} 行")

# 标准化核心变量
df_w1['cls_mean_edu_z'] = (df_w1['cls_mean_max_education'] -
  df_w1['cls_mean_max_education'].mean()) / df_w1['cls_mean_max_education'].std()

# 中介变量标准化
for v in ['academic_pressure_raw', 'parent_rel_quality', 'parent_conflict',
          'parent_investment_raw']:
  if v in df_w1.columns and v + '_z' not in df_w1.columns:
    mean_v = df_w1[v].mean()
    std_v = df_w1[v].std()
    df_w1[v + '_z'] = (df_w1[v] - mean_v) / std_v

# 中介变量: 教养方式综合指数（正向：高值=好的教养方式）
# 如果parent_conflict存在，反转后与parent_rel_quality合并
df_w1['parenting_quality'] = df_w1['parent_rel_quality']
# 如果有parent_conflict，反转编码
if 'parent_conflict' in df_w1.columns:
  # 假设parent_conflict范围1-3或1-5，反转
  max_c = df_w1['parent_conflict'].max()
  min_c = df_w1['parent_conflict'].min()
  df_w1['parent_conflict_inv'] = (max_c + min_c) - df_w1['parent_conflict']
  # 综合教养质量 = 亲子关系质量 + 反转后的低冲突
  df_w1['parenting_quality'] = (df_w1['parent_rel_quality'] +
    df_w1['parent_conflict_inv']) / 2
  df_w1['parenting_quality_z'] = ((df_w1['parenting_quality'] -
    df_w1['parenting_quality'].mean()) / df_w1['parenting_quality'].std())

# 打印变量概况
mediators = ['academic_pressure_z', 'parenting_quality_z',
             'parent_rel_quality', 'parent_conflict', 'parent_investment_z']
for m in mediators:
  if m in df_w1.columns:
    valid = df_w1[m].notna().sum()
    print(f"   {m}: 非缺失={valid}, 均值={df_w1[m].mean():.3f}, std={df_w1[m].std():.3f}")


# ============================================================
# 2. 中介效应分析：学业压力路径
# ============================================================
print("\n" + "=" * 60)
print("2. 中介效应：学业压力路径")
print("   cls_mean_edu → academic_pressure → mental_health")
print("=" * 60)

# 准备完整样本
med1_vars = ['mental_common_z', 'cls_mean_edu_z', 'academic_pressure_z'] + CONTROLS
df_med1 = df_w1.dropna(subset=med1_vars).copy()
print(f"   完整样本: {len(df_med1)} 行")

# Step 1: X → Y (总效应)
m1_step1 = run_ols_std('mental_common_z', ['cls_mean_edu_z'] + CONTROLS, df_med1)
c_total = m1_step1.params['cls_mean_edu_z']
print(f"\n   Step 1 (X→Y): c = {c_total:.4f}, p = {m1_step1.pvalues['cls_mean_edu_z']:.4f}")

# Step 2: X → M (自变量→中介变量)
m1_step2 = run_ols_std('academic_pressure_z', ['cls_mean_edu_z'] + CONTROLS, df_med1)
a = m1_step2.params['cls_mean_edu_z']
se_a = m1_step2.bse['cls_mean_edu_z']
print(f"   Step 2 (X→M): a = {a:.4f}, se = {se_a:.4f}, p = {m1_step2.pvalues['cls_mean_edu_z']:.4f}")

# Step 3: X + M → Y (加入中介变量)
m1_step3 = run_ols_std('mental_common_z',
  ['cls_mean_edu_z', 'academic_pressure_z'] + CONTROLS, df_med1)
c_prime = m1_step3.params['cls_mean_edu_z']
b = m1_step3.params['academic_pressure_z']
se_b = m1_step3.bse['academic_pressure_z']
print(f"   Step 3 (X+M→Y): c' = {c_prime:.4f}, b = {b:.4f}, p(b) = {m1_step3.pvalues['academic_pressure_z']:.4f}")

# Sobel检验
indirect, se_indirect, z_sobel, p_sobel = sobel_test(a, b, se_a, se_b)
print(f"\n   Sobel检验: 间接效应 = {indirect:.4f}, se = {se_indirect:.4f}, z = {z_sobel:.3f}, p = {p_sobel:.4f}")

# 中介比例
total_effect = c_total
mediation_pct = indirect / total_effect * 100 if total_effect != 0 else 0
print(f"   中介比例: {mediation_pct:.1f}% ({indirect:.4f} / {total_effect:.4f})")

# 存储结果
med1_results = {
  '中介路径': '学业压力',
  '总效应(c)': f"{c_total:.4f}",
  '间接效应(a×b)': f"{indirect:.4f}",
  '间接效应se': f"({se_indirect:.4f})",
  '直接效应(c\')': f"{c_prime:.4f}",
  'Sobel z': f"{z_sobel:.3f}",
  'Sobel p': f"{p_sobel:.4f}",
  '中介比例%': f"{mediation_pct:.1f}",
  'N': f"{len(df_med1)}",
}


# ============================================================
# 3. 中介效应分析：教养方式路径
# ============================================================
print("\n" + "=" * 60)
print("3. 中介效应：教养方式路径")
print("   cls_mean_edu → parenting_quality → mental_health")
print("=" * 60)

# 3a. 亲子关系质量
med2_vars = ['mental_common_z', 'cls_mean_edu_z', 'parenting_quality_z'] + CONTROLS
df_med2 = df_w1.dropna(subset=med2_vars).copy()
print(f"   教养质量样本: {len(df_med2)} 行")

m2_step1 = run_ols_std('mental_common_z', ['cls_mean_edu_z'] + CONTROLS, df_med2)
m2_step2 = run_ols_std('parenting_quality_z', ['cls_mean_edu_z'] + CONTROLS, df_med2)
m2_step3 = run_ols_std('mental_common_z',
  ['cls_mean_edu_z', 'parenting_quality_z'] + CONTROLS, df_med2)

a2 = m2_step2.params['cls_mean_edu_z']
se_a2 = m2_step2.bse['cls_mean_edu_z']
b2 = m2_step3.params['parenting_quality_z']
se_b2 = m2_step3.bse['parenting_quality_z']
c_total2 = m2_step1.params['cls_mean_edu_z']
c_prime2 = m2_step3.params['cls_mean_edu_z']
indirect2, se_indirect2, z2, p2 = sobel_test(a2, b2, se_a2, se_b2)
med_pct2 = indirect2 / c_total2 * 100 if c_total2 != 0 else 0

print(f"   Step 1 (X→Y): c = {c_total2:.4f}, p = {m2_step1.pvalues['cls_mean_edu_z']:.4f}")
print(f"   Step 2 (X→M): a = {a2:.4f}, p = {m2_step2.pvalues['cls_mean_edu_z']:.4f}")
print(f"   Step 3 (M→Y): b = {b2:.4f}, p = {m2_step3.pvalues['parenting_quality_z']:.4f}")
print(f"   Sobel: 间接效应 = {indirect2:.4f}, z = {z2:.3f}, p = {p2:.4f}, 中介比例 = {med_pct2:.1f}%")

# 3b. 父母教育投资
med3_vars = ['mental_common_z', 'cls_mean_edu_z', 'parent_investment_z'] + CONTROLS
df_med3 = df_w1.dropna(subset=med3_vars).copy()
print(f"\n   教育投资样本: {len(df_med3)} 行")

m3_step1 = run_ols_std('mental_common_z', ['cls_mean_edu_z'] + CONTROLS, df_med3)
m3_step2 = run_ols_std('parent_investment_z', ['cls_mean_edu_z'] + CONTROLS, df_med3)
m3_step3 = run_ols_std('mental_common_z',
  ['cls_mean_edu_z', 'parent_investment_z'] + CONTROLS, df_med3)

a3 = m3_step2.params['cls_mean_edu_z']
se_a3 = m3_step2.bse['cls_mean_edu_z']
b3 = m3_step3.params['parent_investment_z']
se_b3 = m3_step3.bse['parent_investment_z']
c_total3 = m3_step1.params['cls_mean_edu_z']
c_prime3 = m3_step3.params['cls_mean_edu_z']
indirect3, se_indirect3, z3, p3 = sobel_test(a3, b3, se_a3, se_b3)
med_pct3 = indirect3 / c_total3 * 100 if c_total3 != 0 else 0

print(f"   Step 1 (X→Y): c = {c_total3:.4f}, p = {m3_step1.pvalues['cls_mean_edu_z']:.4f}")
print(f"   Step 2 (X→M): a = {a3:.4f}, p = {m3_step2.pvalues['cls_mean_edu_z']:.4f}")
print(f"   Step 3 (M→Y): b = {b3:.4f}, p = {m3_step3.pvalues['parent_investment_z']:.4f}")
print(f"   Sobel: 间接效应 = {indirect3:.4f}, z = {z3:.3f}, p = {p3:.4f}, 中介比例 = {med_pct3:.1f}%")


# ============================================================
# 4. 分SES组的中介效应
# ============================================================
print("\n" + "=" * 60)
print("4. 分SES组的中介效应...")
print("=" * 60)

ses_mediation_results = []
for ses_val, ses_label in [(0, '低SES'), (1, '中SES'), (2, '高SES')]:
  for path_name, m_vars, df_m in [
    ('学业压力', med1_vars, df_med1),
    ('教养质量', med2_vars, df_med2),
    ('教育投资', med3_vars, df_med3),
  ]:
    subset = df_m[df_m['ses_tercile'] == ses_val]
    if len(subset) < 100:
      continue
    # X→M
    step2 = run_ols_std(m_vars[2], ['cls_mean_edu_z'] + CONTROLS, subset)
    a_s = step2.params['cls_mean_edu_z']
    se_a_s = step2.bse['cls_mean_edu_z']
    # X+M→Y
    step3 = run_ols_std('mental_common_z',
      ['cls_mean_edu_z', m_vars[2]] + CONTROLS, subset)
    b_s = step3.params[m_vars[2]]
    se_b_s = step3.bse[m_vars[2]]
    # Sobel
    ind_s, se_ind_s, z_s, p_s = sobel_test(a_s, b_s, se_a_s, se_b_s)
    # 总效应
    step1 = run_ols_std('mental_common_z', ['cls_mean_edu_z'] + CONTROLS, subset)
    c_s = step1.params['cls_mean_edu_z']
    med_pct_s = ind_s / c_s * 100 if c_s != 0 else 0

    ses_mediation_results.append({
      'SES组': ses_label, '中介路径': path_name,
      '总效应(c)': f"{c_s:.4f}",
      '间接效应(a×b)': f"{ind_s:.4f}",
      'Sobel z': f"{z_s:.3f}",
      'Sobel p': f"{p_s:.4f}",
      '中介比例%': f"{med_pct_s:.1f}",
      'N': f"{len(subset)}",
    })
    print(f"   {ses_label} - {path_name}: 间接效应={ind_s:.4f}, z={z_s:.3f}, p={p_s:.4f}")


# ============================================================
# 5. 路径图可视化
# ============================================================
print("\n" + "=" * 60)
print("5. 路径图可视化...")
print("=" * 60)

try:
  import matplotlib
  matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
  plt.rcParams['axes.unicode_minus'] = False

  fig, axes = plt.subplots(1, 3, figsize=(15, 5))

  paths = [
    ('学业压力路径', 'academic_pressure_z', a, b, c_total, c_prime, indirect, p_sobel, med1_results),
    ('教养质量路径', 'parenting_quality_z', a2, b2, c_total2, c_prime2, indirect2, p2, None),
    ('教育投资路径', 'parent_investment_z', a3, b3, c_total3, c_prime3, indirect3, p3, None),
  ]

  for idx, (title, m_name, a_val, b_val, c_val, cp_val, ind_val, p_val, _) in enumerate(paths):
    ax = axes[idx]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # 节点
    ax.text(0.1, 0.5, '同学教育\n水平', ha='center', va='center',
            fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#4A90D9', alpha=0.3))
    ax.text(0.9, 0.5, '心理健康', ha='center', va='center',
            fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#E74C3C', alpha=0.3))
    ax.text(0.5, 0.8, m_name.replace('_z', '').replace('_', ' '),
            ha='center', va='center', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#F39C12', alpha=0.3))

    # 路径线
    # X→M
    ax.annotate('', xy=(0.35, 0.75), xytext=(0.2, 0.55),
                arrowprops=dict(arrowstyle='->', color='#2ECC71', lw=2))
    ax.text(0.25, 0.7, f'a={a_val:.3f}', fontsize=8, color='#2ECC71')
    # M→Y
    ax.annotate('', xy=(0.75, 0.55), xytext=(0.6, 0.75),
                arrowprops=dict(arrowstyle='->', color='#2ECC71', lw=2))
    ax.text(0.65, 0.65, f'b={b_val:.3f}', fontsize=8, color='#2ECC71')
    # X→Y (直接效应)
    ax.annotate('', xy=(0.8, 0.45), xytext=(0.2, 0.45),
                arrowprops=dict(arrowstyle='->', color='#E74C3C', lw=1.5, linestyle='dashed'))
    ax.text(0.45, 0.4, f"c'={cp_val:.3f}", fontsize=8, color='#E74C3C')

    # 标题
    ax.set_title(f'{title}\n间接效应={ind_val:.4f}\np={p_val:.4f}', fontsize=11, fontweight='bold')

  plt.tight_layout()
  plt.savefig(os.path.join(FIGURE_DIR, 'mediation_path_diagram.png'), dpi=150, bbox_inches='tight')
  plt.close()
  print(f"   路径图保存至: {FIGURE_DIR}/mediation_path_diagram.png")

except Exception as e:
  print(f"   警告: 可视化失败: {e}")


# ============================================================
# 6. 保存结果表
# ============================================================
print("\n" + "=" * 60)
print("6. 保存结果表...")
print("=" * 60)

# 学业压力中介
med1_rows = [med1_results]
pd.DataFrame(med1_rows).to_csv(
  os.path.join(TABLE_DIR, 'mediation_academic_pressure.csv'),
  index=False, encoding='utf-8-sig')
print(f"   学业压力中介结果保存至: {TABLE_DIR}/mediation_academic_pressure.csv")

# 教养方式中介
med2_rows = [{
  '中介路径': '教养质量',
  '总效应(c)': f"{c_total2:.4f}",
  '间接效应(a×b)': f"{indirect2:.4f}",
  '间接效应se': f"({se_indirect2:.4f})",
  '直接效应(c\')': f"{c_prime2:.4f}",
  'Sobel z': f"{z2:.3f}",
  'Sobel p': f"{p2:.4f}",
  '中介比例%': f"{med_pct2:.1f}",
  'N': f"{len(df_med2)}",
}, {
  '中介路径': '教育投资',
  '总效应(c)': f"{c_total3:.4f}",
  '间接效应(a×b)': f"{indirect3:.4f}",
  '间接效应se': f"({se_indirect3:.4f})",
  '直接效应(c\')': f"{c_prime3:.4f}",
  'Sobel z': f"{z3:.3f}",
  'Sobel p': f"{p3:.4f}",
  '中介比例%': f"{med_pct3:.1f}",
  'N': f"{len(df_med3)}",
}]
pd.DataFrame(med2_rows).to_csv(
  os.path.join(TABLE_DIR, 'mediation_parenting.csv'),
  index=False, encoding='utf-8-sig')
print(f"   教养方式中介结果保存至: {TABLE_DIR}/mediation_parenting.csv")

# 分SES组中介
pd.DataFrame(ses_mediation_results).to_csv(
  os.path.join(TABLE_DIR, 'mediation_by_ses.csv'),
  index=False, encoding='utf-8-sig')
print(f"   分SES组中介结果保存至: {TABLE_DIR}/mediation_by_ses.csv")


# ============================================================
# 7. 结果摘要
# ============================================================
print("\n" + "=" * 60)
print("中介效应分析摘要")
print("=" * 60)
print(f"1. 学业压力路径:")
print(f"   间接效应 = {indirect:.4f} (Sobel z={z_sobel:.3f}, p={p_sobel:.4f})")
print(f"   中介比例 = {mediation_pct:.1f}%")
print(f"2. 教养质量路径:")
print(f"   间接效应 = {indirect2:.4f} (Sobel z={z2:.3f}, p={p2:.4f})")
print(f"   中介比例 = {med_pct2:.1f}%")
print(f"3. 教育投资路径:")
print(f"   间接效应 = {indirect3:.4f} (Sobel z={z3:.3f}, p={p3:.4f})")
print(f"   中介比例 = {med_pct3:.1f}%")
print("\n✅ 脚本7完成: 中介效应分析成功!")