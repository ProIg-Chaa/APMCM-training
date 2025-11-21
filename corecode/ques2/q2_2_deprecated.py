import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. 参数设定 (保持不变)
# ==========================================
Q_total_base = 5_600_000
epsilon = -3.0
lambda_sens = 0.15

# 成本参数 (USD)
c_J, t_sea = 21120, 1600
c_M, t_land = 19680, 600
c_U, F_U = 24000, 900
parts_import_value = 5000  # 假设每辆美国产车需要进口$5000的日本零部件


# ==========================================
# 2. 核心模型函数 (升级版)
# ==========================================
def solve_impact_analysis(tariff_base, tariff_add_range):
    results = []

    for t_add in tariff_add_range:
        tau_J = tariff_base + t_add
        tau_M = tariff_base

        # 1. 计算到岸成本
        Cost_J = (c_J + t_sea) * (1 + tau_J)
        Cost_M = (c_M + t_land) * (1 + tau_M)
        Cost_U = c_U + F_U

        # 2. 计算非关税应对 (产量份额) - Logit模型
        costs = np.array([Cost_J, Cost_M, Cost_U])
        exp_util = np.exp(-lambda_sens * (costs / 1000))
        shares = exp_util / np.sum(exp_util)
        s_J, s_M, s_U = shares

        # 3. 经济传导 (价格与总需求)
        C_avg = s_J * Cost_J + s_M * Cost_M + s_U * Cost_U
        if len(results) == 0: base_price = C_avg  # 记录初始价格

        price_change = (C_avg - base_price) / base_price
        new_demand = Q_total_base * (1 + epsilon * price_change)

        # 4. 计算具体销量
        vol_J = new_demand * s_J
        vol_M = new_demand * s_M
        vol_U = new_demand * s_U

        # ==========================================
        # 5. 题目要求的核心指标计算 (关键修改)
        # ==========================================

        # A. 美日汽车贸易 (U.S.-Japan Trade)
        # 日本整车出口额 (FOB价格)
        trade_val_cars = vol_J * c_J

        # B. 美国进口结构 (Import Structure)
        # 整车进口量 (CBU) = 日本 + 墨西哥
        import_vol_cbu = vol_J + vol_M
        # 零部件进口额 (Parts) = 美国产量 * 单车进口件价值
        import_val_parts = vol_U * parts_import_value

        # C. 美国汽车工业 (US Auto Industry)
        # 产业规模 (本土产值)
        us_industry_revenue = vol_U * c_U
        # 消费者负担 (总支出变化)
        consumer_expenditure = new_demand * C_avg

        results.append({
            'Tariff_Add': t_add,
            'Vol_J': vol_J, 'Vol_M': vol_M, 'Vol_U': vol_U,
            'Total_Demand': new_demand,
            'Avg_Price': C_avg,
            # 针对性指标
            'Trade_Value_Japan_Cars': trade_val_cars,
            'Import_Vol_CBU': import_vol_cbu,
            'Import_Val_Parts': import_val_parts,
            'US_Local_Production': vol_U
        })

    return pd.DataFrame(results)


# 运行模拟
df = solve_impact_analysis(0.10, np.linspace(0, 0.50, 51))

# ==========================================
# 3. 绘图：针对题目三个问题
# ==========================================
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# 图1：美日汽车贸易 (整车贸易额断崖式下跌)
axes[0].plot(df['Tariff_Add'] * 100, df['Trade_Value_Japan_Cars'] / 1e9, 'r-', linewidth=2)
axes[0].set_title('Impact on US-Japan Auto Trade')
axes[0].set_xlabel('Additional Tariff (%)')
axes[0].set_ylabel('Import Value form Japan ($ Billion)')
axes[0].grid(True)

# 图2：进口结构 (整车降，零部件升)
axes[1].plot(df['Tariff_Add'] * 100, df['Import_Vol_CBU'] / 1e6, 'b--', label='CBU Imports (Million Units)')
axes[1].set_xlabel('Additional Tariff (%)')
axes[1].set_ylabel('Finished Cars Volume', color='b')
ax2 = axes[1].twinx()
ax2.plot(df['Tariff_Add'] * 100, df['Import_Val_Parts'] / 1e9, 'g-', label='Parts Import Value ($ Bn)')
ax2.set_ylabel('Parts Import Value', color='g')
axes[1].set_title('Impact on Import Structure')
axes[1].legend(loc='upper left')
ax2.legend(loc='upper right')

# 图3：美国汽车工业 (产量回流 vs 市场萎缩)
axes[2].plot(df['Tariff_Add'] * 100, df['US_Local_Production'] / 1e6, 'm-', linewidth=2, label='US Local Production')
axes[2].set_xlabel('Additional Tariff (%)')
axes[2].set_ylabel('Million Units')
axes[2].plot(df['Tariff_Add'] * 100, df['Total_Demand'] / 1e6, 'k:', label='Total Market Demand')
axes[2].set_title('Impact on US Auto Industry')
axes[2].legend()
axes[2].grid(True)

plt.tight_layout()
plt.show()