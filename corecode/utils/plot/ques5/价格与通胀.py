import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# 读取数据（使用指定路径）
df = pd.read_csv(r'C:\Users\15963\Desktop\APMCM-training\data\raw\ques5\价格与通胀\价格与通胀.csv')

# 获取所有年份和指标
years = df['year'].tolist()
indices = df.columns[1:].tolist()
N = len(indices)

# 计算雷达图角度（闭合图形）
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]  # 闭合角度

# 创建图形
fig, ax = plt.subplots(figsize=(15, 13), subplot_kw=dict(projection='polar'))

# 使用viridis渐变色彩（年份越新颜色越深）
colors = plt.cm.viridis(np.linspace(0, 1, len(years)))

# 以2016年为基准标准化所有数据
base_2016 = df[df['year'] == 2016].iloc[0, 1:].values

# 计算所有标准化数据的范围（自动确定最佳量程）
all_data_norm = []
for year in years:
    current_data = df[df['year'] == year].iloc[0, 1:].values
    data_norm = current_data / base_2016
    all_data_norm.extend(data_norm)

# 自动计算最优量程（覆盖99%数据，留出少量余量）
data_min = np.min(all_data_norm)
data_max = np.max(all_data_norm)
range_min = max(0, np.floor(data_min * 10) / 10)  # 向下取整到0.1
range_max = np.ceil(data_max * 10) / 10  # 向上取整到0.1

# 绘制每个年份的雷达图（统一实线+渐变色彩）
for i, year in enumerate(years):
    current_data = df[df['year'] == year].iloc[0, 1:].values
    data_norm = current_data / base_2016
    data_norm = np.append(data_norm, data_norm[0])  # 闭合数据

    # 线条属性（年份越新越突出）
    linewidth = 1.2 + i * 0.45
    markersize = 6 + i * 0.6
    alpha = 0.65 + i * 0.035

    # 绘制雷达线
    ax.plot(angles, data_norm, 'o-',
            linewidth=linewidth,
            color=colors[i],
            label=str(year),
            alpha=alpha,
            markersize=markersize,
            markeredgecolor='white',
            markeredgewidth=1.8)

# 设置自动优化的量程
ax.set_ylim(range_min, range_max)

# 根据量程自动设置刻度（确保刻度数量合理）
tick_interval = max(0.2, (range_max - range_min) / 5)
tick_positions = np.arange(range_min, range_max + tick_interval, tick_interval)
ax.set_yticks(tick_positions)
ax.set_yticklabels([f'{x:.1f}x' for x in tick_positions],
                   fontsize=11, fontweight='bold', alpha=0.85)

# 放大角度标签
ax.set_xticks(angles[:-1])
ax.set_xticklabels(indices, fontsize=13, fontweight='bold', ha='center')

# 强化背景网格
ax.grid(True, alpha=0.7, linestyle='-', linewidth=1.2, color='#E0E0E0')
ax.spines['polar'].set_linewidth(1.8)
ax.spines['polar'].set_color('#CCCCCC')

# 添加标题（显示实际量程范围）
ax.set_title(f'Inflation Structure Evolution (2016-2025)\n(Base: 2016=1.0x, Range: {range_min}x-{range_max}x)',
             fontsize=18, fontweight='bold', pad=35)

# 单一颜色条（替代图例，避免遮挡）
sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(vmin=min(years), vmax=max(years)))
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, orientation='vertical', pad=0.18, shrink=0.85)
cbar.set_label('Year', fontsize=14, fontweight='bold', labelpad=15)
cbar.ax.tick_params(labelsize=12)

# 调整布局
plt.subplots_adjust(right=0.82)

# 保存图片（使用指定路径）
save_dir = r'C:\Users\15963\Desktop\APMCM-training\results\figures\ques5\价格与通胀'
import os

if not os.path.exists(save_dir):
    os.makedirs(save_dir)
plt.savefig(os.path.join(save_dir, 'inflation_radar_auto_range.png'),
            dpi=300, bbox_inches='tight', facecolor='white')
plt.close()