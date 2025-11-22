import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ===========================
# 1. 参数定义 (基于 7.1 逆向推导值)
# ===========================
C_base = {
    'High': {'US': 113.3, 'CN': 999.0, 'Alt': 100.0},
    'Mid':  {'US': 113.9, 'CN': 95.0,  'Alt': 100.0},
    'Low':  {'US': 118.0, 'CN': 85.0,  'Alt': 100.0}
}
lambda_sens = 0.15

# ===========================
# 2. 核心模型函数
# ===========================
def evaluate_policy(tier, tariff_cn, subsidy_us, export_control):
    c_us_final = C_base[tier]['US'] - subsidy_us
    c_cn_final = C_base[tier]['CN'] * (1 + tariff_cn)
    c_alt_final = C_base[tier]['Alt']
    
    costs = np.array([c_us_final, c_cn_final, c_alt_final])
    utils = np.exp(-lambda_sens * costs)
    shares = utils / np.sum(utils)
    s_us, s_cn, s_alt = shares
    
    min_base = min(C_base[tier]['CN'], C_base[tier]['Alt'])
    avg_price = np.dot(shares, costs)
    inflation = (avg_price - min_base) / min_base * 100
    
    innovation_factor = 0.7 if (export_control and tier == 'High') else 1.0
    security_score = (0.7 * s_us + 0.3 * innovation_factor) * 100
    
    return s_us, s_cn, s_alt, inflation, security_score

# ===========================
# 3. 运行情景模拟
# ===========================
tiers = ['High', 'Mid', 'Low']
rows = []

for tier in tiers:
    s_us_t, s_cn_t, s_alt_t, inf_t, sec_t = evaluate_policy(tier, 0.50, 0, True)
    s_us_b, s_cn_b, s_alt_b, inf_b, sec_b = evaluate_policy(tier, 0.25, 15, True)

    rows.append({
        'Tier': tier,
        'US_Share_Trump(%)': s_us_t * 100,
        'CN_Share_Trump(%)': s_cn_t * 100,
        'Alt_Share_Trump(%)': s_alt_t * 100,
        'Trump_Security': sec_t,
        'Biden_Security': sec_b,
        'Trump_Inflation(%)': inf_t,
        'Biden_Inflation(%)': inf_b
    })

df = pd.DataFrame(rows)

# ===========================
# 4. 终端输出完整结果
# ===========================
print("\n==================== 模型输出结果（完整表格） ====================")
print(df.to_string(index=False, float_format="%.2f"))
print("================================================================\n")

# 单独打印更可读的结果（逐项）
for i, row in df.iterrows():
    print(f"------ {row['Tier']} Tier ------")
    print(f"Trump  - Market Share: US={row['US_Share_Trump(%)']:.1f}%, CN={row['CN_Share_Trump(%)']:.1f}%, Alt={row['Alt_Share_Trump(%)']:.1f}%")
    print(f"Biden  - Security Score: {row['Biden_Security']:.2f}")
    print(f"Trump  - Security Score: {row['Trump_Security']:.2f}")
    print(f"Biden  - Inflation: {row['Biden_Inflation(%)']:.2f}%")
    print(f"Trump  - Inflation: {row['Trump_Inflation(%)']:.2f}%\n")

# ===========================
# 5. 绘图可视化
# ===========================
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# 图1 市场份额结构（Trump）
x = np.arange(len(tiers))
axes[0].bar(x, df['US_Share_Trump(%)'], label='US Domestic')
axes[0].bar(x, df['Alt_Share_Trump(%)'], bottom=df['US_Share_Trump(%)'], label='Alternative')
axes[0].bar(x, df['CN_Share_Trump(%)'], bottom=df['US_Share_Trump(%)'] + df['Alt_Share_Trump(%)'], label='China')
axes[0].set_title('Fig 7.1: Market Share Structure (Trump Policy)')
axes[0].set_ylabel('Market Share (%)')
axes[0].set_xticks(x); axes[0].set_xticklabels(tiers)
axes[0].legend(loc='lower right')

# 图2 国家安全指数
width = 0.35
axes[1].bar(x - width/2, df['Trump_Security'], width, label='Trump')
axes[1].bar(x + width/2, df['Biden_Security'], width, label='Biden')
axes[1].set_title('Fig 7.2: National Security Index')
axes[1].set_ylabel('Score (0-100)')
axes[1].set_xticks(x); axes[1].set_xticklabels(tiers)
axes[1].legend()

# 图3 经济代价（通胀）
axes[2].plot(tiers, df['Trump_Inflation(%)'], 'r-o', lw=3, label='Trump Inflation')
axes[2].plot(tiers, df['Biden_Inflation(%)'], 'b--s', lw=2, label='Biden Inflation')
axes[2].set_title('Fig 7.3: Economic Cost (Inflation)')
axes[2].set_ylabel('Price Increase (%)')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
