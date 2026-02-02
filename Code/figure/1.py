import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# 1. 构造状态空间
# -----------------------------
ES = np.linspace(0, 1, 200)          # Emotional State
A = np.linspace(0, 1, 200)           # Opponent attractiveness
ES_grid, A_grid = np.meshgrid(ES, A)

# -----------------------------
# 2. 定义定价倍率函数
# -----------------------------
price_multiplier = np.zeros_like(ES_grid)

# Defensive
mask_def = ES_grid < 0.3
price_multiplier[mask_def] = (
    0.7 + 0.2 * A_grid[mask_def]
)

# Neutral
mask_neu = (ES_grid >= 0.3) & (ES_grid <= 0.6)
price_multiplier[mask_neu] = (
    0.95 + 0.1 * A_grid[mask_neu]
)

# Aggressive
mask_agg = ES_grid > 0.6
price_multiplier[mask_agg] = (
    1.2 + 0.3 * A_grid[mask_agg]
)

# -----------------------------
# 3. 绘制热力图
# -----------------------------
plt.figure(figsize=(8, 6))

im = plt.imshow(
    price_multiplier,
    origin="lower",
    aspect="auto",
    extent=[0, 1, 0, 1]
)

plt.colorbar(im, label="Relative Ticket Price  $p / p_g^*$")

# 状态分界线
plt.axvline(0.3, linestyle="--")
plt.axvline(0.6, linestyle="--")

# 标注
plt.text(0.15, 0.95, "Defensive", ha="center", va="top")
plt.text(0.45, 0.95, "Neutral", ha="center", va="top")
plt.text(0.8, 0.95, "Aggressive", ha="center", va="top")

plt.xlabel("Emotional State Index $ES_t$")
plt.ylabel("Opponent Attractiveness $A_g$")
plt.title("State-Dependent Dynamic Ticket Pricing Heatmap")

plt.tight_layout()
plt.show()
plt.savefig("dynamic_ticket_pricing_heatmap.png", dpi=300)