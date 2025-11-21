import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io

# 设置绘图风格和中文显示
sns.set_style("whitegrid")
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def analyze_tariff_impact(data_string):
    
    # 1. 直接从字符串加载数据 (使用io.StringIO来模拟文件读取)
    # 注意：这里我们只使用用户提供的头部和数据行
    # 原始数据中包含 import 价格和 value，但用户提供的简化数据中缺失，我们使用 Export 价格作为代理
    try:
        df = pd.read_csv(io.StringIO(data_string))
    except Exception as e:
        print(f"数据加载失败: {e}")
        return

    # **关键修正**：清理并统一列名：小写化并移除所有空格
    df.columns = df.columns.str.lower().str.replace(' ', '_', regex=False).str.strip('_')
    
    # 2. 数据清洗 (Data Cleaning)
    def clean_numeric_col(x):
        if isinstance(x, str):
            # 移除常见非数字字符，如 '(annualized)' 和 ','
            x = x.replace(' (annualized)', '').replace(',', '')
            # 处理类似 '10400/200' 的情况，取第一个值
            if '/' in x:
                x = x.split('/')[0]
        return x

    # 识别需要清洗的列（排除年份和文本列）
    cols_to_clean = [col for col in df.columns if col != 'year']

    # 应用清洗函数
    for col in cols_to_clean:
        df[col] = df[col].apply(clean_numeric_col)
        # 强制转换为数字，无法转换的变为NaN
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna(subset=['year']).sort_values('year')

    # 3. 构建经济指标 (Construct Economic Indicators)
    
    # A. 贸易冲突冲击指标 (使用 Export Unit Price 作为贸易价格信号代理)
    df['Cost_Rare_Earths'] = df['rare_earths_export_unit_price']
    df['Cost_Lithium'] = df['lithium_export_unit_price']

    # B. 制造业回流指标 (Reshoring Indicators)
    # 使用用户提供的简化列名
    df['Reshoring_Employment'] = df['manufacturing_employment']
    df['Reshoring_Investment'] = df['fixed_asset_investment']
    df['Reshoring_Production'] = df['industrial_production_index']

    # C. 农业指标 (Agriculture Impact)
    df['Ag_Export_Value'] = df['soybeans_export_value']

    # 4. 模型分析：相关性矩阵 (Correlation Analysis)
    indicators = ['Cost_Rare_Earths', 'Cost_Lithium', 
                  'Reshoring_Employment', 'Reshoring_Investment', 'Reshoring_Production',
                  'Ag_Export_Value']
    
    corr_matrix = df[indicators].corr()
    
    print("--- 关键指标相关性矩阵 (Correlation Matrix) ---")
    print(corr_matrix)

    # 5. 可视化 (Visualization)
    plt.figure(figsize=(15, 10))

    # 图1: 贸易价格信号 (Trade Price Signal)
    plt.subplot(2, 2, 1)
    sns.lineplot(data=df, x='year', y='Cost_Rare_Earths', marker='o', label='稀土出口单价 (Rare Earths)')
    sns.lineplot(data=df, x='year', y='Cost_Lithium', marker='s', label='锂出口单价 (Lithium)')
    plt.title('贸易冲突：关键原材料出口价格信号')
    plt.ylabel('单位价格')
    plt.legend()

    # 图2: 制造业回流表现 (Reshoring Performance)
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

    # 图3: 产出与价格的关系 (Production vs Price)
    plt.subplot(2, 2, 3)
    # 使用年份趋势来展现产出
    sns.lineplot(data=df, x='year', y='Reshoring_Production', marker='o', color='purple')
    plt.title('工业生产指数年度趋势')
    plt.ylabel('工业生产指数')
    
    # 图4: 农业受损情况 (Agriculture Impact)
    plt.subplot(2, 2, 4)
    sns.lineplot(data=df, x='year', y='Ag_Export_Value', marker='o', color='orange')
    plt.title('农业冲击：大豆出口额')
    plt.ylabel('出口额 (十亿美元)')

    plt.tight_layout()
    # plt.show() # 如果在本地环境中运行，请取消注释这行来显示图像

