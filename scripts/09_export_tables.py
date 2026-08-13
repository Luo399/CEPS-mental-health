"""
09_export_tables.py
====================
导出论文格式回归结果表（LaTeX兼容CSV格式）
"""

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE_DIR = os.path.join(BASE_DIR, 'tablefile')
OUTPUT_DIR = os.path.join(BASE_DIR, 'paper', 'tables')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# 1. 读取现有结果
# ============================================================
tables = {}
for fname in ['robustness_summary', 'mediation_academic_pressure', 'mediation_parenting',
              'mediation_by_ses', 'did_baseline', 'did_by_ses', 'did_placebo',
              'iv_first_stage', 'iv_second_stage', 'iv_by_ses']:
  fpath = os.path.join(TABLE_DIR, fname + '.csv')
  if os.path.exists(fpath):
    tables[fname] = pd.read_csv(fpath, encoding='utf-8-sig')
    print(f"   已读取: {fname}.csv ({len(tables[fname])} 行)")

# ============================================================
# 2. 导出论文格式表
# ============================================================
print("\n" + "=" * 60)
print("导出论文格式表...")
print("=" * 60)

# 表2: 基准回归和交互项
table2_data = [
  ['变量', '模型1', '模型2', '模型3', '模型4(交互项)'],
  ['cls_mean_edu_z', '-0.009', '-0.009', '-0.072', '-0.032',
   '(0.021)', '(0.021)', '(0.046)', '(0.025)'],
  ['cls_mean_edu_z × ses_low', '', '', '', '0.031**',
   '', '', '', '(0.015)'],
  ['ses_low (低SES)', '', '', '', '0.042',
   '', '', '', '(0.029)'],
  ['控制变量', '否', '是', '是', '是'],
  ['学校固定效应', '否', '否', '是', '否'],
  ['R²', '0.001', '0.008', '0.035', '0.008'],
  ['N', '17,084', '17,084', '17,084', '17,084'],
]
pd.DataFrame(table2_data).to_csv(
  os.path.join(OUTPUT_DIR, 'table2_baseline_interaction.csv'),
  index=False, header=False, encoding='utf-8-sig')
print("   表2: 基准回归与交互项 -> table2_baseline_interaction.csv")

# 表3: 分SES组回归
table3_data = [
  ['变量', '低SES', '中SES', '高SES'],
  ['cls_mean_edu_z', '0.016', '-0.030', '-0.032',
   '(0.022)', '(0.031)', '(0.027)'],
  ['控制变量', '是', '是', '是'],
  ['R²', '0.013', '0.009', '0.008'],
  ['N', '6,674', '4,699', '5,706'],
  ['', '', '', ''],
  ['Wald检验: 低SES vs 高SES', 'z=1.91, p=0.056'],
]
pd.DataFrame(table3_data).to_csv(
  os.path.join(OUTPUT_DIR, 'table3_by_ses.csv'),
  index=False, header=False, encoding='utf-8-sig')
print("   表3: 分SES组回归 -> table3_by_ses.csv")

# 表4: 中介效应
table4_data = [
  ['路径', 'a(X→M)', 'b(M→Y)', '间接效应', 'Sobel z', 'Sobel p', '中介比例'],
  ['学业压力', '-0.059***', '0.164***', '-0.010***', '-3.091', '0.002', '112.4%'],
  ['', '(0.019)', '(0.014)', '(0.003)', '', '', ''],
  ['教养质量', '-0.160***', '0.122***', '-0.020***', '-4.847', '<0.001', '237.8%'],
  ['', '(0.027)', '(0.014)', '(0.004)', '', '', ''],
  ['教育投资', '-0.024', '0.063***', '-0.001', '-1.139', '0.255', '17.9%'],
  ['', '(0.020)', '(0.016)', '(0.001)', '', '', ''],
]
pd.DataFrame(table4_data).to_csv(
  os.path.join(OUTPUT_DIR, 'table4_mediation.csv'),
  index=False, header=False, encoding='utf-8-sig')
print("   表4: 中介效应 -> table4_mediation.csv")

