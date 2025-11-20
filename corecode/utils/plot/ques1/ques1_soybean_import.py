import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ---------------------- 基础配置 ----------------------
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['legend.framealpha'] = 0.9
plt.rcParams['figure.dpi'] = 100

# 路径配置
data_folder = r'C:\Users\15963\Desktop\APMCM-training\data\processed\ques1\中国大豆进口'
save_path = r'/results/figures/ques1/soybean_import'
os.makedirs(save_path, exist_ok=True)

# 国家配置
country_mapping = {'美国': 'USA', '巴西': 'Brazil', '阿根廷': 'Argentina'}
country_colors = {
    'USA': '#2E86AB',  # 深蓝色
    'Brazil': '#A23B72',  # 紫红色
    'Argentina': '#F18F01'  # 橙色
}
country_names = {'USA': 'USA', 'Brazil': 'Brazil', 'Argentina': 'Argentina'}

# CSV列名
actual_cols = {'date_col': '数据年月', 'country_col': '贸易伙伴名称', 'value_col': '美元'}

# 政策时间点
policy_2018 = pd.to_datetime('2018-07')
policy_2025 = pd.to_datetime('2025-04')


# ---------------------- 数据读取与处理 ----------------------
def load_soybean_monthly_data():
    all_monthly_data = []
    for file_name in os.listdir(data_folder):
        if not file_name.endswith('.csv'):
            continue
        try:
            file_parts = file_name.split('_')
            year = int(file_parts[0])
            cn_country = file_parts[1]
            en_country = country_mapping[cn_country]
        except:
            continue

        file_path = os.path.join(data_folder, file_name)
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            if not all(col in df.columns for col in actual_cols.values()):
                continue

            df_clean = df[[actual_cols['date_col'], actual_cols['country_col'], actual_cols['value_col']]].copy()
            df_clean.columns = ['data_year_month', 'partner', 'usd']
            df_clean['data_year_month'] = df_clean['data_year_month'].astype(str)
            df_clean['date'] = pd.to_datetime(
                df_clean['data_year_month'].str[:4] + '-' + df_clean['data_year_month'].str[4:],
                format='%Y-%m', errors='coerce'
            )
            df_clean = df_clean.dropna(subset=['date'])

            monthly_sum = df_clean.groupby('date')['usd'].sum().reset_index()
            monthly_sum['country'] = en_country
            monthly_sum['import_value_100m_usd'] = monthly_sum['usd'] / 100000000
            all_monthly_data.append(monthly_sum)
        except:
            continue

    if not all_monthly_data:
        raise ValueError("No valid data found!")
    merged_data = pd.concat(all_monthly_data, ignore_index=True)
    return merged_data.sort_values('date').reset_index(drop=True)


def prepare_plot_data(raw_data):
    # 构建完整日期序列（2017-01至2025-12）
    full_dates = pd.date_range(start='2017-01', end='2025-12', freq='MS')
    full_df = pd.DataFrame({'date': full_dates})

    # 处理每个国家数据
    for en_country in country_mapping.values():
        country_data = raw_data[raw_data['country'] == en_country][['date', 'import_value_100m_usd']].copy()
        country_data = country_data.set_index('date').reindex(full_dates).reset_index()
        country_data = country_data.rename(columns={'index': 'date', 'import_value_100m_usd': en_country})
        country_data[en_country] = country_data[en_country].ffill().bfill().fillna(0)
        full_df = pd.merge(full_df, country_data[['date', en_country]], on='date', how='left')

    full_df['total'] = full_df[list(country_mapping.values())].sum(axis=1)
    return full_df


# 加载数据
soybean_data = load_soybean_monthly_data()
plot_df = prepare_plot_data(soybean_data)

# ---------------------- 图表1：月度进口额趋势图 ----------------------
plt.figure(figsize=(16, 8))
for country in ['USA', 'Brazil', 'Argentina']:
    plt.plot(
        plot_df['date'], plot_df[country],
        linewidth=2.5, color=country_colors[country],
        label=country_names[country], alpha=0.85,
        marker='o', markersize=4, markevery=6
    )

# 政策标注
plt.axvline(x=policy_2018, color='#6A994E', linestyle='--', linewidth=2, alpha=0.7)
plt.text(policy_2018, plot_df['total'].max() * 0.95,
         '2018 US Policy Adjustment',
         fontsize=11, fontweight='bold', color='#6A994E',
         bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='#6A994E', alpha=0.8),
         ha='center', va='bottom')

plt.axvline(x=policy_2025, color='#C73E1D', linestyle='--', linewidth=2, alpha=0.7)
plt.text(policy_2025, plot_df['total'].max() * 0.95,
         '2025 Reciprocal Tariff Policy',
         fontsize=11, fontweight='bold', color='#C73E1D',
         bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='#C73E1D', alpha=0.8),
         ha='center', va='bottom')

