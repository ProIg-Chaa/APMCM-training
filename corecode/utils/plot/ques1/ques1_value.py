import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import os

# ---------------------- 基础配置 ----------------------
plt.rcParams['font.sans-serif'] = ['Arial', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 数据路径
data_path = r"C:\Users\15963\Desktop\APMCM-training\data\processed\ques1\大豆价格"
file_name = "PSOYBUSDM.csv"
file_path = os.path.join(data_path, file_name)

# 保存路径
save_path = r"C:\Users\15963\Desktop\APMCM-training\results\figures\ques1\value"
os.makedirs(save_path, exist_ok=True)

# ---------------------- 数据读取与预处理 ----------------------
df = pd.read_csv(file_path, encoding='utf-8')
df['observation_date'] = pd.to_datetime(df['observation_date'])
df['year'] = df['observation_date'].dt.year
df['month'] = df['observation_date'].dt.month

# 构建年度-月度价格矩阵
price_pivot = df.pivot_table(
    index='year',
    columns='month',
    values='PSOYBUSDM',
    aggfunc='mean'
)

# ---------------------- 自定义配色 ----------------------
colors = ['#2E86AB', '#A23B72', '#F18F01']
cmap = LinearSegmentedColormap.from_list('soybean_cmap', colors, N=100)

# ---------------------- 绘制热力图 ----------------------
fig, ax = plt.subplots(figsize=(14, 8))

# 热力图主体
im = ax.imshow(price_pivot.values, cmap=cmap, aspect='auto')

# 坐标轴设置
ax.set_xticks(np.arange(len(price_pivot.columns)))
ax.set_yticks(np.arange(len(price_pivot.index)))
ax.set_xticklabels([f'M{m}' for m in price_pivot.columns])  # M1-M12表示月份
ax.set_yticklabels(price_pivot.index)

# 旋转x轴标签
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

# 添加数值标注（跳过NaN值）
for i in range(len(price_pivot.index)):
    for j in range(len(price_pivot.columns)):
        if not np.isnan(price_pivot.iloc[i, j]):
            text = ax.text(j, i, f'{price_pivot.iloc[i, j]:.1f}',
                           ha="center", va="center", color="white", fontsize=8)

# 颜色条
cbar = ax.figure.colorbar(im, ax=ax)
cbar.ax.set_ylabel('PSOYBUSDM Price', rotation=-90, va="bottom", fontsize=12)

# 标题与保存
ax.set_title('Soybean Price Heatmap (Year × Month) 2014-2024', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(save_path, 'price_heatmap.png'), dpi=300, bbox_inches='tight')
plt.close()

print(f"价格热力图已保存至：{save_path}")