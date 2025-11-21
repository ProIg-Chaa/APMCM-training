import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 设置中文和绘图风格
sns.set_style("whitegrid")
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def analyze_and_visualize_correlation(file_path='result.csv'):
    # 1. 从 CSV 文件读取相关性矩阵
    try:
        corr_df = pd.read_csv(file_path, index_col=0)
    except Exception as e:
        print(f"读取 CSV 失败: {e}")
        return

    # 2. 生成相关性热力图
    plt.figure(figsize=(9, 8))
    sns.heatmap(corr_df, 
                annot=True, 
                fmt=".2f", 
                cmap='coolwarm', 
                center=0,
                linewidths=.5,
                linecolor='black',
                cbar_kws={'label': '相关系数'})
    plt.title('贸易冲突与经济指标相关性热力图', fontsize=16)
    plt.tight_layout()
    plt.savefig('correlation_heatmap.png')  # 保存图像
    print("已生成相关性热力图: correlation_heatmap.png")

    # 3. 提取和排名关键结论（绝对值排序）
    print("\n--- 关键关系排名（绝对值排序）---")
    
    # 使用矩阵的所有组合生成排名
    results = []
    cols = corr_df.columns
    for i, row_name in enumerate(cols):
        for j, col_name in enumerate(cols):
            if i < j:  # 只取上三角
                value = corr_df.loc[row_name, col_name]
                results.append({'关系': f'{row_name} vs {col_name}', '相关系数': value})

    results_df = pd.DataFrame(results)
    results_df['相关性强度'] = results_df['相关系数'].abs()
    results_df = results_df.sort_values(by='相关性强度', ascending=False).reset_index(drop=True)

    # 打印最强的前7个关系
    print(f"{'关系':<30}{'相关系数':<15}{'强度等级'}")
    print("-" * 60)

    def get_strength(r):
        if abs(r) >= 0.7: return "极强"
        if abs(r) >= 0.5: return "强"
        if abs(r) >= 0.3: return "中等"
        return "弱"

    for _, row in results_df.head(7).iterrows():
        strength = get_strength(row['相关系数'])
        print(f"{row['关系']:<30}{row['相关系数']:-<15.4f}{strength}")

# 运行分析
if __name__ == "__main__":
    analyze_and_visualize_correlation('result.csv')