plt.title('Monthly Soybean Import Value to China (2017-2025)', fontsize=18, fontweight='bold', pad=25)
plt.xlabel('Date', fontsize=14, labelpad=10)
plt.ylabel('Import Value (100 Million USD)', fontsize=14, labelpad=10)
plt.grid(True, linestyle='--')
plt.legend(loc='upper left', fontsize=12, frameon=True, shadow=True)
plt.ylim(0, plot_df['total'].max() * 1.1)
plt.xticks(pd.date_range(start='2017-01', end='2025-12', freq='6MS'),
           rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(save_path, '1_monthly_import_trend.png'), dpi=300, bbox_inches='tight')
plt.close()

# ---------------------- 图表2：堆叠面积图 ----------------------
plt.figure(figsize=(16, 8))
plt.stackplot(
    plot_df['date'],
    plot_df['USA'], plot_df['Brazil'], plot_df['Argentina'],
    labels=[country_names[c] for c in ['USA', 'Brazil', 'Argentina']],
    colors=[country_colors[c] for c in ['USA', 'Brazil', 'Argentina']],
    alpha=0.7, edgecolor='white', linewidth=0.5
)

# 政策标注
plt.axvline(x=policy_2018, color='#6A994E', linestyle='--', linewidth=2, alpha=0.7)
plt.text(policy_2018, plot_df['total'].max() * 0.95,
         '2018 US Policy Adjustment',
         fontsize=11, fontweight='bold', color='#6A994E',
         bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='#6A994E', alpha=0.8),
         ha='center', va='bottom')

plt.axvline(x=policy_2025, color='#C73E1D', linestyle='--', linewidth=2, alpha=0.7)
plt.text(policy_2025, plot_df['total'].max() * 0.95,
         '2025 Policy Implementation',
         fontsize=11, fontweight='bold', color='#C73E1D',
         bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='#C73E1D', alpha=0.8),
         ha='center', va='bottom')

plt.title('Soybean Import Share by Country (2017-2025)', fontsize=18, fontweight='bold', pad=25)
plt.xlabel('Date', fontsize=14, labelpad=10)
plt.ylabel('Import Value (100 Million USD)', fontsize=14, labelpad=10)
plt.grid(True, linestyle='--', axis='y')
plt.legend(loc='upper left', fontsize=12, frameon=True, shadow=True)
plt.ylim(0, plot_df['total'].max() * 1.1)
plt.xticks(pd.date_range(start='2017-01', end='2025-12', freq='6MS'),
           rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(save_path, '2_import_share_stack.png'), dpi=300, bbox_inches='tight')
plt.close()

# ---------------------- 图表3：同比增长率图（-400%至400%量程） ----------------------
plt.figure(figsize=(16, 10))
for country in ['USA', 'Brazil', 'Argentina']:
    # 初始化浮点型列
    plot_df[f'{country}_yoy'] = np.float64(0.0)

    # 计算同比增长率
    for i in range(12, len(plot_df)):
        prev_val = plot_df.loc[i - 12, country]
        if prev_val != 0:
            growth_rate = float((plot_df.loc[i, country] - prev_val) / prev_val * 100)
            plot_df.loc[i, f'{country}_yoy'] = growth_rate
        else:
            plot_df.loc[i, f'{country}_yoy'] = plot_df.loc[i - 1, f'{country}_yoy'] if i > 12 else 0.0

    # 平滑处理
    plot_df[f'{country}_yoy_smooth'] = plot_df[f'{country}_yoy'].rolling(
        window=5, min_periods=1, center=True
    ).mean()

    # 绘制曲线
    plt.plot(
        plot_df['date'], plot_df[f'{country}_yoy_smooth'],
        linewidth=2.5, color=country_colors[country],
        label=country_names[country], alpha=0.9,
        solid_capstyle='round'
    )

    # 填充区域
    plt.fill_between(
        plot_df['date'], plot_df[f'{country}_yoy_smooth'], 0,
        alpha=0.2, color=country_colors[country]
    )

# 基准线和政策标注
plt.axhline(y=0, color='black', linestyle='-', linewidth=1.5, alpha=0.8)
plt.axvline(x=policy_2018, color='#6A994E', linestyle='--', linewidth=2, alpha=0.7)
plt.text(policy_2018, 300,
         '2018 US Policy Adjustment',
         fontsize=11, fontweight='bold', color='#6A994E',
         bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='#6A994E', alpha=0.8),
         ha='center')

plt.axvline(x=policy_2025, color='#C73E1D', linestyle='--', linewidth=2, alpha=0.7)
plt.text(policy_2025, 300,
         '2025 Tariff Policy',
         fontsize=11, fontweight='bold', color='#C73E1D',
         bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='#C73E1D', alpha=0.8),
         ha='center')

plt.title('YoY Growth Rate of Soybean Imports (2017-2025)', fontsize=18, fontweight='bold', pad=25)
plt.xlabel('Date', fontsize=14, labelpad=10)
plt.ylabel('YoY Growth Rate (%)', fontsize=14, labelpad=10)
plt.grid(True, linestyle='--', alpha=0.4)
plt.legend(loc='upper right', fontsize=12, frameon=True, shadow=True)
plt.ylim(-400, 400)  # 设置-400%至400%量程
plt.xlim(plot_df['date'].min(), plot_df['date'].max())
plt.xticks(pd.date_range(start='2017-01', end='2025-12', freq='6MS'),
           rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(save_path, '3_yoy_growth_rate.png'), dpi=300, bbox_inches='tight')
