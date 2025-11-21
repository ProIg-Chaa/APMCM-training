import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. 参数校准 (Calibrated Parameters)
# ==========================================
Q_total_base = 5_600_000  # 基础年销量
epsilon = -3.0  # 需求价格弹性 (BLP Model)
lambda_sens = 0.15  # 供应链调整敏感度 (Logit参数)

# 生产与物流成本 (USD/Unit)
c_J = 21120  # Japan Production
t_sea = 1600  # Shipping
c_M = 19680  # Mexico Production
t_land = 600  # Land Freight
c_U = 24000  # US Production
F_U = 900  # US Fixed Cost Amortization


# ==========================================
# 2. 模型逻辑定义
# ==========================================
def solve_auto_model(tariff_base, tariff_add_range):
    results = []

    for t_add in tariff_add_range:
        # total tariff on Japan = Base (10%) + Additional
        tau_J = tariff_base + t_add
        # total tariff on Mexico = Base (10%) - Assuming Reciprocal Tariff hits everyone
        tau_M = tariff_base

        # --- Step A: Calculate Landed Costs ---
        # Path 1: Japan Direct Export
        Cost_J = (c_J + t_sea) * (1 + tau_J)

        # Path 2: Mexico Transshipment
        Cost_M = (c_M + t_land) * (1 + tau_M)

        # Path 3: US Local Production (FDI)
        Cost_U = c_U + F_U  # No tariff, but high cost

        # --- Step B: Non-Tariff Response (Production Share) ---
        # Using Logit Model to simulate market distribution
        costs = np.array([Cost_J, Cost_M, Cost_U])
        exp_util = np.exp(-lambda_sens * (costs / 1000))  # Scale cost for numerical stability
        shares = exp_util / np.sum(exp_util)

        s_J, s_M, s_U = shares[0], shares[1], shares[2]

        # --- Step C: Economic Transmission (Price & Demand) ---
        # Weighted Average Cost
        C_avg = s_J * Cost_J + s_M * Cost_M + s_U * Cost_U

        # Calculate Price Change (assuming constant markup, %Price = %Cost)
        # Base case reference (t_add=0) needed for comparison?
        # Let's compute current cost absolute value

        results.append({
            'Tariff_Add': t_add,
            'Cost_J': Cost_J,
            'Cost_M': Cost_M,
            'Cost_U': Cost_U,
            'Share_J': s_J,
            'Share_M': s_M,
            'Share_U': s_U,
            'Avg_Cost': C_avg
        })

    df = pd.DataFrame(results)

    # --- Step D: Calculate Demand Change relative to Baseline (t_add=0) ---
    base_price = df.iloc[0]['Avg_Cost']  # Assuming t_add=0 is the start status

    df['Price_Change_Pct'] = (df['Avg_Cost'] - base_price) / base_price
    df['New_Demand'] = Q_total_base * (1 + epsilon * df['Price_Change_Pct'])

    # Calculate Volume by Region
    df['Vol_J'] = df['New_Demand'] * df['Share_J']
    df['Vol_M'] = df['New_Demand'] * df['Share_M']
    df['Vol_U'] = df['New_Demand'] * df['Share_U']

    return df


# ==========================================
# 3. 运行模拟
# ==========================================
# 设定额外关税范围：0% 到 50%
tariff_range = np.linspace(0, 0.50, 51)
baseline_tariff = 0.10  # 题目设定的 10% 最低基准

df_res = solve_auto_model(baseline_tariff, tariff_range)

# ==========================================
# 4. 结果可视化
# ==========================================
plt.figure(figsize=(12, 5))

# Plot 1: Production Shares (非关税应对策略)
plt.subplot(1, 2, 1)
plt.stackplot(df_res['Tariff_Add'] * 100,
              df_res['Share_J'], df_res['Share_M'], df_res['Share_U'],
              labels=['Japan Export', 'Mexico Transshipment', 'US Production (FDI)'],
              colors=['#ff9999', '#66b3ff', '#99ff99'], alpha=0.8)
plt.title('Impact on Production Location (Reshoring)')
plt.xlabel('Additional Tariff on Japan (%)')
plt.ylabel('Market Share')
plt.legend(loc='lower left')
plt.grid(True, alpha=0.3)

# Plot 2: Price & Demand (经济传导)
plt.subplot(1, 2, 2)
ax1 = plt.gca()
ax1.plot(df_res['Tariff_Add'] * 100, df_res['Price_Change_Pct'] * 100, 'r-', label='Price Increase (%)')
ax1.set_xlabel('Additional Tariff on Japan (%)')
ax1.set_ylabel('Price Increase (%)', color='r')
ax1.tick_params(axis='y', labelcolor='r')

ax2 = ax1.twinx()
ax2.plot(df_res['Tariff_Add'] * 100, df_res['New_Demand'] / 10000, 'b--', label='Total Demand (10k Units)')
ax2.set_ylabel('Total Demand (10k Units)', color='b')
ax2.tick_params(axis='y', labelcolor='b')

plt.title('Economic Transmission: Price vs Demand')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# ==========================================
# 5. 输出关键数据点
# ==========================================
print("--- Simulation Results ---")
# Scenario: Baseline (0% extra)
base = df_res.iloc[0]
print(f"[Baseline] Tariff: 10% | US Share: {base['Share_U']:.1%} | Price: ${base['Avg_Cost']:.0f}")

# Scenario: Trade War (+25% extra)
war = df_res.iloc[25]
print(
    f"[Trade War] Tariff: 35% | US Share: {war['Share_U']:.1%} | Price: ${war['Avg_Cost']:.0f} | Demand Loss: {(war['New_Demand'] - Q_total_base) / Q_total_base:.1%}")

# Tipping Point Analysis
# Check when US cost becomes lower than Japan Import cost
tipping_idx = np.where(df_res['Cost_U'] < df_res['Cost_J'])[0][0]
print(
    f"\n[Tipping Point] FDI becomes cheaper than Direct Import at: {df_res.iloc[tipping_idx]['Tariff_Add'] * 100:.1f}% Additional Tariff")