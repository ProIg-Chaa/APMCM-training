import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ===========================
# 1. 参数定义 (Data-Driven Calibration)
# ===========================
# [Source: MTS CSV] 2024 Base Import ($ Billions)
V_2024 = 3290.0       

# [Source: CBO PDF] Nominal GDP Growth (Real GDP + PCE Inflation)
# Time: 2025, 2026, 2027, 2028
g_cbo = np.array([0.043, 0.043, 0.041, 0.041]) 

# [Source: Problem Description]
tau_old = 0.0244      # Baseline Tariff
tau_new = 0.2011      # Trump Tariff
years = np.array([2025, 2026, 2027, 2028])

# [Source: Calculated from -35% drop] Dynamic Elasticity
# Linear deterioration from -2.03 to -2.8
epsilon = np.linspace(-2.03, -2.8, 4)

# ===========================
# 2. 迭代计算
# ===========================
results = []
v_base_curr = V_2024

for i in range(4):
    # A. 基准更新 (CBO Baseline)
    v_base_curr = v_base_curr * (1 + g_cbo[i])
    r_base = v_base_curr * tau_old
    
    # B. 政策冲击 (Policy Scenario)
    price_shock = (tau_new - tau_old) / (1 + tau_old) # ~17.25%
    vol_shock = epsilon[i] * price_shock              # Volume loss %
    
    v_policy = v_base_curr * (1 + vol_shock)
    r_policy = v_policy * tau_new
    
    # C. 净变化
    net_change = r_policy - r_base
    
    results.append({
        'Year': years[i],
        'Baseline_Revenue': r_base,
        'Policy_Revenue': r_policy,
        'Net_Change': net_change,
        'Baseline_Import': v_base_curr,
        'Policy_Import': v_policy,
        'Volume_Loss_Pct': vol_shock * 100
    })

df = pd.DataFrame(results)

# ===========================
# 3. 结果可视化
# ===========================
fig, ax1 = plt.subplots(figsize=(10, 6))

# 柱状图: 净收入增加
bars = ax1.bar(df['Year'], df['Net_Change'], color='#2ca02c', alpha=0.8, label='Net Revenue Gain')
ax1.set_ylabel('Net Revenue Increase ($ Billions)', color='#2ca02c', fontsize=12, fontweight='bold')
ax1.bar_label(bars, fmt='$%.0f B', padding=3, fontsize=10)
ax1.set_ylim(0, 500)
ax1.set_title('Fig 8.1: Predicted Tariff Revenue Impact (2025-2028)', fontsize=14)

# 折线图: 进口量对比
ax2 = ax1.twinx()
ax2.plot(df['Year'], df['Baseline_Import'], 'b--', linewidth=2, label='CBO Baseline Imports')
ax2.plot(df['Year'], df['Policy_Import'], 'r-o', linewidth=2, label='Policy Scenario Imports')
ax2.set_ylabel('Import Volume ($ Billions)', color='b', fontsize=12, fontweight='bold')
ax2.set_ylim(1500, 4200)

# 图例
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(lines + lines2, labels + labels2, loc='center right')
ax1.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()

print("--- Simulation Results (Billions USD) ---")
print(df[['Year', 'Baseline_Revenue', 'Policy_Revenue', 'Net_Change', 'Policy_Import']].round(1))
print(f"\nTotal 4-Year Net Gain: ${df['Net_Change'].sum():.1f} Billion")