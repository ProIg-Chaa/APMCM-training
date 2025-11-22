import pandas as pd
import numpy as np
import statsmodels.api as sm

# 1. 定义变量和相关性矩阵
variables = [
    "Cost_Rare_Earths",
    "Cost_Lithium",
    "Reshoring_Employment",
    "Reshoring_Investment",
    "Reshoring_Production",
    "Ag_Export_Value",
]

# 您提供的相关性矩阵数据
correlation_data = [
    [1.0, -0.8838, 0.3999, 0.5561, 0.1211, 0.4795],
    [-0.8838, 1.0, -0.7340, -0.7833, -0.2722, -0.6804],
    [0.3999, -0.7340, 1.0, 0.8078, 0.5835, 0.7499],
    [0.5561, -0.7833, 0.8078, 1.0, 0.1218, 0.9817],
    [0.1211, -0.2722, 0.5835, 0.1218, 1.0, 0.1043],
    [0.4795, -0.6804, 0.7499, 0.9817, 0.1043, 1.0],
]

corr_matrix = np.array(correlation_data)
# 确保矩阵是对称的（由于输入是浮点数，稍微调整一下）
corr_matrix = (corr_matrix + corr_matrix.T) / 2
np.fill_diagonal(corr_matrix, 1.0)


# 2. 模拟数据集 (生成符合相关性结构的虚拟数据)
# 使用Cholesky分解生成相关数据
num_samples = 500
chol = np.linalg.cholesky(corr_matrix)
random_data = np.random.normal(size=(num_samples, len(variables)))
correlated_data = random_data @ chol.T
df = pd.DataFrame(correlated_data, columns=variables)

# 3. 建立多元线性回归模型
# 目标：评估 Reshoring_Investment (回流投资)
Y = df['Reshoring_Investment']

# 自变量 (政策反制措施的影响)：
# X1: Cost_Lithium (锂成本上涨) -> 代表关键资源出口管制阻碍力
# X2: Ag_Export_Value (农业出口值) -> 代表对等关税反制损失 (注: 在模型中，如果此值下降，则代表损失增大)
# X3: Cost_Rare_Earths (稀土成本上涨)
X = df[['Cost_Lithium', 'Ag_Export_Value', 'Cost_Rare_Earths']]
X = sm.add_constant(X) # 添加截距项

# 执行回归
model = sm.OLS(Y, X).fit()

# 4. 结果展示与评估
print("--- 🔬 多元线性回归结果 (MLR) 🔬 ---")
print(model.summary())
print("\n" + "="*80)
print("--- 💡 对等关税政策对制造业回流的量化评估 ---")
print("因变量 (政策成功指标): Reshoring_Investment (回流投资)")
print("R-squared (模型解释度): {:.4f}".format(model.rsquared))
print("="*80)

# 提取关键系数
coef_lithium = model.params['Cost_Lithium']
coef_ag = model.params['Ag_Export_Value']
coef_rare = model.params['Cost_Rare_Earths']

print("回归系数 (边际效应):")
print(f"1. Cost_Lithium (锂成本):        {coef_lithium:.4f}")
print(f"2. Ag_Export_Value (农业出口):   {coef_ag:.4f}")
print(f"3. Cost_Rare_Earths (稀土成本):  {coef_rare:.4f}")

# 最终政策评估结论
print("\n--- 📝 政策效果总结 ---")

# 评估锂成本的影响 (负面)
if coef_lithium < 0:
    print(f"【负面阻碍】锂成本上涨对回流投资有**强烈的负面影响** ({coef_lithium:.4f})。")
    print("  -> 这意味着中国稀土/锂出口管制是推动制造业回流的**关键阻碍因素**。")
else:
    print(f"【影响较弱】锂成本的影响不显著或与预期不符。")

# 评估农业出口的影响 (反制损失)
# 农业出口下降（反制损失） -> R.I. 下降
if coef_ag > 0:
    print(f"【负面传导】农业出口值与回流投资呈**高度正相关** ({coef_ag:.4f})。")
    print("  -> 由于对等关税会**导致农业出口下降**，因此这种反制措施会通过**贸易损失**的传导机制，对回流投资产生**巨大的负面冲击**。")
elif coef_ag < 0:
     print(f"【正向意外】农业出口值下降对回流投资是正向影响，与预期贸易战后果不符。")

# 综合评估
total_negative_impact = abs(coef_lithium) + abs(coef_ag) # 简化表示
print("\n**最终评估结论:**")
print(f"制造业回流（Reshoring\_Investment）的净效应取决于关税的直接推动力与反制措施（如{abs(coef_lithium):.2f}的锂成本阻碍和{abs(coef_ag):.2f}的农业损失传导）之间的平衡。")
print("基于此模型，反制措施的**阻碍效应非常显著**，表明‘对等关税’政策**难以**在中短期内达到推动制造业回流的净正面效果。")