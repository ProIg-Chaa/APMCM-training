import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------------------- 数据路径配置 ----------------------
data_path = r"C:\Users\15963\Desktop\APMCM-training\data\processed\ques1\中国大豆进口"
file_name = "formalresult.csv"
file_path = os.path.join(data_path, file_name)

save_path = r"C:\Users\15963\Desktop\APMCM-training\results\figures\ques1\soybean_import\formalresult"
os.makedirs(save_path, exist_ok=True)

# ---------------------- 数据读取与预处理 ----------------------
df = pd.read_csv(file_path, encoding='utf-8')

# 确保列名标准化（根据实际数据列名调整，若已匹配可跳过）
# 假设数据列名为：year, origin, import_volume, import_value（若不同请替换）
if not all(col in df.columns for col in ["year", "origin", "import_volume", "import_value"]):
    # 若列名不同，手动映射（示例：根据实际列名修改）
    df.rename(columns={
        "年份": "year",
        "来源国": "origin",
        "进口量": "import_volume",
        "进口额": "import_value"
    }, inplace=True)

df["year"] = df["year"].astype(int)  # 确保年份为整数

# ---------------------- 绘图样式配置 ----------------------
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
colors = {
    'Brazil': '#A23B72',
    'United States': '#C73E1D',
    'Argentina': '#F18F01',
    '巴西': '#A23B72',    # 兼容中文国名
    '美国': '#C73E1D',
    '阿根廷': '#F18F01'
}
markers = {
    'Brazil': 's',
    'United States': 'D',
    'Argentina': '^',
    '巴西': 's',          # 兼容中文国名
    '美国': 'D',
    '阿根廷': '^'
}

# ---------------------- 图表1：各国进口量趋势折线图 ----------------------
plt.figure(figsize=(12, 6))
for country in df["origin"].unique():
    country_data = df[df["origin"] == country]
    plt.plot(
        country_data["year"], country_data["import_volume"],
        linewidth=3, color=colors.get(country, '#2E86AB'),
        marker=markers.get(country, 'o'), markersize=7, label=country
    )

plt.title("Soybean Import Volume to China (2017-2025)", fontsize=16, fontweight='bold')
plt.xlabel("Year", fontsize=14)
plt.ylabel("Import Volume (1000 MT)", fontsize=14)
plt.legend(loc='upper left', fontsize=12)
plt.grid(linestyle='--', alpha=0.3)
plt.xticks(df["year"].unique())
plt.tight_layout()
plt.savefig(os.path.join(save_path, '1_import_volume_trend.png'), dpi=300, bbox_inches='tight')
plt.close()

# ---------------------- 图表2：进口量占比堆叠柱状图 ----------------------
yearly_total = df.groupby("year")["import_volume"].sum().reset_index()
df_with_ratio = df.merge(yearly_total, on="year", suffixes=("", "_total"))
df_with_ratio["ratio"] = (df_with_ratio["import_volume"] / df_with_ratio["import_volume_total"]) * 100

plt.figure(figsize=(12, 6))
bottom = [0] * len(yearly_total)
for country in df["origin"].unique():
    country_ratio = df_with_ratio[df_with_ratio["origin"] == country]["ratio"].values
    plt.bar(
        yearly_total["year"], country_ratio, bottom=bottom,
        color=colors.get(country, '#2E86AB'), alpha=0.8, label=country
    )
    bottom = bottom + country_ratio

plt.title("Soybean Import Volume Share to China (2017-2025)", fontsize=16, fontweight='bold')
plt.xlabel("Year", fontsize=14)
plt.ylabel("Import Share (%)", fontsize=14)
plt.legend(loc='upper left', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.3)
plt.xticks(yearly_total["year"])
plt.tight_layout()
plt.savefig(os.path.join(save_path, '2_import_volume_share.png'), dpi=300, bbox_inches='tight')
plt.close()

# ---------------------- 图表3：进口量-金额关联散点图 ----------------------
plt.figure(figsize=(10, 6))
for country in df["origin"].unique():
    country_data = df[df["origin"] == country]
    plt.scatter(
        country_data["import_volume"], country_data["import_value"],
        s=100, color=colors.get(country, '#2E86AB'),
        marker=markers.get(country, 'o'), alpha=0.8, label=country
    )
    # 添加年份标注
    for idx, row in country_data.iterrows():
        plt.text(row["import_volume"], row["import_value"], str(row["year"]),
                 fontsize=9, ha='center', va='bottom')

plt.title("Import Volume vs Import Value (2017-2025)", fontsize=16, fontweight='bold')
plt.xlabel("Import Volume (1000 MT)", fontsize=14)
plt.ylabel("Import Value (USD Million)", fontsize=14)
plt.legend(loc='upper left', fontsize=12)
plt.grid(linestyle='--', alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(save_path, '3_volume_vs_value.png'), dpi=300, bbox_inches='tight')
plt.close()

print(f"所有图表已保存至：{save_path}")
print("生成文件：")
print("1. 1_import_volume_trend.png（进口量趋势图）")
print("2. 2_import_volume_share.png（进口量占比图）")
print("3. 3_volume_vs_value.png（量价关联图）")