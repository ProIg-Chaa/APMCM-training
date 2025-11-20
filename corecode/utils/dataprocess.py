import pandas as pd

for i in range(2017,2026):
    df = pd.read_csv(
        rf"D:\GS_LearningAndWork\MATH-model\APMCM-training\data\raw\{i}.csv",
        encoding="gbk"
    )

    # 删除完全为空的列
    df = df.dropna(axis=1, how="all")

    df = df[["数据年月", "贸易伙伴名称", "美元"]]

    # 将“美元”转换为 float
    df["美元"] = (
        df["美元"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
        .astype(float)
    )

    # print(df.info())
    countries = ["美国", "阿根廷", "巴西"]

    for c in countries:
        df_c = df[df["贸易伙伴名称"] == c]
        out_path = rf"D:\GS_LearningAndWork\MATH-model\APMCM-training\data\processed\{i}_{c}_to_China.csv"
        df_c.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"已生成文件：{out_path}")
