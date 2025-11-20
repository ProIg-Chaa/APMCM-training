import pandas as pd
import glob
import os

# 你的文件夹路径
folder = r"D:\GS_LearningAndWork\MATH-model\APMCM-training\data\processed\ques1\中国大豆进口"

# 获取所有 csv 文件
csv_files = glob.glob(os.path.join(folder, "*.csv"))

print("找到的文件：", csv_files)

# 读取并合并
dfs = []
for file in csv_files:
    df = pd.read_csv(file)
    dfs.append(df)

merged = pd.concat(dfs, ignore_index=True)

# 如果有重复行，可去重
merged = merged.drop_duplicates()

# 保存
out_path = r"D:\GS_LearningAndWork\MATH-model\APMCM-training\data\processed\ques1\中国大豆进口\all.csv"
merged.to_csv(out_path, index=False)

print("合并完成！输出：all.csv")
