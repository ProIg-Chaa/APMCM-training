import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io

# 设置中文和绘图风格
sns.set_style("whitegrid")
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def analyze_and_visualize_correlation():
    # 1. 定义用户提供的相关性矩阵数据
    data = {
        '稀土成本冲击': [1.000000, -0.883834, 0.399957, 0.556128, 0.121165, 0.479498],
        '锂成本冲击': [-0.883834, 1.000000, -0.734001, -0.783281, -0.272180, -0.680350],
        '回流-就业': [0.399957, -0.734001, 1.000000, 0.807819, 0.583546, -0.007746],
        '回流-投资': [0.556128, -0.783281, 0.807819, 1.000000, 0.121772, 0.477880],
        '回流-产出': [0.121165, -0.272180, 0.583546, 0.121772, 1.000000, -0.498688],
        '农业出口值': [0.479498, -0.680350, -0.007746, 0.477880, -0.498688, 1.000000]
    }
    
    # 2. 创建 DataFrame
    index_names = list(data.keys())
    corr_df = pd.DataFrame(data, index=index_names)
    
    # 3. 生成相关性热力图 (Heatmap)
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
    plt.savefig('correlation_heatmap.png') # 保存图像供用户查看

    print("已生成相关性热力图: correlation_heatmap.png")
    
    # 4. 提取和排名关键结论 (使用标准格式打印)
    print("\n--- 关键关系排名（绝对值排序）---")
    
    # 关注与成本冲击和回流相关的核心交叉项
    analysis_focus = [
        ('锂成本冲击', '回流-投资'), 
        ('锂成本冲击', '回流-就业'), 
        ('锂成本冲击', '稀土成本冲击'), 
        ('锂成本冲击', '农业出口值'),
        ('稀土成本冲击', '回流-投资'),
        ('回流-投资', '回流-就业'),
        ('回流-就业', '回流-产出')
    ]
    
    results = []
    for row, col in analysis_focus:
        # 确保只取矩阵上三角部分或对称对
        value = corr_df.loc[row, col] if row in corr_df.index and col in corr_df.columns else corr_df.loc[col, row]
        results.append({'关系': f'{row} vs {col}', '相关系数': value})

    results_df = pd.DataFrame(results)
    results_df['相关性强度'] = results_df['相关系数'].abs()
    results_df = results_df.sort_values(by='相关性强度', ascending=False).reset_index(drop=True)
    
    # 打印最强的前7个关系，使用标准字符串格式化
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
    analyze_and_visualize_correlation()