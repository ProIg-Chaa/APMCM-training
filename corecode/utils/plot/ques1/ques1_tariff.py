import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------------------- 数据准备 ----------------------
data = {
    'Year': [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
    'MFN_Tariff': [3, 3, 3, 3, 3, 3, 3, 3],
    'Retaliatory_Tariff': [25, 27.75, 12.5, 12.5, 12.5, 12.5, 7.5, 16.5],
    'Total_Effective_Tariff': [41, 45.5, 16, 16, 16, 16, 24, 39],
    'Other_Surcharges': [13, 14.75, 0.5, 0.5, 0.5, 0.5, 13.5, 9.5]
}
df = pd.DataFrame(data)

# 路径设置
save_path = r'C:\Users\15963\Desktop\APMCM-training\results\figures\ques1\tariff'
os.makedirs(save_path, exist_ok=True)

# 绘图样式配置
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['axes.linewidth'] = 1.2

# ---------------------- 图表1：关税趋势图 ----------------------
plt.figure(figsize=(14, 8))

# 绘制各关税类型趋势
plt.plot(
    df['Year'], df['Total_Effective_Tariff'],
    linewidth=3, color='#C73E1D', marker='o', markersize=7,
    label='Total Effective Tariff', alpha=0.9
)
plt.plot(
    df['Year'], df['Retaliatory_Tariff'],
    linewidth=2.5, color='#A23B72', linestyle='--', marker='s', markersize=6,
    label='Retaliatory Tariff', alpha=0.9
)
plt.axhline(
    y=df['MFN_Tariff'].iloc[0], color='#2E86AB', linewidth=2.5, linestyle=':',
    label='MFN Tariff (3%)', alpha=0.9
)

# 政策节点标注
plt.axvline(x=2018, color='#6A994E', linestyle='--', linewidth=2, alpha=0.7)
plt.text(2018, 42, '2018 US Policy', fontsize=11, fontweight='bold', color='#6A994E', ha='center',
         bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='#6A994E'))

plt.axvline(x=2025, color='#C73E1D', linestyle='--', linewidth=2, alpha=0.7)
plt.text(2025, 42, '2025 Tariff Adjustment', fontsize=11, fontweight='bold', color='#C73E1D', ha='center',
         bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='#C73E1D'))

# 美化与保存
plt.title('Tariff Trend (2018-2025)', fontsize=18, fontweight='bold')
plt.xlabel('Year', fontsize=14)
plt.ylabel('Tariff (%)', fontsize=14)
plt.legend(loc='upper left', fontsize=12)
plt.grid(linestyle='--', alpha=0.3)
plt.xticks(df['Year'])
plt.ylim(0, 50)
plt.tight_layout()
plt.savefig(os.path.join(save_path, '1_tariff_trend.png'), dpi=300, bbox_inches='tight')
plt.close()

# ---------------------- 图表2：关税叠加构成图 ----------------------
plt.figure(figsize=(14, 8))

# 叠加面积图展示关税构成
plt.fill_between(df['Year'], 0, df['MFN_Tariff'],
                 color='#2E86AB', alpha=0.7, label='MFN Tariff (Base)')
plt.fill_between(df['Year'], df['MFN_Tariff'], df['MFN_Tariff'] + df['Retaliatory_Tariff'],
                 color='#A23B72', alpha=0.7, label='Retaliatory Tariff')
plt.fill_between(df['Year'], df['MFN_Tariff'] + df['Retaliatory_Tariff'],
                 df['MFN_Tariff'] + df['Retaliatory_Tariff'] + df['Other_Surcharges'],
                 color='#F18F01', alpha=0.7, label='Other Surcharges')

# 总关税折线突出总量
total_tariff = df['MFN_Tariff'] + df['Retaliatory_Tariff'] + df['Other_Surcharges']
plt.plot(df['Year'], total_tariff, color='#C73E1D', linewidth=3, marker='o', label='Total Effective Tariff')

# 政策节点标注
plt.axvline(x=2018, color='#6A994E', linestyle='--', linewidth=2, alpha=0.7)
plt.axvline(x=2025, color='#C73E1D', linestyle='--', linewidth=2, alpha=0.7)

# 美化与保存
plt.title('Tariff Composition & Trend (2018-2025)', fontsize=18, fontweight='bold')
plt.xlabel('Year', fontsize=14)
plt.ylabel('Tariff (%)', fontsize=14)
plt.legend(loc='upper left', fontsize=11)
plt.grid(linestyle='--', alpha=0.3)
plt.xticks(df['Year'])
plt.ylim(0, 50)
plt.tight_layout()
plt.savefig(os.path.join(save_path, '2_tariff_composition_stack.png'), dpi=300, bbox_inches='tight')
plt.close()

print(f"图表已保存至：{save_path}")
print("生成文件：")
print("1. 1_tariff_trend.png（关税趋势图）")
print("2. 2_tariff_composition_stack.png（关税叠加构成图）")