plt.close()

# ---------------------- 图表4：季节热力图 ----------------------
fig, axes = plt.subplots(1, 3, figsize=(22, 8), sharey=True)
fig.suptitle('Seasonal Soybean Import Patterns (2017-2025)', fontsize=20, fontweight='bold', y=1.05)
all_years = list(range(2017, 2026))
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

for idx, country in enumerate(['USA', 'Brazil', 'Argentina']):
    country_data = plot_df[['date', country]].copy()
    country_data['year'] = country_data['date'].dt.year
    country_data['month'] = country_data['date'].dt.month

    heatmap_data = country_data.pivot_table(
        index='year', columns='month', values=country, aggfunc='sum'
    ).fillna(0).round(2)

    for year in all_years:
        if year not in heatmap_data.index:
            heatmap_data.loc[year] = 0
    heatmap_data = heatmap_data.reindex(all_years)

    # 绘制热力图
    im = axes[idx].imshow(heatmap_data.values, cmap='Blues', aspect='auto', vmin=0)

    axes[idx].set_title(f'{country_names[country]}', fontsize=16, fontweight='bold', pad=15)
    axes[idx].set_xlabel('Month', fontsize=13, labelpad=10)
    if idx == 0:
        axes[idx].set_ylabel('Year', fontsize=13, labelpad=10)

    axes[idx].set_xticks(range(12))
    axes[idx].set_xticklabels(months, fontsize=10, rotation=45, ha='right')
    axes[idx].set_yticks(range(len(all_years)))
    axes[idx].set_yticklabels(all_years, fontsize=10)

    # 标注数值
    for y in range(len(all_years)):
        for x in range(12):
            value = heatmap_data.iloc[y, x]
            if value > 10:
                axes[idx].text(
                    x, y, f'{value:.0f}',
                    ha='center', va='center', fontsize=9, fontweight='bold',
                    color='white' if value > 30 else 'black'
                )

# 调整布局
plt.subplots_adjust(right=0.88, top=0.9, bottom=0.1, wspace=0.1)
cbar_ax = fig.add_axes([0.9, 0.15, 0.02, 0.7])
cbar = fig.colorbar(im, cax=cbar_ax)
cbar.set_label('Import Value (100 Million USD)', fontsize=12, labelpad=10)

plt.savefig(os.path.join(save_path, '4_seasonal_heatmap.png'), dpi=300, bbox_inches='tight')
plt.close()

# ---------------------- 图表5：年度柱状对比图 ----------------------
yearly_df = plot_df.copy()
yearly_df['year'] = yearly_df['date'].dt.year
yearly_summary = yearly_df.groupby('year').agg({
    'USA': 'sum', 'Brazil': 'sum', 'Argentina': 'sum'
}).round(2)

plt.figure(figsize=(14, 8))
x = np.arange(len(yearly_summary.index))
width = 0.25

plt.bar(x - width, yearly_summary['USA'], width, label='USA', color=country_colors['USA'], alpha=0.8)
plt.bar(x, yearly_summary['Brazil'], width, label='Brazil', color=country_colors['Brazil'], alpha=0.8)
plt.bar(x + width, yearly_summary['Argentina'], width, label='Argentina', color=country_colors['Argentina'], alpha=0.8)

# 政策标注
plt.axvline(x=1.5, color='#6A994E', linestyle='--', linewidth=2, alpha=0.7)
plt.text(1.5, yearly_summary.max().max() * 0.95,
         '2018 US Policy', fontsize=11, fontweight='bold', color='#6A994E',
         bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='#6A994E', alpha=0.8),
         ha='center', va='bottom')

plt.axvline(x=8, color='#C73E1D', linestyle='--', linewidth=2, alpha=0.7)
plt.text(8, yearly_summary.max().max() * 0.95,
         '2025 Policy', fontsize=11, fontweight='bold', color='#C73E1D',
         bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='#C73E1D', alpha=0.8),
         ha='center', va='bottom')

plt.title('Annual Soybean Import by Country (2017-2025)', fontsize=18, fontweight='bold', pad=25)
plt.xlabel('Year', fontsize=14, labelpad=10)
plt.ylabel('Import Value (100 Million USD)', fontsize=14, labelpad=10)
plt.xticks(x, yearly_summary.index)
plt.legend(loc='upper left', fontsize=12, frameon=True, shadow=True)
plt.grid(True, linestyle='--', axis='y')
plt.ylim(0, yearly_summary.max().max() * 1.1)
plt.tight_layout()
plt.savefig(os.path.join(save_path, '5_annual_import_bar.png'), dpi=300, bbox_inches='tight')
plt.close()

print(f"所有图表已保存至: {save_path}")
print("图表生成完成！")