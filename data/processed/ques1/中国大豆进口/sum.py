import pandas as pd

# 读取你合并后的数据
df = pd.read_csv(r"D:\GS_LearningAndWork\MATH-model\APMCM-training\data\processed\ques1\中国大豆进口\all.csv")

# 1. 提取年份（从前 4 位）
df["年份"] = df["数据年月"].astype(str).str[:4]

# 2. 按年份 + 国家求和
year_country_sum = (
    df.groupby(["年份", "贸易伙伴名称"], as_index=False)["美元"]
      .sum()
      .sort_values(["年份", "贸易伙伴名称"])
)

# 3. 保存输出
year_country_sum.to_csv("year_country_sum.csv", index=False)
