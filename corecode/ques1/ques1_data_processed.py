import pandas as pd
import numpy as np

# =====================================================
# 1. 读入数据（请把文件名替换成你的）
# =====================================================

# 中国从美国/巴西/阿根廷进口的大豆（量、值）
df_trade = pd.read_csv(r"D:\GS_LearningAndWork\MATH-model\APMCM-training\data\processed\ques1\中国大豆进口\formalresult.csv")
# 示例列：year, origin (US/Brazil/Argentina), import_volume, import_value

# 各国年度产量、库存（USDA PSD）
df_supply = pd.read_csv(r"D:\GS_LearningAndWork\MATH-model\APMCM-training\data\processed\ques1\各国出口数据\soybean_production_export_consumption_stock.csv")
# 示例列：year, country, production, ending_stocks

# 国际价格（期货均价）、FOB价格（如有）
df_price = pd.read_csv(r"D:\GS_LearningAndWork\MATH-model\APMCM-training\data\processed\ques1\大豆价格\formalresult.csv")
# 示例列：year, futures_price, us_fob, br_fob, ar_fob

# 汇率（人民币兑美元，美元兑巴西雷亚尔/阿根廷比索）
df_fx = pd.read_csv(r"D:\GS_LearningAndWork\MATH-model\APMCM-training\data\processed\ques1\exrate\exrate.csv")
# 示例列：year, rmb_usd, usd_brl, usd_ars

# 关税（MFN + 加征关税）
df_tariff = pd.read_csv(r"D:\GS_LearningAndWork\MATH-model\APMCM-training\data\processed\ques1\tariff\tariff.csv")
# 示例列：year, origin, mfn_rate, additional_rate

# =====================================================
# 2. 数据预处理：统一国家名称格式
# =====================================================

country_map = {
    "US": "United States",
    "Brazil": "Brazil",
    "Argentina": "Argentina",
    "USA": "United States"
}

df_trade["origin"] = df_trade["origin"].replace(country_map)
df_tariff["origin"] = df_tariff["origin"].replace(country_map)
df_supply["country"] = df_supply["country"].replace(country_map)

# =====================================================
# 3. 合并面板数据
# =====================================================

# 贸易数据作为主体
panel = df_trade.copy()

# 合并关税
panel = panel.merge(df_tariff, on=["year", "origin"], how="left")

# 合并供给数据
panel = panel.merge(df_supply, left_on=["year", "origin"],
                    right_on=["year", "country"], how="left")
panel.drop(columns=["country"], inplace=True)

# 合并价格
panel = panel.merge(df_price, on="year", how="left")

# 合并汇率
panel = panel.merge(df_fx, on="year", how="left")

# =====================================================
# 4. 清洗：生成常用变量
# =====================================================

# 到岸价（示例，基于 FOB + 期货价调整，你可以按自己公式替换）
panel["cif_price"] = panel.apply(
    lambda row: row[f"{row['origin'][:2].lower()}_fob"]
    if f"{row['origin'][:2].lower()}_fob" in panel.columns
    else row["futures_price"],
    axis=1
)

# 实际关税
panel["total_tariff"] = panel["mfn_rate"] + panel["additional_rate"]

# 价格含关税
panel["cif_tax_price"] = panel["cif_price"] * (1 + panel["total_tariff"])

# 贸易单价
panel["unit_value"] = panel["import_value"] / panel["import_volume"]

# 滞后变量
panel = panel.sort_values(by=["origin", "year"])
panel["lag_import"] = panel.groupby("origin")["import_volume"].shift(1)
panel["lag_price"] = panel.groupby("origin")["cif_price"].shift(1)

# 缺失处理
panel.replace([np.inf, -np.inf], np.nan, inplace=True)
panel.fillna(method="bfill", inplace=True)
panel.fillna(method="ffill", inplace=True)

# =====================================================
# 5. 输出整理好的面板文件
# =====================================================
panel.to_csv("panel_cleaned.csv", index=False)
print("✓ 已生成 panel_cleaned.csv")

# =====================================================
# 6. 基期描述（例如 2023 年）
# =====================================================

if "year" in panel.columns:
    latest_year = panel["year"].max()

    print("\n===== 中国进口来源份额 =====")
    base = panel[panel["year"] == latest_year]

    base_share = (
        base.groupby("origin")["import_volume"].sum()
        / base["import_volume"].sum()
    )

    print(base_share)

    print("\n===== 年度价格趋势 =====")
    price_trend = panel.groupby("year")["unit_value"].mean()
    print(price_trend)

# =====================================================
# 7. 为后续模型准备的一些核心变量检查
# =====================================================

required = [
    "import_volume", "cif_price", "cif_tax_price",
    "production", "ending_stocks", "rmb_usd", "total_tariff"
]

missing_cols = [c for c in required if c not in panel.columns]

if len(missing_cols) == 0:
    print("\n✓ 面板中用于建模的关键变量齐全")
else:
    print("\n⚠️ 缺少以下关键变量，请检查：", missing_cols)

