import pandas as pd
import numpy as np
from scipy.optimize import fsolve
import warnings
warnings.filterwarnings('ignore')

# ==============================
# 1. 读取数据（直接用您上传的文件）
# ==============================
df = pd.read_csv('panel_cleaned.csv')

# 统一国家名称（去掉可能的空格）
df['origin'] = df['origin'].str.strip()

# 使用2025年作为基准年
data = df[df['year'] == 2025].copy()
data = data[data['origin'].isin(['United States', 'Brazil', 'Argentina'])]

base = data.set_index('origin')[['import_volume', 'import_value', 'cif_price']].copy()

base['volume'] = base['import_volume'] / 1e6      # 百万吨
base['value']  = base['import_value'] / 1e9        # 十亿美元
base['price']  = base['cif_price']

# 计算价值份额
base['share'] = base['value'] / base['value'].sum()

print("2025年基准情况（中国从三国进口大豆）")
print(base[['volume', 'value', 'price', 'share']].round(3))

# ==============================
# 2. 参数（可自行修改）
# ==============================
sigma = 8.0                                      # Armington替代弹性
epsilon = -1.0                                   # 中国总进口需求弹性
eta = {'United States': 0.6, 'Brazil': 0.8, 'Argentina': 0.7}  # 供给弹性

# ==============================
# 3. 均衡求解器（已修复NaN问题）
# ==============================
def solve_equilibrium(tariff_us, sigma=sigma, eta=eta, epsilon=epsilon, max_iter=300, tol=1e-8):
    countries = ['United States', 'Brazil', 'Argentina']
    
    # 初始值（必须确保索引完全一致）
    p = base['price'].copy()      # 出口国收到价格（CIF价）
    m = base['volume'].copy()     # 进口量（百万吨）
    
    tariff = {c: tariff_us if c == 'United States' else 0.0 for c in countries}
    
    for it in range(max_iter):
        p_old = p.copy()
        m_old = m.copy()
        
        # 消费者面对的价格 = CIF × (1 + 关税)
        p_cons = p * (1 + pd.Series([tariff[c] for c in countries], index=countries))
        
        # CES份额
        num = (p_cons ** (-sigma)) * m
        den = num.sum()
        share = (m * (p_cons ** (-sigma))) / den
        
        # 世界价格指数
        P_world = (share * (p_cons ** (1-sigma))).sum() ** (1/(1-sigma))
        
        # 中国总进口量变化（需求弹性）
        total_m = base['volume'].sum() * (P_world ** epsilon)
        
        # 新进口量
        m_new = share * total_m
        
        # 防止出现0或负值
        m_new = m_new.clip(lower=1e-6)
        
        # 供给侧：价格响应供给弹性
        for c in countries:
            p[c] = p_old[c] * (m_new[c] / m_old[c]) ** (1/eta[c])
        
        # 收敛判断
        if (np.nanmax(np.abs(p - p_old)) < tol and np.nanmax(np.abs(m - m_old)) < tol):
            # print(f"第 {it+1} 轮收敛")
            break
            
        m = m_new.copy()
    else:
        print(f"警告：{tariff_us*100:.1f}%关税情景未完全收敛（{it}轮）")
    
    # 出口额（出口国收到，不含关税）
    value = m * p
    china_pay = m * p_cons  # 中国实际支付额
    
    result = pd.DataFrame({
        'volume_mt': m,
        'export_price': p,
        'value_bn': value,
        'china_cost_bn': china_pay
    })
    result['vol_pct'] = (result['volume_mt'] / base['volume'] - 1) * 100
    result['val_pct'] = (result['value_bn'] / base['value'] - 1) * 100
    
    return result.round(3)

# ==============================
# 4. 各种关税情景模拟
# ==============================
scenarios = {
    '现状 (额外16.5%)': 0.165,
    '加征到25%': 0.25,
    '加征到40%': 0.40,
    '加征到60%': 0.60,
    '取消额外关税仅3%': 0.03,
}

print("\n" + "="*60)
for name, t in scenarios.items():
    print(f"\n=== {name} ===")
    res = solve_equilibrium(t)
    print(res[['volume_mt', 'value_bn', 'vol_pct', 'val_pct']])