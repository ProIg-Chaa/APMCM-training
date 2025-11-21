import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 设置绘图风格和中文显示
sns.set_style("whitegrid")
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def analyze_tariff_impact(file_path):
    # 1. 从 CSV 文件加载数据
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print("文件未找到，请检查路径。")
        return
    except Exception as e:
        print(f"数据加载失败: {e}")
        return

    # **关键修正**：清理并统一列名：小写化并移除所有空格
    df.columns = df.columns.str.lower().str.replace(' ', '_', regex=False).str.strip('_')
    
    # 2. 数据清洗
    def clean_numeric_col(x):
        if isinstance(x, str):
            x = x.replace(' (annualized)', '').replace(',', '')
            if '/' in x:
                x = x.split('/')[0]
        return x

    cols_to_clean = [col for col in df.columns if col != 'year']

    for col in cols_to_clean:
        df[col] = df[col].apply(clean_numeric_col)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna(subset=['year']).sort_values('year')

    # 3. 构建经济指标
    df['Cost_Rare_Earths'] = df.get('rare_earths_export_unit_price')
    df['Cost_Lithium'] = df.get('lithium_export_unit_price')
    df['Reshoring_Employment'] = df.get('manufacturing_employment')
    df['Reshoring_Investment'] = df.get('fixed_asset_investment')
    df['Reshoring_Production'] = df.get('industrial_production_index')
    df['Ag_Export_Value'] = df.get('soybeans_export_value')

    # 4. 相关性矩阵
    indicators = ['Cost_Rare_Earths', 'Cost_Lithium', 
                  'Reshoring_Employment', 'Reshoring_Investment', 'Reshoring_Production',
                  'Ag_Export_Value']
    
    corr_matrix = df[indicators].corr()
    print("--- 关键指标相关性矩阵 (Correlation Matrix) ---")
    print(corr_matrix)
    
    # 4. 模型分析：相关性矩阵
    indicators = ['Cost_Rare_Earths', 'Cost_Lithium', 
                'Reshoring_Employment', 'Reshoring_Investment', 'Reshoring_Production',
                'Ag_Export_Value']

    corr_matrix = df[indicators].corr()

    print("--- 关键指标相关性矩阵 (Correlation Matrix) ---")
    print(corr_matrix)

    # 保存到 CSV 文件
    corr_matrix.to_csv('result.csv', encoding='utf-8-sig')
    print("相关性矩阵已保存到 result.csv")


    # 5. 可视化
    plt.figure(figsize=(15, 10))

    # 图1: 贸易价格信号
    plt.subplot(2, 2, 1)
    sns.lineplot(data=df, x='year', y='Cost_Rare_Earths', marker='o', label='稀土出口单价 (Rare Earths)')
    sns.lineplot(data=df, x='year', y='Cost_Lithium', marker='s', label='锂出口单价 (Lithium)')
    plt.title('贸易冲突：关键原材料出口价格信号')
    plt.ylabel('单位价格')
    plt.legend()

    # 图2: 制造业回流表现
    plt.subplot(2, 2, 2)
    ax1 = plt.gca()
    sns.lineplot(data=df, x='year', y='Reshoring_Employment', ax=ax1, color='green', marker='o', label='制造业就业 (Employment)')
    ax2 = ax1.twinx()
    sns.lineplot(data=df, x='year', y='Reshoring_Investment', ax=ax2, color='red', marker='s', label='固定资产投资 (Investment)')
    ax1.set_ylabel('就业人数 (千人)')
    ax2.set_ylabel('投资额 (十亿美元)')
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    plt.title('回流指标：就业与投资')

    # 图3: 工业生产指数
    plt.subplot(2, 2, 3)
    sns.lineplot(data=df, x='year', y='Reshoring_Production', marker='o', color='purple')
    plt.title('工业生产指数年度趋势')
    plt.ylabel('工业生产指数')
    
    # 图4: 农业受损情况
    plt.subplot(2, 2, 4)
    sns.lineplot(data=df, x='year', y='Ag_Export_Value', marker='o', color='orange')
    plt.title('农业冲击：大豆出口额')
    plt.ylabel('出口额 (十亿美元)')

    plt.tight_layout()
    # plt.show()  # 本地运行时可取消注释显示图像

# 运行分析
if __name__ == "__main__":
    analyze_tariff_impact('allprocessed.csv')  # 直接读取 CSV 文件
