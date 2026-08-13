"""
02_construct_variables.py
=========================
在合并情绪题的基础上，进一步：
  1. 合并学业压力变量 (b32, w2a29)
  2. 合并教养方式变量 (b22-b24, w2a18-w2a21)
  3. 构造家庭SES综合指数
  4. 构造班级层面心理健康不平等指标
  5. 保存最终分析数据集

输入:
  - data/analysis_data.dta  (脚本1输出)
  - CEPS/2013-2014/cepsw1studentCN.dta
  - CEPS/2014-2015/cepsw2studentCN.dta

输出:
  - data/analysis_final.dta  (最终分析数据集)
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
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'analysis_data.dta')
WAVE1_DATA = os.path.join(BASE_DIR, 'CEPS', '2013-2014', 'cepsw1studentCN.dta')
WAVE2_DATA = os.path.join(BASE_DIR, 'CEPS', '2014-2015', 'cepsw2studentCN.dta')
OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'analysis_final.dta')

# 辅助函数: 按wave合并（使用merge而非update以支持新列）
def merge_wave_vars(df_main, df_wave, merge_cols, wave_value, var_names):
  """按wave值合并变量，返回合并后的完整df"""
  df_wave_sub = df_wave[merge_cols].copy()
  if wave_value == 1:
    mask = df_main['grade'].isin([0, 2])
  else:
    mask = df_main['grade'] == 1
  # 仅对wave子集merge
  df_main_wave = df_main[mask].drop(columns=[c for c in var_names if c in df_main.columns], errors='ignore')
  df_main_wave = df_main_wave.merge(df_wave_sub, on='ids', how='left')
  # 将合并结果写回完整df
  df_main_nonwave = df_main[~mask]
  df_combined = pd.concat([df_main_wave, df_main_nonwave], axis=0, ignore_index=True)
  return df_combined


# ============================================================
# 1. 读取合并后数据
# ============================================================
print("=" * 60)
print("1. 读取合并后数据...")
print("=" * 60)

df = pd.read_stata(INPUT_FILE, convert_categoricals=False)
print(f"   数据: {df.shape[0]} 行 × {df.shape[1]} 列")


# ============================================================
# 2. 合并学业压力变量
# ============================================================
print("\n" + "=" * 60)
print("2. 合并学业压力变量...")
print("=" * 60)

# 2a Wave1: b32 (1=没有压力, 5=压力很大)
df_w1 = pd.read_stata(WAVE1_DATA, convert_categoricals=False)
df = merge_wave_vars(df, df_w1, ['ids', 'b32'], wave_value=1, var_names=['b32'])
mask_w1 = df['grade'].isin([0, 2])
n_w1 = df.loc[mask_w1, 'b32'].notna().sum()
print(f"   Wave1 b32匹配: {n_w1}/{mask_w1.sum()} ({n_w1/mask_w1.sum()*100:.1f}%)")

# 2b Wave2: w2a29 (1=没有压力, 5=压力很大)
df_w2 = pd.read_stata(WAVE2_DATA, convert_categoricals=False)
df = merge_wave_vars(df, df_w2, ['ids', 'w2a29'], wave_value=2, var_names=['w2a29'])
mask_w2 = df['grade'] == 1
n_w2 = df.loc[mask_w2, 'w2a29'].notna().sum()
print(f"   Wave2 w2a29匹配: {n_w2}/{mask_w2.sum()} ({n_w2/mask_w2.sum()*100:.1f}%)")

# 2c 构造跨期一致的学业压力变量
# 注意: b32和w2a29都是1-5量表, 但具体题文不同, 按wave分别标准化
df['academic_pressure_raw'] = np.where(
  df['grade'].isin([0, 2]), df['b32'], df['w2a29'])

# z-score标准化
m1 = df.loc[mask_w1, 'b32'].mean()
s1 = df.loc[mask_w1, 'b32'].std()
m2 = df.loc[mask_w2, 'w2a29'].mean()
s2 = df.loc[mask_w2, 'w2a29'].std()
df['academic_pressure_z'] = np.where(
  df['grade'].isin([0, 2]),
  (df['b32'] - m1) / s1,
  (df['w2a29'] - m2) / s2)
print(f"   学业压力: w1均值={m1:.2f}(sd={s1:.2f}), w2均值={m2:.2f}(sd={s2:.2f})")


# ============================================================
# 3. 合并教养方式变量
# ============================================================
print("\n" + "=" * 60)
print("3. 合并教养方式变量...")
print("=" * 60)

# 3a Wave1教养方式: b2201-b2202(父母关系), b2301-b2308(亲子关系)
w1_edu_cols = ['ids', 'b2201', 'b2202', 'b2301', 'b2302', 'b2303',
               'b2304', 'b2305', 'b2306', 'b2307', 'b2308']
df = merge_wave_vars(df, df_w1, w1_edu_cols, wave_value=1,
                     var_names=['b2201', 'b2202', 'b2301', 'b2302', 'b2303',
                                'b2304', 'b2305', 'b2306', 'b2307', 'b2308'])

# 验证匹配
for v in ['b2201', 'b2301']:
  n = df.loc[mask_w1, v].notna().sum()
  print(f"   Wave1 {v}匹配: {n}/{mask_w1.sum()} ({n/mask_w1.sum()*100:.1f}%)")

# 3b Wave2教养方式: w2a18-w2a19(父母关系), w2a2001-w2a2006(亲子关系)
w2_edu_cols = ['ids', 'w2a18', 'w2a19', 'w2a2001', 'w2a2002', 'w2a2003',
               'w2a2004', 'w2a2005', 'w2a2006']
df = merge_wave_vars(df, df_w2, w2_edu_cols, wave_value=2,
                     var_names=['w2a18', 'w2a19', 'w2a2001', 'w2a2002', 'w2a2003',
                                'w2a2004', 'w2a2005', 'w2a2006'])

for v in ['w2a18', 'w2a2001']:
  n = df.loc[mask_w2, v].notna().sum()
  print(f"   Wave2 {v}匹配: {n}/{mask_w2.sum()} ({n/mask_w2.sum()*100:.1f}%)")

# 3c 构造教养方式综合指标
# b2201: 父母关系很好 (1-4, 1=很好, 4=不好)
# b2202: 父母关系 (1-4, 1=经常吵架, 4=从不)
# 注意: 方向相反, b2201编码为1=很好, 需要反转
# b2301-b2308: 亲子关系 (1=非常同意, 2=比较同意, 3=不太同意)
# 题目: 父母经常管我/与我讨论/检查作业/指导... 分数越高=越少管教

# 反转b2201使方向一致 (1→4, 2→3, 3→2, 4→1)
df['parent_rel_quality'] = 5 - df['b2201']  # 越高=关系越好
df['parent_conflict'] = df['b2202']  # 越高=冲突越少

# 亲子投入指数 (b2301-b2308的平均, 越高=越少投入, 需要反转)
b23_cols = ['b2301', 'b2302', 'b2303', 'b2304', 'b2305', 'b2306', 'b2307', 'b2308']
# 反转: 1→3, 2→2, 3→1
for col in b23_cols:
  df[col + '_inv'] = 4 - df[col]
df['parent_investment_w1'] = df[[c + '_inv' for c in b23_cols]].mean(axis=1, skipna=True)

# 亲子沟通频率 (w2a2001: 谈论学校里的事, 1=经常, 3=从不, 需要反转)
w2a20_cols = ['w2a2001', 'w2a2002', 'w2a2003', 'w2a2004', 'w2a2005', 'w2a2006']
for col in w2a20_cols:
  df[col + '_inv'] = 4 - df[col]
df['parent_investment_w2'] = df[[c + '_inv' for c in w2a20_cols]].mean(axis=1, skipna=True)

# 跨期一致的亲子投入指数 (按wave分别标准化)
m_pi_w1 = df.loc[mask_w1, 'parent_investment_w1'].mean()
s_pi_w1 = df.loc[mask_w1, 'parent_investment_w1'].std()
m_pi_w2 = df.loc[mask_w2, 'parent_investment_w2'].mean()
s_pi_w2 = df.loc[mask_w2, 'parent_investment_w2'].std()
df['parent_investment_z'] = np.where(
  df['grade'].isin([0, 2]),
  (df['parent_investment_w1'] - m_pi_w1) / s_pi_w1,
  (df['parent_investment_w2'] - m_pi_w2) / s_pi_w2)
print(f"   亲子投入: w1均值={m_pi_w1:.2f}(sd={s_pi_w1:.2f}), w2均值={m_pi_w2:.2f}(sd={s_pi_w2:.2f})")


# ============================================================
# 4. 构造家庭SES综合指数
# ============================================================
print("\n" + "=" * 60)
print("4. 构造家庭SES综合指数...")
print("=" * 60)

# 4a 父母教育年限标准化
# 已有: mom_education_ (受教育年限, 原始编码), dad_education_
# 注意: 这些变量可能已有缺失值
# 取父母教育年限的最大值作为家庭最高教育水平
df['edu_max_years'] = df[['mom_education_', 'dad_education_']].max(axis=1, skipna=True)
# 如果父母都缺失, 则用mean_education
df['edu_max_years'] = df['edu_max_years'].fillna(df['mean_education'])

# 4b 经济状况标准化
# child_economic_status: 学生自评 (1-5, 1=非常困难, 5=很富裕)
# parent_economic_status: 家长评价 (1-5)
# 取两者均值
df['econ_status'] = df[['child_economic_status', 'parent_economic_status']].mean(axis=1, skipna=True)

# 4c 综合SES指数 (简单标准化加总)
ses_components = ['edu_max_years', 'econ_status', 'hukou_type']

# 对每个成分标准化
for c in ses_components:
  if c in df.columns:
    mean_v = df[c].mean()
    std_v = df[c].std()
    df[c + '_z'] = (df[c] - mean_v) / std_v
    print(f"   {c}: 均值={mean_v:.2f}, 标准差={std_v:.2f}")

# 综合SES = 三个标准化分量的简单平均
z_cols = [c + '_z' for c in ses_components]
df['ses_index'] = df[z_cols].mean(axis=1, skipna=True)
print(f"   SES综合指数: 均值={df['ses_index'].mean():.3f}, "
      f"标准差={df['ses_index'].std():.3f}, "
      f"缺失={df['ses_index'].isna().sum()}")

# 4d SES三分组 (低/中/高)
df['ses_tercile'] = pd.qcut(df['ses_index'], q=3, labels=[1, 2, 3], duplicates='drop')
print(f"   SES三分组: {df['ses_tercile'].value_counts().sort_index().to_dict()}")

# 4e 低SES虚拟变量 (用于非对称效应检验)
df['ses_low'] = (df['ses_tercile'] == 1).astype(float)
df['ses_high'] = (df['ses_tercile'] == 3).astype(float)


# ============================================================
# 5. 处理班级层面变量
# ============================================================
print("\n" + "=" * 60)
print("5. 班级层面变量处理...")
print("=" * 60)

# 5a 班级平均心理健康水平 (leave-out-self)
cls_mean_mh = df.groupby('clsids')['mental_common_z'].transform(
  lambda x: (x.sum() - x) / (x.count() - 1))
df['cls_mean_mental'] = cls_mean_mh
print(f"   班级平均心理健康(leave-out-self): 均值={df['cls_mean_mental'].mean():.3f}")

# 5b 班级心理健康不平等 (标准差, 对z-score适用)
# 注意: 标准Gini系数要求变量非负, 而z-score有负值, 使用标准差衡量不平等
cls_sd_mental = df.groupby('clsids')['mental_common_z'].transform('std')
df['cls_sd_mental'] = cls_sd_mental
print(f"   班级心理健康标准差: 均值={df['cls_sd_mental'].mean():.3f}")

# 另用原始分数计算班级内变异系数 (CV)
cls_cv = df.groupby('clsids')['mental_common_raw'].apply(
  lambda x: x.std() / x.mean() if x.mean() > 0 else np.nan)
df['cls_cv_mental'] = df['clsids'].map(cls_cv)
print(f"   班级心理健康CV: 均值={df['cls_cv_mental'].mean():.3f}")

# 5c 核心自变量: 班级平均父母教育水平与自身SES的交互项
df['cls_mean_edu_x_ses'] = df['cls_mean_max_education'] * df['ses_index']
df['cls_mean_edu_x_ses_low'] = df['cls_mean_max_education'] * df['ses_low']
print(f"   交互项构造完成")


# ============================================================
# 6. 清理与保存
# ============================================================
print("\n" + "=" * 60)
print("6. 保存最终分析数据...")
print("=" * 60)

# 列出所有新构造的变量
new_vars = [
  # 学业压力
  'b32', 'w2a29', 'academic_pressure_raw', 'academic_pressure_z',
  # 教养方式
  'b2201', 'b2202', 'b2301', 'b2302', 'b2303', 'b2304', 'b2305', 'b2306', 'b2307', 'b2308',
  'w2a18', 'w2a19', 'w2a2001', 'w2a2002', 'w2a2003', 'w2a2004', 'w2a2005', 'w2a2006',
  'parent_rel_quality', 'parent_conflict',
  'parent_investment_w1', 'parent_investment_w2', 'parent_investment_z',
  # SES
  'edu_max_years', 'econ_status',
  'edu_max_years_z', 'econ_status_z', 'hukou_type_z',
  'ses_index', 'ses_tercile', 'ses_low', 'ses_high',
  # 班级层面
  'cls_mean_mental', 'cls_sd_mental',
  'cls_mean_edu_x_ses', 'cls_mean_edu_x_ses_low',
  # 反转变量
  'b2301_inv', 'b2302_inv', 'b2303_inv', 'b2304_inv', 'b2305_inv',
  'b2306_inv', 'b2307_inv', 'b2308_inv',
  'w2a2001_inv', 'w2a2002_inv', 'w2a2003_inv', 'w2a2004_inv', 'w2a2005_inv', 'w2a2006_inv',
]

# 只保留存在于df中的变量
existing_new = [v for v in new_vars if v in df.columns]
print(f"   新构造变量: {len(existing_new)} 个")

# 保存
df.to_stata(OUTPUT_FILE, write_index=False)
print(f"   保存至: {OUTPUT_FILE}")
print(f"   最终数据: {df.shape[0]} 行 × {df.shape[1]} 列")

# 输出关键变量列表
key_vars = [
  # 因变量
  'mental_common_z', 'mental_health_z', 'mental_health_z_w2', 'mental_poor',
  # 核心自变量
  'cls_mean_max_education', 'cls_sd_max_education',
  # SES
  'ses_index', 'ses_tercile', 'ses_low', 'ses_high',
  # 中介变量
  'academic_pressure_z', 'parent_investment_z',
  # 交互项
  'cls_mean_edu_x_ses', 'cls_mean_edu_x_ses_low',
  # 控制变量
  'gender', 'hukou_type', 'nationality', 'grade', 'yn_single_child',
  'age', 'cls_ave_economic',
  # 班级层面
  'cls_mean_mental', 'cls_sd_mental',
]
print("\n   关键分析变量:")
for v in key_vars:
  if v in df.columns:
    if df[v].dtype.name == 'category':
      print(f"     ✅ {v}: 分类变量, 缺失={df[v].isna().sum()}")
    else:
      print(f"     ✅ {v}: 均值={df[v].mean():.3f}, 缺失={df[v].isna().sum()}")
  else:
    print(f"     ❌ {v}: 缺失")

print("\n✅ 脚本2完成: 变量构造成功!")