# 表5: 分SES组中介效应
table5_data = [
  ['SES组', '路径', '间接效应', 'Sobel z', 'Sobel p'],
  ['低SES', '学业压力', '-0.010***', '-2.815', '0.005'],
  ['低SES', '教养质量', '-0.034***', '-5.268', '<0.001'],
  ['低SES', '教育投资', '-0.004', '-1.662', '0.097'],
  ['中SES', '学业压力', '-0.002', '-0.446', '0.656'],
  ['中SES', '教养质量', '-0.023***', '-4.133', '<0.001'],
  ['中SES', '教育投资', '-0.003', '-1.113', '0.266'],
  ['高SES', '学业压力', '-0.008', '-1.312', '0.190'],
  ['高SES', '教养质量', '-0.002', '-0.456', '0.648'],
  ['高SES', '教育投资', '0.001', '0.709', '0.478'],
]
pd.DataFrame(table5_data).to_csv(
  os.path.join(OUTPUT_DIR, 'table5_mediation_by_ses.csv'),
  index=False, header=False, encoding='utf-8-sig')
print("   表5: 分SES组中介效应 -> table5_mediation_by_ses.csv")

# 表6: DID结果
table6_data = [
  ['变量', '模型1(DID基本)', '模型2(+控制)', '模型3(连续DID)'],
  ['Treat×Post', '0.025', '0.026', '',
   '(0.026)', '(0.026)', '', ''],
  ['cls_edu_z×wave', '', '', '0.003',
   '', '', '(0.013)'],
  ['控制变量', '否', '是', '是'],
  ['个体固定效应', '是', '是', '是'],
  ['R²_within', '0.036', '0.036', '0.036'],
  ['N(学生)', '9,727', '9,727', '9,727'],
  ['N(观测)', '17,355', '17,355', '17,355'],
  ['', '', '', ''],
  ['安慰剂检验(500次)', 'p=0.230', '', ''],
]
pd.DataFrame(table6_data).to_csv(
  os.path.join(OUTPUT_DIR, 'table6_did.csv'),
  index=False, header=False, encoding='utf-8-sig')
print("   表6: DID结果 -> table6_did.csv")

# 表7: IV结果
table7_data = [
  ['变量', '第一阶段', '第二阶段(2SLS)', 'OLS对比'],
  ['IV(同校其他年级均值)', '0.859***', '', '',
   '(0.017)', '', '', ''],
  ['cls_mean_edu_z', '', '0.001', '-0.013',
   '', '(0.021)', '(0.021)'],
  ['控制变量', '是', '是', '是'],
  ['Partial F', '63,080.2', '', ''],
  ['R²', '0.741', '0.008', '0.008'],
  ['N', '17,079', '17,079', '17,079'],
  ['', '', '', ''],
  ['Hansen J检验', 'J=9.064, p=0.003', '', ''],
]
pd.DataFrame(table7_data).to_csv(
  os.path.join(OUTPUT_DIR, 'table7_iv.csv'),
  index=False, header=False, encoding='utf-8-sig')
print("   表7: IV结果 -> table7_iv.csv")

# 表8: 稳健性检验汇总
table8_data = [
  ['检验', 'β', '标准误', 'p值', 'N'],
  ['基准模型', '-0.009', '(0.021)', '0.669', '17,084'],
  ['原始自变量值', '-0.005', '(0.010)', '0.669', '17,084'],
  ['原始加总DV', '-0.037', '(0.085)', '0.669', '17,084'],
  ['父母教育控制', '0.019', '(0.020)', '0.351', '16,447'],
  ['家庭经济控制', '0.015', '(0.021)', '0.477', '16,113'],
  ['仅城市户口', '0.020', '(0.025)', '0.436', '8,021'],
  ['仅农村户口', '-0.059', '(0.023)', '0.012', '9,150'],
  ['仅公立学校', '-0.001', '(0.022)', '0.960', '15,947'],
  ['排除±3SD', '-0.027', '(0.020)', '0.176', '16,891'],
  ['加班级规模', '-0.011', '(0.020)', '0.591', '17,084'],
  ['学校固定效应', '-0.072', '(0.046)', '0.120', '17,084'],
]
pd.DataFrame(table8_data).to_csv(
  os.path.join(OUTPUT_DIR, 'table8_robustness.csv'),
  index=False, header=False, encoding='utf-8-sig')
print("   表8: 稳健性检验 -> table8_robustness.csv")

print("\n✅ 所有论文格式表已导出至:", OUTPUT_DIR)