import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. 参数初始化 (基于最终校准值)
# ==========================================
Q_base = 4_150_000       # 2024年总销量
Exchange_Rate = 151.46   # 汇率

# 成本参数 (USD)
c_J = 3000000 / Exchange_Rate # ≈ 19807
c_M = 19680
c_U = 24000

t_sea = 1600
t_land = 600
F_U = 900

# 零部件进口假设 (用于分析内容替代)
# 假设每辆在美国生产的日系车需进口 $8,000 的核心零部件(发动机/变速箱/芯片)
parts_val_per_unit = 8000 

# 政策参数
tau_base = 0.15         # 2025年基准关税
epsilon = -3.0          # 需求弹性
lambda_sens = 0.25      # Logit敏感度

# ==========================================
# 2. 模型运算
# ==========================================
def solve_scenarios(t_add_range):
    data = []
    for t_add in t_add_range:
        # 关税设定
        tau_J = tau_base + t_add  # 日本: 基准+额外
        tau_M = tau_base          # 墨西哥: 仅基准
        
        # 到岸成本
        Cost_J = (c_J + t_sea) * (1 + tau_J)
        Cost_M = (c_M + t_land) * (1 + tau_M)
        Cost_U = c_U + F_U
        
        # Logit 分配
        costs = np.array([Cost_J, Cost_M, Cost_U])
        exp_util = np.exp(-lambda_sens * (costs / 1000))
        shares = exp_util / np.sum(exp_util)
        s_J, s_M, s_U = shares
        
        # 经济传导
        C_avg = np.dot(shares, costs)
        if len(data) == 0: base_price = C_avg
        
        price_delta = (C_avg - base_price) / base_price
        Q_new = Q_base * (1 + epsilon * price_delta)
        
        # 具体指标
        Vol_J = Q_new * s_J
        Vol_M = Q_new * s_M
        Vol_U = Q_new * s_U
        
        # 零部件进口额 (Billion USD)
        Val_Parts = (Vol_U * parts_val_per_unit) / 1e9
        
        data.append({
            'Tariff_Add': t_add,
            'Vol_J': Vol_J, 'Vol_M': Vol_M, 'Vol_U': Vol_U,
            'Total_Demand': Q_new,
            'Val_Parts': Val_Parts,
            'Avg_Price': C_avg
        })
    return pd.DataFrame(data)

# 运行模拟 (0% 到 50% 额外关税)
df = solve_scenarios(np.linspace(0, 0.50, 51))

# ==========================================
# 3. 绘图 (生成两张核心图表)
# ==========================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# --- 图 1: 进口结构分析 (6.4.2) ---
# 左轴: 整车进口量 (日本 vs 墨西哥)
l1 = ax1.plot(df['Tariff_Add']*100, df['Vol_J']/1e6, 'r-', linewidth=2, label='Japan CBU Import')
l2 = ax1.plot(df['Tariff_Add']*100, df['Vol_M']/1e6, 'g--', linewidth=2, label='Mexico CBU Import')
ax1.set_xlabel('Additional Tariff on Japan (%)')
ax1.set_ylabel('CBU Import Volume (Million Vehicles)')
ax1.set_title('Fig 6.4.2: Import Structure Shift (Source & Content)')
ax1.grid(True, alpha=0.3)

# 右轴: 零部件进口额
ax1_right = ax1.twinx()
l3 = ax1_right.plot(df['Tariff_Add']*100, df['Val_Parts'], 'b:', linewidth=2.5, label='Parts Import Value ($Bn)')
ax1_right.set_ylabel('Parts Import Value ($ Billion)', color='b')
ax1_right.tick_params(axis='y', labelcolor='b')

# 合并图例
lines = l1 + l2 + l3
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='center left')


# --- 图 2: 美国汽车工业影响 (6.4.3) ---
# 左轴: 美国本土产量 (回流)
l4 = ax2.plot(df['Tariff_Add']*100, df['Vol_U']/1e6, 'm-', linewidth=2.5, label='US Local Production (Reshoring)')
ax2.set_xlabel('Additional Tariff on Japan (%)')
ax2.set_ylabel('Local Production (Million Vehicles)', color='m')
ax2.tick_params(axis='y', labelcolor='m')
ax2.set_title('Fig 6.4.3: US Auto Industry (Reshoring vs Demand)')
ax2.grid(True, alpha=0.3)

# 右轴: 市场总需求 (萎缩)
ax2_right = ax2.twinx()
l5 = ax2_right.plot(df['Tariff_Add']*100, df['Total_Demand']/1e6, 'k-.', linewidth=2, label='Total Market Demand')
ax2_right.set_ylabel('Total Market Demand (Million Vehicles)', color='k')

# 合并图例
lines2 = l4 + l5
labels2 = [l.get_label() for l in lines2]
ax2.legend(lines2, labels2, loc='center right')

plt.tight_layout()
plt.show()