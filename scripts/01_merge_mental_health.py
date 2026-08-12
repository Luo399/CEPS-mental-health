"""
01_merge_mental_health.py
=========================
将完整版CEPS的情绪题（a1801-a1805, w2c2501-w2c2510）合并到已有清洗数据中。
同时构造标准化的心理健康指数。

输入:
  - 教育减负--代码与数据/datafile/final_ceps_all1123.dta  (清洗后数据)
  - CEPS/2013-2014/cepsw1studentCN.dta                      (wave1完整版)
  - CEPS/2014-2015/cepsw2studentCN.dta                      (wave2完整版)

输出:
  - data/analysis_data.dta  (合并后的分析数据)

变量说明:
  - a1801-a1805: 基线抑郁量表 (1=从不, 5=总是)
  - w2c2501-w2c2510: 追踪情绪量表 (1=从不, 5=总是)
  - 两期共有5题: 沮丧/抑郁/不快乐/生活没有意思/悲伤
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
CLEANED_DATA = os.path.join(BASE_DIR, '教育减负--代码与数据', 'datafile', 'final_ceps_all1123.dta')
WAVE1_DATA = os.path.join(BASE_DIR, 'CEPS', '2013-2014', 'cepsw1studentCN.dta')
WAVE2_DATA = os.path.join(BASE_DIR, 'CEPS', '2014-2015', 'cepsw2studentCN.dta')
OUTPUT_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'analysis_data.dta')

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# 1. 读取清洗后数据
# ============================================================
print("=" * 60)
print("1. 读取清洗后数据...")
print("=" * 60)

df_clean = pd.read_stata(CLEANED_DATA, convert_categoricals=False)
print(f"   清洗后数据: {df_clean.shape[0]} 行 × {df_clean.shape[1]} 列")
print(f"   唯一学生数: {df_clean['ids'].nunique()}")
print(f"   grade分布: 0(7年级w1)={ (df_clean['grade']==0).sum() }, "
      f"1(8年级w2)={ (df_clean['grade']==1).sum() }, "
      f"2(9年级w1)={ (df_clean['grade']==2).sum() }")

# 判断哪些行属于wave1, 哪些属于wave2
df_clean['_wave'] = np.where(df_clean['grade'].isin([0, 2]), 1, 2)
print(f"   Wave1行数: {(df_clean['_wave']==1).sum()}, Wave2行数: {(df_clean['_wave']==2).sum()}")


# ============================================================
# 2. 合并wave1情绪题 (a1801-a1805)
# ============================================================
print("\n" + "=" * 60)
print("2. 合并Wave1情绪题 (a1801-a1805)...")
print("=" * 60)

# 读取wave1完整版
df_w1 = pd.read_stata(WAVE1_DATA, convert_categoricals=False)
print(f"   Wave1完整版: {df_w1.shape[0]} 行 × {df_w1.shape[1]} 列")

# 提取情绪题和学业压力备选
w1_merge_cols = ['ids', 'a1801', 'a1802', 'a1803', 'a1804', 'a1805']
df_w1_merge = df_w1[w1_merge_cols].copy()

# 检查缺失率
for c in ['a1801', 'a1802', 'a1803', 'a1804', 'a1805']:
    miss_rate = df_w1_merge[c].isna().mean() * 100
    print(f"   {c}: 缺失率={miss_rate:.1f}%")

# 只合并到wave1行 (grade=0 或 grade=2)
mask_w1 = df_clean['_wave'] == 1
df_clean_w1 = df_clean[mask_w1].copy()
df_clean_w2 = df_clean[~mask_w1].copy()

# 左连接
df_clean_w1 = df_clean_w1.merge(df_w1_merge, on='ids', how='left', suffixes=('', '_w1'))
print(f"   合并后Wave1行数: {len(df_clean_w1)}")

# 验证合并是否成功
n_matched = df_clean_w1['a1801'].notna().sum()
print(f"   情绪题匹配成功: {n_matched}/{len(df_clean_w1)} ({n_matched/len(df_clean_w1)*100:.1f}%)")


# ============================================================
# 3. 合并wave2情绪题 (w2c2501-w2c2510)
# ============================================================
print("\n" + "=" * 60)
print("3. 合并Wave2情绪题 (w2c2501-w2c2510)...")
print("=" * 60)

df_w2 = pd.read_stata(WAVE2_DATA, convert_categoricals=False)
print(f"   Wave2完整版: {df_w2.shape[0]} 行 × {df_w2.shape[1]} 列")

# 提取情绪题
w2_merge_cols = ['ids'] + [f'w2c25{i:02d}' for i in range(1, 11)]
df_w2_merge = df_w2[w2_merge_cols].copy()

# 检查缺失率
for c in w2_merge_cols[1:]:
    miss_rate = df_w2_merge[c].isna().mean() * 100
    print(f"   {c}: 缺失率={miss_rate:.1f}%")

# 左连接到wave2行
df_clean_w2 = df_clean_w2.merge(df_w2_merge, on='ids', how='left', suffixes=('', '_w2'))
print(f"   合并后Wave2行数: {len(df_clean_w2)}")

n_matched = df_clean_w2['w2c2501'].notna().sum()
print(f"   情绪题匹配成功: {n_matched}/{len(df_clean_w2)} ({n_matched/len(df_clean_w2)*100:.1f}%)")


# ============================================================
# 4. 合并回完整数据框
# ============================================================
print("\n" + "=" * 60)
print("4. 合并回完整数据框...")
print("=" * 60)

df_merged = pd.concat([df_clean_w1, df_clean_w2], axis=0, ignore_index=True)
duplicate_cols = [c for c in df_merged.columns if c.endswith('_w1') or c.endswith('_w2')]
if duplicate_cols:
  df_merged.drop(columns=duplicate_cols, inplace=True)
print(f"   最终数据: {df_merged.shape[0]} 行 × {df_merged.shape[1]} 列")


# ============================================================
# 5. 构造心理健康指数
# ============================================================
print("\n" + "=" * 60)
print("5. 构造心理健康指数...")
print("=" * 60)

# 5a 基线心理健康: a1801-a1805 加总 (分数越高=心理越差)
df_merged['mental_w1_raw'] = df_merged[['a1801', 'a1802', 'a1803', 'a1804', 'a1805']].sum(axis=1, min_count=3)
# 如缺失题数>2, 设为缺失
df_merged['mental_w1_raw'] = np.where(
  df_merged[['a1801', 'a1802', 'a1803', 'a1804', 'a1805']].isna().sum(axis=1) > 2,
  np.nan, df_merged['mental_w1_raw'])

# 5b 追踪心理健康: w2c2501-w2c2510 加总 (分数越高=心理越差)
w2c_cols = [f'w2c25{i:02d}' for i in range(1, 11)]
df_merged['mental_w2_raw'] = df_merged[w2c_cols].sum(axis=1, min_count=6)
df_merged['mental_w2_raw'] = np.where(
  df_merged[w2c_cols].isna().sum(axis=1) > 4,
  np.nan, df_merged['mental_w2_raw'])

# 5c 跨期公用心理健康指数 (仅使用两期共有的5题: 沮丧/抑郁/不快乐/生活没有意思/悲伤)
# wave1: a1801-a1805, wave2: 需要确认对应关系
# 按题项内容, w2c25前5题通常对应a18的5题
# 实际对应关系: w2c2501=沮丧, w2c2502=抑郁, w2c2503=不快乐, w2c2504=生活没意思, w2c2505=悲伤
df_merged['mental_common_raw'] = np.where(
  df_merged['_wave'] == 1,
  df_merged['mental_w1_raw'],  # wave1直接用a18
  df_merged[['w2c2501', 'w2c2502', 'w2c2503', 'w2c2504', 'w2c2505']].sum(axis=1, min_count=3)
)

# 共享5题缺失处理
common5_cols_w2 = ['w2c2501', 'w2c2502', 'w2c2503', 'w2c2504', 'w2c2505']
mask_w2_common = df_merged['_wave'] == 2
df_merged.loc[mask_w2_common & (df_merged[common5_cols_w2].isna().sum(axis=1) > 2), 'mental_common_raw'] = np.nan

# 5d 标准化为z-score (按wave分别标准化, 保证跨期可比)
# 基线心理健康z-score
mask_w1 = df_merged['_wave'] == 1
m1_mean = df_merged.loc[mask_w1, 'mental_w1_raw'].mean()
m1_std = df_merged.loc[mask_w1, 'mental_w1_raw'].std()
df_merged['mental_health_z'] = np.where(
  mask_w1,
  (df_merged['mental_w1_raw'] - m1_mean) / m1_std,
  np.nan)
print(f"   基线心理健康z-score: 均值={m1_mean:.2f}, 标准差={m1_std:.2f}")

# 追踪心理健康z-score
mask_w2 = df_merged['_wave'] == 2
m2_mean = df_merged.loc[mask_w2, 'mental_w2_raw'].mean()
m2_std = df_merged.loc[mask_w2, 'mental_w2_raw'].std()
df_merged['mental_health_z_w2'] = np.where(
  mask_w2,
  (df_merged['mental_w2_raw'] - m2_mean) / m2_std,
  np.nan)
print(f"   追踪心理健康z-score: 均值={m2_mean:.2f}, 标准差={m2_std:.2f}")

# 跨期可比心理健康z-score (按wave分别标准化)
m_common_mean = df_merged.loc[mask_w1, 'mental_common_raw'].mean()
m_common_std = df_merged.loc[mask_w1, 'mental_common_raw'].std()
# 以wave1为基准, 用wave1的均值和标准差标准化wave2
df_merged['mental_common_z'] = (df_merged['mental_common_raw'] - m_common_mean) / m_common_std
print(f"   跨期可比心理健康z-score (基准=wave1): 均值={m_common_mean:.2f}, 标准差={m_common_std:.2f}")

# 5e 构造心理健康"不良"二值变量 (得分最高的25%)
p75 = df_merged['mental_common_z'].quantile(0.75)
df_merged['mental_poor'] = (df_merged['mental_common_z'] > p75).astype(float)
print(f"   心理健康不良(>P75): {df_merged['mental_poor'].mean()*100:.1f}%")


# ============================================================
# 6. 检查summary并保存
# ============================================================
print("\n" + "=" * 60)
print("6. 变量概况与保存...")
print("=" * 60)

mental_vars = ['mental_w1_raw', 'mental_w2_raw', 'mental_common_raw',
               'mental_health_z', 'mental_health_z_w2', 'mental_common_z', 'mental_poor']
print("\n   心理健康变量概况:")
print(df_merged[mental_vars].describe().to_string())

# 删除辅助变量
df_merged.drop(columns=['_wave'], inplace=True)

# 保存
df_merged.to_stata(OUTPUT_FILE, write_index=False)
print(f"\n   保存至: {OUTPUT_FILE}")
print(f"   最终数据: {df_merged.shape[0]} 行 × {df_merged.shape[1]} 列")

print("\n✅ 脚本1完成: 情绪题合并成功!")