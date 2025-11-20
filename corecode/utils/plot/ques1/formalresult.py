import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------------------- 基础配置 ----------------------
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 数据路径
file_path = r"C:\Users\15963\Desktop\APMCM-training\data\processed\ques1\中国大豆进口\formalresult.csv"
save_path = r"C:\Users\15963\Desktop\APMCM-training\results\figures\ques1\soybean_import\formalresult"
os.makedirs(save_path, exist_ok=True)

# ---------------------- 数据读取与预处理 ----------------------
try:
    df = pd.read_csv(file_path, encoding='utf-8')
except FileNotFoundError:
    print(f"Error: File not found - {file_path}")
    exit()

# 列名映射（兼容中英文）
column_mapping = {
    "年份": "year", "来源国": "origin", "进口量": "import_volume",
    "Year": "year", "Country": "origin", "Volume": "import_volume"
}
df.rename(columns=column_mapping, inplace=True)
df["year"] = df["year"].astype(int)

# 统一国家名称（兼容所有变体）
def standardize_country(country):
    if country in ['USA', 'US', '美国', 'United States']:
        return 'United States'
    elif country in ['巴西', 'Brazil']:
        return 'Brazil'
    elif country in ['阿根廷', 'Argentina']:
        return 'Argentina'
    else:
        return country

df['origin'] = df['origin'].apply(standardize_country)

# ---------------------- 绘图配置 ----------------------
colors = {
    'Brazil': '#A23B72',
    'United States': '#C73E1D',
    'Argentina': '#F18F01'
}
markers = {
    'Brazil': 's',
    'United States': 'D',
    'Argentina': '^'
}

# ---------------------- 绘制趋势图（英文注释） ----------------------
plt.figure(figsize=(12, 6))

# 绘制各国进口量趋势
for country in df["origin"].unique():
    country_data = df[df["origin"] == country]
    plt.plot(
        country_data["year"], country_data["import_volume"],
        linewidth=3, color=colors[country], marker=markers[country],
        markersize=7, label=country
    )

# 标注关税政策改革时间点（英文注释）
plt.axvline(x=2018, color='red', linestyle='--', linewidth=2, alpha=0.8, label='2018 Tariff Policy Reform')
plt.axvline(x=2025, color='orange', linestyle='--', linewidth=2, alpha=0.8, label='2025 Tariff Policy Reform')

# 图表标题与标签（全英文）
plt.title("Soybean Import Volume to China (2017-2025) - Tariff Policy Impact", fontsize=16, fontweight='bold')
plt.xlabel("Year", fontsize=14)
plt.ylabel("Import Volume (1000 MT)", fontsize=14)
plt.legend(loc='upper left', fontsize=12)
plt.grid(linestyle='--', alpha=0.3)
plt.xticks(sorted(df["year"].unique()))
plt.tight_layout()

# 保存图表
plt.savefig(os.path.join(save_path, 'import_volume_trend_with_policy_english.png'), dpi=300, bbox_inches='tight')
plt.close()

print(f"Chart saved to: {os.path.join(save_path, 'import_volume_trend_with_policy_english.png')}")