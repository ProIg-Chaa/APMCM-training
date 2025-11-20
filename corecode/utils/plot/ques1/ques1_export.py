import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------------------- 1. 数据读取与预处理 ----------------------
data_path = r'C:\Users\15963\Desktop\APMCM-training\data\processed\ques1\各国出口数据'
file_name = 'soybean_production_export_consumption_stock.csv'
file_path = os.path.join(data_path, file_name)

# 读取数据（注意首列是索引列）
df = pd.read_csv(file_path, index_col=0, encoding='utf-8')

# 提取年份列
years = [str(year) for year in range(2015, 2026)]

# 定义颜色映射
colors = {
    'Argentina': '#F18F01',
    'Brazil': '#A23B72',
    'China': '#2E86AB',
    'United States': '#C73E1D'
}
markers = {
    'Argentina': '^',
    'Brazil': 's',
    'China': 'o',
    'United States': 'D'
}

# 保存路径
save_path = (r'C:\Users\15963\Desktop\APMCM-training\results\figures\ques1\export'
             r'')
os.makedirs(save_path, exist_ok=True)


# ---------------------- 通用绘图函数 ----------------------
def plot_indicator_trend(indicator_name, title_suffix):
    """绘制指定指标的趋势图"""
    # 筛选数据
    indicator_df = df[df['Attribute'] == indicator_name].copy()

    # 转换为长格式
    trend_data = indicator_df.melt(
        id_vars=['Country'],
        value_vars=years,
        var_name='Year',
        value_name=indicator_name
    )
    trend_data['Year'] = trend_data['Year'].astype(int)

    # 绘图
    plt.figure(figsize=(14, 8))
    for country in indicator_df['Country'].unique():
        country_data = trend_data[trend_data['Country'] == country]
        plt.plot(
            country_data['Year'], country_data[indicator_name],
            linewidth=3, color=colors[country], marker=markers[country],
            markersize=7, label=country, alpha=0.9
        )

    plt.title(f'Soybean {title_suffix} Trend by Country (2015-2025)', fontsize=18, fontweight='bold')
    plt.xlabel('Year', fontsize=14)
    plt.ylabel(f'{title_suffix} (1000 MT)', fontsize=14)
    plt.legend(loc='upper left', fontsize=12)
    plt.grid(linestyle='--', alpha=0.3)
    plt.xticks(range(2015, 2026, 1))
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, f'{indicator_name.lower().replace(" ", "_")}_trend.png'), dpi=300,
                bbox_inches='tight')
    plt.close()


# ---------------------- 生成四类指标图表 ----------------------
# 1. Production（产量）
plot_indicator_trend('Production', 'Production')

# 2. Exports（出口）
plot_indicator_trend('Exports', 'Exports')

# 3. Domestic Consumption（国内消费）
plot_indicator_trend('Domestic Consumption', 'Domestic Consumption')

# 4. Ending Stocks（期末库存）
plot_indicator_trend('Ending Stocks', 'Ending Stocks')

# ---------------------- 额外：四大指标对比图（以中国为例） ----------------------
plt.figure(figsize=(14, 8))
china_data = df[df['Country'] == 'China']

# 提取中国各指标数据
china_production = china_data[china_data['Attribute'] == 'Production'][years].values.flatten()
china_exports = china_data[china_data['Attribute'] == 'Exports'][years].values.flatten()
china_consumption = china_data[china_data['Attribute'] == 'Domestic Consumption'][years].values.flatten()
china_stocks = china_data[china_data['Attribute'] == 'Ending Stocks'][years].values.flatten()

# 绘图（注意出口量量级差异，单独用右轴）
ax1 = plt.gca()
ax2 = ax1.twinx()

ax1.plot(years, china_production, linewidth=3, color='#2E86AB', marker='o', label='Production')
ax1.plot(years, china_consumption, linewidth=3, color='#A23B72', marker='s', label='Domestic Consumption')
ax1.plot(years, china_stocks, linewidth=3, color='#F18F01', marker='^', label='Ending Stocks')
ax2.plot(years, china_exports, linewidth=3, color='#C73E1D', marker='D', label='Exports')

ax1.set_xlabel('Year', fontsize=14)
ax1.set_ylabel('Volume (1000 MT)', fontsize=14, color='#2E86AB')
ax2.set_ylabel('Exports (1000 MT)', fontsize=14, color='#C73E1D')
ax1.tick_params(axis='y', labelcolor='#2E86AB')
ax2.tick_params(axis='y', labelcolor='#C73E1D')

# 合并图例
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=12)

plt.title('China Soybean Key Indicators (2015-2025)', fontsize=18, fontweight='bold')
plt.grid(linestyle='--', alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(save_path, 'china_indicators_comparison.png'), dpi=300, bbox_inches='tight')
plt.close()

print(f"所有指标图表已保存至：{save_path}")
print("生成文件列表：")
print("1. production_trend.png（产量趋势图）")
print("2. exports_trend.png（出口趋势图）")
print("3. domestic_consumption_trend.png（国内消费趋势图）")
print("4. ending_stocks_trend.png（期末库存趋势图）")
print("5. china_indicators_comparison.png（中国四大指标对比图）")