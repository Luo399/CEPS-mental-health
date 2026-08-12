"""
03_descriptive_stats.py
=========================
生成描述性统计表和相关可视化。

输出:
  - tablefile/descriptive_stats.csv   (描述性统计表)
  - tablefile/correlation_matrix.csv  (相关性矩阵)
  - figurefile/mental_dist.png        (心理健康分布图)
  - figurefile/mental_by_ses.png      (按SES分组的心理健康)
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

# ============================================================
# 1. 读取数据
# ============================================================
print("=" * 60)
print("1. 读取最终分析数据...")
print("=" * 60)

df = pd.read_stata(INPUT_FILE, convert_categoricals=False)
print(f"   数据: {df.shape[0]} 行 × {df.shape[1]} 列")

# 仅保留wave1样本用于截面分析
mask_w1 = df['grade'].isin([0, 2])
df_w1 = df[mask_w1].copy()
print(f"   Wave1截面样本: {len(df_w1)} 行")


# ============================================================
# 2. 描述性统计表
# ============================================================
print("\n" + "=" * 60)
print("2. 生成描述性统计表...")
print("=" * 60)

# 核心变量列表
core_vars = {
  # 因变量
  'mental_common_z': '心理健康(z-score)',
  'mental_poor': '心理健康不良(>P75)',
  # 核心自变量
  'cls_mean_max_education': '班级平均父母教育年限',
  'cls_sd_max_education': '班级父母教育年限标准差',
  'college_yn': '班级上过大学比例',
  # SES
  'ses_index': '家庭SES综合指数',
  'ses_low': '低SES(虚拟变量)',
  'ses_high': '高SES(虚拟变量)',
  # 中介变量
  'academic_pressure_z': '学业压力(z-score)',
  'parent_investment_z': '亲子投入(z-score)',
  # 控制变量
  'gender': '性别(女=1)',
  'hukou_type': '户口(非农=1)',
  'nationality': '民族(汉=1)',
  'yn_single_child': '独生子女',
  'tscore': '标准化成绩',
  # 班级层面
  'cls_mean_mental': '班级平均心理健康',
  'cls_sd_mental': '班级心理健康标准差',
}

# 生成描述性统计表
stats_rows = []
for var, label in core_vars.items():
  if var not in df.columns:
    continue
  s = df[var]
  n = s.notna().sum()
  stats_rows.append({
    '变量': label,
    '变量名': var,
    '样本量': n,
    '均值': f"{s.mean():.3f}",
    '标准差': f"{s.std():.3f}",
    '最小值': f"{s.min():.3f}",
    'P25': f"{s.quantile(0.25):.3f}",
    '中位数': f"{s.median():.3f}",
    'P75': f"{s.quantile(0.75):.3f}",
    '最大值': f"{s.max():.3f}",
  })

df_stats = pd.DataFrame(stats_rows)
df_stats.to_csv(os.path.join(TABLE_DIR, 'descriptive_stats.csv'), index=False, encoding='utf-8-sig')
print(f"   保存至: {TABLE_DIR}/descriptive_stats.csv")
print(f"   变量数: {len(df_stats)}")
print(df_stats[['变量', '样本量', '均值', '标准差']].to_string(index=False))


# ============================================================
# 3. 按SES分组的描述性统计
# ============================================================
print("\n" + "=" * 60)
print("3. 按SES分组统计...")
print("=" * 60)

# 使用wave1样本
df_w1 = df[df['grade'].isin([0, 2])].copy()
# 删除缺失
df_w1 = df_w1.dropna(subset=['ses_tercile', 'mental_common_z'])

# 按SES三分组统计
group_vars = ['mental_common_z', 'cls_mean_max_education', 'academic_pressure_z',
              'parent_investment_z', 'tscore', 'gender']
group_stats = df_w1.groupby('ses_tercile')[group_vars].agg(['mean', 'std', 'count'])
group_stats.to_csv(os.path.join(TABLE_DIR, 'by_ses_stats.csv'), encoding='utf-8-sig')
print(f"   保存至: {TABLE_DIR}/by_ses_stats.csv")
print(group_stats.to_string())


# ============================================================
# 4. 相关性矩阵
# ============================================================
print("\n" + "=" * 60)
print("4. 生成相关性矩阵...")
print("=" * 60)

corr_vars = ['mental_common_z', 'cls_mean_max_education', 'ses_index',
             'academic_pressure_z', 'parent_investment_z', 'tscore', 'gender']
existing_corr = [v for v in corr_vars if v in df.columns]
df_corr = df[existing_corr].dropna()

corr_matrix = df_corr.corr(method='pearson')
corr_matrix.to_csv(os.path.join(TABLE_DIR, 'correlation_matrix.csv'), encoding='utf-8-sig')
print(f"   保存至: {TABLE_DIR}/correlation_matrix.csv")
print(corr_matrix.round(3).to_string())


# ============================================================
# 5. 心理健康分布可视化
# ============================================================
print("\n" + "=" * 60)
print("5. 生成可视化图表...")
print("=" * 60)

try:
  import matplotlib
  matplotlib.use('Agg')
  import matplotlib.pyplot as plt

  # 设置中文字体
  plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
  plt.rcParams['axes.unicode_minus'] = False

  # 5a 心理健康分布直方图
  fig, axes = plt.subplots(1, 2, figsize=(12, 5))

  # 全样本分布
  axes[0].hist(df_w1['mental_common_z'].dropna(), bins=40, color='#4A90D9', alpha=0.7, edgecolor='white')
  axes[0].axvline(x=0, color='red', linestyle='--', alpha=0.5, label='均值')
  axes[0].set_xlabel('心理健康(z-score)')
  axes[0].set_ylabel('频数')
  axes[0].set_title('Wave1 心理健康分布')
  axes[0].legend()

  # 按SES分组分布
  for ses_val, color, label in [(1, '#E74C3C', '低SES'), (2, '#F39C12', '中SES'), (3, '#2ECC71', '高SES')]:
    subset = df_w1[df_w1['ses_tercile'] == ses_val]['mental_common_z'].dropna()
    axes[1].hist(subset, bins=30, alpha=0.5, color=color, label=label, density=True)
  axes[1].set_xlabel('心理健康(z-score)')
  axes[1].set_ylabel('密度')
  axes[1].set_title('按SES分组的心理健康分布')
  axes[1].legend()

  plt.tight_layout()
  plt.savefig(os.path.join(FIGURE_DIR, 'mental_dist.png'), dpi=150, bbox_inches='tight')
  plt.close()
  print(f"   心理健康分布图保存至: {FIGURE_DIR}/mental_dist.png")

  # 5b SES-Group × 心理健康柱状图
  fig, ax = plt.subplots(figsize=(8, 5))
  ses_groups = df_w1.groupby('ses_tercile')['mental_common_z'].agg(['mean', 'sem'])
  ses_groups.index = ['低SES', '中SES', '高SES']
  colors = ['#E74C3C', '#F39C12', '#2ECC71']
  ses_groups['mean'].plot(kind='bar', yerr=ses_groups['sem']*1.96, color=colors, alpha=0.8, ax=ax, capsize=4)
  ax.set_ylabel('心理健康(z-score, 越高越差)')
  ax.set_title('不同SES水平的心理健康状况')
  ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
  plt.tight_layout()
  plt.savefig(os.path.join(FIGURE_DIR, 'mental_by_ses.png'), dpi=150, bbox_inches='tight')
  plt.close()
  print(f"   SES分组心理健康图保存至: {FIGURE_DIR}/mental_by_ses.png")

  print("\n✅ 可视化图表生成完成!")

except ImportError:
  print("   警告: matplotlib未安装, 跳过可视化")
except Exception as e:
  print(f"   警告: 可视化生成失败: {e}")


# ============================================================
# 6. 输出分析样本概况
# ============================================================
print("\n" + "=" * 60)
print("6. 分析样本概况...")
print("=" * 60)

# 计算完整分析样本（无缺失）
analysis_vars = ['mental_common_z', 'cls_mean_max_education', 'ses_index',
                 'gender', 'hukou_type', 'nationality', 'grade']
complete = df_w1.dropna(subset=analysis_vars)
print(f"   Wave1总样本: {len(df_w1)}")
print(f"   完整分析样本: {len(complete)} ({len(complete)/len(df_w1)*100:.1f}%)")
print(f"   班级数: {df_w1['clsids'].nunique()}")
print(f"   学校数: {df_w1['schids'].nunique()}")
print(f"   低SES占比: {df_w1['ses_low'].mean()*100:.1f}%")
print(f"   高SES占比: {df_w1['ses_high'].mean()*100:.1f}%")

print("\n✅ 脚本3完成: 描述性统计生成成功!")