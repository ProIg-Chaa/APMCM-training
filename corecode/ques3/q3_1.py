import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ===========================
# 1. 参数定义 (基于 7.1 逆向推导值)
# ===========================
# 基础成本指数 (Alt = 100)
C_base = {
    'High': {'US': 113.3, 'CN': 999.0, 'Alt': 100.0}, # CN High banned
    'Mid':  {'US': 113.9, 'CN': 95.0,  'Alt': 100.0},
    'Low':  {'US': 118.0, 'CN': 85.0,  'Alt': 100.0}
}
lambda_sens = 0.15

# ===========================
# 2. 核心模型函数
# ===========================
def evaluate_policy(tier, tariff_cn, subsidy_us, export_control):
    # A. 计算最终到岸成本
    c_us_final = C_base[tier]['US'] - subsidy_us
    c_cn_final = C_base[tier]['CN'] * (1 + tariff_cn)
    c_alt_final = C_base[tier]['Alt'] 
    
    # B. Logit 分配份额
    costs = np.array([c_us_final, c_cn_final, c_alt_final])
    utils = np.exp(-lambda_sens * costs)
    shares = utils / np.sum(utils)
    s_us, s_cn, s_alt = shares
    
    # C. 计算指标
    # 1. 价格通胀 (Inflation)
    min_base = min(C_base[tier]['CN'], C_base[tier]['Alt']) 
    avg_price = np.dot(shares, costs)
    inflation = (avg_price - min_base) / min_base * 100
    
    # 2. 国家安全 (Security Score)
    innovation_factor = 0.7 if (export_control and tier == 'High') else 1.0
    security_score = (0.7 * s_us + 0.3 * innovation_factor) * 100
    
    return s_us, s_cn, s_alt, inflation, security_score

# ===========================
# 3. 运行情景模拟
# ===========================
tiers = ['High', 'Mid', 'Low']
results = []

for tier in tiers:
    # Scenario A: Trump (50% Tariff, 0 Subsidy)
    s_us_t, s_cn_t, s_alt_t, inf_t, sec_t = evaluate_policy(tier, 0.50, 0, True)
    
    # Scenario B: Biden (25% Tariff, $15 Subsidy)
    s_us_b, _, _, inf_b, sec_b = evaluate_policy(tier, 0.25, 15, True)
    
    results.append({
        'Tier': tier,
        # Share Breakdown (Trump Scenario)
        'Share_US': s_us_t, 'Share_CN': s_cn_t, 'Share_Alt': s_alt_t,
        # Metrics Comparison
        'Trump_Sec': sec_t, 'Biden_Sec': sec_b,
        'Trump_Inf': inf_t, 'Biden_Inf': inf_b
    })

df = pd.DataFrame(results)

# ===========================
# 4. 绘图可视化 (3 Panel Chart)
# ===========================
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# 图1: 市场份额结构 (Trump Scenario) - 新增图表
x = np.arange(len(tiers))
axes[0].bar(x, df['Share_US']*100, label='US Domestic', color='#1f77b4')
axes[0].bar(x, df['Share_Alt']*100, bottom=df['Share_US']*100, label='Alternative (Vietnam/Taiwan)', color='#2ca02c')
axes[0].bar(x, df['Share_CN']*100, bottom=(df['Share_US']+df['Share_Alt'])*100, label='China', color='#d62728')
axes[0].set_title('Fig 7.1: Market Share Structure (Trump Policy)')
axes[0].set_ylabel('Market Share (%)')
axes[0].set_xticks(x); axes[0].set_xticklabels(tiers)
axes[0].legend(loc='lower right')

# 图2: 国家安全得分
width = 0.35
axes[1].bar(x - width/2, df['Trump_Sec'], width, label='Trump (Tariff Only)', color='#d62728')
axes[1].bar(x + width/2, df['Biden_Sec'], width, label='Biden (Subsidy+)', color='#1f77b4')
axes[1].set_title('Fig 7.2: National Security Index')
axes[1].set_ylabel('Score (0-100)')
axes[1].set_xticks(x); axes[1].set_xticklabels(tiers)
axes[1].legend()
axes[1].bar_label(axes[1].containers[0], fmt='%.1f'); axes[1].bar_label(axes[1].containers[1], fmt='%.1f')

# 图3: 经济代价 (通胀)
axes[2].plot(tiers, df['Trump_Inf'], 'r-o', lw=3, label='Trump Inflation')
axes[2].plot(tiers, df['Biden_Inf'], 'b--s', lw=2, label='Biden Inflation')
axes[2].set_title('Fig 7.3: Economic Cost (Inflation)')
axes[2].set_ylabel('Price Increase (%)')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()