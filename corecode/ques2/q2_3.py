import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. 参数定义 (严格依据提供的校准表)
# ==========================================
Q_base = 4_150_000      # 2024年总销量 (topmodel.csv)
Exchange_Rate = 151.46  # 2024年汇率 (美日汇率.csv)

# 成本参数 (USD)
# c_J 动态计算: 300万日元 / 151.46
c_J = 3000000 / Exchange_Rate 
c_M = 19680             # 墨西哥成本
c_U = 24000             # 美国成本

t_sea = 1600            # 日本运费
t_land = 600            # 墨西哥运费
F_U = 900               # 美国固定摊销

# 政策与弹性参数
tau_base = 0.15         # 2025年基准关税 (美国汽车关税.csv)
epsilon = -3.0          # 需求弹性
lambda_sens = 0.25      # Logit敏感度 (调高以模拟明显的资本逐利)

# ==========================================
# 2. 模型求解逻辑
# ==========================================
def solve_strategy(t_add_range):
    results = []
    
    for t_add in t_add_range:
        # --- 1. 计算三条路径的到岸成本 ---
        
        # 路径 J: 日本 (基准 + 额外)
        # Cost = (生产 + 运费) * (1 + 15% + 额外)
        tau_J = tau_base + t_add
        Cost_J = (c_J + t_sea) * (1 + tau_J)
        
        # 路径 M: 墨西哥 (仅基准)
        # Cost = (生产 + 运费) * (1 + 15%)
        # 假设互惠关税下，USMCA优惠取消，统一征收基准税
        Cost_M = (c_M + t_land) * (1 + tau_base)
        
        # 路径 U: 美国 (无税，有固定成本)
        Cost_U = c_U + F_U
        
        # --- 2. 非关税应对 (Logit 份额分配) ---
        costs = np.array([Cost_J, Cost_M, Cost_U])
        # 归一化处理防溢出
        exp_util = np.exp(-lambda_sens * (costs / 1000))
        shares = exp_util / np.sum(exp_util)
        s_J, s_M, s_U = shares
        
        # --- 3. 经济传导 (价格与需求) ---
        # 行业加权平均成本
        C_avg = s_J * Cost_J + s_M * Cost_M + s_U * Cost_U
        
        # 记录基准价格 (当 t_add=0 时)
        if len(results) == 0:
            base_price = C_avg
            
        # 价格变化率
        price_delta = (C_avg - base_price) / base_price
        
        # 新总需求
        Q_new = Q_base * (1 + epsilon * price_delta)
        
        # --- 4. 计算具体指标 ---
        # 各地销量
        vol_J = Q_new * s_J
        vol_M = Q_new * s_M
        vol_U = Q_new * s_U
        
        # 贸易额 (日本整车出口 FOB价值)
        # Trade Value = 销量 * 日本离岸生产成本
        trade_val_J = vol_J * c_J
        
        results.append({
            'Tariff_Add': t_add,
            'Cost_J': Cost_J,
            'Cost_M': Cost_M,
            'Cost_U': Cost_U,
            'Share_J': s_J,
            'Share_M': s_M,
            'Share_U': s_U,
            'Vol_J': vol_J,
            'Vol_U': vol_U,
            'Total_Demand': Q_new,
            'Trade_Value_J': trade_val_J
        })
        
    return pd.DataFrame(results)

# ==========================================
# 3. 运行与输出
# ==========================================
# 模拟额外关税从 0% 到 50%
df_res = solve_strategy(np.linspace(0, 0.50, 51))

# 提取关键点
p0 = df_res.iloc[0]  # +0% 额外关税
p10 = df_res.iloc[10] # +10% 额外关税 (总25%)

print("--- 2025年关税政策模拟结果 (基于新参数) ---")
print(f"参数检查: c_J=${c_J:.0f} (汇率{Exchange_Rate}), c_M=${c_M:.0f}, c_U=${c_U:.0f}")
print(f"参数检查: tau_base={tau_base:.0%}")

print("\n[情景 A: 仅实施 15% 基准关税]")
print(f"  日本成本: ${p0['Cost_J']:.0f} | 墨西哥成本: ${p0['Cost_M']:.0f} | 美国成本: ${p0['Cost_U']:.0f}")
print(f"  >> 墨西哥成本最低 ({p0['Cost_M']:.0f}) -> 企业首选墨西哥中转")
print(f"  >> 市场份额: 日本 {p0['Share_J']:.1%} | 墨西哥 {p0['Share_M']:.1%} | 美国 {p0['Share_U']:.1%}")

print("\n[情景 B: 叠加 10% 额外关税 (总25%)]")
print(f"  日本成本: ${p10['Cost_J']:.0f} | 美国成本: ${p10['Cost_U']:.0f}")
print(f"  >> 日本成本反超美国 -> 触发本土化回流 (Share_U 升至 {p10['Share_U']:.1%})")

# 绘图
plt.figure(figsize=(10, 6))
plt.stackplot(df_res['Tariff_Add']*100, 
              df_res['Vol_J']/1e6, df_res['Vol_U']/1e6, (df_res['Total_Demand'] - df_res['Vol_J'] - df_res['Vol_U'])/1e6,
              labels=['Japan Export', 'US Local Prod', 'Mexico Transshipment'],
              colors=['#ff9999','#66b3ff','#99ff99'], alpha=0.8)
plt.title(f'Supply Chain Reconfiguration (Base Tariff {tau_base:.0%})')
plt.xlabel('Additional Tariff on Japan (%)')
plt.ylabel('Sales Volume (Million)')
plt.legend(loc='lower left')
plt.grid(True, alpha=0.3)
plt.show()