# 运行分析
if __name__ == "__main__":
    # 用户提供的完整数据字符串
    user_data = """year,industrial_production_index,capacity_utilization,manufacturing_employment,auto_employment,electronic_employment,machinery_employment,fixed_asset_investment,semiconductor_index,auto_production,steel_production,autos_export_unit_price,electronics_export_unit_price,lithium_export_unit_price,rare_earths_export_unit_price,semiconductors_export_unit_price,soybeans_export_unit_price,autos_export_value,electronics_export_value,lithium_export_value,rare_earths_export_value,semiconductors_export_value,soybeans_export_value,dxy,cny,brl,ars,eur,jpy,us2y,us5y,us10y,us30y,credit_spread_bbb_aaa,sp500,nasdaq,carz,smh,xli,erp,cpi_all,cpi_core,cpi_food_beverage,cpi_auto,ppi_intermediate,ppi_final,import_price_index,ppi_auto_parts,ppi_electronic_components,gdp_real,gdp_yoy,pmi,ceo_confidence,oecd_bci,consumer_confidence
2016,99.2,74.8,12348,935.3,1048.5,1075.2,2315.6,98.5,12.2,78.5,100000,7.5,66.7,10,0.6,0.6,383,500,1500,0.5,0.2,300,22.6,95.7,6.64,3.49,14.8,0.9,108.8,0.83,1.37,1.84,2.6,0.45,2094,4737,32.5,57.0,54.5,4.5,240.0,247.9,242.8,100.5,179.6,109.9,116.8,125.4,67.6
2017,100.0,75.5,12448,945.7,1052.3,1085.6,2450.2,100.0,11.2,81.6,100000,7.6,65.8,10,0.6,0.6,400,520,1600,0.55,0.22,320,24.0,93.0,6.75,3.19,16.6,0.89,112.1,1.26,1.92,2.33,2.89,0.38,2449,6181,38.2,80.5,66.8,4.2,245.1,253.5,244.9,99.2,187.6,112.8,120.6,125.2,66.7
2018,102.5,76.9,12691,959.1,1060.4,1102.8,2605.8,102.8,11.3,86.6,100000,7.7,64.5,10,0.61,0.61,375,550,1700,0.6,0.25,340,18.0,95.1,6.62,3.65,28.1,0.85,110.4,2.52,2.76,2.91,3.11,0.42,2747,7138,37.4,89.3,69.2,4.8,251.1,260.0,248.3,98.6,201.5,116.5,124.9,125.7,65.9
2019,101.5,75.9,12835,954.2,1065.7,1115.3,2750.4,101.2,10.9,87.8,100000,7.7,63.3,10,0.62,0.62,348,520,1650,0.65,0.28,360,16.0,97.5,6.91,3.95,48.3,0.89,109.0,1.92,1.95,2.14,2.57,0.50,2914,7973,34.8,120.5,77.4,5.1,255.7,265.9,252.9,99.1,198.1,118.2,123.3,127.8,64.5
2020,95.0,71.5,12178,870.6,1025.9,1050.4,2650.1,95.6,8.8,72.7,100000,7.3,66.7,10,0.64,0.64,423,400,1600,0.8,0.3,350,25.8,93.4,6.9,5.16,70.5,0.88,106.8,0.38,0.53,0.89,1.45,0.85,3218,10462,45.6,175.2,79.8,5.5,258.8,270.1,261.6,100.9,187.8,118.5,118.7,128.4,63.0
2021,99.8,76.2,12453,905.8,1040.2,1070.1,2850.7,100.5,9.2,85.8,100000,7.5,66.7,10,0.65,0.65,419,580,1800,0.9,0.32,400,26.0,91.9,6.45,5.39,95.2,0.85,109.8,0.28,0.86,1.45,1.9,0.4,4273,14448,59.3,280.4,101.5,4.3,271.0,282.6,273.5,111.5,236.8,128.6,134.8,131.6,62.6
2022,100.5,77.8,12762,950.4,1065.8,1105.7,3100.3,102.0,10.1,82.0,100000,7.7,65.0,10,0.66,0.66,429,620,2000,1.0,0.35,420,27.0,108.2,6.73,5.16,130.6,0.95,131.5,2.95,3.0,2.95,3.02,0.55,4098,12041,50.1,210.3,98.5,5.2,292.7,306.2,302.3,133.8,279.7,151.3,152.5,145.5,64.2
2023,99.2,76.5,12958,965.2,1080.5,1120.3,3250.9,103.5,10.6,80.9,100000,7.8,63.0,10,0.66,0.66,431,600,1950,1.1,0.38,430,25.0,103.4,7.08,4.99,295.0,0.92,140.9,4.56,4.06,3.96,4.11,0.50,4168,13219,52.7,160.8,107.3,5.0,304.7,320.3,324.4,135.3,255.3,156.0,143.7,155.7,66.8
2024,100.0,77.0,12991,970.1,1090.4,1125.6,3400.5,105.0,11.0,82.5,100000,7.6,60.0,10,0.66,0.66,452,650,2140,1.2,0.4,440,28.0,102.5,7.10,5.00,850.0,0.93,151.5,4.41,4.13,4.08,4.35,0.45,5428,16920,58.4,240.5,125.0,5.5,314.1,330.1,332.2,132.8,252.8,160.5,144.0,160.2,67.5
2025,100.5,76.8,13000,975.0,1100.0,1130.0,3550.0,108.0,11.7,86.0,110000,9.3,52.0,42,0.82,0.82,520,576,2040,1.2,0.36,456,25.2,99.4,7.20,5.61,1324.0,0.89,148.9,3.95,3.95,4.07,4.45,0.60,6140,20143,75.0,350.7,153.7,7.86,322.5,338.5,341.0,131.5,255.0,165.0,145.0,163.0,68.0"""

    analyze_tariff_impact(user_data)