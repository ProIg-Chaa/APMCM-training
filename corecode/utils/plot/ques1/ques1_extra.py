import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# ---------------------- 数据准备 ----------------------
data = {
    'Year': [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
    'CNY_per_USD': [6.76, 6.63, 6.91, 6.9, 6.45, 6.73, 7.09, 7.19, 7.21],
    'BRL_per_USD': [3.19, 3.87, 4.04, 5.16, 5.4, 5.16, 4.99, 5.39, 5.3],
    'ARS_per_USD': [17.72, 37.49, 63.01, 85.49, 105.83, 169.15, 371.66, 1030.78, 1350],
    'USD_per_USD': [1, 1, 1, 1, 1, 1, 1, 1, 1]
}
exrate_df = pd.DataFrame(data)

# ---------------------- 保存路径 ----------------------
save_path = r'/results/figures/ques1/extra'
os.makedirs(save_path, exist_ok=True)

# ---------------------- 绘图设置（双Y轴适配） ----------------------
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.unicode_minus'] = False
fig, ax1 = plt.subplots(figsize=(14, 8))

# 左Y轴：CNY和BRL（低波动）
color_cny = '#2E86AB'
color_brl = '#A23B72'
ax1.set_xlabel('Year', fontsize=14, fontweight='bold')
ax1.set_ylabel('CNY / BRL per USD', fontsize=14, fontweight='bold', color='black')
ax1.plot(exrate_df['Year'], exrate_df['CNY_per_USD'],
         color=color_cny, linewidth=3, marker='o', markersize=7, label='CNY/USD', alpha=0.9)
ax1.plot(exrate_df['Year'], exrate_df['BRL_per_USD'],
         color=color_brl, linewidth=3, marker='s', markersize=7, label='BRL/USD', alpha=0.9)
ax1.tick_params(axis='y', labelcolor='black')
ax1.set_ylim(0, 10)  # 适配CNY/BRL范围

# 右Y轴：ARS（高波动）
ax2 = ax1.twinx()
color_ars = '#F18F01'
ax2.set_ylabel('ARS per USD', fontsize=14, fontweight='bold', color=color_ars)
ax2.plot(exrate_df['Year'], exrate_df['ARS_per_USD'],
         color=color_ars, linewidth=3, marker='^', markersize=7, label='ARS/USD', alpha=0.9)
ax2.tick_params(axis='y', labelcolor=color_ars)
ax2.set_yscale('log')  # 对数刻度适配高波动

# ---------------------- 图表美化 ----------------------
fig.suptitle('Exchange Rate Trend (2017-2025)', fontsize=18, fontweight='bold', y=0.98)
ax1.grid(True, linestyle='--', alpha=0.3)

# 合并图例
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=12, frameon=True, shadow=True)

plt.tight_layout()
plt.savefig(os.path.join(save_path, 'exchange_rate_trend_optimized.png'), dpi=300, bbox_inches='tight')
plt.close()

print(f"优化后汇率图已保存至：{os.path.join(save_path, 'exchange_rate_trend_optimized.png')}")